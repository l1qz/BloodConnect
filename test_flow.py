"""اختبار كامل للمسار: متبرع يقبل -> مستشفى يؤكد -> مدير يوافق. التشغيل: python test_flow.py"""
import os
import tempfile

from app import create_app
from db import init_db, get_db
from seed import populate

tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
tmp.close()
app = create_app({"DATABASE": tmp.name, "TESTING": True, "CSRF_ENABLED": False, "RATELIMIT_ENABLED": False})

with app.app_context():
    init_db()
    populate()


def login(phone, password):
    c = app.test_client()
    r = c.post("/login", data={"phone": phone, "password": password})
    assert r.status_code == 302, f"login failed for {phone}"
    return c


def text(resp):
    return resp.data.decode("utf-8")


# 1) المتبرع أحمد (O-) يرى الطلب الحرج
ahmed = login("07702000001", "donor123")
page = text(ahmed.get("/donor/dashboard"))
assert "مستشفى كركوك العام" in page and "أستطيع التبرع" in page
print("1. donor sees the matching request")

# 2) حسن (آخر تبرع قبل 30 يومًا) ورنا (وزن 48) وكرار (غير متاح) لا يُطابَقون
with app.app_context():
    db = get_db()
    names = [r[0] for r in db.execute(
        "SELECT u.full_name FROM request_matches m JOIN donors d ON d.id=m.donor_id "
        "JOIN users u ON u.id=d.user_id WHERE m.request_id=1")]
    for excluded in ("حسن جاسم", "رنا سامي", "كرار عباس", "عمر خالد"):
        assert excluded not in names, excluded
    assert "أحمد حسن" in names and "سارة علي" in names
print("2. cooldown / weight / availability / blood-type rules work")

# 3) أحمد يقبل عبر AJAX
r = ahmed.post("/donor/matches/1/respond", data={"action": "accept"})
assert r.status_code == 200 and r.get_json()["status"] == "accepted", r.data
r = ahmed.post("/donor/matches/1/respond", data={"action": "accept"})
assert r.status_code == 409          # لا يمكن الرد مرتين
print("3. accept works, double response blocked")

# 4) أحمد لا يستطيع الرد على مطابقة غيره ولا فتح لوحة المستشفى
assert ahmed.post("/donor/matches/2/respond", data={"action": "accept"}).status_code == 404
assert ahmed.get("/hospital/dashboard").status_code == 403
print("4. ownership and role checks work")

# 5) المستشفى يرى الأرقام فقط للموافقين، ثم يؤكد التبرع
hosp = login("07701000001", "hosp123")
page = text(hosp.get("/hospital/requests/1"))
assert "07702000001" in page and "07702000002" in page      # أحمد وسارة وافقا
assert "07702000004" not in page                            # زينب لم ترد بعد: رقمها مخفي
hosp.post("/hospital/matches/1/confirm")
hosp.post("/hospital/matches/2/confirm")
with app.app_context():
    db = get_db()
    req = db.execute("SELECT units_received, status FROM blood_requests WHERE id=1").fetchone()
    assert req["units_received"] == 2 and req["status"] == "open"
    last = db.execute("SELECT last_donation_date FROM donors WHERE id=1").fetchone()[0]
    assert last is not None
print("5. phones hidden until accepted; confirm updates units and cooldown date")

# 6) المستشفى ينشر طلبًا جديدًا فيصل الإشعار للمتبرعين
r = hosp.post("/hospital/requests/new", data={"blood_type_id": 7, "units_needed": 1, "urgency": "urgent", "notes": ""})
assert r.status_code == 302
assert ahmed.get("/api/notifications").get_json()["count"] >= 1
print("6. new request creates notifications")

# 7) المستشفى المعلّق لا ينشر، والمدير يوافق
pending = login("07701000003", "hosp123")
assert pending.get("/hospital/requests/new").status_code == 302
admin = login("07700000000", "admin123")
assert "مستشفى الحويجة العام" in text(admin.get("/admin/dashboard"))
admin.post("/admin/hospitals/3/approve")
assert pending.get("/hospital/requests/new").status_code == 200
print("7. unapproved hospital blocked until admin approves")

# 8) تسجيل متبرع جديد + كلمة مرور خاطئة
c = app.test_client()
r = c.post("/register/donor", data={"full_name": "تجربة", "phone": "07999999999", "password": "secret123",
           "blood_type_id": 1, "district_id": 1, "gender": "male", "birth_date": "2000-01-01", "weight_kg": 70})
