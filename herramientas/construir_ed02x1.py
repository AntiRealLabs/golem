#!/usr/bin/env python3
"""Escribe ED02-X1 en la portada y sus páginas de lectura a partir del paquete público de coordinación.

Uso:  python3 -I herramientas/construir_ed02x1.py CARPETA_DEL_PAQUETE site

El paquete (Golem_Bench_ED02_X1_publico_para_Claude) no vive en este repo. Este script:
  1. Comprueba la huella SHA-256 de cada archivo que lee contra manifiesto_publico_X1.json, y que el
     índice cuadra (2 configuraciones, 12 recorridos, 60 textos, 24 críticas, 144 lecturas, 384 niveles).
  2. Escribe los bloques <!-- x1:NOMBRE --> … <!-- /x1:NOMBRE --> de site/index.html y site/en/index.html:
     la cartela de la placa, las cuatro esquinas, los tráileres del celular y las partes de ED02-X1 en
     Resultados, Laboratorio y Cómo medimos. Lo que hay entre marcadores no se edita a mano.
  3. Escribe una página por recorrido (site/ed02-x1/m03-c01-r1/ y site/en/ed02-x1/…) con los cinco textos,
     las dos críticas, el caso y las 32 lecturas de los dos motores, y la página de método y materiales.

Los textos del paquete pasan tal cual (escapados para HTML): los del modelo, los de los jueces, los
materiales y los editoriales. Nada se traduce aquí: en inglés cambian la interfaz y las explicaciones
editoriales del paquete; los cuerpos siguen en español original. Lo único escrito en este archivo son
los rótulos funcionales de ROT y las notas de N (✎ propuesta de Claude; las aprueba coordinación).
Los textos editoriales que una revisión aprobada cambió viven en ed02x1_ajustes.json, con su origen:
ese archivo dice qué texto del paquete reemplaza cada uno.
No calcula notas, órdenes ni promedios: muestra las cifras del índice con su redondeo publicado. Cuenta
(registros, pasajes distintos) solo para decir qué se muestra, nunca para puntuar.
Después de correrlo: versionar_recursos.py, cotejar_ed02x1.py y verificar_portada.py.
"""
import collections
import hashlib
import html
import json
import re
import sys
from pathlib import Path

PAQ, SITIO = Path(sys.argv[1]), Path(sys.argv[2])
EDICION = "ED02-X1"
CARPETA = "ed02-x1"


# ---------------------------------------------------------------- el paquete, con sus huellas

MANIFIESTO = json.loads((PAQ / "manifiesto_publico_X1.json").read_text(encoding="utf-8"))["files"]


def crudo(rel):
    """Los bytes de un archivo del paquete, después de comprobar su huella en el manifiesto."""
    b = (PAQ / rel).read_bytes()
    esperado = MANIFIESTO[rel]
    assert hashlib.sha256(b).hexdigest() == esperado["sha256"] and len(b) == esperado["bytes"], f"huella distinta: {rel}"
    return b


def texto(rel):
    return crudo(rel).decode("utf-8")


def leer(rel):
    return json.loads(texto(rel))


IDX = leer("indice_publico_X1.json")
WEB = leer("editorial/Contenido_web_X1_ES_EN.json")
# los textos de la revisión de la portada (20 oct 2026): viven fuera del paquete, con su origen
_AJ = json.loads((Path(__file__).resolve().parent / "ed02x1_ajustes.json").read_text(encoding="utf-8"))
AJUSTES = _AJ["textos"]
# el resumen de las baldosas del celular: los principios en una palabra (una de cada apuesta, tal cual en su título)
PRINCIPIOS = _AJ["resumen_movil"]["principios"]
assert all(len(PRINCIPIOS[l]) == 6 for l in ("es", "en"))
MAPA = leer("editorial/Mapa_editorial_casos_y_jueces_X1_ES_EN.json")
NOTA = leer("editorial/Nota_publica_incidentes_ES_EN_X1.json")
RESUMEN = texto("editorial/Resumen_resultados_X1_ES_EN.txt")
FRAG = leer("fragmentos_citados.json")
DIAG = leer("diagnostico_citas_no_promovidas.json")
REFS = leer("mapa_referencias_lecturas.json")

A = IDX["arithmetic"]
assert IDX["edition_id"] == EDICION and A["edition_id"] == EDICION
assert IDX["strict_protocol_conformance"] is False and IDX["original_strict_ED02_complete"] is False
assert A["human_validation"] is False and WEB["human_validation"] is False and WEB["scores_are_accuracy_percentages"] is False
assert WEB["primary_order_is_robust"] is False and A["robust_pairs"] == [] and A["sensitivity_is_confidence_interval"] is False
CTA = IDX["counts"]
PANEL = A["required_common_panel"]
TRAY = IDX["trajectories"]
assert len(TRAY) == CTA["trajectories"] == PANEL["slots"] == 12
assert PANEL["configurations"] == CTA["ranked_configurations"] == 2 and PANEL["numeric_levels"] == 384
assert CTA["original_levels"] + CTA["supplemental_levels"] == 384
assert sum(len(t["visible_texts"]) for t in TRAY) == CTA["visible_texts"] == 60
assert sum(len(t["critiques"]) for t in TRAY) == CTA["critiques"] == 24
assert sum(len(t["public_judge_readings"]) for t in TRAY) == CTA["selected_judge_bodies"] == 144
assert len(FRAG["items"]) == CTA["verified_cited_fragments"]
assert len(A["sensitivity_runs"]) == A["sensitivity_runs_required"] == CTA["sensitivity_orders"] == 42

CRIT = {c["id"]: c for c in IDX["criteria"]}
assert len(CRIT) == 16
CASO = {c["id"]: c for c in MAPA["cases"]}
IDX_CASO = {c["id"]: c["materials"] for c in IDX["cases"]}
assert sorted(CASO) == sorted(IDX_CASO) == ["ED02-C01", "ED02-C02", "ED02-C03"]
PERSP = {p["id"]: p for p in MAPA["perspectives"]}
REGISTRO = {c["configuration"]: c for c in A["configuration_register"]}
FILAS = WEB["rank_rows"]                        # el orden condicional, tal como lo publica el índice
FILA = {f["configuration"]: f for f in FILAS}
for f in FILAS:                                  # la tabla del contenido web cuadra con la aritmética
    c = f["configuration"]
    assert f'{f["primary_index"]:.1f}' == A["primary_comparison"]["scores"][c]["display_one_decimal"]
    assert f'{f["judge_GPT_index"]:.1f}' == A["engine_profiles"]["JG"][c]["primary_index"]["display_one_decimal"]
    assert f'{f["judge_Claude_index"]:.1f}' == A["engine_profiles"]["JC"][c]["primary_index"]["display_one_decimal"]
    assert f["position_in_primary_index"] == A["primary_comparison"]["ranks"][c]
CONFIGS = ("M03", "M04")                         # orden fijo de registro: no es un orden de resultados
MOTORES = ("JG", "JC")
FASES = ("A", "B", "R1", "R2", "E")
CLASES = {"A_J1": ("A", ["J1.1"]), "A_J2": ("A", ["J2.1"]), "AB_J1": ("B", ["J1.2", "J1.3", "J1.4", "J1.5", "J1.6"]),
          "AB_J2": ("B", ["J2.2", "J2.3", "J2.4", "J2.5"]), "R_J3": ("R", ["J3.1", "J3.2", "J3.3"]), "E_J3": ("E", ["J3.4", "J3.5"])}


def frase(texto_completo, comienzo, final="."):
    """Una oración del resumen, tal cual: desde «comienzo» hasta el primer «final» que la cierra."""
    i = texto_completo.index(comienzo)
    j = texto_completo.index(final, i + len(comienzo) - 1) + len(final)
    return texto_completo[i:j]


RES_ES, RES_EN = RESUMEN.split("\nENGLISH\n")
CORTE = frase(RESUMEN, "Corte: 18 de octubre de 2026")
CASOS_REALES = ("Casos ficticios; respuestas reales.", "Fictional cases; real model responses.")
S = {  # oraciones del resumen que la portada cita, en sus dos idiomas
    "indice": (frase(RES_ES, "El índice 0–100 combina"), frase(RES_EN, "The 0–100 index combines")),
    "panel": (frase(RES_ES, "El panel examina"), frase(RES_EN, "The panel examines")),
    "textos": (frase(RES_ES, "Hay 60 textos analizados"), frase(RES_EN, "X1 examines 60 texts")),
    "estricto": (frase(RES_ES, "ED02 admite estrictamente"), frase(RES_EN, "ED02 strictly admits")),
    "tercios": (frase(RES_ES, "Tres especialidades aportan"), frase(RES_EN, "Three perspectives each contribute")),
    "no_admitidas": (frase(RES_ES, "Dos configuraciones abiertas previstas"), frase(RES_EN, "Two planned open configurations")),
    "gemini": (frase(RES_ES, "Gemini queda"), frase(RES_EN, "Gemini remains")),
    "esfuerzo": (frase(RES_ES, "La prueba fue en español"), frase(RES_EN, "Execution was in Spanish")),
    "computo": (frase(RES_ES, "No se acredita igualdad"), frase(RES_EN, "Equal compute and immutable")),
    "fragmentos": (frase(RES_ES, "Estos fragmentos no son"), frase(RES_EN, "These passages are not")),
    "novedad": (frase(RES_ES, "La novedad evaluada"), frase(RES_EN, "Assessed novelty")),
    "desviaciones": (frase(RES_ES, "También se documentan"), frase(RES_EN, "Earlier deviations in criticism")),
    "escenarios": (frase(RES_ES, "Los escenarios no son"), frase(RES_EN, "These scenarios are not")),
}
RUBRICA = texto("metodo/rubrica_original_es.txt")
assert texto("materiales_comunes/RUBRICA.txt") == RUBRICA
ANCLAS = {int(m.group(1)): m.group(2) for m in re.finditer(r"(\d) = ([^;.]+)", RUBRICA.split("NE significa")[0])}
assert sorted(ANCLAS) == [0, 1, 2, 3, 4], ANCLAS
RUBRICA_TITULO = RUBRICA.splitlines()[0]

