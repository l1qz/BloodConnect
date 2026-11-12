# Security Audit — Kirkuk Emergency Blood Donor Matcher

**Scope:** full source of `blood_matcher_fixed` (Flask + SQLite + Tailwind/JS), uploaded three times; the three archives contain identical code.
**Method:** manual code review of every route, service, template and script, plus proof-of-concept attacks run against the original code, then fixes and regression tests.
**Result:** 2 critical, 4 high, 6 medium, 5 low findings. All are fixed in code except the items listed under *Residual risks*. `test_flow.py` (11 functional checks) and the new `test_security.py` (16 security checks) pass.

---

## 1. Findings

| ID | Severity | Finding | Evidence (original code) | Status |
|---|---|---|---|---|
| C1 | Critical | **Session forgery.** `SECRET_KEY` defaulted to the public string `dev-only-change-me`; the session cookie is only signed, so anyone can mint `{"role":"admin"}`. | Forged cookie → `GET /admin/dashboard` = **200** | Fixed: random per-process key in dev, mandatory 32+ char key in production (app refuses to start otherwise) |
| C2 | Critical | **Donor-card tokens were forgeable and never checked in the DB.** Token = HMAC with the (known) key; `parse_donor_token` only verified the signature. Any hospital login could read every donor (name, blood type, donation history). Tokens could not be revoked or expire. | Self-minted tokens returned **15 of 15** donors | Fixed: opaque 256-bit random tokens, looked up in the DB, 365-day expiry, rotate button, approved-hospital/admin only, phone no longer selected, every scan audited |
| H1 | High | **No CSRF protection** on any POST (approve hospital, confirm donation, redeem reward, accept/decline, toggle availability, logout). | Admin POST with foreign `Origin` → **302 (executed)** | Fixed: session-bound token on all forms and AJAX (`X-CSRFToken`), `SameSite=Lax` |
| H2 | High | **No brute-force protection**, 6-character passwords, no rate limits anywhere. | 60 wrong passwords, never throttled | Fixed: 5 failures/15 min per phone, 25/15 min per IP, rate limits on register/chatbot/verify/API, password ≥ 8 with letters + digits |
| H3 | High | **Stale authorization.** Role and identity were trusted from the cookie; deactivated users kept access. | Deactivated donor → dashboard **200** | Fixed: every request re-checks `is_active` and role in the DB; 30-min idle and 8-h absolute session limits |
| H4 | High | Any self-registered (unapproved) hospital could use `/features/verify`. | Code review | Fixed: approved hospitals and admins only |
| M1 | Medium | **No security headers:** clickjacking on approve/confirm buttons, no `nosniff`, tokens leaking through `Referer`, PII pages cacheable. | Header check: all missing | Fixed (see §5) |
| M2 | Medium | Cookie flags incomplete (no `SameSite`, no `Secure`, no `__Host-` prefix). | `Set-Cookie: …; HttpOnly; Path=/` | Fixed (Secure + `__Host-` when `APP_ENV=production`) |
| M3 | Medium | **Input validation gaps:** HTTP 500 on bad `urgency` and on a JSON-string chatbot body; 100 KB names, `weight=inf`, phone `"1"`, free-form dates accepted. | All five reproduced | Fixed: central `validators.py`, allow-lists, length caps, 64 KB body limit |
| M4 | Medium | Logout via GET (forced logout through an image tag); Referer-based redirects in `/language/<x>` and `confirm`. | Code review | Fixed: POST + CSRF; same-host redirect check |
| M5 | Medium | Reward redemption checked then deducted in separate statements (race → 500 / inconsistent state). | Code review | Fixed: single atomic `UPDATE … WHERE balance >= cost` |
| M6 | Medium | README runs `flask run --debug` (interactive Werkzeug debugger = remote code execution if reachable). | README | Documented; never use `--debug` off localhost |
| L1 | Low | Account-enumeration by timing (unknown phone skipped the hash check). | Code review | Fixed with a dummy hash |
| L2 | Low | No audit trail of who viewed or changed sensitive data. | — | Added `audit_log` (ids only, no PII) |
| L3 | Low | No erasure or retention policy; donors could not delete their data. | — | Added erase/anonymise + `purge-data` job |
| L4 | Low | Shipped `blood.db` contained demo accounts with weak passwords; `seed.py` wipes the DB. | zip contents | DB removed from the package; `seed.py` refuses to run when `APP_ENV=production` |
| L5 | Low | `GET /donor/dashboard` writes to the DB (matching back-fill); the new per-request session check adds one indexed lookup per request. | Code review | Noted (design); see *Residual risks* |

