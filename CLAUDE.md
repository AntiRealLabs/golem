# Golem Bench · golembench.org

Idioma de trabajo: español. Todo contenido público va en español y en inglés.

## Qué hay en este repo

- `site/`: lo único que se publica. La portada: HTML y CSS estáticos, dos scripts propios pequeños
  (`assets/centro.js`, la cruz; `assets/archivo.js`, los carruseles de pasajes, el panel de lectura,
  el ajuste de las esquinas y las páginas de lectura) y ningún recurso externo. `index.html` (ES),
  `en/index.html` (EN), `404.html`, `_headers`, `robots.txt`, `sitemap.xml`, fuentes e imágenes.
  Además, las páginas de lectura de ED02-X1: `ed02-x1/<recorrido>/` (doce) y `ed02-x1/metodo/`, con su
  par en `en/ed02-x1/`.
- `herramientas/`: puerta de publicación, servidor local que imita Pages, verificación de la
  portada, huellas de versión de CSS y JS, generador del favicon y de las imágenes para compartir,
  el constructor del primer corte ED01 (`construir_ed01.py`) con su cotejo (`cotejar_ed01.py`) y el
  de ED02-X1 (`construir_ed02x1.py`) con el suyo (`cotejar_ed02x1.py`).
- `DEPLOY.md`: cómo se despliega y registro de publicaciones.

El prototipo de Golem Lab (propuesta v0.1) no está en este repo: contiene materiales del piloto
y el repo es público. Juan lo tiene en la entrega `golem-lab-propuesta-v0.1.zip`. Si el repo pasa
a privado, el prototipo puede guardarse aquí, fuera de `site/`.

## Reglas del proyecto

Vienen del paquete de coordinación del piloto. No se cambian en un commit:

1. Originales, dictámenes y guías se conservan tal cual. No se cambian notas, rúbricas ni textos.
2. No se calculan notas nuevas, rankings ni tendencias. Un dato desconocido nunca se muestra como 0.
3. Una revisión por IA se rotula como tal y nunca se presenta como validación humana.
   «Listo para integración» no es «publicado».
4. Tres voces separadas por rótulo y estructura, no solo por color: el texto del modelo, la
   valoración del juez y la explicación editorial o del Lab.
5. Una traducción no cuenta como otra lectura. Los ejemplos ficticios van marcados como
   demostración y fuera de todo recuento.
6. No se simulan lectores humanos.
7. La reserva del benchmark y las claves nunca entran en este repo.

## Sesiones de Claude en este repo

- No se usan como participantes ni como jueces del benchmark.
- Las decisiones editoriales que proponga Claude llevan la marca ✎ y las aprueba coordinación.

## Antes de publicar el Lab

No se publica nada del piloto ni del Lab, ni se copia a `site/`, hasta que se cumplan todas:

1. El piloto está cerrado y pasó la revisión final.
2. Coordinación aprobó las reglas editoriales que propuso el diseño (la lectura de portada del
   Lab y las reglas del Cuaderno).
3. Una capa de presentación oculta en la versión pública los datos técnicos internos de los
   dictámenes (por ejemplo, rutas de archivos locales), sin tocar los originales ni sus huellas.
4. La integración con la base visual sigue la propuesta de integración de la entrega v0.1, con
   versión nueva de la base.
5. Juan aprueba la publicación y queda anotada en el registro de `DEPLOY.md`.

Al publicar el Lab: actualizar `herramientas/comprobar_publicacion.py` en el mismo commit y decir
por qué en el mensaje.

## Primer corte ED01 (publicado el 18 oct 2026)

El paquete de contenidos v0.1 de coordinación (18 oct 2026) está integrado en la portada y publicado
desde el 18 oct 2026, con la aprobación de Juan anotada en `DEPLOY.md`. Desde ese commit la puerta
(`comprobar_publicacion.py`) admite dos identificadores, y solo esos: «IA-01», que nombra la serie
anterior en la nota que la separa de ED01, y «BF-03», que está en el texto literal de una fuente. Admitir
otro pide lo mismo: aprobación de Juan, el cambio de la puerta en el mismo commit y la línea en `DEPLOY.md`.