# ---------------------------------------------------------------- ✎ rótulos funcionales (propuesta de Claude)
ROT = {
    "badge": (WEB["es"]["badge"], WEB["en"]["badge"]),
    "rotulo_preguntas": ("Preguntas abiertas", "Open questions"),
    "rotulo_laboratorio": ("Laboratorio", "Laboratory"),
    "rotulo_resultados": ("Resultados", "Results"),
    "rotulo_como-medimos": ("Cómo medimos", "How we measure"),
    "orden": ("Orden condicional", "Conditional order"),
    "configuracion": ("Configuración", "Configuration"),
    "combinado": ("Índice combinado", "Combined index"),
    "motor_JG": ("Motor GPT", "GPT engine"),
    "motor_JC": ("Motor Claude", "Claude engine"),
    "juez_JG": ("Motor juez GPT", "GPT judging engine"),
    "juez_JC": ("Motor juez Claude", "Claude judging engine"),
    "primero_motor": ("primero para este motor", "first for this engine"),
    "primero_cada": ("primero para cada motor", "first for each engine"),
    "lee_t": ("Quién puntúa cada especialidad", "Who scores each perspective"),
    "puntua": ("puntúa", "scores"),
    "res_apuestas": ("Seis apuestas", "Six commitments"),
    "res_motores": ("Motores", "Engines"),
    "u_textos_corto": ("textos", "texts"),
    "esfuerzo": ("esfuerzo", "effort"),
    "exactos": ("Valores exactos del índice combinado: {a}. La cifra con un decimal es una presentación.",
                "Exact combined index values: {a}. The one-decimal figure is a presentation."),
    "esc_t": ("42 escenarios, partidos por motor", "42 scenarios, split by engine"),
    "esc_motor": ("{m} · 21 escenarios", "{m} · 21 scenarios"),
    "esc_celda": ("{p} primero", "{p} first"),
    "esc_ejes": ("7 juegos de pesos × 3 conversiones de niveles", "7 weight sets × 3 level recodings"),
    "esc_lectura": ("Dentro de cada motor, ningún juego de pesos ni conversión de niveles cambia el orden. Lo que lo invierte es el motor.",
                    "Within each engine, no weight set or level recoding changes the order. What reverses it is the engine."),
    "aviso": ("Aviso", "Notice"),
    "nota_completa": ("Leer la nota completa de incidencias", "Read the full incident note"),
    "no_admitidas_t": ("Fuera de este índice", "Outside this index"),
    "no_admitida": ("No admitida técnicamente · sin nota ni posición", "Not technically admitted · no score or position"),
    "pendiente_gemini": ("Pendiente", "Pending"),
    "perfiles_t": ("Perfiles por especialidad y por caso", "Profiles by perspective and by case"),
    "media_motores": ("Media de los dos motores", "Mean of both engines"),
    "especialidad": ("Especialidad", "Perspective"),
    "caso": ("Caso", "Case"),
    "limites_t": ("Lo que este índice no dice", "What this index does not say"),
    "ir_lecturas": ("Leer las lecturas, recorrido por recorrido", "Read the judgments, run by run"),
    "unidades_t": ("Cuatro unidades distintas", "Four different units"),
    "u_recorridos": ("recorridos", "runs"),
    "u_textos": ("textos analizados", "texts examined"),
    "u_criticas": ("críticas", "critiques"),
    "u_lecturas": ("lecturas", "readings"),
    "u_recorridos_d": ("Una configuración ante un caso, de la pregunta a la transferencia: dos configuraciones × tres casos × dos recorridos.",
                       "One configuration facing one case, from question to transfer: two configurations × three cases × two runs."),
    "u_criticas_d": ("Dos por recorrido. Cada una abre una rama: el modelo la examina y decide qué mantiene o cambia.",
                     "Two per run. Each opens a branch: the model examines it and decides what to keep or change."),
    "u_lecturas_d": ("Dictámenes de los dos motores: doce por recorrido. Juntas fijan 384 niveles (16 criterios × 2 motores × 12 recorridos).",
                     "Judgments by the two engines: twelve per run. Together they set 384 levels (16 criteria × 2 engines × 12 runs)."),
    "carrusel_t": (FRAG["label_es"][0].upper() + FRAG["label_es"][1:], FRAG["label_en"][0].upper() + FRAG["label_en"][1:]),
    "carrusel_regla": ("Uno por cada uno de los 60 textos: el primer pasaje que un juez citó, entre los de 60 a 240 caracteres. Cada visita los baraja.",
                       "One for each of the 60 texts: the first passage a judge cited, among those of 60 to 240 characters. Each visit shuffles them."),
    "casos_t": ("Tres casos ficticios, doce recorridos", "Three fictional cases, twelve runs"),
    "casos_orden": ("Orden fijo de registro: no es un orden de resultados.", "Fixed registration order: not an order of results."),
    "recorrido_n": ("Recorrido {n}", "Run {n}"),
    "recorrido_de": ("Recorrido {n} de 2", "Run {n} of 2"),
    "leer_contexto": ("Leer en contexto", "Read in context"),
    "citado_por": ("Citado por", "Cited by"),
    "voz_modelo": ("Texto del modelo", "Model’s text"),
    "voz_juez": ("Lectura del juez", "Judge’s reading"),
    "voz_editorial": ("Explicación editorial", "Editorial explanation"),
    "voz_critica": ("Crítica recibida", "Criticism received"),
    "voz_caso": ("Material del caso", "Case material"),
    "voz_comun": ("Material común", "Common material"),
    "original_es": ("", "Spanish original · not translated"),
    "etapa": ("Etapa", "Stage"),
    "anterior": ("Pasaje anterior", "Previous passage"),
    "siguiente": ("Pasaje siguiente", "Next passage"),
    "cuenta_pre": ("Pasaje", "Passage"),
    "cuenta_de": ("de", "of"),
    "cerrar": ("Cerrar", "Close"),
    "panel_t": ("Pasaje citado por un juez", "Passage cited by a judge"),
    "panel_texto": ("El pasaje en su texto", "The passage in its text"),
    "panel_jueces": ("Por qué lo citó el juez", "Why the judge cited it"),
    "panel_abrir": ("Abrir el recorrido completo", "Open the full run"),
    "panel_error": ("No pudimos cargar el recorrido. Puedes abrirlo en su página.", "We couldn’t load the run. You can open it on its own page."),
    "incidencias_t": (NOTA["es"]["title"], NOTA["en"]["title"]),
    "medimos_esp_t": ("Tres especialidades, dos motores", "Three perspectives, two engines"),
    "peso_tercio": ("Peso en el índice: {w}", "Weight in the index: {w}"),
    "criterio": ("Criterio", "Criterion"),
    "peso": ("Peso", "Weight"),
    "lee": ("Lee", "Reads"),
    "escala_t": ("La escala y el índice", "The scale and the index"),
    "sensibilidad_t": ("Sensibilidad", "Sensitivity"),
    "orden_t": ("Orden de lectura", "Reading order"),
    "materiales": ("La rúbrica original, la guía, las condiciones y las consignas", "The original rubric, guide, conditions and instructions"),
    "metodo_pag": ("Método y materiales de ED02-X1", "ED02-X1 method and materials"),
    "volver_lab": ("Volver al laboratorio", "Back to the laboratory"),
    "volver_metodo": ("Volver a cómo medimos", "Back to how we measure"),
    "ruta_aria": ("Etapas del recorrido", "Stages of the run"),
    "palabras": ("{n} palabras · máximo {m}", "{n} words · limit {m}"),
    "aceptado": ("Aceptado en ED02", "Accepted in ED02"),
    "incidente": ("Incidente administrativo de extensión: fuera de ED02 estricto, examinado íntegro en X1",
                  "Administrative length incident: outside strict ED02, examined intact in X1"),
    "pasajes_t": ("Pasajes citados por los jueces: {n}", "Passages cited by the judges: {n}"),
    "pasajes_registros": ("{r} registros de cita en {n} pasajes distintos. Ninguna de las dos cifras cuenta ideas.",
                          "{r} citation records across {n} distinct passages. Neither figure counts ideas."),
    "ver_texto": ("ver en el texto", "see in the text"),
    "lecturas_t": ("Cómo lo leyeron los dos motores", "How the two engines read it"),
    "lecturas_ramas": ("Las dos ramas, leídas juntas", "Both branches, read together"),
    "nivel": ("Nivel {n} de 4", "Level {n} of 4"),
    "nivel_alcance": ("vale para {f}, no para una frase", "applies to {f}, not to a single sentence"),
    "f_A": ("la pregunta (A)", "the question (A)"),
    "f_A+B": ("la pregunta y la propuesta (A+B)", "the question and the proposal (A+B)"),
    "f_RAMAS": ("las dos ramas de revisión", "both revision branches"),
    "f_E": ("la transferencia (E)", "the transfer (E)"),
    "ancla_rubrica": ("anclaje de la rúbrica", "rubric anchor"),
    "regla": ("Nivel {n} en una regla de 0 a 4", "Level {n} on a 0 to 4 scale"),
    "j_justificacion": ("Justificación", "Justification"),
    "j_limite": ("Límite o carencia", "Limitation or shortcoming"),
    "anclas_nota": ("Los anclajes se citan tal cual de la rúbrica original.", "The anchors are quoted from the original Spanish rubric."),
    "j_sin_limite": ("El dictamen no registra ninguno.", "The judgment records none."),
    "j_todo": ("Todo el dictamen", "The full judgment"),
    "j_propiedad": ("Propiedad evaluada", "Property assessed"),
    "j_evidencias": ("Evidencias", "Evidence"),
    "j_alternativa": ("Lectura alternativa", "Alternative reading"),
    "j_tratamiento": ("Tratamiento", "Treatment"),
    "j_razon": ("Razón", "Reason"),
    "j_cambiaria": ("Evidencia que cambiaría el juicio", "Evidence that would change the judgment"),
    "j_procedencia": ("Procedencia de cada afirmación", "Provenance of each claim"),
    "j_clase": ("Clase", "Class"),
    "j_puente": ("Puente", "Bridge"),
    "j_alt_considerada": ("Alternativa considerada", "Alternative considered"),
    "j_merito": ("Cuenta como mérito del participante", "Counts as the participant’s merit"),
    "j_merito_no": ("No cuenta como mérito del participante", "Does not count as the participant’s merit"),
    "j_uso": ("Justificación de uso", "Reason for use"),
    "j_alertas": ("Alertas", "Alerts"),
    "j_ne": ("Causa de no evaluable", "Reason for not assessable"),
    "j_archivo": ("Cuerpo publicado", "Published body"),
    "ref_doc": ("Referencia a: {d}", "Reference to: {d}"),
    "ref_no_promovida": ("No es un pasaje evaluado en esta lectura: no se destaca.", "Not a passage evaluated in this reading: not highlighted."),
    "ref_inexacta": ("La cita no aparece literal en el segmento declarado: no se destaca.", "The quote does not appear literally in the declared segment: not highlighted."),
    "rol_evidencias": ("evidencia", "evidence"),
    "rol_procedencia": ("procedencia", "provenance"),
    "rol_alertas": ("alerta", "alert"),
    "rama": ("Rama {r}", "Branch {r}"),
    "critica_nota": ("La preparación de las críticas tuvo desviaciones documentadas.", "Criticism preparation had documented deviations."),
    "e_rama": ("La transferencia parte de la historia de la rama {r}.", "The transfer builds on the history of branch {r}."),
    "contraste": ("Contraste T", "Contrast T"),
    "el_caso": ("El caso", "The case"),
    "expediente": ("Expediente", "Case file"),
    "corpus": ("Corpus", "Corpus"),
    "huellas_t": ("Procedencia", "Provenance"),
    "huella": ("SHA-256 del original", "SHA-256 of the original"),
    "ficticio": ("Caso ficticio", "Fictional case"),
    "sin_validacion": ("Sin validación humana.", "No human validation."),
    "ninguno": ("—", "—"),
    "conf_id": ("identificador", "identifier"),
    "documentos": {"A": ("la pregunta (A)", "the question (A)"), "B": ("la propuesta (B)", "the proposal (B)"),
                   "R1": ("la respuesta R1", "response R1"), "R2": ("la respuesta R2", "response R2"), "E": ("la transferencia (E)", "the transfer (E)"),
                   "CR1": ("la crítica 1", "criticism 1"), "CR2": ("la crítica 2", "criticism 2"), "T": ("el contraste T", "contrast T"),
                   "CASO": ("el expediente del caso", "the case file"), "CORPUS": ("el corpus del caso", "the case corpus"),
                   "COND": ("las condiciones comunes", "the common conditions"), "GUIA": ("la guía de lectura", "the reading guide"),
                   "RUBRICA": ("la rúbrica", "the rubric"), "CONS_A": ("la consigna A", "instruction A"), "CONS_B": ("la consigna B", "instruction B"),
                   "CONS_R1": ("la consigna R", "instruction R"), "CONS_R2": ("la consigna R", "instruction R"), "CONS_E": ("la consigna E", "instruction E"),
                   "RAMA_E": ("la historia de la rama que recibe E", "the branch history given to E"),
                   "H": ("el historial visible (solo contexto)", "the visible history (context only)")},
    "metodo_x1_t": ("Qué es ED02-X1", "What ED02-X1 is"),
    "cifras_t": ("Las cifras del panel, con lo que cuentan", "The panel’s figures, and what they count"),
    "materiales_t": ("Materiales comunes, en su original", "Common materials, in the original"),
    "materiales_nota": ("Lo que recibieron los modelos y los jueces. En español, como se usaron.", "What the models and judges received. In Spanish, as used."),
}
CRIT_EN = {  # ✎ traducción editorial de los nombres de la rúbrica; en la página inglesa va junto al original
    "J1.1": "Problem formulation and understanding", "J1.2": "Conceptual understanding and precision",
    "J1.3": "Argument reconstruction and critical examination", "J1.4": "Context and comparison",
    "J1.5": "Sources and traceability", "J1.6": "Autonomous use of the philosophical repertoire",
    "J2.1": "Investigable fruitfulness of the question", "J2.2": "Originality relative to the corpus",
    "J2.3": "Articulation and grounding of the contribution", "J2.4": "Philosophical gain",
    "J2.5": "Developable continuations", "J3.1": "Discernment about the question under criticism",
    "J3.2": "Response to objections", "J3.3": "Revision and autonomy of judgment",
    "J3.4": "Transfer and limits", "J3.5": "Situated effectiveness and consequences",
}
assert sorted(CRIT_EN) == sorted(CRIT)


def nombre_criterio(crit, lang, breve=False):
    """En español, el nombre de la rúbrica; en inglés, la traducción editorial y, al lado, el original
    (en las esquinas, que son una muestra, va solo la traducción)."""
    es = e(CRIT[crit]["nombre"])
    if lang == "es":
        return f'<span class="crit-nombre">{es}</span>'
    if breve:
        return f'<span class="crit-nombre">{e(CRIT_EN[crit])}</span>'
    return f'<span class="crit-nombre">{e(CRIT_EN[crit])}</span> <span class="crit-original" lang="es">{es}</span>'


CONSIGNA = {k: texto(f"materiales_comunes/CONS_{k if k != 'R' else 'R1'}.txt").splitlines()[0] for k in ("A", "B", "R", "E")}
FASE_NOMBRE = {  # el nombre de cada etapa sale de la primera línea de su consigna original; en inglés, ✎
    "A": (" · ".join(CONSIGNA["A"].split(" · ")[:2]), "A · Question and justification"),
    "B": (" · ".join(CONSIGNA["B"].split(" · ")[:2]), "B · Proposal"),
    "R": (" · ".join(CONSIGNA["R"].split(" · ")[:2]), "R · Examining the criticism received"),
    "E": (" · ".join(CONSIGNA["E"].split(" · ")[:2]), "E · Contrast and limits"),
}
LIMITE = {"A": 200, "B": 900, "R1": 350, "R2": 350, "E": 350}
assert all(CONSIGNA["R" if k in ("R1", "R2") else k].endswith(f"Máximo {LIMITE[k]} palabras") for k in LIMITE)
SPLIT_SALA = {"preguntas": "preguntas_abiertas", "laboratorio": "laboratorio", "resultados": "resultados", "como-medimos": "como_medimos"}


def L(par, lang):
    return par[0 if lang == "es" else 1]


def r(clave, lang, **k):
    s = L(ROT[clave], lang)
    return s.format(**k) if k else s


def e(s):
    return html.escape(str(s), quote=True)


def w(campo, lang):
    """Un texto del contenido web del paquete, en su idioma."""
    return e(WEB[lang][campo])


def aj(clave, lang):
    """Un texto de la revisión de la portada (ed02x1_ajustes.json), en su idioma."""
    return e(AJUSTES[clave][lang])


# «Cambiar de motor invierte el orden»: la frase del paquete que va junto a las cifras, tal cual
GIRO = {"es": "Cambiar de motor invierte el orden.", "en": "Switching judging engines reverses the order."}
for _l, _g in GIRO.items():
    assert WEB[_l]["quadrants"]["resultados"]["preview"].count(_g) == 1, f"la frase del giro no está en el paquete ({_l})"


