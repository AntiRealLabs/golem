#!/usr/bin/env python3
"""Puerta de publicación: comprueba que la carpeta que se va a publicar solo
contiene la portada y nada del piloto ni del prototipo del Lab.

Uso:  python3 -I herramientas/comprobar_publicacion.py [CARPETA]   (por defecto: site)
Sale con código 1 si encuentra algo que no debe publicarse.

El despliegue la ejecuta antes de subir nada. Cuando coordinación apruebe
publicar el Lab, esta regla se cambia a propósito, en el mismo commit que
añade el Lab, y se deja escrito en DEPLOY.md (ver CLAUDE.md, «Antes de
publicar el Lab»).
"""
import re
import sys
from pathlib import Path

ALLOWED_SUFFIXES = {".html", ".css", ".js", ".woff2", ".png", ".jpg", ".webp", ".svg", ".ico", ".txt", ".xml"}
ALLOWED_NAMES = {"_headers", "_redirects"}
MAX_BYTES = 2_000_000

# Nombres de archivo del piloto y del prototipo del Lab
FORBIDDEN_NAMES = re.compile(
    r"(ia01|dictamen|lote[-_]diseno|estado_operativo|operativo\.js|autocritica|propuestas-diseno|"
    r"DEMOSTRACION|REGISTRO_EMPAQUETADO|lab-textos|adaptador\.js|compartir\.js|manifiesto\.json|trabajos\.json)",
    re.I,
)
# Huellas de datos del piloto dentro de los archivos de texto
FORBIDDEN_TEXT = [
    (re.compile(r"/Users/"), "ruta local de un equipo"),
    (re.compile(r"\bLOT-[0-9a-f]{8,}"), "identificador de lote"),
    (re.compile(r"\bdoc-[0-9a-f]{16}\b"), "identificador de documento del lote"),
    (re.compile(r"\bJ[123]_P-[0-9A-F]{8}"), "identificador de selección del piloto"),
    (re.compile(r"\b[A-Z]{2}-\d{2}\b"), "identificador de corrida o de caso"),
    (re.compile(r"window\.GOLEM_"), "datos empaquetados del prototipo"),
]
TEXT_SUFFIXES = {".html", ".css", ".js", ".txt", ".xml", ".svg", ""}
# Primer corte ED01 (aprobación de Juan: 18 oct 2026, anotada en DEPLOY.md). Dos identificadores públicos que
# sí pueden aparecer: «IA-01» nombra la serie anterior en la nota que la separa de ED01, y «BF-03» está
# dentro del texto literal de una entrega (SmolLM3-3B, BF03), que no se toca.
PUBLICOS = {"IA-01", "BF-03"}


def check(folder: Path):
    problems = []
    if not folder.is_dir():
        return [f"no existe la carpeta {folder}"]
    files = [p for p in folder.rglob("*") if p.is_file()]
    if not (folder / "index.html").is_file():
        problems.append("falta index.html")
    if not (folder / "404.html").is_file():
        problems.append("falta 404.html (sin él, Pages trata el sitio como una aplicación de una sola página)")
    for p in files:
        rel = p.relative_to(folder).as_posix()
        if p.name.startswith("."):
            problems.append(f"{rel}: archivo oculto")
            continue
        if p.suffix.lower() not in ALLOWED_SUFFIXES and p.name not in ALLOWED_NAMES:
            problems.append(f"{rel}: tipo de archivo no previsto en la portada")
        if FORBIDDEN_NAMES.search(rel):
            problems.append(f"{rel}: nombre de un archivo del piloto o del prototipo del Lab")
        if p.stat().st_size > MAX_BYTES:
            problems.append(f"{rel}: pesa {p.stat().st_size} bytes (máximo {MAX_BYTES})")
        if p.suffix.lower() in TEXT_SUFFIXES or p.name in ALLOWED_NAMES:
            text = p.read_text(encoding="utf-8", errors="replace")
            for rx, what in FORBIDDEN_TEXT:
                m = next((x for x in rx.finditer(text) if x.group(0) not in PUBLICOS), None)
                if m:
                    problems.append(f"{rel}: contiene {what} («{m.group(0)}»)")
    return problems


def main():
    folder = Path(sys.argv[1] if len(sys.argv) > 1 else "site")
    problems = check(folder)
    if problems:
        print(f"NO SE PUBLICA: {len(problems)} problema(s) en {folder}/")
        for p in problems:
            print(f"  - {p}")
        sys.exit(1)
    n = sum(1 for p in folder.rglob("*") if p.is_file())
    print(f"Puerta de publicación: {folder}/ contiene solo la portada ({n} archivos).")


if __name__ == "__main__":
    main()
