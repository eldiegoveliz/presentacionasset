"""Comprobaciones de cálculos económicos y de los archivos realmente entregados."""
import hashlib
import json
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd

from datos import RAIZ, leer_config
from analisis import cartera, cargar_mensuales, metricas, pesos_escenario, riqueza_y_caida


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
        with self.assertRaises(ValueError):
            pesos_escenario(leer_config(), 0.5)

    def test_rechaza_cambio_mbs(self):
        c = leer_config()
        c["pesos_fondo_usd"]["MBB"] = 0.10
        c["pesos_fondo_usd"]["IEF"] += 0.05
        with self.assertRaises(ValueError):
            pesos_escenario(c, 0)

    def test_pesos_y_acciones(self):
        c = leer_config()
        for delta in c["traspasos_ief_a_shy"].values():
            w = pesos_escenario(c, delta)
            self.assertNotIn("SPY", w)
            self.assertAlmostEqual(w.sum(), 0.69)
            self.assertAlmostEqual(w.MBB, 0.15)
            self.assertAlmostEqual(w[["SHY", "IEI", "IEF"]].sum(), 0.40)


class ArchivosReales(unittest.TestCase):
    def test_integridad_datos(self):
        m = json.loads((RAIZ / "data/metadatos.json").read_text())
        c = leer_config()
        self.assertTrue(set(c["etfs"] + [c["tipo_cambio"], "DGS2", "DGS10"]).issubset(m["archivos"]))
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
        w = pesos_escenario(c, 0) / 0.69
        bruto_inicial = sum(w[t] * r[t].iloc[0] for t in w.index)
        esperado = (1 - c["costo_por_dolar_transado"]) * (1 + bruto_inicial) - 1
        guardado = pd.read_csv(RAIZ / "results/retornos_carteras_mensuales.csv", index_col=0)
        self.assertAlmostEqual(guardado.iloc[0, 0], esperado)
        resumen = pd.read_csv(RAIZ / "results/metricas.csv", index_col=0)
        riqueza_final = np.prod(1 + guardado.iloc[:, 0])
        self.assertAlmostEqual(resumen.iloc[0].retorno_anual_pct, (riqueza_final ** (12 / len(guardado)) - 1) * 100)

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
