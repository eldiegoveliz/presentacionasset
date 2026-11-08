# Metodología anticíclica del FEES

El usuario delimitó el análisis a FEES y cuatro alternativas, y autorizó una quinta combinación optimizada. Esta actualización reemplaza las carteras parciales del 69%, el tipo de cambio Yahoo y las puts renovadas mensualmente. Las decisiones técnicas siguientes son del asistente, no revisiones ni firmas del equipo.

## Referencia y presupuestos completos

El FEES observado usa 153 retornos mensuales netos, enero de 2014 a septiembre de 2026, de informes oficiales. No se obtiene rendimiento a partir del cambio del saldo, que contiene aportes y retiros. Se coteja cada retorno de la tabla con la explicación en prosa del informe. Los PDF redondean a 0,01 puntos porcentuales.

Las alternativas son presupuestos completos con núcleo FEES y satélites. Así se comparan series del mismo capital, evitando mezclar el fondo completo con una proxy parcial:

| Estrategia | Regla |
| --- | --- |
| H1 | FEES 90%, BIL 10% |
| H2 | FEES con put de 12 meses, nocional subyacente 10%, prima financiada vendiendo FEES |
| H3 | FEES 80%, SHY 20% |
| H4 | FEES 90%, MBB 10% |

H1, H3 y H4 rebalancean en enero y dejan fluctuar pesos el resto del año. Esto es un calendario de simulación, no una afirmación sobre las fechas operativas reales. Se cobra 5 pb por dólar comprado o vendido, incluida compra inicial. El FEES observado ya incluye sus comisiones. La quinta mezcla añade 5 pb por dólar reasignado entre estrategias; se declara esta capa adicional.

El significado de H3 es aumentar exposición a Treasury corto, no mantener artificialmente 40% de un índice Treasury reconstruido. H4 prueba más MBS sobre el fondo completo, dado que el FEES no tenía MBS antes de noviembre de 2023. La reducción de 2 pp desde diciembre de 2023 se conserva como sensibilidad de atribución marginal `r_FEES + 0,02 × (r_BIL − r_MBB)`, no como cartera real reconstruida ni réplica exacta de la clase MBS oficial. No se usa para elegir H5.

El histórico FEES refleja políticas que cambiaron e incluyó acciones antes del fin del mandato en septiembre de 2021. No se afirma que toda su historia corresponde a su actual política de bonos. Sus operaciones y rebalanceos ya afectan los retornos oficiales. Las fechas documentadas de fin de gestión de acciones e inicio MBS se señalan en la gráfica; no se inventa un calendario exhaustivo de rebalanceos.

## Datos oficiales, moneda y ciclo

El dólar observado diario se extrae de la página pública BCCh, serie F073.TCO.PRE.Z.D. Se conserva la fecha chilena de cada observación y se toma el último valor publicado disponible en cada mes. Este indicador refleja transacciones del día hábil anterior; no equivale al cierre FX internacional de Hacienda. No se espera identidad con el retorno CLP publicado por Hacienda.

El IPC mensual se obtiene de BCCh con fuente INE. El PIB es volumen encadenado desestacionalizado trimestral, serie F032.PIB.FLU.R.CLP.EP18.Z.Z.1.T. Retornos trimestrales solo se forman con tres meses completos y se comparan hasta el último PIB publicado, junio de 2026. No se interpola el PIB ni se crean retornos diarios del FEES.

```text
1 + r_CLP = (1 + r_USD) × FX_fin / FX_inicio
1 + r_CLP_real = (1 + r_CLP) / (1 + inflación_mensual)
contracción = crecimiento trimestral del PIB real desestacionalizado < 0
```

Se usa el mayor período común 2014–septiembre de 2026; el período de evaluación de H5 comienza después de reunir historia suficiente. El saldo efectivo en USD se extrae de la hoja Datos Evo. Hist. del Excel de septiembre de 2026 y se convierte a CLP corrientes. Esa gráfica incluye flujos y se presenta separada de la rentabilidad sin flujos.

El control de portadas detectó que el enlace de Hacienda de julio de 2016 devolvía junio. Se reemplazó por el documento correcto de DIPRES. No se rellenó ese retorno ni se reutilizó el de junio. Los archivos extraídos, referencias y hashes están en data/oficial; los PDF completos permanecen en una caché local excluida de Git y del ZIP. El cobre se amplió desde 2010 mediante descarga explícita para disponer de volatilidad anterior a 2014; los otros ETF congelados se conservaron.

## Put larga y valoración mensual

