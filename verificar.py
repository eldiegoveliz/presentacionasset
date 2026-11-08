"""Verifica dinero, datos oficiales, vencimientos y decisiones sin futuro."""
import hashlib
import json
import re
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd

from datos import RAIZ, leer_config
from datos_oficiales import extraer_retorno, bcch_movil
from carteras import cartera_anual, put_larga, precio_put_black76, riqueza_y_caida
from optimizacion import generar_pesos, simular_mezclas, elegir_pesos
from analisis import cargar_datos


class Motores(unittest.TestCase):
    def test_caida_inicial(self):
        _, d = riqueza_y_caida(pd.DataFrame({"x": [-.2, .1]}))
        self.assertAlmostEqual(d.x.min(), -.2)

    def test_rebalanceo_anual_con_drift(self):
        fechas = pd.to_datetime(["2019-11-30", "2019-12-31", "2020-01-31"])
        r = pd.DataFrame({"a": [.2, .1, .1], "b": [-.2, -.1, -.1]}, index=fechas)
        serie, audit = cartera_anual(r, {"a": .5, "b": .5}, .001)
        self.assertAlmostEqual(serie.iloc[0], -.001)
        self.assertAlmostEqual(serie.iloc[1], .02)
        self.assertEqual(audit.rebalanceo.tolist(), [True, False, True])
        self.assertAlmostEqual(audit.a.iloc[1], .6)
        self.assertAlmostEqual(audit.a.iloc[2], .5)
        self.assertGreater(audit.costo.iloc[2], 0)

    def test_rechaza_pesos_inventados(self):
        r = pd.DataFrame({"a": [0.], "b": [0.]}, index=pd.to_datetime(["2020-01-31"]))
        with self.assertRaises(ValueError):
            cartera_anual(r, {"a": 1.1, "b": -.1})

    def test_black76_caso_cerrado(self):
        self.assertAlmostEqual(precio_put_black76(100, 100, .2, 0, 1), 7.9655674554, places=8)
        self.assertEqual(precio_put_black76(80, 95, .2, .02, 0), 15)

    def escenario_put(self, meses=24):
        fechas = pd.date_range("2019-01-31", periods=meses, freq="ME")
        precio = pd.Series(100., index=pd.date_range("2018-12-31", periods=meses+1, freq="ME"))
        sigma = pd.Series(.2, index=precio.index)
        tasa = pd.Series(0., index=precio.index)
        fees = pd.Series(0., index=fechas)
        return fees, precio, sigma, tasa, dict(leer_config()["puts"])

    def test_puts_son_anuales_no_mensuales(self):
        fees, precio, sigma, tasa, params = self.escenario_put()
        _, a = put_larga(fees, precio, sigma, tasa, params, 0)
        self.assertEqual(int(a.compra.sum()), 2)
        self.assertEqual(a.loc["2019", "strike_fijo"].nunique(), 1)
        self.assertEqual(a.loc["2019", "cantidad_fija"].nunique(), 1)
        self.assertEqual(a.plazo_restante_meses.round().tolist(), list(range(11,-1,-1))*2)

    def test_put_semestral_renueva_dos_veces_anio(self):
        fees, precio, sigma, tasa, params = self.escenario_put()
        params["plazo_meses"] = 6
        _, a = put_larga(fees, precio, sigma, tasa, params, 0)
        self.assertEqual(int(a.compra.sum()), 4)

    def test_put_cero_reproduce_fees(self):
        fees, precio, sigma, tasa, params = self.escenario_put()
        fees.iloc[0] = -.01
        params["nocional"] = 0
        sim, _ = put_larga(fees, precio, sigma, tasa, params)
        np.testing.assert_allclose(sim, fees, atol=1e-14)

    def test_financiacion_y_pago_unico(self):
        fees, precio, sigma, tasa, params = self.escenario_put()
        precio.loc["2019-12-31":] = 80
        sim, a = put_larga(fees, precio, sigma, tasa, params, 0)
        prima = .1 / 100 * precio_put_black76(100, 95, .2*1.25, 0, 1)
        esperado = 1 - prima*1.1 + .1/100*15
        self.assertAlmostEqual(a.loc["2019-12-31", "riqueza"], esperado)
        self.assertAlmostEqual((1+sim.loc["2019"]).prod(), esperado)
        self.assertAlmostEqual(a.loc["2020-01-31", "cantidad_fija"], .1*esperado/80)

    def test_put_pendiente_no_se_cierra_artificialmente(self):
        fees, precio, sigma, tasa, params = self.escenario_put(9)
        _, a = put_larga(fees, precio, sigma, tasa, params)
        self.assertEqual(round(a.plazo_restante_meses.iloc[-1]), 3)
        self.assertGreater(a.valor_opcion.iloc[-1], 0)
        self.assertEqual(a.pago_vencimiento.iloc[-1], 0)

    def test_compra_no_usa_precio_futuro(self):
        fees, precio, sigma, tasa, params = self.escenario_put()
        _, antes = put_larga(fees, precio, sigma, tasa, params, 0)
        precio.loc["2019-02-28":] *= 1.3
        _, despues = put_larga(fees, precio, sigma, tasa, params, 0)
        for campo in ("strike_fijo", "cantidad_fija", "vol_compra_fija", "prima_por_riqueza_previa"):
            self.assertEqual(antes.iloc[0][campo], despues.iloc[0][campo])


