# Golem Bench

Sitio de [golembench.org](https://golembench.org) · «Preguntas desde el futuro / Questions from the future».
Un proyecto de [Anti-Real Labs](https://antireallabs.com).

| Carpeta | Qué es |
|---|---|
| `site/` | Portada pública en español e inglés (lo único que se publica) |
| `herramientas/` | Verificación, servidor local, puerta de publicación e imágenes |

- Despliegue: [`DEPLOY.md`](DEPLOY.md). Cada push a `main` que toque `site/` se publica con GitHub Actions en Cloudflare Pages.
- Reglas del proyecto y condiciones para publicar el Lab: [`CLAUDE.md`](CLAUDE.md).

Probar en local: `python3 -I herramientas/servidor_local.py 8788` → http://127.0.0.1:8788
Verificar: `python3 -I herramientas/verificar_portada.py` (dependencias en `herramientas/requirements.txt`).
