"""Descarga datos públicos. Los CSV y JSON entregados permiten trabajar sin red."""
import argparse
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import time

import pandas as pd
import requests

RAIZ = Path(__file__).resolve().parent


def leer_config():
    return json.loads((RAIZ / "config.json").read_text())


def pedir(url, params=None):
    """Tres intentos, TLS normal y error explícito. No se fabrican datos."""
    ultimo_error = None
    for intento in range(3):
        try:
            # Yahoo requiere un agente de navegador en este entorno. FRED
            # responde con el agente estándar de requests y tarda con Mozilla.
            headers = {"User-Agent": "Mozilla/5.0"} if "finance.yahoo.com" in url else {}
            r = requests.get(url, params=params, headers=headers, timeout=30)
            r.raise_for_status()
            return r
        except requests.RequestException as error:
            ultimo_error = error
            if intento < 2:
                time.sleep(2 ** intento)
    raise RuntimeError(f"No se pudo descargar {url}. Use los archivos entregados. {ultimo_error}")


def bajar_yahoo(ticker, config):
    inicio = pd.Timestamp(config["inicio_descarga"], tz="UTC")
    fin = pd.Timestamp(config["corte"], tz="UTC") + pd.Timedelta(days=1)
    parametros = {"period1": int(inicio.timestamp()), "period2": int(fin.timestamp()),
                  "interval": "1d", "events": "div,splits", "includeAdjustedClose": "true"}
    for host in ("query1", "query2"):
        try:
            r = pedir(f"https://{host}.finance.yahoo.com/v8/finance/chart/{ticker}", parametros)
            contenido = r.json()
            d = contenido["chart"]["result"][0]
            break
        except (RuntimeError, ValueError, KeyError, TypeError, IndexError):
            if host == "query2":
                raise RuntimeError(f"Yahoo no entregó {ticker}. Conserve la caché o reintente después.")
    moneda = "CLP" if ticker == config["tipo_cambio"] else "USD"
    if d["meta"]["currency"] != moneda:
        raise ValueError(f"Moneda inesperada para {ticker}")
    fechas = pd.to_datetime(d["timestamp"], unit="s", utc=True).tz_convert(
        d["meta"]["exchangeTimezoneName"]).tz_localize(None).normalize()
    tabla = pd.DataFrame({"fecha": fechas,
                          "cierre": d["indicators"]["quote"][0]["close"],
                          "ajustado": d["indicators"]["adjclose"][0]["adjclose"]})
    tabla = tabla.set_index("fecha").sort_index()
    dividendos = {}
    for evento in d.get("events", {}).get("dividends", {}).values():
        fecha = pd.Timestamp(evento["date"], unit="s", tz="UTC").tz_convert(
            d["meta"]["exchangeTimezoneName"]).tz_localize(None).normalize()
        dividendos[fecha] = dividendos.get(fecha, 0) + evento["amount"]
    tabla["dividendo"] = pd.Series(dividendos, dtype=float).reindex(tabla.index).fillna(0)
    tabla = tabla.loc[config["inicio_descarga"]:config["corte"]]
    # Yahoo ya expresa cierre y dividendos en unidades ajustadas por splits.
    # BIL tiene un reverse split 1:2 en 2017: no aplicarlo otra vez.
    # analisis.py contrasta retornos diarios, incluido ese día, antes de usarlos.
    # FX conserva días sin cotización como NA; el análisis exige un cierre
    # observado a no más de 7 días del fin de mes. No interpola esos días.
    faltantes_etf = ticker in config["etfs"] and tabla.isna().any().any()
    if faltantes_etf or tabla.index.has_duplicates or (tabla[["cierre", "ajustado"]] <= 0).any().any():
        raise ValueError(f"Datos faltantes, duplicados o precios inválidos en {ticker}.")
    return tabla, r.content, r.url


def descargar(actualizar=False):
    config = leer_config()
    carpeta = RAIZ / "data/raw"
    carpeta.mkdir(parents=True, exist_ok=True)
    ruta_manifiesto = RAIZ / "data/metadatos.json"
    anterior = json.loads(ruta_manifiesto.read_text()) if ruta_manifiesto.exists() else {}
    if not actualizar:
        for archivo, sha in anterior.get("sha256", {}).items():
            p = RAIZ / archivo
            if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest() != sha:
                raise ValueError(f"Caché alterada: {archivo}. Restaure los archivos o use --actualizar.")
    registros = anterior.get("archivos", {})
    momento = datetime.now(timezone.utc).isoformat()
    for ticker in config["etfs"] + [config["tipo_cambio"], config["cobre"]]:
        ruta = carpeta / f"{ticker}.csv"
        if ruta.exists() and ticker in registros and not actualizar:
            print(f"Caché: {ticker}")
            continue
        tabla, original, url = bajar_yahoo(ticker, config)
        (carpeta / f"{ticker}.json").write_bytes(original)
        tabla.to_csv(ruta, float_format="%.12g")
        registros[ticker] = {"fuente": "Yahoo Finance chart", "url": url, "descarga_utc": momento,
                              "primera_fecha": str(tabla.index.min().date()),
                              "ultima_fecha": str(tabla.cierre.dropna().index.max().date()),
                              "filas": len(tabla), "cierres_faltantes": int(tabla.cierre.isna().sum())}
        print(f"Descargado: {ticker}, {len(tabla)} observaciones")
        ruta_manifiesto.write_text(json.dumps({"archivos": registros}, indent=2))
    for serie in ("DGS1MO", "DGS2", "DGS10"):
        ruta = carpeta / f"{serie}.csv"
        if ruta.exists() and serie in registros and not actualizar:
            print(f"Caché: {serie}")
            continue
        # Descargar la serie completa y recortar localmente: este URL público
        # funciona también cuando el servidor tarda con parámetros de fechas.
        r = pedir("https://fred.stlouisfed.org/graph/fredgraph.csv", {"id": serie})
        tabla = pd.read_csv(io.StringIO(r.text), index_col=0, parse_dates=True, na_values=["."])
        tabla.index.name = "fecha"
        tabla = tabla.loc[config["inicio_descarga"]:config["corte"]]
        tabla[serie] = pd.to_numeric(tabla[serie], errors="raise")
        tabla.to_csv(ruta)
        registros[serie] = {"fuente": "FRED", "url": r.url, "descarga_utc": momento,
                             "primera_fecha": str(tabla.index.min().date()),
                             "ultima_fecha": str(tabla[serie].dropna().index.max().date()),
                             "filas": len(tabla), "faltantes": int(tabla[serie].isna().sum())}
        print(f"Descargado: {serie}")
        ruta_manifiesto.write_text(json.dumps({"archivos": registros}, indent=2))
    # Guardar hashes de cada archivo realmente usado, incluidos los originales Yahoo.
    hashes = {str(p.relative_to(RAIZ)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sorted(carpeta.iterdir()) if p.is_file()}
    ruta_manifiesto.write_text(json.dumps({"archivos": registros, "sha256": hashes}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--actualizar", action="store_true", help="Reemplazar explícitamente la descarga guardada")
    descargar(parser.parse_args().actualizar)
