# Metodología: una cartera por hipótesis

Actualización del 8 de noviembre de 2026 tras la corrección del usuario. La primera implementación comparaba solo tres variantes de duración y dejaba puts y MBS fuera del cálculo. Ese diseño no correspondía a la solicitud y fue reemplazado.

## Alcance e interpretación

El usuario pide una simulación con una cartera por cada una de sus cuatro hipótesis, más una referencia. También exige documentar y respetar las reglas del FEES. Para conservar ambas cosas, el análisis calcula los escenarios económicos y muestra el filtro normativo: una hipótesis fuera de la política vigente no se presenta como cartera ejecutable autorizada.

El curso exige FEES y FRP; esta etapa solo aborda FEES. La referencia sigue cubriendo el bloque USD de 69% de la asignación. Europa 19%, Japón 9% y China 3% no se replican. Sus exposiciones se suponen iguales entre escenarios, pero no se inventan retornos ni métricas del fondo completo.

## Cinco carteras

Los cambios se expresan como puntos porcentuales sobre el FEES completo. Los cálculos del bloque dividen los pesos de activos por 0,69.

| Cartera | Diseño propuesto por el asistente | Estado normativo |
| --- | --- | --- |
| Referencia | BIL 10%, Treasury 40% en tercios SHY/IEI/IEF, STIP 4%, MBB 15% | Proxy de asignación, no réplica ni elegibilidad certificada |
| H1 Más letras | Mover 10 pp de IEF a BIL | Cambia letras a 20% y Treasury a 30%; requiere cambiar asignación y evaluar riesgo |
| H2 Puts de cobre | Mantener la base y comprar puts mensuales de nocional 10%, strike 95%, pagadas con BIL | Instrumento fuera de la política consultada; resultado teórico |
| H3 Treasury corto | Mover 2 pp de IEF a SHY | Conserva clases; cumplimiento ex ante no verificado |
| H4 Menos MBS | Mover 5 pp de MBB a BIL: MBS 10%, letras 15% | Cambia el 15% estratégico MBS |

H1 traduce la inquietud sobre correlación en menor exposición a bonos largos y más letras. Es una operacionalización del asistente, no una cartera definida expresamente por el usuario. SPY sigue siendo solo diagnóstico; no se añaden acciones al FEES. H1 cambia la clase asignada, mientras H3 cambia el tramo de madurez manteniendo 40% Treasury.

Los parámetros son supuestos exploratorios, no estimaciones óptimas ni decisiones ya revisadas por el equipo. Se conocía la historia de los ETF al corregir el diseño. Por eso no se presenta como una preregistración ni validación fuera de muestra.

## Datos

| Series | Uso | Limitación |
| --- | --- | --- |
| BIL, SHY, IEI, IEF, STIP, MBB | Letras, tres tramos Treasury, TIPS y MBS; cierre ajustado Yahoo | No replican exactamente los índices oficiales. STIP es 0–5 años frente a TIPS oficial 1–10. Los tercios Treasury son supuestos. |
| SPY | Correlación con bonos | Diagnóstico externo, nunca pesa en carteras |
| HG=F | Cierre diario continuo del cobre para el modelo | Puede cambiar de contrato entre fechas; no es un futuro identificado ni retorno de una posición negociable |
| DGS1MO | Proxy de tasa anual de descuento para la put | Tasa cotizada Treasury aproximada como continua; no es retorno de inversión |
| DGS2, DGS10 | Contexto de tasas | No se convierten sus variaciones en retornos |
| CLP=X | Conversión ilustrativa USD/CLP | Cotización Yahoo distinta del dólar observado oficial y con otro horario |

Se descargan datos desde diciembre de 2013 hasta octubre de 2026. La muestra principal tiene 82 meses, enero de 2020 a octubre de 2026. La correlación anterior a 2020 usa 2014–2019. Para comparar las cinco carteras en un período anterior se usa 2015–2019, con suficiente calentamiento de volatilidad del cobre.

Los ETF conservan las descargas congeladas de la primera versión. Se añadieron HG=F y DGS1MO sin reemplazarlas. Los JSON originales, CSV, URLs y hashes están en `data/`. No se rellenan precios de ETF ni se inventan primas. Las fechas ETF deben coincidir y cada mes exige un cierre observado a no más de siete días del fin de mes. FX, cobre y tasas conservan sus calendarios propios, sin interpolación.

