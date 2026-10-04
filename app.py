"""Tiny static server for Heroku, with optional password protection.

Set APP_PASSWORD (and optionally APP_USER, default "knitter") as Heroku config vars
to require a login. If APP_PASSWORD is unset, the site is public.
"""
import base64, hmac, os
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.abspath(__file__))
USER = os.environ.get("APP_USER", "knitter")
PASSWORD = os.environ.get("APP_PASSWORD")
HIDDEN = {"app.py", "Procfile", "requirements.txt", ".python-version", ".gitignore"}


class Handler(SimpleHTTPRequestHandler):
    def _authorized(self):
        if not PASSWORD:
            return True
        header = self.headers.get("Authorization", "")
        if not header.startswith("Basic "):
            return False
        try:
            user, _, pw = base64.b64decode(header[6:]).decode().partition(":")
        except Exception:
            return False
        return hmac.compare_digest(user, USER) and hmac.compare_digest(pw, PASSWORD)

    def _gate(self):
        if self.path.lstrip("/").split("?")[0] in HIDDEN:
            self.send_error(404)
            return False
        if not self._authorized():
            self.send_response(401)
            self.send_header("WWW-Authenticate", 'Basic realm="Hoff Aran chart"')
            self.end_headers()
            return False
        return True

    def do_GET(self):
        if self._gate():
            super().do_GET()

    def do_HEAD(self):
        if self._gate():
            super().do_HEAD()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8765))
    print(f"Serving on port {port} ({'password protected' if PASSWORD else 'public'})")
    ThreadingHTTPServer(("0.0.0.0", port), partial(Handler, directory=ROOT)).serve_forever()
