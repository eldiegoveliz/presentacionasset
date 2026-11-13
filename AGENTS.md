# Instrucciones del proyecto

Este repositorio corresponde al proyecto final de Asset Pricing 2026 de la Universidad de los Andes, Tema A: fondos soberanos de Chile (FEES y FRP).

## Leer antes de trabajar

- [Encargo y evaluación](docs/encargo.md): requisitos de los dos enunciados entregados por el usuario.
- [Metodología y decisiones](docs/metodologia.md): distinguir decisiones aceptadas, ideas y asuntos pendientes.
- [Registro de IA](docs/registro-ia.md): formato obligatorio y trazabilidad de la asistencia.

Los requisitos del profesor, las instrucciones del usuario y las propuestas del asistente deben quedar identificados por separado. No presentar una propuesta como una exigencia del curso ni como una decisión del equipo. Ante contradicciones entre fuentes, señalarlas y pedir aclaración si afectan el trabajo.

## Forma de trabajo

- Trabajar en el checkout existente. No crear worktrees salvo petición explícita del usuario.
- El destinatario es el Comité Financiero. El encargo académico completo cubre ambos fondos, pero el usuario delimitó esta implementación a FEES y sus alternativas. No añadir FRP a este alcance.
- Evaluar cada fondo de acuerdo con su mandato, horizonte, liquidez y riesgos. Verificar estos elementos en fuentes oficiales antes de tratarlos como hechos. No juzgar una política solamente por su retorno histórico.
- El usuario exige FEES histórico, una cartera por cada una de sus cuatro hipótesis y una quinta mezcla optimizada para proteger recursos reales en CLP durante contracciones chilenas. Los supuestos técnicos están en config.json y requieren revisión académica del equipo.
- No inventar datos, fuentes, resultados, integrantes, firmas ni verificaciones. Separar hechos, supuestos e hipótesis. Citar la fuente y fecha de los datos y de las políticas utilizadas.
- Declarar los supuestos y evaluar la sensibilidad de las conclusiones. No usar información futura para construir decisiones históricas; documentar moneda, retornos, frecuencia y tratamiento de datos faltantes.
- Toda cifra, tabla y gráfico del memo debe provenir del notebook o de una fuente citada. Conservar trazabilidad entre resultados y entregables.
- El notebook debe ejecutarse completo en un runtime limpio de Google Colab, usando archivos entregados o URLs públicas. No depender de rutas privadas de este entorno ni de estado oculto de celdas anteriores.
- Mantener el memo dentro de 10 páginas sin anexos. Es un documento para decidir, con recomendaciones concretas, evidencia e incertidumbre.
- Registrar el uso relevante de IA conforme ocurre: prompts literales, aportes, errores, verificaciones, cambios del equipo y limitaciones. No atribuir al equipo decisiones o revisiones que todavía no hizo.
- Cada integrante debe poder explicar cualquier parte del análisis y del código. Favorecer código comprensible y explicaciones económicas defendibles.

## Alcance actual

El usuario amplió la autorización para investigar las reglas del FEES, descargar datos reales y desarrollar un análisis sencillo de sus cuatro hipótesis. La aclaración posterior pide incluir puts y MBS en la simulación, una cartera por hipótesis. Mostrar su estado normativo: simular un instrumento fuera de política no equivale a autorizar su ejecución. No usar GitHub Actions.

Las reglas verificadas están en `docs/reglas-fees.md`. La referencia es el FEES observado completo, no la antigua proxy del 69%. Las alternativas son núcleo FEES con satélites, y H2 usa puts sintéticas de 12 meses valoradas mensualmente; no son contratos históricos COMEX observados. Se convierten los retornos con dólar observado diario BCCh y se deflactan con IPC. La quinta alternativa selecciona pesos antes de cada año y publica aparte los pesos finales.

Conservar el filtro normativo. La existencia de bandas MBS 13%–17% publicadas en informes anuales 2023/2024 corrige el resumen anterior; no equivale a elegibilidad ni certificación ex ante. No presentar la mejor mezcla de una rejilla como óptimo universal ni afirmar anticiclicidad si el resultado no la demuestra.

Al cambiar el análisis, ejecutar `python analisis.py`, `python verificar.py` y `python validar_notebook.py`; este último regenera y ejecuta el notebook y prepara la entrega. Conservar los datos congelados y su trazabilidad. No reemplazar los archivos de datos sin solicitud explícita o uso deliberado de `datos.py --actualizar`.

El análisis del FRP y el memo académico final quedan fuera de esta etapa. No atribuir revisiones o firmas al equipo.
