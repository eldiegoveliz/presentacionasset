"""Fuentes públicas BCCh y FEES. Guarda las extracciones y la trazabilidad."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
from pypdf import PdfReader
import openpyxl

from datos import RAIZ, pedir

CARPETA = RAIZ / "data/oficial"
MESES = "enero febrero marzo abril mayo junio julio agosto septiembre octubre noviembre diciembre".split()
BASE = "https://www.hacienda.cl"
LISTA = BASE + "/areas-de-trabajo/finanzas-internacionales/fondos-soberanos/fondo-de-estabilizacion-economica-y-social/informes-mensuales"
PIB_URL = "https://si3.bcentral.cl/siete/ES/Siete/Cuadro/CAP_CCNN/MN_CCNN76/CCNN2018_P0_V2?idSerie=F032.PIB.FLU.R.CLP.EP18.Z.Z.1.T"


def bcch_movil(html):
    m = re.search(r"var razorArrayDatos\s*=\s*(\[.*?\]);", html, re.S)
    if not m:
        raise ValueError("El BCCh cambió el formato público: no hay razorArrayDatos")
    pares = [json.loads(x) for x in json.loads(m[1])]
    d = pd.DataFrame(pares, columns=["fecha", "valor"])
    d["fecha"] = pd.to_datetime(d.fecha, unit="ms", utc=True).dt.tz_convert("America/Santiago").dt.tz_localize(None).dt.normalize()
    if d.fecha.duplicated().any() or d.valor.isna().any():
        raise ValueError("Observaciones BCCh inválidas")
    return d.set_index("fecha").valor.sort_index()


def bcch_pib(html):
    filas = []
    for tr in BeautifulSoup(html, "html.parser").select("table tr"):
        c = [td.get_text(" ", strip=True) for td in tr.select("td")]
        if len(c) != 2:
            continue
        m = re.fullmatch(r"(IV|III|II|I)\.(\d{4})", c[0])
        if m:
            q = {"I": 1, "II": 2, "III": 3, "IV": 4}[m[1]]
            fecha = pd.Period(f"{m[2]}Q{q}", freq="Q").end_time.normalize()
            filas.append((fecha, float(c[1].replace(".", "").replace(",", "."))))
    d = pd.Series(dict(filas), dtype=float).sort_index().rename("pib_real_desestacionalizado")
    if len(d) < 40 or (d <= 0).any():
        raise ValueError("Serie PIB incompleta")
    return d


def extraer_retorno(texto):
    texto = texto.replace("−", "-").replace("–", "-").replace("\xa0", " ")
    patron = r"Retorno\s+en\s+USD\s*(?:\([^)]*\))?\s*(-?\s*\d+[,.]\d+)\s*%"
    m = re.search(patron, texto, re.I)
    if not m:
        raise ValueError("No se identificó el retorno mensual USD del FEES")
    valor = float(m[1].replace(" ", "").replace("\n", "").replace(",", ".")) / 100
    if not -0.25 < valor < 0.25:
        raise ValueError("Retorno FEES fuera de rango: revisar extracción")
    return valor, m[0]


def descargar_mes(elemento):
    fecha, urls = elemento
    url = urls[0]
    cache = CARPETA / "pdf_cache" / f"{fecha:%Y-%m}.pdf"
    texto_path = CARPETA / "fees_textos" / f"{fecha:%Y-%m}.txt"
    meta_path = texto_path.with_suffix(".json")
    if texto_path.exists() and meta_path.exists():
        meta = json.loads(meta_path.read_text())
        return meta
    if cache.exists():
        contenido = cache.read_bytes()
    else:
        contenido = None
        for pagina_url in urls:
            pagina = pedir(pagina_url)
            if pagina.content.startswith(b"%PDF"):
                contenido, url = pagina.content, pagina_url
                break
            enlaces_pdf = [urljoin(BASE, a["href"]) for a in BeautifulSoup(pagina.text, "html.parser").select("main a[href]")
                           if "pdf" in a.get_text(" ", strip=True).lower()]
            if enlaces_pdf:
                url = enlaces_pdf[0]
                contenido = pedir(url).content
                break
        if contenido is None or not contenido.startswith(b"%PDF"):
            raise ValueError(f"No hay enlace PDF válido: {urls}")
        cache.write_bytes(contenido)
    reader = PdfReader(io.BytesIO(contenido))
    textos = [p.extract_text() or "" for p in reader.pages]
    texto = "\n".join(f"PAGINA {i+1}\n{t}" for i, t in enumerate(textos))
    portada = texto[:700].lower()
    if MESES[fecha.month-1] not in portada or str(fecha.year) not in portada:
        raise ValueError(f"Portada no corresponde a {fecha.date()}: {portada[:150]}")
    retorno, evidencia = extraer_retorno(texto)
    pagina = next(i+1 for i, t in enumerate(textos) if re.search(r"Retorno\s+en\s+USD", t, re.I))
    meta = {"fecha": str(fecha.date()), "retorno_usd": retorno, "url": url, "pagina": pagina,
            "evidencia": evidencia, "sha256_pdf": hashlib.sha256(contenido).hexdigest()}
    texto_path.write_text(texto)
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2))
    return meta


def descargar():
    for nombre in ("pdf_cache", "fees_textos", "paginas"):
        (CARPETA / nombre).mkdir(parents=True, exist_ok=True)
    fuentes = {}
    for nombre, url, frecuencia in [
        ("bcch_dolar", "https://si3.bcentral.cl/Bdemovil/BDE/Series/MOV_ID_TC1", "diaria"),
        ("bcch_ipc", "https://si3.bcentral.cl/Bdemovil/BDE/Series/MOV_SC_PR1", "mensual"),
        ("bcch_pib", PIB_URL, "trimestral")]:
        ruta = CARPETA / "paginas" / f"{nombre}.html"
        if not ruta.exists():
            ruta.write_text(pedir(url).text)
        html = ruta.read_text()
        serie = bcch_pib(html) if nombre == "bcch_pib" else bcch_movil(html)
        serie = serie.loc["2013-01-01":"2026-10-31"]
        if nombre == "bcch_ipc":
            serie.index = serie.index.to_period("M").to_timestamp("M")
        serie.rename(nombre).to_csv(CARPETA / f"{nombre}.csv", index_label="fecha")
        fuentes[nombre] = {"url": url, "frecuencia": frecuencia, "filas": len(serie),
                            "primera": str(serie.index.min().date()), "ultima": str(serie.index.max().date())}
        print(nombre, len(serie), str(serie.index.max().date()), flush=True)

    # Seguir la paginación publicada; no adivinar slugs de informes antiguos.
    paginas = [LISTA]
    html0 = pedir(LISTA).text
    for a in BeautifulSoup(html0, "html.parser").select("a[href]"):
        url = urljoin(BASE, a["href"])
        if "foco=" in url and url not in paginas:
            paginas.append(url)
    enlaces = {}
    for i, url in enumerate(paginas):
        ruta = CARPETA / "paginas" / f"hacienda_lista_{i}.html"
        if not ruta.exists():
            ruta.write_text(pedir(url).text)
        for a in BeautifulSoup(ruta.read_text(), "html.parser").select("a[href]"):
            titulo = a.get_text(" ", strip=True).lower()
            m = re.search(r"\binforme\s+(\w+)\s+(\d{4})$", titulo)
            if m and m[1] in MESES:
                fecha = pd.Timestamp(int(m[2]), MESES.index(m[1])+1, 1) + pd.offsets.MonthEnd(0)
                if pd.Timestamp("2014-01-31") <= fecha <= pd.Timestamp("2026-09-30"):
                    url_mes = urljoin(BASE, a["href"])
                    enlaces.setdefault(fecha, [])
                    if url_mes not in enlaces[fecha]:
                        enlaces[fecha].append(url_mes)
    # El enlace de Hacienda para julio 2016 devuelve el informe de junio.
    # DIPRES conserva el informe correcto; validar siempre mes y año de portada.
    enlaces[pd.Timestamp("2016-07-31")] = ["https://www.dipres.gob.cl/598/articles-149467_doc_pdf.pdf"]
    esperados = pd.date_range("2014-01-31", "2026-09-30", freq="ME")
    faltantes = esperados.difference(pd.DatetimeIndex(enlaces))
    if len(faltantes):
        raise ValueError(f"Faltan enlaces oficiales: {list(faltantes)}")
    resultados, errores = [], []
    # Cada hilo tiene un archivo propio. El índice solo se escribe al terminar.
    with ThreadPoolExecutor(max_workers=4) as pool:
        tareas = {fecha: pool.submit(descargar_mes, (fecha, url)) for fecha, url in sorted(enlaces.items())}
        for i, (fecha, tarea) in enumerate(tareas.items(), 1):
            try:
                resultados.append(tarea.result())
            except Exception as e:
                errores.append(f"{fecha.date()}: {e}")
            if i % 12 == 0:
                print("Informes procesados", i, "/", len(tareas), flush=True)
    if errores:
        (CARPETA / "errores_descarga.txt").write_text("\n".join(errores))
        raise ValueError(f"{len(errores)} informes requieren revisión. Ver data/oficial/errores_descarga.txt")
    (CARPETA / "errores_descarga.txt").unlink(missing_ok=True)
    d = pd.DataFrame(resultados).set_index("fecha").sort_index()
    d.to_csv(CARPETA / "fees_mensual.csv")
    fuentes["fees"] = {"url_indice": LISTA, "filas": len(d), "precision": "PDF: retorno mensual redondeado a 0,01 pp"}
    url_saldos = LISTA + "/informe-septiembre-2026/xls"
    archivo_saldos = CARPETA / "paginas/fees_saldos_fuente.xlsx"
    if not archivo_saldos.exists():
        archivo_saldos.write_bytes(pedir(url_saldos).content)
    libro = openpyxl.load_workbook(io.BytesIO(archivo_saldos.read_bytes()), data_only=True, read_only=True)
    hoja = libro["Datos Evo. Hist."]
    saldos = [(fila[0], fila[1]) for fila in hoja.iter_rows(min_row=5, max_row=300, max_col=2, values_only=True)
              if isinstance(fila[0], datetime) and isinstance(fila[1], (float, int))]
    saldo = pd.Series(dict(saldos), dtype=float).sort_index().loc["2013-12-01":"2026-09-30"]
    saldo.rename("saldo_usd_millones").to_csv(CARPETA / "fees_saldos.csv", index_label="fecha")
    fuentes["saldos_fees"] = {"url": url_saldos, "hoja": "Datos Evo. Hist.", "filas": len(saldo)}
    hashes = {str(p.relative_to(RAIZ)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sorted(CARPETA.rglob("*")) if p.is_file() and "pdf_cache" not in p.parts and p.name != "metadatos.json"}
    (CARPETA / "metadatos.json").write_text(json.dumps({"consulta_utc": datetime.now(timezone.utc).isoformat(),
                                                      "fuentes": fuentes, "sha256": hashes}, indent=2))
    print("Datos oficiales listos", len(d), "meses FEES", flush=True)


if __name__ == "__main__":
    descargar()
