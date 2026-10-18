#!/usr/bin/env python3
"""Escribe el primer corte ED01 en las dos portadas a partir del paquete de coordinación.

Uso:  python3 -I herramientas/construir_ed01.py CARPETA_DEL_PAQUETE site [--ranking RESULTADOS.json]

El paquete (Golem_portada_contenidos_Claude_v0_1, de coordinación) no vive en este repo. Este script
lee solo sus campos de contenido público (01, 02, 03, 04, 06 y 07) y los escribe entre los marcadores
<!-- ed01:NOMBRE --> … <!-- /ed01:NOMBRE --> de site/index.html y site/en/index.html. Lo que hay entre
marcadores no se edita a mano: se regenera. Nunca copia instrucciones, manifiestos, la verificación
del paquete ni huellas de dictámenes.

Cada texto del paquete pasa tal cual (escapado para HTML). Lo único escrito aquí son los rótulos
funcionales de ROT y los textos de la portada anterior que se conservan, propuestos por Claude (✎)
para que coordinación los apruebe. Después de correrlo: versionar_recursos.py, cotejar_ed01.py y
verificar_portada.py.
"""
import html
import json
import re
import sys
import urllib.parse
from pathlib import Path

PAQ, SITIO = Path(sys.argv[1]), Path(sys.argv[2])


def leer(nombre):
    return json.loads((PAQ / nombre).read_text(encoding="utf-8"))


P = leer("01_Portada_ES_EN.json")
E = leer("02_ED01_estado_y_cohorte_ES_EN.json")
F = leer("03_Fragmentos_ES_EN.json")
S = leer("04_Fuentes_A_ES_EN.json")
M = leer("06_Metodo_y_limites_ES_EN.json")
D = leer("07_Un_texto_dos_lecturas_ES_EN.json")

SH = P["shared"]
Q = {q["id"]: q for q in P["quadrants"]}
FRAG = {f["id"]: f for f in F["items"]}
FUENTE = {s["id"]: s for s in S["sources"]}
ENTREGA = {x["id"]: x for x in E["submissions"]}
CASO = {x["case_id"]: x["case_label"] for x in E["submissions"]}
ETAPA = {x["id"]: x for x in E["stages"]}
ANCLA = {a["value"]: a["label"] for a in M["anchors"]}
CRIT = {c["id"]: (j, c) for j in M["judges"] for c in j["criteria"]}
F004 = "GB-ED01-F004"
# fuentes y fragmentos van de uno en uno: cada fuente sostiene exactamente una cita
assert sorted(f["source_id"] for f in F["items"]) == sorted(FUENTE), "cada fragmento con su fuente"
DE_FUENTE = {f["source_id"]: f for f in F["items"]}

# ✎ Rótulos funcionales que el paquete no trae (propuesta de Claude; los aprueba coordinación)
ROT = {
    "contexto": ("Contexto", "Context"),
    "pregunta_ed": ("Pregunta editorial", "Editorial question"),
    "limite": ("Límite de lectura", "Reading limit"),
    "cuenta_pre": ("Fragmento", "Excerpt"),
    "cuenta_de": ("de", "of"),
    "cerrar": ("Cerrar", "Close"),
    "panel": ("Lectura", "Reading"),
    "caso": ("Caso", "Case"),
    "fase": ("Fase", "Phase"),
    "palabras": ("Palabras contadas", "Words counted"),
    "limite_palabras": ("{n} · límite: {l}", "{n} · limit: {l}"),
    "estado": ("Estado", "Status"),
    "cerrada": ("Cerrada", "Closed"),
    "lectura_cerrada": ("Lectura inicial cerrada", "Initial reading closed"),
    "motor": ("motor evaluador", "evaluator engine"),
    "fuera": ("Cerrada · fuera de comparación", "Closed · outside comparison"),
    "que_contamos": ("Qué contamos", "What we count"),
    "fuentes_t": ("Las cinco fuentes", "The five sources"),
    "fuentes_nota": ("Las respuestas completas que sostienen los cinco fragmentos. No son los expedientes de los casos, ni las doce entregas, ni los dictámenes.",
                     "The complete responses behind the five excerpts. They are not the case files, the twelve submissions or the assessments."),
    "temas_t": ("Temas de este lote", "Themes in this batch"),
    "puerta_estado": ("Todavía en el taller", "Still in the workshop"),
    "mientras": ("Mientras tanto:", "Meanwhile:"),
    "ir_fuentes": ("las cinco fuentes completas", "the five complete sources"),
    "ir_dos": ("una pregunta con dos lecturas", "one question with two readings"),
    "ir_voces": ("los fragmentos de ED01", "the ED01 excerpts"),
    "cohorte_t": ("Las cuatro configuraciones", "The four configurations"),
    "cohorte_orden": ("Orden fijo de la cohorte: no es un orden de resultados.", "Fixed cohort order: not an order of results."),
    "por_caso": ("Estados por caso", "Status by case"),
    "fases_t": ("Las fases de ED01", "The ED01 phases"),
    "ranking_t": ("Ranking general", "Overall ranking"),
    "limites_t": ("Límites de este corte", "Limits of this release"),
    "juez_cita": ("Lectura del juez · cita literal del dictamen", "Judge’s reading · literal quotation from the assessment"),
    "juez_trad": ("Lectura del juez · traducción editorial del original español", "Judge’s reading · editorial translation of the Spanish original"),
    "campo_razon_del_anclaje": ("Razón del anclaje", "Reason for the anchor"),
    "campo_limite_o_carencia": ("Límite o carencia", "Limitation or shortcoming"),
    "nivel": ("Nivel {n}", "Level {n}"),
    "regla": ("Nivel {n} en una regla de 0 a 4", "Level {n} on a scale from 0 to 4"),
    "criterio": ("Qué valora el criterio", "What the criterion assesses"),
    "entrega_completa": ("Leer la entrega completa", "Read the full submission"),
    "criterios_t": ("Criterios y pesos", "Criteria and weights"),
    "referentes_t": ("Referentes", "Reference thinkers"),
    "escala_t": ("La escala", "The scale"),
    "indice_t": ("El índice candidato", "The candidate index"),
    "razones_t": ("Razones y límites", "Reasons and limits"),
    "criterio_col": ("Criterio", "Criterion"),
    "peso": ("Peso en la especialidad", "Weight within the specialty"),
    "evidencia": ("Lee la fase", "Reads phase"),
    "en_ed01": ("En ED01", "In ED01"),
    "procedencia": ("Huella SHA-256 del original", "SHA-256 fingerprint of the original"),
    "procedencia_en": ("", "SHA-256 fingerprint of the translation"),
    "rumbos_t": ("Los cuatro rumbos", "The four bearings"),
    "discutir": ("Discútelo con nosotros", "Discuss it with us"),
    "discutir_asunto": ("Supuesto a examen · GB-ED01-F004", "An assumption to examine · GB-ED01-F004"),
    "dentro": ("dentro del límite", "within the limit"),
    "fuera_c": ("fuera de comparación", "outside comparison"),
    "juez": ("Juez", "Judge"),
    "fases_aria": ("Fases de ED01", "ED01 phases"),
    "voces_lista": ("Fragmentos de ED01", "ED01 excerpts"),
    "taller": ("En el taller", "In the workshop"),
}
NO_DISPONIBLE = ("Este fragmento todavía no está disponible. Puedes explorar las preguntas del laboratorio.",
                 "This excerpt is not available yet. You can explore the lab’s questions.")
