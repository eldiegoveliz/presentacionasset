# Encargo del proyecto final — Asset Pricing 2026

## Procedencia y alcance

Transcripción organizada y consolidada de las dos instrucciones pegadas por el usuario: la página del proyecto en Canvas/documento compartido y el PDF de enunciados con su anexo de IA. Las secciones duplicadas se consolidan sin añadir exigencias. Los enlaces no se han consultado independientemente; esta referencia se basa en el texto proporcionado.

- Curso: Universidad de los Andes, Asset Pricing (MSCF-2002 / EAD-0329).
- Profesor: Juan Sotes Paladino.
- Modalidad: grupos de 6 integrantes; cuatro grupos por tema.
- Proyecto: 30% de la nota final del curso.
- Tema asignado según el usuario: Tema A, fondos soberanos de Chile (también referido como «Tema 1»).
- [Documento compartido](https://docs.google.com/document/d/1EZsJJcdbAHwQY6Fj1Lrt9rj0nqhjDyUuX6Hzwa3Gtmg/edit?tab=t.t6c39rdo1tzz).
- [PDF en Canvas](https://uandes.instructure.com/courses/47940/files/4955769?wrap=1).

## Pregunta y destinatario

Según el enunciado, Chile tiene dos fondos soberanos creados por la Ley de Responsabilidad Fiscal de 2006: el Fondo de Estabilización Económica y Social (FEES) y el Fondo de Reserva de Pensiones (FRP). Sus políticas de inversión las fija el Ministerio de Hacienda, con asesoría del Comité Financiero; las políticas y el desempeño son públicos.

El equipo asesora al Comité Financiero y debe responder:

> ¿Están bien invertidos los fondos soberanos de Chile?
>
> ¿Qué cambiarían de su política de inversión, y por qué?

La respuesta debe cubrir **ambos fondos**. Las afirmaciones del enunciado son contexto del encargo; las cifras y políticas empleadas en el análisis requerirán sus fuentes correspondientes.

Las instrucciones son deliberadamente breves: precisar la pregunta, definir el criterio de evaluación, encontrar datos y escoger herramientas del curso forma parte de lo evaluado. No se impone una lista de métodos. El equipo debe justificar sus supuestos y analizar cuánto cambian las conclusiones cuando estos cambian. Si una recomendación solo se sostiene bajo un supuesto particular, debe decirlo.

El Tema B, comprar o arrendar vivienda en Chile, es el tema alternativo del curso y queda fuera del alcance de este equipo.

## Fechas oficiales de 2026

| Fecha | Actividad |
| --- | --- |
| Miércoles 28 de octubre | Grupos conformados en Canvas |
| Jueves 29 de octubre | Asignación aleatoria de temas |
| Lunes 16 de noviembre | Entrega final de todos los grupos: memo, notebook, datos necesarios y anexo de IA |
| Martes 17 de noviembre | Presentaciones del Tema A |
| Jueves 19 de noviembre | Presentaciones del Tema B |

No se proporcionó hora límite de entrega.

## Componentes de evaluación

### Informe — 40%

- **Memo dirigido al Comité Financiero:** máximo 10 páginas, sin anexos. Debe servir para tomar una decisión; no es un informe de todo lo realizado.
- **Notebook de Google Colab:** reproduce el análisis de principio a fin en un runtime limpio. Carga datos desde archivos entregados junto al notebook o desde una URL pública.
- **Trazabilidad:** toda cifra, tabla y gráfico del memo debe salir del notebook o de una fuente citada. Declarar explícitamente los supuestos que sustituyan datos.
- **Anexo obligatorio de uso de IA:** seguir los siete campos del PDF, recogidos en [registro-ia.md](registro-ia.md).
- **Evaluación por pares:** cada integrante califica de 1 a 5 a cada compañero. Si X es el puntaje del informe del grupo y P es el promedio recibido por un integrante, su puntaje es `X × (P − 1) / 4`. Con P = 4 recibe el 75% del puntaje del informe grupal.

### Evaluación oral comparativa — 30%

Todos los grupos presentan y comentan. Al inicio se sortea qué otro grupo del mismo tema critica cada grupo. Cada grupo critica a uno y es criticado por uno.

| Bloque | Duración máxima | Responsable |
| --- | --- | --- |
| Presentación | 12 minutos | Grupo que presenta |
| Comentarios | 7 minutos | Grupo sorteado para comentar |
| Preguntas | 5 minutos | Profesor y audiencia; responden integrantes designados |

La crítica se basa en comparar con el enfoque propio:

- Diferencias en cómo se planteó el problema.
- Metodología alternativa que emplearían y por qué.
- Razones por las que podrían obtenerse resultados distintos.
- Fortalezas y debilidades del trabajo evaluado.

Se valoran la autenticidad del análisis, la coherencia metodológica y la reflexión crítica más que la perfección técnica.

### Evaluación individual — 30%

Se basa en las respuestas durante la presentación. El profesor o los ayudantes designan quién responde. Cada integrante debe explicar cualquier parte del trabajo, incluido el código. Según las instrucciones, esta nota no es disputable.

## Rúbricas

### Informe

| Criterio | Peso dentro del informe | Qué se evalúa |
| --- | --- | --- |
| Enfoque conceptual y claridad | 25% | Problema, destinatario y criterio de juicio definidos; recomendación concreta que se sigue del análisis |
| Rigor analítico y empírico | 30% | Modelos y herramientas bien aplicados; datos con fuente y revisados; incertidumbre medida; conclusiones proporcionales a la evidencia |
| Originalidad y creatividad | 25% | Preguntas o interpretaciones propias; aporte del equipo por sobre la IA, documentado en el registro |
| Comunicación | 20% | Texto, gráficos y tablas claros; documento útil para decidir |

### Evaluación oral comparativa

| Criterio | Peso dentro del componente | Qué se evalúa |
| --- | --- | --- |
| Presentación | 50% | Claridad, síntesis e implicancias económicas; respetar el tiempo y presentar sin leer |
| Crítica | 50% | Análisis crítico y contraste con el enfoque propio |

### Evaluación individual

| Criterio | Peso dentro del componente | Qué se evalúa |
| --- | --- | --- |
| Respuestas a preguntas | 100% | Explicar cualquier parte, incluido el código, y defender decisiones con argumentos propios |

## Herramientas, fuentes y uso de IA

- Se recomienda Python en Google Colab: pandas, numpy, matplotlib y statsmodels. Es una recomendación, no una metodología obligatoria.
- Fuentes sugeridas: Banco Central de Chile, CMF, Yahoo Finance, FRED y datos de Kenneth French (Dartmouth), entre otras. La lista no garantiza la calidad ni pertinencia de cada serie.
- Se permite y espera usar IA, citando herramienta, modelo, versión y prompts, y mostrando razonamiento propio.
- **Contenido generado por IA sin citación será tratado como plagio.**
- Se evalúa lo que agrega el equipo: preguntas a la herramienta, respuestas descartadas o corregidas y capacidad de defender el resultado sin ella.

## Criterios de excelencia

- Datos de alta calidad y/o originales construidos por el grupo.
- Pregunta propia y precisa, pensada para el destinatario de la decisión.
- Conclusiones que reconocen cuánto se sabe y cuánto no.
- Resultados conectados con implicancias prácticas.
- Presentación profesional y narrativa coherente.
- Capacidad de responder preguntas sobre cualquier parte del trabajo.

## Formato obligatorio del anexo de IA

Una fila por herramienta utilizada, con todos los campos completos:

1. Herramienta, modelo y versión.
2. Prompts relevantes transcritos literalmente, especialmente los que cambiaron el resultado.
3. Qué código, texto o cálculo se incorporó y en qué sección o celda.
4. Errores detectados en el output.
5. Cómo y contra qué se verificó el resultado.
6. Qué corrigió, descartó o reescribió el equipo.
7. Limitaciones persistentes y su efecto en las conclusiones.

Debe incluir: «Declaramos que lo anterior es completo y veraz», integrantes y firmas. Si no se usó IA, el PDF exige escribir «No se utilizó IA en este entregable» y firmar igualmente. Esa declaración no corresponde a un entregable que incorpore esta asistencia.
