# Golem Bench · golembench.org

Idioma de trabajo: español. Todo contenido público va en español y en inglés.

## Qué hay en este repo

- `site/`: lo único que se publica. La portada: HTML y CSS estáticos, dos scripts propios pequeños
  (`assets/centro.js`, la cruz; `assets/archivo.js`, los fragmentos, el panel de lectura y el ajuste
  de las esquinas) y ningún recurso externo. `index.html` (ES), `en/index.html` (EN), `404.html`,
  `_headers`, `robots.txt`, `sitemap.xml`, fuentes e imágenes.
- `herramientas/`: puerta de publicación, servidor local que imita Pages, verificación de la
  portada, huellas de versión de CSS y JS, generador del favicon y de las imágenes para compartir,
  y el constructor del primer corte ED01 (`construir_ed01.py`) con su cotejo (`cotejar_ed01.py`).
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

## Antes de cada push a main

- Si cambian `portada.css`, `centro.js` o `archivo.js`: `python3 -I herramientas/versionar_recursos.py`.
  Pone la huella `?v=` en las páginas; Cloudflare guarda CSS y JS 4 horas en los navegadores y, sin
  huella nueva, quien ya visitó vería la página nueva con estilos viejos. La verificación y los dos
  workflows fallan si una huella quedó vieja.
- Si llega un paquete nuevo de ED01: `python3 -I herramientas/construir_ed01.py PAQUETE site`, luego
  `python3 -I herramientas/cotejar_ed01.py PAQUETE site` (0 fallas) y las huellas.
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
  edición («Edición experimental · Primeras lecturas») va inscrito en el marco de abajo, como una
  cartela: no agranda la placa. Alrededor, cuatro rumbos: el nombre llano en un recuadro (`.lugar`) y, en cursiva, un susurro
  de lo que hay allá (`.susurro`; a los lados va debajo del recuadro). En los cuatro cuadrantes que forma
  la cruz, un tráiler de su sala en rueda de molino: noroeste → preguntas, noreste → laboratorio,
  sureste → resultados, suroeste → cómo medimos. Cada tráiler dice lo mismo en el mismo orden: rótulo,
  titular, una muestra concreta y una invitación. En el HTML cada rumbo y su cuadrante van juntos en
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
- **← Cómo medimos** (`#como-medimos`): el recorrido de cuatro pasos, las tres especialidades (J1, J2 y
  J3 no son modelos: GPT y Claude son motores que hacen lecturas), su alcance en este corte, y en
  desplegables los criterios y pesos, los referentes, la escala, el índice candidato y las razones y
  límites. Cierra la cita.
- **→ Laboratorio** (`#laboratorio`): Golem Lab y sus tres puertas, en el taller (borde discontinuo:
  cada puerta dice que no está construida y qué existe mientras tanto). Debajo, con borde firme, lo que
  ya hay de ED01: las cifras con lo que cuentan, los fragmentos («Una voz del archivo»), el supuesto a
  examen, los temas del lote, las cinco fuentes completas y la nota de IA-01, aparte.
- **↓ Resultados de evaluaciones** (`#resultados`): el primer corte ED01 (las cuatro configuraciones
  en orden fijo de cohorte, las 10 entregas dentro del límite y las 2 fuera de comparación, las fases
  cerradas y pendientes, el ranking en preparación, «Una pregunta. Dos lecturas.» y los límites), el
  pacto y el suelo de barro con el golem que entreabre los ojos y el contacto. El pie va debajo, sobre
  carbón.

Cómo está hecho: el centro va primero en el HTML (lectores de pantalla y teclado empiezan ahí) y la
rejilla de `main` lo pone en medio. El centro es una rejilla en cruz de 5×5; las dos filas de aire
miden lo mismo, así que la placa queda en el centro exacto (la verificación lo mide). De la placa
salen dos meridianos que atraviesan la página: suben por la escalera y bajan por cada sección hasta
el barro. La fila del centro es un carrusel horizontal con `scroll-snap` de una pantalla de alto; las
salas laterales se recorren por dentro, así no queda vacío entre el centro y los resultados.
`site/assets/centro.js` (pequeño, sin dependencias) aterriza en el centro en una visita nueva, mueve
los dos ejes con los enlaces, marca la brújula y atiende ← →. La brújula, un sello pequeño, aparece
cuando uno se aleja del centro. Sin JavaScript todo sigue accesible con enlaces. El scroll es el del
navegador: nada de secuestrarlo. `site/assets/archivo.js` baraja los cinco fragmentos una vez por visita
(se avanzan a mano, sin avance automático; el cambio de idioma conserva el fragmento), abre el panel de
lectura (`<dialog>`: se cierra con Esc, su botón o tocando afuera, y devuelve el foco) y ajusta las
esquinas. Sin él queda GB-ED01-F001 quieto y «Leer en contexto» lleva a la ficha de su fuente.

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
`site/assets/fonts/`.

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
