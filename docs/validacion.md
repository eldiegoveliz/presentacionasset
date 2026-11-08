# Validación de la entrega anticíclica

Validación del asistente, no revisión académica ni certificación del custodio. Entorno Python 3.11, con versiones exactas en requirements-lock.txt.

## Fuentes realmente utilizadas

Se obtuvieron 153 retornos mensuales FEES, enero 2014–septiembre 2026. Cada número extraído de la tabla coincide con la explicación en prosa del informe correspondiente. Se validó la portada antes de aceptar un documento. Julio de 2016 usa DIPRES porque el enlace de Hacienda devolvía el mes anterior.

Se conserva extracción textual, fecha, URL, página, evidencia y hash del PDF. Las páginas BCCh conservan dólar observado diario, IPC mensual y PIB trimestral, con sus hashes. No se usa el tipo de cambio Yahoo para la conversión del fondo. Los PDF completos se mantienen en caché local, excluida del ZIP y Git, sin impedir la reproducción con los archivos extraídos entregados.

La referencia generada coincide con los retornos oficiales. El saldo de la hoja Datos Evo. Hist. del Excel de septiembre de 2026 se convierte por separado: no se utiliza como retorno. Los ETF congelados se preservaron; se amplió únicamente cobre mediante descarga explícita desde 2010 para el calentamiento de volatilidad.

## Comprobaciones económicas

Se ejecutan 24 pruebas mediante `python verificar.py`. Comprueban:

- los 153 retornos oficiales contra su prosa y los hashes;
- valor oficial verificable del dólar observado y carga sin red ni Yahoo FX;
- conversión compuesta USD/CLP e inflación;
- cartera anual con pesos que fluctúan y rebalanceo en enero;
- motor vectorizado de mezclas contra tenencias individuales;
- put anual, renovación semestral de sensibilidad y strike/cantidad fijos;
- financiación de prima, pago único, nocional cero y opción pendiente al corte;
- prima de compra inalterada por precios posteriores;
- restricciones de pesos, selección sin trimestres futuros e historia mínima;
- PIB con 90 días anteriores a las fechas de decisión;
- separación del presupuesto invertido y nocional subyacente.

La evaluación de ciclo solo usa trimestres completos con PIB disponible. H5 queda sin valores antes de disponer de entrenamiento suficiente: no se rellena artificialmente con FEES. Los pesos finales se guardan aparte de la curva progresiva. Se conserva sensibilidad de límites y exclusión de contracciones.

## Notebook y gráficos

`python validar_notebook.py` regenera el notebook, crea un ZIP, lo extrae a una carpeta temporal y elimina todos sus resultados. Usa un kernel temporal con el Python actual y los paquetes instalados, con PIP_NO_INDEX=1. Ejecuta todas las celdas y las pruebas; compara doce archivos regenerados byte por byte con el script. Conserva el notebook ejecutado y actualiza la entrega ZIP.

Esto verifica un kernel nuevo con los datos entregados. No se afirma haber ejecutado dentro del servicio web de Google Colab. La primera celda acepta archivos entregados o el archivo público de la rama GitHub, sin rutas privadas.

Los gráficos separan FEES observado, saldo efectivo, rebalanceos simulados, PIB, contracciones y puts. Las comparaciones de riqueza de las seis estrategias empiezan en la misma fecha y capital. Los cambios de política marcados no se presentan como todas las fechas de rebalanceo real.

## Qué no demuestra la verificación

La optimización es exhaustiva dentro de una rejilla, no un óptimo universal. Usa PIB revisado, decisiones de diseño retrospectivas, pocos episodios y primas sintéticas. Un resultado pequeño o una solución concentrada no se presenta como cartera anticíclica demostrada. La validación no certifica TE ex ante, contratos negociables, liquidez de venta, cobertura fiscal completa ni autorizaciones normativas.