PENDIENTE_NOTA = ("Los resultados de esta fase siguen pendientes. Un dato pendiente no equivale a cero.",
                  "Results for this phase are still pending. A pending result is not zero.")
ERROR_FUENTE = ("No pudimos cargar la fuente. Intenta de nuevo.", "We couldn’t load the source. Try again.")
SIN_RANKING = ("Sin clasificación general publicada", "No overall ranking published")
# textos de la portada actual que se conservan (aprobados en la fase 1)
PULL_NOTA = ("Cada dictamen guarda una razón, una lectura alternativa y la evidencia que cambiaría la nota.",
             "Every assessment keeps a reason, an alternative reading and the evidence that would change the score.")
JUECES_T = ("Del número al argumento.", "From the number to the argument.")


def L(par, lang):
    return par[0 if lang == "es" else 1]


def r(clave, lang, **k):
    s = L(ROT[clave], lang)
    return s.format(**k) if k else s


def e(s):
    return html.escape(str(s), quote=True)


def t(campo, lang):
    """Un campo bilingüe del paquete, escapado."""
    return e(campo[lang])


def md(texto, resaltar=None):
    """Presenta el texto del participante sin cambiarlo: párrafos, saltos y el énfasis que marcó.
    Si se pide, marca el pasaje citado (aparece una sola vez en la fuente)."""
    if resaltar:
        assert texto.count(resaltar) == 1, resaltar[:40]
        i = texto.index(resaltar)
        texto = texto[:i] + "\x01" + resaltar + "\x02" + texto[i + len(resaltar):]
    partes = []
    for p in re.split(r"\n\s*\n", texto.strip()):
        p = e(p.strip())
        p = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", p)
        p = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", p)
        p = re.sub(r" *\n", "<br>", p)
        partes.append(f"<p>{p}</p>")
    salida = "".join(partes)
    return salida.replace("\x01", '<mark class="cita-en-fuente">').replace("\x02", "</mark>")


def simbolo(nombre, extra=""):
    return f'<svg class="simbolo{extra}" aria-hidden="true" focusable="false"><use href="#s-{nombre}"/></svg>'


SIMB = {"preguntas": "preguntas", "laboratorio": "laboratorio", "resultados": "resultados", "como-medimos": "medimos"}
DESTINO = {"preguntas": "#apuestas", "laboratorio": "#laboratorio", "resultados": "#resultados", "como-medimos": "#como-medimos"}
FLECHA = {"preguntas": "↑", "laboratorio": "→", "resultados": "↓", "como-medimos": "←"}


def enlace(qid, lang, clase):
    f, txt = FLECHA[qid], t(Q[qid]["cta"], lang)
    cuerpo = f'{txt} <span aria-hidden="true">{f}</span>' if f == "→" else f'<span aria-hidden="true">{f}</span> {txt}'
    return f'<a class="{clase}" href="{DESTINO[qid]}">{cuerpo}</a>'


def rotulo(qid, lang, clase):
    return f'<p class="{clase}">{simbolo(SIMB[qid])}<span>{t(Q[qid]["eyebrow"], lang)}</span></p>'


# ---------------------------------------------------------------- muestras

def triptico(lang):
    notas = "".join(f'<div class="tri-nota"><dt>{t(v["label"], lang)}</dt><dd>{t(v["line"], lang)}</dd></div>'
                    for v in Q["preguntas"]["visual_items"])
    return f'<dl class="triptico">{notas}</dl>'


def cifras(lang, que=True):
    """La franja de datos: siempre con su alcance al lado."""
    items = "".join(f'<li><span class="cifra">{m["value"]}</span> <span class="cifra-l">{t(m["label"], lang)}</span></li>' for m in E["metrics"])
    boton = (f'<a class="cifras-que" href="#que-contamos" data-panel="que-contamos">{r("que_contamos", lang)}</a>' if que else "")
    return (f'<div class="cifras"><p class="cifras-alcance">{t(Q["laboratorio"]["metric_scope"], lang)}</p>'
            f'<ul class="cifras-lista" role="list">{items}</ul>{boton}</div>')


def leer_en_contexto(f, lang):
    return f'<a class="f-leer" href="#fuente-{f["source_id"]}" data-panel="fuente-{f["source_id"]}">{t(Q["laboratorio"]["quote_cta"], lang)}</a>'


