"""Security regression tests. Run: python test_security.py   (security controls are ENABLED here)."""
import os
import re
import subprocess
import sys
import tempfile

from flask import Flask
from flask.sessions import SecureCookieSessionInterface

from app import create_app
from db import get_db, init_db
from security import limiter
from seed import populate
from services.features import ensure_feature_tables
from crypto import FieldCipher, generate_keys

tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
tmp.close()
app = create_app({"DATABASE": tmp.name, "TESTING": True, "PROPAGATE_EXCEPTIONS": False})
with app.app_context():
    init_db()
    populate()


def csrf_from(client, url="/login"):
    html = client.get(url).get_data(as_text=True)
    return re.search(r'name="csrf-token" content="([^"]+)"', html).group(1)


def login(phone, password):
    c = app.test_client()
    r = c.post("/login", data={"phone": phone, "password": password, "csrf_token": csrf_from(c)})
    assert r.status_code == 302, f"login failed for {phone}: {r.status_code}"
    return c


def sql(query, params=()):
    with app.app_context():
        db = get_db()
        cur = db.execute(query, params)
        db.commit()
        return cur.fetchall() if query.lstrip().upper().startswith("SELECT") else cur.rowcount


def fresh():
    limiter.reset_all()


# 1) security headers on every response -------------------------------------------------
fresh()
r = app.test_client().get("/login")
for header in ("X-Content-Type-Options", "X-Frame-Options", "Referrer-Policy",
               "Permissions-Policy", "Content-Security-Policy", "Content-Security-Policy-Report-Only"):
    assert r.headers.get(header), f"missing {header}"
assert "frame-ancestors 'none'" in r.headers["Content-Security-Policy"]
print("1. security headers present (nosniff, frame-ancestors none, CSP, referrer, permissions)")

# 2) CSRF -------------------------------------------------------------------------------
fresh()
admin = login("07700000000", "admin123")
assert admin.post("/admin/hospitals/3/approve").status_code == 400                      # no token
assert admin.post("/admin/hospitals/3/approve", data={"csrf_token": "forged"}).status_code == 400
assert sql("SELECT is_approved FROM hospitals WHERE id = 3")[0][0] == 0
ok = admin.post("/admin/hospitals/3/approve", data={"csrf_token": csrf_from(admin, "/admin/dashboard")})
assert ok.status_code == 302 and sql("SELECT is_approved FROM hospitals WHERE id = 3")[0][0] == 1
ahmed = login("07702000001", "donor123")
assert ahmed.post("/donor/toggle-availability", headers={"Accept": "application/json"}).status_code == 400
token = csrf_from(ahmed, "/donor/dashboard")
assert ahmed.post("/donor/toggle-availability", headers={"X-CSRFToken": token}).status_code == 200
print("2. CSRF: forms and AJAX rejected without a valid token, accepted with it")

# 3) cookie flags -----------------------------------------------------------------------
fresh()
c = app.test_client()
cookie = c.post("/login", data={"phone": "07702000001", "password": "donor123",
                                "csrf_token": csrf_from(c)}).headers.get("Set-Cookie", "")
assert "HttpOnly" in cookie and "SameSite=Lax" in cookie
print("3. session cookie is HttpOnly + SameSite=Lax (Secure/__Host- when APP_ENV=production)")

# 4) forged admin session with the OLD default key is rejected --------------------------
old = Flask("old")
old.secret_key = "dev-only-change-me"
forged = SecureCookieSessionInterface().get_signing_serializer(old).dumps(
    {"user_id": 1, "role": "admin", "name": "x"})
atk = app.test_client()
atk.set_cookie(app.config["SESSION_COOKIE_NAME"], forged)
assert atk.get("/admin/dashboard").status_code == 302
print("4. forged admin cookie (old default SECRET_KEY) no longer works")

# 5) brute force lock-out -----------------------------------------------------------------
fresh()
b = app.test_client()
t = csrf_from(b)
for _ in range(app.config["LOGIN_MAX_FAILURES"]):
    assert b.post("/login", data={"phone": "07702000003", "password": "bad", "csrf_token": t}).status_code == 200
r = b.post("/login", data={"phone": "07702000003", "password": "donor123", "csrf_token": t})
assert r.status_code == 429 and "Retry-After" in r.headers
print("5. login lock-out after repeated failures (even the right password is refused)")

# 6) deactivated user loses access immediately ------------------------------------------------
fresh()
d = login("07702000004", "donor123")
assert d.get("/donor/dashboard").status_code == 200
sql("UPDATE users SET is_active = 0 WHERE phone = '07702000004'")
assert d.get("/donor/dashboard").status_code == 302
print("6. deactivated account is cut off on the very next request")

# 7) donor card tokens: opaque, server-side, revocable, role-restricted -----------------
fresh()
donor = login("07702000001", "donor123")
donor.get("/features/card")
with app.app_context():
    ensure_feature_tables(get_db())
