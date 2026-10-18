# Golem Bench · golembench.org

Idioma de trabajo: español. Todo contenido público va en español y en inglés.

## Qué hay en este repo

- `site/`: lo único que se publica. Portada de la fase 1: HTML y CSS estáticos, un script propio
  pequeño (`assets/centro.js`) y ningún recurso externo. `index.html` (ES), `en/index.html` (EN), `404.html`,
  `_headers`, `robots.txt`, `sitemap.xml`, fuentes e imágenes.
- `herramientas/`: puerta de publicación, servidor local que imita Pages, verificación de la
  portada, huellas de versión de CSS y JS, y generador del favicon y de las imágenes para compartir.
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

## Antes de cada push a main

- Si cambian `portada.css` o `centro.js`: `python3 -I herramientas/versionar_recursos.py`. Pone la
  huella `?v=` en las páginas; Cloudflare guarda CSS y JS 4 horas en los navegadores y, sin huella
  nueva, quien ya visitó vería la página nueva con estilos viejos. La verificación y los dos
  workflows fallan si una huella quedó vieja.
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
  descriptor, «Golem» centrado, «Bench» debajo y el lema. Alrededor, cuatro rumbos: el nombre llano en
  un recuadro (`.lugar`) y, en cursiva, un susurro de lo que hay allá (`.susurro`). En los cuatro
  cuadrantes que forma la cruz, un resumen que invita a ir, en rueda de molino: noroeste → preguntas,
  noreste → laboratorio, sureste → resultados, suroeste → cómo medimos. En el HTML cada rumbo y su
  cuadrante van juntos en una estación (`.estacion--preguntas`, `--laboratorio`, `--medimos`,
  `--resultados`; en escritorio son `display:contents`). Es donde aterriza una visita nueva. En
  pantallas bajas los cuadrantes muestran solo título y enlace; la verificación comprueba en nueve
  tamaños que nada se toque y que los cuatro recuadros midan lo mismo.
- **En el celular** (boceto de Juan, 18 oct 2026) el centro no copia el escritorio: cada estación es
  una baldosa que se toca entera (el enlace del recuadro se estira sobre ella), con el recuadro junto a
  la placa, el resumen hacia afuera y una flecha en la mitad del borde por donde se sale: ↑ arriba,
  → derecha, ← izquierda, ↓ abajo. El lado de la flecha guarda margen para que nada la toque. Sin
  susurros ni enlaces secundarios: la baldosa es el enlace. El tinte al pasar el puntero solo existe
  donde hay puntero (`hover:hover`); en un teléfono no se queda pegado.
- **↑ Preguntas abiertas** (`#preguntas`): un cielo nocturno con la escalera de preguntas, que se lee
  de abajo hacia arriba (`flex-direction: column-reverse`: el primer elemento del documento es el
  más cercano al centro). Abajo del cielo amanece hacia el papel. Será el lugar del Atlas del Lab.
- **← Cómo medimos** (`#como-medimos`): el recorrido de cuatro pasos, los tres jueces y la cita.
- **→ Laboratorio** (`#laboratorio`): Golem Lab, en el taller (borde discontinuo).
- **↓ Resultados de evaluaciones** (`#resultados`): la sala vacía a propósito, el pacto y el suelo de
  barro con el golem de ojos cerrados y el contacto. El pie va debajo, sobre carbón.

Cómo está hecho: el centro va primero en el HTML (lectores de pantalla y teclado empiezan ahí) y la
rejilla de `main` lo pone en medio. El centro es una rejilla en cruz de 5×5; las dos filas de aire
miden lo mismo, así que la placa queda en el centro exacto (la verificación lo mide). De la placa
salen dos meridianos que atraviesan la página: suben por la escalera y bajan por cada sección hasta
el barro. La fila del centro es un carrusel horizontal con `scroll-snap` de una pantalla de alto; las
salas laterales se recorren por dentro, así no queda vacío entre el centro y los resultados.
`site/assets/centro.js` (pequeño, sin dependencias) aterriza en el centro en una visita nueva, mueve
los dos ejes con los enlaces, marca la brújula y atiende ← →. La brújula, un sello pequeño, aparece
cuando uno se aleja del centro. Sin JavaScript todo sigue accesible con enlaces. El scroll es el del
navegador: nada de secuestrarlo.

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

El borde discontinuo marca lo que está en el taller. La CSP no admite estilos ni scripts en línea:
nada de `style=""` ni `<script>` sin archivo.

## Marca

Golem Bench es una marca de Anti-Real Labs S.A.S. Recomendación del 17 oct 2026: radicar la
solicitud ante la SIC (clases 41 y 42) antes de la difusión pública (redes, columnas,
antireallabs.com).
