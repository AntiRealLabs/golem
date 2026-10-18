#!/usr/bin/env python3
"""Huellas de versión para la hoja de estilos y los scripts de la portada.

Uso:  python3 -I herramientas/versionar_recursos.py              pone las huellas
      python3 -I herramientas/versionar_recursos.py --comprobar  solo revisa (sale con 1 si falta algo)

Por qué: la zona de Cloudflare les dice a los navegadores que guarden CSS, JS e
imágenes durante 4 horas (Browser Cache TTL: «cache-control: max-age=14400»),
aunque Pages mande max-age=0. El HTML, en cambio, llega fresco en cada visita.
Sin huella, quien ya había visitado recibe el HTML nuevo con el CSS viejo hasta
que vence su copia, y la cruz se desarma. Con «?v=<huella>» la dirección cambia
cuando cambia el archivo, y el navegador lo pide de nuevo.
"""
import hashlib
import re
import sys
from pathlib import Path

SITE = Path(__file__).resolve().parents[1] / "site"
RECURSOS = ("assets/portada.css", "assets/centro.js", "assets/archivo.js")


def huella(rel, site=SITE):
    return hashlib.sha256((site / rel).read_bytes()).hexdigest()[:10]


def _patron(rel):
    # "/assets/portada.css" o "/assets/portada.css?v=…", entre comillas
    return re.compile(r'(["\'])/' + re.escape(rel) + r'(?:\?v=[0-9a-z]*)?\1')


def _leer(p):
    with open(p, encoding="utf-8", newline="") as f:
        return f.read()


def revisar(site=SITE):
    """Lista las referencias a CSS o JS sin huella o con una huella vieja."""
    problemas = []
    for html in sorted(site.rglob("*.html")):
        texto = _leer(html)
        for rel in RECURSOS:
            esperado = f"/{rel}?v={huella(rel, site)}"
            for m in _patron(rel).finditer(texto):
                if m.group(0)[1:-1] != esperado:
                    problemas.append(f"{html.relative_to(site)}: {m.group(0)[1:-1]} (debería ser {esperado})")
    return problemas


def versionar(site=SITE):
    """Pone la huella actual en todas las páginas. Devuelve las que cambiaron."""
    cambiadas = []
    for html in sorted(site.rglob("*.html")):
        texto = _leer(html)
        nuevo = texto
        for rel in RECURSOS:
            ref = f"/{rel}?v={huella(rel, site)}"
            nuevo = _patron(rel).sub(lambda m, ref=ref: m.group(1) + ref + m.group(1), nuevo)
        if nuevo != texto:
            with open(html, "w", encoding="utf-8", newline="") as f:
                f.write(nuevo)
            cambiadas.append(str(html.relative_to(site)))
    return cambiadas


def main():
    if "--comprobar" in sys.argv:
        problemas = revisar()
        if problemas:
            print("Huellas de versión viejas o ausentes. Corre: python3 -I herramientas/versionar_recursos.py")
            for p in problemas:
                print("  - " + p)
            return 1
        print("Huellas de versión al día: " + ", ".join(f"{r}?v={huella(r)}" for r in RECURSOS))
        return 0
    cambiadas = versionar()
    print(("Huellas puestas en: " + ", ".join(cambiadas)) if cambiadas else "Las huellas ya estaban al día.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
