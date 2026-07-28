# The story: vulnerable → detected → remediated → verified

This file documents the journey of this repo — the part that actually matters.
(I'll fill in the screenshots and Action run links as they happen.)

## 1 · The vulnerable app (initial main)

`app/app.py` ships with three intentional vulnerabilities, each mapped to the
OWASP Top 10:

| # | Vulnerability | OWASP | Where | How to trigger it |
|---|---|---|---|---|
| 1 | Reflected XSS | A03 Injection | `/hello?name=` | `<script>alert(1)</script>` |
| 2 | SQL Injection | A03 Injection | `/user?id=` | `1 OR 1=1` |
| 3 | Missing security headers | A05 Security Misconfiguration | every response | headguard scores **F** |

Each one is commented in the code with what makes it dangerous and what the fix is.

## 2 · Detection — the pipeline goes red

*(screenshots of the failed run)*

- **SAST (Semgrep)** flagged the string-concatenated SQL query and the unescaped
  HTML output — before the app ever ran.
- **DAST (ZAP baseline)** flagged the reflected XSS and the missing headers at runtime.
- **headguard** graded the headers **F** and blocked the merge.

What I found interesting here: the two tools catch **different** things. SAST sees
the dangerous code patterns; DAST sees the actual behavior. Neither alone is enough —
that's exactly why AppSec pipelines run both.

## 3 · Remediation (commit: `fix: remediate OWASP findings`)

The three fixes I applied:

1. **XSS** → Jinja templates with autoescaping (`render_template_string` + `{{ name }}`).
2. **SQLi** → parameterized queries (`conn.execute("... WHERE id = ?", (uid,))`).
3. **Headers** → added `Content-Security-Policy`, `X-Frame-Options`,
   `X-Content-Type-Options` and `Referrer-Policy` (HSTS belongs at the TLS layer).

## 4 · Verification — the pipeline goes green

*(screenshot of the passing run)*

- Semgrep: 0 findings
- ZAP: 0 high alerts
- headguard: **F → A**

## What this demonstrates

- **SAST catches bugs in code** before they ever run.
- **DAST catches bugs in behavior** that static analysis can't see (headers, runtime config).
- **The merge gate makes security a requirement** — vulnerable code literally cannot land.
- Remediation isn't "fixed and forgotten": the same pipeline that caught the bugs
  is the one that verifies the fix.
