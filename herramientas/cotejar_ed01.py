#!/usr/bin/env python3
"""Coteja la portada con el paquete de coordinación de ED01: cada texto público aparece tal cual en su
idioma, cada cita está en su fuente y en el lugar que dice el paquete, las huellas SHA-256 coinciden,
las cifras son las del paquete y no se cuela nada de las instrucciones ni de los registros internos.

Uso:  python3 -I herramientas/cotejar_ed01.py CARPETA_DEL_PAQUETE site
Sale con código 1 si algo no coincide. El paquete no vive en este repo.
Desde ED02-X1 (19 oct 2026) las esquinas, la cartela y los tráileres son de ED02-X1: aquí se coteja lo que
ED01 sigue publicando en sus salas.
"""
import hashlib, html, json, re, sys
from pathlib import Path

PAQ, SITIO = Path(sys.argv[1]), Path(sys.argv[2])
J = lambda n: json.loads((PAQ / n).read_text(encoding="utf-8"))
P, E, F, S, M, D = (J("01_Portada_ES_EN.json"), J("02_ED01_estado_y_cohorte_ES_EN.json"), J("03_Fragmentos_ES_EN.json"),
                    J("04_Fuentes_A_ES_EN.json"), J("06_Metodo_y_limites_ES_EN.json"), J("07_Un_texto_dos_lecturas_ES_EN.json"))

def texto(html_crudo):
    s = re.sub(r"<script.*?</script>|<style.*?</style>", " ", html_crudo, flags=re.S)
    s = re.sub(r"<br\s*/?>", "\n", s)
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    return re.sub(r"\s+", " ", s)

PAG = {"es": (SITIO / "index.html").read_text(encoding="utf-8"), "en": (SITIO / "en" / "index.html").read_text(encoding="utf-8")}
TXT = {k: texto(v) for k, v in PAG.items()}
fallas, cuenta = [], 0

def debe(lang, valor, donde):
    global cuenta
    cuenta += 1
    v = re.sub(r"\s+", " ", valor).strip()
    if v not in TXT[lang]:
        fallas.append(f"[{lang}] falta {donde}: «{v[:90]}»")

def biling(campo, donde):
    for lang in ("es", "en"):
        debe(lang, campo[lang], donde)

sh = P["shared"]
for k in ("cutoff", "status", "scope", "pending", "source_label", "editorial_label"):
    biling(sh[k], f"shared.{k}")
debe("en", sh["translation_label"]["en"], "shared.translation_label"); debe("en", sh["original_action"]["en"], "shared.original_action (solo junto a la traducción)")
biling(P["brand"]["tagline"], "brand.tagline"); biling(P["brand"]["descriptor"], "brand.descriptor")
# lo que ED01 sigue publicando de cada cuadrante, ahora en sus salas (las esquinas son de ED02-X1)
EN_SALAS = {"laboratorio": ("headline", "body", "hook", "metric_scope", "quote_caption", "quote_cta"),
            "resultados": ("headline", "body", "scope", "status_badge"),
            "como-medimos": ("current_scope", "hook")}
for q in P["quadrants"]:
    for k in EN_SALAS.get(q["id"], ()):
        if k in q: biling(q[k], f"{q['id']}.{k}")
    if "future_ranking" in q:
        for lang in ("es", "en"):
            for c in q["future_ranking"]["columns"][lang]: debe(lang, c, "columna del ranking")
pd = P["principles_detail"]
for k in ("heading", "intro", "weight_note", "replace_existing_training_assumption"): biling(pd[k], f"principios.{k}")
for it in pd["items"]:
    for k in ("title", "text", "prompt"): biling(it[k], f"{it['id']}.{k}")
ld = P["lab_detail"]
for k in ("subtitle", "intro", "historical_note"): biling(ld[k], f"lab.{k}")
for ro in ld["routes"]: biling(ro["name"], "puerta"); biling(ro["body"], "puerta texto")
for th in ld["themes"]: biling(th["label"], "tema")
biling(E["public_status"], "public_status")
for m in E["metrics"]: biling(m["label"], "métrica"); biling(m["definition"], "definición de métrica")
for c in E["cohort"]:
    for lang in ("es", "en"):
        debe(lang, c["name"], "cohorte"); debe(lang, c["artifact_or_service_identifier"], "identificador")
    biling(c["configuration"], "configuración"); biling(c["status_label"], "estado de la cohorte")
a = E["administrative_summary"]; biling(a["label"], "resumen administrativo"); biling(a["explanation"], "explicación administrativa")
for x in E["submissions"]: biling(x["case_label"], "caso")
for st in E["stages"]:
    biling(st["label"], f"fase {st['id']}")
    if "scope" in st: biling(st["scope"], f"fase {st['id']} alcance")
for lang in ("es", "en"):
    for li in E["limitations"][lang]: debe(lang, li, "límite")
biling(F["note"], "nota de selección")
for f in F["items"]:
    for k in ("selection_type", "quote", "context", "editorial_question", "editorial_limit"): biling(f[k], f"{f['id']}.{k}")
    biling(f["configuration"], f"{f['id']} configuración")
for j in M["judges"]:
    for k in ("short_title", "full_title", "question", "summary", "guardrail"): biling(j[k], f"{j['id']}.{k}")
    for lang in ("es", "en"): debe(lang, ", ".join(j["orientations"][lang]), f"{j['id']} referentes")
    for c in j["criteria"]: biling(c["name"], c["id"])
for k in ("roles_vs_engines", "independence_limit", "orientations_note", "anti_agreement_bias", "guide_role", "fragment_selection_note", "scale_note", "evaluation_order"):
    biling(M[k], f"método.{k}")
