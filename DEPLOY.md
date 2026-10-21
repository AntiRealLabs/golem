# Deploy de Golem Bench

## Estado actual

`golembench.org` vive en Cloudflare Pages, en el proyecto:

- `golembench`

Se publica como proyecto de *direct upload* desde GitHub Actions, igual que
simioplateado. En el dashboard aparece `No Git connection`: es lo esperado.

**Hoy se publica la portada con ED02-X1 y, aparte, el primer corte de ED01**
(ED01 desde el 18 oct 2026; ED02-X1 desde el 20 oct 2026, con sus 26 páginas de
lectura; las dos con aprobación de Juan): la carpeta `site/`. El prototipo del Lab
no está en este repo y **no se publica** (ver `CLAUDE.md`, «Antes de publicar el Lab»).

## Flujo

```text
git push origin main          (con cambios en site/)
  -> GitHub Actions           .github/workflows/deploy-pages.yml
  -> puerta de publicación    herramientas/comprobar_publicacion.py site
  -> wrangler pages deploy site --project-name=golembench --branch=main
```

El primer despliegue crea el proyecto `golembench` si todavía no existe. Un
push que solo cambie documentos no despliega nada.

**Borradores:** cualquier otra rama que toque `site/` se publica como vista previa
(`.github/workflows/deploy-preview.yml`) en `https://<rama>.golembench.pages.dev`,
sin tocar golembench.org. Así se revisa en el teléfono antes de pasar a `main`.
Para volver a desplegar sin cambios: *Actions → Deploy Cloudflare Pages → Run
workflow*.

## Secretos requeridos en GitHub

*Settings → Secrets and variables → Actions*, con los mismos nombres que en
simioplateado:

- `CLOUDFLARE_API_TOKEN`: token con el permiso *Account · Cloudflare Pages · Edit*
- `CLOUDFLARE_ACCOUNT_ID`

El token no se pega en chats ni en archivos del repo.

## Dominio

- Registrador: Namecheap. Titular: Anti-Real Labs S.A.S. Nameservers (desde el 17 oct 2026):
  `ram.ns.cloudflare.com` y `rosa.ns.cloudflare.com`. DNSSEC apagado en Namecheap.
- Zona `golembench.org` en la misma cuenta de Cloudflare que los otros dominios (plan Free).
- *Custom domains* del proyecto: `golembench.org` y `www.golembench.org`. Se agregan
  una sola vez en *Workers & Pages → golembench → Custom domains*; como la zona está en
  la misma cuenta, Cloudflare crea los registros DNS.
- `golembench.pages.dev` queda como dirección técnica.
- Al conectar la zona se borraron los dos registros de estacionamiento de Namecheap (A `@` y
  CNAME `www`). Los MX y el TXT de reenvío de correo de Namecheap siguen en la zona, sin uso.
- Cloudflare oculta los correos de la página (Email Address Obfuscation): reescribe el `mailto:`
  e inserta `/cdn-cgi/scripts/…/email-decode.min.js`. La CSP lo admite porque es del mismo origen.

## Caché

- El HTML llega fresco en cada visita (`max-age=0`). CSS, JS e imágenes salen con
  `max-age=14400`: es el *Browser Cache TTL* de 4 horas de la zona, que se impone sobre lo que
  manda Pages.
- Por eso las páginas piden `portada.css` y `centro.js` con `?v=<huella>`: cuando el archivo
  cambia, cambia la dirección y el navegador lo pide de nuevo. Sin eso, quien ya había visitado
  vería el HTML nuevo con el CSS viejo (pasó el 18 oct 2026, al publicar la cruz).
  `herramientas/versionar_recursos.py` pone las huellas; la verificación y los dos workflows
  fallan si alguna quedó vieja.
- Las fuentes llevan caché de un año (`immutable`): un archivo de fuente nunca se cambia
  conservando su nombre.
- Una imagen que cambie conservando su nombre puede tardar hasta 4 horas en verse donde ya
  estaba guardada. Si importa, se publica con otro nombre.

## Antes de cada push

```bash
python3 -I herramientas/construir_ed01.py PAQUETE site   # si llegó un paquete nuevo de ED01
python3 -I herramientas/cotejar_ed01.py PAQUETE site     # y su cotejo: 0 fallas
python3 -I herramientas/construir_ed02x1.py PAQUETE site # si llegó un paquete nuevo de ED02-X1
python3 -I herramientas/cotejar_ed02x1.py PAQUETE site   # y su cotejo: 0 fallas
python3 -I herramientas/versionar_recursos.py       # si cambiaron portada.css, centro.js o archivo.js
python3 -I herramientas/verificar_portada.py        # Playwright + Chromium; todo debe dar correcto
python3 -I herramientas/comprobar_publicacion.py site
```

Dependencias de las herramientas: `herramientas/requirements.txt`.

Para mirar el sitio en local tal como lo sirve Pages (cabeceras, 404, `/en` → `/en/`):

```bash
python3 -I herramientas/servidor_local.py 8788      # http://127.0.0.1:8788
```

## Qué no cambiar sin una decisión explícita

- No conectar el proyecto a Git desde el dashboard de Cloudflare: duplicaría los
  despliegues. Si algún día se migra, hacerlo como en simioplateado (prueba,
  comprobar dominios y solo entonces quitar el workflow).
- No copiar a `site/` datos del piloto IA-01 ni archivos del prototipo del Lab. Lo de
  ED01 entra solo con `construir_ed01.py`, desde un paquete de coordinación; lo de ED02-X1,
  solo con `construir_ed02x1.py`, desde su paquete público. Un paquete nuevo se integra en
  una rama local y no se sube hasta que Juan lo apruebe y quede anotado abajo: cualquier rama
  que toque `site/` sale como vista previa pública.
