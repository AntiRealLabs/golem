#!/usr/bin/env python3
"""Verificación automática de la portada antes de publicarla.

Uso:  python3 -I herramientas/verificar_portada.py [--sin-capturas]

Levanta herramientas/servidor_local.py (imita Cloudflare Pages con _headers),
abre las páginas en Chromium (Playwright) y comprueba: puerta de publicación,
estados HTTP y cabeceras, las reglas del primer corte ED01 (lo pendiente nunca es
cero, sin ranking ni notas por frase, tres voces separadas), las de ED02-X1 (la etiqueta
del piloto a la vista, el orden condicional con los dos motores, los avisos también en el
celular, cada pasaje abre su fuente, las voces sin mezclarse al cambiar de idioma), las
páginas de los recorridos, paridad ES/EN, enlaces,
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
# ED02-X1: páginas de lectura que se revisan con el mismo cuidado (la de 351 palabras, otra de GPT y el método)
LECTURAS = {"rc-es": "/ed02-x1/m03-c02-r1/", "rc-en": "/en/ed02-x1/m03-c02-r1/", "rc-gpt": "/ed02-x1/m04-c01-r1/",
            "metodo-es": "/ed02-x1/metodo/", "metodo-en": "/en/ed02-x1/metodo/"}
BADGE = {"es": "Piloto exploratorio · ED02-X1", "en": "Exploratory pilot · ED02-X1"}
WIDTHS = [1440, 1024, 768, 390, 320]
FAMILIES = ["UnifrakturMaguntia", "Chakra Petch", "Archivo", "Fragment Mono", "DM Sans", "Newsreader"]
EXTERNAL_OK = {"https://antireallabs.com", "mailto:admin@antireallabs.com"}
# Primer corte ED01: estas son las únicas configuraciones que la portada puede nombrar (ED02-X1 nombra además
# a Gemini, solo como pendiente, fuera de su índice), y los textos de estado que nunca pueden faltar ni volverse cero.
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
    check("sitemap.xml es XML válido con las dos portadas y las 26 páginas de ED02-X1", s == 200 and okxml and b.count(b"<loc>") == 28, f"{b.count(b'<loc>')} direcciones")
    for nombre, ruta in LECTURAS.items():
        st, hh, bb = http(base, ruta)
        check(f"HTTP: {ruta} responde 200 con HTML", st == 200 and hh.get("Content-Type", "").startswith("text/html"), str(st))

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
                text = page.evaluate("""() => { const c = document.body.cloneNode(true); c.querySelectorAll('.x1-fuera-lista, script, style, template').forEach(e => e.remove());
                    return c.textContent.replace(/\\s+/g, ' '); }""")
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
                      for (const g of document.querySelectorAll('[data-voz="editorial"]')) if (!/\\S/.test((g.querySelector('.capa-rotulo, .f-sub') || {}).textContent || '')) out.push('guía sin rótulo');
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
                x1 = page.evaluate(
                    """(badge) => {
                      const out = [], vis = e => !!e && e.checkVisibility({visibilityProperty: true});
                      // la etiqueta del piloto: en la cartela de la placa, a la vista al llegar, y encima de los resultados
                      const cart = document.querySelector('.onfalo .placa-estado');
                      if (!cart || cart.textContent.trim() !== badge || !vis(cart)) out.push('cartela');
                      const res = document.querySelector('#resultados .x1-badge');
                      if (!res || res.textContent.trim() !== badge) out.push('etiqueta en resultados');
                      // el orden condicional: dos filas y, al lado, los dos motores, cada uno con su primero marcado
                      const filas = [...document.querySelectorAll('.x1-tabla tbody tr')];
                      if (filas.length !== 2 || filas.some(f => f.querySelectorAll('.x1-num').length !== 3)) out.push('tabla');
                      if (document.querySelectorAll('.x1-tabla .x1-num--primero').length !== 2) out.push('el primero de cada motor');
                      if (filas.length === 2 && filas[0].querySelector('.x1-num--primero') === filas[1].querySelector('.x1-num--primero')) out.push('primeros');
                      // ninguna cifra del índice como porcentaje, ni ganadores
                      const t = document.querySelector('#resultados').textContent;
                      if (/\\d[.,]\\d\\s*%/.test(t) || /ganador|winner|campeón|champion/i.test(t)) out.push('porcentaje o ganador');
                      // los 42 escenarios: 21 y 21, cada rejilla de un solo color: el motor decide
                      const rej = [...document.querySelectorAll('.esc-rejilla')].map(r => [...r.children].map(c => c.className.split('--')[1]));
                      if (rej.length !== 2 || rej.some(r => r.length !== 21 || new Set(r).size !== 1) || rej[0][0] === rej[1][0]) out.push('escenarios');
                      // fuera del índice: sin cifra y sin puesto; Gemini, pendiente
                      const fuera = document.querySelector('.x1-fuera-lista');
                      if (!fuera || !/Gemini/.test(fuera.textContent) || /\\d[.,]\\d/.test(fuera.textContent) || fuera.querySelectorAll('li').length !== 3) out.push('fuera del índice');
                      // el aviso de las 351 palabras, con la nota completa a un clic
                      const aviso = document.querySelector('#resultados .aviso-x1');
                      if (!aviso || !/351/.test(aviso.textContent) || !/59/.test(aviso.textContent) || !aviso.querySelector('a[data-panel="x1-incidencias"]')) out.push('aviso');
                      if (!document.querySelector('#x1-incidencias .panel-contenido[data-voz="editorial"] .capa-rotulo')) out.push('nota completa');
                      // las cuatro unidades del laboratorio, cada cifra una sola vez y con lo que cuenta
                      if (document.querySelectorAll('.cifras--x1 .cifras-lista li').length !== 4 || document.querySelectorAll('.cifras--x1 .cifras-lista li .cifra-d').length !== 4) out.push('unidades');
                      // a la izquierda, muestras sin cifras: lo que pesan las preguntas, dibujado (tres tercios, cada uno con su
                      // pregunta), y quién puntúa cada especialidad (J1–J3 por dos motores). Nombres completos y pesos, en su sala.
                      // Se mira lo que se ve en el escritorio: el resumen de la baldosa del celular sí lleva el peso de J1–J3 (Juan)
                      for (const q of document.querySelectorAll('.q--preguntas, .q--como-medimos, .trailer--preguntas, .trailer--como-medimos')) {
                        if (/J\\d\\.\\d|1\\/3|(peso|weight)\\s*\\d/i.test(q.innerText)) out.push('pesos en ' + q.className.split(' ').pop());
                        const pesa = q.querySelector('.pesa'), lee = q.querySelector('.lee');
                        if (/preguntas/.test(q.className) && (!pesa || pesa.querySelectorAll('.pesa-tercio .pesa-tramo').length !== 3)) out.push('la barra de las preguntas');
                        if (/medimos/.test(q.className) && (!lee || lee.querySelectorAll('tbody tr').length !== 3 || lee.querySelectorAll('tbody .lee-hoja').length !== 6)) out.push('quién puntúa');
                      }
                      if (document.querySelectorAll('#x1-medimos .x1-crit--pregunta').length !== 3 || !document.querySelector('#x1-medimos .x1-persp-lista + .x1-pesos')) out.push('de dónde sale el 30 %');
                      // junto a las cifras, encima de los dos motores: cambiar de motor invierte el orden
                      const giro = document.querySelector('.x1-tabla thead th.x1-giro-th[colspan="2"][scope="colgroup"]');
                      if (!giro || !vis(giro) || !document.querySelector('.q--resultados .x1-giro')) out.push('el giro junto a las cifras');
                      // en el laboratorio, primero lo disponible: el pasaje, las unidades y los recorridos; el taller, al final
                      const antes = (a, b) => { const x = document.querySelector(a), y = document.querySelector(b);
                        return x && y && (x.compareDocumentPosition(y) & Node.DOCUMENT_POSITION_FOLLOWING); };
                      if (!antes('#x1-laboratorio .x1-voces', '#x1-laboratorio .x1-unidades') || !antes('#x1-laboratorio', '#laboratorio .taller')
                          || !antes('#laboratorio .edicion-aparte', '#laboratorio .taller')) out.push('orden del laboratorio');
                      if (!document.querySelector('.x1-voces .rotador + details.x1-como')) out.push('cómo se eligen los pasajes');
                      // los doce recorridos, enlazados
                      if (document.querySelectorAll('#x1-recorridos a.x1-rec-a').length !== 12) out.push('recorridos');
                      // ED02-X1 no se mezcla con ED01: cada serie en su lugar
                      for (const sel of ['#resultados', '#x1-laboratorio', '#x1-medimos']) {
                        const e = document.querySelector(sel);
                        if (!e || /ED01|IA-01/.test(e.textContent)) out.push('mezcla en ' + sel);
                      }
                      if (document.querySelectorAll('.edicion-aparte').length !== 3) out.push('separadores de ED01');
                      return out;
                    }""",
                    BADGE[key],
                )
                check(f"[{key}] ED02-X1: «{BADGE[key]}» en la placa y en resultados; orden condicional con los dos motores y, encima de ellos, que cambiar de motor invierte el orden; 42 escenarios partidos por motor; sin porcentajes; fuera del índice sin cifras; el aviso de 351 palabras con su nota; cada unidad una vez; a la izquierda, el 30 % dibujado y quién puntúa cada especialidad, sin pesos; el 30 % explicado en su sala; el laboratorio empieza por el pasaje y deja el taller al final; doce recorridos; ED01 aparte",
                      not x1, "; ".join(sorted(set(x1))))
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
            for key, path in list(PAGES.items()) + list(LECTURAS.items()):
                page.goto(base + path, wait_until="networkidle")
                page.evaluate("document.fonts.ready")
                sw = page.evaluate("document.documentElement.scrollWidth")
                if sw > w:
                    overflow.append(f"{key}@{w}: {sw}")
            ctx.close()
        check("Sin desplazamiento horizontal a 1440, 1024, 768, 390 y 320 px (portadas, 404, recorridos y método)", not overflow, str(overflow))

        # ---------- «Volver al centro» no se mete en el texto de su sala ----------
        # Está fijo en el borde de cada sala lateral y el texto pasa por debajo al bajar: basta con que ninguna
        # caja con texto de la sala comparta columnas con él. A 1165 px tapaba «Un caso nuevo» (revisión del 20 oct).
        cruces = []
        for w, h in ((960, 700), (1000, 700), (1100, 700), (1165, 720), (1200, 760), (1280, 720), (1300, 760), (1340, 768), (1366, 768), (1440, 900), (1920, 1080)):
            ctx = browser.new_context(viewport={"width": w, "height": h})
            page = ctx.new_page()
            for key in ("es", "en"):
                page.goto(base + PAGES[key], wait_until="networkidle")
                page.evaluate("document.fonts.ready")
                for c in page.evaluate("""() => {
                    const out = [];
                    for (const v of document.querySelectorAll('.volver-lado')) {
                      const b = v.getBoundingClientRect(), sala = v.closest('.panel--lado');
                      if (!b.width) continue;
                      for (const el of sala.querySelectorAll('.lado-in :is(h2,h3,h4,h5,p,li,dt,dd,summary,td,th,blockquote,figcaption,a,button)')) {
                        const r = el.getBoundingClientRect();
                        if (r.width && r.height && el.textContent.trim() && Math.min(r.right, b.right) - Math.max(r.left, b.left) > .5)
                          out.push(sala.id + ': ' + el.textContent.trim().slice(0, 30));
                      }
                    }
                    return out;
                  }"""):
                    cruces.append(f"{key}@{w}: {c}")
            ctx.close()
        check("«Volver al centro» no se cruza con el texto de su sala entre 960 y 1920 px, en los dos idiomas y con los desplegables (acostado desde 1340; de lado por debajo)",
              not cruces, str(sorted(set(cruces))[:6]))

        # ---------- objetivos táctiles, teclado ----------
        ctx = browser.new_context(viewport={"width": 390, "height": 844}, has_touch=True, is_mobile=True)
        page = ctx.new_page()
        small = []
        for key, path in list(PAGES.items()) + list(LECTURAS.items()):
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
        quieto = page.evaluate("""() => { const t = document.getElementById('x1-pasajes'), primero = t && t.content.firstElementChild;
            return {primero: primero ? primero.dataset.fragmento : null, rotadores: [...document.querySelectorAll('[data-rotador]')].map(r => {
              const vis = [...r.querySelectorAll('.rot-pila > [data-fragmento]')].filter(f => !f.hidden).map(f => f.dataset.fragmento);
              const ctl = r.querySelector('[data-rot-controles]');
              return vis.join(',') + (ctl && ctl.hidden ? '' : ' +controles'); }),
              enlaces: [...document.querySelectorAll('[data-rotador] a[data-x1-pasaje]')].map(a => a.getAttribute('href'))}; }""")
        destinos = []
        for href in set(quieto["enlaces"]):
            ruta, ancla = href.split("#")
            st, _, cuerpo = http(base, ruta)
            destinos.append(st == 200 and f'id="{ancla}"' in cuerpo.decode())
        fichas = page.evaluate("[...document.querySelectorAll('a[data-panel]')].every(a => { const t = document.getElementById(a.getAttribute('href').slice(1)); return t && t.querySelector('.panel-contenido'); })")
        check("Sin JavaScript: cada carrusel de ED02-X1 queda quieto en su primer pasaje, sin controles; «Leer en contexto» lleva al pasaje en la página de su recorrido y cada ficha está en la página",
              quieto["primero"] and quieto["rotadores"] and all(q == quieto["primero"] for q in quieto["rotadores"]) and destinos and all(destinos) and fichas,
              f"{quieto} {destinos} {fichas}")
        ctx.close()

        # ---------- los fragmentos: se barajan por visita, se avanzan a mano y conservan su lugar al cambiar de idioma ----------
        ctx = browser.new_context(viewport={"width": 1440, "height": 900}, reduced_motion="no-preference")
        page = ctx.new_page()
        page.goto(base + "/", wait_until="networkidle")
        page.evaluate("document.fonts.ready")
        ACTUAL = "() => { const r = document.querySelector('.cuadrante [data-rotador]'); const f = r && r.querySelector('[data-actual]'); return [f ? f.dataset.fragmento : null, r ? r.querySelector('.rot-cuenta').textContent.trim() : null]; }"
        antes = page.evaluate(ACTUAL)
        orden = page.evaluate("JSON.parse(sessionStorage.getItem('gb-x1-pasajes') || 'null')")
        plantilla = page.evaluate("[...document.getElementById('x1-pasajes').content.children].map(c => c.dataset.fragmento)")
        boton = page.locator(".cuadrante [data-rotador] [data-rot='1']")
        boton.focus()
        page.keyboard.press("Enter")
        page.wait_for_timeout(100)
        despues = page.evaluate(ACTUAL)
        foco = page.evaluate("document.activeElement.matches('.cuadrante [data-rot=\"1\"]')")
        anim = page.evaluate("getComputedStyle(document.querySelector('.cuadrante [data-actual]')).animationName")
        esperado = orden["orden"][(orden["orden"].index(antes[0]) + 1) % 60] if orden and antes[0] in orden.get("orden", []) else None
        page.wait_for_timeout(3000)
        quieto = page.evaluate(ACTUAL)
        page.goto(base + "/en/", wait_until="networkidle")
        page.evaluate("document.fonts.ready")
        en = page.evaluate(ACTUAL)
        check("Pasajes de ED02-X1: los 60 de la plantilla, barajados una vez por visita; «siguiente» avanza uno y el foco se queda en el botón; sin avance automático; el inglés conserva el mismo pasaje",
              orden and len(plantilla) == 60 and sorted(orden["orden"]) == sorted(plantilla) and despues[0] == esperado and foco
              and quieto == despues and en[0] == despues[0] and despues[1] != antes[1],
              f"{orden} {antes} {despues} {quieto} {en} foco={foco}")
        ctx.close()
        ctx = browser.new_context(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
        page = ctx.new_page()
        page.goto(base + "/", wait_until="networkidle")
        page.click(".cuadrante [data-rotador] [data-rot='1']")
        anim_reducido = page.evaluate("getComputedStyle(document.querySelector('.cuadrante [data-actual]')).animationName")
        check("Movimiento reducido: el cambio de pasaje aparece sin animación (con movimiento, un fundido corto)",
              anim_reducido == "none" and anim == "aparece", f"{anim_reducido} / {anim}")

        # ---------- el panel de lectura ----------
        panel = []
        enlace = page.locator(".cuadrante [data-actual] a[data-x1-pasaje]")
        href = enlace.get_attribute("href")
        enlace.focus()
        page.keyboard.press("Enter")
        page.wait_for_function("() => { const d = document.getElementById('panel-lectura'); return d.open && !d.hasAttribute('aria-busy'); }", timeout=8000)
        abierto = page.evaluate("""(href) => { const d = document.getElementById('panel-lectura'), c = d.querySelector('.pl-cuerpo');
            const caja = c.querySelector('.px1-caja'), marca = caja && caja.querySelector('.cita.activa');
            const rc = caja ? caja.getBoundingClientRect() : null, rm = marca ? marca.getBoundingClientRect() : null;
            const jueces = [...c.querySelectorAll('.px1-jueces .juicio')];
            return {abierto: d.open, foco: d.contains(document.activeElement), titulo: d.querySelector('.pl-titulo').textContent.trim(),
                    marca: !!marca && rm.top >= rc.top - 1 && rm.bottom <= rc.bottom + 1, modelo: !!c.querySelector('.px1-caja .rc-texto[data-voz="modelo"][lang="es"]'),
                    jueces: jueces.length, completos: jueces.every(j => j.querySelector('.capa-rotulo') && j.querySelector('.regla .regla-pos--marca') && j.querySelectorAll('.juicio-cuerpo .j-campo').length === 2),
                    etapa: (c.querySelector('.px1-meta') || {}).textContent || '', abrir: (c.querySelector('.px1-abrir') || {}).getAttribute ? c.querySelector('.px1-abrir').getAttribute('href') === href : false,
                    ids: c.querySelectorAll('[id]').length}; }""", href)
        if not (abierto["abierto"] and abierto["foco"] and abierto["marca"] and abierto["modelo"] and abierto["jueces"] >= 1 and abierto["completos"]
                and abierto["abrir"] and abierto["ids"] == 0 and abierto["titulo"] not in ("", "Lectura") and "ED02-" in abierto["etapa"]):
            panel.append(f"abrir: {abierto}")
        page.keyboard.press("Escape")
        page.wait_for_timeout(100)
        vuelve = page.evaluate("[document.getElementById('panel-lectura').open, document.activeElement.matches('.cuadrante [data-actual] a[data-x1-pasaje]')]")
        if vuelve != [False, True]:
            panel.append(f"Esc y foco de vuelta: {vuelve}")
        # la nota completa de incidencias, desde el aviso de resultados; se cierra tocando afuera
        page.evaluate("document.querySelector('#resultados .aviso-x1 a[data-panel]').click()")
        page.wait_for_timeout(100)
        nota = page.evaluate("[document.getElementById('panel-lectura').open, /351/.test(document.querySelector('#panel-lectura .pl-cuerpo').textContent), document.querySelector('#panel-lectura .pl-titulo').textContent.trim()]")
        page.mouse.click(8, 8)   # el fondo oscuro, fuera del panel
        page.wait_for_timeout(100)
        if not (nota[0] and nota[1]) or page.evaluate("document.getElementById('panel-lectura').open"):
            panel.append(f"nota de incidencias / clic afuera: {nota}")
        # si falta la ficha o el recorrido, el panel lo dice (y deja el enlace)
        page.evaluate("""() => { for (const [id, attr, h] of [['prueba-panel', 'panel', 'no-existe'], ['prueba-x1', 'x1Pasaje', '/ed02-x1/no-existe/#p-a-1-2']]) {
            const a = document.createElement('a'); a.href = attr === 'panel' ? '#' + h : h; a.dataset[attr] = h; a.id = id; a.textContent = 'x'; document.querySelector('.foot').append(a); } }""")
        page.click("#prueba-panel")
        page.wait_for_timeout(100)
        error = page.evaluate("[document.getElementById('panel-lectura').open, !document.querySelector('#panel-lectura .pl-error').hidden]")
        page.click("#panel-lectura [data-cerrar]")
        if error != [True, True] or page.evaluate("document.getElementById('panel-lectura').open"):
            panel.append(f"ficha que no está: {error}")
        page.click("#prueba-x1")
        page.wait_for_function("() => !document.getElementById('panel-lectura').hasAttribute('aria-busy')", timeout=8000)
        error_x1 = page.evaluate("[document.getElementById('panel-lectura').open, !!document.querySelector('#panel-lectura .pl-cuerpo .pl-error a[href]')]")
        page.click("#panel-lectura [data-cerrar]")
        if error_x1 != [True, True]:
            panel.append(f"recorrido que no está: {error_x1}")
        check("Panel de lectura: «Leer en contexto» abre el pasaje marcado a la vista en su texto original y las lecturas que lo citan (rótulo, nivel, justificación y límite), con el enlace a su recorrido; la nota de incidencias se abre igual; se cierra con Esc, con su botón o tocando afuera, el foco vuelve al enlace y, si algo falta, lo dice",
              not panel, "; ".join(panel))
        ctx.close()

        # ---------- ED02-X1: las páginas de los recorridos y la de método ----------
        ctx = browser.new_context(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
        ctx.add_init_script("window.__csp=[];document.addEventListener('securitypolicyviolation',e=>window.__csp.push(e.violatedDirective+' '+e.blockedURI));")
        for key, path in LECTURAS.items():
            page = ctx.new_page()
            errors = []
            page.on("console", lambda m, errors=errors: errors.append(m.text) if m.type == "error" else None)
            page.on("pageerror", lambda e, errors=errors: errors.append(str(e)))
            page.goto(base + path, wait_until="networkidle")
            page.evaluate("document.fonts.ready")
            lang = "en" if key.endswith("-en") else "es"
            info = page.evaluate("""(lang) => {
                const out = [];
                if (document.documentElement.lang !== lang) out.push('idioma');
                if (document.querySelectorAll('h1').length !== 1) out.push('h1');
                const can = (document.querySelector('link[rel=canonical]') || {}).href || '';
                if (!can.startsWith('https://golembench.org/') || !can.endsWith(location.pathname)) out.push('canónica ' + can);
                if ([...document.querySelectorAll('link[rel=alternate][hreflang]')].map(l => l.hreflang).sort().join() !== 'en,es') out.push('hreflang');
                if (!document.querySelector('.stamp') || !/ED02-X1/.test(document.querySelector('.stamp').textContent)) out.push('etiqueta del piloto');
                // las voces, cada una con su rótulo y su forma, sin anidarse
                for (const j of document.querySelectorAll('.juicio[data-voz="juez"]')) if (!j.firstElementChild.matches('.capa-rotulo')) out.push('juez sin rótulo');
                for (const t of document.querySelectorAll('.rc-texto[data-voz="modelo"]')) if (!t.closest('.rc-texto-caja') || !t.closest('.rc-texto-caja').querySelector('.capa-rotulo')) out.push('modelo sin rótulo');
                for (const c of document.querySelectorAll('[data-voz="critica"], [data-voz="editorial"]')) if (!c.querySelector('.capa-rotulo')) out.push(c.dataset.voz + ' sin rótulo');
                if (document.querySelector('[data-voz] [data-voz]')) out.push('voces anidadas');
                // en inglés cambia la interfaz; los cuerpos del modelo, de las críticas y de los jueces siguen en español
                for (const e of document.querySelectorAll('.rc-texto, .rc-critica-texto, .rc-material-texto, .j-campo > p:not(.j-rot):not(.j-vacio):not(.j-sub), .j-sub > span:not(.j-rot-in), .juicio-ancla span:not(.j-rot-in), .ref-cita q, .ref-otra q, .j-proc > li > p:not(.j-sub), .j-alertas > li > p:not(:has(.j-alerta)), .j-alerta'))
                  if (e.closest('[lang]').getAttribute('lang') !== 'es') { out.push('cuerpo sin lang=es: ' + e.className + ' ' + e.textContent.slice(0, 40)); break; }
                if (lang === 'en' && document.querySelector('.rc-texto') && !/Spanish original/.test(document.body.textContent)) out.push('sin aviso de original');
                // enlaces de la página: cada ancla existe
                for (const a of document.querySelectorAll('a[href^="#"]')) if (!document.getElementById(a.getAttribute('href').slice(1))) { out.push('ancla rota ' + a.getAttribute('href')); break; }
                return out; }""", lang)
            csp = page.evaluate("window.__csp")
            rotos = []
            for href in set(page.evaluate("[...document.querySelectorAll('a[href^=\"/\"]')].map(a => a.getAttribute('href'))")):
                st, hh, _ = http(base, href.split("#")[0])
                if st == 308:
                    st, _, _ = http(base, hh.get("Location", ""))
                if st != 200:
                    rotos.append(f"{href} → {st}")
            check(f"[{key}] ED02-X1: sin errores ni violaciones de la CSP; idioma, h1, canónica y hreflang; la etiqueta del piloto; cada voz con su rótulo y los cuerpos en español; enlaces que llegan",
                  not errors and not csp and not info and not rotos, f"{errors} {csp} {info} {rotos}")
            if key.startswith("rc-"):
                rc = page.evaluate("""() => ({lecturas: document.querySelectorAll('.juicio').length, textos: document.querySelectorAll('.rc-texto[data-voz="modelo"]').length,
                    criticas: document.querySelectorAll('.rc-critica').length, pasajes: document.querySelectorAll('.p-a').length,
                    niveles: [...document.querySelectorAll('.juicio .regla')].every(r => r.children.length === 5 && r.querySelectorAll('.regla-pos--marca').length === 1),
                    aviso: !!document.querySelector('#etapa-e .aviso-x1'), palabras351: /351 (palabras|words)/.test(document.querySelector('#etapa-e .rc-meta').textContent)})""")
                es351 = key in ("rc-es", "rc-en")
                check(f"[{key}] ED02-X1: el recorrido trae 5 textos, 2 críticas y 32 lecturas, cada una con una sola marca en su regla de 0 a 4"
                      + ("; la transferencia de 351 palabras lleva su aviso" if es351 else ""),
                      rc["lecturas"] == 32 and rc["textos"] == 5 and rc["criticas"] == 2 and rc["pasajes"] > 0 and rc["niveles"] and (rc["aviso"] == es351 == rc["palabras351"]), str(rc))
                # seguir un pasaje: se ilumina entero, aunque esté partido en tramos, y queda a la vista bajo la barra y la ruta
                pid = page.evaluate("[...document.querySelectorAll('.p-a')].find(a => document.querySelectorAll('.cita[data-p~=\"' + a.id + '\"]').length > 1).id")
                page.goto(base + path + "#" + pid, wait_until="networkidle")
                page.wait_for_timeout(300)
                seguido = page.evaluate("""(pid) => { const tramos = [...document.querySelectorAll('.cita[data-p~="' + pid + '"]')];
                    const r = document.getElementById(pid).getBoundingClientRect(), ruta = document.querySelector('.rc-ruta').getBoundingClientRect();
                    return {tramos: tramos.length, activos: tramos.filter(t => t.classList.contains('activa')).length,
                            otros: document.querySelectorAll('.cita.activa').length, visible: r.top >= ruta.bottom - 2 && r.top < innerHeight}; }""", pid)
                check(f"[{key}] ED02-X1: seguir un pasaje lo ilumina entero (todos sus tramos, ninguno más) y lo deja a la vista bajo la ruta",
                      seguido["tramos"] > 1 and seguido["activos"] == seguido["tramos"] and seguido["otros"] == seguido["tramos"] and seguido["visible"], str(seguido))
            page.close()
        ctx.close()
        # en el celular, los avisos siguen a la vista: la etiqueta, el orden condicional, los escenarios y las 351 palabras
        ctx = browser.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True, reduced_motion="reduce")
        page = ctx.new_page()
        movil = []
        for key, path in (("es", "/"), ("en", "/en/")):
            page.goto(base + path, wait_until="networkidle")
            page.evaluate("document.fonts.ready")
            r = page.evaluate("""(badge) => { const vis = e => !!e && e.checkVisibility({visibilityProperty: true}) && e.getBoundingClientRect().width > 40;
                const cart = document.querySelector('.onfalo .placa-estado'), rc = cart.getBoundingClientRect();
                const tr = document.querySelector('.trailer--resultados');
                return {cartela: vis(cart) && rc.top >= 0 && rc.bottom <= innerHeight && cart.textContent.trim() === badge,
                        trailer: vis(tr) && vis(tr.querySelector('.stamp')) && tr.querySelectorAll('.tr-aviso').length === 2 && [...tr.querySelectorAll('.tr-aviso')].every(vis) && vis(tr.querySelector('.x1-mini')),
                        sala: ['.x1-orden .x1-nota', '.x1-tabla', '.x1-sensibilidad .x1-nota', '.x1-nota--sesgo', '#resultados .aviso-x1', '.x1-fuera-lista', '.x1-limites .limites-lista'].map(s => vis(document.querySelector(s))),
                        tabla: document.querySelector('.x1-tabla-caja').scrollWidth <= document.querySelector('.x1-tabla-caja').clientWidth + 1,
                        // la vista inicial resume las cuatro estaciones a la vista, y la de resultados dice que el motor invierte el orden
                        resumenes: [...document.querySelectorAll('.onfalo .q-resumen.res')].filter(e => vis(e) && e.getBoundingClientRect().top >= 0
                                     && e.getBoundingClientRect().bottom <= innerHeight).length === 4 && vis(document.querySelector('.res--resultados .res-giro'))}; }""", BADGE[key])
            # al tocar la baldosa de resultados, lo primero que se ve es el orden: la primera fila entera, con la etiqueta encima
            page.click(".estacion--resultados .lugar")
            page.wait_for_timeout(1200)
            r["llegada"] = page.evaluate("""() => { const f = document.querySelector('.x1-tabla tbody tr').getBoundingClientRect(),
                b = document.querySelector('#resultados .x1-badge').getBoundingClientRect();
                return f.top >= 0 && f.bottom <= innerHeight && b.top >= 0; }""")
            if not (r["cartela"] and r["trailer"] and all(r["sala"]) and r["tabla"] and r["resumenes"] and r["llegada"]):
                movil.append(f"{key}: {r}")
        check("En el celular la etiqueta del piloto y el resumen de las cuatro estaciones quedan a la vista al llegar; tocar Resultados lleva primero al orden; el tráiler de resultados y su sala conservan las advertencias (orden condicional, escenarios, sesgo, 351 palabras, fuera del índice, límites) y la tabla cabe sin desplazarse",
              not movil, "; ".join(movil))
        # el cambio de idioma no mezcla voces: el mismo pasaje sigue en español y con el mismo destino
        page.goto(base + "/", wait_until="networkidle")
        es_ = page.evaluate("(() => { const f = document.querySelector('.trailers [data-actual]'); return [f.dataset.fragmento, f.querySelector('.f-cita').textContent.trim(), f.querySelector('.f-cita').lang]; })()")
        page.goto(base + "/en/", wait_until="networkidle")
        en_ = page.evaluate("(() => { const f = document.querySelector('.trailers [data-actual]'); return [f.dataset.fragmento, f.querySelector('.f-cita').textContent.trim(), f.querySelector('.f-cita').lang, !!f.querySelector('.f-traduccion')]; })()")
        check("Cambio de idioma: el mismo pasaje, palabra por palabra, sigue en español original (lang=es) y avisa que no está traducido; la interfaz cambia, la voz del modelo no",
              es_[0] == en_[0] and es_[1] == en_[1] and es_[2] == en_[2] == "es" and en_[3], f"{es_} {en_}")
        ctx.close()

        # ---------- axe y espaciado de texto (sin CSP, para poder inyectar) ----------
        axe_fail, axe_bp = [], []
        for w in (1440, 390):
            ctx = browser.new_context(viewport={"width": w, "height": 900}, bypass_csp=True)
            page = ctx.new_page()
            for key, path in list(PAGES.items()) + list(LECTURAS.items()):
                page.goto(base + path, wait_until="networkidle")
                page.evaluate(AXE)
                r = page.evaluate("axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']}})")
                for v in r["violations"]:
                    axe_fail.append(f"{key}@{w}: {v['id']} ({len(v['nodes'])})")
                r = page.evaluate("axe.run(document,{runOnly:{type:'tag',values:['best-practice']}})")
                for v in r["violations"]:
                    axe_bp.append(f"{key}@{w}: {v['id']}")
            ctx.close()
        check("axe-core 4.14 · WCAG 2.0/2.1/2.2 A y AA: sin violaciones (8 páginas × 2 anchos: portadas, 404, recorridos y método)", not axe_fail, str(axe_fail))
        check("axe-core · buenas prácticas: sin avisos", not axe_bp, str(sorted(set(axe_bp))))

        spacing = []
        for w in (1280, 390):
            ctx = browser.new_context(viewport={"width": w, "height": 900}, bypass_csp=True)
            page = ctx.new_page()
            for key, path in list(PAGES.items()) + list(LECTURAS.items()):
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