def autoria(f, lang, enlace=False):
    """Quién habla y dónde: la voz del modelo, la configuración y el caso. En la versión breve,
    «Leer en contexto» va en el mismo renglón del caso."""
    trad = f' <span class="f-traduccion">{t(SH["translation_label"], "en")}</span>' if lang == "en" else ""
    leer = f' <span class="f-sep" aria-hidden="true">·</span> {leer_en_contexto(f, lang)}' if enlace else ""
    return (f'<figcaption class="f-autoria"><span class="f-voz">{t(SH["source_label"], lang)}</span> '
            f'<span class="f-quien">{e(f["model_name"])} · {t(f["configuration"], lang)}</span> '
            f'<span class="f-caso">{e(f["case_id"])} · {t(CASO[f["case_id"]], lang)}{leer}</span>{trad}</figcaption>')


def guia(f, lang, clase="f-guia"):
    """La guía editorial: otra voz, con su rótulo; nunca entre las comillas de la cita."""
    return (f'<div class="{clase}" data-voz="editorial"><p class="capa-rotulo">{t(SH["editorial_label"], lang)}</p>'
            f'<p><span class="f-sub">{r("contexto", lang)}</span> {t(f["context"], lang)}</p>'
            f'<p><span class="f-sub">{r("pregunta_ed", lang)}</span> {t(f["editorial_question"], lang)}</p>'
            f'<p><span class="f-sub">{r("limite", lang)}</span> {t(f["editorial_limit"], lang)}</p></div>')


def fragmento(f, lang, completo, visible=True, extra=""):
    fid = f["id"]
    supuesto = fid == F004
    clases = "fragmento" + (" fragmento--supuesto" if supuesto else "") + (" fragmento--completo" if completo else " fragmento--breve")
    rol = ' role="listitem"' if completo and not supuesto else ""
    h = [f'<div class="{clases}" data-fragmento="{fid}"{rol}{"" if visible else " hidden"}>',
         f'<p class="f-tipo">{t(f["selection_type"], lang)}</p>',
         f'<figure class="f-figura"><blockquote class="f-cita" data-voz="modelo"><p>{t(f["quote"], lang)}</p></blockquote>',
         autoria(f, lang, enlace=not completo), "</figure>"]
    if completo:
        h.append(guia(f, lang))
        h.append(f'<p class="f-acciones">{leer_en_contexto(f, lang)}</p>')
    elif supuesto:
        # el supuesto a examen nunca viaja sin su nota: se muestra para discutirlo
        h.append(f'<p class="f-nota" data-voz="editorial"><span class="f-sub">{t(SH["editorial_label"], lang)}</span> {t(f["editorial_limit"], lang)}</p>')
    h.append(extra)
    h.append("</div>")
    return "".join(h)


def rotador(lang, clave):
    """Cinco fragmentos, uno a la vista. Sin JavaScript queda F001, quieto; con él, el orden se baraja
    una vez por visita y se avanza a mano. Los controles aparecen solo si el script los atiende."""
    items = F["items"]
    figs = "".join(fragmento(f, lang, False, f["id"] == Q["laboratorio"]["fallback_quote_id"]) for f in items)
    ctl = Q["laboratorio"]["quote_controls"]
    return (f'<div class="rotador" data-rotador="{clave}">'
            f'<div class="rot-pila">{figs}</div>'
            f'<p class="rot-vacio" hidden>{e(L(NO_DISPONIBLE, lang))}</p>'
            f'<div class="rot-controles" data-rot-controles hidden>'
            f'<button type="button" class="rot-btn" data-rot="-1" aria-label="{t(ctl["previous"], lang)}"><span aria-hidden="true">←</span></button>'
            f'<p class="rot-cuenta" aria-live="polite" aria-atomic="true"><span class="sr-only">{r("cuenta_pre", lang)} </span>'
            f'<span data-n>1</span> {r("cuenta_de", lang)} <span data-t>{len(items)}</span></p>'
            f'<button type="button" class="rot-btn" data-rot="1" aria-label="{t(ctl["next"], lang)}"><span aria-hidden="true">→</span></button>'
            f'</div></div>')


def estado_etapa(et, lang):
    return r("cerrada", lang) if et["status"] == "closed" else t(SH["pending"], lang)


def ruta(lang, etapas=("A", "B", "R", "E")):
    """A cerrada → propuesta, críticas y transferencia pendientes. No es un porcentaje."""
    items = "".join(f'<li class="ruta-fase{" ruta-fase--cerrada" if ETAPA[k]["status"] == "closed" else ""}">'
                    f'<span class="ruta-l">{t(ETAPA[k]["label"], lang)}</span> <span class="ruta-e">{e(estado_etapa(ETAPA[k], lang))}</span></li>'
                    for k in etapas)
    return f'<ol class="ruta" role="list" aria-label="{r("fases_aria", lang)}">{items}</ol>'


def cohorte_mini(lang):
    filas = "".join(f'<li><span class="c-nombre">{e(c["name"])}</span> <span class="c-conf">{t(c["configuration"], lang)}</span></li>'
                    for c in E["cohort"])
    return f'<ul class="cohorte-mini" role="list">{filas}</ul>'


def resumen_mini(lang):
    a = E["administrative_summary"]
    return (f'<p class="resumen-mini"><span class="cifra-s">{a["within_limit"]}</span> {r("dentro", lang)} '
            f'<span aria-hidden="true">·</span> <span class="cifra-s">{a["outside_comparison"]}</span> {r("fuera_c", lang)}</p>')


def sellos(lang):
    """Tres sellos del mismo tamaño; un trazo los une a la hoja que examinan los tres."""
    items = "".join(f'<li class="sello"><span class="sello-txt"><span class="sello-t"><span class="sr-only">{j["id"]} · </span>{t(j["short_title"], lang)}</span> '
                    f'<span class="sello-q">{t(j["question"], lang)}</span></span><span class="seal seal--sello" aria-hidden="true">{j["id"]}</span></li>'
                    for j in M["judges"])
    return (f'<div class="sellos"><ul class="sellos-lista" role="list">{items}</ul>'
            f'<span class="sellos-traza" aria-hidden="true"></span><span class="sellos-hoja" aria-hidden="true"></span></div>')