tok = sql("SELECT card_token FROM donor_cards")[0][0]
hosp = login("07701000001", "hosp123")
page = hosp.get("/features/verify", query_string={"token": tok}).get_data(as_text=True)
assert "07702000001" not in page and "O-" in page                    # donor found, phone not exposed
import hmac as _h, hashlib as _hl
sig = _h.new(b"dev-only-change-me", b"1:x", _hl.sha256).hexdigest()
bad = hosp.get("/features/verify", query_string={"token": f"1.x.{sig}"}).get_data(as_text=True)
assert "O-" not in bad                                                # forged token useless
assert login("07701000003", "hosp123").get("/features/verify", query_string={"token": tok}).status_code in (200, 403)
sql("UPDATE hospitals SET is_approved = 0 WHERE id = 3")
assert login("07701000003", "hosp123").get("/features/verify", query_string={"token": tok}).status_code == 403
assert donor.get("/features/verify", query_string={"token": tok}).status_code == 403
donor.post("/features/card/rotate", data={"csrf_token": csrf_from(donor, "/features/card")})
assert "O-" not in hosp.get("/features/verify", query_string={"token": tok}).get_data(as_text=True)
assert sql("SELECT COUNT(*) FROM audit_log WHERE action LIKE 'card_%'")[0][0] >= 3
print("7. card tokens: random + DB-checked, forged/old tokens fail, unapproved hospital/donor blocked, audited")

# 8) input validation -> clean errors, never a 500 --------------------------------------
fresh()
h = login("07701000001", "hosp123")
def new_req(**kw):
    data = {"blood_type_id": "1", "units_needed": "2", "urgency": "urgent", "notes": "",
            "csrf_token": csrf_from(h, "/hospital/requests/new")}
    data.update(kw)
    return h.post("/hospital/requests/new", data=data)
before = sql("SELECT COUNT(*) FROM blood_requests")[0][0]
for bad_kw in ({"urgency": "HACK"}, {"units_needed": "9999"}, {"units_needed": "-1"},
               {"blood_type_id": "999"}, {"notes": "x" * 5000}):
    assert new_req(**bad_kw).status_code == 200, bad_kw
assert sql("SELECT COUNT(*) FROM blood_requests")[0][0] == before
assert new_req().status_code == 302
anon = app.test_client()
assert anon.post("/features/chatbot/ask", data='"str"', content_type="application/json",
                 headers={"X-CSRFToken": csrf_from(anon, "/features/chatbot")}).status_code == 200
reg = app.test_client()
for payload in ({"full_name": "A" * 5000, "phone": "07911111111"}, {"full_name": "Ali", "phone": "1"},
                {"full_name": "<script>x</script>", "phone": "07911111111"},
                {"full_name": "Ali", "phone": "07911111111", "weight_kg": "inf"},
                {"full_name": "Ali", "phone": "07911111111", "birth_date": "2999-01-01"},
                {"full_name": "Ali", "phone": "07911111111", "password": "12345678"}):
    data = {"full_name": "Ali Test", "phone": "07911111111", "password": "goodpass1", "blood_type_id": "1",
            "district_id": "1", "gender": "male", "birth_date": "1995-05-05", "weight_kg": "70",
            "csrf_token": csrf_from(reg, "/register/donor")}
    data.update(payload)
    assert reg.post("/register/donor", data=data).status_code == 200, payload
assert sql("SELECT COUNT(*) FROM users WHERE phone = '07911111111'")[0][0] == 0
print("8. strict validation: bad urgency/units/blood type/names/phones/dates/passwords rejected, no 500s")

# 9) logout only via POST --------------------------------------------------------------------
fresh()
d = login("07702000005", "donor123")
assert d.get("/logout").status_code == 405
assert d.post("/logout", data={"csrf_token": csrf_from(d, "/donor/dashboard")}).status_code == 302
assert d.get("/donor/dashboard").status_code == 302
print("9. logout is POST + CSRF protected")

# 10) no open redirect ---------------------------------------------------------------------
r = app.test_client().get("/language/en", headers={"Referer": "https://evil.example/phish"})
assert "evil.example" not in r.headers["Location"]
print("10. no open redirect through the Referer header")

# 11) production start-up refuses weak/missing secrets -------------------------------------
def boot(env):
    e = {k: v for k, v in os.environ.items() if k not in ("SECRET_KEY", "APP_ENV")}
    e.update(env)
    return subprocess.run([sys.executable, "-c", "import config"], env=e, capture_output=True).returncode
assert boot({"APP_ENV": "production"}) != 0
assert boot({"APP_ENV": "production", "SECRET_KEY": "short"}) != 0
assert boot({"APP_ENV": "production", "SECRET_KEY": "k" * 40}) == 0
print("11. APP_ENV=production refuses to start without a strong SECRET_KEY")

