#!/usr/bin/env python3
"""Verificación automática de la portada antes de publicarla.

Uso:  python3 -I herramientas/verificar_portada.py [--sin-capturas]

Levanta herramientas/servidor_local.py (imita Cloudflare Pages con _headers),
abre las páginas en Chromium (Playwright) y comprueba: puerta de publicación,
estados HTTP y cabeceras, contenido de la fase 1, paridad ES/EN, enlaces,
fuentes, CSP sin violaciones, anchos sin desborde, espaciado de texto,
teclado, objetivos táctiles, axe-core (WCAG 2.2 A/AA), peso e imágenes.
Escribe verificacion/portada/informe.md e informe.json; las capturas van a
verificacion/portada/capturas/ (no se suben al repo).

Es una inspección automática: no sustituye pruebas con personas ni revisar
el sitio publicado en Cloudflare.
"""
import io
import json
import re
import shutil
import sys
import tempfile
import threading
import urllib.error
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path
from xml.etree import ElementTree

from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
OUT = ROOT / "verificacion" / "portada"
SHOTS = OUT / "capturas"
sys.path.insert(0, str(ROOT / "herramientas"))
import comprobar_publicacion  # noqa: E402
import servidor_local  # noqa: E402
import versionar_recursos  # noqa: E402

AXE = (ROOT / "herramientas" / "vendor" / "axe.min.js").read_text(encoding="utf-8")
PAGES = {"es": "/", "en": "/en/", "404": "/esta-ruta-no-existe"}
WIDTHS = [1440, 1024, 768, 390, 320]
FAMILIES = ["UnifrakturMaguntia", "Chakra Petch", "Archivo", "Fragment Mono", "DM Sans", "Newsreader"]
EXTERNAL_OK = {"https://antireallabs.com", "mailto:admin@antireallabs.com"}
# Fase 1: nada del piloto en la portada (ni nombres de modelos, ni corridas o casos, ni cifras)
PHASE1_FORBIDDEN = re.compile(r"\b(Claude|GPT|Gemini|Llama|Mistral|Grok|DeepSeek)\b|\b[A-Z]{2}-\d{2}\b", re.I)
DIGITS_OK = {"1", "2", "3", "01", "02", "03", "04", "2026", "404"}
SPANISH_HINTS = re.compile(r"ñ|ción\b|\b(el|los|las|del|una|que|para|con)\b", re.I)
ENGLISH_HINTS = re.compile(r"\b(the|and|of|with|what|which|is)\b", re.I)

results = []


def check(name, ok, detail=""):
    results.append({"comprobacion": name, "ok": bool(ok), "detalle": detail})
    print(("OK   " if ok else "FALLA") + f" {name}" + (f" — {detail}" if detail and not ok else ""))


def http(base, path, method="GET"):
    req = urllib.request.Request(base + path, method=method)

    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *a, **k):
            return None

    opener = urllib.request.build_opener(NoRedirect)
    try:
        r = opener.open(req)
        return r.status, dict(r.headers), r.read()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read()


def visible_text(page, exclude_lang=None):
    return page.evaluate(
        """(ex) => {
          const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
          const out = [];
          while (w.nextNode()) {
            const n = w.currentNode, el = n.parentElement;
            if (!el || el.closest('script,style')) continue;
            if (ex && el.closest('[lang]') && el.closest('[lang]').getAttribute('lang') === ex
                && el.closest('[lang]') !== document.documentElement) continue;
            const cs = getComputedStyle(el);
            if (cs.display === 'none' || cs.visibility === 'hidden') continue;
            if (n.textContent.trim()) out.push(n.textContent.trim());
          }
          return out.join(' ');
        }""",
        exclude_lang,
    )