def muestra(qid, lang, ancho):
    if qid == "preguntas":
        return triptico(lang)
    if qid == "laboratorio":
        return cifras(lang) + rotador(lang, f"breve-{ancho}")
    if qid == "resultados":
        return (f'<p class="stamp stamp--estado">{t(Q["resultados"]["status_badge"], lang)}</p>'
                + cohorte_mini(lang) + ruta(lang) + resumen_mini(lang))
    if qid == "como-medimos":
        return sellos(lang) + f'<p class="q-alcance">{t(Q["como-medimos"]["current_scope"], lang)}</p>'


def cuadrante(qid, lang, pos):
    q = Q[qid]
    return (f'<div class="cuadrante cuadrante--{pos} q q--{qid}">'
            f'<p class="q-resumen">{t(q["headline"], lang)}</p>'
            f'{rotulo(qid, lang, "q-rotulo")}'
            f'<h2 class="q-titular">{t(q["headline"], lang)}</h2>'
            f'<div class="q-muestra">{muestra(qid, lang, "q")}</div>'
            f'<p class="q-gancho">{t(q["hook"], lang)}</p>'
            f'{enlace(qid, lang, "q-enlace")}</div>')


def trailers(lang):
    """En el celular los cuatro tráileres van apilados, debajo del centro: preguntas → laboratorio → resultados → método."""
    arts = []
    for qid in ("preguntas", "laboratorio", "resultados", "como-medimos"):
        q = Q[qid]
        tid = f"tr-{qid}"
        arts.append(f'<article class="trailer trailer--{qid}" aria-labelledby="{tid}">'
                    f'{rotulo(qid, lang, "tr-rotulo")}'
                    f'<h3 class="tr-titular" id="{tid}">{t(q["headline"], lang)}</h3>'
                    f'<p class="tr-cuerpo">{t(q["body"], lang)}</p>'
                    f'<div class="tr-muestra">{muestra(qid, lang, "tr")}</div>'
                    f'<p class="tr-gancho">{t(q["hook"], lang)}</p>'
                    f'{enlace(qid, lang, "tr-enlace")}</article>')
    return (f'<section class="trailers" aria-labelledby="trailers-t"><h2 class="sr-only" id="trailers-t">{r("rumbos_t", lang)}</h2>\n      '
            + "\n      ".join(arts) + "\n    </section>")


# ---------------------------------------------------------------- arriba: las seis apuestas

def apuestas(lang):
    d = P["principles_detail"]
    items = "".join(f'<details class="apuesta"><summary><span class="ap-t">{t(p["title"], lang)}</span>'
                    f'<span class="ap-pregunta">{t(p["prompt"], lang)}</span></summary>'
                    f'<p class="ap-texto">{t(p["text"], lang)}</p></details>'
                    for p in d["items"])
    return (f'<section class="apuestas" id="apuestas" aria-labelledby="apuestas-t">'
            f'<h3 class="apuestas-titulo" id="apuestas-t">{t(d["heading"], lang)}</h3>'
            f'<p class="apuestas-intro">{t(d["intro"], lang)}</p>'
            f'<div class="apuestas-lista">{items}</div>'
            f'<p class="apuestas-peso">{t(d["weight_note"], lang)}</p></section>')


# ---------------------------------------------------------------- el laboratorio

def fuente(s, lang):
    sub = ENTREGA[s["id"]]
    f = DE_FUENTE[s["id"]]
    estado = r("cerrada", lang) if sub["state"] == "CLOSED" else r("fuera", lang)
    titulo = f'{s["model_name"]} · {s["case_id"]} · {s["case_label"][lang]}'
    meta = (f'<dl class="fuente-meta">'
            f'<div><dt>{r("caso", lang)}</dt><dd>{e(s["case_id"])} · {t(s["case_label"], lang)}</dd></div>'
            f'<div><dt>{r("fase", lang)}</dt><dd>{e(s["phase"])} · {t(ETAPA["A"]["label"], lang)}</dd></div>'
            f'<div><dt>{r("palabras", lang)}</dt><dd>{r("limite_palabras", lang, n=sub["counted_words"], l=sub["word_limit"])}</dd></div>'
            f'<div><dt>{r("estado", lang)}</dt><dd>{e(estado)}</dd></div></dl>')
    voz = (f'<p class="fuente-voz"><span class="f-voz">{t(SH["source_label"], lang)}</span> '
           f'<span class="f-quien">{e(s["model_name"])} · {t(s["configuration"], lang)}</span>'
           + (f' <span class="f-traduccion">{t(SH["translation_label"], "en")}</span>' if lang == "en" else "") + "</p>")
    if lang == "es":
        texto = f'<div class="fuente-texto" data-voz="modelo">{md(s["text"]["es"], f["quote"]["es"])}</div>'
        huellas = f'<p class="fuente-huella">{r("procedencia", lang)} <code>{s["original_utf8_sha256"]}</code></p>'
    else:
        texto = (f'<div class="fuente-texto" data-voz="modelo">{md(s["text"]["en"], f["quote"]["en"])}</div>'
                 f'<details class="original"><summary>{t(SH["original_action"], "en")}</summary>'
                 f'<div class="fuente-texto" data-voz="modelo" lang="es">{md(s["text"]["es"], f["quote"]["es"])}</div></details>')
        huellas = (f'<p class="fuente-huella">{r("procedencia", lang)} <code>{s["original_utf8_sha256"]}</code><br>'
                   f'{r("procedencia_en", lang)} <code>{s["english_utf8_sha256"]}</code></p>')
    return (f'<details class="fuente" id="fuente-{s["id"]}"><summary><span class="fuente-modelo">{e(s["model_name"])}</span> '
            f'<span class="fuente-conf">{t(s["configuration"], lang)}</span> <span class="fuente-caso">{e(s["case_id"])} · {t(s["case_label"], lang)}</span></summary>'
            f'<div class="panel-contenido" data-panel-titulo="{e(titulo)}">{meta}'
            f'<p class="fuente-tipo">{t(f["selection_type"], lang)}</p>{guia(f, lang, "f-guia f-guia--fuente")}'
            f'{voz}{texto}<p class="fuente-aviso">{t(s["notice"], lang)}</p>{huellas}</div></details>')


