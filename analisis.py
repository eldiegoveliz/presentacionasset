"""Análisis exploratorio del bloque USD del FEES. Sin optimización de pesos."""
import json
from math import erf, exp, log, sqrt
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from datos import RAIZ, leer_config


def cargar_mensuales(config):
    """Fin de mes disponible; exigir meses completos y fechas comunes en los ETF."""
    series, calidad = {}, []
    indices = []
    for ticker in config["etfs"]:
        d = pd.read_csv(RAIZ / f"data/raw/{ticker}.csv", index_col=0, parse_dates=True)
        if d.index.has_duplicates or not d.index.is_monotonic_increasing or d.isna().any().any():
            raise ValueError(f"Fechas o valores inválidos: {ticker}")
        if (d[["cierre", "ajustado"]] <= 0).any().any():
            raise ValueError(f"Precios no positivos: {ticker}")
        d = d.loc[config["inicio_descarga"]:config["corte"]]
        indices.append(d.index)
        # Contrastar ajuste de Yahoo con precio + dividendo en la fecha ex-dividendo.
        reconstruido = (d.cierre + d.dividendo) / d.cierre.shift(1) - 1
        ajustado = d.ajustado.pct_change(fill_method=None)
        error = float((reconstruido - ajustado).abs().max())
        if error > 0.001:
            raise ValueError(f"Ajuste de dividendos de {ticker} difiere más de 10 pb: {error}")
        mensual = d.ajustado.resample("ME").last()
        fechas = pd.Series(d.index, index=d.index).resample("ME").last()
        if mensual.isna().any() or ((mensual.index - pd.DatetimeIndex(fechas)).days > 7).any():
            raise ValueError(f"Mes faltante o cierre alejado de fin de mes: {ticker}")
        series[ticker] = mensual
        calidad.append({"ticker": ticker, "filas": len(d), "primera": str(d.index.min().date()),
                        "ultima": str(d.index.max().date()), "dividendos": int((d.dividendo != 0).sum()),
                        "max_error_retorno_pb": error * 10000})
    if any(not i.equals(indices[0]) for i in indices[1:]):
        raise ValueError("Los ETF tienen fechas distintas. Revisar, no rellenar silenciosamente.")
    precios = pd.DataFrame(series)
    precios = precios.loc[:config["corte"]]
    if precios.isna().any().any():
        raise ValueError("Precios mensuales incompletos")
    retornos = precios.pct_change(fill_method=None).iloc[1:]
    esperados = pd.date_range(retornos.index.min(), pd.Timestamp(config["corte"]), freq="ME")
    if not retornos.index.equals(esperados):
        raise ValueError("Faltan meses hasta el corte configurado. No extender el período por suposición.")
    return retornos, pd.DataFrame(calidad).set_index("ticker")


def pesos_escenario(config, escenario):
    """Una cartera por hipótesis. Los cambios de política se rotulan por separado."""
    w = pd.Series(config["pesos_fondo_usd"], dtype=float)
    traspaso = escenario["traspaso"]
    if traspaso < 0:
        raise ValueError("El traspaso debe ser positivo")
    if traspaso:
        if escenario["origen"] not in w or escenario["destino"] not in w:
            raise ValueError("Instrumento ajeno al bloque de renta fija")
        w[escenario["origen"]] -= traspaso
        w[escenario["destino"]] += traspaso
    if (w < 0).any() or not np.isclose(w.sum(), 0.69):
        raise ValueError("Pesos negativos o bloque distinto de 69%")
    if escenario["tipo"] in ("referencia", "puts", "duracion"):
        if not np.allclose(w[["BIL", "STIP", "MBB"]], [0.10, 0.04, 0.15]):
            raise ValueError("Este escenario no puede cambiar pesos estratégicos de clases")
        if not np.isclose(w[["SHY", "IEI", "IEF"]].sum(), 0.40):
            raise ValueError("La asignación Treasury de este escenario debe mantenerse en 40%")
    elif escenario["tipo"] not in ("liquidez", "mbs"):
        raise ValueError("Tipo de cartera no reconocido")
    return w


def cartera(retornos, pesos, costo=0.0005):
    """Rebalanceo mensual; costo por cada dólar comprado o vendido, sin dividir por dos."""
    w = pesos / pesos.sum()
    r = retornos.loc[:, w.index]
    bruto = r.dot(w)
    # Pesos que quedan después de la rentabilidad del mes previo.
    despues = r.add(1).mul(w).div(1 + bruto, axis=0)
    transado = despues.shift(1).sub(w).abs().sum(axis=1)
    transado.iloc[0] = 1.0  # Compra inicial desde efectivo.
    neto = (1 - costo * transado) * (1 + bruto) - 1
    return neto


