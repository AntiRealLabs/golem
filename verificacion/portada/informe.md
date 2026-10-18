# Verificación de la portada

**94 de 94 comprobaciones correctas** · 2026-10-18 01:14 (UTC−5) · Chromium (Playwright) contra `herramientas/servidor_local.py`.

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
| ✓ | sitemap.xml es XML válido con las dos páginas |  |
| ✓ | favicon.ico trae 16, 32 y 48 px |  |
| ✓ | apple-touch-icon.png mide 180×180 |  |
| ✓ | og-es.jpg mide 1200×630 |  |
| ✓ | og-en.jpg mide 1200×630 |  |
| ✓ | Figura del centro: recorte del arte original sin reescalar; las fuentes quedan fuera de site/ |  |
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
| ✓ | [es] enlaces internos válidos y solo los externos previstos |  |
| ✓ | [es] fase 1: sin nombres de modelos ni corridas en el texto |  |
| ✓ | [es] fase 1: ninguna cifra del piloto (solo J1–J3, 01–04 y el año) |  |
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
| ✓ | [en] enlaces internos válidos y solo los externos previstos |  |
| ✓ | [en] fase 1: sin nombres de modelos ni corridas en el texto |  |
| ✓ | [en] fase 1: ninguna cifra del piloto (solo J1–J3, 01–04 y el año) |  |
| ✓ | [en] sin restos del otro idioma fuera de lo marcado con lang |  |
| ✓ | [404] sin errores de consola ni violaciones de la CSP |  |
| ✓ | [404] fuentes de la marca cargadas |  |
| ✓ | [404] todo se sirve desde el mismo origen |  |
| ✓ | [404] peso total de la página ≤ 700 KB |  |
| ✓ | Paridad ES/EN: mismos h2, h3, elementos de lista, párrafos y enlaces |  |
| ✓ | Sin desplazamiento horizontal a 1440, 1024, 768, 390 y 320 px |  |
| ✓ | Objetivos táctiles ≥ 24 px en móvil (WCAG 2.5.8) |  |
| ✓ | Teclado: el primer Tab se queda en el centro, a la vista (selector de idioma) |  |
| ✓ | Teclado: desde el centro, ES → EN → ↑ → ← → → → ↓ |  |
| ✓ | Teclado: el foco se ve (contorno de 3 px) |  |
| ✓ | Cruz [es · escritorio]: se llega al centro (pregunta a la vista, brújula en el centro) |  |
| ✓ | Cruz [es · escritorio]: el sello queda en el centro exacto de la pantalla (±3 px) |  |
| ✓ | Cruz [es · escritorio]: arriba se lee de abajo hacia arriba (la primera pregunta queda junto al centro) |  |
| ✓ | Cruz [es · escritorio]: ← y → recorren la fila (lo que guardamos / lo que medimos) |  |
| ✓ | Cruz [es · escritorio]: la pista ← lleva a lo que medimos y se ve desde su primera línea |  |
| ✓ | Cruz [es · escritorio]: los enlaces llevan a cada sala y la brújula lo marca |  |
| ✓ | Cruz [es · escritorio]: la brújula se esconde en el centro y aparece al alejarse |  |
| ✓ | Cruz [en · escritorio]: se llega al centro (pregunta a la vista, brújula en el centro) |  |
| ✓ | Cruz [en · escritorio]: el sello queda en el centro exacto de la pantalla (±3 px) |  |
| ✓ | Cruz [en · escritorio]: arriba se lee de abajo hacia arriba (la primera pregunta queda junto al centro) |  |
| ✓ | Cruz [en · escritorio]: ← y → recorren la fila (lo que guardamos / lo que medimos) |  |
| ✓ | Cruz [en · escritorio]: la pista ← lleva a lo que medimos y se ve desde su primera línea |  |
| ✓ | Cruz [en · escritorio]: los enlaces llevan a cada sala y la brújula lo marca |  |
| ✓ | Cruz [en · escritorio]: la brújula se esconde en el centro y aparece al alejarse |  |
| ✓ | Cruz [es · móvil]: se llega al centro (pregunta a la vista, brújula en el centro) |  |
| ✓ | Cruz [es · móvil]: el sello queda en el centro exacto de la pantalla (±3 px) |  |
| ✓ | Cruz [es · móvil]: arriba se lee de abajo hacia arriba (la primera pregunta queda junto al centro) |  |
| ✓ | Cruz [es · móvil]: ← y → recorren la fila (lo que guardamos / lo que medimos) |  |
| ✓ | Cruz [es · móvil]: la pista ← lleva a lo que medimos y se ve desde su primera línea |  |
| ✓ | Cruz [es · móvil]: los enlaces llevan a cada sala y la brújula lo marca |  |
| ✓ | Cruz [es · móvil]: la brújula se esconde en el centro y aparece al alejarse |  |
| ✓ | Cruz [en · móvil]: se llega al centro (pregunta a la vista, brújula en el centro) |  |
| ✓ | Cruz [en · móvil]: el sello queda en el centro exacto de la pantalla (±3 px) |  |
| ✓ | Cruz [en · móvil]: arriba se lee de abajo hacia arriba (la primera pregunta queda junto al centro) |  |
| ✓ | Cruz [en · móvil]: ← y → recorren la fila (lo que guardamos / lo que medimos) |  |
| ✓ | Cruz [en · móvil]: la pista ← lleva a lo que medimos y se ve desde su primera línea |  |
| ✓ | Cruz [en · móvil]: los enlaces llevan a cada sala y la brújula lo marca |  |
| ✓ | Cruz [en · móvil]: la brújula se esconde en el centro y aparece al alejarse |  |
| ✓ | Cruz sin JavaScript: todo el contenido sigue ahí, con sus enlaces |  |
| ✓ | axe-core 4.14 · WCAG 2.0/2.1/2.2 A y AA: sin violaciones (3 páginas × 2 anchos) |  |
| ✓ | axe-core · buenas prácticas: sin avisos |  |
| ✓ | Espaciado de texto ampliado (WCAG 1.4.12): no se pierde texto |  |
| ✓ | Capturas de escritorio y móvil, ES, EN y 404 |  |