- No relajar `comprobar_publicacion.py` salvo en el commit que publique algo aprobado,
  con la aprobación anotada abajo. El 18 oct 2026 admitió «IA-01» y «BF-03» para el
  primer corte ED01 (ver el registro).
- La CSP de `site/_headers` no admite estilos ni scripts en línea. Cloudflare Web
  Analytics está activo (comprobado el 18 oct 2026): Cloudflare inyecta `beacon.min.js`
  desde `static.cloudflareinsights.com` y envía las mediciones a `/cdn-cgi/rum`. La CSP
  ya lo admite; cualquier otro servicio externo requiere cambiar la CSP.

## Registro de publicaciones

| Fecha | Qué se publicó | Aprobó |
|---|---|---|
| 2026-10-17 | Portada fase 1, ES/EN, sin datos del piloto | Juan · Anti-Real Labs (en el chat de diseño) |
| 2026-10-18 | Portada «la cruz»: se llega a la pregunta y se navega hacia los cuatro lados. Lema «Preguntas desde el futuro». ES/EN, sin datos del piloto. CSS y JS con huella de versión | Juan · Anti-Real Labs (en el chat de diseño) |
| 2026-10-18 | Portada «el mapa en cruz», sobre el boceto de Juan: el nombre en el centro, cuatro rumbos (Preguntas abiertas, Cómo medimos, Laboratorio, Resultados de evaluaciones) y cuatro cuadrantes que invitan a navegar. Sin la pregunta como titular; tarjetas con el lema. ES/EN, sin datos del piloto | Juan · Anti-Real Labs (en el chat de diseño) |
| 2026-10-18 | Primer corte ED01, del paquete de contenidos v0.1 de coordinación: cuatro tráileres en las esquinas de la cruz y sus salas en profundidad (seis apuestas, cifras, cinco fragmentos con sus fuentes completas, supuesto a examen, cohorte en orden fijo, fases, ranking en preparación sin datos, «Una pregunta. Dos lecturas.», método y límites). Símbolos de las estaciones y baldosas en el celular (rama `estaciones`). La mascota del golem firma el pie y va a la izquierda de «Golem», de su tamaño y a su altura, en la placa, en «Golem Lab» y en las tarjetas para compartir. La puerta admite «IA-01» (nombre de la serie anterior) y «BF-03» (texto literal de una entrega). ES/EN | Juan · Anti-Real Labs (en el chat de diseño: «PUBLICA!! ME ENCANTA!») |
| 2026-10-20 | ED02-X1, piloto exploratorio, del paquete público de coordinación (18 oct 2026). En la portada: la cartela «Piloto exploratorio · ED02-X1», las cuatro esquinas y los tráileres del celular; en Resultados, el orden condicional (GPT-6.1-sol 86,2 · Claude Opus 5.5 82,7) con los dos motores al lado, los 42 escenarios partidos por motor, el aviso de 351 palabras con la nota de incidencias y lo que queda fuera del índice, sin cero ni puesto (Gemini, pendiente); en el Laboratorio, las cuatro unidades, el carrusel de 60 pasajes citados por los jueces y los doce recorridos; en Cómo medimos, tres especialidades puntuadas por dos motores. 26 páginas de lectura (12 recorridos y el método, ES/EN) con 1.222 pasajes y las 144 lecturas. ED01 sigue debajo y aparte; su tríptico de la esquina sale. En inglés, interfaz y editorial; los cuerpos siguen en español original. Newsreader 600 para lo que el modelo escribió en negrita o como título. Las decisiones ✎ de Claude salen con esta aprobación. La puerta no cambia | Juan · Anti-Real Labs (en el chat de diseño: «PUBLICA PORFA!») |
| 2026-10-20 | Revisión de la portada, sobre ocho propuestas que trajo Juan: en el centro, frases más cortas y la izquierda con dibujo en lugar de cifras (lo que pesan las preguntas, en una barra de tres tercios con su «?»; quién puntúa cada especialidad, los sellos J1–J3 frente a los dos motores); sin los tres «peso 30» ni los nombres completos de J1–J3, que viven en Cómo medimos. Cómo medimos con una sola entrada, los criterios de la pregunta marcados y de dónde sale el 30 %. El laboratorio empieza por el pasaje, cada cifra va una vez y Golem Lab, compacto, al final. «Cambiar de motor invierte el orden» encima de los dos motores en la tabla de resultados. «Volver al centro» ya no tapa texto entre 960 y 1339 px. Los textos nuevos, en `herramientas/ed02x1_ajustes.json` con su origen. La puerta no cambia | Juan · Anti-Real Labs (en el chat de diseño: «publica porfa») |
| 2026-10-21 | Vista móvil, sobre lo que Juan vio en su teléfono: en la vista inicial cada baldosa resume su estación, pequeña y concreta (Preguntas, los seis principios, una palabra de cada apuesta; Laboratorio, 12 recorridos, 60 textos, 24 críticas y 144 lecturas; Cómo medimos, J1–J3 con su verbo y su peso de 1/3 y los motores GPT y Claude; Resultados, el orden del índice combinado, 86,2 y 82,7, con «Cambiar de motor invierte el orden»). Resultados empieza por el orden, en el celular y en el escritorio: la nota, el alcance y el corte van debajo de la tabla. En el celular la tabla se lee en tarjetas, sin cabeceras partidas, y los roles ARIA la mantienen como tabla. La puerta no cambia | Juan · Anti-Real Labs (en el chat de diseño: «publica porfa») |
