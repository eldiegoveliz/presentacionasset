# Validación de la entrega

Verificación ejecutada por el asistente el 8 de noviembre de 2026. No equivale a revisión del equipo ni certificación del custodio.

## Flujo de datos y cálculos

Se ejecutaron `python datos.py`, `python analisis.py` y `python verificar.py` con Python 3.11. El entorno exacto está en `requirements-lock.txt`; las dependencias de instalación están en `requirements.txt`.

- Yahoo entregó siete ETFs con 3.248 observaciones diarias cada uno, desde el 2/12/2013 hasta el 30/10/2026.
- USD/CLP contiene 3.370 filas y ocho días sin cotización, conservados como faltantes. Se usa el último cierre observado del mes.
- Se añadieron HG=F y DGS1MO sin reemplazar los ETF congelados. HG=F contiene 3.253 observaciones. FRED DGS1MO descuenta las primas; DGS2/DGS10 sirven como contexto. Sus variaciones no se usan como retornos de bonos.
- Se obtuvieron 154 retornos mensuales desde enero de 2014, y 82 desde enero de 2020 para la muestra principal.
- Se comprobaron fechas comunes, meses completos y distribuciones. La máxima diferencia diaria entre ajuste Yahoo y reconstrucción con cierre más distribución fue menor a 3 pb, dentro del umbral de 10 pb fijado por el código. El detalle está en `results/calidad_datos.csv`.
- Se inspeccionaron los gráficos generados de riqueza y puts para comprobar leyendas, unidades y visibilidad de las cinco carteras. Los cinco PNG se generaron con 1.600 × 800 píxeles.

Las dieciocho pruebas de `verificar.py` pasaron. Cubren pérdida inicial, retorno compuesto, costos, pesos y clasificación normativa, cinco carteras distintas, prima Black-76 con un caso numérico cerrado, financiación desde BIL, payoff, rechazo de primas no financiables, ausencia de datos futuros en la entrada, cobertura cero equivalente a referencia, moneda CLP, hashes y resultados reales. La carga del análisis se probó con las solicitudes HTTP bloqueadas.

## Notebook y archivos entregados

Para repetir la comprobación: `python validar_notebook.py`. El script genera un kernel temporal con el Python actual, ejecuta la entrega, compara las nueve salidas y guarda el ZIP actualizado.

El notebook se ejecutó completo mediante `nbclient` en un kernel nuevo, desde una carpeta temporal creada al extraer `entrega_fees.zip`. Se borró `results/` antes de ejecutar, de modo que todas las salidas se reconstruyeran. La instalación de paquetes se ejecutó con `PIP_NO_INDEX=1` sobre el entorno instalado, sin acceder a índices externos. No hubo celdas con error.

Se compararon byte por byte nueve archivos regenerados frente a la ejecución del script: `metricas.csv`, `retornos_carteras_mensuales.csv`, `metricas_clp.csv`, `correlaciones.csv`, `incertidumbre.csv`, `informe.md`, `puts_auditoria.csv`, `sensibilidad_puts.csv` y `sensibilidad_mbs.csv`. Coincidieron. Esto comprueba un kernel limpio con archivos entregados, no una ejecución dentro del servicio web de Google Colab.

El notebook tiene código visible generado desde `analisis.py`. Se conservaron las salidas de la ejecución. El ZIP contiene código, datos, documentación, resultados y notebook; excluye `.git`, `.venv` y configuración de autenticación.

## Límites de la validación

No hay primas históricas observadas: se simulan opciones europeas sobre el proxy continuo, con primas Black-76. Los pagos, primas, fricción y financiación se guardan por mes. Se prueban 27 combinaciones de supuestos y pesos MBS de 10/15/20%. No se replica el 31% extranjero del FEES. No se verificó el tracking error ex ante ni la elegibilidad de un portafolio ejecutable. La incertidumbre y las sensibilidades no convierten el backtest exploratorio en una prueba independiente de las hipótesis.
