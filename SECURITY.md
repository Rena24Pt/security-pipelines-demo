# A história do projeto (vulnerável → detetado → remediado → verificado)

> Este ficheiro documenta a narrativa DevSecOps do repo — preencher com prints
> e links para os runs da Actions à medida que acontecem.

## 1 · Estado vulnerável (main inicial)

A app (`app/app.py`) tem três vulnerabilidades deliberadas, mapeadas ao OWASP Top 10:

| # | Vulnerabilidade | OWASP | Onde | Como explorar |
|---|---|---|---|---|
| 1 | Reflected XSS | A03 Injection | `/hello?name=` | `<script>alert(1)</script>` |
| 2 | SQL Injection | A03 Injection | `/user?id=` | `1 OR 1=1` |
| 3 | Security headers ausentes | A05 Security Misconfiguration | todas as respostas | `headguard` → grade F |

## 2 · Deteção (pipeline a vermelho)

- **SAST (Semgrep):** *(print do run + findings: concatenação SQL, HTML sem escape)*
- **DAST (ZAP baseline):** *(print do run + alerts: XSS reflected, headers em falta)*

## 3 · Remediação (commit X)

As correções aplicadas:

1. **XSS:** templates Jinja com autoescape (`render_template_string` + `{{ name }}`).
2. **SQLi:** queries parametrizadas (`conn.execute("... WHERE id = ?", (uid,))`).
3. **Headers:** `Content-Security-Policy`, `X-Frame-Options`, `X-Content-Type-Options`,
   `Referrer-Policy` — e HSTS quando atrás de TLS.

## 4 · Verificação (pipeline a verde)

- *(print do run verde: 0 findings high)*
- headguard: grade F → grade A *(print)*

## O que isto demonstra

- SAST apanha vulnerabilidades **no código** (antes de correr).
- DAST apanha vulnerabilidades **a correr** (o que o SAST não vê: headers, comportamento).
- O quality gate **falha o merge** enquanto houver findings High — segurança como requisito do pipeline, não como passo manual posterior.
