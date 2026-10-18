# Golem Bench · golembench.org

Idioma de trabajo: español. Todo contenido público va en español y en inglés.

## Qué hay en este repo

- `site/`: lo único que se publica. Portada de la fase 1: HTML y CSS estáticos, un script propio
  pequeño (`assets/centro.js`) y ningún recurso externo. `index.html` (ES), `en/index.html` (EN), `404.html`,
  `_headers`, `robots.txt`, `sitemap.xml`, fuentes e imágenes.
- `herramientas/`: puerta de publicación, servidor local que imita Pages, verificación de la
  portada y generador del favicon y de las imágenes para compartir.
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

- `python3 -I herramientas/verificar_portada.py` debe dar todo correcto.
- `python3 -I herramientas/comprobar_publicacion.py site`.
- Si cambian textos de la portada: mantener la paridad entre `site/index.html` y
  `site/en/index.html`, actualizar `lastmod` en `site/sitemap.xml` y la línea «Actualizado en…»,
  y regenerar las imágenes si cambian el lema o la marca (`herramientas/generar_imagenes.py`).
- Cada push a main que toque `site/` se publica solo en golembench.org.

## Estructura: la cruz

Idea de Juan (18 oct 2026): no todo va de arriba hacia abajo. La portada es una cruz y se llega al
centro; desde ahí se puede ir hacia todos los lados.

- **Centro** (`#pregunta`): la pregunta y la arcilla. Es donde aterriza una visita nueva.
- **↑ Arriba** (`#arriba`): lo que no sabemos. Una escalera de preguntas abiertas que se lee de abajo
  hacia arriba (`flex-direction: column-reverse`: el primer elemento del documento es el más cercano
  al centro). Será el lugar del Atlas de preguntas del Lab.
- **↓ Abajo** (`#abajo`): lo que nos sostiene. El recorrido, los jueces, el pacto y el suelo de barro
  con el contacto.
- **← Izquierda** (`#medimos`): lo que medimos. La sala de resultados, vacía a propósito hasta que se
  publique el piloto.
- **→ Derecha** (`#guardamos`): lo que guardamos. Golem Lab, en el taller.

Cómo está hecho: el centro va primero en el HTML (lectores de pantalla y teclado empiezan en la
pregunta) y la rejilla de `main` lo pone en medio. La fila del centro es un carrusel horizontal con
`scroll-snap`. `site/assets/centro.js` (pequeño, sin dependencias) aterriza en el centro en una visita
nueva, mueve los dos ejes con los enlaces, marca la brújula y atiende ← →. Sin JavaScript todo sigue
accesible con enlaces. El scroll es el del navegador: nada de secuestrarlo.

## Voz: parresía

Pedido de Juan (17 oct 2026), y vale para cada decisión de texto y de diseño: nada de mensajes ni
textos genéricos o formulados. Hablar y diseñar con parresía, como decían los griegos: con la fuerza
de nuestros planteamientos, con orgullo y autenticidad, rompiendo un poco los moldes y con chispa,
sin caer en la oscuridad ni en la distancia, sino para traer calidez y seducción.

En la práctica:

- Una pregunta antes que un eslogan. La portada abre con «¿Hasta dónde puede filosofar una máquina?».
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

Imágenes: vienen de la colección de redes v0.4 (`golem_redes_sociales_v0_4.zip`, arte generado con
IA y aprobado; se rotula «Imagen generada con IA para Golem Bench»). `taller-*.webp` es la versión
panorámica del taller (escritorio) y `arcilla-*.webp` la figura vertical (móvil), elegidas con
`<picture>`. El favicon es la G marfil sobre burdeos, como el perfil rojo de esa colección.
`herramientas/generar_imagenes.py` rehace el favicon y las tarjetas para compartir.

El borde discontinuo marca lo que está en el taller. La CSP no admite estilos ni scripts en línea:
nada de `style=""` ni `<script>` sin archivo.

## Marca

Golem Bench es una marca de Anti-Real Labs S.A.S. Recomendación del 17 oct 2026: radicar la
solicitud ante la SIC (clases 41 y 42) antes de la difusión pública (redes, columnas,
antireallabs.com).
