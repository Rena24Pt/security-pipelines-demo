"""
Deliberately vulnerable mini Flask app — OWASP Top 10 demo.
Every vulnerability is marked with a VULN comment, its OWASP category,
and how it should be fixed. This is teaching material — never write
code like this in production.
"""
import sqlite3
from flask import Flask, request

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
    # VULN — A03 Injection (Reflected XSS):
    # user input is concatenated straight into the HTML, unescaped.
    # Proof: /hello?name=<script>alert(1)</script>
    # Fix: Jinja templates with autoescaping (render_template_string + {{ name }})
    # or markupsafe.escape(name).
    return f"<h1>Hello, {name}!</h1>"


@app.route("/user")
def user():
    uid = request.args.get("id", "1")
    conn = sqlite3.connect(DB)
    # VULN — A03 Injection (SQL Injection):
    # the query is built by string concatenation with user input.
    # Proof: /user?id=1 OR 1=1   (returns EVERY user)
    # Fix: parameterized queries: conn.execute("... WHERE id = ?", (uid,))
    rows = conn.execute("SELECT id, name, role FROM users WHERE id = " + uid).fetchall()
    conn.close()
    return {"users": [{"id": r[0], "name": r[1], "role": r[2]} for r in rows]}


@app.after_request
def no_security_headers(resp):
    # VULN — A05 Security Misconfiguration:
    # the app sets no security headers at all (CSP, HSTS, X-Frame-Options...).
    # Proof: headguard against http://127.0.0.1:5000 → grade F.
    # Fix: set the headers (see the 'fixed' version).
    return resp


if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5000)