def riqueza_y_caida(retornos):
    riqueza = (1 + retornos).cumprod()
    # El capital inicial es 1: incluirlo evita esconder una caída en el primer mes.
    maximo = riqueza.cummax().clip(lower=1)
    return riqueza, riqueza / maximo - 1


def metricas(retornos):
    _, caida = riqueza_y_caida(retornos)
    return pd.DataFrame({"retorno_anual_pct": ((1 + retornos).prod() ** (12 / len(retornos)) - 1) * 100,
                         "volatilidad_anual_pct": retornos.std(ddof=1) * np.sqrt(12) * 100,
                         "caida_max_mensual_pct": caida.min() * 100,
                         "peor_mes_pct": retornos.min() * 100})


def bootstrap_media(diferencia, bloque, repeticiones, semilla):
    """Mismos meses para ambas carteras; bloques circulares preservan dependencia local."""
    valores = np.asarray(diferencia)
    n = len(valores)
    rng = np.random.default_rng(semilla)
    inicios = rng.integers(0, n, size=(repeticiones, int(np.ceil(n / bloque))))
    indices = (inicios[:, :, None] + np.arange(bloque)) % n
    muestras = valores[indices.reshape(repeticiones, -1)[:, :n]]
    return np.quantile(muestras.mean(axis=1) * 12 * 100, [0.025, 0.975])


def precio_put_black76(futuro, strike, volatilidad, tasa, plazo):
    """Prima teórica europea por unidad. No es una cotización de una opción real."""
    if futuro <= 0 or strike <= 0 or volatilidad < 0 or plazo < 0:
        raise ValueError("Parámetros inválidos para la put")
    if plazo == 0:
        return max(strike - futuro, 0)
    if volatilidad == 0:
        return exp(-tasa * plazo) * max(strike - futuro, 0)
    d1 = (log(futuro / strike) + 0.5 * volatilidad ** 2 * plazo) / (volatilidad * sqrt(plazo))
    d2 = d1 - volatilidad * sqrt(plazo)
    normal_menos_d1 = 0.5 * (1 + erf(-d1 / sqrt(2)))
    normal_menos_d2 = 0.5 * (1 + erf(-d2 / sqrt(2)))
    return exp(-tasa * plazo) * (strike * normal_menos_d2 - futuro * normal_menos_d1)


def preparar_insumos_puts(cobre, tasa, ventana):
    """Alinear el mes del pago con precios, volatilidad y tasa conocidos al entrar."""
    mensual = cobre.resample("ME").last()
    sigma = np.log(cobre / cobre.shift(1)).rolling(ventana).std(ddof=1) * np.sqrt(252)
    return pd.DataFrame({"futuro_inicial": mensual.shift(1), "futuro_final": mensual,
                         "sigma_hist_entrada": sigma.resample("ME").last().shift(1),
                         "tasa_entrada": tasa.resample("ME").last().shift(1) / 100})


def cargar_insumos_puts(config):
    cobre = pd.read_csv(RAIZ / f"data/raw/{config['cobre']}.csv", index_col=0, parse_dates=True).cierre
    tasa = pd.read_csv(RAIZ / "data/raw/DGS1MO.csv", index_col=0, parse_dates=True).DGS1MO
    for serie in (cobre, tasa):
        fechas = pd.Series(serie.dropna().index, index=serie.dropna().index).resample("ME").last()
        if fechas.isna().any() or ((fechas.index - pd.DatetimeIndex(fechas)).days > 7).any():
            raise ValueError("Cobre o tasa sin cierre mensual reciente")
    return preparar_insumos_puts(cobre.dropna(), tasa, config["puts"]["ventana_vol_dias"])


