# FEES: datos, reglas y análisis reproducible

Análisis exploratorio de las cuatro ideas del usuario: correlación bonos/acciones, puts de cobre, menor duración del Tesoro y peso de MBS. Las reglas oficiales están en [reglas-fees.md](docs/reglas-fees.md). Los resultados calculados están en [informe.md](results/informe.md).

Las puts de cobre quedan excluidas y se conserva el 15% estratégico de MBS. Se comparan tres reducciones pequeñas de duración con una referencia proxy del **bloque USD, 69% de la asignación del FEES**. Los ETFs no replican el fondo completo ni constituyen instrumentos recomendados para su ejecución. El cumplimiento ex ante no puede certificarse con estas series públicas.

## Ejecutar localmente

Se requiere Python 3.10 o posterior. Desde la carpeta del repositorio:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python analisis.py
python verificar.py
```

En Windows, activar con `.venv\Scripts\activate` y usar `python` en lugar de `python3`. El análisis usa los CSV entregados: no llama a Yahoo ni a FRED. Genera tablas, cuatro gráficos y el mini informe en `results/`.

Para descargar nuevamente los datos hasta el corte fijo del 31 de octubre de 2026:

```bash
python datos.py --actualizar
python analisis.py
python verificar.py
```

`python datos.py` usa la caché cuando existe. `--actualizar` reemplaza los archivos y su manifiesto. Se requiere acceso público a Yahoo y FRED, sin claves. Si una API falla, el análisis sigue disponible con los datos entregados; no se crean series artificiales. Las descargas pueden revisarse con el tiempo y cambiar cifras por redondeo o revisiones del proveedor.

## Abrir el notebook en Colab

Abrir [notebooks/fees.ipynb](notebooks/fees.ipynb) en Google Colab y ejecutar todas las celdas. La primera celda busca el proyecto local o descarga su archivo público desde la rama `analisis-fees`. También acepta `entrega_fees.zip` si se sube al runtime antes de ejecutar. No necesita claves ni carpetas privadas.

El notebook muestra el mismo código de análisis, dividido en funciones con explicaciones económicas. La descarga de precios está separada: Colab usa los datos congelados incluidos. Para regenerar el notebook después de editar el análisis:

```bash
python crear_notebook.py
```

Para preparar el ZIP con código, datos, documentación y notebook:

```bash
python preparar_entrega.py
```

## Qué revisar

| Archivo | Para qué sirve |
| --- | --- |
| [Informe generado](results/informe.md) | Resultados, gráficos, incertidumbre y límites de las conclusiones |
| [Reglas verificadas](docs/reglas-fees.md) | Mandato, pesos, restricciones y admisibilidad por hipótesis, con páginas oficiales |
| [Metodología](docs/metodologia.md) | Pesos, períodos, costos, proxies y decisiones del asistente que requieren revisión del equipo |
| [Guía del código](docs/guia-codigo.md) | Qué hace cada cálculo y cómo explicarlo en la presentación |
| `config.json` | Supuestos fijados antes de comparar resultados |
| `datos.py` | Descargas, CSV, originales Yahoo y metadatos |
| `analisis.py` | Retornos, carteras, métricas, bootstrap y mini informe |
| `verificar.py` | Pruebas de cálculos, moneda, integridad y ejecución sin red |
| `data/raw/` y `data/metadatos.json` | Datos reproducibles, URLs, fechas y hashes SHA-256 |
| `data/fuentes/` | PDF oficial y páginas de Hacienda guardadas |
| [Registro de IA](docs/registro-ia.md) | Prompts, aportes, errores y verificaciones del asistente |
| [Encargo del curso](docs/encargo.md) | Requisitos oficiales y fechas |

Este trabajo aborda el FEES parcialmente. El encargo académico completo también exige analizar el FRP. La revisión del equipo, el memo final y las firmas siguen pendientes. El [traspaso anterior](docs/traspaso-anterior.md) se conserva como antecedente, no como instrucciones de ejecución vigentes.