### What was already done well
Parameterised SQL everywhere (no SQL injection found), Jinja autoescape and `textContent` in JS (no XSS sink found; verified by test), password hashing with Werkzeug, ownership checks in every hospital/donor route (no IDOR found), role decorator, phone numbers masked until a donor accepts, DB `CHECK`/foreign-key constraints, transactions, generic login error, `session.clear()` on login, whitelisted language values.

---

## 2. Pillar 1 — Data protection & privacy

### Where sensitive data lives
| Data | Table / column | At rest | Exposure |
|---|---|---|---|
| Name, phone | `users.full_name`, `users.phone` | **Plaintext** | Hospitals see the name of every *matched* donor; phone only after acceptance |
| Birth date, weight, gender, blood type, last donation | `donors.*` | **Plaintext** | Hospitals see blood type + district of matches |
| Donation history | `donations` | Plaintext | Donor, and verified card scans |
| IP addresses | `audit_log.ip` | Plaintext | Admin/DB only; 365-day retention |
| Passwords | `users.password_hash` | Salted hash (good) | — |

The application does not log passwords or phone numbers; Werkzeug request logging is lowered to WARNING outside debug mode (card-verification tokens travel in the URL, so keep debug/access logging off in production and restrict log access).

### In transit
The app itself cannot provide TLS. Terminate HTTPS at a reverse proxy and set `APP_ENV=production` (Secure + `__Host-` cookie, HSTS header) and `TRUST_PROXY=1`:

```nginx
server { listen 80; server_name blood.example.iq; return 301 https://$host$request_uri; }
server {
  listen 443 ssl http2;
  server_name blood.example.iq;
  ssl_protocols TLSv1.2 TLSv1.3;
  ssl_certificate     /etc/letsencrypt/live/blood.example.iq/fullchain.pem;
  ssl_certificate_key /etc/letsencrypt/live/blood.example.iq/privkey.pem;
  client_max_body_size 64k;
  location / {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-For $remote_addr;
    proxy_set_header X-Forwarded-Proto https;
    proxy_set_header X-Forwarded-Host $host;
  }
}
```
```bash
APP_ENV=production SECRET_KEY=... TRUST_PROXY=1 gunicorn -w 3 -b 127.0.0.1:8000 app:app
```
Make sure only your real domain reaches the app (nginx `server_name` plus a catch-all `return 444;` server, or Flask 3.1+ `TRUSTED_HOSTS`), because QR URLs are built from the request host.

### Encryption at rest — layered recommendation
1. **Now (no code):** full-disk encryption (LUKS/BitLocker) on the server, `chmod 600 blood.db`, database outside any web root, encrypted off-site backups.
2. **Production database:** PostgreSQL on an encrypted volume (or SQLite + SQLCipher) with a least-privilege application role.
3. **Field-level encryption for the most sensitive columns** (name, phone, birth date). `crypto.py` is ready (Fernet/AES + HMAC, `MultiFernet` for zero-downtime key rotation, HMAC *blind index* so login can still look up a phone number). It is **not wired in by default** because it changes the login query and every place a name/phone is shown. Integration pattern:

```python
cipher = FieldCipher.from_env()           # FIELD_ENCRYPTION_KEYS, BLIND_INDEX_KEY from the environment
# schema:  phone_enc TEXT NOT NULL, phone_idx TEXT NOT NULL UNIQUE
db.execute("INSERT INTO users (full_name_enc, phone_enc, phone_idx, ...) VALUES (?,?,?,...)",
           (cipher.encrypt(name), cipher.encrypt(phone), cipher.blind_index(phone), ...))
user = db.execute("SELECT * FROM users WHERE phone_idx = ?", (cipher.blind_index(phone),)).fetchone()
phone = cipher.decrypt(user["phone_enc"])           # only when the UI is allowed to show it
```
Generate keys with `flask --app app generate-keys`; keep them in a secrets manager, never in git. Rotate: add the new key first in `FIELD_ENCRYPTION_KEYS`, run `cipher.rotate()` over all rows, then drop the old key.

