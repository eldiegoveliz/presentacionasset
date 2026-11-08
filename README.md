# FEES: protección anticíclica en pesos

El análisis compara el FEES histórico observado, cuatro alternativas y una quinta mezcla optimizada. La pregunta es cuánto poder adquisitivo conserva el fondo durante contracciones del PIB chileno. El usuario delimitó el alcance a FEES; FRP queda fuera de este trabajo.

[Informe generado](results/informe.md) · [Notebook](notebooks/fees.ipynb) · [Reglas y fuentes](docs/reglas-fees.md) · [Guía del código](docs/guia-codigo.md)

## Carteras y objetivo

| Estrategia | Construcción |
| --- | --- |
| FEES histórico | Retornos oficiales mensuales netos de Hacienda, 2014–septiembre 2026 |
| H1 Más letras | 90% FEES y 10% BIL, rebalanceo anual |
| H2 Puts largas | FEES con puts teóricas de 12 meses, nocional 10%, financiadas vendiendo parte del FEES |
| H3 Treasury corto | 80% FEES y 20% SHY, rebalanceo anual |
| H4 Más MBS | 90% FEES y 10% MBB, rebalanceo anual; sensibilidad de reducción MBS posterior a su introducción |
| H5 Mezcla optimizada | Asigna presupuesto entre FEES y H1–H4; pesos suman 100%, sin cortos ni deuda |

H5 maximiza el peor retorno trimestral real en CLP durante contracciones del PIB, buscando en pasos de 5%. Se permite concentrar una estrategia sin puts en lugar de forzar una mezcla; se conserva como sensibilidad un mínimo de 20% FEES explícito y máximo de 60% por estrategia. Los pesos finales describen una decisión posterior a la muestra. La curva histórica de H5 usa elecciones anteriores a cada año, con al menos 90 días de rezago para el PIB. Las estrategias comparten el núcleo FEES: sus pesos no representan cinco activos independientes.

Las puts se valoran mensualmente manteniendo contrato sintético, strike y cantidad hasta vencer. No se dispone de primas ni curvas históricas de contratos COMEX identificados. Se conserva el riesgo de base del proxy continuo usado para construir el futuro sintético. La simulación no certifica ejecutabilidad ni cumplimiento de las directrices.

## Ejecutar sin APIs

Desde esta carpeta, con Python 3.10 o posterior:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python analisis.py
python verificar.py
python validar_notebook.py
```

En Windows, activar con `.venv\Scripts\activate` y usar `python` en lugar de `python3`. El análisis usa los datos entregados. La última orden ejecuta el notebook en un kernel temporal desde el ZIP, elimina resultados previos y compara doce salidas con el script. También guarda el notebook ejecutado y actualiza `entrega_fees.zip`.

## Datos oficiales y descargas

- FEES: 153 retornos mensuales oficiales y saldo efectivo en USD. Se conserva la extracción de cada informe, URL, página y hash del PDF. Cada retorno se coteja contra la prosa del mismo informe.
- Tipo de cambio: dólar observado diario BCCh, serie F073.TCO.PRE.Z.D. Se toma el último valor publicado disponible por mes; no se usa Yahoo CLP=X.
- Ciclo e inflación: PIB real trimestral desestacionalizado BCCh, serie F032.PIB.FLU.R.CLP.EP18.Z.Z.1.T, e IPC mensual BCCh con fuente INE. Se usan trimestres completos publicados, sin interpolar el PIB.
- Satélites: cierres ajustados Yahoo BIL, SHY y MBB. Cobre HG=F y tasas FRED para la valoración teórica; volatilidad conocida al comprar.

Para reproducir adquisición y extracción:

```bash
python datos_oficiales.py
python datos.py
```

Ambos usan caché. `python datos.py --actualizar --solo-cobre` amplía únicamente el cobre desde 2010 para el calentamiento de volatilidad. Una descarga nueva puede contener revisiones y exige repetir el análisis. No se necesitan claves ni GitHub Actions. Las páginas y extracciones oficiales están en `data/oficial/`; los PDF descargados completos se guardan en una caché local excluida de Git y del ZIP.

Se detectó un enlace de Hacienda de julio 2016 que devolvía junio. El script utiliza el informe correcto de DIPRES y valida la portada. Los informes anuales 2023/2024 publican bandas MBS 13%–17%; esta información corrige la conclusión anterior de que no existían bandas publicadas.

## Colab y archivos

Abrir `notebooks/fees.ipynb` en Google Colab y ejecutar todo. La primera celda encuentra el proyecto local, acepta `entrega_fees.zip` subido al runtime o descarga la rama pública `analisis-fees`. No requiere rutas privadas ni llamadas a APIs de mercado para calcular resultados.

| Archivo | Función |
| --- | --- |
| `datos_oficiales.py` | Extraer FEES, dólar observado, PIB, IPC y saldo con trazabilidad |
| `datos.py` | Descargar precios de mercado y tasas con caché |
| `carteras.py` | Rebalanceo anual, puts largas y cálculos de riqueza |
| `optimizacion.py` | Rejilla de pesos, simulación anual y elección temporal |
| `analisis.py` | Unir datos, evaluar contracciones, generar gráficos e informe |
| `config.json` | Pesos, costos y límites del experimento |
| `crear_notebook.py` | Mostrar los mismos tres módulos de cálculo en el notebook |
| `verificar.py` | Verificar datos oficiales y cálculos económicos |
| `validar_notebook.py` | Probar una ejecución completa en kernel nuevo |
| `preparar_entrega.py` | Crear el ZIP sin Git, entorno, secretos ni caché de PDF |

Los resultados anteriores de la proxy parcial de 69% fueron retirados para evitar confusiones; se conservan en el historial Git. El memo académico, la revisión del equipo y sus firmas siguen pendientes. El informe explica que el PIB es revisado y que una mejora pequeña no demuestra protección anticíclica futura.
