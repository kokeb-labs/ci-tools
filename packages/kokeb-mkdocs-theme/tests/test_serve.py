"""kokeb-docs serve: text compressed as GitHub Pages sends it, other files and redirects unchanged."""

from __future__ import annotations

import gzip
import http.client
import pathlib
import tempfile
import threading
import unittest

from kokeb_mkdocs_theme import serve


class ServeTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        site = pathlib.Path(self.tmp.name)
        (site / "quickstart").mkdir()
        self.html = b"<p>" + b"quickstart " * 200 + b"</p>"
        (site / "index.html").write_bytes(b"<p>home</p>")
        (site / "quickstart" / "index.html").write_bytes(self.html)
        (site / "font.woff2").write_bytes(b"\x00font")
        self.srv = serve.server(site, 0)
        threading.Thread(target=self.srv.serve_forever, daemon=True).start()

    def tearDown(self):
        self.srv.shutdown()
        self.srv.server_close()
        self.tmp.cleanup()

    def get(self, path, gz=True):
        c = http.client.HTTPConnection("127.0.0.1", self.srv.server_address[1])
        c.request("GET", path, headers={"Accept-Encoding": "gzip"} if gz else {})
        r = c.getresponse()
        body = r.read()
        c.close()
        return r, body

    def test_text_is_gzipped_when_accepted(self):
        r, body = self.get("/quickstart/")
        self.assertEqual(r.status, 200)
        self.assertEqual(r.getheader("Content-Encoding"), "gzip")
        self.assertEqual(gzip.decompress(body), self.html)
        self.assertLess(len(body), len(self.html))

    def test_plain_without_accept_encoding(self):
        r, body = self.get("/quickstart/", gz=False)
        self.assertIsNone(r.getheader("Content-Encoding"))
        self.assertEqual(body, self.html)

    def test_binary_is_sent_as_is(self):
        r, body = self.get("/font.woff2")
        self.assertIsNone(r.getheader("Content-Encoding"))
        self.assertEqual(body, b"\x00font")

    def test_directory_without_slash_redirects(self):
        r, _ = self.get("/quickstart")
        self.assertEqual(r.status, 301)
        self.assertEqual(r.getheader("Location"), "/quickstart/")

    def test_missing_file_is_404(self):
        r, _ = self.get("/nope.html")
        self.assertEqual(r.status, 404)

    def test_usage(self):
        self.assertEqual(serve.main([]), 2)
        self.assertEqual(serve.main([self.tmp.name + "/missing", "1"]), 2)


if __name__ == "__main__":
    unittest.main()
