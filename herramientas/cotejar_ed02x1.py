#!/usr/bin/env python3
"""Coteja la portada y las páginas de lectura con el paquete público de ED02-X1.

Uso:  python3 -I herramientas/cotejar_ed02x1.py CARPETA_DEL_PAQUETE site
Sale con código 1 si algo no coincide. El paquete no vive en este repo.

Comprueba, sin usar el código que construye las páginas:
  · que cada archivo del paquete tiene la huella del manifiesto;
  · que el índice cuadra: 2 configuraciones, 12 recorridos, 60 textos, 24 críticas, 144 lecturas, 384 niveles;
  · que los textos editoriales, las notas y las cifras aparecen tal cual y en su idioma, y la etiqueta
    «Piloto exploratorio · ED02-X1» a la vista; que ninguna cifra del índice lleva «%»;
  · que cada página de recorrido trae sus cinco textos completos, sus dos críticas, sus 32 lecturas con el
    nivel, la justificación y el límite de cada una, y cada pasaje citado en su sitio y con todos sus vínculos;
  · que cada pasaje del carrusel abre su fuente correcta (recorrido, etapa y bytes);
  · que ninguna referencia no promovida se destaca, y que en inglés los cuerpos siguen en español original;
  · que nada de ED01, IA-01 o la app se cuela en las piezas de ED02-X1, ni nada interno del paquete.
"""
import collections
import hashlib
import html
import json
import re
import sys
from pathlib import Path

PAQ, SITIO = Path(sys.argv[1]), Path(sys.argv[2])
fallas, cuenta = [], 0


def ok(cond, msg):
    global cuenta
    cuenta += 1
    if not cond:
        fallas.append(msg)
    return cond


def leer(rel):
    return json.loads((PAQ / rel).read_text(encoding="utf-8"))


def plano(h):
    """El texto de un trozo de HTML, como lo lee una persona."""
    s = re.sub(r"<script.*?</script>|<style.*?</style>|<template.*?</template>", " ", h, flags=re.S)
    s = re.sub(r"<br\s*/?>", "\n", s)
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def sin_asteriscos(s, al_comienzo_de_linea=False):
    """Una cita sin sus marcas de énfasis (puede cortar un énfasis por la mitad: sus marcas quedan sueltas).
    Si empieza donde empieza un renglón, su marca de lista o de título tampoco se muestra."""
    if al_comienzo_de_linea:
        s = re.sub(r"^(?:#{1,6} |[-•] |\d+[.)] )", "", s)
    return norm(s.replace("*", ""))


def sin_marcas(s):
    """Un texto del participante sin las marcas de formato que la página no muestra (énfasis, listas, títulos)."""
    s = re.sub(r"(?m)^\s*(?:#{1,6} |[-*•] |\d+[.)] )", "", s)
    s = s.replace("**", "")
    s = re.sub(r"(?<![\w*])\*(?!\s)([^*\n]+?)(?<!\s)\*(?![\w*])", r"\1", s)
    return norm(s)


# ---------------------------------------------------------------- 1. el paquete, con sus huellas
MAN = leer("manifiesto_publico_X1.json")
for rel, info in MAN["files"].items():
    b = (PAQ / rel).read_bytes()
    ok(hashlib.sha256(b).hexdigest() == info["sha256"] and len(b) == info["bytes"], f"huella del paquete: {rel}")
ok(MAN["private_files_copied"] == 0 and MAN["models_called"] == 0 and MAN["local_paths_exported"] is False, "manifiesto: nada privado")

IDX = leer("indice_publico_X1.json")
WEB = leer("editorial/Contenido_web_X1_ES_EN.json")
MAPA = leer("editorial/Mapa_editorial_casos_y_jueces_X1_ES_EN.json")
NOTA = leer("editorial/Nota_publica_incidentes_ES_EN_X1.json")
FRAG = leer("fragmentos_citados.json")["items"]
DIAG = leer("diagnostico_citas_no_promovidas.json")["items"]
A = IDX["arithmetic"]
TRAY = IDX["trajectories"]

