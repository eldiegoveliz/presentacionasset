# Registro de uso de IA

Plantilla de trabajo para el anexo obligatorio. Mantener una fila por herramienta y agregar en sus campos los usos sucesivos. Los prompts extensos pueden transcribirse en bloques identificados, referenciados desde la tabla. No sustituir prompts literales por resúmenes.

Este registro inicial documenta la creación de instrucciones del repositorio; no afirma que estos textos se hayan incorporado al memo o al notebook. El equipo debe completar los usos posteriores y revisar el registro antes de firmar.

| Herramienta, modelo y versión | Prompts utilizados | Qué se incorporó al entregable | Errores detectados en el output | Cómo se verificó el resultado | Qué cambió el equipo | Limitaciones que persisten |
| --- | --- | --- | --- | --- | --- | --- |
| Codex, basado en GPT-6 según identificación de la sesión. Versión específica no informada. | P1 y P2, transcritos abajo. Los enunciados completos fueron aportados por el usuario como contexto. | Documentación del repositorio: `AGENTS.md`, `docs/encargo.md`, `docs/metodologia.md` y este registro. No hay incorporación al memo, notebook ni cálculos por ahora. | No se han documentado errores en esta redacción; la revisión del equipo está pendiente. Esto no demuestra ausencia de errores. | El asistente cotejó la documentación con los textos proporcionados y comprobó la presencia de los archivos y su contenido. No consultó los enlaces originales ni verificó datos financieros. | El usuario autorizó documentar los enunciados. No se han comunicado correcciones del equipo a estos archivos; revisión pendiente. | Las fuentes originales enlazadas no se comprobaron de forma independiente. Modelo sin versión específica disponible. No existe análisis empírico ni validación financiera. Actualizar esta fila y conservar los prompts adicionales si se incorpora asistencia posterior. |

## Prompts relevantes de esta tarea

### P1 — solicitud de documentación, dentro del mensaje con los enunciados

El siguiente fragmento se transcribe literalmente; el contexto restante del mensaje eran los enunciados del proyecto, organizados en [encargo.md](encargo.md).

```text
estoy pensando en hacer portafolios de prueba para ver opciones de instrumentos como dijo gpt. aun no hagas nada, te pued odar las instrucciones axactas para que hagas markdowns con ellas y que sea permanente, que tal?
```

### P2 — autorización para crear los archivos

```text
esas son las dos instrucciones que tenemos, juegue
```

## Continuación del análisis, 8 de noviembre de 2026

| Herramienta, modelo y versión | Prompts utilizados | Qué se incorporó al entregable | Errores detectados en el output | Cómo se verificó el resultado | Qué cambió el equipo | Limitaciones que persisten |
| --- | --- | --- | --- | --- | --- | --- |
| T3 Code mediante Codex, modelo `gpt-6.1-sol`, esfuerzo high. Sin identificador de revisión adicional informado por el proveedor. | P3, mensaje literal de continuación transcrito abajo. El prompt anterior citado por el usuario está incluido en él. | `datos.py`, `analisis.py`, `config.json`, `verificar.py`, notebook, reglas, metodología, guía, datos y resultados. `crear_notebook.py` genera el mismo análisis visible en Colab. | Se supuso inicialmente que los ETFs no tenían splits; BIL tiene un reverse split 1:2 en 2017 y Yahoo ya ajusta sus cierres. Se consideró por error DEXCHUS como CLP, pero es yuan chino: se detectó antes de generar resultados CLP y se reemplazó por CLP=X, validando moneda y tipo de instrumento. Un mismo User-Agent funcionaba con Yahoo y demoraba FRED: se diferenciaron por host. Los primeros intentos de análisis se iniciaron antes de terminar las descargas y fallaron por archivos ausentes; la entrega final usa archivos completos. Una edición de documentación fue rechazada por el formato del parche y se reaplicó correctamente. | PDF oficial guardado y cotejado por páginas; composición publicada de septiembre de 2026; eventos y cierres diarios frente a ajustes Yahoo; URLs y hashes de datos; pruebas de costos, capital inicial, CAGR, pesos, moneda y resultados reales. Ver `docs/validacion.md` para la ejecución efectivamente comprobada. | El usuario autorizó continuar; no hay revisiones del código, cambios de interpretación ni firmas comunicadas por integrantes. Las elecciones técnicas son del asistente y requieren revisión del equipo. | Cobertura proxy del bloque USD 69%, no FEES completo. Faltan índices oficiales y verificación de TE ex ante. ETFs no son una cartera elegible certificada. Hipótesis y política aplicadas retrospectivamente; bootstrap descriptivo sin ajuste múltiple. Conversión Yahoo no es dólar observado. No se estudia FRP, ni se produce el memo académico final. |

### P3 — continuación con autorización de datos y código

Se transcribe el mensaje relevante literalmente. La instrucción de preferencia de modelo y el contexto de entorno se conservan en la sesión de la herramienta; no se delegó trabajo.

```text
https://github.com/eldiegoveliz/presentacionasset/tree/main

tu eres el proximo agente este fue le prompt de antes:
1. mucha correlacion entre bonos y acciones recientemente (o sea no hay hedge por usar bonos)
2. puts sobre futuros del cobre
3. bonos del tesoro de menos duracion
4. menos o mas ponderacion a los mbs

que se sigan cumpliendo las reglas del fees: buscalas y dejalas en algun archivo en el repo



dale con la busqueda de datos (yahoo o fred y en la tarea instrucciones hay cosas sobre donde buscar datos). dale con el codigo: NO HAGAS ALGO COMPLICADO, TENEMOS QUE EXPLICAR EL CODIGO.&#x20;



No pares hasta que termines, si tienes dudas, creeme no voy a saber mas que tu.



GODSPEED.


tuvimos problemas con api por restricciones del entorno del otro agente, tu no deberias tenerlo. porfa salvanos
```

Se conservó `&#x20;` tal como aparece en el mensaje recibido. No se atribuye al equipo la verificación efectuada únicamente por el asistente.

## Cierre del anexo para el entregable final

Completar y firmar solamente después de revisar todos los usos de IA del entregable, incluidos los de los demás integrantes y herramientas. No atribuir a los integrantes verificaciones hechas únicamente por el asistente.

Declaramos que lo anterior es completo y veraz.

| Integrante | Firma |
| --- | --- |
| Por completar | Por completar |
| Por completar | Por completar |
| Por completar | Por completar |
| Por completar | Por completar |
| Por completar | Por completar |
| Por completar | Por completar |
