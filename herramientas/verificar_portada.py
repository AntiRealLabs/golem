#!/usr/bin/env python3
"""Verificación automática de la portada antes de publicarla.

Uso:  python3 -I herramientas/verificar_portada.py [--sin-capturas]

Levanta herramientas/servidor_local.py (imita Cloudflare Pages con _headers),
abre las páginas en Chromium (Playwright) y comprueba: puerta de publicación,
estados HTTP y cabeceras, las reglas del primer corte ED01 (lo pendiente nunca es
cero, sin ranking ni notas por frase, tres voces separadas), paridad ES/EN, enlaces,
fuentes, CSP sin violaciones, anchos sin desborde, espaciado de texto, teclado,
objetivos táctiles, símbolos de las estaciones, choques y desbordes en el centro,
fragmentos que rotan, panel de lectura, axe-core (WCAG 2.2 A/AA), peso e imágenes.
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
# Primer corte ED01: estas son las únicas configuraciones que la portada puede nombrar,
# y los textos de estado que nunca pueden faltar ni volverse cero.
COHORTE = ["SmolLM3-3B", "Qwen3-8B", "Claude Opus 5.5", "GPT-6.1-sol"]
OTROS_MODELOS = re.compile(r"\b(Gemini|Llama|Mistral|Grok|DeepSeek|o3|GPT-4|GPT-5(?!\.\d-sol)|Sonnet|Haiku)\b")
PENDIENTE = {"es": "Pendiente", "en": "Pending"}
SIN_RANKING = {"es": "Sin clasificación general publicada", "en": "No overall ranking published"}
EN_PREPARACION = {"es": "Ranking general en preparación", "en": "Overall ranking in preparation"}
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
          not viejas and len(sirven) == len(versionar_recursos.RECURSOS) and all(x == 200 for x in sirven),
          "; ".join(viejas) or f"estados {sirven}")
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
    # la figura del golem va completa, sin sombreado añadido; la versión panorámica solo sirve a las tarjetas
    fuentes = ROOT / "herramientas" / "fuentes"
    sizes = {f: Image.open(SITE / "assets" / f).size for f in ("arcilla-1122.webp", "arcilla-720.webp")}
    taller = Image.open(fuentes / "taller-2172.webp").size
    check("Figura del golem: arte original a tamaño completo (1122×1402); la panorámica no se publica",
          sizes == {"arcilla-1122.webp": (1122, 1402), "arcilla-720.webp": (720, 900)} and taller == (2172, 724)
          and not (SITE / "assets" / "taller-2172.webp").exists(), f"{sizes} {taller}")
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
                      counts: ['h2','h3','li','p','a'].map(s=>[...document.querySelectorAll('main '+s+', header '+s+', footer '+s)].filter(e=>!e.parentElement.closest('[lang]:not(html)')).length),
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
                sim = page.evaluate(
                    """() => {
                      const ids = new Set([...document.querySelectorAll('svg.simbolos symbol')].map(s => s.id));
                      const rotos = [...document.querySelectorAll('use')].map(u => u.getAttribute('href')).filter(h => !h || h[0] !== '#' || !ids.has(h.slice(1)));
                      const ruidosos = [...document.querySelectorAll('svg.simbolo, svg.simbolos')].filter(s => s.getAttribute('aria-hidden') !== 'true' || s.getAttribute('focusable') !== 'false').length;
                      const rumbos = [...document.querySelectorAll('.onfalo .rumbo .lugar')].map(a => { const u = a.querySelector('svg.simbolo use'); return a.getAttribute('href') + '>' + (u ? u.getAttribute('href') : ''); });
                      const dibujados = [...document.querySelectorAll('.onfalo .rumbo .lugar svg.simbolo')].every(s => { const r = s.getBoundingClientRect(); return r.width >= 16 && r.height >= 16; });
                      const mascota = ['.foot-brand svg.simbolo--golem', '#laboratorio .lockup svg.marca-golem', '.onfalo .placa svg.placa-golem'].every(s => { const u = document.querySelector(s + ' use'); return u && u.getAttribute('href') === '#s-golem'; })
                        // en la placa, la mascota va a la izquierda de «Golem», de su mismo alto y a su altura (Juan, 18 oct 2026)
                        && (() => { const m = document.querySelector('.onfalo .placa-golem').getBoundingClientRect(), w = document.querySelector('.onfalo .wordmark-g'),
                                          g = w.getBoundingClientRect(), fs = parseFloat(getComputedStyle(w).fontSize);
                                    // y «Golem» sigue en el eje de la placa
                                    const p = document.querySelector('.onfalo .placa').getBoundingClientRect();
                                    return m.right <= g.left && Math.abs(m.height - .74 * fs) < 2 && Math.abs(m.top - g.top) < 3
                                      && Math.abs((g.left + g.right) / 2 - (p.left + p.right) / 2) < 2; })();
                      return {ids: [...ids].sort(), rotos, ruidosos, rumbos, dibujados, mascota};
                    }"""
                )
                want_r = ["#preguntas>#s-preguntas", "#laboratorio>#s-laboratorio", "#como-medimos>#s-medimos", "#resultados>#s-resultados"]
                check(f"[{key}] cada estación lleva su símbolo; la mascota va a la izquierda de «Golem» y firma el pie y el laboratorio; los lectores de pantalla los saltan",
                      sim["ids"] == ["s-golem", "s-laboratorio", "s-medimos", "s-preguntas", "s-resultados"] and not sim["rotos"]
                      and not sim["ruidosos"] and sim["rumbos"] == want_r and sim["dibujados"] and sim["mascota"], str(sim))
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
                m = OTROS_MODELOS.search(text)
                check(f"[{key}] ED01: solo se nombran las cuatro configuraciones de la cohorte", not m and all(c in text for c in COHORTE),
                      m.group(0) if m else "falta alguna de la cohorte")
                ed = page.evaluate(
                    """([pend, sinRk, prep]) => {
                      const txt = s => [...document.querySelectorAll(s)].map(e => e.textContent.trim());
                      const out = [];
                      // lo pendiente dice «Pendiente»: nunca un cero, un guion o un hueco
                      const pendientes = [...txt('.ruta-fase:not(.ruta-fase--cerrada) .ruta-e'), ...txt('.fase:not(.fase--cerrada) .fase-e'), ...txt('.criterios .es-pendiente')];
                      if (!pendientes.length || pendientes.some(t => t !== pend)) out.push('pendiente: ' + [...new Set(pendientes)].join('|'));
                      // sin ranking publicado: la tabla no tiene filas, dice que no hay clasificación y el sello sigue a la vista
                      const rk = document.querySelector('#ranking');
                      if (!rk || rk.querySelectorAll('tbody tr').length) out.push('ranking con filas');
                      if (rk && rk.querySelector('caption').textContent.trim() !== sinRk) out.push('ranking sin su estado vacío');
                      if (!txt('.stamp').includes(prep)) out.push('falta «' + prep + '»');
                      // ningún fragmento lleva nota, medalla, regla ni barra
                      if (document.querySelector('.fragmento .regla, .fragmento meter, .fragmento progress, meter, progress')) out.push('nota o barra en un fragmento');
                      // una pregunta, dos lecturas: dos reglas de cinco posiciones con una sola marca cada una
                      const reglas = [...document.querySelectorAll('.regla')];
                      if (reglas.length !== 2 || reglas.some(r => r.children.length !== 5 || r.querySelectorAll('.regla-pos--marca').length !== 1)) out.push('reglas');
                      if (/[→⟶]|promedio|average/i.test(document.querySelector('.dl-lecturas').textContent)) out.push('flecha o promedio entre las lecturas');
                      // tres voces separadas por rótulo y estructura
                      for (const q of document.querySelectorAll('[data-voz="modelo"]')) {
                        const caja = q.closest('figure, .fuente-texto, .panel-contenido');
                        if (!caja || (!caja.querySelector('.f-voz') && !(q.closest('.panel-contenido') && q.closest('.panel-contenido').querySelector('.fuente-voz .f-voz')))) out.push('texto del modelo sin su rótulo');
                      }
                      for (const g of document.querySelectorAll('[data-voz="editorial"]')) if (!/\S/.test((g.querySelector('.capa-rotulo, .f-sub') || {}).textContent || '')) out.push('guía sin rótulo');
                      for (const j of document.querySelectorAll('[data-voz="juez"]')) if (!j.closest('.lectura-juez') || !j.closest('.lectura-juez').querySelector('.capa-rotulo')) out.push('lectura del juez sin rótulo');
                      if (document.querySelector('[data-voz] [data-voz]')) out.push('voces anidadas');
                      // el supuesto a examen nunca viaja sin su nota
                      for (const f of document.querySelectorAll('[data-fragmento="GB-ED01-F004"]')) if (!f.querySelector('[data-voz="editorial"]')) out.push('F004 sin su nota');
                      return out;
                    }""",
                    [PENDIENTE[key], SIN_RANKING[key], EN_PREPARACION[key]],
                )
                check(f"[{key}] ED01: lo pendiente dice «{PENDIENTE[key]}», sin ranking ni notas por frase; dos reglas con una marca; las tres voces con su rótulo; F004 con su nota",
                      not ed, "; ".join(sorted(set(ed))))
                other = visible_text(page, exclude_lang="es" if key == "en" else "en")
                hint = (SPANISH_HINTS if key == "en" else ENGLISH_HINTS).findall(other)
                check(f"[{key}] sin restos del otro idioma fuera de lo marcado con lang", not hint, str(sorted(set(hint)))[:200])
            page.close()
        check("Paridad ES/EN: mismos h2, h3, elementos de lista, párrafos y enlaces (sin contar el original español que acompaña a la traducción)",
              structure.get("es") == structure.get("en"), str(structure))
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
                if bb and (bb["width"] < 24 or bb["height"] < 24) and a.evaluate("e=>e.checkVisibility({visibilityProperty:true})&&(getComputedStyle(e).position!=='absolute'||e.matches(':focus'))"):
                    small.append(f"{key}: {a.inner_text()[:30]} {bb['width']:.0f}×{bb['height']:.0f}")
        check("Objetivos táctiles ≥ 24 px en móvil (WCAG 2.5.8)", not small, str(small))
        ctx.close()

        ctx = browser.new_context(viewport={"width": 1280, "height": 800})
        page = ctx.new_page()
        page.goto(base + "/", wait_until="networkidle")
        page.keyboard.press("Tab")
        first = page.evaluate("document.activeElement.getAttribute('href')")
        vis = page.evaluate("(()=>{const r=document.activeElement.getBoundingClientRect();return r.top>=0&&r.bottom<=innerHeight})()")
        check("Teclado: el primer Tab se queda en el centro, a la vista (selector de idioma)", first == "/" and vis, f"{first} {vis}")
        order = []
        page.goto(base + "/", wait_until="networkidle")
        page.evaluate("document.fonts.ready")
        for _ in range(24):
            page.keyboard.press("Tab")
            info = page.evaluate("""() => { const a = document.activeElement, e = a.closest('.estacion');
                return [a.classList.contains('lugar') ? 'lugar ' + a.getAttribute('href') : (a.getAttribute('href') || a.className || a.tagName),
                        e ? e.className.split('--')[1] : (a.closest('.langs') ? 'idioma' : 'fuera')]; }""")
            if info[1] == "fuera":
                break
            order.append(info)
        lugares = [o[0] for o in order if o[0].startswith("lugar ")]
        # lo de cada esquina va justo después de su recuadro, sin mezclarse con otra estación
        tramos, actual = [], None
        for o in order[2:]:
            if o[0].startswith("lugar "):
                actual = o[1]
                tramos.append(actual)
            elif o[1] != actual:
                tramos.append("¡" + o[1] + "!")
        check("Teclado: desde el centro, ES → EN → cada estación con lo de su esquina: ↑, →, ←, ↓",
              [o[0] for o in order[:2]] == ["/", "/en/"] and lugares == ["lugar #preguntas", "lugar #laboratorio", "lugar #como-medimos", "lugar #resultados"]
              and not any(t.startswith("¡") for t in tramos), str(order))
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
                pos = page.evaluate("""() => { const c=document.getElementById('cruce'),
                    f=document.getElementById('fila'), p=document.getElementById('centro'), s=document.querySelector('.onfalo .placa').getBoundingClientRect();
                    return {dy: Math.round(-c.getBoundingClientRect().top), dx: Math.round(f.scrollLeft - p.offsetLeft),
                            sx: Math.round(s.left + s.width / 2 - document.documentElement.clientWidth / 2), sy: Math.round(s.top + s.height / 2 - innerHeight / 2),
                            brj: getComputedStyle(document.querySelector('.brujula')).visibility,
                            cur: (document.querySelector('.brujula [aria-current]')||{}).dataset?.sala || null}; }""")
                check(f"Cruz [{key} · {label}]: se llega al centro (el nombre a la vista, brújula en el centro)",
                      abs(pos["dy"]) <= 3 and abs(pos["dx"]) <= 3 and pos["cur"] == "centro", str(pos))
                check(f"Cruz [{key} · {label}]: la placa del nombre queda en el centro exacto de la pantalla (±3 px)",
                      abs(pos["sx"]) <= 3 and abs(pos["sy"]) <= 3, str(pos))
                order_ok = page.evaluate("""() => { const pie=document.querySelector('.escalera-pie').getBoundingClientRect().top,
                    a=document.querySelector('.peldano').getBoundingClientRect().top,
                    z=document.querySelector('.peldano--ultimo').getBoundingClientRect().top,
                    cima=document.querySelector('.escalera-cima').getBoundingClientRect().top,
                    centro=document.getElementById('cruce').getBoundingClientRect().top;
                    return pie > a && a > z && z > cima && pie < centro; }""")
                check(f"Cruz [{key} · {label}]: arriba se lee de abajo hacia arriba (la primera pregunta queda junto al centro)", order_ok)
                # el signo del pie no lo atraviesa ninguna línea: ni la de la escalera, ni sus tramos y puntos, ni la que baja al centro
                pie = page.evaluate("""() => {
                    const pie = document.querySelector('.escalera-pie').getBoundingClientRect(), zona = [pie.top - 12, pie.bottom + 12];
                    const tramos = [], caja = (e, pseudo, n) => { const c = getComputedStyle(e, pseudo);
                        if (c.display === 'none' || c.content === 'none') return;
                        const t = e.getBoundingClientRect().top + parseFloat(c.top); tramos.push([n, t, t + parseFloat(c.height)]); };
                    caja(document.querySelector('.escalera'), '::before', 'línea');
                    for (const e of document.querySelectorAll('.peldano, .escalera-cima')) { caja(e, '::before', 'punto'); caja(e, '::after', 'tramo'); }
                    caja(document.querySelector('.sala--arriba'), '::after', 'tramo de abajo');
                    return {tramos: tramos.length, cruzan: tramos.filter(([n, a, b]) => a < zona[1] && b > zona[0]).map(([n, a, b]) => n + ' ' + Math.round(a - pie.top) + '…' + Math.round(b - pie.top))};
                }""")
                check(f"Cruz [{key} · {label}]: ninguna línea toca el signo del pie de la escalera (12 px de aire)",
                      pie["tramos"] >= 3 and not pie["cruzan"], str(pie))
                page.keyboard.press("ArrowRight")
                page.wait_for_timeout(900)
                right = page.evaluate("(document.querySelector('.brujula [aria-current]')||{}).dataset?.sala || null")
                page.keyboard.press("ArrowLeft"); page.wait_for_timeout(900)
                page.keyboard.press("ArrowLeft"); page.wait_for_timeout(900)
                left = page.evaluate("(document.querySelector('.brujula [aria-current]')||{}).dataset?.sala || null")
                check(f"Cruz [{key} · {label}]: ← y → recorren la fila (laboratorio / cómo medimos)", right == "laboratorio" and left == "como-medimos", f"{right} {left}")
                page.goto(base + path, wait_until="networkidle")
                page.wait_for_timeout(200)
                page.click(".rumbo--o .lugar")
                page.wait_for_timeout(500)
                vis = page.evaluate("""() => { const e=document.querySelector('#como-medimos .lugar--aqui').getBoundingClientRect();
                    return e.top >= -1 && e.left >= 0 && e.right <= innerWidth && location.hash === '#como-medimos'; }""")
                check(f"Cruz [{key} · {label}]: el rumbo ← lleva a cómo medimos y se ve desde su primera línea", vis)
                lado = page.evaluate("""() => { const p=document.getElementById('como-medimos'), s=p.querySelector('.lado-scroll');
                    return {alto: Math.round(p.getBoundingClientRect().height - innerHeight), corre: s.scrollHeight > s.clientHeight, modo: getComputedStyle(s).overflowY}; }""")
                check(f"Cruz [{key} · {label}]: las salas laterales miden una pantalla y se recorren por dentro",
                      abs(lado["alto"]) <= 2 and lado["corre"] and lado["modo"] == "auto", str(lado))
                hueco = page.evaluate("""() => { const abajo = document.querySelector('.sala--abajo').getBoundingClientRect(), c = document.getElementById('cruce').getBoundingClientRect(),
                    tr = document.querySelector('.trailers'), r = document.getElementById('resultados').getBoundingClientRect();
                    const tramo = tr.getClientRects().length ? tr.getBoundingClientRect() : null;
                    return [Math.round(abajo.top - c.bottom), Math.round(r.top - (tramo ? tramo.bottom : c.bottom))]; }""")
                check(f"Cruz [{key} · {label}]: sin vacío entre el centro y lo de abajo (en el celular, los cuatro tráileres; luego, los resultados)",
                      abs(hueco[0]) <= 1 and abs(hueco[1]) <= 1, f"{hueco} px")
                page.goto(base + path + "#resultados", wait_until="networkidle")
                page.wait_for_timeout(400)
                down = page.evaluate("(document.querySelector('.brujula [aria-current]')||{}).dataset?.sala || null")
                brj_abajo = page.evaluate("getComputedStyle(document.querySelector('.brujula')).visibility")
                page.goto(base + path + "#preguntas", wait_until="networkidle")
                page.wait_for_timeout(400)
                up = page.evaluate("(document.querySelector('.brujula [aria-current]')||{}).dataset?.sala || null")
                check(f"Cruz [{key} · {label}]: los enlaces llevan a cada sala y la brújula lo marca", down == "resultados" and up == "preguntas", f"{down} {up}")
                check(f"Cruz [{key} · {label}]: la brújula se esconde en el centro y aparece al alejarse",
                      pos["brj"] == "hidden" and brj_abajo == "visible", f"{pos['brj']} {brj_abajo}")
            ctx.close()
        # el centro no se amontona: los cuadrantes no tocan la placa ni los rumbos, y la placa sigue en el centro
        choques = []
        CHOQUES_JS = """() => {
          const m = parseFloat(getComputedStyle(document.querySelector('.onfalo')).getPropertyValue('--marco')) || 12;
          const caja = (e, pad=0) => { const r = e.getBoundingClientRect(); return {x0:r.left-pad, y0:r.top-pad, x1:r.right+pad, y1:r.bottom+pad, n:String(e.className).split(' ').pop()}; };
          const vis = s => [...document.querySelectorAll(s)].filter(e => e.getClientRects().length);
          const toca = (a, b) => a.x0 < b.x1 && a.x1 > b.x0 && a.y0 < b.y1 && a.y1 > b.y0;
          const fuera = (a, r) => a.x0 < r.left - 1 || a.x1 > r.right + 1 || a.y0 < r.top - 1 || a.y1 > r.bottom + 1;
          const fijos = [caja(document.querySelector('.onfalo .placa'), m + 1), ...vis('.onfalo .rumbo .lugar, .onfalo .rumbo .susurro, .langs a').map(e => caja(e))];
          const flechas = vis('.onfalo .lugar-f').map(e => caja(e));   // solo en el celular
          const p = document.getElementById('centro').getBoundingClientRect(), s = document.querySelector('.onfalo .placa').getBoundingClientRect();
          const out = [];
          if (Math.abs(s.top + s.height / 2 - innerHeight / 2) > 3) out.push('placa fuera del centro');
          for (const e of vis('.cuadrante > *, .onfalo .rumbo .lugar')) {
            const a = caja(e), cuad = !!e.closest('.cuadrante');
            if (cuad && fuera(a, p)) out.push('fuera: ' + a.n);
            if (cuad) for (const b of fijos) if (toca(a, b)) out.push(a.n + ' × ' + b.n);
            if (!cuad && toca(a, fijos[0])) out.push(a.n + ' × placa');   // los rumbos tampoco tocan el marco de la placa
            for (const b of flechas) if (toca(a, b)) out.push(a.n + ' × ' + b.n);
            // en el celular cada estación es una baldosa: lo suyo no se sale de ella
            const t = e.closest('.estacion');
            if (t && t.getClientRects().length && fuera(a, t.getBoundingClientRect())) out.push('fuera de su estación: ' + a.n);
          }
          // nada se sale de su esquina: lo que no cabe se guarda entero
          for (const c of vis('.cuadrante')) {
            if (getComputedStyle(c).containerType !== 'size') continue;
            const r = c.getBoundingClientRect(), cs = getComputedStyle(c);
            for (const h of c.children) {
              if (!h.getClientRects().length) continue;
              const b = h.getBoundingClientRect();
              if (b.top < r.top + parseFloat(cs.paddingTop) - 1 || b.bottom > r.bottom - parseFloat(cs.paddingBottom) + 1) out.push('se sale de su esquina: ' + String(h.className).split(' ')[0]);
            }
          }
          // los cuatro recuadros miden lo mismo (en el celular caben dos renglones; ninguno pide tres)
          const altos = vis('.onfalo .rumbo .lugar').map(e => Math.round(e.getBoundingClientRect().height));
          if (Math.max(...altos) - Math.min(...altos) > 1) out.push('recuadros desiguales: ' + altos.join('/'));
          return out;
        }"""
        for vw, vh in ((1920, 1080), (1440, 790), (1366, 768), (1280, 720), (1024, 768), (768, 1024), (390, 844), (360, 740), (375, 667), (320, 568)):
            ctx = browser.new_context(viewport={"width": vw, "height": vh}, reduced_motion="reduce", is_mobile=vw < 600, has_touch=vw < 600)
            page = ctx.new_page()
            for key, path in (("es", "/"), ("en", "/en/")):
                page.goto(base + path, wait_until="networkidle")
                page.evaluate("document.fonts.ready")
                choques += [f"{key}@{vw}×{vh}: {c}" for c in page.evaluate(CHOQUES_JS)]
            ctx.close()
        check("Centro sin choques: tráileres, rumbos, flechas y placa no se tocan en diez tamaños; nada se sale de su esquina ni de su estación; los cuatro recuadros miden lo mismo y la placa sigue en el centro",
              not choques, "; ".join(sorted(set(choques)))[:300])
        ctx = browser.new_context(viewport={"width": 1280, "height": 800}, java_script_enabled=False)
        page = ctx.new_page()
        page.goto(base + "/", wait_until="networkidle")
        nojs = page.evaluate("[document.querySelectorAll('h1').length, ['preguntas','cruce','centro','resultados','como-medimos','laboratorio'].every(id => !!document.getElementById(id))]")
        check("Cruz sin JavaScript: todo el contenido sigue ahí, con sus enlaces", nojs == [1, True], str(nojs))
        quieto = page.evaluate("""() => [...document.querySelectorAll('[data-rotador]')].map(r => {
            const vis = [...r.querySelectorAll('.rot-pila > [data-fragmento]')].filter(f => !f.hidden).map(f => f.dataset.fragmento);
            const ctl = r.querySelector('[data-rot-controles]');
            return vis.join(',') + (ctl && ctl.hidden ? '' : ' +controles'); })""")
        fichas = page.evaluate("[...document.querySelectorAll('a[data-panel]')].every(a => { const t = document.getElementById(a.getAttribute('href').slice(1)); return t && t.querySelector('.panel-contenido'); })")
        check("Sin JavaScript: cada fragmento rotativo queda quieto en GB-ED01-F001, sin controles, y «Leer en contexto» lleva a la ficha completa de su fuente",
              quieto and all(q == "GB-ED01-F001" for q in quieto) and fichas, f"{quieto} {fichas}")
        ctx.close()

        # ---------- los fragmentos: se barajan por visita, se avanzan a mano y conservan su lugar al cambiar de idioma ----------
        ctx = browser.new_context(viewport={"width": 1440, "height": 900}, reduced_motion="no-preference")
        page = ctx.new_page()
        page.goto(base + "/", wait_until="networkidle")
        page.evaluate("document.fonts.ready")
        ACTUAL = "() => { const r = document.querySelector('.cuadrante [data-rotador]'); const f = r && r.querySelector('[data-actual]'); return [f ? f.dataset.fragmento : null, r ? r.querySelector('.rot-cuenta').textContent.trim() : null]; }"
        antes = page.evaluate(ACTUAL)
        orden = page.evaluate("JSON.parse(sessionStorage.getItem('gb-ed01-fragmentos') || 'null')")
        boton = page.locator(".cuadrante [data-rotador] [data-rot='1']")
        boton.focus()
        page.keyboard.press("Enter")
        page.wait_for_timeout(100)
        despues = page.evaluate(ACTUAL)
        foco = page.evaluate("document.activeElement.matches('.cuadrante [data-rot=\"1\"]')")
        anim = page.evaluate("getComputedStyle(document.querySelector('.cuadrante [data-actual]')).animationName")
        esperado = orden["orden"][(orden["orden"].index(antes[0]) + 1) % 5] if orden and antes[0] in orden.get("orden", []) else None
        page.wait_for_timeout(3000)
        quieto = page.evaluate(ACTUAL)
        page.goto(base + "/en/", wait_until="networkidle")
        page.evaluate("document.fonts.ready")
        en = page.evaluate(ACTUAL)
        check("Fragmentos: orden barajado de cinco por visita; «siguiente» avanza uno y el foco se queda en el botón; sin avance automático; el inglés conserva el mismo fragmento",
              orden and sorted(orden["orden"]) == [f"GB-ED01-F00{i}" for i in range(1, 6)] and despues[0] == esperado and foco
              and quieto == despues and en[0] == despues[0] and despues[1] != antes[1],
              f"{orden} {antes} {despues} {quieto} {en} foco={foco}")
        ctx.close()
        ctx = browser.new_context(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
        page = ctx.new_page()
        page.goto(base + "/", wait_until="networkidle")
        page.click(".cuadrante [data-rotador] [data-rot='1']")
        anim_reducido = page.evaluate("getComputedStyle(document.querySelector('.cuadrante [data-actual]')).animationName")
        check("Movimiento reducido: el cambio de fragmento aparece sin animación (con movimiento, un fundido corto)",
              anim_reducido == "none" and anim == "aparece", f"{anim_reducido} / {anim}")

        # ---------- el panel de lectura ----------
        panel = []
        enlace = page.locator(".cuadrante [data-actual] a[data-panel]")
        enlace.focus()
        page.keyboard.press("Enter")
        page.wait_for_timeout(150)
        abierto = page.evaluate("""() => { const d = document.getElementById('panel-lectura'), c = d.querySelector('.pl-cuerpo'), m = c.querySelector('mark');
            const rc = c.getBoundingClientRect(), rm = m ? m.getBoundingClientRect() : null;
            return {abierto: d.open, foco: d.contains(document.activeElement), titulo: d.querySelector('.pl-titulo').textContent.trim(),
                    marca: !!m && rm.top >= rc.top - 1 && rm.bottom <= rc.bottom + 1, voz: !!c.querySelector('.fuente-voz .f-voz'), aviso: !!c.querySelector('.fuente-aviso')}; }""")
        if not (abierto["abierto"] and abierto["foco"] and abierto["marca"] and abierto["voz"] and abierto["aviso"] and abierto["titulo"] not in ("", "Lectura")):
            panel.append(f"abrir: {abierto}")
        page.keyboard.press("Escape")
        page.wait_for_timeout(100)
        vuelve = page.evaluate("[document.getElementById('panel-lectura').open, document.activeElement.matches('.cuadrante [data-actual] a[data-panel]')]")
        if vuelve != [False, True]:
            panel.append(f"Esc y foco de vuelta: {vuelve}")
        page.click(".cuadrante a[data-panel='que-contamos']")
        page.wait_for_timeout(100)
        definiciones = page.evaluate("document.querySelectorAll('#panel-lectura[open] .definiciones dt').length")
        page.mouse.click(8, 8)   # el fondo oscuro, fuera del panel
        page.wait_for_timeout(100)
        if definiciones != 3 or page.evaluate("document.getElementById('panel-lectura').open"):
            panel.append(f"qué contamos / clic afuera: {definiciones}")
        page.evaluate("() => { const a = document.createElement('a'); a.href = '#no-existe'; a.dataset.panel = 'no-existe'; a.id = 'prueba-panel'; a.textContent = 'x'; document.querySelector('.foot').append(a); }")
        page.click("#prueba-panel")
        page.wait_for_timeout(100)
        error = page.evaluate("[document.getElementById('panel-lectura').open, !document.querySelector('#panel-lectura .pl-error').hidden]")
        page.click("#panel-lectura [data-cerrar]")
        if error != [True, True] or page.evaluate("document.getElementById('panel-lectura').open"):
            panel.append(f"fuente que no está: {error}")
        check("Panel de lectura: «Leer en contexto» abre la fuente con la cita marcada a la vista; se cierra con Esc, con su botón o tocando afuera, y el foco vuelve al enlace; si falta la fuente lo dice",
              not panel, "; ".join(panel))
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
                # los títulos solo para lectores de pantalla (.sr-only) van recortados a propósito
                clipped = page.evaluate("""[...document.querySelectorAll('h1,h2,h3,p,a,li')].filter(e=>!e.matches('.sr-only') && e.scrollWidth>e.clientWidth+1 && getComputedStyle(e).overflow!=='visible').length""")
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
                        for sala in ("preguntas", "como-medimos", "laboratorio", "resultados"):
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