- Los textos salen del paquete, tal cual y en su idioma; los rótulos funcionales que no trae (✎) están
  en `ROT` de `construir_ed01.py`.
- Tres voces separadas por rótulo y estructura: el texto del modelo (letra de libro recta, marca de
  cita y «Texto del modelo» con configuración y caso), la lectura del juez (recuadro firme con su sello)
  y la guía editorial (filo de arcilla y «Guía de lectura editorial»). Los cinco fragmentos son selección
  editorial, no de los jueces.
- Lo pendiente dice «Pendiente» y lleva borde discontinuo; nunca un cero. No hay puestos, medias,
  notas totales ni barras. El ranking queda preparado y dormido: solo se llena con un conjunto liberado
  oficialmente (`construir_ed01.py --ranking`), y la página muestra lo que ese conjunto diga, sin
  calcular ni desempatar.
- El nivel de J1.1 es de toda la entrega A, nunca de la cita: dos reglas de cinco posiciones con una
  marca cada una, sin flecha entre 4 y 3 ni promedio.
- IA-01, la app y ED01 son series distintas: la nota de IA-01 va aparte y no suma a las cifras.
- Desde ED02-X1 (20 oct 2026) las esquinas, la cartela de la placa y los tráileres del celular son de
  ED02-X1. ED01 sigue en sus salas, debajo de ED02-X1, detrás de un separador que dice que es otra serie y que
  sus cifras no se suman. `cotejar_ed01.py` coteja lo que ED01 sigue publicando.

## ED02-X1 (publicado el 20 oct 2026)

El paquete público de coordinación (`Golem_Bench_ED02_X1_publico_para_Claude`, 18 oct 2026) está integrado en
la portada y publicado desde el 20 oct 2026, con la aprobación de Juan anotada en `DEPLOY.md`. La puerta lo dejó
pasar sin cambios: no trae identificadores bloqueados ni archivos fuera de lo previsto. Las decisiones ✎ de
abajo salieron con esa aprobación; si coordinación pide cambiar alguna, se cambia en `construir_ed02x1.py` y se
reconstruye.

Un paquete nuevo se integra en una rama local que no se sube hasta que Juan apruebe: el repo es público y
cualquier rama que toque `site/` se publica como vista previa en `<rama>.golembench.pages.dev`.

- `construir_ed02x1.py PAQUETE site` comprueba la huella de cada archivo contra el manifiesto, escribe los
  bloques `<!-- x1:… -->` de las dos portadas, las 26 páginas de lectura y su parte del `sitemap.xml`.
  `cotejar_ed02x1.py PAQUETE site` lo revisa sin usar ese código (0 fallas).
- Es un piloto exploratorio con desviaciones, no un cierre de ED02 estricto. La etiqueta «Piloto exploratorio
  · ED02-X1» va en la cartela de la placa y encima de cada parte con cifras.
- El índice combinado es un orden condicional, nunca un ganador ni un porcentaje: la tabla lleva al lado los
  dos motores, cada uno con su primero marcado, y los valores exactos. Los 42 escenarios van en dos rejillas de
  7 × 3, una por motor (✎ lectura de Claude: ningún peso ni conversión cambia el orden; lo cambia el motor).
- El aviso de las 351 palabras va con la nota completa de incidencias (en Cómo medimos y en el panel). Los 60
  textos son 59 admitidos en ED02 más 1 de X1: nunca 60 admisiones estrictas. Las desviaciones de las críticas
  quedan en el método. Las dos configuraciones no admitidas no tienen cero ni puesto; Gemini dice «Pendiente».
- 12 recorridos, 60 textos, 24 críticas y 144 lecturas son unidades distintas, cada una con lo que cuenta.
  Tres especialidades puntuadas por dos motores, no tres jueces.
- Los pasajes son citas verificadas que usó un juez, no una selección de ideas. Un pasaje es una frase visible
  en su fuente y etapa (la misma citada con o sin sus «**» cuenta una vez): 2.282 registros, 1.222 pasajes. Cada
  uno conserva todos sus vínculos de juez y criterio. Las 488 referencias no promovidas se muestran dentro del
  dictamen, nunca se destacan. Carrusel (✎): de cada texto, el primer pasaje citado entre los de 60 a 240
  caracteres; 60 en una plantilla, barajados por visita.