def lab(lang):
    d = P["lab_detail"]
    q = Q["laboratorio"]
    f4 = FRAG[F004]
    destinos = (("#fuentes", "ir_fuentes"), ("#dos-lecturas", "ir_dos"), ("#voces", "ir_voces"))
    puertas = "".join(
        f'<li class="door"><h3>{t(ro["name"], lang)}</h3><p>{t(ro["body"], lang)}</p>'
        f'<p class="door-estado"><span class="door-sello">{r("puerta_estado", lang)}</span> '
        f'{r("mientras", lang)} <a href="{destinos[i][0]}">{r(destinos[i][1], lang)}</a>.</p></li>'
        for i, ro in enumerate(d["routes"]))
    temas = "".join(f'<li><span class="tema-l">{t(th["label"], lang)}</span> <span class="tema-caso">{e(th["case"])} · {t(CASO[th["case"]], lang)}</span></li>'
                    for th in d["themes"])
    definiciones = "".join(f'<div><dt><span class="cifra-s">{m["value"]}</span> {t(m["label"], lang)}</dt><dd>{t(m["definition"], lang)}</dd></div>'
                           for m in E["metrics"])
    asunto = urllib.parse.quote(r("discutir_asunto", lang))
    voces = "".join(fragmento(FRAG[x["id"]], lang, True) for x in F["items"] if x["id"] != F004)
    invitacion = f'<p class="supuesto-discutir"><a class="btn btn--carbon" href="mailto:admin@antireallabs.com?subject={asunto}">{r("discutir", lang)}</a></p>'
    n = chr(10) + " " * 14
    return n.join([
        '<div class="taller">',
        f'  <div class="lab-head"><p class="lockup"><span class="lockup-par"><svg class="marca-golem" viewBox="10.6 2.9 34.5 53.2" aria-hidden="true" focusable="false"><use href="#s-golem" width="64" height="64"/></svg><span class="lockup-g">Golem</span></span> <span class="lockup-lab">Lab</span></p>'
        f'<p class="lab-sub">{t(d["subtitle"], lang)}</p><p class="stamp">{r("taller", lang)}</p></div>',
        f'  <p class="lab-text">{t(d["intro"], lang)}</p>',
        f'  <ul class="doors" role="list">{puertas}</ul>',
        '</div>',
        f'<section class="lab-bloque lab-cifras" aria-labelledby="cifras-t"><h3 class="lab-h" id="cifras-t">{t(q["headline"], lang)}</h3>'
        f'<p class="lab-lead">{t(q["body"], lang)}</p>{cifras(lang, que=False)}'
        f'<div class="que-contamos" id="que-contamos"><div class="panel-contenido" data-panel-titulo="{r("que_contamos", lang)}">'
        f'<p class="pc-alcance">{t(q["metric_scope"], lang)}<br>{t(SH["cutoff"], lang)}</p><dl class="definiciones">{definiciones}</dl></div></div></section>',
        f'<section class="lab-bloque voces" id="voces" aria-labelledby="voces-t"><h3 class="lab-h" id="voces-t">{t(q["quote_caption"], lang)}</h3>'
        f'<p class="lab-lead lab-lead--voz">{t(q["hook"], lang)}</p><p class="voces-nota">{t(F["note"], lang)}</p>'
        f'<div class="voces-lista" data-voces role="list" aria-label="{r("voces_lista", lang)}">{voces}</div></section>',
        f'<section class="lab-bloque supuesto" id="supuesto" aria-labelledby="supuesto-t"><h3 class="lab-h" id="supuesto-t">{t(f4["selection_type"], lang)}</h3>'
        f'{fragmento(f4, lang, True, extra=invitacion)}</section>',
        f'<section class="lab-bloque temas" id="temas" aria-labelledby="temas-t"><h3 class="lab-h" id="temas-t">{r("temas_t", lang)}</h3><ul class="temas-lista" role="list">{temas}</ul></section>',
        f'<section class="lab-bloque fuentes" id="fuentes" aria-labelledby="fuentes-t"><h3 class="lab-h" id="fuentes-t">{r("fuentes_t", lang)}</h3>'
        f'<p class="fuentes-nota">{r("fuentes_nota", lang)} {t(SH["scope"], lang)}</p>'
        + "".join(fuente(FUENTE[x["source_id"]], lang) for x in F["items"]) + "</section>",
        f'<p class="lab-historia">{t(d["historical_note"], lang)}</p>',
    ])


# ---------------------------------------------------------------- cómo medimos