### Data minimisation
* Phone numbers are shown only after the donor accepts (already in place).
* Card verification returns name, blood type, last donation and history, **never the phone**.
* Birth dates of anonymised donors are reduced to the year; erased donors lose name, phone, e-mail, notifications, card and points.
* Recommended next step (not applied, so your demo script stays unchanged): show only initials until acceptance:
```sql
CASE WHEN m.status IN ('accepted','donated') THEN u.full_name
     ELSE substr(u.full_name, 1, 1) || '.' END AS display_name
```

### Retention & deletion (implemented)
| Data | Policy | Mechanism |
|---|---|---|
| Notifications | 90 days | `flask --app app purge-data` (run daily from cron/systemd timer) |
| Audit log | 365 days | same job |
| Closed requests without donations | 730 days | same job |
| Donor account | On request, immediately | Donor button "Delete my account" (password re-check), or `flask --app app erase-user <phone>`; hard delete if no donation records, otherwise anonymise (medical/accounting record kept without identity) |

Adjust the numbers in `config.py`. Check with your institution what legal retention periods apply to donation records.

---

## 3. Pillar 2 — OWASP Top 10 mapping

| OWASP 2021 | Result |
|---|---|
| A01 Broken access control | RBAC by decorator + per-row ownership filters (no IDOR). Added: approved-hospital check for card verification, live role/active re-check, audit trail |
| A02 Cryptographic failures | Known secret key removed; opaque random tokens; cookie `Secure`/`__Host-`; HSTS; field-encryption helper (opt-in) |
| A03 Injection | All SQL parameterised; the only non-parameterised fragments are fixed strings (table names in `retention.py`, a static `replace` in `matching.py`), never user input. Output escaped by Jinja; JS uses `textContent`; inline JS removed (CSP-ready) |
| A04 Insecure design | Rate limiting, lock-out, atomic reward spend, minimised exposure, erasure |
| A05 Misconfiguration | Security headers, no default secrets, debug guidance, body-size limit, generic error pages (no stack traces) |
| A06 Vulnerable components | `requirements.txt` ranges; run `pip-audit` in CI; Tailwind/Fonts still come from CDNs (see residual risks) |
| A07 Authentication failures | Lock-out, password policy, constant-time unknown-user path, new session on login, idle/absolute timeouts, POST logout |
| A08 Integrity failures | CSRF tokens; no unsigned data trusted; CDN script not pinned (residual) |
| A09 Logging & monitoring | New `audit_log` (login ok/failed, verify, confirm, approve, erase). Ship it to your log system and alert on spikes of `login_failed` |
| A10 SSRF | No server-side URL fetching in the app |

### RBAC matrix (enforced)
| Capability | Donor | Hospital (approved) | Hospital (pending) | Admin |
|---|---|---|---|---|
| Own dashboard / respond to own matches | ✔ | — | — | — |
| Create/cancel/confirm own requests | — | ✔ | ✖ (create) | — |
| See matched donors' phone | — | only after acceptance | ✖ | — |
| Verify donor card | ✖ | ✔ | ✖ | ✔ |
| Approve hospitals, manage rewards | ✖ | ✖ | ✖ | ✔ |

---

## 4. Pillar 3 — Input validation

All validators live in `validators.py` and raise `ValueError`; routes turn that into a form error, never a 500.

| Input | Rule |
|---|---|
| Phone | normalised (`+964…` → `0…`), must match `07` + 9 digits |
| Name | NFC-normalised, control characters stripped, 2–100 chars, no `<`, `>`, `"`, backtick, `{`, `}` or backslash |
| Password | 8–128 chars, at least one letter and one digit, must not contain the phone number |
| Blood type, district | must be an existing id from the lookup tables |
| Gender, urgency | fixed allow-lists |
| Birth date | valid ISO date between 1900-01-01 and today |
| Weight | finite number 20–300 kg |
| Units | integer 1–20 (`MAX_UNITS_PER_REQUEST`) |
| Notes / address / reward text | length caps (500 / 200 / 80+300) |
| Chatbot question | must be a string, cut to 300 characters |
| Request body | 64 KB maximum (HTTP 413) |