# ---------------------------------------------------------------- 2. el índice cuadra
ok(len([c for c in A["configuration_register"] if c["admitted_to_execution"]]) == 2, "2 configuraciones admitidas")
ok(len(TRAY) == 12 == IDX["counts"]["trajectories"], "12 recorridos")
ok(sum(len(t["visible_texts"]) for t in TRAY) == 60 == IDX["counts"]["visible_texts"], "60 textos")
ok(sum(len(t["critiques"]) for t in TRAY) == 24 == IDX["counts"]["critiques"], "24 críticas")
lecturas = [l for t in TRAY for l in t["public_judge_readings"]]
ok(len(lecturas) == 144 == IDX["counts"]["selected_judge_bodies"], "144 lecturas")
CUERPO = {l["id"]: leer(l["public_selected_body"]["file"]) for l in lecturas}
niveles = sum(len(c["criterios"]) for c in CUERPO.values())
ok(niveles == 384 == A["required_common_panel"]["numeric_levels"] == IDX["counts"]["original_levels"] + IDX["counts"]["supplemental_levels"], f"384 niveles (hay {niveles})")
ok(len(A["sensitivity_runs"]) == 42, "42 escenarios")
ok(len(FRAG) == IDX["counts"]["verified_cited_fragments"], "registros de cita")
estrictos = sum(1 for t in TRAY for v in t["visible_texts"].values() if v["strict_ED02_accepted"])
ok(estrictos == 59 == IDX["counts"]["strict_ED02_accepted_texts"], "59 textos admitidos estrictamente")

# ---------------------------------------------------------------- 3. la portada
PAG = {"es": (SITIO / "index.html").read_text(encoding="utf-8"), "en": (SITIO / "en" / "index.html").read_text(encoding="utf-8")}


def bloques_x1(h):
    return "".join(m.group(1) for m in re.finditer(r"<!-- x1:[a-z-]+ -->(.*?)<!-- /x1:[a-z-]+ -->", h, re.S))


X1 = {k: bloques_x1(v) for k, v in PAG.items()}
TX = {k: plano(v) for k, v in X1.items()}


def debe(lang, valor, donde, en=None):
    v = norm(valor)
    ok(v in (en if en is not None else TX[lang]), f"[{lang}] falta {donde}: «{v[:80]}»")


for lang in ("es", "en"):
    w = WEB[lang]
    for k in ("headline", "badge", "ranking_title", "ranking_note", "sensitivity_note", "scope", "length_note", "judges_note",
              "question_note", "bias_note", "originality_note", "language_note"):
        debe(lang, w[k], k)
    for q, d in w["quadrants"].items():
        for k in ("title", "preview", "cta"):
            debe(lang, d[k], f"{q}.{k}")
    for c in MAPA["cases"]:
        debe(lang, c["title_" + lang], f"caso {c['id']}")
        debe(lang, c["preview_" + lang], f"caso {c['id']} vista previa")
    for p in MAPA["perspectives"]:
        debe(lang, p["title_" + lang], f"especialidad {p['id']}")
        debe(lang, p["preview_" + lang], f"especialidad {p['id']} vista previa")
    debe(lang, MAPA["question_priority"][lang], "prioridad de las preguntas")
    debe(lang, MAPA["case_status"][lang], "estado de los casos")
    debe(lang, NOTA[lang]["title"], "título de la nota de incidencias")
    debe(lang, NOTA[lang]["text"], "nota de incidencias completa")
    debe(lang, WEB["profiles_note"][lang], "nota de los perfiles")
    # la etiqueta del piloto: en la cartela de la placa y a la vista en resultados
    badge = html.escape(WEB[lang]["badge"])
    ok(f'<p class="placa-estado">{badge}</p>' in PAG[lang], f"[{lang}] la cartela de la placa no dice {WEB[lang]['badge']}")
    sec = re.search(r'<section class="sec sec--resultados sec--x1" id="resultados".*?</section>\s*<!-- /x1:resultados -->', PAG[lang], re.S)
    ok(sec and badge in sec.group(0), f"[{lang}] la sala de resultados no lleva la etiqueta del piloto")