def cartera_puts(retornos, pesos, insumos, parametros, costo):
    """Cartera base + put mensual, pagada vendiendo letras. Sin exposición futura desnuda."""
    d = insumos.reindex(retornos.index).copy()
    if d.isna().any().any() or (d[["futuro_inicial", "futuro_final", "sigma_hist_entrada"]] <= 0).any().any():
        raise ValueError("Faltan insumos anteriores a la compra de puts o hay valores inválidos")
    h = parametros["nocional_sobre_fondo"]
    k = parametros["strike_sobre_futuro"]
    friccion = parametros["friccion_sobre_prima"]
    if not 0 <= h <= 1 or k <= 0 or friccion < 0 or parametros["multiplicador_vol"] <= 0:
        raise ValueError("Parámetros económicos inválidos para la cobertura")
    d["strike"] = k * d.futuro_inicial
    d["vol_modelo"] = parametros["multiplicador_vol"] * d.sigma_hist_entrada
    d["prima_por_libra_modelo"] = [precio_put_black76(f, strike, sigma, tasa, parametros["plazo_anios"])
                                    for f, strike, sigma, tasa in zip(d.futuro_inicial, d.strike, d.vol_modelo, d.tasa_entrada)]
    d["prima_sobre_fondo"] = h * d.prima_por_libra_modelo / d.futuro_inicial
    d["friccion_sobre_fondo"] = friccion * d.prima_sobre_fondo
    d["payoff_sobre_fondo"] = h * (d.strike - d.futuro_final).clip(lower=0) / d.futuro_inicial
    pagado = d.prima_sobre_fondo + d.friccion_sobre_fondo
    if (pagado > pesos["BIL"]).any():
        raise ValueError("La prima y sus costos superan las letras disponibles: no se permite endeudamiento")
    # El dinero de prima y fricción deja de ganar el retorno de BIL ese mes.
    d["ingreso_BIL_sacrificado"] = pagado * retornos.BIL
    d["aporte_neto_bloque"] = (d.payoff_sobre_fondo - pagado - d.ingreso_BIL_sacrificado) / pesos.sum()
    base = cartera(retornos, pesos, costo)
    objetivo = pesos / pesos.sum()
    anteriores = None
    rendimientos, costos = [], []
    for fecha, r_mes in retornos[objetivo.index].iterrows():
        # Al vencer, el pago entra en BIL. El mes siguiente se rebalancea
        # desde las tenencias reales, incluidos los pagos o pérdidas del seguro.
        transado = 1.0 if anteriores is None else (objetivo - anteriores).abs().sum()
        factor = 1 - costo * transado
        tenencias = objetivo * factor
        tenencias["BIL"] -= factor * pagado.loc[fecha] / pesos.sum()
        final = tenencias * (1 + r_mes)
        final["BIL"] += factor * d.loc[fecha, "payoff_sobre_fondo"] / pesos.sum()
        riqueza_final = final.sum()
        if riqueza_final <= 0:
            raise ValueError("Capital agotado en la simulación")
        rendimientos.append(riqueza_final - 1)
        costos.append(costo * transado)
        anteriores = final / riqueza_final
    d["retorno_cartera"] = rendimientos
    d["costo_rebalanceo_bloque"] = costos
    d["aporte_tras_costos_base"] = d.retorno_cartera - base
    return d.retorno_cartera, d


def comparar_carteras(retornos, config, insumos, costo=None):
    costo = config["costo_por_dolar_transado"] if costo is None else costo
    pesos, carteras, auditoria = {}, {}, None
    for escenario in config["carteras"]:
        nombre = escenario["nombre"]
        w = pesos_escenario(config, escenario)
        pesos[nombre] = w
        if escenario["tipo"] == "puts":
            carteras[nombre], auditoria = cartera_puts(retornos, w, insumos, config["puts"], costo)
        else:
            carteras[nombre] = cartera(retornos, w, costo)
    return pd.DataFrame(carteras), pd.DataFrame(pesos), auditoria


def clasificar_carteras(config):
    estados = {"referencia": "Referencia proxy; cumplimiento no certificado",
               "liquidez": "Requiere cambiar asignacion y evaluar riesgo ex ante",
               "puts": "Instrumento fuera de la politica consultada; simulacion teorica",
               "duracion": "Pesos de clases conservados; TE ex ante no verificado",
               "mbs": "Requiere cambiar el 15% estrategico de MBS"}
    return pd.DataFrame([{"cartera": e["nombre"], "hipotesis": e["hipotesis"],
                          "estado_normativo": estados[e["tipo"]],
                          "evidencia": "Primas teoricas, subyacente continuo proxy" if e["tipo"] == "puts" else "Retornos ETF proxy"}
                         for e in config["carteras"]]).set_index("cartera")