def con_giro(texto_plano, lang):
    """El texto, escapado, con la frase del giro destacada (sigue siendo el mismo texto)."""
    a, b = texto_plano.split(GIRO[lang])
    return f'{e(a)}<strong class="x1-giro">{e(GIRO[lang])}</strong>{e(b)}'


def num(valor, lang):
    """La cifra publicada con un decimal; en español, con coma. No redondea: la toma del índice."""
    s = valor if isinstance(valor, str) else f"{valor:.1f}"
    return s.replace(".", ",") if lang == "es" else s


def simbolo(nombre, extra=""):
    return f'<svg class="simbolo{extra}" aria-hidden="true" focusable="false"><use href="#s-{nombre}"/></svg>'


def slug(tid):
    return tid.removeprefix("ED02-").lower()


def raiz(lang):
    return "/" if lang == "es" else "/en/"


def url_recorrido(tid, lang):
    return f"{raiz(lang)}{CARPETA}/{slug(tid)}/"


def url_metodo(lang):
    return f"{raiz(lang)}{CARPETA}/metodo/"


ESFUERZO = {  # ✎ el valor del índice, dicho en cada idioma
    "high": ("high", "high"),
    "high requested / effective effort not separately reported": ("high solicitado; el esfuerzo efectivo no se informa por separado",
                                                                  "high requested; effective effort not separately reported"),
}


def esfuerzo_de(conf, lang):
    return L(ESFUERZO[FILA[conf]["effort"]], lang)


def nombre_modelo(conf):
    return FILA[conf]["model"]


def ident_jid(motor, crit):
    return f"j-{motor.lower()}-{crit.lower().replace('.', '-')}"


# ---------------------------------------------------------------- texto del participante, con sus pasajes
# Se presenta sin cambiar una letra: párrafos, renglones, listas, títulos y el énfasis que marcó.
# Cada pasaje citado lleva su ancla (id) donde empieza y sus tramos llevan data-p con los pasajes que los
# cubren: un mismo tramo puede estar en varios pasajes (uno dentro de otro, o que se cruzan).

def inline(raw, a, b, pasajes, ancladas):
    """raw[a:b] en HTML, con negrita, cursiva y los tramos de los pasajes que lo cubren."""
    oculto, negrita, cursiva = set(), set(), set()
    seg = raw[a:b]
    for m in re.finditer(r"\*\*(.+?)\*\*", seg):
        oculto.update((a + m.start(), a + m.start() + 1, a + m.end() - 2, a + m.end() - 1))
        negrita.update(range(a + m.start(1), a + m.end(1)))
    for m in re.finditer(r"(?<![\w*])\*(?!\s)([^*\n]+?)(?<!\s)\*(?![\w*])", seg):
        if a + m.start() in oculto:
            continue
        oculto.update((a + m.start(), a + m.end() - 1))
        cursiva.update(range(a + m.start(1), a + m.end(1)))
    salida, run, clave_run = [], [], None

    def cerrar():
        if not run:
            return
        neg, cur, ps = clave_run
        t = e("".join(run))
        if ps:
            t = f'<span class="cita" data-p="{" ".join(sorted(ps))}">{t}</span>'
        if cur:
            t = f"<em>{t}</em>"
        if neg:
            t = f"<strong>{t}</strong>"
        salida.append(t)
        run.clear()

    for i in range(a, b):
        if i in oculto:
            continue
        for p in pasajes:
            if p["pid"] not in ancladas and p["ini"] <= i < p["fin"]:
                cerrar()
                clave_run = None
                ancladas.add(p["pid"])
                salida.append(f'<span class="p-a" id="{p["pid"]}" data-cita="{p["citas_attr"]}"></span>')
        clave = (i in negrita, i in cursiva, frozenset(p["pid"] for p in pasajes if p["ini"] <= i < p["fin"]))
        if clave != clave_run:
            cerrar()
            clave_run = clave
        run.append(raw[i])
    cerrar()
    return "".join(salida)


LINEA = re.compile(r"^(?:(?P<h>#{1,6} )|(?P<ul>[-*•] )|(?P<ol>\d+[.)] ))?")


def presentar(raw, pasajes=()):
    """El texto entero: bloques separados por renglones en blanco; dentro, listas, títulos y párrafos."""
    ancladas = set()
    partes = []
    pos = 0
    for bloque in re.split(r"(\n\s*\n)", raw):
        if not bloque.strip() or re.fullmatch(r"\n\s*\n", bloque):
            pos += len(bloque)
            continue
        lineas, off = [], pos
        for ln in bloque.split("\n"):
            lineas.append((off, ln))
            off += len(ln) + 1
        pos += len(bloque)
        grupo, tipo = [], None

        def volcar():
            if not grupo:
                return
            if tipo == "ul":
                partes.append("<ul>" + "".join(f"<li>{x}</li>" for x in grupo) + "</ul>")
            elif tipo == "ol":
                partes.append("<ol>" + "".join(f'<li value="{v}">{x}</li>' for v, x in grupo) + "</ol>")
            elif tipo == "h":
                partes.extend(f'<p class="t-h">{x}</p>' for x in grupo)
            else:
                partes.append("<p>" + "<br>".join(grupo) + "</p>")
            grupo.clear()

        for off, ln in lineas:
            if not ln.strip():
                continue
            m = LINEA.match(ln)
            t = "h" if m.group("h") else "ul" if m.group("ul") else "ol" if m.group("ol") else "p"
            ini = off + m.end()
            fin = off + len(ln.rstrip())
            contenido = inline(raw, ini, fin, pasajes, ancladas)
            if t != tipo:
                volcar()
                tipo = t
            grupo.append((m.group("ol").rstrip(".) ").strip() if t == "ol" else None, contenido) if t == "ol" else contenido)
        volcar()
    faltan = {p["pid"] for p in pasajes} - ancladas
    assert not faltan, f"pasajes sin ancla: {sorted(faltan)[:3]}"
    return "".join(partes)


# ---------------------------------------------------------------- los pasajes citados, agrupados

def offsets_a_caracteres(b, ini, fin):
    return len(b[:ini].decode("utf-8")), len(b[:fin].decode("utf-8"))


PUNTERO = re.compile(r"^/criterios/(J\d\.\d)/(evidencias|procedencia|alertas)/(\d+)(?:/(apoyos|referencias)/(\d+))?$")
VERIFICADA = {}           # (juicio, puntero) -> id del pasaje
def tramo_visible(it):
    """Los bytes del pasaje sin las marcas de énfasis de sus bordes: la misma frase citada con o sin sus «**»
    es un solo pasaje (fuente + etapa + posición visible), con todos sus vínculos de juez y criterio."""
    o, q = it["exact_occurrences_utf8"][0], it["quote_es"]
    izq, der = len(q) - len(q.lstrip("*")), len(q) - len(q.rstrip("*"))
    return o["start_byte"] + izq, o["end_byte"] - der


GRUPOS = collections.OrderedDict()   # (fuente, fase, ini, fin) visibles -> registros
for it in FRAG["items"]:
    assert it["exact_substring_verified"] is True and it["translation"] is None and len(it["exact_occurrences_utf8"]) == 1
    GRUPOS.setdefault((it["source_file"], it["source_final_phase"], *tramo_visible(it)), []).append(it)
NO_PROMOVIDA = {(x["judgment_id"], x["criterion_pointer"]): x["reason"] for x in DIAG["items"]}
assert DIAG["used_for_scores_or_exclusion"] is False and all(x["grade_or_hold_changed"] is False for x in DIAG["items"])


def pid_de(fase, ini, fin):
    """El ancla de un pasaje: su etapa y sus bytes en el original («p-b-1532-1688»). Estable entre construcciones."""
    return f"p-{fase.lower()}-{ini}-{fin}"


def juicio_de(jid):
    """«ED02-M03-C01-R1_A_J1_JG» → recorrido, clase de lectura y motor."""
    tid, resto = jid.split("_", 1)
    clase, motor = resto.rsplit("_", 1)
    return tid, clase, motor


POR_FUENTE = collections.defaultdict(list)    # archivo fuente -> pasajes
for (fuente, fase, ini, fin), regs in GRUPOS.items():
    b = crudo(fuente)
    ci, cf = offsets_a_caracteres(b, ini, fin)
    cita = b[ini:fin].decode("utf-8")   # la frase visible, con las marcas de dentro (se presentan como énfasis)
    assert all(x["quote_es"].strip("*") == cita and x["source_sha256"] == hashlib.sha256(b).hexdigest() for x in regs)
    for x in regs:
        o = x["exact_occurrences_utf8"][0]
        assert b[o["start_byte"]:o["end_byte"]].decode("utf-8") == x["quote_es"]
    pid = pid_de(fase, ini, fin)
    citas = []
    for x in regs:
        tid, clase, motor = juicio_de(x["judgment_id"])
        m = PUNTERO.match(x["criterion_pointer"])
        assert m, x["criterion_pointer"]
        crit, rol = m.group(1), m.group(2)
        assert crit in CLASES[clase][1], (clase, crit)
        VERIFICADA[(x["judgment_id"], x["criterion_pointer"])] = pid
        citas.append({"motor": motor, "crit": crit, "rol": rol, "jid": ident_jid(motor, crit), "puntero": x["criterion_pointer"]})
    # cada vínculo de juez y criterio se conserva; en el ancla, una vez por juicio y papel
    unicos = list(dict.fromkeys((c["jid"], c["rol"]) for c in citas))
    # si la cita empieza donde empieza un renglón, su viñeta o su número de lista no se muestran (como en el texto)
    vista = re.sub(r"^(?:#{1,6} |[-•] |\d+[.)] )", "", cita) if ini == 0 or b[ini - 1:ini] == b"\n" else cita
    POR_FUENTE[fuente].append({"pid": pid, "fase": fase, "ini": ci, "fin": cf, "bytes": (ini, fin), "cita": cita, "vista": vista,
                               "registros": regs, "citas": citas,
                               "citas_attr": " ".join(f"{j}:{rol[0]}" for j, rol in unicos)})
for v in POR_FUENTE.values():
    v.sort(key=lambda p: (p["ini"], -p["fin"]))
assert len(GRUPOS) == sum(len(v) for v in POR_FUENTE.values())


def carrusel_de(fuente):
    """La regla del carrusel (✎): el primer pasaje citado del texto, entre los de 60 a 240 caracteres."""
    candidatos = [p for p in POR_FUENTE[fuente] if 60 <= len(p["cita"]) <= 240]
    assert candidatos, fuente
    return min(candidatos, key=lambda p: (p["ini"], p["fin"]))


# ---------------------------------------------------------------- las lecturas

CUERPOS = {}   # id de lectura -> cuerpo publicado
DOCS = {}      # id de lectura -> {documento_id: artifact_id}
for rr in REFS["readings"]:
    DOCS[rr["judgment_id"]] = {d["documento_id"]: d["artifact_id"] for d in rr["documents"]}
NIVELES = 0
for t in TRAY:
    for lec in t["public_judge_readings"]:
        cuerpo = leer(lec["public_selected_body"]["file"])
        assert lec["public_selected_body"]["translation"] is False and lec["editorial_translation"] is None
        clase = lec["kind"]
        assert sorted(cuerpo["criterios"]) == sorted(CLASES[clase][1]) == sorted(lec["criteria"]), lec["id"]
        for c in cuerpo["criterios"].values():
            assert c["nivel"] in (0, 1, 2, 3, 4), lec["id"]    # en X1 no hay NE: los 384 niveles son números
            NIVELES += 1
        CUERPOS[lec["id"]] = cuerpo
assert NIVELES == 384 and len(CUERPOS) == 144


def todas_las_referencias():
    """Cada cita de un dictamen es un pasaje verificado o una referencia no promovida, nunca las dos."""
    for jid, cuerpo in CUERPOS.items():
        for crit, c in cuerpo["criterios"].items():
            for i, ev in enumerate(c.get("evidencias") or []):
                yield jid, f"/criterios/{crit}/evidencias/{i}", ev
            for i, pr in enumerate(c.get("procedencia") or []):
                for k, ap in enumerate(pr.get("apoyos") or []):
                    yield jid, f"/criterios/{crit}/procedencia/{i}/apoyos/{k}", ap
            for i, al in enumerate(c.get("alertas") or []):
                for k, rf in enumerate(al.get("referencias") or []):
                    yield jid, f"/criterios/{crit}/alertas/{i}/referencias/{k}", rf


_refs = [(j, p) for j, p, ref in todas_las_referencias() if ref.get("cita")]
assert len(_refs) == len(VERIFICADA) + len(NO_PROMOVIDA), (len(_refs), len(VERIFICADA), len(NO_PROMOVIDA))
assert all(((j, p) in VERIFICADA) != ((j, p) in NO_PROMOVIDA) for j, p in _refs)


# ---------------------------------------------------------------- las piezas de un recorrido

def regla(n, lang, etiqueta):
    pos = "".join(f'<span class="regla-pos{" regla-pos--marca" if v == n else ""}"><span class="regla-n">{v}</span></span>' for v in range(5))
    return f'<div class="regla" role="img" aria-label="{e(r("regla", lang, n=n) + " · " + etiqueta)}">{pos}</div>'


def nombre_documento(jid, doc_id, lang):
    art = DOCS[jid].get(doc_id, "")
    clave = "H" if re.fullmatch(r"H\d+[DN]", art) else art
    return L(ROT["documentos"].get(clave, (art, art)), lang)


