"""
Fixed version of the demo app — the three OWASP findings remediated.
Each fix is marked with a FIX comment referencing the original vulnerability.
(The vulnerable version lives in git history — that red-to-green diff is the point.)
"""
import sqlite3
from flask import Flask, request, render_template_string
from werkzeug.serving import WSGIRequestHandler

# FIX — information disclosure: don't advertise framework + versions.
# (Werkzeug's dev server injects its own "Server: Werkzeug/x.y Python/x.y" header;
# override it so only our neutral banner goes out.)
WSGIRequestHandler.server_version = "secure-pipeline-demo"
WSGIRequestHandler.sys_version = ""

app = Flask(__name__)
DB = "/tmp/demo.db"


def init_db():
    """Create a minimal sqlite DB with test data."""
    conn = sqlite3.connect(DB)
    conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER, name TEXT, role TEXT)")
    conn.execute("DELETE FROM users")
    conn.executemany(
        "INSERT INTO users VALUES (?, ?, ?)",
        [(1, "ana", "admin"), (2, "bruno", "user"), (3, "carla", "user")],
    )
    conn.commit()
    conn.close()


@app.route("/hello")
def hello():
    name = request.args.get("name", "world")
    # FIX — A03 Injection (Reflected XSS):
    # Jinja autoescapes {{ name }}, so injected markup is rendered as inert text.
    return render_template_string("<h1>Hello, {{ name }}!</h1>", name=name)


@app.route("/user")
def user():
    uid = request.args.get("id", "1")
    conn = sqlite3.connect(DB)
    # FIX — A03 Injection (SQL Injection):
    # parameterized query — user input is data, never SQL syntax.
    try:
        rows = conn.execute(
            "SELECT id, name, role FROM users WHERE id = ?", (uid,)
        ).fetchall()
    except sqlite3.Error:
        rows = []
    conn.close()
    return {"users": [{"id": r[0], "name": r[1], "role": r[2]} for r in rows]}


@app.after_request
def security_headers(resp):
    # FIX — A05 Security Misconfiguration: explicit security headers.
    # (HSTS deliberately absent: it only makes sense over TLS, which terminates
    # upstream — that's also why the CI gate targets grade B on plain HTTP.)
    resp.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none'"
    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    resp.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    resp.headers["Cross-Origin-Opener-Policy"] = "same-origin"
    resp.headers["Cross-Origin-Resource-Policy"] = "same-origin"
    return resp


if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5000)
