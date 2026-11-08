# Cómo explicar el código

El análisis responde una pregunta acotada: qué habría ocurrido al reducir un poco la duración del componente Treasury en dólares, manteniendo los pesos estratégicos de clases. No busca una cartera óptima.

## Datos y retornos

`datos.py` descarga precios diarios, distribuciones y tasas. Guarda los archivos y las URLs utilizadas. `analisis.py` lee esos archivos sin red.

`cargar_mensuales` toma el último precio ajustado observado de cada mes. Calcula `precio_actual / precio_anterior − 1`. Si un precio pasa de 100 a 102, el retorno es 2%. El cierre ajustado aproxima la reinversión de las distribuciones; sumarlas de nuevo contaría ese ingreso dos veces.

Se comprueba que no falten meses y que los ETF tengan el mismo calendario. Las tasas FRED de 2 y 10 años solo aparecen en un gráfico de contexto. Una tasa de 4% no es un retorno mensual de 4%.

## Pesos y rebalanceo

`pesos_escenario` empieza con los pesos sobre el FEES completo. El bloque estudiado suma 69%. Para calcular el retorno de ese bloque, `cartera` divide cada peso por 0,69. Así los pesos del cálculo suman uno.

El retorno bruto mensual es la suma de `peso × retorno de cada activo`. Los pesos se fijan al inicio del mes; ningún retorno futuro modifica esa decisión. Al terminar el mes, los activos que subieron pesan más. Antes del siguiente mes se vuelve al objetivo y se cobra el costo de las compras y ventas necesarias.

El modelo cobra 5 pb por dólar planeado de transacción sobre el capital antes de comisiones. Con pesos 50/50 y retornos +20%/−20%, se termina 60/40. Para volver a 50/50 se vende 10% y se compra 10%: se cobra sobre 20%, no sobre 10%. Al inicio se cobra la compra de 100% del capital.

La referencia dedica 40 pp del fondo a Treasuries, repartidos en tres tramos. El escenario de 2 pp mueve 2 del tramo 7–10 al tramo 1–3 años. No reduce el 40% total ni cambia MBS. Una pérdida menor en una subida de tasas puede acompañarse de una ganancia menor cuando las tasas caen.

## Métricas

`riqueza_y_caida` multiplica sucesivamente `1 + retorno`. Una pérdida de 10% seguida de una ganancia de 10% deja 99 por cada 100 iniciales. No deja 100.

`metricas` calcula el retorno geométrico anual equivalente, la desviación estándar mensual multiplicada por raíz de 12 y la mayor caída desde un máximo. La caída incluye el capital inicial: no se esconde una pérdida del primer mes. Se usan cierres mensuales y pueden omitirse pérdidas mayores dentro del mes.

El tracking error mide cuánto varía la diferencia contra una referencia. Aquí solo se estima la diferencia producida por cambiar de tramo. El cálculo usa el denominador 85% del mandato soberano, distinto del 69% del bloque medido. El presupuesto oficial es ex ante y exige otra información; este diagnóstico no certifica una cartera.

## Correlación e incertidumbre

Una correlación positiva significa que dos retornos tendieron a moverse juntos durante esa ventana. No significa que fueran iguales, ni que ambos perdieran siempre. Por eso también se guardan los meses de pérdidas conjuntas y el retorno de bonos en meses de caída de SPY.

`bootstrap_media` toma diferencias de retorno entre cada escenario y la referencia en las mismas fechas. Remuestrea grupos de meses consecutivos para conservar parte de la dependencia temporal. Cada muestra produce una media anualizada; los percentiles 2,5 y 97,5 delimitan el intervalo descriptivo del 95%.

Si el intervalo incluye cero, no hay evidencia firme de una mejora de media con este procedimiento. Incluso si no incluyera cero, seguirían el sesgo de diseño dentro de muestra y las comparaciones múltiples. El intervalo es para la media aritmética anualizada, no para el retorno compuesto.

## Preguntas para practicar

- ¿Por qué no llamamos a esta cartera el FEES? Faltan tres componentes extranjeros y los índices se aproximan con ETFs.
- ¿Por qué no probamos puts de cobre? Las directrices consultadas no las incluyen entre los instrumentos elegibles.
- ¿Por qué no subimos MBS al 20%? La referencia fija 15%. El 20% que aparece en las pautas tiene otro alcance: deuda permitida dentro del mandato MBS.
- ¿Por qué usar pesos si medimos en USD? El Fisco gasta en CLP. La conversión muestra la exposición al dólar, pero no demuestra cobertura de sus necesidades de caja.
- ¿Qué significa una mejora histórica de pocos puntos base? Es pequeña frente a la incertidumbre, los desajustes de proxies y los costos. No basta para recomendar ejecución.
