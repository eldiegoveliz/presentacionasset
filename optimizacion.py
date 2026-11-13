"""Búsqueda exhaustiva y explicable: pesos en rejilla, sin cortos ni deuda."""
from itertools import product

import numpy as np
import pandas as pd


def generar_pesos(config):
    """Cinco estrategias; H2 (posición 2) limitada por riesgo de modelo."""
    n = round(1 / config["paso"])
    maximo = int(round(config["peso_max_estrategia"] * n))
    minimo_fees = int(round(config["peso_min_fees"] * n))
    max_put = int(round(config["peso_max_puts"] * n))
    candidatos = []
    for a, b, c, d in product(range(maximo+1), repeat=4):
        e = n - a - b - c - d
        if a >= minimo_fees and c <= max_put and 0 <= e <= maximo:
            candidatos.append([a/n, b/n, c/n, d/n, e/n])
    return np.asarray(candidatos)


def simular_mezclas(retornos, pesos, costo):
    """Simula todas las mezclas con pesos que fluctúan y rebalanceo en enero."""
    pesos = np.atleast_2d(pesos)
    actuales = pesos.copy()
    salida = np.empty((len(retornos), len(pesos)))
    for i, (fecha, r) in enumerate(retornos.iterrows()):
        if i == 0 or fecha.month == 1:
            volumen = np.ones(len(pesos)) if i == 0 else np.abs(actuales - pesos).sum(axis=1)
            actuales = pesos.copy()
        else:
            volumen = np.zeros(len(pesos))
        bruto = actuales @ r.to_numpy()
        salida[i] = (1 - costo * volumen) * (1 + bruto) - 1
        actuales = actuales * (1 + r.to_numpy()) / (1 + bruto[:, None])
    return pd.DataFrame(salida, index=retornos.index)


def elegir_pesos(trimestrales, crecimiento_pib, fecha_decision, config, candidatos):
    """PIB revisado con rezago conservador de 90 días; nunca usa trimestres posteriores."""
    conocidos = trimestrales.index + pd.Timedelta(days=config["rezago_pib_dias"]) <= pd.Timestamp(fecha_decision)
    conocidos &= crecimiento_pib.reindex(trimestrales.index).notna().to_numpy()
    malos = conocidos & (crecimiento_pib.reindex(trimestrales.index).to_numpy() < 0)
    if conocidos.sum() < config["min_trimestres"] or malos.sum() < config["min_contracciones"]:
        return None, None
    episodios = trimestrales.loc[malos].to_numpy()
    peor = episodios.min(axis=0)
    media = episodios.mean(axis=0)
    # Primero maximizar el peor trimestre de contracción. Desempatar por media
    # en contracciones y luego por menor concentración. No se usa CAGR total.
    orden = np.lexsort(((candidatos ** 2).sum(axis=1), -media, -peor))
    ranking = pd.DataFrame({"candidato": orden, "peor_contraccion_pct": peor[orden] * 100,
                            "media_contraccion_pct": media[orden] * 100,
                            "trimestres_conocidos": int(conocidos.sum()), "contracciones": int(malos.sum())})
    return int(orden[0]), ranking


def optimizar_progresivo(retornos, factor_clp_real, crecimiento_pib, config):
    candidatos = generar_pesos(config)
    mezclas_usd = simular_mezclas(retornos, candidatos, config["costo_rebalanceo"])
    mezclas_real = (1 + mezclas_usd).mul(factor_clp_real, axis=0) - 1
    trimestrales = (1 + mezclas_real).resample("QE").prod() - 1
    conteos = mezclas_real.resample("QE").count().iloc[:, 0]
    trimestrales = trimestrales.loc[conteos == 3]
    calendario, auditoria = {}, []
    for anio in sorted(set(retornos.index.year)):
        fecha = pd.Timestamp(anio, 1, 1)
        elegido, ranking = elegir_pesos(trimestrales, crecimiento_pib, fecha, config, candidatos)
        if elegido is not None:
            calendario[anio] = candidatos[elegido]
            fila = dict(zip(retornos.columns, candidatos[elegido]))
            fila.update(fecha=fecha, ultimo_pib_permitido=fecha-pd.Timedelta(days=config["rezago_pib_dias"]),
                        ultimo_trimestre_usado=trimestrales.index[(trimestrales.index + pd.Timedelta(days=config["rezago_pib_dias"]) <= fecha) & crecimiento_pib.reindex(trimestrales.index).notna()].max(),
                        trimestres_conocidos=int(ranking.iloc[0].trimestres_conocidos),
                        peor_contraccion_entrenamiento_pct=ranking.iloc[0].peor_contraccion_pct,
                        contracciones=int(ranking.iloc[0].contracciones))
            auditoria.append(fila)
    if not calendario:
        raise ValueError("Historia insuficiente para evaluar la optimización temporal")
    inicio = pd.Timestamp(min(calendario), 1, 1)
    sub = retornos.loc[inicio:]
    actuales, resultado, registros = None, [], []
    for i, (fecha, r) in enumerate(sub.iterrows()):
        objetivo = calendario[fecha.year]
        rebal = i == 0 or fecha.month == 1
        volumen = 1. if i == 0 else np.abs(objetivo - actuales).sum() if rebal else 0.
        if rebal:
            actuales = objetivo.copy()
        bruto = actuales @ r.to_numpy()
        resultado.append((1 - config["costo_rebalanceo"] * volumen) * (1 + bruto) - 1)
        registros.append(dict(fecha=fecha, rebalanceo=rebal, **dict(zip(retornos.columns, actuales))))
        actuales = actuales * (1 + r.to_numpy()) / (1 + bruto)
    decision_final = retornos.index[-1] + pd.Timedelta(days=1)
    elegido, ranking = elegir_pesos(trimestrales, crecimiento_pib, decision_final, config, candidatos)
    pesos_finales = pd.Series(candidatos[elegido], index=retornos.columns)
    ranking = ranking.merge(pd.DataFrame(candidatos, columns=retornos.columns).reset_index(names="candidato"),
                            on="candidato", how="left", sort=False)
    # Sensibilidad: retirar una contracción cada vez y volver a elegir.
    sensibilidad = []
    malos_finales = crecimiento_pib.loc[crecimiento_pib < 0].index.intersection(trimestrales.index)
    for fecha in malos_finales:
        pib_sin_episodio = crecimiento_pib.drop(fecha)
        ix, _ = elegir_pesos(trimestrales, pib_sin_episodio, decision_final, config, candidatos)
        if ix is not None:
            sensibilidad.append(dict(episodio_excluido=fecha, **dict(zip(retornos.columns, candidatos[ix]))))
    return {"retornos_usd": pd.Series(resultado, index=sub.index, name="H5 Optimo temporal"),
            "pesos_finales": pesos_finales, "pesos_anuales": pd.DataFrame(auditoria).set_index("fecha"),
            "pesos_mensuales": pd.DataFrame(registros).set_index("fecha"), "ranking": ranking,
            "sensibilidad": pd.DataFrame(sensibilidad), "candidatos": len(candidatos),
            "casi_optimos_002pp": int((ranking.peor_contraccion_pct >= ranking.peor_contraccion_pct.iloc[0] - .02).sum())}