- Cada recorrido trae sus cinco textos, las dos críticas, el contraste T, el caso y las 32 lecturas lado a lado
  por motor: nivel en su regla («vale para la etapa, no para una frase»), justificación y límite a la vista; el
  resto del dictamen, desplegable. Siete dictámenes de nivel 4 no registran límite: la página lo dice.
- En inglés cambian la interfaz y lo editorial del paquete; los cuerpos del modelo, de las críticas y de los
  jueces siguen en español original con `lang="es"` y el aviso de que no están traducidos. Los nombres de
  criterio en inglés son traducción editorial (✎) y van con el original al lado. La novedad se juzga
  respecto del corpus, no de toda la historia. No hay validación humana.

## Antes de cada push a main

- Si cambian `portada.css`, `centro.js` o `archivo.js`: `python3 -I herramientas/versionar_recursos.py`.
  Pone la huella `?v=` en las páginas; Cloudflare guarda CSS y JS 4 horas en los navegadores y, sin
  huella nueva, quien ya visitó vería la página nueva con estilos viejos. La verificación y los dos
  workflows fallan si una huella quedó vieja.
- Si llega un paquete nuevo de ED01: `python3 -I herramientas/construir_ed01.py PAQUETE site`, luego
  `python3 -I herramientas/cotejar_ed01.py PAQUETE site` (0 fallas) y las huellas.
- Si llega un paquete nuevo de ED02-X1: `python3 -I herramientas/construir_ed02x1.py PAQUETE site`, luego
  `python3 -I herramientas/cotejar_ed02x1.py PAQUETE site` (0 fallas) y las huellas.
- `python3 -I herramientas/verificar_portada.py` debe dar todo correcto.
- `python3 -I herramientas/comprobar_publicacion.py site`.
- Si cambian textos de la portada: mantener la paridad entre `site/index.html` y
  `site/en/index.html`, actualizar `lastmod` en `site/sitemap.xml` y la línea «Actualizado en…»,
  y regenerar las imágenes si cambian el lema o la marca (`herramientas/generar_imagenes.py`).
- Cada push a main que toque `site/` se publica solo en golembench.org.

## Estructura: el mapa en cruz

Idea de Juan (18 oct 2026): no todo va de arriba hacia abajo. La portada es una cruz y se llega al
centro; desde ahí se puede ir hacia todos los lados. Con su boceto del mismo día: el logo solo en el
centro, cuatro rumbos alrededor, nada de arquitectura tradicional (sin barra superior ni pie al uso).

- **Centro** (`#centro`, `.onfalo`): la placa del nombre en el centro exacto, sobre papel: el
  descriptor, «Golem» centrado con la mascota a su izquierda, «Bench» debajo y el lema. El estado de la
  edición va inscrito en el marco de abajo, como una cartela: no agranda la placa (hoy, «Piloto
  exploratorio · ED02-X1»; con ED01 decía «Edición experimental · Primeras lecturas»).
  Alrededor, cuatro rumbos: el nombre llano en un recuadro (`.lugar`) y, en cursiva, un susurro
  de lo que hay allá (`.susurro`; a los lados va debajo del recuadro). En los cuatro cuadrantes que forma
  la cruz, un tráiler de su sala en rueda de molino: noroeste → preguntas, noreste → laboratorio,
  sureste → resultados, suroeste → cómo medimos. Cada tráiler dice lo mismo en el mismo orden: rótulo,
  titular, una muestra concreta y una invitación. Son de ED02-X1: el 30 % de las preguntas
  (J1.1, J2.1 y J3.1, cada uno con «peso 30»: sin la palabra, el número se leería como una nota), un pasaje citado por un juez, el orden condicional con los dos motores y las tres
  especialidades; la etiqueta del piloto y la cifra con su advertencia son lo último que se guarda. En el HTML cada rumbo y su cuadrante van juntos en
  una estación (`.estacion--preguntas`, `--laboratorio`, `--medimos`, `--resultados`; en escritorio son
  `display:contents`). Es donde aterriza una visita nueva.
