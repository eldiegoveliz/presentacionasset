"""Motores de carteras: rebalanceo anual y puts con vencimiento fijo."""
from math import erf, exp, log, sqrt

import numpy as np
import pandas as pd


def precio_put_black76(futuro, strike, volatilidad, tasa, plazo):
    if futuro <= 0 or strike <= 0 or volatilidad < 0 or plazo < 0:
        raise ValueError("Parámetros inválidos para la put")
    if plazo == 0:
        return max(strike - futuro, 0)
    if volatilidad == 0:
        return exp(-tasa * plazo) * max(strike - futuro, 0)
    d1 = (log(futuro / strike) + 0.5 * volatilidad ** 2 * plazo) / (volatilidad * sqrt(plazo))
    d2 = d1 - volatilidad * sqrt(plazo)
    n1 = 0.5 * (1 + erf(-d1 / sqrt(2)))
    n2 = 0.5 * (1 + erf(-d2 / sqrt(2)))
    return exp(-tasa * plazo) * (strike * n2 - futuro * n1)


def cartera_anual(retornos, pesos, costo=0.0005):
    """Objetivo en enero; los pesos fluctúan entre rebalanceos."""
    w = pd.Series(pesos, dtype=float).reindex(retornos.columns, fill_value=0)
    if (w < 0).any() or not np.isclose(w.sum(), 1) or retornos.isna().any().any():
        raise ValueError("Pesos o retornos inválidos")
    actuales = w.copy()
    rendimientos, auditoria = [], []
    for i, (fecha, r) in enumerate(retornos.iterrows()):
        rebalanceo = i == 0 or fecha.month == 1
        volumen = 1. if i == 0 else (w - actuales).abs().sum() if rebalanceo else 0.
        if rebalanceo:
            actuales = w.copy()
        bruto = actuales.dot(r)
        rendimientos.append((1 - costo * volumen) * (1 + bruto) - 1)
        auditoria.append({"fecha": fecha, "rebalanceo": rebalanceo, "costo": costo * volumen, **actuales.to_dict()})
        actuales = actuales * (1 + r) / (1 + bruto)
    return pd.Series(rendimientos, index=retornos.index), pd.DataFrame(auditoria).set_index("fecha")


def put_larga(fees, cobre, volatilidad, tasa, parametros, costo=0.0005):
    """Un contrato sintético de 6/12 meses; strike y cantidad fijos hasta vencer.

    El cobre continuo se usa como proxy de spot, NO como contrato histórico fijo.
    F(t,T)=proxy(t)*exp(r*(T-t)), con almacenaje menos conveniencia supuesto cero.
    Se pagan prima y costos vendiendo parte del FEES; no se toma deuda.
    """
    plazo = parametros["plazo_meses"]
    if plazo not in (6, 12) or not 0 <= parametros["nocional"] <= 1:
        raise ValueError("Plazo o nocional inválido")
    core, valor_opcion, riqueza_anterior = 1., 0., 1.
    cantidad, strike, sigma, entrada = 0., 0., 0., None
    resultados, auditoria = [], []
    for i, (fecha, retorno_fees) in enumerate(fees.items()):
        compra = i % plazo == 0
        prima, friccion, comision = 0., 0., 0.
        if compra:
            entrada = fecha - pd.offsets.MonthEnd(1)
            s0, sigma_hist, r0 = cobre.loc[entrada], volatilidad.loc[entrada], tasa.loc[entrada]
            if not np.isfinite([s0, sigma_hist, r0]).all() or s0 <= 0 or sigma_hist <= 0:
                raise ValueError(f"Faltan datos previos para comprar put: {entrada}")
            sigma = sigma_hist * parametros["multiplicador_vol"]
            f0 = s0 * exp(r0 * plazo / 12)
            strike = parametros["strike_relativo"] * f0
            cantidad = parametros["nocional"] * riqueza_anterior / f0
            prima = cantidad * precio_put_black76(f0, strike, sigma, r0, plazo / 12)
            friccion = prima * parametros["friccion_sobre_prima"]
            comision = costo * (prima + friccion)
            core = riqueza_anterior - prima - friccion - comision
            if core < 0:
                raise ValueError("Prima sin financiación: no se permite endeudamiento")
        restante = (plazo - (i % plazo) - 1) / 12
        s, r_actual = cobre.loc[fecha], tasa.loc[fecha]
        futuro_modelo = s * exp(r_actual * restante)
        precio = precio_put_black76(futuro_modelo, strike, sigma, r_actual, restante)
        valor_opcion = cantidad * precio
        core *= 1 + retorno_fees
        riqueza = core + valor_opcion
        resultados.append(riqueza / riqueza_anterior - 1)
        auditoria.append({"fecha": fecha, "compra": compra, "entrada": entrada,
                          "plazo_restante_meses": restante * 12, "strike_fijo": strike,
                          "cantidad_fija": cantidad, "vol_compra_fija": sigma,
                          "prima_por_riqueza_previa": prima / riqueza_anterior,
                          "friccion_por_riqueza_previa": friccion / riqueza_anterior,
                          "comision_por_riqueza_previa": comision / riqueza_anterior,
                          "valor_opcion": valor_opcion, "valor_FEES": core,
                          "pago_vencimiento": valor_opcion if restante == 0 else 0,
                          "riqueza": riqueza})
        riqueza_anterior = riqueza
    return pd.Series(resultados, index=fees.index), pd.DataFrame(auditoria).set_index("fecha")


def riqueza_y_caida(retornos):
    riqueza = (1 + retornos).cumprod()
    return riqueza, riqueza / riqueza.cummax().clip(lower=1) - 1


def metricas(retornos):
    _, caida = riqueza_y_caida(retornos)
    return pd.DataFrame({"retorno_anual_pct": ((1 + retornos).prod() ** (12 / len(retornos)) - 1) * 100,
                         "volatilidad_anual_pct": retornos.std(ddof=1) * np.sqrt(12) * 100,
                         "caida_max_mensual_pct": caida.min() * 100,
                         "peor_mes_pct": retornos.min() * 100})