def ejecutar():
    config = leer_config()
    salida = RAIZ / "results"
    figuras = salida / "figuras"
    figuras.mkdir(parents=True, exist_ok=True)
    todos, calidad = cargar_mensuales(config)
    insumos = cargar_insumos_puts(config)
    r = todos.loc[config["inicio_analisis"]:]
    portafolios, pesos, auditoria = comparar_carteras(r, config, insumos)
    referencia = portafolios.iloc[:, 0]
    estados = clasificar_carteras(config)
    resumen = metricas(portafolios)
    resumen["diferencia_cagr_pp"] = resumen.retorno_anual_pct - resumen.retorno_anual_pct.iloc[0]
    resumen["te_proxy_soberano_pb"] = np.nan
    soberanos = [t for t in pesos.index if t != "MBB"]
    for e in config["carteras"]:
        if e["tipo"] in ("referencia", "liquidez", "duracion"):
            cambio = pesos[e["nombre"]] - pesos.iloc[:, 0]
            activo = r[soberanos].dot(cambio[soberanos]) / 0.85
            resumen.loc[e["nombre"], "te_proxy_soberano_pb"] = activo.std(ddof=1) * np.sqrt(12) * 10000
    for nombre, tabla in {"calidad_datos": calidad, "retornos_activos_mensuales": todos,
                          "pesos_sobre_fondo": pesos, "retornos_carteras_mensuales": portafolios,
                          "metricas": resumen, "estado_carteras": estados, "puts_auditoria": auditoria}.items():
        tabla.to_csv(salida / f"{nombre}.csv")

    sensibilidad = []
    for inicio, fin, periodo in [("2015", "2019", "2015-2019"), ("2020", "2021", "2020-2021"),
                                  ("2022", "2022", "2022"), ("2023", config["corte"], "2023-corte")]:
        carteras, _, _ = comparar_carteras(todos.loc[inicio:fin], config, insumos)
        m = metricas(carteras)
        m["periodo"] = periodo
        m["meses"] = len(carteras)
        sensibilidad.append(m.reset_index(names="cartera"))
    sensibilidad = pd.concat(sensibilidad, ignore_index=True)
    sensibilidad.to_csv(salida / "sensibilidad_periodos.csv", index=False)
    costos = []
    for costo in (0, config["costo_por_dolar_transado"], 0.001):
        carteras, _, _ = comparar_carteras(r, config, insumos, costo)
        m = metricas(carteras)
        m["costo_pb_por_dolar"] = costo * 10000
        costos.append(m.reset_index(names="cartera"))
    pd.concat(costos).to_csv(salida / "sensibilidad_costos.csv", index=False)

    incertidumbre = []
    for nombre in portafolios.columns[1:]:
        delta = portafolios[nombre] - referencia
        for bloque in (3, 6, 12):
            inferior, superior = bootstrap_media(delta, bloque, config["bootstrap_repeticiones"], config["semilla"])
            incertidumbre.append({"cartera": nombre, "bloque_meses": bloque,
                                  "media_anualizada_pp": delta.mean() * 12 * 100,
                                  "ic95_inferior_pp": inferior, "ic95_superior_pp": superior})
    incertidumbre = pd.DataFrame(incertidumbre)
    incertidumbre.to_csv(salida / "incertidumbre.csv", index=False)

    sensibilidad_puts = []
    for strike in (0.90, 0.95, 1.00):
        for vol in (1.0, 1.25, 1.5):
            for h in (0.05, 0.10, 0.20):
                parametros = dict(config["puts"], strike_sobre_futuro=strike,
                                  multiplicador_vol=vol, nocional_sobre_fondo=h)
                sim, _ = cartera_puts(r, pesos.iloc[:, 0], insumos, parametros, config["costo_por_dolar_transado"])
                m = metricas(sim.to_frame("H2")).iloc[0].to_dict()
                sensibilidad_puts.append(dict(m, strike=strike, multiplicador_vol=vol, nocional=h))
    sensibilidad_puts = pd.DataFrame(sensibilidad_puts)
    sensibilidad_puts.to_csv(salida / "sensibilidad_puts.csv", index=False)
    sensibilidad_mbs = []
    for peso_mbs in (0.10, 0.15, 0.20):
        w = pesos.iloc[:, 0].copy()
        w.MBB = peso_mbs
        w.BIL += 0.15 - peso_mbs
        m = metricas(cartera(r, w, config["costo_por_dolar_transado"]).to_frame("MBS")).iloc[0].to_dict()
        sensibilidad_mbs.append(dict(m, peso_mbs_sobre_fondo=peso_mbs))
    sensibilidad_mbs = pd.DataFrame(sensibilidad_mbs)
    sensibilidad_mbs.to_csv(salida / "sensibilidad_mbs.csv", index=False)

    correlaciones = []
    for inicio, fin, periodo in [("2014", "2019", "2014-2019"), ("2020", "2021", "2020-2021"),
                                  ("2022", "2022", "2022"), ("2023", config["corte"], "2023-corte")]:
        sub = todos.loc[inicio:fin]
        for bono in ("SHY", "IEI", "IEF", "MBB"):
            correlaciones.append({"periodo": periodo, "bono": bono, "meses": len(sub),
                                   "correlacion_SPY": sub[bono].corr(sub.SPY),
                                   "ambos_negativos_meses": int(((sub[bono] < 0) & (sub.SPY < 0)).sum())})
    correlaciones = pd.DataFrame(correlaciones)
    correlaciones.to_csv(salida / "correlaciones.csv", index=False)
    estres = []
    for inicio, fin, periodo in [("2020-01", "2020-03", "2020 T1"), ("2022", "2022", "2022")]:
        estres.append(((1 + portafolios.loc[inicio:fin]).prod() - 1).rename(periodo))
    estres = pd.DataFrame(estres) * 100
    estres.to_csv(salida / "estres.csv")

    fx = pd.read_csv(RAIZ / f"data/raw/{config['tipo_cambio']}.csv", index_col=0, parse_dates=True).cierre
    fx_mensual = fx.resample("ME").last().loc[todos.index.min() - pd.offsets.MonthEnd(1):config["corte"]]
    fechas_fx = pd.Series(fx.dropna().index, index=fx.dropna().index).resample("ME").last()
    if fx_mensual.isna().any() or ((fechas_fx.index - pd.DatetimeIndex(fechas_fx)).days > 7).any():
        raise ValueError("Faltan cierres de FX. No rellenar.")
    cambio = fx_mensual.pct_change(fill_method=None).reindex(r.index)
    if cambio.isna().any():
        raise ValueError("FX sin alinear con carteras")
    clp = (1 + portafolios).mul(1 + cambio, axis=0) - 1
    clp.to_csv(salida / "retornos_carteras_clp.csv")
    metricas(clp).to_csv(salida / "metricas_clp.csv")

    plt.rcParams.update({"figure.figsize": (10, 5), "axes.spines.top": False,
                         "axes.spines.right": False, "axes.grid": True, "grid.alpha": 0.2})
    riqueza, caida = riqueza_y_caida(portafolios)
    origen = portafolios.index[0] - pd.offsets.MonthEnd(1)
    riqueza = pd.concat([pd.DataFrame(1., index=[origen], columns=riqueza.columns), riqueza])
    for tabla, nombre, titulo, unidad in [(100 * riqueza, "riqueza", "Referencia y una cartera por hipotesis: bloque USD", "USD por 100 iniciales"),
                                          (100 * caida, "caidas", "Caidas mensuales: cuatro hipotesis", "Caida (%)")]:
        ax = tabla.plot(title=titulo)
        ax.set_ylabel(unidad); ax.set_xlabel("")
        plt.tight_layout(); plt.savefig(figuras / f"{nombre}.png", dpi=160); plt.close()
    movil = pd.DataFrame({b: todos[b].rolling(12).corr(todos.SPY) for b in ("SHY", "IEI", "IEF", "MBB")})
    movil.to_csv(salida / "correlacion_movil_12m.csv")
    ax = movil.plot(title="Correlacion con SPY: retornos mensuales, ventana de 12 meses", ylim=(-1, 1))
    ax.axhline(0, color="black", linewidth=0.7); ax.set_ylabel("Correlacion"); ax.set_xlabel("")
    plt.tight_layout(); plt.savefig(figuras / "correlacion.png", dpi=160); plt.close()
    tasas = pd.concat([pd.read_csv(RAIZ / f"data/raw/{s}.csv", index_col=0, parse_dates=True)[s]
                       for s in ("DGS1MO", "DGS2", "DGS10")], axis=1)
    ax = tasas.loc[config["inicio_analisis"]:].plot(title="Tasas FRED: descuento de puts y contexto, no retornos")
    ax.set_ylabel("Tasa anual (%)"); ax.set_xlabel("")
    plt.tight_layout(); plt.savefig(figuras / "tasas.png", dpi=160); plt.close()
    fig, ax = plt.subplots()
    ax.bar(auditoria.index, auditoria.payoff_sobre_fondo * 100, width=20, label="Pago put (modelo)")
    ax.bar(auditoria.index, -(auditoria.prima_sobre_fondo + auditoria.friccion_sobre_fondo) * 100,
           width=20, label="Prima y friccion (modelo)")
    ax.set_title("H2: pagos y costo mensual de puts teoricas")
    ax.set_ylabel("% del capital total hipotetico al inicio del mes")
    ax.legend(); plt.tight_layout(); plt.savefig(figuras / "puts.png", dpi=160); plt.close()

    informe(config, resumen, pesos, estados, correlaciones, incertidumbre, sensibilidad,
            sensibilidad_puts, sensibilidad_mbs, auditoria, estres, metricas(clp), len(r))
    print(resumen.round(3).to_string())
    print(f"\nReferencia + {len(portafolios.columns) - 1} carteras. {len(r)} meses. Informe: {salida / 'informe.md'}")
    return resumen


