"""Comprobaciones de cálculos económicos y de los archivos realmente entregados."""
import hashlib
import json
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd

from datos import RAIZ, leer_config
from analisis import (cartera, cargar_mensuales, metricas, pesos_escenario, riqueza_y_caida,
                      precio_put_black76, preparar_insumos_puts, cartera_puts,
                      clasificar_carteras, cargar_insumos_puts, comparar_carteras)


class Calculos(unittest.TestCase):
    def test_perdida_inicial_incluida(self):
        r = pd.DataFrame({"fondo": [-0.2, 0.1]})
        riqueza, caida = riqueza_y_caida(r)
        self.assertAlmostEqual(riqueza.fondo.iloc[-1], 0.88)
        self.assertAlmostEqual(caida.fondo.min(), -0.2)

    def test_rebalanceo_y_costos(self):
        # Primer mes: 50/50, uno gana 20% y otro pierde 20%.
        # Segundo mes: los pesos vuelven a 50/50. Se transa 20% del capital.
        r = pd.DataFrame({"a": [0.2, 0.1], "b": [-0.2, 0.1]})
        neto = cartera(r, pd.Series({"a": 0.5, "b": 0.5}), 0.001)
        self.assertAlmostEqual(neto.iloc[0], -0.001)
        self.assertAlmostEqual(neto.iloc[1], (1 - 0.001 * 0.2) * 1.1 - 1)

    def test_cagr_compuesto(self):
        r = pd.DataFrame({"fondo": [0.01] * 12})
        self.assertAlmostEqual(metricas(r).loc["fondo", "retorno_anual_pct"], (1.01 ** 12 - 1) * 100)

    def test_rechaza_traspaso_excesivo(self):
        c = leer_config()
        e = dict(c["carteras"][1], traspaso=0.5)
        with self.assertRaises(ValueError):
            pesos_escenario(c, e)

    def test_rechaza_cambio_mbs_en_escenario_duracion(self):
        c = leer_config()
        c["pesos_fondo_usd"]["MBB"] = 0.10
        c["pesos_fondo_usd"]["IEF"] += 0.05
        with self.assertRaises(ValueError):
            pesos_escenario(c, c["carteras"][3])

    def test_pesos_y_acciones(self):
        c = leer_config()
        for escenario in c["carteras"]:
            w = pesos_escenario(c, escenario)
            self.assertNotIn("SPY", w)
            self.assertAlmostEqual(w.sum(), 0.69)
            if escenario["tipo"] in ("referencia", "duracion", "puts"):
                self.assertAlmostEqual(w.MBB, 0.15)
                self.assertAlmostEqual(w[["SHY", "IEI", "IEF"]].sum(), 0.40)

    def test_una_cartera_por_hipotesis_y_estado_normativo(self):
        c = leer_config()
        self.assertEqual([e["tipo"] for e in c["carteras"]], ["referencia", "liquidez", "puts", "duracion", "mbs"])
        estados = clasificar_carteras(c)
        self.assertIn("fuera de la politica", estados.loc["H2 Puts cobre (modelo)", "estado_normativo"])
        self.assertIn("cambiar", estados.loc["H4 Menos MBS", "estado_normativo"])

    def test_prima_black76_caso_cerrado_y_limites(self):
        # F=K=100, sigma=20%, T=1, r=0: 100*(2*N(0.1)-1).
        self.assertAlmostEqual(precio_put_black76(100, 100, 0.2, 0, 1), 7.9655674554, places=8)
        self.assertEqual(precio_put_black76(100, 95, 0.2, 0.02, 0), 0)
        self.assertEqual(precio_put_black76(80, 95, 0.2, 0.02, 0), 15)
        self.assertGreater(precio_put_black76(100, 95, 0.4, 0.02, 1/12),
                           precio_put_black76(100, 95, 0.2, 0.02, 1/12))

    def test_put_financiada_y_pago(self):
        c = leer_config()
        fecha = pd.to_datetime(["2020-01-31"])
        w = pesos_escenario(c, c["carteras"][0])
        r = pd.DataFrame(0., index=fecha, columns=w.index)
        entrada = pd.DataFrame({"futuro_inicial": [100.], "futuro_final": [80.],
                                "sigma_hist_entrada": [0.3], "tasa_entrada": [0.02]}, index=fecha)
        resultado, auditoria = cartera_puts(r, w, entrada, c["puts"], 0)
        p = precio_put_black76(100, 95, 0.3 * 1.25, 0.02, 1/12)
        esperado = (0.10 * 15/100 - 0.10 * p/100 * 1.10) / 0.69
        self.assertAlmostEqual(resultado.iloc[0], esperado)
        self.assertAlmostEqual(auditoria.payoff_sobre_fondo.iloc[0], 0.015)
        entrada["futuro_final"] = 110.
        sin_pago, _ = cartera_puts(r, w, entrada, c["puts"], 0)
        self.assertAlmostEqual(sin_pago.iloc[0], -0.10 * p/100 * 1.10 / 0.69)

    def test_cobertura_cero_reproduce_referencia(self):
        c = leer_config()
        r, _ = cargar_mensuales(c)
        r = r.loc["2020":]
        w = pesos_escenario(c, c["carteras"][0])
        parametros = dict(c["puts"], nocional_sobre_fondo=0)
        sim, _ = cartera_puts(r, w, cargar_insumos_puts(c), parametros, c["costo_por_dolar_transado"])
        np.testing.assert_allclose(sim, cartera(r, w, c["costo_por_dolar_transado"]), atol=1e-14)

    def test_rebalanceo_incluye_pago_del_seguro(self):
        c = leer_config()
        fechas = pd.to_datetime(["2020-01-31", "2020-02-29"])
        w = pesos_escenario(c, c["carteras"][0])
        r = pd.DataFrame(0., index=fechas, columns=w.index)
        entrada = pd.DataFrame({"futuro_inicial": [100., 80.], "futuro_final": [80., 80.],
                                "sigma_hist_entrada": [0.3, 0.3], "tasa_entrada": [0., 0.]}, index=fechas)
        _, a = cartera_puts(r, w, entrada, c["puts"], 0.001)
        # Con activos planos, solo cambia BIL. Para volver al objetivo se
        # vende parte del pago y se compra el resto de activos.
        ganancia = a.aporte_neto_bloque.iloc[0]
        peso_bil = w.BIL / w.sum()
        volumen = 2 * abs(ganancia) * (1 - peso_bil) / (1 + ganancia)
        self.assertAlmostEqual(a.costo_rebalanceo_bloque.iloc[1], 0.001 * volumen)
        self.assertGreater(a.costo_rebalanceo_bloque.iloc[1], 0)

    def test_prima_sin_datos_futuros(self):
        fechas = pd.bdate_range("2020-01-01", "2021-06-30")
        rng = np.random.default_rng(17)
        cobre = pd.Series(100 * np.exp(np.cumsum(rng.normal(0, 0.01, len(fechas)))), index=fechas)
        tasas = pd.Series(2., index=fechas)
        original = preparar_insumos_puts(cobre, tasas, 63)
        cobre.loc["2021-02-01":] *= 2
        tasas.loc["2021-02-01":] = 10
        cambiado = preparar_insumos_puts(cobre, tasas, 63)
        for columna in ("futuro_inicial", "sigma_hist_entrada", "tasa_entrada"):
            self.assertEqual(original.loc["2021-02-28", columna], cambiado.loc["2021-02-28", columna])

    def test_rechaza_prima_superior_al_efectivo(self):
        c = leer_config()
        fecha = pd.to_datetime(["2020-01-31"])
        w = pesos_escenario(c, c["carteras"][0])
        r = pd.DataFrame(0., index=fecha, columns=w.index)
        entrada = pd.DataFrame({"futuro_inicial": [100.], "futuro_final": [80.],
                                "sigma_hist_entrada": [3.], "tasa_entrada": [0.]}, index=fecha)
        parametros = dict(c["puts"], nocional_sobre_fondo=1)
        with self.assertRaisesRegex(ValueError, "letras disponibles"):
            cartera_puts(r, w, entrada, parametros, 0)