Yahoo ya ajusta cierres y distribuciones por splits. Se valida el retorno ajustado con cierre más distribución; BIL tuvo un reverse split en 2017 y no se aplica dos veces. Los cocientes de ajustados aproximan distribuciones reinvertidas, netas de gastos internos del ETF.

## Prima y financiación de puts

La cartera H2 es una simulación paramétrica de opciones europeas hipotéticas sobre el proxy continuo. No se descargaron primas históricas observadas por contrato, strike y vencimiento. Las especificaciones negociables de COMEX no se reemplazan por estos supuestos.

Para cada mes se usa el precio al cierre del mes anterior como futuro inicial F, strike K = 0,95 × F y plazo T = 1/12. La volatilidad histórica usa los últimos 63 cambios logarítmicos diarios disponibles a ese cierre, anualizados con raíz de 252. Se multiplica por 1,25 para la volatilidad de valoración. Ese incremento de 25% es un supuesto, no una observación de volatilidad implícita. Se usa la última DGS1MO del mes anterior, dividida por 100.

La prima se calcula con [Black (1976)](https://doi.org/10.1016/0304-405X(76)90024-6):

```text
d1 = [ln(F/K) + 0,5 × sigma² × T] / [sigma × raíz(T)]
d2 = d1 − sigma × raíz(T)
prima = exp(−rT) × [K × N(−d2) − F × N(−d1)]
```

Con h = 10% de nocional sobre el capital total hipotético, la prima relativa es `h × prima/F` y el pago relativo es `h × max(K − F_final, 0)/F`. Se asumen cantidades fraccionarias; no se redondea a contratos enteros de 25.000 libras. No se mantiene una posición descubierta en futuros.

La fricción adicional es 10% de la prima, supuesto separado de los 5 pb por dólar transado en ETF. Prima y fricción salen de BIL, con lo que dejan de ganar el retorno de letras durante el mes. El pago al vencimiento se suma a BIL. El siguiente mes se rebalancea desde las tenencias efectivas, incluidos los pagos o pérdidas del seguro. El código rechaza primas que superen las letras disponibles y evita endeudamiento.

El nocional se mide sobre el capital posterior al costo de rebalanceo de activos de ese mes. No es un peso de capital que se sume al 69%. El CSV `puts_auditoria.csv` muestra cada flujo y la diferencia final frente a la referencia. Con nocional cero se reproduce la cartera base, comprobado en pruebas.

El cambio de vencimientos del proxy continuo puede crear o borrar pagos que no existirían en un contrato real. Tampoco se modelan ejercicio americano, entrega física, strikes negociados, estructura de volatilidad, spreads reales ni vencimientos oficiales. El modelo europeo no estima esos efectos. Sus retornos e intervalos no prueban desempeño histórico ejecutable de puts reales.

## Comparación y sensibilidad

Rebalanceo mensual a objetivos fijos y sin flujos fiscales. Costos de activos: 5 pb por dólar de compras más ventas, incluida la inversión inicial; sensibilidad 0 y 10 pb. No se divide el volumen por dos. El calendario es un supuesto del ejercicio: la norma oficial instruye rebalanceos por flujos y al menos uno anual sin ellos.

Se reportan CAGR, volatilidad anualizada con raíz de 12, caída máxima desde cierres mensuales incluyendo capital inicial y peor mes. Se convierten las mismas cinco series a CLP. Para H1 y H3 se muestra el TE histórico incremental del mandato soberano, dividiendo el retorno activo por 85%. No es el TE ex ante del custodio ni incorpora error de réplica del índice.

Para puts se calculan todas las 27 combinaciones de strikes 90/95/100%, multiplicadores de volatilidad 1/1,25/1,5 y nocionales 5/10/20%. Para MBS se muestran 10/15/20%, con la diferencia en BIL. No se elige un ganador para redefinir las carteras principales.

El bootstrap pareado por bloques circulares usa 2.000 repeticiones, semilla 20261108 y bloques de 3, 6 y 12 meses. Sus intervalos son individuales para diferencias de medias mensuales multiplicadas por 12, no diferencias de CAGR. No corrigen pruebas múltiples, sesgo de diseño ni error de modelo de opciones.

La protección fiscal del cobre requiere ingresos tributarios, producción y retiros del fondo, que aquí no se modelan. Una put puede pagar en meses de caída del cobre y aun así reducir el retorno promedio o aumentar pérdidas de la cartera financiera. Esa distinción forma parte de la conclusión.
