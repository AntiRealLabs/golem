#!/usr/bin/env python3
"""Servidor local que imita lo esencial de Cloudflare Pages para probar site/.

Uso:  python3 -I herramientas/servidor_local.py [PUERTO]   → http://127.0.0.1:PUERTO

Imita: index.html por carpeta, redirección /carpeta → /carpeta/ (308),
404.html con estado 404 para rutas que no existen, y las reglas de _headers
(los valores repetidos de varias reglas se unen con comas, como en Pages).
No imita: la caché de Cloudflare, la compresión ni lo que añade la zona
(ofuscación de correos, Web Analytics).
"""
import fnmatch
import http.server
import mimetypes
import sys
from pathlib import Path

SITE = Path(__file__).resolve().parents[1] / "site"

TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".woff2": "font/woff2",
    ".svg": "image/svg+xml",
    ".ico": "image/x-icon",
    ".png": "image/png",
    ".txt": "text/plain; charset=utf-8",
    ".xml": "application/xml; charset=utf-8",
}


def parse_headers(site):
    rules, current = [], None
    f = site / "_headers"
    if not f.exists():
        return rules
    for raw in f.read_text(encoding="utf-8").splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if raw[0] not in " \t":
            current = (raw.strip(), [])
            rules.append(current)
        elif current is not None and ":" in raw:
            k, v = raw.strip().split(":", 1)
            current[1].append((k.strip(), v.strip()))
    return rules


def headers_for(path, rules):
    out = {}
    for pattern, hs in rules:
        if fnmatch.fnmatchcase(path, pattern):
            for k, v in hs:
                out[k] = f"{out[k]}, {v}" if k in out else v
    return out


class Handler(http.server.BaseHTTPRequestHandler):
    rules = parse_headers(SITE)

    def log_message(self, *a):
        pass

    def send(self, status, body=b"", ctype=None, extra=None, path=None):
        self.send_response(status)
        if ctype:
            self.send_header("Content-Type", ctype)
        for k, v in headers_for(path or self.path.split("?")[0], self.rules).items():
            if k.lower() == "content-type" and ctype:
                continue
            self.send_header(k, v)
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        url = self.path.split("?")[0].split("#")[0]
        if url.startswith("/_headers") or url.startswith("/_redirects"):
            return self.not_found(url)
        target = (SITE / url.lstrip("/")).resolve()
        if SITE not in target.parents and target != SITE:
            return self.not_found(url)
        if target.is_dir():
            if not url.endswith("/"):
                return self.send(308, extra={"Location": url + "/"})
            target = target / "index.html"
        if target.is_file():
            ctype = TYPES.get(target.suffix, mimetypes.guess_type(target.name)[0] or "application/octet-stream")
            return self.send(200, target.read_bytes(), ctype)
        return self.not_found(url)

    def not_found(self, url):
        page = SITE / "404.html"
        return self.send(404, page.read_bytes() if page.exists() else b"404", TYPES[".html"], path=url)


def serve(port=0):
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", port), Handler)
    return srv


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8788
    srv = serve(port)
    print(f"http://127.0.0.1:{srv.server_address[1]}  (site/)")
    srv.serve_forever()
