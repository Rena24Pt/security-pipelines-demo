"""
Mini app Flask deliberadamente vulnerável — demo OWASP Top 10.
Cada vulnerabilidade está marcada com um comentário VULN e a categoria OWASP.
NUNCA usar este padrão em código real — é material didático.
"""
import sqlite3
from flask import Flask, request

app = Flask(__name__)
DB = "/tmp/demo.db"


def init_db():
    """Cria uma BD sqlite mínima com dados de teste."""
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
    name = request.args.get("name", "mundo")
    # VULN — A03 Injection (Reflected XSS):
    # o input do utilizador é concatenado diretamente no HTML sem escape.
    # Prova: /hello?name=<script>alert(1)</script>
    # Correção: usar templates Jinja com autoescape (render_template_string
    # com {{ name }}) ou markupsafe.escape(name).
    return f"<h1>Olá, {name}!</h1>"


@app.route("/user")
def user():
    uid = request.args.get("id", "1")
    conn = sqlite3.connect(DB)
    # VULN — A03 Injection (SQL Injection):
    # a query é construída por concatenação de strings com input do utilizador.
    # Prova: /user?id=1 OR 1=1   (devolve TODOS os utilizadores)
    # Correção: queries parametrizadas: conn.execute("... WHERE id = ?", (uid,))
    rows = conn.execute("SELECT id, name, role FROM users WHERE id = " + uid).fetchall()
    conn.close()
    return {"users": [{"id": r[0], "name": r[1], "role": r[2]} for r in rows]}


@app.after_request
def no_security_headers(resp):
    # VULN — A05 Security Misconfiguration:
    # a app não define nenhum security header (CSP, HSTS, X-Frame-Options...).
    # Prova: corre o headguard contra http://127.0.0.1:5000 → grade F.
    # Correção: adicionar headers (ver branch 'fixed').
    return resp


if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5000)