# las cifras: la tabla del orden condicional, fila por fila, en el orden del índice
for lang in ("es", "en"):
    f = (lambda x: f"{x:.1f}".replace(".", ",")) if lang == "es" else (lambda x: f"{x:.1f}")
    tabla = re.search(r'<table class="x1-tabla">.*?</table>', PAG[lang], re.S)
    ok(tabla, f"[{lang}] falta la tabla del orden condicional")
    if tabla:
        filas = re.findall(r"<tr><th scope=\"row\" class=\"x1-pos\">(\d)</th>(.*?)</tr>", tabla.group(0), re.S)
        ok(len(filas) == 2, f"[{lang}] la tabla no tiene dos filas")
        for (pos, cuerpo), rr in zip(filas, sorted(WEB["rank_rows"], key=lambda x: x["position_in_primary_index"])):
            celdas = re.findall(r'<td class="x1-num[^"]*">([\d.,]+)', cuerpo)
            ok(pos == str(rr["position_in_primary_index"]) and rr["model"] in cuerpo, f"[{lang}] fila {pos}: modelo u orden")
            ok(celdas == [f(rr["primary_index"]), f(rr["judge_GPT_index"]), f(rr["judge_Claude_index"])],
               f"[{lang}] fila {pos}: cifras {celdas}")
        ok(A["primary_comparison"]["scores"]["M04"]["exact"] in tabla.string and A["primary_comparison"]["scores"]["M03"]["exact"] in PAG[lang],
           f"[{lang}] faltan los valores exactos")
    # ninguna cifra del índice como porcentaje
    for v in (86.2, 82.7, 95.3, 87.1, 78.3, 77.1):
        ok(not re.search(re.escape(f(v)) + r"\s*%", X1[lang]), f"[{lang}] {f(v)} aparece como porcentaje")
    for palabra in ("ganador", "ganó", "winner", "won ", "campeón", "champion"):
        ok(palabra not in TX[lang].lower(), f"[{lang}] aparece «{palabra}»")
    # los 42 escenarios, partidos por motor, como dice el índice
    rej = re.findall(r'<ul class="esc-rejilla"[^>]*>(.*?)</ul>', X1[lang], re.S)
    ok(len(rej) == 2, f"[{lang}] faltan las dos rejillas de escenarios")
    for motor, cel in zip(("JG", "JC"), rej):
        esperado = ["m04" if r["ranks"]["M04"] == 1 else "m03" for r in sorted((x for x in A["sensitivity_runs"] if x["engine"] == motor),
                                                                              key=lambda x: (x["weight_variant"], x["recoding_variant"]))]
        ok(re.findall(r'class="esc esc--(m0[34])"', cel) == esperado, f"[{lang}] escenarios del motor {motor}")
    # las cuatro unidades del laboratorio
    for n, k in ((12, "trajectories"), (60, "visible_texts"), (24, "critiques"), (144, "selected_judge_bodies")):
        ok(f'<span class="cifra">{n}</span>' in X1[lang] and IDX["counts"][k] == n, f"[{lang}] unidad {n}")
    # fuera del índice: sin cifra
    fuera = re.search(r'<ul class="x1-fuera-lista".*?</ul>', X1[lang], re.S)
    ok(fuera and not re.search(r"\d+[.,]\d", plano(fuera.group(0))) and "Gemini" in fuera.group(0), f"[{lang}] fuera del índice: sin cifras y con Gemini")
    # nada de otras series ni de lo interno
    for x in ("ED01", "IA-01", "Mensaje_para_Claude", "/home/", "scratchpad", "EXPERIMENTAL_CON_DESVIACIONES", "source_aggregation_sha256"):
        ok(x not in X1[lang], f"[{lang}] en las piezas de ED02-X1 aparece «{x}»")

# las frases del resumen que se citan, tal cual
RES = (PAQ / "editorial/Resumen_resultados_X1_ES_EN.txt").read_text(encoding="utf-8")
for lang in ("es", "en"):
    for m in re.finditer(r'<p class="x1-fuera-nota">(.*?)</p>', X1[lang], re.S):
        ok(norm(html.unescape(m.group(1))) in norm(RES), f"[{lang}] nota de no admitidas no es del resumen")

# ---------------------------------------------------------------- 4. los recorridos
# un pasaje es una frase visible en su fuente y su etapa: la misma, citada con o sin las marcas de énfasis
# de sus bordes, cuenta una vez y conserva todos sus vínculos
GRUPOS = collections.defaultdict(list)
for it in FRAG:
    o, q = it["exact_occurrences_utf8"][0], it["quote_es"]
    ini, fin = o["start_byte"] + len(q) - len(q.lstrip("*")), o["end_byte"] - (len(q) - len(q.rstrip("*")))
    GRUPOS[(it["source_file"], it["source_final_phase"], ini, fin)].append(it)
