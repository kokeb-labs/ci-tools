"""``kokeb-docs serve SITE PORT``: serve a built site on 127.0.0.1 the way GitHub Pages serves it.

GitHub Pages sends HTML, CSS, JavaScript, JSON, SVG and XML gzip-compressed to a client that accepts it. Lighthouse
measures what it is served, so a plain ``python3 -m http.server`` (no compression) scores every page on two to three
times the bytes a reader downloads, and the performance score then depends on runner speed more than on the page.
This server compresses the same types, so the budget measures the published site.
"""

from __future__ import annotations

import gzip
import http.server
import os
import pathlib
import sys
from functools import partial

COMPRESSED = (".html", ".css", ".js", ".json", ".svg", ".xml", ".txt", ".map")


class PagesHandler(http.server.SimpleHTTPRequestHandler):
    """Static files as GitHub Pages sends them: compressed text, everything else unchanged."""

    _body: bytes | None = None

    def send_head(self):  # noqa: D401 - http.server's name
        self._body = None
        path = self.translate_path(self.path)
        if os.path.isdir(path):
            if not self.path.split("?", 1)[0].endswith("/"):
                return super().send_head()  # the redirect to the trailing slash
            path = os.path.join(path, "index.html")
        if "gzip" not in self.headers.get("Accept-Encoding", "") or not path.endswith(COMPRESSED):
            return super().send_head()
        try:
            body = gzip.compress(pathlib.Path(path).read_bytes(), 6)
        except OSError:
            return super().send_head()  # the 404
        self.send_response(200)
        self.send_header("Content-Type", self.guess_type(path))
        self.send_header("Content-Encoding", "gzip")
        self.send_header("Vary", "Accept-Encoding")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self._body = body
        return None

    def do_GET(self):  # noqa: N802 - http.server's name
        f = self.send_head()
        if self._body is not None:
            self.wfile.write(self._body)
        elif f:
            try:
                self.copyfile(f, self.wfile)
            finally:
                f.close()

    def do_HEAD(self):  # noqa: N802 - http.server's name
        f = self.send_head()
        if f:
            f.close()

    def log_message(self, *args):
        pass


def server(site: pathlib.Path, port: int) -> http.server.ThreadingHTTPServer:
    """A server for ``site`` on 127.0.0.1:``port`` (0 picks a free port); the caller runs serve_forever()."""
    return http.server.ThreadingHTTPServer(("127.0.0.1", port), partial(PagesHandler, directory=str(site)))


def main(argv: list[str]) -> int:
    if len(argv) != 2 or not argv[1].isdigit():
        print("usage: kokeb-docs serve SITE PORT", file=sys.stderr)
        return 2
    site = pathlib.Path(argv[0])
    if not (site / "index.html").is_file():
        print(f"kokeb-docs serve: no index.html in {site}", file=sys.stderr)
        return 2
    server(site, int(argv[1])).serve_forever()
    return 0