---

## 5. Pillar 4 — Hardening

**Headers (every response):** `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: same-origin`, `Permissions-Policy`, COOP/CORP `same-origin`, `Cache-Control: no-store` for logged-in pages and card verification, HSTS in production. CSP: `frame-ancestors 'none'; base-uri 'self'; form-action 'self'; object-src 'none'` is **enforced**; the strict script/style policy (with per-request nonces) is sent as `Content-Security-Policy-Report-Only` because the UI loads Tailwind and the font from CDNs. To enforce it fully: compile Tailwind locally (`npx tailwindcss -i in.css -o static/css/app.css --minify`), self-host the font, replace the CDN tags, then set `CSP_STRICT_ENFORCE = True`.

**Rate limiting:** login (per phone and per IP), registration, chatbot, card verification, notification polling, account deletion. The limiter is in-memory and per process: with several gunicorn workers use Redis-backed Flask-Limiter instead.

**Sessions:** HttpOnly, SameSite=Lax, Secure + `__Host-` prefix in production, 30-minute idle timeout (background polling does not count as activity), 8-hour absolute lifetime, fresh session on login, server-side re-validation per request.

**Deployment checklist**
- [ ] `APP_ENV=production`, 32+ char `SECRET_KEY` from `flask --app app generate-keys`
- [ ] HTTPS reverse proxy, `TRUST_PROXY=1`, only your domain accepted (see §2)
- [ ] No `--debug`, no `seed.py`, no demo accounts; create the admin with `flask --app app create-admin <phone> <strong-password>`
- [ ] `chmod 600 blood.db`, outside web root, encrypted backups tested by restoring
- [ ] Daily `purge-data` job; log shipping for `audit_log`
- [ ] `pip-audit` and dependency pinning in CI

---

## 6. Residual risks (not fixed in code) — in priority order
1. **Data at rest is still plaintext** unless you adopt disk/DB encryption or wire `crypto.py` (see §2).
2. **No second factor** for admin and hospital accounts and **no password-reset flow**. Add TOTP (e.g. `pyotp`) for admin/hospital, and phone verification at registration.
3. **Hospitals see names of matched donors before acceptance** (privacy-by-design improvement: initials only).
4. **Third-party CDN scripts** (Tailwind, Google Fonts) cannot be pinned with SRI; strict CSP is report-only until they are self-hosted.
5. **No explicit consent record** at registration. Add a checkbox and store `consent_at` with the policy version.
6. **Matching back-fill runs on `GET /donor/dashboard`** (writes on a read; costly with many open requests). Move it to a background task or to the events that change eligibility.
7. SQLite is fine for a demo; for real traffic and concurrent writers move to PostgreSQL.
8. No CAPTCHA on registration; the in-memory limiter resets on restart.
9. The new Kurdish and Arabic strings were written by me; have a native speaker review them.
10. Legal compliance (Iraqi data-protection rules, health-data regulations, hospital policies) needs review by your institution; this audit is technical, not legal advice.

---

## 7. Verify it yourself
```bash
pip install -r requirements.txt
python test_flow.py        # 11 functional checks (CSRF/rate limits off by design)
python test_security.py    # 16 security checks (all controls ON)
python seed.py && flask --app app run
```
`test_security.py` covers: headers, CSRF (forms + AJAX), cookie flags, forged old-key session, lock-out, deactivated user, card tokens (forged/rotated/unapproved/role), validation without 500s, POST-only logout, open redirect, production start-up checks, erasure + retention, stored-XSS escaping, chatbot rate limit, reward double-spend, field encryption.

## 8. Files changed
New: `security.py`, `validators.py`, `crypto.py`, `services/retention.py`, `test_security.py`, `SECURITY_AUDIT.md`.
Modified: `config.py`, `app.py`, `routes/{auth,donor,hospital,admin,api,features}.py`, `services/features.py`, `translations.py`, `seed.py`, `static/js/app.js`, all templates containing forms plus `base.html`, `features/card.html`, `donor/dashboard.html`, `features/chatbot.html`, `hospital/request_detail.html`, `requirements.txt`, `README.md`, `test_flow.py` (CSRF/rate-limit flags off, 8+ character test password, POST logout).
Removed from the package: `blood.db` (run `python seed.py`).
