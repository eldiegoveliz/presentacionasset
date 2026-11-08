"""Ejecuta la entrega desde cero en un kernel nuevo y compara sus salidas."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from zipfile import ZipFile

import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager
from jupyter_client.kernelspec import KernelSpecManager

RAIZ = Path(__file__).resolve().parent

for script in ("crear_notebook.py", "preparar_entrega.py"):
    subprocess.run([sys.executable, str(RAIZ / script)], check=True)

with tempfile.TemporaryDirectory(prefix="fees-notebook-") as tmp:
    temporal = Path(tmp)
    proyecto = temporal / "proyecto"
    with ZipFile(RAIZ / "entrega_fees.zip") as z:
        z.extractall(proyecto)
    shutil.rmtree(proyecto / "results")
    # El kernel usa el Python actual y desaparece al terminar la verificación.
    kernel = temporal / "kernels" / "fees-validacion"
    kernel.mkdir(parents=True)
    (kernel / "kernel.json").write_text(json.dumps({
        "argv": [sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}"],
        "display_name": "FEES validacion", "language": "python"}))
    gestor = KernelManager(kernel_name="fees-validacion", kernel_spec_manager=KernelSpecManager(
        kernel_dirs=[str(kernel.parent)]))
    nb = nbformat.read(proyecto / "notebooks/fees.ipynb", as_version=4)
    os.environ["PIP_NO_INDEX"] = "1"
    try:
        NotebookClient(nb, km=gestor, timeout=180, resources={"metadata": {"path": str(proyecto)}}).execute()
    finally:
        if gestor.has_kernel:
            gestor.shutdown_kernel(now=True)
    salidas = ["metricas.csv", "retornos_carteras_mensuales.csv", "metricas_clp.csv", "correlaciones.csv",
               "incertidumbre.csv", "informe.md", "puts_auditoria.csv", "sensibilidad_puts.csv", "sensibilidad_mbs.csv"]
    for archivo in salidas:
        if (proyecto / "results" / archivo).read_bytes() != (RAIZ / "results" / archivo).read_bytes():
            raise AssertionError(f"El notebook y el script difieren: {archivo}")
    nbformat.write(nb, RAIZ / "notebooks/fees.ipynb")
    print("Notebook completo en kernel limpio; nueve salidas idénticas byte por byte.")

subprocess.run([sys.executable, str(RAIZ / "preparar_entrega.py")], check=True)
