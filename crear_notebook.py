"""Genera el notebook con los mismos motores, búsqueda y análisis visibles."""
from pathlib import Path
import nbformat as nbf
RAIZ = Path(__file__).resolve().parent
BOOTSTRAP = 'from pathlib import Path\nimport io\nimport os\nimport zipfile\nimport requests\n\nproyecto = Path.cwd()\nif not (proyecto / "config.json").exists() and (proyecto.parent / "config.json").exists():\n    proyecto = proyecto.parent\nif not (proyecto / "config.json").exists():\n    archivo = proyecto / "entrega_fees.zip"\n    if archivo.exists():\n        contenido = archivo.read_bytes()\n    else:\n        url = "https://github.com/eldiegoveliz/presentacionasset/archive/refs/heads/analisis-fees.zip"\n        respuesta = requests.get(url, timeout=60)\n        respuesta.raise_for_status()\n        contenido = respuesta.content\n    destino = proyecto / "proyecto_fees"\n    with zipfile.ZipFile(io.BytesIO(contenido)) as z:\n        z.extractall(destino)\n    proyecto = next(destino.rglob("config.json")).parent\nos.chdir(proyecto)\nprint("Archivos de trabajo:", proyecto)\n'


def crear():
    nb = nbf.v4.new_notebook()
    nb.metadata["kernelspec"] = {"display_name": "Python 3", "language": "python", "name": "python3"}
    nb.cells = [nbf.v4.new_markdown_cell("""# FEES y cinco alternativas: protección anticíclica en CLP

Referencia: FEES histórico observado. H1 más letras, H2 puts de 12 meses, H3 Treasury corto, H4 más MBS. H5 asigna presupuesto entre esas cinco estrategias, con una búsqueda de pesos que prioriza el peor trimestre de contracción del PIB en CLP real.

Los datos oficiales están entregados. No se consultan APIs de precios al analizar. La primera celda encuentra el proyecto local, acepta entrega_fees.zip subido al runtime o descarga el archivo público de GitHub. No se necesitan credenciales.

Las puts son modeladas y la evaluación usa PIB revisado con rezago conservador. Un mejor resultado de entrenamiento no garantiza protección futura ni certifica admisibilidad normativa.
"""), nbf.v4.new_code_cell(BOOTSTRAP), nbf.v4.new_code_cell('%pip install -q -r requirements.txt')]
    explicaciones = {
        "precio_put_black76": "Prima europea teórica. Al vencer queda el valor intrínseco, no se renueva mensualmente.",
        "cartera_anual": "Presupuesto completo: rebalancear en enero y dejar fluctuar los pesos durante el año.",
        "put_larga": "Pagar una opción desde el FEES, mantener strike y cantidad, valorar su plazo residual y renovar al vencer.",
        "riqueza_y_caida": "Acumular retornos e incluir el capital inicial al medir pérdidas.",
        "metricas": "Retorno compuesto y riesgo como contexto. El optimizador no maximiza CAGR.",
        "generar_pesos": "Enumerar pesos en pasos de 5%, sin cortos ni deuda. Los límites son supuestos del experimento.",
        "simular_mezclas": "Calcular carteras candidatas con rebalanceo anual y costos, sin suponer pesos constantes cada mes.",
        "elegir_pesos": "Usar solo trimestres anteriores y PIB con 90 días de rezago. Maximizar el peor retorno en contracciones.",
        "optimizar_progresivo": "Elegir antes de cada año. La curva usa esos pesos históricos; los pesos finales no se aplican al pasado.",
        "leer_config": "Leer los supuestos guardados en config.json.",
        "cargar_datos": "Unir FEES oficial, dólar diario BCCh, inflación, PIB y precios. No rellenar faltantes silenciosamente.",
        "evaluar_ciclo": "Acumular retornos a trimestres completos y comparar contracciones del PIB.",
        "bootstrap_ciclo": "Intervalo descriptivo por bloques de cuatro trimestres, manteniendo fechas emparejadas.",
        "ejecutar": "Construir H1–H4, estimar H5, evaluar protección, guardar auditorías y sensibilidades.",
        "graficos": "Separar rentabilidad sin flujos, saldo efectivo con flujos y rebalanceos simulados.",
        "escribir_informe": "Generar el informe desde resultados, con límites de datos, valoración y política."
    }
    for archivo in ("carteras.py", "optimizacion.py", "analisis.py"):
        nb.cells.append(nbf.v4.new_markdown_cell(f"## Código visible de {archivo}"))
        fuente = (RAIZ / archivo).read_text().split('if __name__ == "__main__":')[0].rstrip()
        fuente = fuente.replace('from datos import RAIZ, leer_config', 'RAIZ = Path.cwd()\n\ndef leer_config():\n    return json.loads((RAIZ / "config.json").read_text())')
        fuente = "\n".join(l for l in fuente.splitlines() if not l.startswith('from carteras import ') and not l.startswith('from optimizacion import '))
        partes = fuente.split("\ndef ")
        nb.cells.append(nbf.v4.new_code_cell(partes[0]))
        for parte in partes[1:]:
            nombre = parte.split("(",1)[0]
            nb.cells.append(nbf.v4.new_markdown_cell(f"### {nombre}\n\n{explicaciones[nombre]}"))
            nb.cells.append(nbf.v4.new_code_cell("def " + parte.strip()))
    nb.cells.extend([
        nbf.v4.new_markdown_cell("## Ejecutar y evaluar\n\nSe muestra protección durante contracciones y después los gráficos; el retorno total es secundario."),
        nbf.v4.new_code_cell("ciclo = ejecutar()\ndisplay(ciclo.round(3))"),
        nbf.v4.new_code_cell("display(pd.read_csv(RAIZ / 'results/pesos_optimos_finales.csv', index_col=0))\ndisplay(pd.read_csv(RAIZ / 'results/exposicion_optima.csv', index_col=0))"),
        nbf.v4.new_code_cell("from IPython.display import Image, Markdown, display\nfor nombre in ['fees_historico','rebalanceos','pib_y_carteras','contracciones','pesos_h5','puts_largas','riqueza_real','saldo_efectivo']:\n    display(Image(filename=str(RAIZ / f'results/figuras/{nombre}.png')))\ndisplay(Markdown((RAIZ / 'results/informe.md').read_text()))"),
        nbf.v4.new_markdown_cell("## Verificar\n\nComprobar datos oficiales, prima financiada, vencimiento, pesos, conversión CLP y decisiones sin trimestres futuros."),
        nbf.v4.new_code_cell("import subprocess\nimport sys\nsubprocess.run([sys.executable, 'verificar.py'], check=True)"),
        nbf.v4.new_markdown_cell("## Interpretación y uso de IA\n\nNo llamar anticíclica a una cartera que sigue perdiendo en contracciones. Leer docs/guia-codigo.md, docs/metodologia.md y docs/registro-ia.md. Las firmas y la revisión académica del equipo no están supuestas. El alcance acordado es solo FEES.")
    ])
    for i,c in enumerate(nb.cells):
        c["id"] = f"fees-{i:02d}"
    nbf.write(nb,RAIZ / "notebooks/fees.ipynb")
    print(RAIZ / "notebooks/fees.ipynb")


if __name__ == "__main__":
    crear()
