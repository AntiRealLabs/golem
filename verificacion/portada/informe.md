# Verificación de la portada

**133 de 133 comprobaciones correctas** · 2026-10-20 01:12 (UTC−5) · Chromium (Playwright) contra `herramientas/servidor_local.py`.

Inspección automática. No sustituye pruebas con personas, lectores de pantalla reales, otros navegadores ni la revisión del sitio ya publicado en Cloudflare.

| | Comprobación | Detalle |
|---|---|---|
| ✓ | Puerta de publicación: site/ contiene solo la portada |  |
| ✓ | Puerta de publicación: rechaza datos del piloto colados (prueba con archivos falsos) |  |
| ✓ | HTTP: / responde 200 con HTML |  |
| ✓ | HTTP: /en/ responde 200 |  |
| ✓ | HTTP: /en redirige a /en/ |  |
| ✓ | HTTP: una ruta inexistente (p. ej. /lab.html) da 404 con la página propia |  |
| ✓ | HTTP: _headers no se sirve como archivo |  |
| ✓ | Cabeceras de seguridad presentes en / |  |
| ✓ | Caché de fuentes sin valores unidos por reglas repetidas |  |
| ✓ | La hoja de estilos no lleva caché larga (cambia con cada versión) |  |
| ✓ | CSS y JS llevan la huella de su versión (?v=) en todas las páginas y se sirven con ella |  |
| ✓ | robots.txt enlaza el sitemap |  |
| ✓ | sitemap.xml es XML válido con las dos portadas y las 26 páginas de ED02-X1 |  |
| ✓ | HTTP: /ed02-x1/m03-c02-r1/ responde 200 con HTML |  |
| ✓ | HTTP: /en/ed02-x1/m03-c02-r1/ responde 200 con HTML |  |
| ✓ | HTTP: /ed02-x1/m04-c01-r1/ responde 200 con HTML |  |
| ✓ | HTTP: /ed02-x1/metodo/ responde 200 con HTML |  |
| ✓ | HTTP: /en/ed02-x1/metodo/ responde 200 con HTML |  |
| ✓ | favicon.ico trae 16, 32 y 48 px |  |
| ✓ | apple-touch-icon.png mide 180×180 |  |
| ✓ | og-es.jpg mide 1200×630 |  |
| ✓ | og-en.jpg mide 1200×630 |  |
| ✓ | Figura del golem: arte original a tamaño completo (1122×1402); la panorámica no se publica |  |
| ✓ | favicon.svg es SVG válido |  |
| ✓ | [es] sin errores de consola ni violaciones de la CSP |  |
| ✓ | [es] las cinco familias de la base cargan desde el propio sitio |  |
| ✓ | [es] todo se sirve desde el mismo origen |  |
| ✓ | [es] peso total de la página ≤ 700 KB |  |
| ✓ | [es] idioma del documento declarado |  |
| ✓ | [es] un solo h1 |  |
| ✓ | [es] descripción presente y ≤ 170 caracteres |  |
| ✓ | [es] canónica correcta |  |
| ✓ | [es] alternativas hreflang es/en/x-default |  |
| ✓ | [es] imagen para compartir absoluta y existente |  |
| ✓ | [es] imágenes cargadas y con texto alternativo descriptivo |  |
| ✓ | [es] el selector marca el idioma actual |  |
| ✓ | [es] cada estación lleva su símbolo; la mascota va a la izquierda de «Golem» y firma el pie y el laboratorio; los lectores de pantalla los saltan |  |
| ✓ | [es] enlaces internos válidos y solo los externos previstos |  |
| ✓ | [es] ED01: solo se nombran las cuatro configuraciones de la cohorte |  |
| ✓ | [es] ED01: lo pendiente dice «Pendiente», sin ranking ni notas por frase; dos reglas con una marca; las tres voces con su rótulo; F004 con su nota |  |
| ✓ | [es] ED02-X1: «Piloto exploratorio · ED02-X1» en la placa y en resultados; orden condicional con los dos motores; 42 escenarios partidos por motor; sin porcentajes; fuera del índice sin cifras; el aviso de 351 palabras con su nota; doce recorridos; ED01 aparte |  |
| ✓ | [es] sin restos del otro idioma fuera de lo marcado con lang |  |
| ✓ | [en] sin errores de consola ni violaciones de la CSP |  |
| ✓ | [en] las cinco familias de la base cargan desde el propio sitio |  |
| ✓ | [en] todo se sirve desde el mismo origen |  |
| ✓ | [en] peso total de la página ≤ 700 KB |  |
| ✓ | [en] idioma del documento declarado |  |
| ✓ | [en] un solo h1 |  |
| ✓ | [en] descripción presente y ≤ 170 caracteres |  |
| ✓ | [en] canónica correcta |  |
| ✓ | [en] alternativas hreflang es/en/x-default |  |
| ✓ | [en] imagen para compartir absoluta y existente |  |
| ✓ | [en] imágenes cargadas y con texto alternativo descriptivo |  |
| ✓ | [en] el selector marca el idioma actual |  |
| ✓ | [en] cada estación lleva su símbolo; la mascota va a la izquierda de «Golem» y firma el pie y el laboratorio; los lectores de pantalla los saltan |  |
| ✓ | [en] enlaces internos válidos y solo los externos previstos |  |
| ✓ | [en] ED01: solo se nombran las cuatro configuraciones de la cohorte |  |
| ✓ | [en] ED01: lo pendiente dice «Pending», sin ranking ni notas por frase; dos reglas con una marca; las tres voces con su rótulo; F004 con su nota |  |
| ✓ | [en] ED02-X1: «Exploratory pilot · ED02-X1» en la placa y en resultados; orden condicional con los dos motores; 42 escenarios partidos por motor; sin porcentajes; fuera del índice sin cifras; el aviso de 351 palabras con su nota; doce recorridos; ED01 aparte |  |
| ✓ | [en] sin restos del otro idioma fuera de lo marcado con lang |  |
| ✓ | [404] sin errores de consola ni violaciones de la CSP |  |
| ✓ | [404] fuentes de la marca cargadas |  |
| ✓ | [404] todo se sirve desde el mismo origen |  |
| ✓ | [404] peso total de la página ≤ 700 KB |  |
| ✓ | Paridad ES/EN: mismos h2, h3, elementos de lista, párrafos y enlaces (sin contar el original español que acompaña a la traducción) |  |
| ✓ | Sin desplazamiento horizontal a 1440, 1024, 768, 390 y 320 px (portadas, 404, recorridos y método) |  |
| ✓ | Objetivos táctiles ≥ 24 px en móvil (WCAG 2.5.8) |  |
| ✓ | Teclado: el primer Tab se queda en el centro, a la vista (selector de idioma) |  |
| ✓ | Teclado: desde el centro, ES → EN → cada estación con lo de su esquina: ↑, →, ←, ↓ |  |
| ✓ | Teclado: el foco se ve (contorno de 3 px) |  |
| ✓ | Cruz [es · escritorio]: se llega al centro (el nombre a la vista, brújula en el centro) |  |
| ✓ | Cruz [es · escritorio]: la placa del nombre queda en el centro exacto de la pantalla (±3 px) |  |
| ✓ | Cruz [es · escritorio]: arriba se lee de abajo hacia arriba (la primera pregunta queda junto al centro) |  |
| ✓ | Cruz [es · escritorio]: ninguna línea toca el signo del pie de la escalera (12 px de aire) |  |
| ✓ | Cruz [es · escritorio]: ← y → recorren la fila (laboratorio / cómo medimos) |  |
| ✓ | Cruz [es · escritorio]: el rumbo ← lleva a cómo medimos y se ve desde su primera línea |  |
| ✓ | Cruz [es · escritorio]: las salas laterales miden una pantalla y se recorren por dentro |  |
| ✓ | Cruz [es · escritorio]: sin vacío entre el centro y lo de abajo (en el celular, los cuatro tráileres; luego, los resultados) |  |
| ✓ | Cruz [es · escritorio]: los enlaces llevan a cada sala y la brújula lo marca |  |
| ✓ | Cruz [es · escritorio]: la brújula se esconde en el centro y aparece al alejarse |  |
| ✓ | Cruz [en · escritorio]: se llega al centro (el nombre a la vista, brújula en el centro) |  |
| ✓ | Cruz [en · escritorio]: la placa del nombre queda en el centro exacto de la pantalla (±3 px) |  |
| ✓ | Cruz [en · escritorio]: arriba se lee de abajo hacia arriba (la primera pregunta queda junto al centro) |  |
| ✓ | Cruz [en · escritorio]: ninguna línea toca el signo del pie de la escalera (12 px de aire) |  |
| ✓ | Cruz [en · escritorio]: ← y → recorren la fila (laboratorio / cómo medimos) |  |
| ✓ | Cruz [en · escritorio]: el rumbo ← lleva a cómo medimos y se ve desde su primera línea |  |
| ✓ | Cruz [en · escritorio]: las salas laterales miden una pantalla y se recorren por dentro |  |
| ✓ | Cruz [en · escritorio]: sin vacío entre el centro y lo de abajo (en el celular, los cuatro tráileres; luego, los resultados) |  |
| ✓ | Cruz [en · escritorio]: los enlaces llevan a cada sala y la brújula lo marca |  |
| ✓ | Cruz [en · escritorio]: la brújula se esconde en el centro y aparece al alejarse |  |
| ✓ | Cruz [es · móvil]: se llega al centro (el nombre a la vista, brújula en el centro) |  |
| ✓ | Cruz [es · móvil]: la placa del nombre queda en el centro exacto de la pantalla (±3 px) |  |
| ✓ | Cruz [es · móvil]: arriba se lee de abajo hacia arriba (la primera pregunta queda junto al centro) |  |
| ✓ | Cruz [es · móvil]: ninguna línea toca el signo del pie de la escalera (12 px de aire) |  |
| ✓ | Cruz [es · móvil]: ← y → recorren la fila (laboratorio / cómo medimos) |  |
| ✓ | Cruz [es · móvil]: el rumbo ← lleva a cómo medimos y se ve desde su primera línea |  |
| ✓ | Cruz [es · móvil]: las salas laterales miden una pantalla y se recorren por dentro |  |
| ✓ | Cruz [es · móvil]: sin vacío entre el centro y lo de abajo (en el celular, los cuatro tráileres; luego, los resultados) |  |
| ✓ | Cruz [es · móvil]: los enlaces llevan a cada sala y la brújula lo marca |  |
| ✓ | Cruz [es · móvil]: la brújula se esconde en el centro y aparece al alejarse |  |
| ✓ | Cruz [en · móvil]: se llega al centro (el nombre a la vista, brújula en el centro) |  |
| ✓ | Cruz [en · móvil]: la placa del nombre queda en el centro exacto de la pantalla (±3 px) |  |
| ✓ | Cruz [en · móvil]: arriba se lee de abajo hacia arriba (la primera pregunta queda junto al centro) |  |
| ✓ | Cruz [en · móvil]: ninguna línea toca el signo del pie de la escalera (12 px de aire) |  |
| ✓ | Cruz [en · móvil]: ← y → recorren la fila (laboratorio / cómo medimos) |  |
| ✓ | Cruz [en · móvil]: el rumbo ← lleva a cómo medimos y se ve desde su primera línea |  |
| ✓ | Cruz [en · móvil]: las salas laterales miden una pantalla y se recorren por dentro |  |
| ✓ | Cruz [en · móvil]: sin vacío entre el centro y lo de abajo (en el celular, los cuatro tráileres; luego, los resultados) |  |
| ✓ | Cruz [en · móvil]: los enlaces llevan a cada sala y la brújula lo marca |  |
| ✓ | Cruz [en · móvil]: la brújula se esconde en el centro y aparece al alejarse |  |
| ✓ | Centro sin choques: tráileres, rumbos, flechas y placa no se tocan en diez tamaños; nada se sale de su esquina ni de su estación; los cuatro recuadros miden lo mismo y la placa sigue en el centro |  |
| ✓ | Cruz sin JavaScript: todo el contenido sigue ahí, con sus enlaces |  |
| ✓ | Sin JavaScript: cada carrusel de ED02-X1 queda quieto en su primer pasaje, sin controles; «Leer en contexto» lleva al pasaje en la página de su recorrido y cada ficha está en la página |  |
| ✓ | Pasajes de ED02-X1: los 60 de la plantilla, barajados una vez por visita; «siguiente» avanza uno y el foco se queda en el botón; sin avance automático; el inglés conserva el mismo pasaje |  |
| ✓ | Movimiento reducido: el cambio de pasaje aparece sin animación (con movimiento, un fundido corto) |  |
| ✓ | Panel de lectura: «Leer en contexto» abre el pasaje marcado a la vista en su texto original y las lecturas que lo citan (rótulo, nivel, justificación y límite), con el enlace a su recorrido; la nota de incidencias se abre igual; se cierra con Esc, con su botón o tocando afuera, el foco vuelve al enlace y, si algo falta, lo dice |  |
| ✓ | [rc-es] ED02-X1: sin errores ni violaciones de la CSP; idioma, h1, canónica y hreflang; la etiqueta del piloto; cada voz con su rótulo y los cuerpos en español; enlaces que llegan |  |
| ✓ | [rc-es] ED02-X1: el recorrido trae 5 textos, 2 críticas y 32 lecturas, cada una con una sola marca en su regla de 0 a 4; la transferencia de 351 palabras lleva su aviso |  |
| ✓ | [rc-es] ED02-X1: seguir un pasaje lo ilumina entero (todos sus tramos, ninguno más) y lo deja a la vista bajo la ruta |  |
| ✓ | [rc-en] ED02-X1: sin errores ni violaciones de la CSP; idioma, h1, canónica y hreflang; la etiqueta del piloto; cada voz con su rótulo y los cuerpos en español; enlaces que llegan |  |
| ✓ | [rc-en] ED02-X1: el recorrido trae 5 textos, 2 críticas y 32 lecturas, cada una con una sola marca en su regla de 0 a 4; la transferencia de 351 palabras lleva su aviso |  |
| ✓ | [rc-en] ED02-X1: seguir un pasaje lo ilumina entero (todos sus tramos, ninguno más) y lo deja a la vista bajo la ruta |  |
| ✓ | [rc-gpt] ED02-X1: sin errores ni violaciones de la CSP; idioma, h1, canónica y hreflang; la etiqueta del piloto; cada voz con su rótulo y los cuerpos en español; enlaces que llegan |  |
| ✓ | [rc-gpt] ED02-X1: el recorrido trae 5 textos, 2 críticas y 32 lecturas, cada una con una sola marca en su regla de 0 a 4 |  |
| ✓ | [rc-gpt] ED02-X1: seguir un pasaje lo ilumina entero (todos sus tramos, ninguno más) y lo deja a la vista bajo la ruta |  |
| ✓ | [metodo-es] ED02-X1: sin errores ni violaciones de la CSP; idioma, h1, canónica y hreflang; la etiqueta del piloto; cada voz con su rótulo y los cuerpos en español; enlaces que llegan |  |
| ✓ | [metodo-en] ED02-X1: sin errores ni violaciones de la CSP; idioma, h1, canónica y hreflang; la etiqueta del piloto; cada voz con su rótulo y los cuerpos en español; enlaces que llegan |  |
| ✓ | En el celular la etiqueta del piloto queda a la vista al llegar; el tráiler de resultados y su sala conservan las advertencias (orden condicional, escenarios, sesgo, 351 palabras, fuera del índice, límites) y la tabla cabe sin desplazarse |  |
| ✓ | Cambio de idioma: el mismo pasaje, palabra por palabra, sigue en español original (lang=es) y avisa que no está traducido; la interfaz cambia, la voz del modelo no |  |
| ✓ | axe-core 4.14 · WCAG 2.0/2.1/2.2 A y AA: sin violaciones (8 páginas × 2 anchos: portadas, 404, recorridos y método) |  |
| ✓ | axe-core · buenas prácticas: sin avisos |  |
| ✓ | Espaciado de texto ampliado (WCAG 1.4.12): no se pierde texto |  |
| ✓ | Capturas de escritorio y móvil, ES, EN y 404 |  |