def informe(config, resumen, pesos, estados, correlaciones, incertidumbre, sensibilidad,
            sensibilidad_puts, sensibilidad_mbs, auditoria, estres, clp, n):
    tabla_pesos = (100 * pesos.T).round(3)
    tabla_pesos["nocional_put_pct"] = [100 * config["puts"]["nocional_sobre_fondo"] if e["tipo"] == "puts" else 0
                                        for e in config["carteras"]]
    corr = correlaciones.pivot(index="periodo", columns="bono", values="correlacion_SPY")
    intervalo = incertidumbre.loc[incertidumbre.bloque_meses == 6]
    h2 = resumen.loc["H2 Puts cobre (modelo)"]
    prima_media = auditoria.prima_sobre_fondo.mean() * 12 * 100
    pago_medio = auditoria.payoff_sobre_fondo.mean() * 12 * 100
    cae_cobre = auditoria.futuro_final / auditoria.futuro_inicial - 1 < -0.05
    aporte_en_caidas = auditoria.loc[cae_cobre, "aporte_tras_costos_base"].mean() * 100
    rejilla = sensibilidad_puts.loc[np.isclose(sensibilidad_puts.nocional, config["puts"]["nocional_sobre_fondo"])]
    texto = f"""# FEES: una cartera por hipótesis

Se comparan **una referencia y cuatro carteras distintas**, una por idea del usuario. Datos hasta {config['corte']}, {n} meses desde enero de 2020. Ejecutar `python analisis.py` para regenerar todas las cifras.

La referencia aproxima el bloque USD de **69%** de la asignación estratégica. Faltan Europa 19%, Japón 9% y China 3%. Las métricas son por 100 invertidos en ese bloque y no representan el retorno del FEES completo. La política actual aplicada al pasado es un contrafactual, incluso antes de noviembre de 2023.

**H2 incluye primas y pagos teóricos de puts, no precios históricos observados de opciones.** Se incorpora para estudiar la idea, con su costo y sus límites. Simularla no significa que esté autorizada por la política vigente.

## Diseño de las cuatro carteras

- **H1, más letras:** mover 10 pp del fondo desde Treasury 7–10 años (IEF) hacia letras (BIL). Es la traducción propuesta por el asistente de reducir exposición a bonos largos cuando su correlación con acciones preocupa. No incorpora acciones ni activa señales según correlaciones futuras. Cambia la asignación estratégica.
- **H2, puts de cobre:** conservar la cartera de referencia y comprar puts hipotéticas cada mes. Nocional equivalente a 10% del fondo, strike 95% del precio inicial y plazo 1/12 de año. La prima y fricción se financian reduciendo BIL ese mes. No se posee un futuro descubierto.
- **H3, menor duración:** mover 2 pp desde IEF hacia SHY (Treasury 1–3 años). Conservar el 40% total de Treasuries, el 10% de letras y el 15% MBS.
- **H4, menos MBS:** reducir MBB del 15% al 10% y subir BIL del 10% al 15%. La sensibilidad también prueba 20% MBS. Estos cambios requieren modificar la asignación.

Pesos sobre el fondo completo, **no normalizados**. Suman 69%; el 31% no modelado se supone idéntico entre escenarios. La última columna es nocional subyacente de la opción y no se suma a los pesos de activos. La prima efectiva de H2 varía cada mes y se descuenta de BIL.

{tabla_pesos.to_markdown()}

## Filtro normativo

{estados.to_markdown()}

Las restricciones se mantienen como criterio de decisión: las carteras fuera de política se muestran como hipótesis y no se recomiendan para ejecución bajo las reglas actuales. Los ETFs son proxies, no órdenes elegibles certificadas. El TE realizado aproximado no reemplaza el cálculo ex ante del custodio. H2 y H4 no reciben un TE soberano, porque ese número no decidiría su admisibilidad.

## Comparación del bloque USD

Retorno compuesto y volatilidad anual en %, caída y peor mes en %. La caída incluye el capital inicial y solo observa cierres mensuales. Diferencia CAGR en puntos porcentuales; TE proxy en puntos base anuales del mandato soberano 85%, suponiendo idéntico el resto.

{resumen.round(3).to_markdown()}

![Referencia y cuatro carteras](figuras/riqueza.png)

![Caídas mensuales](figuras/caidas.png)

## Qué produce la simulación de puts

Con los supuestos centrales, H2 devuelve {h2.retorno_anual_pct:.2f}% anual del bloque, con caída máxima mensual de {h2.caida_max_mensual_pct:.2f}%. La prima media anualizada es {prima_media:.2f}% del capital total hipotético tras el costo de rebalanceo de cada mes y los pagos medios anualizados son {pago_medio:.2f}%. Son promedios mensuales por 12, no sumas de caja sobre un capital inicial constante.

Hubo {int(cae_cobre.sum())} meses de caída del proxy del cobre superior a 5%. En ellos, la diferencia media H2 menos referencia fue {aporte_en_caidas:.2f} pp mensuales del bloque. Esto describe la protección frente a ese subyacente y el costo del seguro. **No demuestra cobertura de ingresos fiscales ni de todas las pérdidas de bonos.** No se modelan ingresos tributarios, producción ni retiros del FEES.

![Primas y pagos de puts teóricas](figuras/puts.png)

El CSV `puts_auditoria.csv` guarda para cada mes precio inicial y final, strike, volatilidad histórica conocida al entrar, volatilidad del modelo, tasa, prima, fricción, pago y retorno. Permite seguir el cálculo de un mes sin una caja negra.

La valoración usa **Black-76 europeo**, con volatilidad de los 63 retornos diarios anteriores multiplicada por {config['puts']['multiplicador_vol']}. Ese multiplicador es un supuesto, no volatilidad implícita observada. Se añade fricción del {config['puts']['friccion_sobre_prima'] * 100:.0f}% de la prima. Se descuenta el rendimiento BIL sacrificado al pagar prima y fricción. El programa rechaza una prima superior a las letras disponibles.

`HG=F` es un proxy continuo: el precio inicial y final pueden corresponder a vencimientos distintos. Por ello se simula una **opción europea hipotética sobre ese proxy**, no contratos COMEX históricos identificados. No se replica el rollover de un contrato negociable, el ejercicio americano, la entrega del futuro, la malla de strikes, el spread real ni contratos enteros de 25.000 libras. Los resultados son condicionales y no constituyen un backtest ejecutable de opciones reales.

## Sensibilidad del seguro y de MBS

La siguiente tabla mantiene el nocional de 10% y varía strike y multiplicador de volatilidad. `sensibilidad_puts.csv` contiene las 27 combinaciones de strikes 90/95/100%, volatilidad histórica por 1/1,25/1,5 y nocionales 5/10/20%. Se muestran todas sin elegir la mejor.

{rejilla.round(3).to_markdown(index=False)}

Para MBS, cada cambio se financia con letras. El 15% es la referencia oficial; 10% y 20% son alternativas hipotéticas que cambian la asignación.

{sensibilidad_mbs.round(3).to_markdown(index=False)}

## Correlación, estrés e incertidumbre

La primera hipótesis se evalúa con su propia cartera y con el diagnóstico de correlación. SPY solo se usa para diagnóstico. Una correlación positiva no implica ausencia total de diversificación.

{corr.round(3).to_markdown()}

![Correlación móvil](figuras/correlacion.png)

Retornos acumulados en episodios fijados por calendario. H2 sigue dependiendo de primas teóricas.

{estres.round(3).to_markdown()}

Bootstrap pareado circular con {config['bootstrap_repeticiones']} repeticiones y semilla {config['semilla']}. Aquí se muestran bloques de seis meses; `incertidumbre.csv` también incluye 3 y 12. Intervalos individuales del 95% para diferencias de **medias mensuales por 12**, en pp anuales, no diferencias de CAGR. No corrigen comparaciones múltiples ni la selección retrospectiva. En H2 tampoco incorporan error de valoración de opciones.

{intervalo.round(3).to_markdown(index=False)}

`sensibilidad_periodos.csv` compara 2015–2019, 2020–2021, 2022 y 2023–corte con las mismas cinco carteras. La ventana anterior a 2020 comienza en 2015 para asegurar calentamiento de volatilidad del cobre. `sensibilidad_costos.csv` prueba 0/5/10 pb de costos de activos; la fricción propia de puts se mantiene separada.

## Moneda y límites

Conversión ilustrativa a CLP: `(1 + retorno USD) × (1 + cambio CLP por USD) − 1`, con Yahoo CLP=X. No es dólar observado y sus horarios pueden diferir del cierre de ETF.

{clp.round(3).to_markdown()}

Rebalanceo mensual, sin aportes ni retiros, con costo de {config['costo_por_dolar_transado'] * 10000:.0f} pb por dólar comprado o vendido, incluida la compra inicial. Los cierres ajustados aproximan reinversión de distribuciones y ya incluyen gastos internos de ETF. FRED DGS1MO se usa solo como proxy de descuento para la prima; DGS2/DGS10 dan contexto. Ninguna variación de tasas se interpreta como retorno de bonos.

La referencia divide el 40% Treasury en tercios SHY/IEI/IEF, supuesto que no replica ponderaciones por capitalización. STIP es TIPS 0–5 años, distinto del comparador 1–10. Los demás ETF también tienen desajustes de índice, gastos y gestión. Sin índices oficiales ni cartera global no se certifica rendimiento efectivo ni cumplimiento del FEES. Las hipótesis se diseñaron con conocimiento del pasado; no hay validación independiente fuera de muestra.

## Fuentes

[Política FEES](https://www.hacienda.cl/areas-de-trabajo/finanzas-internacionales/fondos-soberanos/fondo-de-estabilizacion-economica-y-social/politica-de-inversion), [directrices vigentes](https://www.hacienda.cl/areas-de-trabajo/finanzas-internacionales/fondos-soberanos/fondo-de-estabilizacion-economica-y-social/politica-de-inversion/pauta-de-inversion-vigente), [Yahoo cobre](https://finance.yahoo.com/quote/HG=F/), [FRED DGS1MO](https://fred.stlouisfed.org/series/DGS1MO), [Black (1976)](https://doi.org/10.1016/0304-405X(76)90024-6), [CME: opciones de cobre](https://www.cmegroup.com/markets/metals/base/copper.contractSpecs.options.html), [CME: datos históricos DataMine](https://www.cmegroup.com/datamine.html). Las URLs exactas y hashes de las descargas están en `data/metadatos.json`.

El alcance académico completo también requiere FRP. Siguen pendientes la revisión y defensa del equipo, el memo final y las firmas del anexo IA.
"""
    (RAIZ / "results/informe.md").write_text(texto)
    # Resumen portable para presentar las cinco carteras en el hilo.
    filas = []
    escala = max(resumen.retorno_anual_pct.abs().max(), 1)
    for nombre, fila in resumen.iterrows():
        valor = fila.retorno_anual_pct
        ancho = abs(valor) / escala * 48
        izquierda = 50 if valor >= 0 else 50 - ancho
        filas.append(f'<div class="fila"><span>{nombre}</span><div class="pista"><i class="cero"></i>'
                     f'<i class="barra" style="left:{izquierda:.1f}%;width:{ancho:.1f}%"></i></div>'
                     f'<strong>{valor:.2f}%</strong></div>')
    html = '''<!doctype html><html lang="es"><meta charset="utf-8"><style>
body{margin:0;color:var(--foreground);font-family:var(--font-sans)}h3{font-size:17px;margin:0 0 10px}
.nota{font-size:13px;color:var(--muted-foreground);line-height:1.5}
.fila{display:grid;grid-template-columns:170px minmax(0,1fr) 56px;align-items:center;gap:8px;height:43px;font-size:13px}
.pista{position:relative;height:26px;background:var(--secondary);border-radius:var(--radius)}
.cero{position:absolute;left:50%;height:100%;width:1px;background:var(--foreground);opacity:.4}
.barra{position:absolute;top:4px;height:18px;background:var(--chart-1);border-radius:3px}
strong{text-align:right;font-family:var(--font-mono)}
</style><body><h3>Referencia y una cartera por hipótesis</h3>
<p class="nota">Retorno compuesto anual del bloque USD (69% de la asignación), enero 2020–octubre 2026.</p>'''
    html += "".join(filas) + '''<p class="nota">H2 usa primas teóricas y un proxy continuo de cobre.
H1, H2 y H4 requieren cambios de política. Ninguna cartera tiene cumplimiento certificado.
Fuente: analisis.py, results/metricas.csv.</p></body></html>'''
    (RAIZ / "results/resumen.html").write_text(html)


if __name__ == "__main__":
    ejecutar()
