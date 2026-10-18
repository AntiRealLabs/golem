#!/usr/bin/env python3
"""Genera el favicon y las imágenes para compartir de la portada.

Uso:  python3 -I herramientas/generar_imagenes.py [RAIZ_DEL_REPO]

Escribe en site/:
  favicon.svg, favicon.ico (16/32/48), apple-touch-icon.png (180)
  assets/og-es.png, assets/og-en.png (1200×630)

La G sale del contorno de UnifrakturMaguntia (licencia OFL; una imagen hecha
con la fuente no queda sujeta a la licencia). Las imágenes se dibujan con
Chromium (Playwright) usando las mismas fuentes que la página.
Requiere: fonttools, brotli, pillow, playwright.
"""
import io
import sys
from pathlib import Path

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]).resolve()
SITE = ROOT / "site"
FONTS = SITE / "assets" / "fonts"

COAL, ON_COAL, ON_COAL_2, TAN, LINE, RED = "#1c1d1a", "#ece6d8", "#bdb9a9", "#d1b698", "#45463e", "#803a39"


def glyph_g():
    font = TTFont(FONTS / "unifrakturmaguntia-latin-400-normal.woff2")
    gs = font.getGlyphSet()
    name = font.getBestCmap()[ord("G")]
    bp = BoundsPen(gs)
    gs[name].draw(bp)
    pen = SVGPathPen(gs)
    gs[name].draw(pen)
    return pen.getCommands(), bp.bounds


def favicon_svg():
    d, (x0, y0, x1, y1) = glyph_g()
    box, size = 46.0, 64.0          # la G ocupa 46 de 64 unidades
    s = box / max(x1 - x0, y1 - y0)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    tx, ty = size / 2 - s * cx, size / 2 + s * cy
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
        f'<rect width="64" height="64" rx="12" fill="{COAL}"/>'
        f'<path fill="{ON_COAL}" transform="translate({tx:.3f} {ty:.3f}) scale({s:.6f} {-s:.6f})" d="{d}"/>'
        "</svg>\n"
    )


def font_faces():
    faces = [
        ("UnifrakturMaguntia", 400, "unifrakturmaguntia-latin-400-normal.woff2"),
        ("Chakra Petch", 500, "chakra-petch-latin-500-normal.woff2"),
        ("Archivo", 400, "archivo-latin-400-normal.woff2"),
        ("Fragment Mono", 400, "fragment-mono-latin-400-normal.woff2"),
        ("DM Sans", 400, "dm-sans-latin-400-normal.woff2"),
    ]
    return "".join(
        f"@font-face{{font-family:'{fam}';font-weight:{w};src:url('{(FONTS / f).as_uri()}') format('woff2')}}"
        for fam, w, f in faces
    )


OG = {
    "es": ("Benchmark de creación filosófica en IA", "Preguntas desde el futuro", "Primera edición en preparación"),
    "en": ("Benchmark for philosophical creation in AI", "Questions from the future", "First edition in preparation"),
}


def og_html(lang):
    eyebrow, lema, status = OG[lang]
    return f"""<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><style>
{font_faces()}
*{{box-sizing:border-box;margin:0}}
html,body{{width:1200px;height:630px;overflow:hidden}}
body{{position:relative;background:{COAL};color:{ON_COAL};font-family:'Archivo',sans-serif}}
.arc{{position:absolute;right:-230px;top:-290px;width:620px;height:620px;border:1.5px solid {LINE};border-radius:50%;
  box-shadow:0 0 0 52px rgba(255,255,255,.014),0 0 0 104px rgba(255,255,255,.011)}}
.in{{position:absolute;inset:0;padding:70px 80px 64px;display:flex;flex-direction:column}}
.eyebrow{{font:400 22px/1.3 'Fragment Mono';letter-spacing:.14em;text-transform:uppercase;color:{TAN}}}
.mark{{display:flex;align-items:baseline;gap:26px;margin-top:26px}}
.g{{font:400 196px/.9 'UnifrakturMaguntia';letter-spacing:-.035em}}
.b{{font:400 34px/1 'DM Sans';letter-spacing:.34em;color:{ON_COAL_2}}}
.lema{{font:500 50px/1.2 'Chakra Petch';color:{TAN};margin-top:30px}}
.foot{{margin-top:auto;display:flex;justify-content:space-between;align-items:flex-end;padding-top:22px;border-top:1.5px solid {LINE}}}
.st{{font:400 24px/1.3 'Archivo';color:{ON_COAL_2}}}
.url{{font:400 24px/1.3 'Fragment Mono';letter-spacing:.04em;color:{ON_COAL}}}
.bar{{position:absolute;left:0;right:0;bottom:0;height:10px;background:{RED}}}
</style></head><body><div class="arc"></div><div class="in">
<p class="eyebrow">{eyebrow}</p>
<p class="mark"><span class="g">Golem</span><span class="b">BENCH</span></p>
<p class="lema">{lema}</p>
<div class="foot"><span class="st">{status}</span><span class="url">golembench.org</span></div>
</div><div class="bar"></div></body></html>"""


def main():
    svg = favicon_svg()
    (SITE / "favicon.svg").write_text(svg, encoding="utf-8")
    tmp = ROOT / ".tmp-imagenes"
    tmp.mkdir(exist_ok=True)
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            # favicon en PNG grande, luego se reduce
            page = browser.new_page(viewport={"width": 512, "height": 512})
            page.set_content(
                "<html><body style='margin:0;background:transparent'>"
                + svg.replace("<svg ", "<svg width='512' height='512' ")
                + "</body></html>"
            )
            big = Image.open(io.BytesIO(page.screenshot(omit_background=True))).convert("RGBA")
            sizes = [(16, 16), (32, 32), (48, 48)]
            big.resize((48, 48), Image.LANCZOS).save(SITE / "favicon.ico", sizes=sizes)
            # iOS redondea el icono por su cuenta: aquí va a sangre, sin esquinas transparentes
            page.set_content(
                "<html><body style='margin:0'>"
                + svg.replace("<svg ", "<svg width='512' height='512' ").replace(' rx="12"', "")
                + "</body></html>"
            )
            full = Image.open(io.BytesIO(page.screenshot())).convert("RGB")
            full.resize((180, 180), Image.LANCZOS).save(SITE / "apple-touch-icon.png", optimize=True)
            page.close()
            for lang in OG:
                html = tmp / f"og-{lang}.html"
                html.write_text(og_html(lang), encoding="utf-8")
                page = browser.new_page(viewport={"width": 1200, "height": 630})
                page.goto(html.as_uri())
                page.evaluate("document.fonts.ready")
                page.wait_for_timeout(150)
                png = Image.open(io.BytesIO(page.screenshot())).convert("RGB")
                png.save(SITE / "assets" / f"og-{lang}.png", optimize=True)
                page.close()
            browser.close()
    finally:
        for f in tmp.glob("*"):
            f.unlink()
        tmp.rmdir()
    for f in ["favicon.svg", "favicon.ico", "apple-touch-icon.png", "assets/og-es.png", "assets/og-en.png"]:
        print(f"{f}: {(SITE / f).stat().st_size} bytes")


if __name__ == "__main__":
    main()