def main():
    shots = "--sin-capturas" not in sys.argv
    OUT.mkdir(parents=True, exist_ok=True)
    if shots:
        if SHOTS.exists():
            shutil.rmtree(SHOTS)
        SHOTS.mkdir(parents=True)

    # ---------- puerta de publicación ----------
    probs = comprobar_publicacion.check(SITE)
    check("Puerta de publicación: site/ contiene solo la portada", not probs, "; ".join(probs))
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp) / "site"
        shutil.copytree(SITE, t)
        (t / "data").mkdir()
        (t / "data" / "ia01-piloto.json").write_text("{}", encoding="utf-8")
        (t / "fuga.html").write_text("<p>/Users/alguien/doc-0123456789abcdef</p>", encoding="utf-8")
        bad = comprobar_publicacion.check(t)
        check("Puerta de publicación: rechaza datos del piloto colados (prueba con archivos falsos)", len(bad) >= 3, f"{len(bad)} problemas")

    # ---------- servidor tipo Pages ----------
    srv = servidor_local.serve(0)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{srv.server_address[1]}"

    s, h, b = http(base, "/")
    check("HTTP: / responde 200 con HTML", s == 200 and h.get("Content-Type", "").startswith("text/html"))
    s, h, b = http(base, "/en/")
    check("HTTP: /en/ responde 200", s == 200)
    s, h, _ = http(base, "/en")
    check("HTTP: /en redirige a /en/", s == 308 and h.get("Location") == "/en/", f"{s} {h.get('Location')}")
    s, h, b = http(base, "/lab.html")
    check("HTTP: una ruta inexistente (p. ej. /lab.html) da 404 con la página propia", s == 404 and "Esta página no existe" in b.decode())
    s, h, _ = http(base, "/_headers")
    check("HTTP: _headers no se sirve como archivo", s == 404)
    s, h, _ = http(base, "/")
    need = ["Content-Security-Policy", "X-Content-Type-Options", "Referrer-Policy", "Strict-Transport-Security", "X-Frame-Options", "Permissions-Policy"]
    missing = [k for k in need if k not in h]
    check("Cabeceras de seguridad presentes en /", not missing, f"faltan {missing}")
    s, h, _ = http(base, "/assets/fonts/archivo-latin-400-normal.woff2")
    check("Caché de fuentes sin valores unidos por reglas repetidas", h.get("Cache-Control") == "public, max-age=31536000, immutable", h.get("Cache-Control", ""))
    s, h, _ = http(base, "/assets/portada.css")
    check("La hoja de estilos no lleva caché larga (cambia con cada versión)", "immutable" not in h.get("Cache-Control", ""))
    # Cloudflare guarda CSS y JS 4 horas en el navegador: sin huella, quien ya visitó
    # vería el HTML nuevo con estilos viejos (ver herramientas/versionar_recursos.py)
    viejas = versionar_recursos.revisar(SITE)
    sirven = [http(base, f"/{r}?v={versionar_recursos.huella(r)}")[0] for r in versionar_recursos.RECURSOS]
    check("CSS y JS llevan la huella de su versión (?v=) en todas las páginas y se sirven con ella",
          not viejas and sirven == [200, 200], "; ".join(viejas) or f"estados {sirven}")
    s, h, b = http(base, "/robots.txt")
    check("robots.txt enlaza el sitemap", s == 200 and b"Sitemap: https://golembench.org/sitemap.xml" in b)
    s, h, b = http(base, "/sitemap.xml")
    try:
        ElementTree.fromstring(b)
        okxml = True
    except ElementTree.ParseError:
        okxml = False
    check("sitemap.xml es XML válido con las dos páginas", s == 200 and okxml and b.count(b"<loc>") == 2)

    # ---------- imágenes ----------
    ico = Image.open(SITE / "favicon.ico")
    check("favicon.ico trae 16, 32 y 48 px", {(16, 16), (32, 32), (48, 48)} <= set(ico.info.get("sizes", [])))
    check("apple-touch-icon.png mide 180×180", Image.open(SITE / "apple-touch-icon.png").size == (180, 180))
    for lang in ("es", "en"):
        check(f"og-{lang}.jpg mide 1200×630", Image.open(SITE / "assets" / f"og-{lang}.jpg").size == (1200, 630))
    # la figura de la portada tiene que ser el arte original, no una captura reescalada
    sizes = {f: Image.open(SITE / "assets" / f).size for f in ("taller-2172.webp", "taller-1280.webp", "arcilla-1122.webp", "arcilla-720.webp")}
    check("Figura de la portada: arte original a tamaño completo (taller 2172 px, arcilla 1122×1402)",
          sizes["taller-2172.webp"] == (2172, 724) and sizes["arcilla-1122.webp"] == (1122, 1402), str(sizes))
    try:
        ElementTree.fromstring((SITE / "favicon.svg").read_text(encoding="utf-8"))
        check("favicon.svg es SVG válido", True)
    except ElementTree.ParseError as e:
        check("favicon.svg es SVG válido", False, str(e))

    with sync_playwright() as p:
        browser = p.chromium.launch()

        # ---------- contenido, CSP y consola (contexto normal, con la CSP real) ----------
        ctx = browser.new_context(viewport={"width": 1440, "height": 900})
        ctx.add_init_script("window.__csp=[];document.addEventListener('securitypolicyviolation',e=>window.__csp.push(e.violatedDirective+' '+e.blockedURI));")
        structure = {}
        for key, path in PAGES.items():
            page = ctx.new_page()
            errors, sizes, origins = [], [], set()
            page.on("console", lambda m, errors=errors: errors.append(m.text) if m.type == "error" and "404" not in m.text else None)
            page.on("pageerror", lambda e, errors=errors: errors.append(str(e)))
            page.on("response", lambda r, sizes=sizes, origins=origins: (sizes.append(len(r.body() or b"")), origins.add(r.url.split("/")[2])))
            page.goto(base + path, wait_until="networkidle")
            page.evaluate("document.fonts.ready")
            csp = page.evaluate("window.__csp")
            check(f"[{key}] sin errores de consola ni violaciones de la CSP", not errors and not csp, f"{errors} {csp}")
            loaded = page.evaluate("[...document.fonts].filter(f=>f.status==='loaded').map(f=>f.family.replace(/\"/g,''))")
            used = [f for f in FAMILIES if f in loaded]
            if key == "404":
                check(f"[{key}] fuentes de la marca cargadas", "UnifrakturMaguntia" in loaded and "Chakra Petch" in loaded, str(loaded))
            else:
                check(f"[{key}] las cinco familias de la base cargan desde el propio sitio", len(used) == len(FAMILIES), f"cargadas: {loaded}")
            check(f"[{key}] todo se sirve desde el mismo origen", origins == {base.split('/')[2]}, str(origins))
            total = sum(sizes)
            check(f"[{key}] peso total de la página ≤ 700 KB", total <= 700_000, f"{total} bytes")
            if key in ("es", "en"):
                info = page.evaluate(
                    """() => ({
                      lang: document.documentElement.lang,
                      h1: document.querySelectorAll('h1').length,
                      title: document.title,
                      desc: (document.querySelector('meta[name=description]')||{}).content||'',
                      canonical: (document.querySelector('link[rel=canonical]')||{}).href||'',
                      alts: [...document.querySelectorAll('link[rel=alternate][hreflang]')].map(l=>l.hreflang+'='+l.href),
                      og: (document.querySelector('meta[property="og:image"]')||{}).content||'',
                      counts: ['h2','h3','li','p','a'].map(s=>document.querySelectorAll('main '+s+', header '+s+', footer '+s).length),
                      links: [...document.querySelectorAll('a[href]')].map(a=>a.getAttribute('href')),
                      current: [...document.querySelectorAll('.langs a[aria-current=page]')].map(a=>a.textContent.trim())
                    })"""
                )
                structure[key] = info["counts"]
                check(f"[{key}] idioma del documento declarado", info["lang"] == key)
                check(f"[{key}] un solo h1", info["h1"] == 1)
                check(f"[{key}] descripción presente y ≤ 170 caracteres", 0 < len(info["desc"]) <= 170, f"{len(info['desc'])}")
                want = "https://golembench.org/" + ("" if key == "es" else "en/")
                check(f"[{key}] canónica correcta", info["canonical"] == want, info["canonical"])
                check(f"[{key}] alternativas hreflang es/en/x-default", sorted(a.split("=")[0] for a in info["alts"]) == ["en", "es", "x-default"], str(info["alts"]))
                check(f"[{key}] imagen para compartir absoluta y existente", info["og"] == f"https://golembench.org/assets/og-{key}.jpg" and (SITE / "assets" / f"og-{key}.jpg").exists())
                alts = page.evaluate("[...document.querySelectorAll('img')].map(i=>[i.alt.length, i.complete && i.naturalWidth>0])")
                check(f"[{key}] imágenes cargadas y con texto alternativo descriptivo", alts and all(a > 40 and ok for a, ok in alts), str(alts))
                check(f"[{key}] el selector marca el idioma actual", info["current"] == [key.upper()], str(info["current"]))
                bad_links = []
                for href in info["links"]:
                    if href.startswith("#"):
                        if not page.query_selector(href):
                            bad_links.append(href)
                    elif href.startswith("/"):
                        st, hh, _ = http(base, href)
                        if st == 308:
                            st, _, _ = http(base, hh.get("Location", ""))
                        if st != 200:
                            bad_links.append(f"{href} → {st}")
                    elif href.split("?")[0] not in EXTERNAL_OK:
                        bad_links.append(href)
                check(f"[{key}] enlaces internos válidos y solo los externos previstos", not bad_links, str(bad_links))
                text = visible_text(page)
                m = PHASE1_FORBIDDEN.search(text)
                check(f"[{key}] fase 1: sin nombres de modelos ni corridas en el texto", not m, m.group(0) if m else "")
                nums = set(re.findall(r"\d+", text)) - DIGITS_OK
                check(f"[{key}] fase 1: ninguna cifra del piloto (solo J1–J3, 01–04 y el año)", not nums, str(sorted(nums)))
                other = visible_text(page, exclude_lang="es" if key == "en" else "en")
                hint = (SPANISH_HINTS if key == "en" else ENGLISH_HINTS).findall(other)
                check(f"[{key}] sin restos del otro idioma fuera de lo marcado con lang", not hint, str(sorted(set(hint)))[:200])
            page.close()
        check("Paridad ES/EN: mismos h2, h3, elementos de lista, párrafos y enlaces", structure.get("es") == structure.get("en"), str(structure))
        ctx.close()

        # ---------- anchos ----------
        overflow = []
        for w in WIDTHS:
            ctx = browser.new_context(viewport={"width": w, "height": 900})
            page = ctx.new_page()
            for key, path in PAGES.items():
                page.goto(base + path, wait_until="networkidle")
                page.evaluate("document.fonts.ready")
                sw = page.evaluate("document.documentElement.scrollWidth")
                if sw > w:
                    overflow.append(f"{key}@{w}: {sw}")
            ctx.close()
        check("Sin desplazamiento horizontal a 1440, 1024, 768, 390 y 320 px", not overflow, str(overflow))

        # ---------- objetivos táctiles, teclado ----------
        ctx = browser.new_context(viewport={"width": 390, "height": 844}, has_touch=True, is_mobile=True)
        page = ctx.new_page()
        small = []
        for key, path in PAGES.items():
            page.goto(base + path, wait_until="networkidle")
            for a in page.query_selector_all("a[href]"):
                bb = a.bounding_box()
                if bb and (bb["width"] < 24 or bb["height"] < 24) and a.evaluate("e=>getComputedStyle(e).position!=='absolute'||e.matches(':focus')"):
                    small.append(f"{key}: {a.inner_text()[:30]} {bb['width']:.0f}×{bb['height']:.0f}")
        check("Objetivos táctiles ≥ 24 px en móvil (WCAG 2.5.8)", not small, str(small))
        ctx.close()

        ctx = browser.new_context(viewport={"width": 1280, "height": 800})
        page = ctx.new_page()
        page.goto(base + "/", wait_until="networkidle")
        page.keyboard.press("Tab")
        first = page.evaluate("document.activeElement.className")
        vis = page.evaluate("(()=>{const r=document.activeElement.getBoundingClientRect();return r.top>=0&&r.bottom<=innerHeight})()")
        want = page.evaluate("document.querySelector('.skip').getAttribute('href').slice(1)")
        page.keyboard.press("Enter")
        target = page.evaluate("document.activeElement.id")
        check("Teclado: el primer Tab va al salto, visible, y lleva a la pregunta", first == "skip" and vis and target == want, f"{first} {vis} {target}")
        order = []
        page.goto(base + "/", wait_until="networkidle")
        for _ in range(6):
            page.keyboard.press("Tab")
            order.append(page.evaluate("(document.activeElement.className||document.activeElement.textContent.trim().slice(0,12))+' '+document.activeElement.getAttribute('href')"))
        check("Teclado: orden salto → marca → ES → EN → pistas del centro", order[:4] == ["skip #" + want, "brand /", "ES /", "EN /en/"] and order[4].startswith("pista"), str(order))
        outline = page.evaluate("(()=>{document.querySelector('.langs a').focus();const s=getComputedStyle(document.activeElement);return s.outlineStyle+' '+s.outlineWidth})()")
        check("Teclado: el foco se ve (contorno de 3 px)", outline.startswith("solid 3px"), outline)
        ctx.close()

        # ---------- la cruz: se llega al centro y se va hacia todos los lados ----------
        for label, vw, vh in (("escritorio", 1440, 900), ("móvil", 390, 844)):
            ctx = browser.new_context(viewport={"width": vw, "height": vh}, reduced_motion="reduce")
            page = ctx.new_page()
            for key, path in (("es", "/"), ("en", "/en/")):
                page.goto(base + path, wait_until="networkidle")
                page.evaluate("document.fonts.ready")
                page.wait_for_timeout(250)
                pos = page.evaluate("""() => { const t=document.querySelector('.top').offsetHeight, c=document.getElementById('centro'),
                    f=document.getElementById('fila'), p=document.getElementById('pregunta');
                    return {dy: Math.round(scrollY - (c.getBoundingClientRect().top + scrollY - t)), dx: Math.round(f.scrollLeft - p.offsetLeft),
                            cur: (document.querySelector('.brujula [aria-current]')||{}).dataset?.sala || null}; }""")
                check(f"Cruz [{key} · {label}]: se llega al centro (pregunta a la vista, brújula en el centro)",
                      abs(pos["dy"]) <= 3 and abs(pos["dx"]) <= 3 and pos["cur"] == "pregunta", str(pos))
                order_ok = page.evaluate("""() => { const pie=document.querySelector('.escalera-pie').getBoundingClientRect().top,
                    a=document.querySelector('.peldano').getBoundingClientRect().top,
                    z=document.querySelector('.peldano--ultimo').getBoundingClientRect().top,
                    cima=document.querySelector('.escalera-cima').getBoundingClientRect().top,
                    centro=document.getElementById('centro').getBoundingClientRect().top;
                    return pie > a && a > z && z > cima && pie < centro; }""")
                check(f"Cruz [{key} · {label}]: arriba se lee de abajo hacia arriba (la primera pregunta queda junto al centro)", order_ok)
                page.keyboard.press("ArrowRight")
                page.wait_for_timeout(900)
                right = page.evaluate("(document.querySelector('.brujula [aria-current]')||{}).dataset?.sala || null")
                page.keyboard.press("ArrowLeft"); page.wait_for_timeout(900)
                page.keyboard.press("ArrowLeft"); page.wait_for_timeout(900)
                left = page.evaluate("(document.querySelector('.brujula [aria-current]')||{}).dataset?.sala || null")
                check(f"Cruz [{key} · {label}]: ← y → recorren la fila (lo que guardamos / lo que medimos)", right == "guardamos" and left == "medimos", f"{right} {left}")
                page.goto(base + path, wait_until="networkidle")
                page.wait_for_timeout(200)
                page.click(".pista--o")
                page.wait_for_timeout(500)
                vis = page.evaluate("""() => { const e=document.querySelector('#medimos .eyebrow').getBoundingClientRect(),
                    t=document.querySelector('.top').getBoundingClientRect().bottom;
                    return e.top >= t - 1 && e.left >= 0 && e.right <= innerWidth && location.hash === '#medimos'; }""")
                check(f"Cruz [{key} · {label}]: la pista ← lleva a lo que medimos y se ve desde su primera línea", vis)
                page.goto(base + path + "#abajo", wait_until="networkidle")
                page.wait_for_timeout(400)
                down = page.evaluate("(document.querySelector('.brujula [aria-current]')||{}).dataset?.sala || null")
                page.goto(base + path + "#arriba", wait_until="networkidle")
                page.wait_for_timeout(400)
                up = page.evaluate("(document.querySelector('.brujula [aria-current]')||{}).dataset?.sala || null")
                check(f"Cruz [{key} · {label}]: los enlaces llevan a cada sala y la brújula lo marca", down == "abajo" and up == "arriba", f"{down} {up}")
            ctx.close()
        ctx = browser.new_context(viewport={"width": 1280, "height": 800}, java_script_enabled=False)
        page = ctx.new_page()
        page.goto(base + "/", wait_until="networkidle")
        nojs = page.evaluate("[document.querySelectorAll('h1').length, ['arriba','centro','abajo','medimos','guardamos'].every(id => !!document.getElementById(id))]")
        check("Cruz sin JavaScript: todo el contenido sigue ahí, con sus enlaces", nojs == [1, True], str(nojs))
        ctx.close()

        # ---------- axe y espaciado de texto (sin CSP, para poder inyectar) ----------
        axe_fail, axe_bp = [], []
        for w in (1440, 390):
            ctx = browser.new_context(viewport={"width": w, "height": 900}, bypass_csp=True)
            page = ctx.new_page()
            for key, path in PAGES.items():
                page.goto(base + path, wait_until="networkidle")
                page.evaluate(AXE)
                r = page.evaluate("axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']}})")
                for v in r["violations"]:
                    axe_fail.append(f"{key}@{w}: {v['id']} ({len(v['nodes'])})")
                r = page.evaluate("axe.run(document,{runOnly:{type:'tag',values:['best-practice']}})")
                for v in r["violations"]:
                    axe_bp.append(f"{key}@{w}: {v['id']}")
            ctx.close()
        check("axe-core 4.14 · WCAG 2.0/2.1/2.2 A y AA: sin violaciones (3 páginas × 2 anchos)", not axe_fail, str(axe_fail))
        check("axe-core · buenas prácticas: sin avisos", not axe_bp, str(sorted(set(axe_bp))))

        spacing = []
        for w in (1280, 390):
            ctx = browser.new_context(viewport={"width": w, "height": 900}, bypass_csp=True)
            page = ctx.new_page()
            for key, path in PAGES.items():
                page.goto(base + path, wait_until="networkidle")
                page.add_style_tag(content="*{line-height:1.5!important;letter-spacing:.12em!important;word-spacing:.16em!important}p{margin-bottom:2em!important}")
                page.evaluate("document.fonts.ready")
                sw = page.evaluate("document.documentElement.scrollWidth")
                clipped = page.evaluate("""[...document.querySelectorAll('h1,h2,h3,p,a,li')].filter(e=>e.scrollWidth>e.clientWidth+1 && getComputedStyle(e).overflow!=='visible').length""")
                if sw > w or clipped:
                    spacing.append(f"{key}@{w}: ancho {sw}, recortes {clipped}")
            ctx.close()
        check("Espaciado de texto ampliado (WCAG 1.4.12): no se pierde texto", not spacing, str(spacing))

        # ---------- capturas ----------
        if shots:
            for label, vw, vh, mobile in (("escritorio", 1440, 900, False), ("movil", 390, 844, True)):
                ctx = browser.new_context(viewport={"width": vw, "height": vh}, device_scale_factor=1 if not mobile else 2, is_mobile=mobile, has_touch=mobile, reduced_motion="reduce")
                page = ctx.new_page()
                for key, path in PAGES.items():
                    page.goto(base + path, wait_until="networkidle")
                    page.evaluate("document.fonts.ready")
                    page.wait_for_timeout(250)
                    page.screenshot(path=str(SHOTS / f"{label}_{key}.png"))
                    if key != "404":
                        page.screenshot(path=str(SHOTS / f"{label}_{key}_completa.png"), full_page=True)
                        # las otras salas, para revisar a ojo (no cuentan en el total)
                        for sala in ("arriba", "medimos", "guardamos", "abajo"):
                            page.goto(base + path + "#" + sala, wait_until="networkidle")
                            page.wait_for_timeout(500)
                            (SHOTS / "salas").mkdir(exist_ok=True)
                            page.screenshot(path=str(SHOTS / "salas" / f"{label}_{key}_{sala}.png"))
                ctx.close()
            n = len(list(SHOTS.glob("*.png")))  # sin contar salas/
            check("Capturas de escritorio y móvil, ES, EN y 404", n == 10, f"{n} capturas")
        browser.close()
    srv.shutdown()

    ok = sum(r["ok"] for r in results)
    now = datetime.now(timezone(timedelta(hours=-5))).strftime("%Y-%m-%d %H:%M (UTC−5)")
    lines = [
        "# Verificación de la portada",
        "",
        f"**{ok} de {len(results)} comprobaciones correctas** · {now} · Chromium (Playwright) contra `herramientas/servidor_local.py`.",
        "",
        "Inspección automática. No sustituye pruebas con personas, lectores de pantalla reales, otros navegadores ni la revisión del sitio ya publicado en Cloudflare.",
        "",
        "| | Comprobación | Detalle |",
        "|---|---|---|",
    ]
    for r in results:
        lines.append(f"| {'✓' if r['ok'] else '✗'} | {r['comprobacion']} | {r['detalle'] if not r['ok'] else ''} |")
    (OUT / "informe.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (OUT / "informe.json").write_text(json.dumps({"fecha": now, "correctas": ok, "total": len(results), "resultados": results}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n{ok}/{len(results)} correctas → {OUT / 'informe.md'}")
    sys.exit(0 if ok == len(results) else 1)


if __name__ == "__main__":
    main()
