"""Empaqueta solo los archivos de trabajo, sin Git, entorno ni secretos."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

RAIZ = Path(__file__).resolve().parent
archivo = RAIZ / "entrega_fees.zip"
archivos = [p for p in RAIZ.iterdir() if p.suffix in {".py", ".md", ".json", ".txt"} and p.is_file()]
for carpeta in ("data", "docs", "results", "notebooks"):
    archivos.extend(p for p in (RAIZ / carpeta).rglob("*") if p.is_file() and ".ipynb_checkpoints" not in p.parts and "pdf_cache" not in p.parts)
with ZipFile(archivo, "w", ZIP_DEFLATED) as z:
    for p in sorted(archivos):
        z.write(p, str(p.relative_to(RAIZ)))
print(f"{archivo}: {len(archivos)} archivos, {archivo.stat().st_size:,} bytes")