VISIBLE = {k: (PAQ / k[0]).read_bytes()[k[2]:k[3]].decode("utf-8") for k in GRUPOS}
NO_PROM = {(x["judgment_id"], x["criterion_pointer"]) for x in DIAG}
ok(not NO_PROM & {(x["judgment_id"], x["criterion_pointer"]) for x in FRAG}, "una cita no promovida figura entre las verificadas")
total_pasajes = 0


def pid(fase, ini, fin):
    return f"p-{fase.lower()}-{ini}-{fin}"


for lang in ("es", "en"):
    raiz = SITIO / ("" if lang == "es" else "en") / "ed02-x1"
    for t in TRAY:
        slug = t["id"].removeprefix("ED02-").lower()
        archivo = raiz / slug / "index.html"
        if not ok(archivo.is_file(), f"[{lang}] falta la página de {t['id']}"):
            continue
        h = archivo.read_text(encoding="utf-8")
        donde = f"[{lang}] {t['id']}"
        ok(html.escape(WEB[lang]["badge"]) in h, f"{donde}: sin la etiqueta del piloto")
        ok(f'<html lang="{lang}">' in h, f"{donde}: idioma de la página")
        # los cinco textos, completos y en español original
        for fase, info in t["visible_texts"].items():
            raw = (PAQ / info["file"]).read_text(encoding="utf-8")
            m = re.search(r'<div class="rc-texto" data-voz="modelo" data-fase="' + fase + r'" lang="es">(.*?)</div></div>', h, re.S)
            if not ok(m, f"{donde}: falta el texto {fase}"):
                continue
            ok(plano(m.group(1)).replace(" ", "") == sin_marcas(raw).replace(" ", ""), f"{donde}: el texto {fase} no es el original")
            ok(info["sha256"] in h, f"{donde}: falta la huella de {fase}")
            ok(f'{info["words"]} ' in plano(h), f"{donde}: faltan las palabras de {fase}")
            # cada pasaje en su sitio: los tramos con su ancla dicen exactamente la cita
            tramos = re.findall(r'<span class="cita" data-p="([^"]+)">([^<]*)</span>', m.group(1))
            for (fuente, ph, ini, fin), regs in GRUPOS.items():
                if fuente != info["file"]:
                    continue
                total_pasajes += lang == "es"
                p = pid(ph, ini, fin)
                visto = "".join(html.unescape(tx) for ids, tx in tramos if p in ids.split())
                crudo_src = (PAQ / fuente).read_bytes()
                linea = ini == 0 or crudo_src[ini - 1:ini] == b"\n"
                ok(norm(visto).replace(" ", "") == sin_asteriscos(VISIBLE[(fuente, ph, ini, fin)], linea).replace(" ", ""),
                   f"{donde}: el pasaje {p} no dice su cita")
                ok(all(sin_asteriscos(x["quote_es"]).replace(" ", "") == sin_asteriscos(VISIBLE[(fuente, ph, ini, fin)]).replace(" ", "") for x in regs),
                   f"{donde}: el pasaje {p} reúne citas distintas")
                ancla = re.search(r'<span class="p-a" id="' + p + r'" data-cita="([^"]*)"></span>', m.group(1))
                if ok(ancla, f"{donde}: falta el ancla {p}"):
                    vinc = set(ancla.group(1).split())
                    for x in regs:
                        crit, rol = re.match(r"^/criterios/(J\d\.\d)/(evidencias|procedencia|alertas)/", x["criterion_pointer"]).groups()
                        motor = x["judgment_id"].rsplit("_", 1)[1].lower()
                        ok(f"j-{motor}-{crit.lower().replace('.', '-')}:{rol[0]}" in vinc, f"{donde}: {p} perdió un vínculo de juez y criterio")
        # las dos críticas
        for rama, info in t["critiques"].items():
            raw = (PAQ / info["file"]).read_text(encoding="utf-8")
            ok(sin_marcas(raw).replace(" ", "") in plano(h).replace(" ", ""), f"{donde}: la crítica {rama} no está completa")
        # las 32 lecturas: nivel, justificación y límite de cada motor en cada criterio
        juicios = dict(re.findall(r'<article class="juicio juicio--j[gc]" id="(j-j[gc]-j\d-\d)" data-voz="juez".*?>(.*?)</article>', h, re.S))
        ok(len(juicios) == 32, f"{donde}: hay {len(juicios)} lecturas, no 32")
        for l in t["public_judge_readings"]:
            for crit, c in CUERPO[l["id"]]["criterios"].items():
                jid = f"j-{l['engine'].lower()}-{crit.lower().replace('.', '-')}"
                cuerpo = juicios.get(jid, "")
                txt = plano(cuerpo)
                nivel = f"Nivel {c['nivel']} de 4" if lang == "es" else f"Level {c['nivel']} of 4"
                ok(nivel in txt, f"{donde}: {jid} no muestra su nivel")
                ok(norm(c["justificacion_publica"]) in txt, f"{donde}: {jid} sin su justificación")
                if c["limite_o_carencia"]:
                    ok(norm(c["limite_o_carencia"]) in txt, f"{donde}: {jid} sin su límite")
                else:   # el dictamen no registra límite: la página lo dice, sin inventarlo
                    ok('<p class="j-vacio">' in cuerpo, f"{donde}: {jid} no dice que el dictamen no registra límite")
                ok(l["public_selected_body"]["sha256"] in cuerpo, f"{donde}: {jid} sin la huella de su cuerpo")
                # las citas no promovidas no se destacan ni enlazan
                for k, ev in enumerate(c.get("evidencias") or []):
                    if (l["id"], f"/criterios/{crit}/evidencias/{k}") in NO_PROM and ev.get("cita"):
                        otras = [plano(x) for x in re.findall(r'<li class="ref-otra"><q lang="es">(.*?)</q>', cuerpo, re.S)]
                        ok(sin_asteriscos(ev["cita"]).replace(" ", "") in [x.replace(" ", "") for x in otras], f"{donde}: {jid} destaca una cita no promovida")
        # los enlaces a pasajes llevan a un pasaje de la misma página
        ids = set(re.findall(r'id="(p-[a-z0-9]+-\d+-\d+)"', h))
        for destino in set(re.findall(r'data-ir-pasaje="([^"]+)"', h)):
            ok(destino in ids, f"{donde}: enlace a un pasaje que no existe ({destino})")
        # en inglés: la interfaz cambia, los cuerpos no
        if lang == "en":
            ok("Spanish original · not translated" in h, f"{donde}: sin la nota del original")
        # el texto de 351 palabras lleva su aviso
        e = t["visible_texts"]["E"]
        if not e["strict_ED02_accepted"]:
            ok(e["words"] == 351 and norm(html.escape(WEB[lang]["length_note"])) in norm(h), f"{donde}: la transferencia de 351 palabras sin su aviso")
