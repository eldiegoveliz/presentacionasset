"""Genera un notebook con el código visible, sin mantener dos análisis distintos."""
from pathlib import Path

import nbformat as nbf

RAIZ = Path(__file__).resolve().parent


def crear():
    nb = nbf.v4.new_notebook()
    nb.metadata["kernelspec"] = {"display_name": "Python 3", "language": "python", "name": "python3"}
    nb.metadata["language_info"] = {"name": "python", "version": "3.11"}
    nb.cells = [nbf.v4.new_markdown_cell("""# FEES: duración y diversificación

Ejecutar todas las celdas en orden. Se usan los datos congelados del repositorio, sin llamar a APIs de precios. La referencia cubre el bloque USD de **69%** de la asignación; no replica el FEES completo. Puts de cobre quedan excluidas y MBS conserva su peso estratégico.

En Colab, esta celda descarga el proyecto público si no encuentra los archivos. También puede subir `entrega_fees.zip` al runtime antes de ejecutar. Los datos, las reglas y los prompts de IA forman parte de la entrega.
"""), nbf.v4.new_code_cell('''from pathlib import Path
import io
import os
import zipfile
import requests

proyecto = Path.cwd()
if not (proyecto / "config.json").exists() and (proyecto.parent / "config.json").exists():
    proyecto = proyecto.parent
if not (proyecto / "config.json").exists():
    archivo = proyecto / "entrega_fees.zip"
    if archivo.exists():
        contenido = archivo.read_bytes()
    else:
        url = "https://github.com/eldiegoveliz/presentacionasset/archive/refs/heads/analisis-fees.zip"
        respuesta = requests.get(url, timeout=60)
        respuesta.raise_for_status()
        contenido = respuesta.content
    destino = proyecto / "proyecto_fees"
    with zipfile.ZipFile(io.BytesIO(contenido)) as z:
        z.extractall(destino)
    proyecto = next(destino.rglob("config.json")).parent
os.chdir(proyecto)
print("Archivos de trabajo:", proyecto)
'''), nbf.v4.new_code_cell('%pip install -q -r requirements.txt'),
        nbf.v4.new_markdown_cell("""## Preparación

El código siguiente proviene de `analisis.py`. `config.json` fija pesos y costos antes de comparar resultados. El análisis solo lee archivos locales. `verificar.py` comprueba integridad, cálculos y moneda.
""")]
    fuente = (RAIZ / "analisis.py").read_text()
    fuente = fuente.split('if __name__ == "__main__":')[0].rstrip()
    fuente = fuente.replace('from datos import RAIZ, leer_config', '''RAIZ = Path.cwd()

def leer_config():
    return json.loads((RAIZ / "config.json").read_text())''')
    # Cada función aparece con una explicación y su implementación real.
    partes = fuente.split("\ndef ")
    nb.cells.append(nbf.v4.new_code_cell(partes[0]))
    explicaciones = {
        "leer_config": "Leer los supuestos guardados. No ajustarlos para favorecer un resultado.",
        "cargar_mensuales": "Comprobar precios y distribuciones. Convertir cierres diarios a retornos mensuales sin interpolar.",
        "pesos_escenario": "Mover una cantidad fija de IEF a SHY. Mantener las clases estratégicas y normalizar solo el bloque estudiado.",
        "cartera": "Sumar pesos por retornos, rebalancear cada mes y descontar costos sobre compras más ventas.",
        "riqueza_y_caida": "Acumular retornos e incluir el capital inicial al medir pérdidas desde máximos.",
        "metricas": "Calcular retorno compuesto anual, volatilidad anual, mayor caída mensual y peor mes.",
        "bootstrap_media": "Remuestrear las diferencias en bloques de meses. No confundir el intervalo de medias con uno de CAGR.",
        "ejecutar": "Comparar todos los escenarios y períodos definidos. Guardar tablas, gráficos y sensibilidad sin elegir un ganador.",
        "informe": "Escribir el mini informe directamente desde las tablas calculadas. Los límites de las conclusiones quedan junto a los resultados."
    }
    for parte in partes[1:]:
        nombre = parte.split("(", 1)[0]
        nb.cells.append(nbf.v4.new_markdown_cell(f"### {nombre}\n\n{explicaciones[nombre]}"))
        nb.cells.append(nbf.v4.new_code_cell("def " + parte.strip()))
    nb.cells.extend([
        nbf.v4.new_markdown_cell("## Ejecutar el análisis\n\nTodas las cifras del informe salen de esta ejecución."),
        nbf.v4.new_code_cell("resumen = ejecutar()\ndisplay(resumen.round(3))"),
        nbf.v4.new_code_cell('''from IPython.display import Image, Markdown, display
for nombre in ["riqueza", "caidas", "correlacion", "tasas"]:
    display(Image(filename=str(RAIZ / f"results/figuras/{nombre}.png")))
display(Markdown((RAIZ / "results/informe.md").read_text()))'''),
        nbf.v4.new_markdown_cell("## Verificación\n\nLas pruebas comprueban capital inicial, rebalanceo, costos, pesos estratégicos, hashes y conversión CLP. No certifican el tracking error oficial ex ante."),
        nbf.v4.new_code_cell("import subprocess\nimport sys\nsubprocess.run([sys.executable, 'verificar.py'], check=True)"),
        nbf.v4.new_markdown_cell("""## Qué falta para el trabajo académico completo

Revisar los supuestos y resultados con el equipo, analizar FRP y preparar el memo de hasta 10 páginas. Consultar `docs/guia-codigo.md` para practicar la defensa. Revisar `docs/registro-ia.md` y completar los aportes propios y las firmas antes de entregar. Ninguna firma está supuesta.
""")])
    ruta = RAIZ / "notebooks/fees.ipynb"
    ruta.parent.mkdir(exist_ok=True)
    # IDs estables: regenerar el notebook no produce cambios aleatorios.
    for i, celda in enumerate(nb.cells):
        celda["id"] = f"fees-{i:02d}"
    nbf.write(nb, ruta)
    print(ruta)


if __name__ == "__main__":
    crear()