- **Las esquinas** (✎ propuesta de Claude, 18 oct 2026): los tráileres de arriba cuelgan del borde
  superior y los de abajo se apoyan en el inferior; bajan (o suben) hasta los recuadros de los lados sin
  tocarlos. Cada esquina es un contenedor (`container: esquina/size`) y `archivo.js` prueba la versión
  completa en el tamaño real: si no cabe, guarda piezas enteras en un orden fijo, de lo accesorio a lo
  esencial (`data-guardado`). La letra nunca se achica para que algo quepa; lo guardado sigue completo en
  su sala. Sin JavaScript, unos umbrales de altura hacen lo mismo de forma aproximada. La verificación
  comprueba en diez tamaños que nada se toque ni se salga.
- **En el celular** (boceto de Juan, 18 oct 2026) el centro no copia el escritorio: cada estación es
  una baldosa que se toca entera (el enlace del recuadro se estira sobre ella), con el recuadro junto a
  la placa, el resumen hacia afuera (el titular del tráiler) y una flecha en la mitad del borde por donde
  se sale: ↑ arriba, → derecha, ← izquierda, ↓ abajo. El lado de la flecha guarda margen para que nada
  la toque. Sin susurros ni enlaces secundarios: la baldosa es el enlace. El tinte al pasar el puntero
  solo existe donde hay puntero (`hover:hover`); en un teléfono no se queda pegado. Debajo del centro
  van los cuatro tráileres completos, apilados en una columna: preguntas → laboratorio → resultados →
  método.
- **↑ Preguntas abiertas** (`#preguntas`): un cielo nocturno con la escalera de preguntas, que se lee
  de abajo hacia arriba (`flex-direction: column-reverse`: el primer elemento del documento es el
  más cercano al centro). Junto al centro, «Nuestras apuestas, a la vista» (`#apuestas`): las seis
  apuestas como desplegables, cada una con la pregunta que la pone a prueba. Encima, el pie y la
  escalera. Abajo del cielo amanece hacia el papel. Será el lugar del Atlas del Lab.
  El pie (el signo «?» y su explicación, con el `h2` de la sala) va antes de la lista y no es un
  peldaño: la sala es una columna invertida, así que queda abajo, y la línea de la escalera termina
  16 px antes del signo, mida lo que mida el pie. En el celular la línea termina en el punto de la
  primera pregunta. La verificación comprueba que ninguna línea toque el signo.
- **← Cómo medimos** (`#como-medimos`): el recorrido de cuatro pasos; después, ED02-X1
  (`#x1-medimos`: tres especialidades puntuadas por dos motores, cada una con sus criterios; la escala, la
  sensibilidad, el orden de lectura, la nota completa de incidencias `#x1-incidencias` y los límites; el
  enlace a la rúbrica y los materiales) y, aparte, ED01: las tres especialidades (J1, J2 y J3 no son
  modelos: GPT y Claude son motores que hacen lecturas), su alcance en ese corte, y en desplegables los
  criterios y pesos, los referentes, la escala, el índice candidato y las razones y límites. Cierra la cita.
- **→ Laboratorio** (`#laboratorio`): Golem Lab y sus tres puertas, en el taller (borde discontinuo:
  cada puerta dice que no está construida y qué existe mientras tanto). Después, ED02-X1
  (`#x1-laboratorio`: las cuatro unidades, el carrusel de pasajes citados y los tres casos con sus doce
  recorridos, `#x1-recorridos`). Debajo, con borde firme y aparte, lo que hay de ED01: las cifras con lo
  que cuentan, los fragmentos («Una voz del archivo»), el supuesto a examen, los temas del lote, las cinco
  fuentes completas y la nota de IA-01, aparte.