def medimos(lang):
    cards = "".join(
        f'<li class="card"><div class="card-top"><span class="seal"><span class="sr-only">{r("juez", lang)} </span>{j["id"]}</span>'
        f'<span class="card-label">{t(j["short_title"], lang)}</span></div>'
        f'<h4>{t(j["question"], lang)}</h4><p class="card-full">{t(j["full_title"], lang)}</p><p>{t(j["summary"], lang)}</p>'
        f'<p class="card-guarda">{t(j["guardrail"], lang)}</p></li>'
        for j in M["judges"])
    tablas = ""
    for j in M["judges"]:
        filas = "".join(
            f'<tr><th scope="row"><span class="crit-id">{c["id"]}</span> {t(c["name"], lang)}</th><td>{c["weight_within_specialty"]}</td>'
            f'<td>{e(c["evidence"])}</td><td class="{"es-cerrado" if c["ED01_initial_status"] == "closed" else "es-pendiente"}">'
            f'{r("lectura_cerrada", lang) if c["ED01_initial_status"] == "closed" else t(SH["pending"], lang)}</td></tr>'
            for c in j["criteria"])
        tablas += (f'<div class="tabla-caja" role="region" tabindex="0" aria-labelledby="criterios-{j["id"]}"><table class="criterios"><caption id="criterios-{j["id"]}">{j["id"]} · {t(j["full_title"], lang)}</caption>'
                   f'<thead><tr><th scope="col">{r("criterio_col", lang)}</th><th scope="col">{r("peso", lang)}</th>'
                   f'<th scope="col">{r("evidencia", lang)}</th><th scope="col">{r("en_ed01", lang)}</th></tr></thead><tbody>{filas}</tbody></table></div>')
    refs = "".join(f'<div><dt>{j["id"]} · {t(j["short_title"], lang)}</dt><dd>{e(", ".join(j["orientations"][lang]))}</dd></div>' for j in M["judges"])
    anclas = "".join(f'<li><span class="ancla-n">{a["value"]}</span> {t(a["label"], lang)}</li>' for a in M["anchors"])
    ag = M["aggregation"]
    q = Q["como-medimos"]
    n = chr(10) + " " * 12
    return n.join([
        f'<h3 class="sec-titulo sec-titulo--jueces">{e(L(JUECES_T, lang))}</h3>',
        f'<p class="sec-lead">{t(M["roles_vs_engines"], lang)}</p>',
        f'<ul class="cards" role="list">{cards}</ul>',
        f'<p class="alcance">{t(q["current_scope"], lang)}</p>',
        '<div class="desplegables">',
        f'  <details class="desplegable"><summary>{r("criterios_t", lang)}</summary><div class="desplegable-cuerpo">{tablas}</div></details>',
        f'  <details class="desplegable"><summary>{r("referentes_t", lang)}</summary><div class="desplegable-cuerpo"><dl class="referentes">{refs}</dl><p>{t(M["orientations_note"], lang)}</p></div></details>',
        f'  <details class="desplegable"><summary>{r("escala_t", lang)}</summary><div class="desplegable-cuerpo"><ol class="anclas" role="list">{anclas}</ol><p>{t(M["scale_note"], lang)}</p></div></details>',
        f'  <details class="desplegable"><summary>{r("indice_t", lang)}</summary><div class="desplegable-cuerpo"><p>{t(ag["interpretation"], lang)}</p><p>{t(ag["requirements"], lang)}</p><p>{t(P["principles_detail"]["weight_note"], lang)}</p></div></details>',
        f'  <details class="desplegable"><summary>{r("razones_t", lang)}</summary><div class="desplegable-cuerpo"><p>{t(M["anti_agreement_bias"], lang)}</p><p>{t(M["guide_role"], lang)}</p><p>{t(M["independence_limit"], lang)}</p><p>{t(M["fragment_selection_note"], lang)}</p><p>{t(M["evaluation_order"], lang)}</p></div></details>',
        '</div>',
        '<figure class="pull">',
        f'  <blockquote><p>{t(q["hook"], lang)}</p></blockquote>',
        f'  <figcaption class="pull-note">{e(L(PULL_NOTA, lang))}</figcaption>',
        '</figure>',
    ])


# ---------------------------------------------------------------- resultados

def regla(n, lang, criterio):
    pos = "".join(f'<span class="regla-pos{" regla-pos--marca" if v == n else ""}"><span class="regla-n">{v}</span></span>' for v in range(5))
    return f'<div class="regla" role="img" aria-label="{e(r("regla", lang, n=n) + " · " + criterio)}">{pos}</div>'


def dos_lecturas(lang):
    f5 = FRAG[D["fragment_id"]]
    j1, crit = CRIT["J1.1"]
    lecturas = ""
    for lec in D["readings"]:
        n = lec["level"]
        campo = r("campo_" + lec["quote_field"], lang)
        ident = "lectura-" + re.sub(r"[^a-z0-9]+", "-", lec["evaluator"].lower()).strip("-")
        if lang == "es":
            cita = (f'<p class="capa-rotulo">{r("juez_cita", lang)} · {e(campo)}</p>'
                    f'<blockquote class="lectura-cita" data-voz="juez"><p>{t(lec["quote_from_judge"], lang)}</p></blockquote>')
        else:
            cita = (f'<p class="capa-rotulo">{r("juez_trad", lang)} · {e(campo)}</p>'
                    f'<blockquote class="lectura-cita" data-voz="juez"><p>{t(lec["quote_from_judge"], lang)}</p></blockquote>'
                    f'<details class="original"><summary>{t(SH["original_action"], "en")}</summary>'
                    f'<blockquote class="lectura-cita" data-voz="juez" lang="es"><p>{t(lec["quote_from_judge"], "es")}</p></blockquote></details>')
        lecturas += (f'<article class="lectura" aria-labelledby="{ident}">'
                     f'<h4 class="lectura-quien" id="{ident}"><span class="seal seal--chico" aria-hidden="true">{e(lec["evaluator_role"])}</span> '
                     f'<span class="lectura-motor">{e(lec["evaluator"])}</span> <span class="lectura-crit">{r("motor", lang)} · {e(lec["criterion"])}</span></h4>'
                     f'{regla(n, lang, lec["criterion"])}'
                     f'<p class="regla-ancla"><span class="cifra-s">{r("nivel", lang, n=n)}</span> <span aria-hidden="true">·</span> {t(ANCLA[n], lang)}</p>'
                     f'<div class="lectura-juez">{cita}</div>'
                     f'<div class="lectura-guia" data-voz="editorial"><p class="capa-rotulo">{t(SH["editorial_label"], lang)}</p>'
                     f'<p>{t(lec["editorial_explanation"], lang)}</p></div>'
                     f'<p class="lectura-alcance">{t(lec["scope"], lang)}</p></article>')
    trad = f' <span class="f-traduccion">{t(SH["translation_label"], "en")}</span>' if lang == "en" else ""
    return f"""<section class="dos-lecturas" id="dos-lecturas" aria-labelledby="dos-t">
          <p class="eyebrow">{t(D["subheading"], lang)}</p>
          <h3 class="sec-titulo" id="dos-t">{t(D["title"], lang)}</h3>
          <p class="sec-lead">{t(D["intro"], lang)}</p>
          <div class="dl-capas">
            <figure class="dl-pregunta">
              <blockquote class="f-cita" data-voz="modelo"><p>{t(f5["quote"], lang)}</p></blockquote>
              <figcaption class="f-autoria"><span class="f-voz">{t(SH["source_label"], lang)}</span> <span class="f-quien">{e(f5["model_name"])} · {t(f5["configuration"], lang)}</span> <span class="f-caso">{e(f5["case_id"])} · {t(CASO[f5["case_id"]], lang)}</span>{trad}</figcaption>
            </figure>
            <p class="dl-entrega"><a class="f-leer" href="#fuente-{D["source_id"]}" data-panel="fuente-{D["source_id"]}">{r("entrega_completa", lang)}</a></p>
            <div class="dl-criterio"><p class="capa-rotulo">{r("criterio", lang)}</p><p><span class="crit-id">{crit["id"]}</span> {t(crit["name"], lang)}</p><p class="dl-de">{j1["id"]} · {t(j1["short_title"], lang)}: {t(j1["question"], lang)}</p></div>
          </div>
          <div class="dl-lecturas">{lecturas}</div>
          <p class="dl-lector">{t(D["question_to_reader"], lang)}</p>
          <p class="dl-limites">{t(D["limitations"], lang)}</p>
        </section>"""