class Optimizacion(unittest.TestCase):
    def test_rejilla_respeta_limites(self):
        c = leer_config()["optimizacion"]
        w = generar_pesos(c)
        np.testing.assert_allclose(w.sum(axis=1), 1)
        self.assertTrue((w >= 0).all())
        self.assertTrue((w[:,0] >= c["peso_min_fees"]).all())
        self.assertTrue((w <= c["peso_max_estrategia"] + 1e-12).all())
        self.assertTrue((w[:,2] <= .25).all())
        np.testing.assert_allclose(w / .05, np.round(w / .05))

    def test_simulacion_vectorizada_vs_tenencias(self):
        fechas = pd.date_range("2019-01-31", periods=25, freq="ME")
        r = pd.DataFrame(np.random.default_rng(3).normal(0,.02,(25,5)), index=fechas)
        w = np.array([.2]*5)
        vector = simular_mezclas(r, w, .0005).iloc[:,0]
        manual, _ = cartera_anual(r, dict(zip(r.columns,w)), .0005)
        np.testing.assert_allclose(vector, manual, atol=1e-14)

    def test_objetivo_elige_mejor_peor_contraccion(self):
        fechas = pd.date_range("2020-03-31", periods=4, freq="QE")
        r = pd.DataFrame({0:[-.1,-.1,10,10],1:[-.05,-.04,-10,-10]}, index=fechas)
        pib = pd.Series([-.01,-.01,-.5,-.5], index=fechas)
        c = dict(leer_config()["optimizacion"], min_trimestres=2, min_contracciones=1)
        candidatos = np.array([[1,0,0,0,0],[0,1,0,0,0]])
        i, _ = elegir_pesos(r,pib,"2020-10-01",c,candidatos)
        self.assertEqual(i,1)

    def test_decision_no_cambia_con_trimestres_futuros(self):
        fechas = pd.date_range("2020-03-31", periods=4, freq="QE")
        r = pd.DataFrame({0:[-.1,-.1,10,10],1:[-.05,-.04,-10,-10]}, index=fechas)
        pib = pd.Series([-.01,-.01,-.5,-.5], index=fechas)
        c = dict(leer_config()["optimizacion"], min_trimestres=2, min_contracciones=1)
        w = np.array([[1,0,0,0,0],[0,1,0,0,0]])
        antes, _ = elegir_pesos(r,pib,"2020-10-01",c,w)
        r.loc["2020-09-30":] *= -100
        pib.loc["2020-09-30":] = 10
        despues, _ = elegir_pesos(r,pib,"2020-10-01",c,w)
        self.assertEqual(antes,despues)

    def test_rechaza_historia_insuficiente(self):
        r = pd.DataFrame({0:[0]},index=pd.to_datetime(["2020-03-31"]))
        i, _ = elegir_pesos(r,pd.Series([-.1],index=r.index),"2020-10-01",leer_config()["optimizacion"],np.array([[1,0,0,0,0]]))
        self.assertIsNone(i)


