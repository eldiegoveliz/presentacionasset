# Metodología del análisis FEES

Estado al 8 de noviembre de 2026. La autorización posterior del usuario permite investigar y escribir código. El texto anterior que restringía el trabajo a documentación ya no describe el alcance vigente. Se conserva en el historial Git.

## Requisitos y decisiones del usuario

El curso exige evaluar FEES y FRP, justificar supuestos y reproducir cifras en Colab. Este análisis cubre las cuatro hipótesis FEES del usuario; el FRP queda para otra etapa. El usuario exige respetar las reglas del FEES, buscar datos reales y mantener código explicable. No autoriza modificar la política para incorporar cobre.

## Supuestos técnicos del asistente

Estos supuestos se fijaron en `config.json` antes de calcular resultados. Son propuestas de trabajo autorizadas para desarrollar el análisis, no decisiones ya revisadas por el equipo.

| Decisión | Especificación y razón |
| --- | --- |
| Regla de referencia | Política publicada como vigente en Hacienda al 8/11/2026; asignación corroborada en composición de septiembre de 2026. |
| Cobertura del análisis | Bloque USD de 69% del fondo, normalizado a 100 para sus métricas. Faltan Europa 19%, Japón 9% y China 3%. No es una réplica del FEES. |
| Historia | Descargar desde diciembre de 2013 para obtener retornos desde enero de 2014. Muestra principal enero de 2020 a octubre de 2026. Se excluye noviembre incompleto. |
| Frecuencia | Cierres mensuales ajustados, retornos simples entre cierres. Riesgo y medias se anualizan con 12 meses. |
| Referencia proxy | 10% BIL, 40% dividido en tercios entre SHY/IEI/IEF, 4% STIP y 15% MBB, sobre el fondo total. Para el bloque, dividir por 69%. |
| Escenarios | Transferir 1, 2 o 4 pp del fondo desde IEF hacia SHY. Mantener 40% Treasury, 10% letras, 4% TIPS y 15% MBS. No se optimizan pesos ni fechas. |
| Rebalanceo | Mensual al inicio de cada período. Sin flujos fiscales. La norma oficial tiene otro calendario: al menos anual sin flujos y cuando Hacienda instruye por aportes o retiros. |
| Costos | 5 pb por dólar transado, sumando compras y ventas sin dividir por dos; compra inicial incluida. Sensibilidad 0 y 10 pb. Gastos internos de ETFs ya están en el ajuste de precios. |
| Correlación | SPY contra SHY, IEI, IEF y MBB; ventanas móviles de 12 meses y subperíodos 2014–2019, 2020–2021, 2022 y 2023–corte. |
| Incertidumbre | Bootstrap pareado circular con bloques de 3, 6 y 12 meses, 2.000 repeticiones y semilla fija. Intervalos individuales para diferencias de medias, no de CAGR. |
| Cumplimiento | Preservar pesos estratégicos no certifica cumplimiento. El TE proxy histórico es un filtro descriptivo. Faltan índices licenciados y modelo ex ante del custodio. |

## Proxies y fuentes

| Serie | Exposición o unidad | Desajuste frente al FEES | Fuente del instrumento |
| --- | --- | --- | --- |
| BIL | Letras Treasury 1–3 meses | Índice y gastos distintos de ICE BofA; no es efectivo bancario | [State Street BIL](https://www.ssga.com/us/en/individual/etfs/state-street-spdr-bloomberg-1-3-month-t-bill-etf-bil) |
| SHY | Treasuries 1–3 años | Tramo de curva, no índice 1–10 completo | [iShares SHY](https://www.ishares.com/us/products/239452/ishares-13-year-treasury-bond-etf) |
| IEI | Treasuries 3–7 años | Tramo intermedio; peso equiponderado supuesto | [iShares IEI](https://www.ishares.com/us/products/239455/ishares-37-year-treasury-bond-etf) |
| IEF | Treasuries 7–10 años | Tramo largo del universo elegible | [iShares IEF](https://www.ishares.com/us/products/239456/ishares-710-year-treasury-bond-etf) |
| STIP | TIPS 0–5 años | El comparador FEES es 1–10: duración y madurez distintas | [iShares STIP](https://www.ishares.com/us/products/239450/ishares-tips-bond-etf) |
| MBB | MBS de agencias EE.UU. | Gastos, muestreo y gestión del ETF distintos del mandato del FEES | [iShares MBB](https://www.ishares.com/us/products/239465/ishares-mbs-etf) |
| SPY | Acciones S&P 500 | Diagnóstico externo; nunca forma parte de las carteras | [State Street SPY](https://www.ssga.com/us/en/individual/etfs/spdr-sp-500-etf-trust-spy) |
| CLP=X | Pesos chilenos por USD | Cotización de mercado Yahoo, no dólar observado oficial. Horarios y días pueden diferir | [Yahoo USD/CLP](https://finance.yahoo.com/quote/CLP=X/) |
| DGS2 y DGS10 | Tasas Treasury anualizadas en %, diarias | Solo contexto. No son índices de retorno total | [FRED DGS2](https://fred.stlouisfed.org/series/DGS2), [DGS10](https://fred.stlouisfed.org/series/DGS10) |

Los cierres ajustados se descargan desde Yahoo chart con datos diarios y eventos de distribución. Los CSV conservan cierre, ajustado y dividendo por fecha; los JSON conservan la respuesta original. Se contrasta cada retorno ajustado con `(cierre + distribución) / cierre anterior − 1`. Yahoo ya ajusta cierre y distribuciones por splits. BIL tiene un reverse split en 2017 y no se aplica por segunda vez. Se exige discrepancia máxima menor a 10 pb diarios y se publican los errores observados.

No se interpola ningún ETF. Se exige el mismo calendario para todos y observaciones mensuales completas hasta el corte, con última cotización a no más de siete días del fin de mes. FX conserva días sin cotización como NA y usa el último cierre observado de cada mes con la misma restricción de antigüedad. FRED conserva NA por días sin tasa. No se rellenan con ceros ni se usan como retornos.

La columna `ajustado` puede reflejar ajustes del proveedor por distribuciones posteriores al corte en su escala. Se calculan razones entre fechas dentro del corte; no se usan valores absolutos para decidir. La selección retrospectiva de instrumentos, la política de 2023 aplicada desde 2020 y las hipótesis motivadas por datos recientes mantienen sesgo de selección.

## Alcance de las conclusiones

La correlación positiva es una propiedad de la muestra y del instrumento. No demuestra que todos los bonos hayan dejado de diversificar. La necesidad del FEES es disponer de recursos en CLP cuando el Fisco los necesita. Evaluarla por completo requiere retiros, exposición a ingresos fiscales, moneda y cartera global, que aquí no se modelan.

El TE de los escenarios se aproxima con `std(retorno SHY − retorno IEF) × sqrt(12) × traspaso / 0.85`. La división por 85% corresponde al bloque soberano administrado por el Banco Central. El 69% solo normaliza el bloque USD para sus métricas. No intercambiar esos denominadores. El cálculo omite el error de réplica contra el benchmark oficial; por eso ni siquiera un resultado inferior a 25 pb certifica elegibilidad.

El bootstrap no elimina el diseño dentro de muestra. Los intervalos no se corrigen por pruebas múltiples y no permiten declarar un ganador. La sensibilidad temporal y de costos muestra cuánto depende el resultado del régimen, sin transformar el ejercicio en una estrategia validada para el futuro.