def referencia(jid, puntero, ref, lang):
    """Una cita dentro del dictamen: si es un pasaje verificado, enlaza a su lugar; si no, se dice por qué no se destaca."""
    cita = cita_html(ref.get("cita") or "")
    pid = VERIFICADA.get((jid, puntero))
    if pid:
        return f'<li><a class="ref-cita" href="#{pid}" data-ir-pasaje="{pid}"><q lang="es">{cita}</q></a></li>'
    razon = NO_PROMOVIDA.get((jid, puntero))
    doc = nombre_documento(jid, ref.get("documento_id"), lang) if ref.get("documento_id") else ""
    nota = r("ref_inexacta", lang) if razon == "QUOTE_NOT_EXACT_SUBSTRING_OF_DECLARED_SEGMENT_AND_FINAL" else r("ref_no_promovida", lang)
    return (f'<li class="ref-otra"><q lang="es">{cita}</q> <span class="ref-nota">{e(r("ref_doc", lang, d=doc))}. {e(nota)}</span></li>'
            if cita else "")


def limite_vacio(lang):
    """Siete dictámenes de nivel 4 no registran límite: se dice así, sin inventar uno."""
    return f'<div class="j-campo j-campo--limite"><p class="j-rot">{r("j_limite", lang)}</p><p class="j-vacio">{r("j_sin_limite", lang)}</p></div>'


def cita_html(cita):
    """Una cita del texto del participante, con su énfasis como énfasis. Si la cita corta un énfasis por la
    mitad, su marca suelta no se muestra: en estos textos todo asterisco es una marca (ninguno queda a la vista)."""
    return inline(cita, 0, len(cita), [], set()).replace("*", "")


def campo(rot, valor, lang, clase=""):
    if valor in (None, "", []):
        return ""
    return f'<div class="j-campo{(" " + clase) if clase else ""}"><p class="j-rot">{r(rot, lang)}</p><p lang="es">{e(valor)}</p></div>'


def juicio(t, lectura, crit, lang, fase_txt):
    """Un dictamen de un motor sobre un criterio: nivel, justificación y límites a la vista; el resto, desplegable."""
    jid = lectura["id"]
    c = CUERPOS[jid]["criterios"][crit]
    motor = lectura["engine"]
    ident = ident_jid(motor, crit)
    n = c["nivel"]
    evid = "".join(referencia(jid, f"/criterios/{crit}/evidencias/{i}", ev, lang) for i, ev in enumerate(c.get("evidencias") or []))
    alt = c.get("alternativa") or {}
    alt_html = ""
    if alt:
        alt_html = (f'<div class="j-campo"><p class="j-rot">{r("j_alternativa", lang)}</p><p lang="es">{e(alt.get("lectura", ""))}</p>'
                    f'<p class="j-sub"><span class="j-rot-in">{r("j_tratamiento", lang)}:</span> <span lang="es">{e(alt.get("tratamiento", ""))}</span></p>'
                    f'<p class="j-sub"><span class="j-rot-in">{r("j_razon", lang)}:</span> <span lang="es">{e(alt.get("razon_publica", ""))}</span></p></div>')
    proc = ""
    for i, pr in enumerate(c.get("procedencia") or []):
        apoyos = "".join(referencia(jid, f"/criterios/{crit}/procedencia/{i}/apoyos/{k}", ap, lang) for k, ap in enumerate(pr.get("apoyos") or []))
        merito = r("j_merito", lang) if pr.get("usado_como_merito_del_participante") else r("j_merito_no", lang)
        proc += (f'<li><p lang="es">{e(pr.get("afirmacion_publica", ""))}</p>'
                 f'<p class="j-sub"><span class="j-rot-in">{r("j_clase", lang)}:</span> <span lang="es">{e(pr.get("clase", "").replace("_", " "))}</span> · {e(merito)}</p>'
                 + (f'<ul class="j-citas" role="list">{apoyos}</ul>' if apoyos else "")
                 + (f'<p class="j-sub"><span class="j-rot-in">{r("j_puente", lang)}:</span> <span lang="es">{e(pr["puente_publico"])}</span></p>' if pr.get("puente_publico") else "")
                 + (f'<p class="j-sub"><span class="j-rot-in">{r("j_alt_considerada", lang)}:</span> <span lang="es">{e(pr["alternativa_considerada"])}</span></p>' if pr.get("alternativa_considerada") else "")
                 + (f'<p class="j-sub"><span class="j-rot-in">{r("j_uso", lang)}:</span> <span lang="es">{e(pr["justificacion_de_uso"])}</span></p>' if pr.get("justificacion_de_uso") else "")
                 + "</li>")
    alertas = ""
    for i, al in enumerate(c.get("alertas") or []):
        refs = "".join(referencia(jid, f"/criterios/{crit}/alertas/{i}/referencias/{k}", rf, lang) for k, rf in enumerate(al.get("referencias") or []))
        alertas += (f'<li><p><span class="j-alerta" lang="es">{e(al.get("tipo", "").replace("_", " "))}</span></p><p lang="es">{e(al.get("descripcion_publica", ""))}</p>'
                    + (f'<ul class="j-citas" role="list">{refs}</ul>' if refs else "") + "</li>")
    archivo = lectura["public_selected_body"]
    mas = (f'<details class="juicio-mas"><summary>{r("j_todo", lang)}</summary><div class="juicio-mas-in">'
           + campo("j_propiedad", c.get("propiedad_evaluada"), lang)
           + (f'<div class="j-campo"><p class="j-rot">{r("j_evidencias", lang)}</p><ul class="j-citas" role="list">{evid}</ul></div>' if evid else "")
           + alt_html
           + campo("j_cambiaria", c.get("evidencia_que_cambiaria_juicio"), lang)
           + (f'<div class="j-campo"><p class="j-rot">{r("j_procedencia", lang)}</p><ol class="j-proc" role="list">{proc}</ol></div>' if proc else "")
           + (f'<div class="j-campo"><p class="j-rot">{r("j_alertas", lang)}</p><ul class="j-alertas" role="list">{alertas}</ul></div>' if alertas else "")
           + campo("j_ne", c.get("causa_NE"), lang)
           + f'<p class="j-archivo">{r("j_archivo", lang)}: {e(archivo["file"])} · SHA-256 <code>{e(archivo["sha256"])}</code></p>'
           + "</div></details>")
    ancla = ANCLAS[n]
    return (f'<article class="juicio juicio--{motor.lower()}" id="{ident}" data-voz="juez" aria-labelledby="{ident}-t">'
            f'<p class="capa-rotulo">{r("voz_juez", lang)}</p>'
            f'<h4 class="juicio-quien" id="{ident}-t"><span class="juicio-motor">{r("juez_" + motor, lang)}</span> '
            f'<span class="juicio-crit">{crit}</span></h4>'
            f'<div class="juicio-nivel">{regla(n, lang, crit + " · " + r("juez_" + motor, lang))}'
            f'<p class="juicio-n"><span class="cifra-s">{r("nivel", lang, n=n)}</span> · {r("nivel_alcance", lang, f=fase_txt)}</p>'
            f'<p class="juicio-ancla"><span class="j-rot-in">{r("ancla_rubrica", lang)}:</span> <span lang="es">{e(ancla)}</span></p></div>'
            f'<div class="juicio-cuerpo">{campo("j_justificacion", c.get("justificacion_publica"), lang)}'
            f'{campo("j_limite", c.get("limite_o_carencia"), lang, "j-campo--limite") or limite_vacio(lang)}</div>'
            f'{mas}</article>')


def bloque_criterio(t, crit, lang, fase_ev):
    cr = CRIT[crit]
    lects = {l["engine"]: l for l in t["public_judge_readings"] if crit in l["criteria"]}
    assert sorted(lects) == sorted(MOTORES), (t["id"], crit)
    fase_txt = r("f_" + fase_ev, lang)
    pares = "".join(juicio(t, lects[m], crit, lang, fase_txt) for m in MOTORES)
    persp = PERSP[crit.split(".")[0]]
    return (f'<section class="rc-criterio" id="c-{crit.lower().replace(".", "-")}" aria-labelledby="c-{crit.lower().replace(".", "-")}-t">'
            f'<h4 class="rc-crit-t" id="c-{crit.lower().replace(".", "-")}-t"><span class="crit-id">{crit}</span> {nombre_criterio(crit, lang)} '
            f'<span class="rc-crit-peso">{r("peso", lang)} {cr["peso"]} · {e(persp["title_" + lang])}</span></h4>'
            f'<div class="rc-par">{pares}</div></section>')


def lista_pasajes(fuente, lang):
    ps = POR_FUENTE[fuente]
    regs = sum(len(p["registros"]) for p in ps)
    items = ""
    for p in ps:
        vistos, enlaces = set(), []
        for c in p["citas"]:
            k = (c["jid"], c["rol"])
            if k in vistos:
                continue
            vistos.add(k)
            enlaces.append(f'<a href="#{c["jid"]}">{r("motor_" + c["motor"], lang)} · {c["crit"]} <span class="lp-rol">({r("rol_" + c["rol"], lang)})</span></a>')
        items += (f'<li class="lp" id="l{p["pid"]}"><q lang="es">{cita_html(p["vista"])}</q> '
                  f'<a class="lp-ver" href="#{p["pid"]}" data-ir-pasaje="{p["pid"]}">{r("ver_texto", lang)}</a>'
                  f'<p class="lp-por">{r("citado_por", lang)}: {" · ".join(enlaces)}</p></li>')
    return (f'<details class="rc-pasajes"><summary>{r("pasajes_t", lang, n=len(ps))}</summary>'
            f'<p class="rc-pasajes-nota">{r("pasajes_registros", lang, r=regs, n=len(ps))} {e(L(S["fragmentos"], lang))}</p>'
            f'<ol class="lp-lista" role="list">{items}</ol></details>')


def meta_texto(info, lang):
    estado = r("aceptado", lang) if info["original_ED02_state"] == "ACCEPTED" else r("incidente", lang)
    clase = "" if info["strict_ED02_accepted"] else " rc-meta--incidente"
    fase = info["file"].rsplit("/", 1)[1].removesuffix(".txt")
    return (f'<p class="rc-meta{clase}"><span>{r("palabras", lang, n=info["words"], m=LIMITE[fase])}</span> '
            f'<span class="rc-meta-sep" aria-hidden="true">·</span> <span>{e(estado)}</span></p>')


def bloque_texto(t, fase, lang):
    info = t["visible_texts"][fase]
    raw = texto(info["file"])
    cuerpo = presentar(raw, POR_FUENTE[info["file"]])
    trad = f'<p class="rc-original">{r("original_es", lang)}</p>' if lang == "en" else ""
    return (f'{meta_texto(info, lang)}'
            f'<div class="rc-texto-caja"><p class="capa-rotulo">{r("voz_modelo", lang)} · {e(nombre_modelo(t["configuration"]))}</p>{trad}'
            f'<div class="rc-texto" data-voz="modelo" data-fase="{fase}" lang="es">{cuerpo}</div></div>'
            f'{lista_pasajes(info["file"], lang)}'
            f'<p class="rc-huella">{r("huella", lang)} · {e(info["file"])} · <code>{e(info["sha256"])}</code></p>')


def material(rel, lang, rotulo, clase="rc-material"):
    return (f'<div class="{clase}"><p class="capa-rotulo">{rotulo}</p>'
            f'<div class="rc-material-texto" lang="es">{presentar(texto(rel))}</div>'
            f'<p class="rc-huella">{r("huella", lang)} · {e(rel)} · <code>{e(hashlib.sha256(crudo(rel)).hexdigest())}</code></p></div>')


SPRITE = re.search(r'<svg class="simbolos".*?</svg>', (SITIO / "index.html").read_text(encoding="utf-8"), re.S).group(0)


def huella(rel):
    """La misma huella de versión que pone versionar_recursos.py: así la página nace al día."""
    return hashlib.sha256((SITIO / rel).read_bytes()).hexdigest()[:10]


ESTILO = f'<link rel="stylesheet" href="/assets/portada.css?v={huella("assets/portada.css")}">'
SCRIPT = f'<script src="/assets/archivo.js?v={huella("assets/archivo.js")}"></script>'


def pie(lang):
    return (f'<footer class="foot"><div class="wrap foot-in">'
            f'<p class="foot-brand">{simbolo("golem", " simbolo--golem")}<span class="foot-name">Golem Bench</span> '
            f'<span class="foot-lema">{"Preguntas desde el futuro" if lang == "es" else "Questions from the future"}</span></p>'
            f'<ul class="foot-links" role="list"><li><a href="https://antireallabs.com">{"Un proyecto de Anti-Real Labs" if lang == "es" else "A project by Anti-Real Labs"}</a></li>'
            f'<li><a href="mailto:admin@antireallabs.com">admin@antireallabs.com</a></li></ul>'
            f'<p class="foot-legal">© 2026 Anti-Real Labs S.A.S. · {e(CORTE)}</p></div></footer>')


def pagina(lang, ruta_es, ruta_en, titulo, descripcion, cuerpo, volver_href, volver_txt):
    otra = ruta_en if lang == "es" else ruta_es
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(titulo)}</title>
<meta name="description" content="{e(descripcion)}">
<link rel="canonical" href="https://golembench.org{ruta_es if lang == "es" else ruta_en}">
<link rel="alternate" hreflang="es" href="https://golembench.org{ruta_es}">
<link rel="alternate" hreflang="en" href="https://golembench.org{ruta_en}">
<meta name="theme-color" content="#f0ebdf">
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
{ESTILO}
</head>
<body class="lectura-x1">
{SPRITE}
<header class="rc-barra">
  <a class="rc-volver" href="{volver_href}"><span aria-hidden="true">←</span> {volver_txt}</a>
  <a class="rc-marca" href="{raiz(lang)}" aria-label="Golem Bench">{simbolo("golem", " simbolo--golem")}<span class="rc-marca-t">Golem Bench</span></a>
  <nav class="langs rc-langs" aria-label="{"Idioma" if lang == "es" else "Language"}">
    <a href="{ruta_es}" hreflang="es" lang="es"{' aria-current="page"' if lang == "es" else ""} aria-label="ES · Español">ES</a>
    <a href="{ruta_en}" hreflang="en" lang="en"{' aria-current="page"' if lang == "en" else ""} aria-label="EN · English">EN</a>
  </nav>