# ---------------------------------------------------------------- el ranking, dormido
# Se activa solo con un conjunto de resultados liberado oficialmente, en un archivo aparte
# (--ranking RUTA.json), nunca con los campos de espera de este paquete ni porque haya lecturas
# cerradas. La página muestra lo que el conjunto dice, tal cual: no calcula, no promedia, no combina
# motores ni desempata. Forma esperada (✎ propuesta, a confirmar con coordinación):
#   {"status": "released", "comparison_enabled": true, "decision": {"documented": true, "reference": {"es":…,"en":…}},
#    "edition": "ED01", "date": "AAAA-MM-DD",
#    "entries": [{"position": "1", "model_name": "…", "configuration": {"es":…,"en":…},
#                 "index": {"value": "…", "coverage": {"es":…,"en":…}},
#                 "profiles": [{"engine": "…", "J1": "…", "J2": "…", "J3": "…"}, …],
#                 "evidence": {"href": "#…", "label": {"es":…,"en":…}}}, …]}
RANKING = None
CAMPOS_FILA = ("position", "model_name", "configuration", "index", "profiles", "evidence")


def ranking_liberado(x):
    try:
        return (x["status"] == "released" and x["comparison_enabled"] is True and x["decision"]["documented"] is True
                and isinstance(x["entries"], list) and len(x["entries"]) > 0
                and all(all(k in fila for k in CAMPOS_FILA) and fila["profiles"] for fila in x["entries"]))
    except (KeyError, TypeError):
        return False


def ranking(lang):
    q = Q["resultados"]
    fr = q["future_ranking"]
    cols = "".join(f'<th scope="col">{e(c)}</th>' for c in fr["columns"][lang])
    if RANKING is not None and ranking_liberado(RANKING):
        x = RANKING
        filas = ""
        for fila in x["entries"]:
            perfiles = "".join(f'<li><span class="rk-motor">{e(pf["engine"])}</span> J1 {e(pf["J1"])} · J2 {e(pf["J2"])} · J3 {e(pf["J3"])}</li>'
                               for pf in fila["profiles"])
            filas += (f'<tr><th scope="row">{e(fila["position"])}</th>'
                      f'<td><span class="rk-modelo">{e(fila["model_name"])}</span> <span class="rk-conf">{t(fila["configuration"], lang)}</span></td>'
                      f'<td>{e(fila["index"]["value"])} <span class="rk-cobertura">{t(fila["index"]["coverage"], lang)}</span></td>'
                      f'<td><ul class="rk-perfiles" role="list">{perfiles}</ul></td>'
                      f'<td><a href="{e(fila["evidence"]["href"])}">{t(fila["evidence"]["label"], lang)}</a></td></tr>')
        return f"""<section class="ranking ranking--liberado" id="ranking" aria-labelledby="ranking-t">
          <h4 class="sub-titulo" id="ranking-t">{t(fr["headline_when_released"], lang)}</h4>
          <p class="ranking-nota">{t(fr["body_when_released"], lang)} {t(x["decision"]["reference"], lang)}</p>
          <div class="ranking-caja" role="region" tabindex="0" aria-labelledby="ranking-caption">
            <table class="ranking-tabla"><caption id="ranking-caption">{e(x["edition"])} · {e(x["date"])}</caption><thead><tr>{cols}</tr></thead><tbody>{filas}</tbody></table>
          </div>
        </section>"""
    return f"""<section class="ranking" id="ranking" aria-labelledby="ranking-t">
          <h4 class="sr-only" id="ranking-t">{r("ranking_t", lang)}</h4>
          <p class="stamp stamp--estado">{t(q["status_badge"], lang)}</p>
          <div class="ranking-caja" role="region" tabindex="0" aria-labelledby="ranking-caption">
            <table class="ranking-tabla"><caption id="ranking-caption">{e(L(SIN_RANKING, lang))}</caption><thead><tr>{cols}</tr></thead><tbody></tbody></table>
          </div>
          <p class="ranking-nota">{t(M["aggregation"]["requirements"], lang)}</p>
        </section>"""


