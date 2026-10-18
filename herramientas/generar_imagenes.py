#!/usr/bin/env python3
"""Genera el favicon, la cabeza del centro y las imágenes para compartir de la portada.

Uso:  python3 -I herramientas/generar_imagenes.py [--solo-cabeza] [RAIZ_DEL_REPO]

Escribe en site/:
  favicon.svg, favicon.ico (16/32/48), apple-touch-icon.png (180)
  assets/cabeza-720.webp, assets/cabeza-480.webp (la figura del centro, 4:5)
  assets/og-es.jpg, assets/og-en.jpg (1200×630)

Las fuentes del arte (colección de redes v0.4, generada con IA y aprobada) viven
en herramientas/fuentes/ y no se publican: la página solo usa los recortes.
La G sale del contorno de UnifrakturMaguntia (licencia OFL; una imagen hecha
con la fuente no queda sujeta a la licencia). Las imágenes para compartir se
dibujan con Chromium (Playwright) usando las mismas fuentes que la página.
Requiere: fonttools, brotli, pillow, numpy, playwright.
"""
import io
import sys
from pathlib import Path

import numpy as np
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont
from PIL import Image
from playwright.sync_api import sync_playwright

ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
ROOT = Path(ARGS[0] if ARGS else Path(__file__).resolve().parents[1]).resolve()
SITE = ROOT / "site"
FONTS = SITE / "assets" / "fonts"
FUENTES = ROOT / "herramientas" / "fuentes"

COAL, ON_COAL, ON_COAL_2, TAN, LINE, RED, IVORY = "#1c1d1a", "#ece6d8", "#bdb9a9", "#d1b698", "#45463e", "#803a39", "#f4ede0"
TALLER = FUENTES / "taller-2172.webp"    # versión panorámica del taller (2172×724)
FIGURA = FUENTES / "arcilla-1122.webp"   # figura vertical original (1122×1402)


def cabeza():
    """Recorta la cabeza y el borde del pedestal (720×900, sin reescalar) y la funde
    con el carbón de la página, para que salga de la oscuridad encima del sello."""
    im = Image.open(FIGURA).convert("RGB")
    crop = im.crop((301, 150, 1021, 1050))                     # 720×900, la cabeza al centro
    w, h = crop.size
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    # elipse un poco más alta que ancha, centrada algo arriba (la cara), que se apaga hacia los bordes
    d = np.sqrt(((x - w / 2) / (w * .5)) ** 2 + ((y - h * .47) / (h * .53)) ** 2)
    a = np.clip((1.0 - d) / .34, 0, 1)
    a = a * a * (3 - 2 * a)                                     # suavizado (smoothstep)
    src = np.asarray(crop, dtype=np.float32)
    coal = np.array([0x1c, 0x1d, 0x1a], dtype=np.float32)
    out = src * a[..., None] + coal * (1 - a[..., None])
    img = Image.fromarray(np.clip(out + .5, 0, 255).astype(np.uint8))
    img.save(SITE / "assets" / "cabeza-720.webp", quality=84, method=6)
    img.resize((480, 600), Image.LANCZOS).save(SITE / "assets" / "cabeza-480.webp", quality=84, method=6)


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
        f'<rect width="64" height="64" rx="12" fill="{RED}"/>'
        f'<path fill="{IVORY}" transform="translate({tx:.3f} {ty:.3f}) scale({s:.6f} {-s:.6f})" d="{d}"/>'
        "</svg>\n"
    )


def font_faces():
    faces = [
        ("UnifrakturMaguntia", 400, "unifrakturmaguntia-latin-400-normal.woff2"),
        ("Chakra Petch", 500, "chakra-petch-latin-500-normal.woff2"),
        ("Archivo", 400, "archivo-latin-400-normal.woff2"),
        ("Fragment Mono", 400, "fragment-mono-latin-400-normal.woff2"),
        ("DM Sans", 400, "dm-sans-latin-400-normal.woff2"),
        ("Newsreader", 400, "newsreader-latin-400-normal.woff2"),
    ]
    return "".join(
        f"@font-face{{font-family:'{fam}';font-weight:{w};src:url('{(FONTS / f).as_uri()}') format('woff2')}}"
        for fam, w, f in faces
    )


OG = {
    "es": ("Benchmark de creación filosófica en IA", "¿Hasta dónde puede filosofar una máquina?", "Preguntas desde el futuro"),
    "en": ("Benchmark for philosophical creation in AI", "How far can a machine philosophize?", "Questions from the future"),
}


def og_html(lang):
    eyebrow, question, lema = OG[lang]
    return f"""<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><style>
{font_faces()}
*{{box-sizing:border-box;margin:0}}
html,body{{width:1200px;height:630px;overflow:hidden}}
body{{position:relative;background:{COAL} url('{TALLER.as_uri()}') 82% 40%/auto 100% no-repeat;color:{ON_COAL};font-family:'Archivo',sans-serif}}
body::before{{content:"";position:absolute;inset:0;background:linear-gradient(90deg,rgba(24,25,21,.96) 0%,rgba(24,25,21,.86) 38%,rgba(24,25,21,.2) 60%,rgba(24,25,21,0) 70%)}}
.in{{position:absolute;inset:0;padding:58px 72px 54px;display:flex;flex-direction:column;max-width:760px}}
.eyebrow{{font:400 19px/1.3 'Fragment Mono';letter-spacing:.14em;text-transform:uppercase;color:{TAN}}}
.mark{{display:flex;align-items:baseline;gap:20px;margin-top:20px}}
.g{{font:400 132px/.9 'UnifrakturMaguntia';letter-spacing:-.035em}}
.b{{font:400 26px/1 'DM Sans';letter-spacing:.34em;color:{ON_COAL_2}}}
.q{{font:500 50px/1.06 'Chakra Petch';letter-spacing:-.02em;margin-top:30px;max-width:17ch;text-wrap:balance}}
.lema{{font:500 26px/1.2 'Chakra Petch';color:{TAN};margin-top:16px}}
.url{{margin-top:auto;font:400 21px/1.3 'Fragment Mono';letter-spacing:.06em;color:{ON_COAL_2}}}
.bar{{position:absolute;left:0;right:0;bottom:0;height:8px;background:{RED}}}
</style></head><body><div class="in">
<p class="eyebrow">{eyebrow}</p>
<p class="mark"><span class="g">Golem</span><span class="b">BENCH</span></p>
<p class="q">{question}</p>
<p class="lema">{lema}</p>
<p class="url">golembench.org</p>
</div><div class="bar"></div></body></html>"""


def main():
    cabeza()
    if "--solo-cabeza" in sys.argv:
        for f in ["assets/cabeza-720.webp", "assets/cabeza-480.webp"]:
            print(f"{f}: {(SITE / f).stat().st_size} bytes")
        return
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
                png.save(SITE / "assets" / f"og-{lang}.jpg", quality=86, optimize=True, progressive=True)
                page.close()
            browser.close()
    finally:
        for f in tmp.glob("*"):
            f.unlink()
        tmp.rmdir()
    for f in ["favicon.svg", "favicon.ico", "apple-touch-icon.png", "assets/cabeza-720.webp", "assets/cabeza-480.webp",
              "assets/og-es.jpg", "assets/og-en.jpg"]:
        print(f"{f}: {(SITE / f).stat().st_size} bytes")


if __name__ == "__main__":
    main()