- **↓ Resultados de evaluaciones** (`#resultados`): primero ED02-X1 (el orden condicional
  con los dos motores, los 42 escenarios, el aviso de 351 palabras, lo que queda fuera del índice, los
  límites y los perfiles); después, aparte, el primer corte ED01 (`#ed01-resultados`: las cuatro
  configuraciones en orden fijo de cohorte, las 10 entregas dentro del límite y las 2 fuera de
  comparación, las fases cerradas y pendientes, el ranking en preparación, «Una pregunta. Dos lecturas.» y
  los límites), el pacto y el suelo de barro con el golem que entreabre los ojos y el contacto. El pie va
  debajo, sobre carbón.
- **Las páginas de lectura de ED02-X1** (`/ed02-x1/<recorrido>/`, `/ed02-x1/metodo/` y su par en `/en/`):
  una barra con la vuelta al laboratorio, la marca y el idioma; la ruta de etapas fija arriba; cada texto
  con sus pasajes subrayados con puntos y, debajo, las lecturas de los dos motores, criterio por criterio.

Cómo está hecho: el centro va primero en el HTML (lectores de pantalla y teclado empiezan ahí) y la
rejilla de `main` lo pone en medio. El centro es una rejilla en cruz de 5×5; las dos filas de aire
miden lo mismo, así que la placa queda en el centro exacto (la verificación lo mide). De la placa
salen dos meridianos que atraviesan la página: suben por la escalera y bajan por cada sección hasta
el barro. La fila del centro es un carrusel horizontal con `scroll-snap` de una pantalla de alto; las
salas laterales se recorren por dentro, así no queda vacío entre el centro y los resultados.
`site/assets/centro.js` (pequeño, sin dependencias) aterriza en el centro en una visita nueva, mueve
los dos ejes con los enlaces, marca la brújula y atiende ← →. La brújula, un sello pequeño, aparece
cuando uno se aleja del centro. Sin JavaScript todo sigue accesible con enlaces. El scroll es el del
navegador: nada de secuestrarlo. Un ancla dentro de una sala lateral (`#x1-recorridos`, `#fuentes`) desliza
la fila hasta esa sala y la baja por dentro hasta el lugar. `site/assets/archivo.js` baraja cada colección
de pasajes una vez por visita (se avanzan a mano, sin avance automático; el cambio de idioma conserva el
pasaje; los 60 de ED02-X1 salen de la plantilla `#x1-pasajes`), abre el panel de lectura (`<dialog>`: se
cierra con Esc, su botón o tocando afuera, y devuelve el foco; para un pasaje de ED02-X1 trae de la página
de su recorrido el texto con el pasaje marcado y las lecturas que lo citan), ajusta las esquinas y, en las
páginas de lectura, ilumina entero el pasaje que se sigue. Sin él queda quieto el primer pasaje y «Leer en
contexto» lleva al pasaje en la página de su recorrido.

## Voz: parresía

Pedido de Juan (17 oct 2026), y vale para cada decisión de texto y de diseño: nada de mensajes ni
textos genéricos o formulados. Hablar y diseñar con parresía, como decían los griegos: con la fuerza
de nuestros planteamientos, con orgullo y autenticidad, rompiendo un poco los moldes y con chispa,
sin caer en la oscuridad ni en la distancia, sino para traer calidez y seducción.

En la práctica:

- Nombres llanos para orientarse, voz poética para el sentido: el recuadro dice adónde va uno
  («Cómo medimos») y el susurro dice qué encuentra («Lo que nos sostiene»).
- Las preguntas viven arriba, en la escalera; el centro es el nombre. Juan descartó como titular
  «¿Hasta dónde puede filosofar una máquina?» (18 oct 2026): no se usa en la portada ni en las
  tarjetas para compartir.
- El lema es «Preguntas desde el futuro» (EN: «Questions from the future»). Lo decidió Juan el
  18 oct 2026. Las piezas de la colección de redes v0.4 dicen «para el futuro»: ese texto no se
  copia a la portada.
- Frases cortas, con verbo y sujeto. Nada de «soluciones», «potenciar», «innovador», «de vanguardia».
- La franqueza incluye decir lo que no sabemos y lo que todavía no está listo, con gracia
  («Todavía es arcilla», «ni un día antes»), nunca con letra pequeña.
- La metáfora de la casa es el golem: barro que una palabra pone a andar. La figura de arcilla con
  los ojos cerrados es la imagen de la marca.