</header>
{cuerpo}
{pie(lang)}
{SCRIPT}
</body>
</html>
"""


def recorrido(t, lang):
    tid, conf, caso = t["id"], t["configuration"], t["case"]
    cs = CASO[caso]
    n = t["replicate"]
    modelo = nombre_modelo(conf)
    reg = REGISTRO[conf]
    fila = FILA[conf]
    lecturas_de = lambda clase: [l for l in t["public_judge_readings"] if l["kind"] == clase]
    secciones = []
    nav = []

    def lecturas(clases, fase_ev, titulo):
        crits = [c for k in clases for c in CLASES[k][1]]
        return (f'<section class="rc-lecturas"><h3 class="rc-lecturas-t">{titulo}</h3>'
                + "".join(bloque_criterio(t, c, lang, fase_ev) for c in crits) + "</section>")

    # A
    secciones.append(f'<section class="rc-etapa" id="etapa-a" aria-labelledby="etapa-a-t" data-etapa="A">'
                     f'<h2 class="rc-etapa-t" id="etapa-a-t">{e(L(FASE_NOMBRE["A"], lang))}</h2>'
                     f'{bloque_texto(t, "A", lang)}{lecturas(["A_J1", "A_J2"], "A", r("lecturas_t", lang))}</section>')
    nav.append(("etapa-a", "A"))
    # B
    secciones.append(f'<section class="rc-etapa" id="etapa-b" aria-labelledby="etapa-b-t" data-etapa="B">'
                     f'<h2 class="rc-etapa-t" id="etapa-b-t">{e(L(FASE_NOMBRE["B"], lang))}</h2>'
                     f'{bloque_texto(t, "B", lang)}{lecturas(["AB_J1", "AB_J2"], "A+B", r("lecturas_t", lang))}</section>')
    nav.append(("etapa-b", "B"))
    # las dos ramas
    ramas = ""
    for rama, cr in (("R1", "CR_R1"), ("R2", "CR_R2")):
        crit_info = t["critiques"][rama]
        ramas += (f'<section class="rc-rama" id="rama-{rama.lower()}" aria-labelledby="rama-{rama.lower()}-t" data-etapa="{rama}">'
                  f'<h3 class="rc-rama-t" id="rama-{rama.lower()}-t">{r("rama", lang, r=rama)}</h3>'
                  f'<div class="rc-critica" data-voz="critica"><p class="capa-rotulo">{r("voz_critica", lang)} · {rama}</p>'
                  f'<div class="rc-critica-texto" lang="es">{presentar(texto(crit_info["file"]))}</div>'
                  f'<p class="rc-critica-nota">{r("critica_nota", lang)} <a href="{url_metodo(lang)}#incidencias">{r("nota_completa", lang)}</a></p>'
                  f'<p class="rc-huella">{r("huella", lang)} · {e(crit_info["file"])} · <code>{e(crit_info["sha256"])}</code></p></div>'
                  f'{bloque_texto(t, rama, lang)}</section>')
        nav.append((f"rama-{rama.lower()}", rama))
    secciones.append(f'<section class="rc-etapa" id="etapa-r" aria-labelledby="etapa-r-t" data-etapa="R">'
                     f'<h2 class="rc-etapa-t" id="etapa-r-t">{e(L(FASE_NOMBRE["R"], lang))}</h2>{ramas}'
                     f'{lecturas(["R_J3"], "RAMAS", r("lecturas_ramas", lang))}</section>')
    # E
    info_e = t["visible_texts"]["E"]
    aviso_e = ""
    if not info_e["strict_ED02_accepted"]:
        aviso_e = (f'<div class="aviso-x1" role="note"><p class="capa-rotulo">{r("aviso", lang)}</p><p>{w("length_note", lang)}</p>'
                   f'<p><a href="{url_metodo(lang)}#incidencias">{r("nota_completa", lang)}</a></p></div>')
    secciones.append(f'<section class="rc-etapa" id="etapa-e" aria-labelledby="etapa-e-t" data-etapa="E">'
                     f'<h2 class="rc-etapa-t" id="etapa-e-t">{e(L(FASE_NOMBRE["E"], lang))}</h2>{aviso_e}'
                     f'<p class="rc-e-rama">{r("e_rama", lang, r=t["E_source_branch"])}</p>'
                     f'{material(IDX_CASO[caso]["transferencia"]["file"], lang, r("voz_caso", lang) + " · " + r("contraste", lang), "rc-material rc-material--t")}'
                     f'{bloque_texto(t, "E", lang)}{lecturas(["E_J3"], "E", r("lecturas_t", lang))}</section>')
    nav.append(("etapa-e", "E"))
    # el caso
    secciones.append(f'<section class="rc-etapa rc-etapa--caso" id="caso" aria-labelledby="caso-t">'
                     f'<h2 class="rc-etapa-t" id="caso-t">{r("el_caso", lang)} · {e(caso)}</h2>'
                     f'<p class="rc-caso-nota">{e(MAPA["case_status"][lang])}</p>'
                     f'<details class="desplegable"><summary>{r("expediente", lang)}</summary><div class="desplegable-cuerpo">'
                     f'{material(IDX_CASO[caso]["caso"]["file"], lang, r("voz_caso", lang) + " · " + r("expediente", lang))}</div></details>'
                     f'<details class="desplegable"><summary>{r("corpus", lang)}</summary><div class="desplegable-cuerpo">'
                     f'{material(IDX_CASO[caso]["corpus"]["file"], lang, r("voz_caso", lang) + " · " + r("corpus", lang))}</div></details></section>')
    nav.append(("caso", r("el_caso", lang)))

    ruta = "".join(f'<li><a href="#{ancla}">{e(et)}</a></li>' for ancla, et in nav)
    voces = "".join(f'<li class="rc-voz rc-voz--{k}">{r("voz_" + k, lang)}</li>' for k in ("modelo", "juez", "critica", "caso", "editorial"))
    esfuerzo = esfuerzo_de(conf, lang)
    cuerpo = f"""<main class="rc" id="contenido" data-recorrido="{slug(tid)}">
<header class="rc-cabeza">
  <p class="stamp stamp--estado">{r("badge", lang)}</p>
  <p class="eyebrow">{e(tid)}</p>
  <h1 class="rc-titulo"><span class="rc-modelo">{e(modelo)}</span> <span class="rc-caso-t">{e(cs["title_" + lang])}</span></h1>
  <p class="rc-sub">{r("recorrido_de", lang, n=n)} · {r("ficticio", lang)} {e(caso)} · {e(conf)} <span class="rc-ident">({r("conf_id", lang)}: {e(reg["label"])} · {r("esfuerzo", lang)} {e(esfuerzo)})</span></p>
  <div class="rc-preview" data-voz="editorial"><p class="capa-rotulo">{r("voz_editorial", lang)}</p><p>{e(cs["preview_" + lang])}</p></div>
  <ul class="rc-voces" role="list" aria-label="{"Las voces de esta página" if lang == "es" else "The voices on this page"}">{voces}</ul>
  <p class="rc-avisos">{e(MAPA["case_status"][lang])} {w("language_note", lang)} <a href="{url_metodo(lang)}#incidencias">{r("nota_completa", lang)}</a></p>
</header>
<nav class="rc-ruta" aria-label="{r("ruta_aria", lang)}"><ol role="list">{ruta}</ol></nav>
{"".join(secciones)}
</main>"""
    titulo = f"{modelo} · {cs['title_' + lang]} · {r('recorrido_n', lang, n=n)} · {EDICION} · Golem Bench"
    desc = f"{cs['preview_' + lang]} {r('badge', lang)}."
    return pagina(lang, url_recorrido(tid, "es"), url_recorrido(tid, "en"), titulo, desc, cuerpo,
                  f"{raiz(lang)}#x1-recorridos", r("volver_lab", lang))



# ---------------------------------------------------------------- método y materiales

def nota_incidencias(lang, ident="incidencias", panel=False):
    """La nota pública de incidencias, completa y tal cual, en su idioma."""
    n = NOTA[lang]
    cuerpo = (f'<p class="capa-rotulo">{r("voz_editorial", lang)}</p><p class="nota-x1-texto">{e(n["text"])}</p>'
              f'<p class="nota-x1-texto">{e(L(S["desviaciones"], lang))}</p>')
    if panel:
        return (f'<details class="desplegable" id="{ident}"><summary>{e(n["title"])}</summary><div class="desplegable-cuerpo">'
                f'<div class="panel-contenido nota-x1" data-panel-titulo="{e(n["title"])}" data-voz="editorial">{cuerpo}</div></div></details>')
    return (f'<section class="nota-x1 metodo-bloque" id="{ident}" aria-labelledby="{ident}-t" data-voz="editorial">'
            f'<h2 class="sub-titulo" id="{ident}-t">{e(n["title"])}</h2>{cuerpo}</section>')


def cifras_panel(lang):
    filas = [
        ("registered_configurations", "Configuraciones registradas", "Registered configurations", "2 admitidas y comparadas; 2 no admitidas, sin nota ni posición.", "2 admitted and compared; 2 not admitted, with no score or position."),
        ("trajectories", "Recorridos", "Runs", "2 configuraciones × 3 casos × 2 recorridos.", "2 configurations × 3 cases × 2 runs."),
        ("visible_texts", "Textos analizados", "Texts examined", L(S["textos"], "es") + " " + L(S["estricto"], "es"), L(S["textos"], "en") + " " + L(S["estricto"], "en")),
        ("critiques", "Críticas", "Critiques", "Dos por recorrido.", "Two per run."),
        ("selected_judge_bodies", "Lecturas (cuerpos de dictamen)", "Readings (judgment bodies)", f'{CTA["original_ED02_judge_bodies"]} originales de ED02 y {CTA["X1_judge_bodies"]} del suplemento X1.', f'{CTA["original_ED02_judge_bodies"]} original ED02 bodies and {CTA["X1_judge_bodies"]} from the X1 supplement.'),
        (None, "Niveles", "Levels", f'{CTA["original_levels"]} originales y {CTA["supplemental_levels"]} suplementarios: 16 criterios × 2 motores × 12 recorridos.', f'{CTA["original_levels"]} original and {CTA["supplemental_levels"]} supplemental: 16 criteria × 2 engines × 12 runs.'),
        ("sensitivity_orders", "Escenarios de sensibilidad", "Sensitivity scenarios", L(S["escenarios"], "es"), L(S["escenarios"], "en")),
        ("verified_cited_fragments", "Registros de cita verificados", "Verified citation records", f"Agrupados por fuente, etapa y posición (la misma frase citada con o sin sus marcas de énfasis cuenta una vez), son {len(GRUPOS)} pasajes distintos. Ninguna de las dos cifras cuenta ideas.", f"Grouped by source, stage and position (the same sentence cited with or without its emphasis marks counts once), they make {len(GRUPOS)} distinct passages. Neither figure counts ideas."),
        (None, "Referencias no promovidas", "Unpromoted references", f'{len(DIAG["items"])} citas de los dictámenes que no son pasajes evaluados en su lectura: se muestran dentro del dictamen y nunca se destacan.', f'{len(DIAG["items"])} judgment citations that are not passages evaluated in their reading: shown inside the judgment and never highlighted.'),
    ]
    items = ""
    for clave, es_t, en_t, es_d, en_d in filas:
        if clave is None:
            v = CTA["original_levels"] + CTA["supplemental_levels"] if es_t == "Niveles" else len(DIAG["items"])
        else:
            v = CTA[clave]
        items += f'<div><dt><span class="cifra-s">{v}</span> {e(es_t if lang == "es" else en_t)}</dt><dd>{e(es_d if lang == "es" else en_d)}</dd></div>'
    return f'<dl class="definiciones definiciones--x1">{items}</dl>'


def metodo(lang):
    m = IDX["methodology"][lang]
    puntos = "".join(f"<li>{e(v)}</li>" for v in (m["scope"], m["E351"], m["arithmetic"], m["editorial"], m["fragments"], m["public_sources"]))
    mats = (("RUBRICA", "materiales_comunes/RUBRICA.txt"), ("GUIA", "materiales_comunes/GUIA.txt"), ("COND", "materiales_comunes/COND.txt"),
            ("CONS_A", "materiales_comunes/CONS_A.txt"), ("CONS_B", "materiales_comunes/CONS_B.txt"), ("CONS_R1", "materiales_comunes/CONS_R1.txt"),
            ("CONS_E", "materiales_comunes/CONS_E.txt"))
    detalles = ""
    for clave, rel in mats:
        primera = texto(rel).splitlines()[0]
        detalles += (f'<details class="desplegable" id="material-{clave.lower().replace("_", "-")}"><summary><span lang="es">{e(primera)}</span></summary>'
                     f'<div class="desplegable-cuerpo">{material(rel, lang, r("voz_comun", lang))}'
                     + ("<p class=\"rc-material-nota\">La consigna R es la misma en las dos ramas.</p>" if clave == "CONS_R1" and lang == "es" else
                        "<p class=\"rc-material-nota\">Instruction R is the same in both branches.</p>" if clave == "CONS_R1" else "")
                     + "</div></details>")
    recs = lista_recorridos(lang, "h3")
    cuerpo = f"""<main class="rc rc--metodo" id="contenido">