class ArchivosReales(unittest.TestCase):
    def test_integridad_datos(self):
        m = json.loads((RAIZ / "data/metadatos.json").read_text())
        c = leer_config()
        self.assertTrue(set(c["etfs"] + [c["tipo_cambio"], c["cobre"], "DGS1MO", "DGS2", "DGS10"]).issubset(m["archivos"]))
        for archivo, sha in m["sha256"].items():
            self.assertEqual(hashlib.sha256((RAIZ / archivo).read_bytes()).hexdigest(), sha, archivo)
        fuentes = json.loads((RAIZ / "data/fuentes/metadatos.json").read_text())
        for archivo, registro in fuentes.items():
            self.assertEqual(hashlib.sha256((RAIZ / "data/fuentes" / archivo).read_bytes()).hexdigest(), registro["sha256"])

    def test_analisis_no_necesita_red(self):
        with patch("requests.get", side_effect=AssertionError("El análisis no debe llamar APIs")):
            r, calidad = cargar_mensuales(leer_config())
        self.assertEqual(len(r.loc["2020":]), 82)
        self.assertEqual(str(r.index[-1].date()), "2026-10-31")
        self.assertLess(calidad.max_error_retorno_pb.max(), 10)

    def test_resultados_vs_activos(self):
        # Contraste independiente del retorno mensual bruto con un ejemplo real.
        c = leer_config()
        r, _ = cargar_mensuales(c)
        r = r.loc[c["inicio_analisis"]:]
        w = pesos_escenario(c, c["carteras"][0]) / 0.69
        bruto_inicial = sum(w[t] * r[t].iloc[0] for t in w.index)
        esperado = (1 - c["costo_por_dolar_transado"]) * (1 + bruto_inicial) - 1
        guardado = pd.read_csv(RAIZ / "results/retornos_carteras_mensuales.csv", index_col=0)
        self.assertAlmostEqual(guardado.iloc[0, 0], esperado)
        resumen = pd.read_csv(RAIZ / "results/metricas.csv", index_col=0)
        riqueza_final = np.prod(1 + guardado.iloc[:, 0])
        self.assertAlmostEqual(resumen.iloc[0].retorno_anual_pct, (riqueza_final ** (12 / len(guardado)) - 1) * 100)

    def test_cinco_carteras_reales_sin_red(self):
        c = leer_config()
        with patch("requests.get", side_effect=AssertionError("No llamar APIs al analizar")):
            r, _ = cargar_mensuales(c)
            resultado, _, auditoria = comparar_carteras(r.loc["2020":], c, cargar_insumos_puts(c))
        self.assertEqual(resultado.shape, (82, 5))
        self.assertFalse(resultado.isna().any().any())
        self.assertTrue((auditoria.prima_sobre_fondo >= 0).all())
        self.assertTrue((auditoria.payoff_sobre_fondo >= 0).all())
        self.assertFalse(np.allclose(resultado.iloc[:, 0], resultado.iloc[:, 2]))
        raw = json.loads((RAIZ / "data/raw/HG=F.json").read_text())["chart"]["result"][0]
        self.assertEqual(raw["meta"]["instrumentType"], "FUTURE")

    def test_moneda_clp(self):
        # Evita confundir DEXCHUS (yuan chino) con peso chileno.
        c = leer_config()
        raw = json.loads((RAIZ / f"data/raw/{c['tipo_cambio']}.json").read_text())["chart"]["result"][0]
        self.assertEqual(raw["meta"]["currency"], "CLP")
        self.assertEqual(raw["meta"]["symbol"], "CLP=X")
        self.assertEqual(raw["meta"]["instrumentType"], "CURRENCY")
        fx = pd.read_csv(RAIZ / "data/raw/CLP=X.csv", index_col=0, parse_dates=True).cierre
        cambio = fx.resample("ME").last().pct_change(fill_method=None)
        usd = pd.read_csv(RAIZ / "results/retornos_carteras_mensuales.csv", index_col=0, parse_dates=True)
        clp = pd.read_csv(RAIZ / "results/retornos_carteras_clp.csv", index_col=0, parse_dates=True)
        esperado = (1 + usd.iloc[:, 0]) * (1 + cambio.reindex(usd.index)) - 1
        np.testing.assert_allclose(clp.iloc[:, 0], esperado, rtol=1e-10, atol=1e-12)


if __name__ == "__main__":
    unittest.main(verbosity=2)
