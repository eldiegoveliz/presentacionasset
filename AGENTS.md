# Instrucciones del proyecto

Este repositorio corresponde al proyecto final de Asset Pricing 2026 de la Universidad de los Andes, Tema A: fondos soberanos de Chile (FEES y FRP).

## Leer antes de trabajar

- [Encargo y evaluación](docs/encargo.md): requisitos de los dos enunciados entregados por el usuario.
- [Metodología y decisiones](docs/metodologia.md): distinguir decisiones aceptadas, ideas y asuntos pendientes.
- [Registro de IA](docs/registro-ia.md): formato obligatorio y trazabilidad de la asistencia.

Los requisitos del profesor, las instrucciones del usuario y las propuestas del asistente deben quedar identificados por separado. No presentar una propuesta como una exigencia del curso ni como una decisión del equipo. Ante contradicciones entre fuentes, señalarlas y pedir aclaración si afectan el trabajo.

## Forma de trabajo

- Trabajar en el checkout existente. No crear worktrees salvo petición explícita del usuario.
- El destinatario es el Comité Financiero. Responder para ambos fondos si están bien invertidos y qué cambiar de su política, con razones.
- Evaluar cada fondo de acuerdo con su mandato, horizonte, liquidez y riesgos. Verificar estos elementos en fuentes oficiales antes de tratarlos como hechos. No juzgar una política solamente por su retorno histórico.
- La idea inicial del usuario es comparar portafolios de prueba. No hay instrumentos, ponderaciones, período ni modelo aprobados todavía.
- No inventar datos, fuentes, resultados, integrantes, firmas ni verificaciones. Separar hechos, supuestos e hipótesis. Citar la fuente y fecha de los datos y de las políticas utilizadas.
- Declarar los supuestos y evaluar la sensibilidad de las conclusiones. No usar información futura para construir decisiones históricas; documentar moneda, retornos, frecuencia y tratamiento de datos faltantes.
- Toda cifra, tabla y gráfico del memo debe provenir del notebook o de una fuente citada. Conservar trazabilidad entre resultados y entregables.
- El notebook debe ejecutarse completo en un runtime limpio de Google Colab, usando archivos entregados o URLs públicas. No depender de rutas privadas de este entorno ni de estado oculto de celdas anteriores.
- Mantener el memo dentro de 10 páginas sin anexos. Es un documento para decidir, con recomendaciones concretas, evidencia e incertidumbre.
- Registrar el uso relevante de IA conforme ocurre: prompts literales, aportes, errores, verificaciones, cambios del equipo y limitaciones. No atribuir al equipo decisiones o revisiones que todavía no hizo.
- Cada integrante debe poder explicar cualquier parte del análisis y del código. Favorecer código comprensible y explicaciones económicas defendibles.

## Alcance actual

El usuario amplió la autorización para investigar las reglas del FEES, descargar datos reales y desarrollar un análisis sencillo de sus cuatro hipótesis. No modificar la política para habilitar nuevas inversiones. No usar GitHub Actions.

Las reglas verificadas están en `docs/reglas-fees.md`. El código compara proxies del bloque USD de 69%, sin presentarlos como réplica del fondo. Preservar los pesos estratégicos no certifica elegibilidad de instrumentos ni cumplimiento ex ante. Los supuestos están en `config.json` y `docs/metodologia.md`.

Al cambiar el análisis, regenerar el notebook con `python crear_notebook.py` y ejecutar `python analisis.py` y `python verificar.py`. Conservar los datos congelados y su trazabilidad. No reemplazar los archivos de datos sin solicitud explícita o uso deliberado de `datos.py --actualizar`.

El análisis del FRP y el memo académico final quedan fuera de esta etapa. No atribuir revisiones o firmas al equipo.