def resultados(lang):
    q = Q["resultados"]
    filas = ""
    for c in E["cohort"]:
        casos = "".join(
            f'<li><span class="pc-caso">{e(x["case_id"])} · {t(x["case_label"], lang)}</span> '
            f'<span class="pc-estado{"" if x["state"] == "CLOSED" else " pc-estado--fuera"}">{e(r("cerrada", lang) if x["state"] == "CLOSED" else r("fuera", lang))}</span> '
            f'<span class="pc-palabras">{r("palabras", lang)}: {r("limite_palabras", lang, n=x["counted_words"], l=x["word_limit"])}</span></li>'
            for x in E["submissions"] if x["model_id"] == c["id"])
        filas += (f'<li class="cfg"><p class="cfg-nombre">{e(c["name"])}</p>'
                  f'<p class="cfg-conf">{t(c["configuration"], lang)} <span class="cfg-ident">{e(c["artifact_or_service_identifier"])}</span></p>'
                  f'<p class="cfg-estado">{t(c["status_label"], lang)}</p>'
                  f'<details class="cfg-casos"><summary>{r("por_caso", lang)}</summary><ul role="list">{casos}</ul></details></li>')
    fases = "".join(
        f'<li class="fase{" fase--cerrada" if et["status"] == "closed" else ""}{" fase--aparte" if et["id"] == "AR" else ""}">'
        f'<span class="fase-id">{e(et["id"])}</span> <span class="fase-l">{t(et["label"], lang)}</span> <span class="fase-e">{e(estado_etapa(et, lang))}</span>'
        + (f' <span class="fase-alcance">{t(et["scope"], lang)}</span>' if et.get("scope") else "") + "</li>"
        for et in E["stages"])
    adm = E["administrative_summary"]
    limites = "".join(f"<li>{e(x)}</li>" for x in E["limitations"][lang])
    return f"""<section class="sec sec--resultados" id="resultados" aria-labelledby="t-resultados">
      <div class="wrap">
        <h2 class="sr-only" id="t-resultados">{"Resultados de evaluaciones" if lang == "es" else "Evaluation results"}</h2>
        {simbolo("resultados", " simbolo--sala")}
        <p class="eyebrow">{t(SH["cutoff"], lang)}</p>
        <p class="stamp stamp--estado">{t(SH["status"], lang)}</p>
        <h3 class="sec-titulo">{t(q["headline"], lang)}</h3>
        <p class="sec-lead">{t(q["body"], lang)}</p>
        <p class="estado-publico">{t(E["public_status"], lang)}</p>
        <p class="alcance">{t(q["scope"], lang)} {t(SH["scope"], lang)}</p>
        <p class="ir-dos"><a href="#dos-lecturas"><span aria-hidden="true">↓</span> {t(D["cta"], lang)}</a></p>

        <section class="cohorte" aria-labelledby="cohorte-t">
          <h4 class="sub-titulo" id="cohorte-t">{r("cohorte_t", lang)}</h4>
          <p class="cohorte-orden">{r("cohorte_orden", lang)}</p>
          <ul class="cohorte-lista" role="list">{filas}</ul>
          <div class="adm">
            <p class="adm-cifras"><span class="cifra">{adm["within_limit"]}</span> {r("dentro", lang)} <span class="adm-sep" aria-hidden="true">/</span> <span class="cifra">{adm["outside_comparison"]}</span> {r("fuera_c", lang)}</p>
            <p class="adm-label">{t(adm["label"], lang)}</p>
            <p class="adm-exp">{t(adm["explanation"], lang)}</p>
          </div>
        </section>

        <section class="fases" aria-labelledby="fases-t">
          <h4 class="sub-titulo" id="fases-t">{r("fases_t", lang)}</h4>
          <ol class="fases-lista" role="list">{fases}</ol>
          <p class="fases-nota">{e(L(PENDIENTE_NOTA, lang))}</p>
          <p class="fases-orden">{t(M["evaluation_order"], lang)}</p>
        </section>

        {ranking(lang)}

        {dos_lecturas(lang)}

        <section class="limites" aria-labelledby="limites-t">
          <h4 class="sub-titulo" id="limites-t">{r("limites_t", lang)}</h4>
          <ul class="limites-lista" role="list">{limites}</ul>
        </section>
      </div>
    </section>"""


def panel(lang):
    return (f'<dialog class="panel-lectura" id="panel-lectura" aria-labelledby="panel-lectura-t">'
            f'<div class="pl-cabeza"><h2 class="pl-titulo" id="panel-lectura-t">{r("panel", lang)}</h2>'
            f'<button type="button" class="pl-cerrar" data-cerrar>{r("cerrar", lang)}</button></div>'
            f'<div class="pl-cuerpo"></div>'
            f'<p class="pl-error" hidden>{e(L(ERROR_FUENTE, lang))}</p>'
            f'</dialog>')


def placa(lang):
    return f'<p class="placa-estado">{t(SH["status"], lang)}</p>'


BLOQUES = {
    "placa": placa,
    "q-preguntas": lambda l: cuadrante("preguntas", l, "no"),
    "q-laboratorio": lambda l: cuadrante("laboratorio", l, "ne"),
    "q-medimos": lambda l: cuadrante("como-medimos", l, "so"),
    "q-resultados": lambda l: cuadrante("resultados", l, "se"),
    "apuestas": apuestas,
    "lab": lab,
    "medimos": medimos,
    "trailers": trailers,
    "resultados": resultados,
    "panel": panel,
}

if __name__ == "__main__":
    if "--ranking" in sys.argv:
        RANKING = json.loads(Path(sys.argv[sys.argv.index("--ranking") + 1]).read_text(encoding="utf-8"))
        if not ranking_liberado(RANKING):
            sys.exit("El archivo de ranking no es un conjunto liberado: la página sigue con el ranking en preparación.")
    for archivo, lang in ((SITIO / "index.html", "es"), (SITIO / "en" / "index.html", "en")):
        s = archivo.read_text(encoding="utf-8")
        for nombre, fn in BLOQUES.items():
            patron = re.compile(r"<!-- ed01:" + re.escape(nombre) + r" -->.*?<!-- /ed01:" + re.escape(nombre) + r" -->", re.S)
            assert len(patron.findall(s)) == 1, (archivo, nombre)
            s = patron.sub(lambda m: f"<!-- ed01:{nombre} -->{fn(lang)}<!-- /ed01:{nombre} -->", s)
        archivo.write_text(s, encoding="utf-8")
        print(f"{archivo}: {len(BLOQUES)} bloques escritos ({lang})")
