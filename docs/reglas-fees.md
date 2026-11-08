# Reglas del FEES verificadas

Consulta: 8 de noviembre de 2026. Fuente principal: [pauta marcada vigente por Hacienda](https://www.hacienda.cl/areas-de-trabajo/finanzas-internacionales/fondos-soberanos/fondo-de-estabilizacion-economica-y-social/politica-de-inversion/pauta-de-inversion-vigente), oficio ordinario 1085/2023, de 15 de junio de 2023. Se conserva el PDF de 18 páginas en `data/fuentes/directrices.pdf` y su extracción en `directrices.txt`. Las páginas siguientes son las del PDF, que coinciden con su numeración impresa.

La fecha del oficio no es su fecha de implementación. El oficio indica que Hacienda comunicaría la entrada en vigencia al agente fiscal. La [rentabilidad oficial](https://www.hacienda.cl/areas-de-trabajo/finanzas-internacionales/fondos-soberanos/fondo-de-estabilizacion-economica-y-social/informacion-financiera/rentabilidad) registra el inicio del componente MBS el **2 de noviembre de 2023**. La política publicada en la fecha de consulta mantiene esta asignación. No se presume que rigiera desde 2020 ni se certifica que no existan instrucciones operativas posteriores no publicadas.

## Mandato y liquidez

El FEES financia necesidades fiscales ante cambios del ciclo y eventos extraordinarios. Según la [política de Hacienda](https://www.hacienda.cl/areas-de-trabajo/finanzas-internacionales/fondos-soberanos/fondo-de-estabilizacion-economica-y-social/politica-de-inversion), mientras su tamaño sea inferior al 5% del PIB, busca maximizar su valor en pesos durante estrés financiero y mantener elevada liquidez. Si supera ese umbral se revisa la asignación, particularmente para los recursos excedentes.

No hay un horizonte contractual único que permita tratarlo como un fondo de jubilación. Puede requerir liquidaciones en crisis. Maximizar el retorno medio en USD no basta para juzgar su política.

## Asignación y comparadores

Fuente: directrices, sección II.2.1, tabla 1, página 9. El anexo A, página 11, expresa los mismos componentes como porcentajes redondeados del bloque soberano de 85%.

| Componente | Peso del FEES | Comparador de la tabla de asignación |
| --- | ---: | --- |
| Letras del Tesoro de EE.UU. | 10% | ICE BofA US Treasury Bills |
| Bonos soberanos de EE.UU. | 40% | Bloomberg Treasury U.S. 1–10 años |
| Bonos soberanos europeos AAA y AA | 19% | Bloomberg Euro Aggregate Treasury Aaa y Aa, 1–10 años |
| Bonos soberanos japoneses | 9% | Bloomberg Treasury Japan 1–10 años |
| Bonos soberanos chinos | 3% | Bloomberg China Treasury 1–10 años |
| TIPS de EE.UU. | 4% | Bloomberg Inflation-Linked U.S. TIPS 1–10 años |
| MBS de agencias de EE.UU. | 15% | Bloomberg US Mortgage-Backed Securities |

Europa excluye Luxemburgo del subíndice Aaa, y Estonia e Irlanda del Aa; ambos se agregan por capitalización relativa. La tabla del anexo A identifica el componente estadounidense como Bloomberg US Treasury Intermediate, `LT08TRUU`; el índice TIPS como `LTI1TRUU`. La página web y el cuerpo del oficio emplean nombres distintos de los del anexo. Se conservan esas denominaciones, sin afirmar una equivalencia exacta no comprobada de proveedores.

El 81% nominal, 4% indexado y 15% MBS aparece también en la web. Para administración, el bloque soberano incluye TIPS y suma **85%**, gestionado por el Banco Central; MBS corresponde a administradores externos. No confundir el 15% de MBS con un límite máximo opcional: es la asignación de referencia.

La [composición efectiva publicada para septiembre de 2026](https://www.hacienda.cl/areas-de-trabajo/finanzas-internacionales/fondos-soberanos/fondo-de-estabilizacion-economica-y-social/informacion-financiera/composicion-actual) informa 81,0%, 4,0% y 15,0%, respectivamente. Reporta duraciones de 3,4, 4,4 y 5,6 años, y 3,8 años para el total. Estos datos de un cierre no son límites normativos ni una historia de duración. No se usan como información disponible para decisiones en 2020.

## Restricciones relevantes para las hipótesis

| Regla | Alcance y ubicación |
| --- | --- |
| Gestión pasiva | Retornos mensuales totales antes de comisiones similares a los comparadores. Anexo A §1, p.11; anexo B §1, p.16. |
| Riesgo soberano | Tracking error **ex ante** anual de 25 pb, calculado diariamente por custodio o middle office. Anexo A §2.2, p.11. No es un límite de volatilidad total ni un permiso para escoger cualquier duración. |
| Madurez al comprar | Bonos soberanos e indexados: entre 1 año y 10 años y 1 mes de madurez remanente. No exige vender al pasar bajo 1 año. Letras sin restricción por instrumento. Anexo A §2.5.a, p.12. Madurez y duración son conceptos distintos. |
| Emisores y monedas soberanos | EE.UU., países europeos del comparador, Japón y China; TIPS de EE.UU. Solo monedas del respectivo comparador. Anexo A §2.3.2 y §2.4, p.12. |
| Efectivo soberano | Máximo 5% del portafolio administrado. Depósitos hasta 15 días, bancos A− o superior en al menos dos clasificadoras. Concentración por banco: 1% si rating medio al menos AA−; 0,5% entre A− y A+. Hay excepciones temporales para flujos. Anexo A §2.3.1, pp.11–12. Letras no se confunden con este efectivo bancario. |
| Futuros soberanos | Futuros soberanos EE.UU. en CBOT, SOFR en CME y futuros de tasas alemanas en Eurex para cobertura, minimizar diferencias o adquirir exposición al comparador. Anexo A §2.5.b, pp.12–13. |
| Cobertura de monedas | Forwards y swaps entre monedas elegibles, con contrapartes y exposición crediticia restringidas. Anexo A §2.6, pp.13–14. |
| Sin activos chilenos | No invertir en emisores chilenos ni instrumentos denominados en CLP. Anexo A §2.8, p.14. Medir rendimiento en CLP no implica comprar un activo en CLP. |
| Sin apalancamiento | No endeudarse para inversión, salvo fallas de liquidación. Nocionales absolutos de futuros y forwards o swaps de moneda agregados hasta 10% del portafolio del agente fiscal. Anexo A §2.8, p.14. |
| Riesgo MBS | Tracking error ex ante anualizado: promedio mensual 20 pb, máximo diario 30 pb. Desviación de duración efectiva frente al comparador hasta ±0,5 años. Anexo B §2.2, p.16. |
| Instrumentos MBS | Pass-through a tasa fija de GNMA, FNMA y FHLMC en programas del comparador; deuda USD del Gobierno o agencias indicadas; TBA con efectivo que cubra exposición; futuros especificados para fines ligados al comparador. Anexo B §2.4, pp.16–17. La deuda del apartado b no puede superar 20% del portafolio MBS: §2.7.d, p.18. No es una banda de peso MBS para el FEES. |
| TBA y futuros MBS | TBA hasta 30%, vencimiento menor a 90 días, sin cortos ni recepción física. Futuros de tasas hasta 10% nocional absoluto, plazo menor a 110 días y sin entrega física soberana; sin apalancamiento. Anexo B §2.6 y §2.7, pp.17–18. |
| Rebalanceo | Con aportes o retiros en fecha instruida por Hacienda; sin ellos, al menos anual. Excepciones de posicionamiento relativo requieren autorización de Hacienda. Sección II.5, p.9. No se supone obtenida ninguna excepción. |

Este resumen recoge las reglas necesarias para el ejercicio, no sustituye el PDF ni constituye una auditoría de todos los límites operativos.

## Decisión para cada hipótesis

| Hipótesis | Estado bajo las reglas publicadas | Tratamiento en el código |
| --- | --- | --- |
| Correlación bonos y acciones | Compatible como diagnóstico externo. Acciones no integran la asignación vigente. | SPY solo sirve para calcular correlaciones con bonos. Peso SPY en carteras: cero. |
| Puts de futuros de cobre | Incompatible con las listas de instrumentos elegibles consultadas. Autorizar futuros de tasas o monedas no autoriza opciones de materias primas. | Excluidas. No se cambia la política ni se inventa un historial de primas. |
| Menor duración del Tesoro | Los bonos cortos pueden ser elegibles por madurez. Una desviación relevante debe cumplir gestión pasiva y TE ex ante. **Cumplimiento de las carteras proxy no verificado.** | Escenarios pequeños, sin variar 40% estratégico. TE realizado se muestra como diagnóstico, nunca como certificación. |
| Más o menos peso estratégico MBS | Incompatible como libre modificación permanente de 15%. No se halló una banda táctica general. | Peso estratégico MBS se conserva. No se usan tolerancias de duración como si fueran bandas de asignación. |

Los ETFs usados no aparecen como tales en la lista de instrumentos elegibles. Son proxies estadísticos para estudiar exposiciones, no una cartera ejecutable ni una recomendación de adquirir ETFs con recursos del FEES.
