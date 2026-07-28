# Secure Pipeline Demo

I built this project to learn and demonstrate **DevSecOps in practice**: a small
Flask app with intentional vulnerabilities (OWASP Top 10), and a CI pipeline that
catches them automatically and blocks the merge until they're fixed.

The short version: **vulnerable code → pipeline catches it (red build) → I fix it
→ pipeline goes green.** The full story, with screenshots, is in [SECURITY.md](SECURITY.md).

## What's inside

- `app/` — a small Flask app with three intentional vulnerabilities, each one
  commented in the code with the OWASP category it maps to and how to fix it:
  - **Reflected XSS** (A03 Injection) at `/hello?name=`
  - **SQL Injection** (A03 Injection) at `/user?id=`
  - **Missing security headers** (A05 Security Misconfiguration) on every response
- `.github/workflows/security.yml` — the CI pipeline
- `SECURITY.md` — the full narrative (vulnerable → detected → remediated → verified)

## The pipeline

On every Pull Request, GitHub Actions runs three gates:

1. **SAST — Semgrep.** Static analysis of the code: finds the SQL injection and the
   XSS at the source, before anything even runs.
2. **DAST — OWASP ZAP baseline.** Boots the app in a container and attacks it like
   a real user would: finds the missing headers and the reflected XSS at runtime.
3. **Headers gate — [headguard](https://github.com/Rena24Pt/headguard).** My own
   open-source tool, requiring grade **A** on the security headers. (Yes, the
   vulnerable app scores an F — that's the point.)

If any gate fails, the build goes red and the merge is blocked. That's the whole
idea: **security as a merge requirement, not a manual afterthought.**

## Run it locally

```bash
cd app
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python app.py          # http://127.0.0.1:5000
```

Try the vulnerabilities yourself:

```bash
# Reflected XSS
curl 'http://127.0.0.1:5000/hello?name=<script>alert(1)</script>'

# SQL Injection — returns every user in the table
curl 'http://127.0.0.1:5000/user?id=1%20OR%201=1'
```

## Why I built this

Job descriptions in AppSec ask for "SAST, DAST, pipelines". I didn't want to just
list those words on my CV — I wanted to show them working. Everything here is
deliberately small so the security story stays readable: one app, three bugs,
three gates, one fix.