assert r.status_code == 302
assert "غير صحيحة" in text(c.post("/login", data={"phone": "07999999999", "password": "wrong"}))
print("8. registration and bad-login handling work")

# 9) Language selection is retained across login/logout and templates render in all three languages.
for language, expected in (("ar", "لوحة المتبرع"), ("ku", "داشبۆردی بەخشەر"), ("en", "Donor dashboard")):
    language_client = app.test_client()
    language_client.get(f"/language/{language}", headers={"Referer": "http://localhost/login"})
    language_client.post("/login", data={"phone": "07702000001", "password": "donor123"})
    with language_client.session_transaction() as sess:
        assert sess.get("language") == language
    dashboard = text(language_client.get("/donor/dashboard"))
    assert expected in dashboard
    assert language_client.get("/features/motivation").status_code == 200
    language_client.post("/logout")
    login_page = text(language_client.get("/login"))
    assert ("تسجيل الدخول" in login_page if language == "ar" else
            ("چوونەژوورەوە" in login_page if language == "ku" else "Sign in" in login_page))
print("9. Arabic, Sorani, and English remain selected across login/logout")

# 10) Requests created before a donor became eligible are backfilled when that donor opens the dashboard.
new_donor = c.post("/login", data={"phone": "07999999999", "password": "secret123"})
assert new_donor.status_code == 302
with app.app_context():
    db = get_db()
    with db:
        backfill_id = db.execute(
            "INSERT INTO blood_requests (hospital_id, blood_type_id, units_needed, urgency, notes) "
            "VALUES (1, 1, 1, 'urgent', 'BACKFILL-REGRESSION-TEST')"
        ).lastrowid
    donor_id = db.execute("SELECT id FROM donors WHERE user_id = (SELECT id FROM users WHERE phone = '07999999999')").fetchone()[0]
    assert db.execute(
        "SELECT COUNT(*) FROM request_matches WHERE request_id = ? AND donor_id = ?",
        (backfill_id, donor_id),
    ).fetchone()[0] == 0
backfill_page = text(c.get("/donor/dashboard"))
assert "BACKFILL-REGRESSION-TEST" in backfill_page
with app.app_context():
    db = get_db()
    assert db.execute(
        "SELECT COUNT(*) FROM request_matches WHERE request_id = ? AND donor_id = ?",
        (backfill_id, donor_id),
    ).fetchone()[0] == 1
print("10. existing open hospital requests appear for newly registered eligible donors")

# 11) Turning availability back on immediately matches eligible open requests without duplicates.
c.post("/donor/toggle-availability")  # turn off
with app.app_context():
    db = get_db()
    with db:
        toggle_request_id = db.execute(
            "INSERT INTO blood_requests (hospital_id, blood_type_id, units_needed, urgency, notes) "
            "VALUES (1, 1, 1, 'urgent', 'AVAILABILITY-REGRESSION-TEST')"
        ).lastrowid
    assert db.execute(
        "SELECT COUNT(*) FROM request_matches WHERE request_id = ? AND donor_id = ?",
        (toggle_request_id, donor_id),
    ).fetchone()[0] == 0
c.post("/donor/toggle-availability")  # turn on; the route matches immediately
with app.app_context():
    db = get_db()
    assert db.execute(
        "SELECT COUNT(*) FROM request_matches WHERE request_id = ? AND donor_id = ?",
        (toggle_request_id, donor_id),
    ).fetchone()[0] == 1
    notification_count = db.execute(
        "SELECT COUNT(*) FROM notifications WHERE user_id = (SELECT user_id FROM donors WHERE id = ?)",
        (donor_id,),
    ).fetchone()[0]
c.post("/donor/toggle-availability")  # off again; must not create another match or notification
with app.app_context():
    db = get_db()
    assert db.execute(
        "SELECT COUNT(*) FROM request_matches WHERE request_id = ? AND donor_id = ?",
        (toggle_request_id, donor_id),
    ).fetchone()[0] == 1
    assert db.execute(
        "SELECT COUNT(*) FROM notifications WHERE user_id = (SELECT user_id FROM donors WHERE id = ?)",
        (donor_id,),
    ).fetchone()[0] == notification_count
print("11. availability toggle matches immediately without duplicate matches/notifications")

os.unlink(tmp.name)
print("\nALL TESTS PASSED")
