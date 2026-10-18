# Deploy de Golem Bench

## Estado actual

`golembench.org` vive en Cloudflare Pages, en el proyecto:

- `golembench`

Se publica como proyecto de *direct upload* desde GitHub Actions, igual que
simioplateado. En el dashboard aparece `No Git connection`: es lo esperado.

**Hoy se publica solo la portada (fase 1):** la carpeta `site/`. El prototipo
del Lab no está en este repo y **no se publica** (ver `CLAUDE.md`, «Antes de
publicar el Lab»).

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
python3 -I herramientas/versionar_recursos.py       # si cambiaron portada.css o centro.js
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
- No copiar a `site/` datos del piloto ni archivos del prototipo del Lab.
- No relajar `comprobar_publicacion.py` salvo en el commit que publique el Lab,
  con la aprobación anotada abajo.
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