ok(total_pasajes == len(GRUPOS) == 1222, f"pasajes distintos en las páginas: {total_pasajes}")

# en inglés, cada cuerpo del modelo y del juez sigue marcado como español
for f in (SITIO / "en" / "ed02-x1").rglob("index.html"):
    h = f.read_text(encoding="utf-8")
    for m in re.finditer(r'<div class="rc-texto"[^>]*>', h):
        ok('lang="es"' in m.group(0), f"[en] {f.parent.name}: un texto del modelo sin lang=es")
    for m in re.finditer(r'<div class="j-campo[^"]*"><p class="j-rot">[^<]*</p><p( lang="es")?>', h):
        ok(m.group(1), f"[en] {f.parent.name}: un campo del juez sin lang=es")

# ---------------------------------------------------------------- 5. el carrusel: cada pasaje abre su fuente
QUOTE = {pid(ph, ini, fin): VISIBLE[(src, ph, ini, fin)] for (src, ph, ini, fin) in GRUPOS}
FUENTE_DE = {pid(ph, ini, fin): src for (src, ph, ini, fin) in GRUPOS}
for lang in ("es", "en"):
    tpl = re.search(r'<template id="x1-pasajes">(.*?)</template>', PAG[lang], re.S)
    if not ok(tpl, f"[{lang}] falta la plantilla del carrusel"):
        continue
    tarjetas = re.findall(r'<div class="fragmento fragmento--x1" data-fragmento="([a-z0-9-]+):(p-[a-z0-9]+-\d+-\d+)">(.*?)</figure></div>', tpl.group(1), re.S)
    ok(len(tarjetas) == 60, f"[{lang}] el carrusel tiene {len(tarjetas)} pasajes")
    fuentes = set()
    for slug, p, cuerpo in tarjetas:
        src = FUENTE_DE.get(p, "")
        fuentes.add(src)
        ok(src.startswith(f"textos/ED02-{slug.upper()}/"), f"[{lang}] {p} no es de {slug}")
        cita = re.search(r'<blockquote class="f-cita" data-voz="modelo" lang="es"><p>(.*?)</p></blockquote>', cuerpo, re.S)
        k = next(k for k in GRUPOS if pid(k[1], k[2], k[3]) == p and k[0] == src) if src else None
        linea = bool(k) and (k[2] == 0 or (PAQ / src).read_bytes()[k[2] - 1:k[2]] == b"\n")
        ok(cita and plano(cita.group(1)).replace(" ", "") == sin_asteriscos(QUOTE.get(p, "?"), linea).replace(" ", ""), f"[{lang}] {p}: la cita no es la del juez")
        url = ("/" if lang == "es" else "/en/") + f"ed02-x1/{slug}/#{p}"
        ok(f'href="{url}" data-x1-pasaje="{url}"' in cuerpo, f"[{lang}] {p}: «Leer en contexto» no lleva a su recorrido")
        ok(60 <= len(QUOTE.get(p, "")) <= 240, f"[{lang}] {p}: fuera de la regla de 60 a 240 caracteres")
        # la regla: el primero que se citó en su texto, entre los de 60 a 240
        cand = sorted((ini, fin) for (s, ph, ini, fin) in GRUPOS if s == src and 60 <= len(VISIBLE[(s, ph, ini, fin)]) <= 240)
        primero = min(cand, key=lambda x: (len((PAQ / src).read_bytes()[:x[0]].decode("utf-8")), x[1])) if cand else None
        ok(primero and p.endswith(f"-{primero[0]}-{primero[1]}"), f"[{lang}] {p}: no es el primer pasaje citado de su texto")
    ok(len(fuentes) == 60, f"[{lang}] el carrusel no cubre los 60 textos")