# 12) erasure (hard delete vs anonymise) + retention job -------------------------------------
fresh()
def register(phone, name):
    c = app.test_client()
    data = {"full_name": name, "phone": phone, "password": "goodpass1", "blood_type_id": "1", "district_id": "1",
            "gender": "male", "birth_date": "1995-05-05", "weight_kg": "70", "csrf_token": csrf_from(c, "/register/donor")}
    assert c.post("/register/donor", data=data).status_code == 302
    return login(phone, "goodpass1")
c1 = register("07922222222", "Erase Me")
r = c1.post("/donor/delete-account", data={"password": "wrong", "csrf_token": csrf_from(c1, "/donor/dashboard")})
assert sql("SELECT COUNT(*) FROM users WHERE phone = '07922222222'")[0][0] == 1          # wrong password: nothing happens
c1.post("/donor/delete-account", data={"password": "goodpass1", "csrf_token": csrf_from(c1, "/donor/dashboard")})
assert sql("SELECT COUNT(*) FROM users WHERE phone = '07922222222'")[0][0] == 0
c2 = register("07933333333", "Has Donation")
did = sql("SELECT d.id FROM donors d JOIN users u ON u.id = d.user_id WHERE u.phone = '07933333333'")[0][0]
sql("INSERT INTO donations (donor_id, hospital_id) VALUES (?, 1)", (did,))
c2.post("/donor/delete-account", data={"password": "goodpass1", "csrf_token": csrf_from(c2, "/donor/dashboard")})
row = sql("SELECT full_name, phone, is_active FROM users WHERE id = (SELECT user_id FROM donors WHERE id = ?)", (did,))[0]
assert row[0] == "Deleted donor" and row[1].startswith("deleted-") and row[2] == 0
sql("INSERT INTO notifications (user_id, message, created_at) VALUES (1, 'old', '2000-01-01')")
out = app.test_cli_runner().invoke(args=["purge-data"])
assert "notifications" in out.output and sql("SELECT COUNT(*) FROM notifications WHERE message = 'old'")[0][0] == 0
print("12. account erasure (delete or anonymise) and retention purge work")

# 13) stored XSS is escaped on output -------------------------------------------------------
fresh()
sql("UPDATE hospitals SET name = '<img src=x onerror=alert(1)>', is_approved = 0 WHERE id = 3")
page = login("07700000000", "admin123").get("/admin/dashboard").get_data(as_text=True)
assert "<img src=x" not in page and "&lt;img" in page
print("13. injected HTML in stored data is escaped (Jinja autoescape verified)")

# 14) rate limit on the public chatbot ------------------------------------------------------
fresh()
a = app.test_client()
t = csrf_from(a, "/features/chatbot")
codes = [a.post("/features/chatbot/ask", json={"question": "age"}, headers={"X-CSRFToken": t}).status_code
         for _ in range(35)]
assert codes[:30] == [200] * 30 and 429 in codes[30:]
print("14. public chatbot endpoint is rate limited")

# 15) rewards cannot be double-spent --------------------------------------------------------
fresh()
with app.app_context():
    db = get_db()
    ensure_feature_tables(db)
    did = db.execute("SELECT d.id FROM donors d JOIN users u ON u.id = d.user_id WHERE u.phone = '07702000002'").fetchone()[0]
    db.execute("INSERT OR REPLACE INTO donor_points (donor_id, balance) VALUES (?, 100)", (did,))
    db.execute("INSERT OR IGNORE INTO rewards (id, name, description, points_cost) VALUES (1, 'A', 'a', 100)")
    db.commit()
s_ = login("07702000002", "donor123")
for _ in range(3):
    s_.post("/features/rewards", data={"reward_id": "1", "csrf_token": csrf_from(s_, "/features/rewards")})
assert sql("SELECT balance FROM donor_points WHERE donor_id = ?", (did,))[0][0] == 0
assert sql("SELECT COUNT(*) FROM reward_redemptions WHERE donor_id = ?", (did,))[0][0] == 1
print("15. reward redemption is atomic (balance never negative, no double spend)")

# 16) field-encryption helper ---------------------------------------------------------------
keys = generate_keys()
cipher = FieldCipher([keys["FIELD_ENCRYPTION_KEYS"]], keys["BLIND_INDEX_KEY"])
ct = cipher.encrypt("07701234567")
assert ct != "07701234567" and cipher.decrypt(ct) == "07701234567"
assert cipher.blind_index("07701234567") == cipher.blind_index(" 07701234567 ")
try:
    cipher.decrypt(ct[:-4] + "AAAA")
    raise SystemExit("tampering not detected")
except ValueError:
    pass
new_keys = generate_keys()["FIELD_ENCRYPTION_KEYS"]
rot = FieldCipher([new_keys, keys["FIELD_ENCRYPTION_KEYS"]], keys["BLIND_INDEX_KEY"])
assert rot.decrypt(rot.rotate(ct)) == "07701234567"
print("16. field encryption: round-trip, tamper detection, blind index, key rotation")

print("\nALL SECURITY TESTS PASSED")
