# Secure Pipeline Demo

Demo de **DevSecOps num nutshell**: uma pequena app Flask com vulnerabilidades
deliberadas (OWASP Top 10), uma pipeline GitHub Actions que as apanha com
**SAST (Semgrep)** e **DAST (OWASP ZAP)**, e a remediação documentada commit a commit.

## Estrutura

- `app/` — a aplicação vulnerável (comentada em cada falha)
- `.github/workflows/security.yml` — a pipeline SAST + DAST
- `SECURITY.md` — a história: vulnerável → detetado → remediado → verificado

## Correr localmente

```bash
cd app
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python app.py          # http://127.0.0.1:5000
```

Testes rápidos das vulnerabilidades (com a app a correr):

```bash
# Reflected XSS (A03)
curl 'http://127.0.0.1:5000/hello?name=<script>alert(1)</script>'

# SQL Injection (A03) — devolve todos os utilizadores
curl 'http://127.0.0.1:5000/user?id=1%20OR%201=1'

# Security headers em falta (A05) — com o headguard do autor deste repo:
# headguard http://127.0.0.1:5000 --insecure
```

## A pipeline

A cada Pull Request, a GitHub Actions:

1. **SAST** — Semgrep analisa o código (apanha a SQLi e o XSS na fonte)
2. **DAST** — sobe a app num container e corre o OWASP ZAP baseline contra ela
   (apanha os headers em falta e o XSS a correr)
3. Falha o build se houver findings **High** — e publica os relatórios como artifacts.

Ver `SECURITY.md` para a narrativa completa (com prints).