# ---------------------------------------------------------------- 6. método y materiales
for lang in ("es", "en"):
    f = SITIO / ("" if lang == "es" else "en") / "ed02-x1" / "metodo" / "index.html"
    if not ok(f.is_file(), f"[{lang}] falta la página de método"):
        continue
    h = f.read_text(encoding="utf-8")
    ok(norm(NOTA[lang]["text"]) in plano(h), f"[{lang}] método: la nota de incidencias no está completa")
    for rel in ("materiales_comunes/RUBRICA.txt", "materiales_comunes/GUIA.txt", "materiales_comunes/COND.txt", "materiales_comunes/CONS_A.txt",
                "materiales_comunes/CONS_B.txt", "materiales_comunes/CONS_R1.txt", "materiales_comunes/CONS_E.txt"):
        raw = (PAQ / rel).read_text(encoding="utf-8")
        ok(sin_marcas(raw).replace(" ", "") in plano(h).replace(" ", ""), f"[{lang}] método: {rel} no está completo")
    for v in IDX["methodology"][lang].values():
        ok(norm(v) in plano(h), f"[{lang}] método: falta «{v[:60]}»")

avisos = []
for lang in ("es", "en"):
    for palabra in ("paquete", "package"):
        m = re.search(r"\b" + palabra + r"\b", TX[lang], re.I)
        if m:
            avisos.append(f"[{lang}] «…{TX[lang][max(0, m.start() - 60):m.start() + 30]}…»")

print(f"{cuenta} cotejos · {len(fallas)} fallas")
for x in fallas[:60]:
    print("  ✗", x)
if len(fallas) > 60:
    print(f"  … y {len(fallas) - 60} más")
for x in avisos:
    print("  aviso:", x)
sys.exit(1 if fallas else 0)
