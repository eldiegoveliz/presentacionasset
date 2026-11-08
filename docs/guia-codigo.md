# Explicar el análisis sin una caja negra

La pregunta es qué conserva recursos reales en pesos cuando cae la economía chilena. El rendimiento total aparece como contexto; no es la función que elige los pesos.

## Qué contiene cada módulo

`datos_oficiales.py` transforma fuentes públicas en archivos revisables. Extrae retornos FEES de los PDF y comprueba fechas; obtiene dólar, PIB e inflación del Banco Central. `datos.py` conserva precios de ETF, cobre y tasas. El análisis posterior no necesita red.

`carteras.py` contiene los movimientos de dinero. `optimizacion.py` enumera pesos y los elige usando historia anterior. `analisis.py` junta las series y genera el informe. El notebook muestra esos tres módulos de cálculo, no una segunda implementación distinta.

## La referencia es el FEES completo observado

Usamos el retorno mensual oficial, no la variación del saldo. Si el Gobierno retira recursos, baja el saldo aunque la inversión no haya perdido. Por eso hay una gráfica de rentabilidad sin flujos y otra del saldo efectivo.

El FEES histórico incorpora sus rebalanceos y cambios de política. No se dice que sus activos hayan sido siempre los actuales. Las marcas de fin de acciones e inicio MBS tienen fuente; no se inventaron todas las fechas operativas.

## Rebalancear una vez al año

`cartera_anual` empieza con un presupuesto, por ejemplo 90% FEES y 10% letras. Después aplica cada retorno y calcula los pesos que quedaron. Los deja fluctuar hasta enero siguiente, cuando vuelve al objetivo y cobra compras más ventas. No vuelve a 90/10 cada mes.

Las fechas de esos rebalanceos simulados están en `rebalanceos_simulados.csv`. La gráfica de H1 muestra el movimiento de pesos y el retorno al objetivo anual. Ese calendario no se atribuye al FEES observado.

## Convertir a pesos y medir poder adquisitivo

Multiplicamos uno más el retorno USD por la variación del dólar observado BCCh. Después dividimos por uno más la inflación. Esto incluye el producto entre retorno y cambio de moneda. No basta sumar porcentajes.

El tipo de cambio se descarga diariamente, pero la rentabilidad FEES es mensual. Usamos las observaciones correspondientes a los cierres de cada mes; no inventamos una rentabilidad diaria. Para comparar con PIB acumulamos tres meses de retornos. El PIB no se interpola.

## Mantener una put de 12 meses

`put_larga` paga la prima vendiendo parte del FEES. Esa porción deja de ganar el retorno del fondo. Mantiene strike y cantidad durante el contrato y valora mes a mes lo que queda de plazo. Al vencer, el pago se incorpora al capital; no se cuenta dos veces. La última opción puede seguir viva al cierre de datos.

El futuro se modela con vencimiento fijo a partir de un proxy de spot. La prima Black-76 es teórica. No tenemos primas ni curvas históricas COMEX identificadas; el proxy continuo conserva limitaciones de cambio de contrato. La valoración no equivale a un backtest ejecutable.

La volatilidad se calcula con historia conocida al comprar y se congela para ese contrato. Las pruebas cambian precios futuros y comprueban que la prima inicial no cambia. Otra prueba verifica que nocional cero reproduce el FEES.

## Elegir los pesos de H5

`generar_pesos` enumera combinaciones en pasos de 5%, que suman 100%. No hay cortos ni deuda. H2 tiene tope de 25% por riesgo de modelo; las otras estrategias pueden tener peso cero o concentrar todo el presupuesto. No se fuerza una mezcla si la evidencia no la favorece.

`simular_mezclas` calcula qué habría producido cada combinación con rebalanceo anual. `elegir_pesos` compara solo trimestres anteriores cuyo PIB se permite conocer con un rezago de 90 días.

El criterio se puede explicar con un ejemplo ilustrativo: A pierde 8% en una contracción y gana 6% en otra; B pierde 4% y 3%. Aunque A tenga una media mayor, el criterio elige B porque mejora el peor caso. Se busca preservar capital en una mala situación, no maximizar la ganancia promedio.

`optimizar_progresivo` repite la elección antes de cada año. Así la curva histórica no se dibuja con los pesos finales escogidos mirando toda la muestra. El PIB es revisado y las hipótesis nacieron con conocimiento del pasado: el ejercicio sigue siendo retrospectivo.

## Presupuesto de estrategias frente a activos reales

Asignar 60% a H1 no equivale a tener 60% en letras: H1 contiene solo 10% de letras. Ese presupuesto aportaría 6% de letras y 54% de núcleo FEES. La tabla `exposicion_optima.csv` hace esa cuenta para el resultado completo. Las cinco estrategias no son cinco activos independientes.

El nocional de una opción tampoco es dinero que se sume al capital: el desembolso es la prima. Se muestra por separado.

## Defender un resultado que no sea espectacular

El mejor peso puede ser cero para puts o MBS. Eso no elimina la hipótesis: muestra que no ayudó al objetivo bajo estos supuestos. Una solución de 100% en una alternativa también es válida; no fabricamos diversificación.

El bootstrap y la exclusión de contracciones muestran incertidumbre, no una garantía. Si las carteras siguen perdiendo durante contracciones, hay que decirlo. Un óptimo de esta rejilla puede mejorar poco y no demostrar anticiclicidad ni admisibilidad legal.
