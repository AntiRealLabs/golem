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
Para volver a desplegar sin cambios: *Actions → Deploy Cloudflare Pages → Run
workflow*.

## Secretos requeridos en GitHub

*Settings → Secrets and variables → Actions*, con los mismos nombres que en
simioplateado:

- `CLOUDFLARE_API_TOKEN`: token con el permiso *Account · Cloudflare Pages · Edit*
- `CLOUDFLARE_ACCOUNT_ID`

El token no se pega en chats ni en archivos del repo.

## Dominio

- Registrador: Namecheap. Titular: Anti-Real Labs S.A.S. Nameservers: los de Cloudflare.
- Zona `golembench.org` en la misma cuenta de Cloudflare que los otros dominios (plan Free).
- *Custom domains* del proyecto: `golembench.org` y `www.golembench.org`. Se agregan
  una sola vez en *Workers & Pages → golembench → Custom domains*; como la zona está en
  la misma cuenta, Cloudflare crea los registros DNS.
- `golembench.pages.dev` queda como dirección técnica.

## Antes de cada push

```bash
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
- La CSP de `site/_headers` no admite estilos ni scripts en línea. Si se activa
  Cloudflare Web Analytics, ya está permitido; cualquier otro servicio externo
  requiere cambiar la CSP.

## Registro de publicaciones

| Fecha | Qué se publicó | Aprobó |
|---|---|---|
| 2026-10-17 | Portada fase 1, ES/EN, sin datos del piloto | Juan · Anti-Real Labs (en el chat de diseño) |