- El rigor no se negocia por el estilo: cada frase con chispa tiene que seguir siendo verdad según
  las reglas de arriba.
- Prueba antes de publicar un texto: ¿podría firmarlo cualquier otra web? Si sí, se reescribe.
- En el chat con Juan, lo mismo: directo, cálido y sin plantillas.

## Identidad visual

Tokens y letras de la base visual (`site/assets/portada.css`): carbón `#1c1d1a`, marfil `#f0ebdf`,
burdeos `#803a39`, tostado `#d1b698`, arcilla `#b98b6a`. UnifrakturMaguntia para la marca, Chakra Petch
para titulares, Archivo para el texto, Newsreader (cursiva) para las frases con voz literaria,
Fragment Mono para rótulos y DM Sans para «BENCH». Las fuentes (licencia OFL) se sirven desde
`site/assets/fonts/`. El texto del modelo va en Newsreader recta, y lo que el modelo escribió en negrita
o como título va en Newsreader 600, en su propia letra: en la letra de la interfaz, un
título suyo se leería como un rótulo nuestro.

El suelo de la portada es el papel (marfil); arriba, la noche de las preguntas; abajo, la arcilla.

Imágenes: vienen de la colección de redes v0.4 (`golem_redes_sociales_v0_4.zip`, arte generado con
IA y aprobado; se rotula «Imagen generada con IA para Golem Bench»). La página usa la figura
vertical completa (`arcilla-*.webp`), enmarcada y sin sombreado añadido: a Juan no le gustó la
viñeta oval. La versión panorámica del taller vive en `herramientas/fuentes/`, no se publica y solo
la usan las tarjetas para compartir. El favicon y la brújula son la G marfil sobre burdeos, como el
perfil rojo de esa colección. `herramientas/generar_imagenes.py` rehace el favicon y las tarjetas.

Símbolos de las estaciones (✎ propuesta de Claude, 18 oct 2026, a pedido de Juan): un sprite SVG al
comienzo de cada página (`svg.simbolos`, con `<symbol>` y `<use href>`), de trazo fino en el color del
texto. Preguntas abiertas: un signo de pregunta hecho de estrellas (arriba es de noche). Laboratorio:
un matraz con barro adentro. Cómo medimos: un compás de dibujo. Resultados: el ojo cerrado del golem.
Van en el recuadro de cada rumbo (24 px; 22 en el celular), en el título de cada sala lateral, al pie
de la escalera (tostado, sobre la noche) y sobre la sala de resultados (44 px). Son decorativos
(`aria-hidden`): el nombre siempre va escrito. Un símbolo nuevo se agrega al sprite de las dos páginas.

La mascota es la figurita del golem: el busto de arcilla de tres cuartos, con la corona rota y los ojos
cerrados, de un solo trazo (opción C; la eligió Juan el 18 oct 2026). Vive en el sprite como `s-golem`
y firma el pie de las tres páginas (tostado, sobre carbón) y la marca de Golem Lab.

En la placa del centro, en la de la 404 y en las tarjetas para compartir, la mascota va a la izquierda de
«Golem», de su tamaño y a su altura (Juan, 18 oct 2026): el `viewBox` va ajustado a la tinta del dibujo,
que mide lo que la tinta de «Golem» (.74 del cuerpo de la letra, de lo alto de la G al pie) y se apoya en
su línea. «Golem» sigue en el eje de la placa, sobre «Bench» y el lema: la mascota cuelga a la izquierda
y una columna vacía igual la equilibra a la derecha. En «Golem Lab» va igual y el par no se separa; en
un celular estrecho la letra baja lo justo para que quepa. La verificación mide tamaño, altura y eje.

El borde discontinuo marca lo que está en el taller. La CSP no admite estilos ni scripts en línea:
nada de `style=""` ni `<script>` sin archivo.

## Marca

Golem Bench es una marca de Anti-Real Labs S.A.S. Recomendación del 17 oct 2026: radicar la
solicitud ante la SIC (clases 41 y 42) antes de la difusión pública (redes, columnas,
antireallabs.com).