class DatosYEntrega(unittest.TestCase):
    def test_retornos_extraidos_y_unicode(self):
        self.assertEqual(extraer_retorno("Retorno\xa0en\xa0USD (3) -1,66% 3,2%")[0],-.0166)
        self.assertEqual(extraer_retorno("Retorno en USD 0.62% 8.56%")[0],.0062)
        with self.assertRaises(ValueError):
            extraer_retorno("Valor del fondo aumentó por aportes")

    def test_153_retornos_cotejados_con_prosa(self):
        archivos = sorted((RAIZ/"data/oficial/fees_textos").glob("*.json"))
        self.assertEqual(len(archivos),153)
        for p in archivos:
            d = json.loads(p.read_text())
            texto = p.with_suffix(".txt").read_text().replace("\xa0"," ")
            m = re.search(r"[Ll]a rentabilidad.{0,70}?(?:mes|mensual).{0,60}?fue.{0,15}?(-?\d+[,.]\d+)\s*%\s*en\s*d[oó]lares",texto,re.S)
            self.assertIsNotNone(m,p.name)
            self.assertAlmostEqual(float(m[1].replace(",","."))/100,d["retorno_usd"])

    def test_hashes_oficiales_y_mercado(self):
        for archivo in ["data/metadatos.json","data/oficial/metadatos.json"]:
            for nombre, sha in json.loads((RAIZ/archivo).read_text())["sha256"].items():
                self.assertEqual(hashlib.sha256((RAIZ/nombre).read_bytes()).hexdigest(),sha,nombre)

    def test_carga_sin_red_y_sin_yahoo_fx(self):
        original = pd.read_csv
        def leer(ruta,*args,**kwargs):
            if "CLP=X" in str(ruta):
                raise AssertionError("Debe usar dólar observado BCCh")
            return original(ruta,*args,**kwargs)
        with patch("requests.get",side_effect=AssertionError("No usar red al analizar")),patch("pandas.read_csv",side_effect=leer):
            r, fx, real, pib, *_ = cargar_datos(leer_config())
        self.assertEqual(len(r),153)
        self.assertFalse(real.isna().any())
        self.assertEqual(str(pib.dropna().index[-1].date()),"2026-06-30")

    def test_dolar_oficial_tiene_valor_verificable(self):
        d = pd.read_csv(RAIZ/"data/oficial/bcch_dolar.csv",index_col=0)
        self.assertAlmostEqual(d.loc["2026-10-30"].iloc[0],993.22)

    def test_fees_referencia_es_observado(self):
        oficial = pd.read_csv(RAIZ/"data/oficial/fees_mensual.csv",index_col=0).retorno_usd
        generado = pd.read_csv(RAIZ/"results/retornos_carteras_usd.csv",index_col=0)
        self.assertEqual(generado.shape,(153,6))
        np.testing.assert_allclose(generado.iloc[:,0],oficial)
        self.assertTrue(generado.iloc[:60,-1].isna().all())

    def test_conversion_compuesta_clp_real(self):
        usd = pd.read_csv(RAIZ/"results/retornos_carteras_usd.csv",index_col=0)
        clp = pd.read_csv(RAIZ/"results/retornos_carteras_clp.csv",index_col=0)
        real = pd.read_csv(RAIZ/"results/retornos_carteras_clp_real.csv",index_col=0)
        factor = pd.read_csv(RAIZ/"results/conversion_bcch.csv",index_col=0)
        np.testing.assert_allclose(clp.iloc[:,0],(1+usd.iloc[:,0])*factor.iloc[:,0]-1,atol=1e-14)
        np.testing.assert_allclose(real.iloc[:,0],(1+usd.iloc[:,0])*factor.iloc[:,1]-1,atol=1e-14)

    def test_fechas_pib_conocidas_antes_de_pesos(self):
        a = pd.read_csv(RAIZ/"results/pesos_optimos_anuales.csv",parse_dates=["fecha","ultimo_trimestre_usado"])
        self.assertTrue((a.ultimo_trimestre_usado + pd.Timedelta(days=90) <= a.fecha).all())
        self.assertTrue((a.trimestres_conocidos >= 20).all())

    def test_presupuesto_y_nocional_no_se_duplican(self):
        e = pd.read_csv(RAIZ/"results/exposicion_optima.csv",index_col=0).iloc[:,0]
        self.assertAlmostEqual(e.iloc[:4].sum(),1)
        w = pd.read_csv(RAIZ/"results/pesos_optimos_finales.csv",index_col=0).iloc[:,0]
        self.assertAlmostEqual(e.iloc[-1],.1*w.iloc[2])


if __name__ == "__main__":
    unittest.main(verbosity=2)
