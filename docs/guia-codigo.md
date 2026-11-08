# Cómo explicar las cuatro carteras

La unidad del análisis es una cartera por hipótesis, más una referencia. Todas parten de la misma asignación del bloque USD. No son tres tamaños del mismo cambio de duración.

## Qué cambia en cada hipótesis

H1 mueve bonos de 7–10 años hacia letras: busca reducir exposición a bonos largos. H3 mueve una cantidad menor desde 7–10 hacia 1–3 años: conserva la clase Treasury. H4 reduce MBS y pone la diferencia en letras. H2 conserva la base y paga un seguro mensual sobre cobre. La tabla `estado_carteras.csv` muestra qué exige cambiar la política del FEES.

`config.json` contiene esos cambios. `pesos_escenario` construye los pesos de activos sobre el fondo total. Suman 69%, porque no se modela el 31% extranjero restante. Para el retorno del bloque, `cartera` divide por 0,69. No se presenta ese retorno como el del FEES completo.

## La put, paso a paso

Una put paga si el subyacente termina bajo el strike. No es gratis: se paga una prima aunque termine sin valor. Para explicar un mes, abrir `results/puts_auditoria.csv`.

1. Tomar F, el cierre del cobre del mes anterior. Fijar strike en 95% de F.
2. Calcular la volatilidad con los últimos 63 retornos diarios conocidos. Multiplicarla por 1,25, supuesto explícito de valoración.
3. Tomar la tasa Treasury de un mes conocida al entrar y usar Black-76 para la prima europea.
4. Comprar cobertura nocional de 10% del capital total hipotético. Restar prima y fricción de BIL.
5. Aplicar los retornos de activos del mes. El dinero usado para la prima deja de ganar retorno BIL.
6. Al final, sumar a BIL `nocional/F × max(strike − precio final, 0)`. Rebalancear al iniciar el mes siguiente.

Ejemplo solo para entender el pago: si F = 100, strike = 95 y precio final = 80, la put paga 15 por unidad. Con nocional 10% del fondo, eso equivale a 1,5% del capital total antes de restar prima y costos. Si termina en 110, paga cero y se pierde la prima. Estos números son ilustrativos, no datos de un contrato real.

`precio_put_black76` implementa la fórmula de valoración. `preparar_insumos_puts` desplaza los datos para usar información del cierre anterior. `cartera_puts` lleva las tenencias, descuenta la prima y suma el pago. Con nocional cero debe producir la referencia; una prueba lo verifica.

## Qué es dato y qué es supuesto

Los cierres de HG=F son datos descargados. La prima es teórica. La volatilidad implícita no se observó: se aproxima con volatilidad histórica multiplicada por un factor. HG=F puede cambiar de contrato, así que no se reproduce una opción COMEX identificada. Se simula un instrumento europeo hipotético sobre un proxy continuo. No se modela ejercicio americano ni entrega física.

El nocional de la opción mide exposición al subyacente, no dinero invertido. No debe sumarse como otro 10% a los pesos del 69%. El dinero invertido es la prima, que sale de letras y cambia cada mes. El código rechaza una compra que requiera más letras de las disponibles.

## Retornos, costos y riesgo

Los retornos ETF salen de cocientes de cierres ajustados. El ajuste aproxima distribuciones reinvertidas; sumarlas otra vez duplicaría el ingreso. Las tasas FRED no son retornos de bonos.

`cartera` calcula la suma de pesos por retornos, con rebalanceo mensual. Cobra compras más ventas: pasar de 60/40 a 50/50 exige vender 10% y comprar 10%, por lo que el costo se cobra sobre 20%. H2 también incluye el cambio de tenencias causado por los pagos del seguro al calcular el rebalanceo siguiente.

`riqueza_y_caida` multiplica sucesivamente uno más cada retorno. Incluye el capital inicial al medir caídas. `metricas` calcula el retorno compuesto anual equivalente, volatilidad y peor caída mensual. No detecta máximos o pérdidas dentro del mes.

## Cómo defender la interpretación

La correlación con acciones es un diagnóstico: SPY no integra las carteras. Una correlación positiva no significa pérdidas simultáneas en todos los meses.

Una put puede proteger frente a una caída de cobre sin mejorar el retorno medio de la cartera financiera. Su motivo fiscal es distinto del seguro de una cartera que ya posee cobre. Aquí no se modelan ingresos del Estado, producción ni retiros: no se afirma haber demostrado cobertura fiscal.

Los intervalos bootstrap remuestrean bloques de diferencias mensuales pareadas. Describen incertidumbre de medias bajo los supuestos elegidos. No incluyen incertidumbre sobre la prima real, no corrigen múltiples pruebas y no eliminan el diseño retrospectivo.

Simular H1, H2 y H4 permite estudiar las ideas del usuario; no las vuelve admisibles bajo la política actual. H3 conserva clases pero también requiere TE ex ante y revisión de instrumentos. Un mejor CAGR histórico no basta para recomendar ninguna ejecución.
