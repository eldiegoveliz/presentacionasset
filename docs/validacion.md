# Validación de la entrega

Verificación ejecutada por el asistente el 8 de noviembre de 2026. No equivale a revisión del equipo ni certificación del custodio.

## Flujo de datos y cálculos

Se ejecutaron `python datos.py`, `python analisis.py` y `python verificar.py` con Python 3.11. El entorno exacto está en `requirements-lock.txt`; las dependencias de instalación están en `requirements.txt`.

- Yahoo entregó siete ETFs con 3.248 observaciones diarias cada uno, desde el 2/12/2013 hasta el 30/10/2026.
- USD/CLP contiene 3.370 filas y ocho días sin cotización, conservados como faltantes. Se usa el último cierre observado del mes.
- FRED entregó DGS2 y DGS10. Sus ausencias por calendario se conservan como NA y no entran en retornos de carteras.
- Se obtuvieron 154 retornos mensuales desde enero de 2014, y 82 desde enero de 2020 para la muestra principal.
- Se comprobaron fechas comunes, meses completos y distribuciones. La máxima diferencia diaria entre ajuste Yahoo y reconstrucción con cierre más distribución fue menor a 3 pb, dentro del umbral de 10 pb fijado por el código. El detalle está en `results/calidad_datos.csv`.
- Se revisaron visualmente los gráficos de riqueza y correlación. Los cuatro PNG se generaron con 1.600 × 800 píxeles.

Las diez pruebas de `verificar.py` pasaron. Cubren pérdida inicial, retorno compuesto, costo inicial y rebalanceo, rechazo de pesos inválidos, conservación de asignación, ausencia de acciones, moneda CLP, hashes y contraste con resultados reales. La carga del análisis se probó con las solicitudes HTTP bloqueadas.

## Notebook y archivos entregados

El notebook se ejecutó completo mediante `nbclient` en un kernel nuevo, desde una carpeta temporal creada al extraer `entrega_fees.zip`. Se borró `results/` antes de ejecutar, de modo que todas las salidas se reconstruyeran. La instalación de paquetes se ejecutó con `PIP_NO_INDEX=1` sobre el entorno instalado, sin acceder a índices externos. No hubo celdas con error.

Se compararon byte por byte seis archivos regenerados frente a la ejecución del script: `metricas.csv`, `retornos_carteras_mensuales.csv`, `metricas_clp.csv`, `correlaciones.csv`, `incertidumbre.csv` e `informe.md`. Coincidieron. Esto comprueba un kernel limpio con archivos entregados, no una ejecución dentro del servicio web de Google Colab.

El notebook tiene código visible generado desde `analisis.py`. Se conservaron las salidas de la ejecución. El ZIP contiene código, datos, documentación, resultados y notebook; excluye `.git`, `.venv` y configuración de autenticación.

## Límites de la validación

No hay históricos de primas de opciones ni se simulan. No se replica el 31% extranjero del FEES. No se verificó el tracking error ex ante ni la elegibilidad de un portafolio ejecutable. La incertidumbre y las sensibilidades no convierten el backtest exploratorio en una prueba independiente de las hipótesis.