Se compra una opción sintética de 12 meses al comenzar enero. Mantiene cantidad y strike hasta vencer; su valoración mensual usa el plazo residual. Al vencimiento el pago se incorpora al capital y se renueva. Una opción aún no vencida al corte conserva valor teórico, no se liquida artificialmente a cero. El modelo liquida en efectivo y no simula entrega física ni ejercicio americano.

No se consiguieron primas ni curvas históricas por contrato COMEX identificado. Se emplea HG=F como proxy de spot para un futuro sintético de vencimiento fijo `F(t,T) = proxy(t) × exp(r × (T−t))`, suponiendo almacenaje menos conveniencia cero. El cambio de contratos del proxy puede distorsionar ese spot supuesto. No se afirma que el modelo replique futuros u opciones negociables ni que haya eliminado riesgo de base.

La prima usa Black-76 europeo. El strike es 95% del futuro sintético inicial y el nocional 10% del capital previo a la compra. La volatilidad usa 24 retornos mensuales anteriores, anualizada con raíz de 12 y multiplicada por 1,25. Se congela para ese contrato: no se utiliza volatilidad futura para fijar la prima inicial. La tasa es la última DGS1 del mes anterior al comprar y la tasa observada del mes al valorar. La sensibilidad de seis meses usa DGS6MO. La renovación y compra no se confunden con una nueva valoración.

Prima, fricción de 10% de la prima y costo de vender capital para financiarla salen del FEES. La porción vendida deja de ganar su retorno. Se registra valor del núcleo, opción, primas, vencimiento y riqueza. Con nocional cero se reproduce el FEES observado. El pago se cuenta una vez y no hay endeudamiento.

La sensibilidad varía plazo 6/12 meses y multiplicador de volatilidad 1/1,25/1,5, manteniendo H2 fuera de una selección oportunista de supuestos.

## Optimización y evaluación temporal

H5 asigna pesos a cinco estrategias: FEES, H1, H2, H3, H4. Suman 100%, son no negativos y no hay deuda. La rejilla tiene pasos de 5%. En el caso principal se permite hasta 100% por estrategia sin puts; H2 tiene un tope de 25% del presupuesto por incertidumbre de modelo. No se impone que las cinco tengan peso positivo ni se fuerzan mínimos en FEES explícito: las alternativas ya comparten el núcleo.

Se maximiza el peor retorno trimestral en CLP real entre contracciones conocidas del PIB. Se desempata por mejor retorno medio en contracciones y, en un empate adicional, menor concentración. No se maximiza CAGR ni se exige correlación negativa mediante una identidad artificial.

Para cada año, solo se usan retornos de trimestres anteriores y PIB con cierre al menos 90 días antes de la decisión. Se exige un mínimo de 20 trimestres y tres contracciones. Las mezclas candidatas se simulan con rebalanceo anual y pesos que fluctúan, no con promedios de retornos que supongan rebalanceo mensual. La curva de H5 usa los pesos elegidos antes de cada año; los pesos finales se publican aparte y no se aplican hacia atrás.

El PIB disponible es revisado, no primeras publicaciones archivadas. El rezago conservador evita incorporar trimestres futuros pero no elimina sesgo por revisiones. Las hipótesis se diseñaron con conocimiento del pasado. Por ello se llama evaluación temporal retrospectiva, sin prometer una prueba independiente en tiempo real.

Se vuelve a optimizar retirando una contracción cada vez. También se muestra una versión de límites prudentes: mínimo 20% de FEES explícito y máximo 60% por estrategia. Es una sensibilidad de restricciones, no normativa oficial ni una mezcla que deba ser superior. Los límites pueden dominar el resultado.

El bootstrap descriptivo por bloques de cuatro trimestres usa 2.000 repeticiones para la diferencia de media en contracciones H5 menos FEES. No reestima toda la selección ni incluye error de valoración de opciones. Hay pocos episodios adversos. No se hacen afirmaciones de significancia conjunta.

## Interpretación

Las estrategias no son cinco activos independientes. Se publican tanto los pesos de presupuesto como la exposición aproximada subyacente: núcleo FEES, BIL, SHY y MBB adicional, antes de financiar la prima. El nocional de put no se suma a los pesos de activos.

El resultado debe juzgarse por pérdidas en contracciones, peor trimestre, recuperación y recursos reales. Una mejora pequeña o un peso cero en puts es un resultado válido; no se fabrica una mezcla para favorecer las hipótesis. Si sigue habiendo pérdidas en contracciones y correlación positiva con PIB, no se declara que el portafolio sea anticíclico demostrado.

Las reglas y el estado normativo permanecen visibles. No se han modelado ingresos fiscales, producción de cobre ni necesidades concretas de caja. Tampoco se certifica TE ex ante o ejecutabilidad de carteras. El alcance es FEES; FRP no se incluye por instrucción expresa.