for an in M["anchors"]: biling(an["label"], f"ancla {an['value']}")
for k in ("requirements", "interpretation"): biling(M["aggregation"][k], f"agregación.{k}")
for k in ("title", "subheading", "intro", "question_to_reader", "limitations", "cta"): biling(D[k], f"dos lecturas.{k}")
for lec in D["readings"]:
    debe("es", lec["quote_from_judge"]["es"], "cita del juez")
    debe("en", lec["quote_from_judge"]["en"], "cita del juez (traducción)")
    debe("en", lec["quote_from_judge"]["es"], "cita del juez (original junto a la traducción)")
    biling(lec["editorial_explanation"], "explicación editorial"); biling(lec["scope"], "alcance de la lectura")

# las fuentes: el texto completo (sin las marcas de énfasis), su huella y la cita en su sitio
for s_ in S["sources"]:
    f = next(x for x in F["items"] if x["source_id"] == s_["id"])
    huella = hashlib.sha256(s_["text"]["es"].encode("utf-8")).hexdigest()
    cuenta += 1
    if huella != s_["original_utf8_sha256"] or huella != f["source_content_sha256"]: fallas.append(f"huella de {s_['id']}")
    if hashlib.sha256(s_["text"]["en"].encode("utf-8")).hexdigest() != s_["english_utf8_sha256"]: fallas.append(f"huella EN de {s_['id']}")
    sp = f["source_span"]
    cuenta += 1
    if s_["text"]["es"][sp["start_inclusive"]:sp["end_exclusive"]] != f["quote"]["es"] or s_["text"]["es"].count(f["quote"]["es"]) != 1:
        fallas.append(f"la cita {f['id']} no está en su sitio")
    if s_["text"]["en"].count(f["quote"]["en"]) != 1: fallas.append(f"la traducción de {f['id']} no aparece una vez en la traducción completa")
    for lang, pags in (("es", ("es", "en")), ("en", ("en",))):
        plano = re.sub(r"\*\*?", "", s_["text"][lang])
        for par in re.split(r"\n\s*\n", plano.strip()):
            for renglon in par.split("\n"):
                if renglon.strip():
                    for pg in pags: debe(pg, renglon.strip(), f"fuente {s_['id']} ({lang})")
    for lang in ("es", "en"):
        cuenta += 1
        if s_["original_utf8_sha256"] not in PAG[lang]: fallas.append(f"[{lang}] no se muestra la huella de {s_['id']}")
        biling(s_["notice"], "aviso de la fuente")
    # en la ficha, la cita va marcada dentro del texto completo
    for lang in ("es", "en"):
        cuenta += 1
        marca = html.escape(f["quote"][lang], quote=False)
        if f'<mark class="cita-en-fuente">{marca}</mark>' not in PAG[lang]:
            fallas.append(f"[{lang}] la cita {f['id']} no va marcada en su fuente")

# las cifras de la portada son las del paquete
for lang in ("es", "en"):
    for m in E["metrics"]:
        cuenta += 1
        if f'<span class="cifra">{m["value"]}</span> <span class="cifra-l">{html.escape(m["label"][lang])}</span>' not in PAG[lang]:
            fallas.append(f"[{lang}] cifra {m['value']}")

# nada de lo que es instrucción o control interno
# lo interno se lee del propio paquete: las huellas de registros que no se publican, las primeras líneas
# de cada archivo de instrucciones y los nombres de campos de control
def huellas_internas(x, claves=("source_snapshot_sha256", "judge_record_receipt_sha256")):
    if isinstance(x, dict):
        for k, v in x.items():
            if k in claves and isinstance(v, str): yield v
            else: yield from huellas_internas(v, claves)
    elif isinstance(x, list):
        for v in x: yield from huellas_internas(v, claves)
prohibidos = ["/Users/", "/home/", "scratchpad", "source_snapshot_sha256", "judge_record_receipt_sha256", "editorial_semantic_review",
              "fixed_model_id_not_rank", "activation_rule"]
for n in ("01_Portada_ES_EN.json", "02_ED01_estado_y_cohorte_ES_EN.json", "03_Fragmentos_ES_EN.json", "04_Fuentes_A_ES_EN.json",
          "06_Metodo_y_limites_ES_EN.json", "07_Un_texto_dos_lecturas_ES_EN.json", "VERIFICACION.json"):
    prohibidos += [h[:16] for h in huellas_internas(J(n))]
for n in ("00_Mensaje_para_Claude.txt", "05_Direccion_visual_y_estados.txt", "LEEME.txt"):
    lineas = [l.strip() for l in (PAQ / n).read_text(encoding="utf-8").splitlines() if len(l.strip()) > 24]
    prohibidos += [l[:40] for l in lineas[:3]]
for lang in ("es", "en"):
    for x in prohibidos:
        cuenta += 1
        if x in PAG[lang]: fallas.append(f"[{lang}] aparece «{x}»")

avisos = []
for lang in ("es", "en"):
    for palabra in ("paquete", "package"):
        if re.search(r"\b" + palabra + r"\b", TXT[lang], re.I):
            i = re.search(r"\b" + palabra + r"\b", TXT[lang], re.I).start()
            avisos.append(f"[{lang}] «…{TXT[lang][max(0, i - 60):i + 30]}…»")

print(f"{cuenta} cotejos · {len(fallas)} fallas")
for x in fallas: print("  ✗", x)
for x in avisos: print("  aviso:", x)
sys.exit(1 if fallas else 0)