<header class="rc-cabeza">
  <p class="stamp stamp--estado">{r("badge", lang)}</p>
  <h1 class="rc-titulo">{r("metodo_pag", lang)}</h1>
  <p class="rc-sub">{e(NOTA["release_label"][lang])}</p>
  <p class="rc-avisos">{w("language_note", lang)}</p>
</header>
<section class="metodo-bloque" aria-labelledby="que-es-t"><h2 class="sub-titulo" id="que-es-t">{r("metodo_x1_t", lang)}</h2><ul class="limites-lista" role="list">{puntos}</ul></section>
{nota_incidencias(lang)}
<section class="metodo-bloque" aria-labelledby="cifras-t"><h2 class="sub-titulo" id="cifras-t">{r("cifras_t", lang)}</h2>{cifras_panel(lang)}</section>
<section class="metodo-bloque" aria-labelledby="materiales-t"><h2 class="sub-titulo" id="materiales-t">{r("materiales_t", lang)}</h2>
<p class="rc-caso-nota">{r("materiales_nota", lang)}</p><div class="desplegables desplegables--x1">{detalles}</div></section>
<section class="metodo-bloque" aria-labelledby="recorridos-t"><h2 class="sub-titulo" id="recorridos-t">{r("casos_t", lang)}</h2>{recs}</section>
</main>"""
    titulo = f"{r('metodo_pag', lang)} · Golem Bench"
    return pagina(lang, url_metodo("es"), url_metodo("en"), titulo, NOTA["release_label"][lang], cuerpo,
                  f"{raiz(lang)}#x1-medimos", r("volver_metodo", lang))


# ---------------------------------------------------------------- la portada: piezas de ED02-X1

DESTINO = {"preguntas": "#apuestas", "laboratorio": "#laboratorio", "resultados": "#resultados", "como-medimos": "#como-medimos"}
FLECHA = {"preguntas": "↑", "laboratorio": "→", "resultados": "↓", "como-medimos": "←"}
SIMB = {"preguntas": "preguntas", "laboratorio": "laboratorio", "resultados": "resultados", "como-medimos": "medimos"}


def cuadro(qid, lang):
    return WEB[lang]["quadrants"][SPLIT_SALA[qid]]


def enlace(qid, lang, clase):
    f, txt = FLECHA[qid], e(cuadro(qid, lang)["cta"])
    cuerpo = f'{txt} <span aria-hidden="true">{f}</span>' if f == "→" else f'<span aria-hidden="true">{f}</span> {txt}'
    return f'<a class="{clase}" href="{DESTINO[qid]}">{cuerpo}</a>'


def rotulo(qid, lang, clase):
    return f'<p class="{clase}">{simbolo(SIMB[qid])}<span>{r("rotulo_" + qid, lang)}</span></p>'


def primero_para(motor):
    """La configuración que cada motor pone primero, leída del índice publicado (no se recalcula)."""
    campo = "judge_GPT_index" if motor == "JG" else "judge_Claude_index"
    return max(FILAS, key=lambda x: x[campo])["configuration"]


assert primero_para("JG") == "M04" and primero_para("JC") == "M03"


def fila_mini(conf, lang):
    f = FILA[conf]
    gana_g, gana_c = primero_para("JG") == conf, primero_para("JC") == conf
    return (f'<tr><th scope="row">{e(f["model"])}</th><td class="x1-num">{num(f["primary_index"], lang)}</td>'
            f'<td class="x1-num{" x1-num--primero" if gana_g else ""}">{num(f["judge_GPT_index"], lang)}</td>'
            f'<td class="x1-num{" x1-num--primero" if gana_c else ""}">{num(f["judge_Claude_index"], lang)}</td></tr>')


def tabla_mini(lang):
    """Las mismas cifras del índice, con los dos motores al lado. El orden de las filas es el del índice combinado."""
    filas = "".join(fila_mini(f["configuration"], lang) for f in sorted(FILAS, key=lambda x: x["position_in_primary_index"]))
    return (f'<table class="x1-mini"><caption class="sr-only">{r("orden", lang)} · {w("ranking_title", lang)}</caption>'
            f'<thead><tr><th scope="col"><span class="sr-only">{r("configuracion", lang)}</span></th><th scope="col">{r("combinado", lang)}</th>'
            f'<th scope="col">{r("motor_JG", lang)}</th><th scope="col">{r("motor_JC", lang)}</th></tr></thead><tbody>{filas}</tbody></table>'
            f'<p class="x1-mini-ley"><span class="x1-mini-punto" aria-hidden="true"></span>{r("primero_cada", lang)}</p>')


# el carrusel: un pasaje por texto, en el orden fijo de registro (configuración, caso, recorrido, etapa)
CARRUSEL = []
for conf in CONFIGS:
    for t in sorted((x for x in TRAY if x["configuration"] == conf), key=lambda x: (x["case"], x["replicate"])):
        for fase in FASES:
            p = carrusel_de(t["visible_texts"][fase]["file"])
            CARRUSEL.append((t, fase, p))
assert len(CARRUSEL) == 60


def pasaje_card(t, fase, p, lang, visible):
    url = url_recorrido(t["id"], lang)
    cs = CASO[t["case"]]
    etapa = "R" if fase in ("R1", "R2") else fase
    trad = f'<span class="f-traduccion">{r("original_es", lang)}</span>' if lang == "en" else ""
    cita = cita_html(p["vista"])
    return (f'<div class="fragmento fragmento--x1" data-fragmento="{slug(t["id"])}:{p["pid"]}"{"" if visible else " hidden"}>'
            f'<p class="f-tipo">{r("carrusel_t", lang)}</p>'
            f'<figure class="f-figura"><blockquote class="f-cita" data-voz="modelo" lang="es"><p>{cita}</p></blockquote>'
            f'<figcaption class="f-autoria"><span class="f-voz">{r("voz_modelo", lang)}</span> '
            f'<span class="f-quien">{e(nombre_modelo(t["configuration"]))} · {e(t["configuration"])}</span> '
            f'<span class="f-caso">{e(t["case"])} · {e(cs["title_" + lang])} · {r("recorrido_n", lang, n=t["replicate"])} · {r("etapa", lang)} {fase}'
            f' <span class="f-sep" aria-hidden="true">·</span> <a class="f-leer" href="{url}#{p["pid"]}" data-x1-pasaje="{url}#{p["pid"]}">{r("leer_contexto", lang)}</a></span>'
            f'{trad}</figcaption></figure></div>')


def rotador(lang, clave):
    """Sin JavaScript queda quieto el primer pasaje; con él, archivo.js trae los 60 de la plantilla (#x1-pasajes),
    los baraja una vez por visita y se avanzan a mano."""
    t0, fase0, p0 = CARRUSEL[0]
    figs = pasaje_card(t0, fase0, p0, lang, True)
    return (f'<div class="rotador rotador--x1" data-rotador="{clave}" data-coleccion="x1" data-plantilla="x1-pasajes">'
            f'<div class="rot-pila">{figs}</div>'
            f'<div class="rot-controles" data-rot-controles hidden>'
            f'<button type="button" class="rot-btn" data-rot="-1" aria-label="{r("anterior", lang)}"><span aria-hidden="true">←</span></button>'
            f'<p class="rot-cuenta" aria-live="polite" aria-atomic="true"><span class="sr-only">{r("cuenta_pre", lang)} </span>'
            f'<span data-n>1</span> {r("cuenta_de", lang)} <span data-t>{len(CARRUSEL)}</span></p>'
            f'<button type="button" class="rot-btn" data-rot="1" aria-label="{r("siguiente", lang)}"><span aria-hidden="true">→</span></button>'
            f'</div></div>')


# Las palabras de las dos muestras de la izquierda salen del texto del paquete, tal cual (en minúscula).
PESA = {"es": ("formulación", "fecundidad", "revisión"), "en": ("formulation", "fruitfulness", "revision")}
VERBOS = {"es": ("comprender", "crear", "revisar"), "en": ("understand", "create", "revise")}
for _l in ("es", "en"):
    assert all(x in WEB[_l]["quadrants"]["preguntas_abiertas"]["preview"].lower() for x in PESA[_l]), _l
    assert all(x in WEB[_l]["quadrants"]["como_medimos"]["preview"].lower() and x in AJUSTES["medimos_esquina"][_l].lower()
               for x in VERBOS[_l]), _l
assert [p["id"] for p in MAPA["perspectives"]] == ["J1", "J2", "J3"] and all(w == "1/3" for w in (p["weight"] for p in MAPA["perspectives"]))


def pesa_preguntas(lang):
    """El 30 % de las preguntas, dibujado sin cifras (revisión de la portada, 20 oct 2026: los tres «peso 30»
    junto al «30 %» confundían). La barra es el índice, partida en sus tres especialidades, que valen un tercio
    cada una; en cada tercio, en burdeos y con su «?», la parte de su criterio de la pregunta: 30 de 100 dentro de
    la especialidad (el 30 % del ancho de cada tercio, en portada.css). Repite en dibujo lo que dice el texto de al
    lado: va oculta a los lectores de pantalla."""
    partes = "".join(f'<li class="pesa-tercio">{simbolo("preguntas", " pesa-signo")}<span class="pesa-tramo"></span>'
                     f'<span class="pesa-l">{e(n)}</span></li>' for n in PESA[lang])
    return f'<figure class="pesa" aria-hidden="true"><ul class="pesa-barra">{partes}</ul></figure>'


def lee_motores(lang):
    """Tres especialidades, dos motores (revisión de la portada, 20 oct 2026): los sellos J1, J2 y J3 con su verbo,
    sin nombres completos ni pesos (viven en Cómo medimos), y en cada motor una hoja con renglones: una lectura
    con sus razones. Los motores van en el mismo orden que en la tabla de resultados."""
    filas = "".join(
        f'<tr><th scope="row"><span class="lee-esp"><span class="seal seal--lee" aria-hidden="true">{p["id"]}</span>'
        f'<span class="lee-v"><span class="sr-only">{p["id"]} · </span>{e(v)}</span></span></th>'
        + "".join(f'<td><span class="lee-hoja" aria-hidden="true"></span><span class="sr-only">{r("puntua", lang)}</span></td>' for _ in MOTORES)
        + "</tr>" for p, v in zip(MAPA["perspectives"], VERBOS[lang]))
    cab = "".join(f'<th scope="col">{r("motor_" + m, lang)}</th>' for m in MOTORES)
    return (f'<table class="lee"><caption class="sr-only">{r("lee_t", lang)}</caption>'
            f'<thead><tr><td></td>{cab}</tr></thead><tbody>{filas}</tbody></table>')


def muestra(qid, lang, ancho):
    """La muestra de cada esquina: lo que pesan las preguntas, un pasaje, las cifras con sus dos motores y quién
    puntúa cada especialidad. Ninguna repite los nombres completos de J1, J2 y J3 ni sus pesos: viven en Cómo
    medimos (revisión de la portada, 20 oct 2026)."""
    if qid == "preguntas":
        return pesa_preguntas(lang)
    if qid == "laboratorio":
        return rotador(lang, f"x1-{ancho}")
    if qid == "resultados":
        return f'<p class="stamp stamp--estado">{r("badge", lang)}</p>' + tabla_mini(lang)
    if qid == "como-medimos":
        return lee_motores(lang)
    return ""


def cuerpo(qid, lang):
    """El texto de cada esquina y de su tráiler: del paquete, salvo lo que la revisión acortó."""
    if qid == "laboratorio":
        return aj("laboratorio", lang)
    if qid == "como-medimos":
        return aj("medimos_esquina", lang)
    if qid == "resultados":
        return con_giro(cuadro(qid, lang)["preview"], lang)
    return e(cuadro(qid, lang)["preview"])


def resumen(qid, lang):
    """La baldosa de cada estación en el celular (Juan, 20 oct 2026): un resumen pequeño, concreto y visual en la
    vista inicial. Preguntas: los seis principios, una palabra de cada apuesta. Laboratorio: las cuatro unidades.
    Cómo medimos: J1–J3 con su verbo y su peso, y los dos motores que puntúan. Resultados: el orden del índice
    combinado con la frase del paquete que dice el desacuerdo. En el escritorio no se ve: ahí va el tráiler entero."""
    if qid == "preguntas":
        palabras = "".join(f"<li>{e(p)}</li>" for p in PRINCIPIOS[lang])
        cuerpo = f'<p class="res-t">{r("res_apuestas", lang)}</p><ul class="res-palabras">{palabras}</ul>'
    elif qid == "laboratorio":
        uds = (("trajectories", "u_recorridos"), ("visible_texts", "u_textos_corto"), ("critiques", "u_criticas"), ("selected_judge_bodies", "u_lecturas"))
        cuerpo = '<ul class="res-cifras">' + "".join(f'<li><span class="res-n">{CTA[k]}</span> <span class="res-l">{r(rot, lang)}</span></li>' for k, rot in uds) + "</ul>"
    elif qid == "como-medimos":
        filas = "".join(f'<li><span class="seal seal--res" aria-hidden="true">{p["id"]}</span><span class="res-v"><span class="sr-only">{p["id"]} · </span>{e(v)}</span> '
                        f'<span class="res-p">{e(p["weight"])}</span></li>' for p, v in zip(MAPA["perspectives"], VERBOS[lang]))
        cuerpo = f'<ul class="res-esp">{filas}</ul><p class="res-t">{r("res_motores", lang)}: GPT · Claude</p>'
    else:
        filas = "".join(f'<li><span class="res-pos">{f["position_in_primary_index"]}</span> <span class="res-m">{e(f["model"])}</span> '
                        f'<span class="res-n">{num(f["primary_index"], lang)}</span></li>'
                        for f in sorted(FILAS, key=lambda x: x["position_in_primary_index"]))
        cuerpo = f'<p class="res-t">{r("combinado", lang)}</p><ol class="res-orden">{filas}</ol><p class="res-giro">{e(GIRO[lang])}</p>'
    return f'<div class="q-resumen res res--{qid}">{cuerpo}</div>'


def cuadrante(qid, lang, pos):
    q = cuadro(qid, lang)
    m = muestra(qid, lang, "q")
    return (f'<div class="cuadrante cuadrante--{pos} q q--{qid} q--x1">'
            f'{resumen(qid, lang)}'
            f'{rotulo(qid, lang, "q-rotulo")}'
            f'<h2 class="q-titular">{e(q["title"])}</h2>'
            f'<p class="q-cuerpo">{cuerpo(qid, lang)}</p>'
            + (f'<div class="q-muestra">{m}</div>' if m else "") +
            f'{enlace(qid, lang, "q-enlace")}</div>')


def trailers(lang):
    """En el celular, los cuatro tráileres apilados debajo del centro: preguntas → laboratorio → resultados → método."""
    arts = []
    for qid in ("preguntas", "laboratorio", "resultados", "como-medimos"):
        q = cuadro(qid, lang)
        tid = f"tr-{qid}"
        extra = ""
        if qid == "resultados":
            extra = (f'<p class="tr-aviso">{w("sensitivity_note", lang)}</p>'
                     f'<p class="tr-aviso">{w("length_note", lang)} '
                     f'<a href="#x1-incidencias" data-panel="x1-incidencias">{r("nota_completa", lang)}</a></p>')
        m = muestra(qid, lang, "tr")
        arts.append(f'<article class="trailer trailer--{qid}" aria-labelledby="{tid}">'
                    f'{rotulo(qid, lang, "tr-rotulo")}'
                    f'<h3 class="tr-titular" id="{tid}">{e(q["title"])}</h3>'
                    f'<p class="tr-cuerpo">{cuerpo(qid, lang)}</p>'
                    + (f'<div class="tr-muestra">{m}</div>' if m else "") + extra +
                    f'{enlace(qid, lang, "tr-enlace")}</article>')
    titulo = "Los cuatro rumbos" if lang == "es" else "The four bearings"
    return (f'<section class="trailers" aria-labelledby="trailers-t"><h2 class="sr-only" id="trailers-t">{titulo}</h2>\n      '
            + "\n      ".join(arts) + "\n    </section>")


def placa(lang):
    return f'<p class="placa-estado">{r("badge", lang)}</p>'


# ---------------------------------------------------------------- ↓ resultados

def tabla_orden(lang):
    """La tabla del orden condicional. En el celular cada fila se lee como una tarjeta: los roles ARIA mantienen la
    tabla para los lectores de pantalla aunque cambie su forma, y la etiqueta de cada cifra (.x1-l) solo se ve ahí
    (para los lectores ya la dice el encabezado de su columna)."""
    filas = ""
    etiqueta = lambda k: f'<span class="x1-l" aria-hidden="true">{r(k, lang)}</span>'
    for f in sorted(FILAS, key=lambda x: x["position_in_primary_index"]):
        c = f["configuration"]
        prim_g, prim_c = primero_para("JG") == c, primero_para("JC") == c
        marca = f' <span class="x1-primero">{r("primero_motor", lang)}</span>'
        filas += (f'<tr role="row"><th scope="row" class="x1-pos" role="rowheader">{f["position_in_primary_index"]}</th>'
                  f'<td class="x1-cfg" role="cell"><span class="x1-modelo">{e(f["model"])}</span> <span class="x1-conf">{e(c)} · {r("esfuerzo", lang)} {e(esfuerzo_de(c, lang))}</span></td>'
                  f'<td class="x1-num x1-num--combinado" role="cell">{num(f["primary_index"], lang)}{etiqueta("combinado")}</td>'
                  f'<td class="x1-num{" x1-num--primero" if prim_g else ""} x1-num--jg" role="cell">{num(f["judge_GPT_index"], lang)}{marca if prim_g else ""}{etiqueta("juez_JG")}</td>'
                  f'<td class="x1-num{" x1-num--primero" if prim_c else ""} x1-num--jc" role="cell">{num(f["judge_Claude_index"], lang)}{marca if prim_c else ""}{etiqueta("juez_JC")}</td></tr>')
    exactos = "; ".join(f'{e(FILA[c]["model"])} {A["primary_comparison"]["scores"][c]["exact"]}'
                        for c in sorted(CONFIGS, key=lambda c: FILA[c]["position_in_primary_index"]))
    # junto a las cifras, encima de las dos columnas de los motores: la frase del paquete que dice el desacuerdo
    giro = e(GIRO[lang].rstrip("."))
    # en el celular la franja va encima de las tarjetas (la cabecera se guarda): la misma frase, solo a la vista
    return (f'<div class="x1-tabla-caja" role="region" tabindex="0" aria-labelledby="x1-tabla-cap">'
            f'<p class="x1-giro-movil" aria-hidden="true">{giro}</p>'
            f'<table class="x1-tabla" role="table"><caption id="x1-tabla-cap">{e(L(S["indice"], lang))}</caption>'
            f'<colgroup><col span="3"><col span="2" class="x1-col-motores"></colgroup>'
            f'<thead role="rowgroup"><tr role="row"><th scope="col" rowspan="2" role="columnheader">{r("orden", lang)}</th>'
            f'<th scope="col" rowspan="2" role="columnheader">{r("configuracion", lang)}</th>'
            f'<th scope="col" rowspan="2" role="columnheader">{r("combinado", lang)}</th>'
            f'<th scope="colgroup" colspan="2" class="x1-giro-th" role="columnheader"><span class="x1-giro-t">{giro}</span></th></tr>'
            f'<tr role="row"><th scope="col" role="columnheader">{r("juez_JG", lang)}</th><th scope="col" role="columnheader">{r("juez_JC", lang)}</th></tr></thead>'
            f'<tbody role="rowgroup">{filas}</tbody></table></div>'
            f'<p class="x1-exactos">{r("exactos", lang, a=exactos)}</p>')


def escenarios(lang):
    """Los 42 escenarios, tal como los publica el índice, partidos por motor: 7 juegos de pesos × 3 conversiones."""
    runs = A["sensitivity_runs"]
    grupos = ""
    for motor in MOTORES:
        celdas = ""
        for rr in sorted((x for x in runs if x["engine"] == motor), key=lambda x: (x["weight_variant"], x["recoding_variant"])):
            primero = next(c for c in CONFIGS if rr["ranks"][c] == 1)
            pesos = " · ".join(rr["specialty_weights_exact"])
            conv = " · ".join(rr["ordinal_recoding_exact"])
            celdas += (f'<li class="esc esc--{primero.lower()}" title="{e(pesos)} | {e(conv)}">'
                       f'<span class="sr-only">{e(r("esc_celda", lang, p=nombre_modelo(primero)))}</span></li>')
        cuenta = collections.Counter(next(c for c in CONFIGS if x["ranks"][c] == 1) for x in runs if x["engine"] == motor)
        resumen = ", ".join(f"{nombre_modelo(c)} {r('esc_celda', lang, p='').strip()} {n}/21" for c, n in cuenta.items())
        grupos += (f'<figure class="esc-grupo"><figcaption class="esc-motor">{e(r("esc_motor", lang, m=r("juez_" + motor, lang)))}</figcaption>'
                   f'<ul class="esc-rejilla" role="list" aria-label="{e(r("esc_motor", lang, m=r("juez_" + motor, lang)) + ": " + resumen)}">{celdas}</ul></figure>')
    leyenda = "".join(f'<li><span class="esc esc--{c.lower()}" aria-hidden="true"></span> {e(r("esc_celda", lang, p=nombre_modelo(c)))}</li>' for c in ("M04", "M03"))
    return (f'<div class="x1-esc">{grupos}</div><p class="esc-ejes">{r("esc_ejes", lang)}</p>'
            f'<ul class="esc-leyenda" role="list">{leyenda}</ul>')


def perfiles(lang):
    prof = WEB["pooled_specialty_profiles"]
    casos = WEB["pooled_case_profiles"]
    eng = A["engine_profiles"]
    cab = "".join(f'<th scope="col" colspan="3">{e(nombre_modelo(c))}</th>' for c in CONFIGS)
    sub = "".join(f'<th scope="col">{r("media_motores", lang)}</th><th scope="col">{r("motor_JG", lang)}</th><th scope="col">{r("motor_JC", lang)}</th>' for _ in CONFIGS)

    def tabla(titulo, filas_def, ident):
        filas = ""
        for etiqueta, clave, fuente_media, fuente_motor in filas_def:
            celdas = ""
            for c in CONFIGS:
                celdas += (f'<td class="x1-num">{num(fuente_media[c][clave]["display_one_decimal"], lang)}</td>'
                           f'<td class="x1-num">{num(fuente_motor("JG", c, clave), lang)}</td><td class="x1-num">{num(fuente_motor("JC", c, clave), lang)}</td>')
            filas += f'<tr><th scope="row">{etiqueta}</th>{celdas}</tr>'
        return (f'<div class="tabla-caja" role="region" tabindex="0" aria-labelledby="{ident}"><table class="criterios x1-perfil"><caption id="{ident}">{titulo}</caption>'
                f'<thead><tr><th scope="col" rowspan="2">{titulo}</th>{cab}</tr><tr>{sub}</tr></thead><tbody>{filas}</tbody></table></div>')

    esp = tabla(r("especialidad", lang), [(f'{p["id"]} · {e(p["title_" + lang])}', p["id"], prof,
                                             lambda m, c, k: eng[m][c]["specialty_profiles_0_100"][k]["display_one_decimal"]) for p in MAPA["perspectives"]], "x1-perfil-esp")
    cas = tabla(r("caso", lang), [(f'{cid} · {e(CASO[cid]["title_" + lang])}', cid, casos,
                                     lambda m, c, k: eng[m][c]["case_indices"][k]["display_one_decimal"]) for cid in sorted(CASO)], "x1-perfil-caso")
    return (f'<details class="desplegable x1-perfiles"><summary>{r("perfiles_t", lang)}</summary><div class="desplegable-cuerpo">'
            f'<p>{e(WEB["profiles_note"][lang])}</p>{esp}{cas}</div></details>')


def fuera_del_indice(lang):
    items = ""
    for c in ("M01", "M02"):
        reg = REGISTRO[c]
        assert reg["admitted_to_execution"] is False and reg["enabled_trajectories"] == 0
        items += (f'<li class="x1-fuera-item"><span class="x1-modelo">{e(reg["label"].split("/")[-1])}</span> '
                  f'<span class="x1-conf">{e(c)} · {e(reg["label"])}</span> <span class="x1-fuera-e">{r("no_admitida", lang)}</span></li>')
    items += (f'<li class="x1-fuera-item"><span class="x1-modelo">Gemini</span> <span class="x1-fuera-e x1-fuera-e--pendiente">{r("pendiente_gemini", lang)}</span></li>')
    return (f'<section class="x1-fuera" aria-labelledby="x1-fuera-t"><h4 class="sub-titulo" id="x1-fuera-t">{r("no_admitidas_t", lang)}</h4>'
            f'<ul class="x1-fuera-lista" role="list">{items}</ul>'
            f'<p class="x1-fuera-nota">{e(L(S["no_admitidas"], lang))}</p></section>')


def aviso(lang, extra=""):
    return (f'<aside class="aviso-x1" aria-label="{r("aviso", lang)}"><p class="capa-rotulo">{r("aviso", lang)}</p>'
            f'<p>{w("length_note", lang)}</p><p>{e(L(S["textos"], lang))} {e(L(S["estricto"], lang))}</p>'
            f'<p>{e(L(S["desviaciones"], lang))}</p>'
            f'<p><a class="f-leer" href="#x1-incidencias" data-panel="x1-incidencias">{r("nota_completa", lang)}</a></p>{extra}</aside>')


def resultados(lang):
    """La sala de resultados empieza por el orden (Juan, 20 oct 2026: quien llega quiere ver primero el resultado y
    después leer). Antes de la tabla, solo la etiqueta del piloto y el titular; pegadas a ella, la frase del giro y
    la advertencia del porcentaje; justo debajo, la nota del orden, el alcance y el corte."""
    limites = "".join(f"<li>{x}</li>" for x in (w("question_note", lang), w("originality_note", lang), e(L(S["esfuerzo"], lang)) + " " + e(L(S["computo"], lang)), w("language_note", lang)))
    eyebrow = CORTE if lang == "es" else "Cutoff: 18 October 2026, America/Bogota. Fictional cases; real responses."
    return f"""<section class="sec sec--resultados sec--x1" id="resultados" aria-labelledby="t-resultados">
      <div class="wrap">
        <h2 class="sr-only" id="t-resultados">{"Resultados de evaluaciones" if lang == "es" else "Evaluation results"}</h2>
        {simbolo("resultados", " simbolo--sala")}
        <p class="stamp stamp--estado x1-badge">{r("badge", lang)}</p>
        <h3 class="sec-titulo">{w("headline", lang)}</h3>

        <section class="x1-orden" aria-labelledby="x1-orden-t">
          <h4 class="sub-titulo" id="x1-orden-t">{w("ranking_title", lang)}</h4>
          {tabla_orden(lang)}
          <p class="x1-nota">{w("ranking_note", lang)}</p>
          <p class="x1-nota x1-alcance">{w("scope", lang)}</p>
          <p class="eyebrow x1-corte">{e(eyebrow)}</p>
        </section>

        <section class="x1-sensibilidad" aria-labelledby="x1-esc-t">
          <h4 class="sub-titulo" id="x1-esc-t">{r("esc_t", lang)}</h4>
          <p class="x1-nota">{w("sensitivity_note", lang)}</p>
          {escenarios(lang)}
          <p class="x1-lectura">{r("esc_lectura", lang)}</p>
          <p class="x1-nota x1-nota--sesgo">{w("bias_note", lang)}</p>
        </section>

        {aviso(lang)}

        {fuera_del_indice(lang)}

        <section class="x1-limites" aria-labelledby="x1-lim-t">
          <h4 class="sub-titulo" id="x1-lim-t">{r("limites_t", lang)}</h4>
          <ul class="limites-lista" role="list">{limites}</ul>
          {perfiles(lang)}
        </section>
        <p class="ir-dos"><a href="#x1-recorridos"><span aria-hidden="true">→</span> {r("ir_lecturas", lang)}</a></p>
      </div>
    </section>"""


# ---------------------------------------------------------------- → laboratorio

def unidades(lang):
    """Cada unidad una sola vez: la cifra, su nombre y qué cuenta. La definición de los textos es la frase del
    resumen desde sus dos puntos: la cifra ya está arriba (revisión de la portada, 20 oct 2026)."""
    textos = L(S["textos"], lang)
    assert textos.count(": ") == 1, textos
    defs = (("trajectories", "u_recorridos", r("u_recorridos_d", lang)), ("visible_texts", "u_textos", e(textos.split(": ")[1])),
            ("critiques", "u_criticas", r("u_criticas_d", lang)), ("selected_judge_bodies", "u_lecturas", r("u_lecturas_d", lang)))
    items = "".join(f'<li><span class="cifra">{CTA[k]}</span> <span class="cifra-l">{r(rot, lang)}</span>'
                    f'<span class="cifra-d">{d}</span></li>' for k, rot, d in defs)
    return f'<div class="cifras cifras--x1"><ul class="cifras-lista" role="list">{items}</ul></div>'


def lista_recorridos(lang, h="h5"):
    casos = ""
    for cid in sorted(CASO):
        cs = CASO[cid]
        filas = ""
        for conf in CONFIGS:
            enlaces = "".join(f'<a class="x1-rec-a" href="{url_recorrido(t["id"], lang)}">{r("recorrido_n", lang, n=t["replicate"])}</a>'
                              for t in sorted((x for x in TRAY if x["configuration"] == conf and x["case"] == cid), key=lambda x: x["replicate"]))
            filas += f'<li><span class="x1-rec-modelo">{e(nombre_modelo(conf))}</span> {enlaces}</li>'
        casos += (f'<li class="x1-caso"><p class="x1-caso-id">{e(cid)} · {r("ficticio", lang)}</p><{h} class="x1-caso-t">{e(cs["title_" + lang])}</{h}>'
                  f'<p class="x1-caso-pre">{e(cs["preview_" + lang])}</p><ul class="x1-rec" role="list">{filas}</ul></li>')
    return (f'<p class="cohorte-orden">{r("casos_orden", lang)}</p><ul class="x1-casos-lista" role="list">{casos}</ul>')


def lab(lang):
    """Lo disponible primero: el pasaje, las cuatro unidades y los doce recorridos (revisión del 20 oct 2026).
    El procedimiento exacto del carrusel queda en un desplegable debajo de él."""
    q = cuadro("laboratorio", lang)
    como = (f'<details class="desplegable x1-como"><summary>{aj("carrusel_como", lang)}</summary><div class="desplegable-cuerpo">'
            f'<p>{r("carrusel_regla", lang)}</p><p>{e(L(S["fragmentos"], lang))} {e(L(S["novedad"], lang))}</p></div></details>')
    return f"""<section class="lab-bloque x1-lab" id="x1-laboratorio" aria-labelledby="x1-lab-t">
              <p class="stamp stamp--estado x1-badge">{r("badge", lang)}</p>
              <h3 class="lab-h" id="x1-lab-t">{e(q["title"])}</h3>
              <p class="lab-lead">{aj("laboratorio", lang)}</p>
              <section class="x1-voces" aria-labelledby="x1-voces-t">
                <h4 class="sub-titulo" id="x1-voces-t">{r("carrusel_t", lang)}</h4>
                <p class="voces-nota">{aj("carrusel", lang)}</p>
                {rotador(lang, "x1-sala")}
                {como}
              </section>
              <section class="x1-unidades" aria-labelledby="x1-unidades-t"><h4 class="sr-only" id="x1-unidades-t">{r("unidades_t", lang)}</h4>{unidades(lang)}
              <p class="voces-nota">{e(L(S["estricto"], lang))} {e(MAPA["case_status"][lang])}</p></section>
              <section class="x1-casos" id="x1-recorridos" aria-labelledby="x1-casos-t">
                <h4 class="sub-titulo" id="x1-casos-t">{r("casos_t", lang)}</h4>
                {lista_recorridos(lang)}
              </section>
            </section>"""


# ---------------------------------------------------------------- ← cómo medimos

# los criterios de la pregunta en cada especialidad: los que suman el 30 % del índice (question_note del paquete)
PREGUNTA = ("J1.1", "J2.1", "J3.1")
MARCA_PREGUNTA = ' class="x1-crit--pregunta"'
assert all(CRIT[c]["peso"] == 30 for c in PREGUNTA) and "30%" in WEB["es"]["question_note"]

def medimos(lang):
    q = cuadro("como-medimos", lang)
    persp = ""
    for p in MAPA["perspectives"]:
        # J1.1, J2.1 y J3.1 son los criterios de la pregunta: van marcados, y la línea de pesos dice de dónde sale el 30 %
        crits = "".join(f'<li{MARCA_PREGUNTA if c["id"] in PREGUNTA else ""}>'
                        f'<span class="crit-id">{c["id"]}</span> {nombre_criterio(c["id"], lang)} '
                        f'<span class="x1-crit-meta">{r("peso", lang)} {c["peso"]} · {r("lee", lang)} {e(c["fase"])}</span></li>'
                        for c in IDX["criteria"] if c["id"].startswith(p["id"] + "."))
        motores = " · ".join(r("motor_" + m, lang) for m in MOTORES)
        persp += (f'<li class="x1-persp"><div class="card-top"><span class="seal"><span class="sr-only">{"Especialidad" if lang == "es" else "Perspective"} </span>{p["id"]}</span>'
                  f'<span class="card-label">{r("peso_tercio", lang, w=p["weight"])}</span></div>'
                  f'<h4>{e(p["title_" + lang])}</h4><p>{e(p["preview_" + lang])}</p>'
                  f'<ul class="x1-crit-lista" role="list">{crits}</ul>'
                  f'<p class="x1-motores">{"Puntúan" if lang == "es" else "Scored by"}: {motores}</p></li>')
    anclas = "".join(f'<li><span class="ancla-n">{n}</span> <span lang="es">{e(ANCLAS[n])}</span></li>' for n in (4, 3, 2, 1, 0))
    pesos, convs = collections.OrderedDict(), collections.OrderedDict()
    for rr in A["sensitivity_runs"]:
        pesos.setdefault(rr["weight_variant"], rr["specialty_weights_exact"])
        convs.setdefault(rr["recoding_variant"], rr["ordinal_recoding_exact"])
    lista_p = "".join(f'<li>J1 {a} · J2 {b} · J3 {c}</li>' for a, b, c in pesos.values())
    lista_c = "".join(f'<li>0→{v[0]} · 1→{v[1]} · 2→{v[2]} · 3→{v[3]} · 4→{v[4]}</li>' for v in convs.values())
    nota_es = f'<p class="rc-material-nota">{r("anclas_nota", lang)}</p>'
    return f"""<section class="x1-medimos" id="x1-medimos" aria-labelledby="x1-med-t">
              <p class="stamp stamp--estado x1-badge">{r("badge", lang)}</p>
              <h3 class="sec-titulo" id="x1-med-t">{e(q["title"])}</h3>
              <p class="sec-lead">{aj("medimos_sala", lang)}</p>
              <ul class="x1-persp-lista" role="list">{persp}</ul>
              <p class="x1-pesos">{aj("pesos", lang)}</p>
              <p class="alcance">{e(L(S["panel"], lang))}</p>
              <div class="desplegables">
                <details class="desplegable"><summary>{r("escala_t", lang)}</summary><div class="desplegable-cuerpo"><p>{w("judges_note", lang)}</p><ol class="anclas" role="list">{anclas}</ol>{nota_es}<p>{e(L(S["indice"], lang))}</p><p>{e(MAPA["question_priority"][lang])}</p></div></details>
                <details class="desplegable"><summary>{r("sensibilidad_t", lang)}</summary><div class="desplegable-cuerpo"><p>{w("sensitivity_note", lang)}</p><p>{e(L(S["escenarios"], lang))}</p><div class="x1-variantes"><ul role="list">{lista_p}</ul><ul role="list">{lista_c}</ul></div></div></details>
                <details class="desplegable"><summary>{r("orden_t", lang)}</summary><div class="desplegable-cuerpo"><p>{w("question_note", lang)}</p></div></details>
                {nota_incidencias(lang, "x1-incidencias", panel=True)}
                <details class="desplegable"><summary>{r("limites_t", lang)}</summary><div class="desplegable-cuerpo"><p>{w("originality_note", lang)}</p><p>{w("language_note", lang)}</p><p>{e(L(S["esfuerzo"], lang))} {e(L(S["computo"], lang))}</p></div></details>
              </div>
              <p class="x1-materiales"><a class="f-leer" href="{url_metodo(lang)}">{r("materiales", lang)}</a></p>
            </section>"""


def panel_x1(lang):
    """Los rótulos del panel de un pasaje y la plantilla con las 60 tarjetas del carrusel (una sola vez por página)."""
    tarjetas = "".join(pasaje_card(t, fase, p, lang, True) for t, fase, p in CARRUSEL)
    return (f'<template id="x1-panel-rotulos" data-titulo="{r("panel_t", lang)}" data-texto="{r("panel_texto", lang)}" '
            f'data-jueces="{r("panel_jueces", lang)}" data-abrir="{r("panel_abrir", lang)}" data-error="{e(r("panel_error", lang))}"></template>'
            f'<template id="x1-pasajes">{tarjetas}</template>')


BLOQUES = {
    "placa": placa,
    "q-preguntas": lambda l: cuadrante("preguntas", l, "no"),
    "q-laboratorio": lambda l: cuadrante("laboratorio", l, "ne"),
    "q-medimos": lambda l: cuadrante("como-medimos", l, "so"),
    "q-resultados": lambda l: cuadrante("resultados", l, "se"),
    "trailers": trailers,
    "resultados": resultados,
    "lab": lab,
    "medimos": medimos,
    "panel": panel_x1,
}


FECHA = "2026-10-19"   # ✎ la fecha de las páginas de ED02-X1 en el mapa del sitio


def sitemap():
    """Las páginas de lectura en el mapa del sitio, cada una con su par en el otro idioma."""
    rutas = [(url_recorrido(t["id"], "es"), url_recorrido(t["id"], "en")) for t in TRAY] + [(url_metodo("es"), url_metodo("en"))]
    out = []
    for es, en in rutas:
        for loc in (es, en):
            out.append(f'  <url>\n    <loc>https://golembench.org{loc}</loc>\n    <lastmod>{FECHA}</lastmod>\n'
                       f'    <xhtml:link rel="alternate" hreflang="es" href="https://golembench.org{es}"/>\n'
                       f'    <xhtml:link rel="alternate" hreflang="en" href="https://golembench.org{en}"/>\n  </url>')
    return "\n" + "\n".join(out) + "\n  "


def escribir(ruta, contenido):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(contenido, encoding="utf-8")


if __name__ == "__main__":
    for archivo, lang in ((SITIO / "index.html", "es"), (SITIO / "en" / "index.html", "en")):
        s = archivo.read_text(encoding="utf-8")
        for nombre, fn in BLOQUES.items():
            patron = re.compile(r"<!-- x1:" + re.escape(nombre) + r" -->.*?<!-- /x1:" + re.escape(nombre) + r" -->", re.S)
            assert len(patron.findall(s)) == 1, (archivo, nombre)
            s = patron.sub(lambda m: f"<!-- x1:{nombre} -->{fn(lang)}<!-- /x1:{nombre} -->", s)
        archivo.write_text(s, encoding="utf-8")
        print(f"{archivo}: {len(BLOQUES)} bloques escritos ({lang})")
    n = 0
    for lang in ("es", "en"):
        base = SITIO / ("" if lang == "es" else "en") / CARPETA
        for t in TRAY:
            escribir(base / slug(t["id"]) / "index.html", recorrido(t, lang))
            n += 1
        escribir(base / "metodo" / "index.html", metodo(lang))
        n += 1
    print(f"{n} páginas de lectura escritas en {SITIO}/{CARPETA} y {SITIO}/en/{CARPETA}")
    mapa = SITIO / "sitemap.xml"
    sm = mapa.read_text(encoding="utf-8")
    assert sm.count("<!-- x1 -->") == 1
    mapa.write_text(re.sub(r"<!-- x1 -->.*?<!-- /x1 -->", lambda m: f"<!-- x1 -->{sitemap()}<!-- /x1 -->", sm, flags=re.S), encoding="utf-8")
    print(f"sitemap.xml: {2 * (len(TRAY) + 1)} páginas de ED02-X1")
