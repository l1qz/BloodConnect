"""
بيانات تجريبية للعرض أمام الدكاترة.
التشغيل:  python seed.py     (يحذف blood.db القديمة وينشئ قاعدة جديدة ممتلئة)
"""
import os
import sys
from datetime import date, timedelta

from werkzeug.security import generate_password_hash

from db import get_db
from services.matching import create_matches
from services.notifications import notify


if os.environ.get("APP_ENV", "").lower() == "production":
    sys.exit("Refusing to run seed.py with APP_ENV=production: it wipes the database "
             "and creates accounts with well-known demo passwords.")


def days_ago(n):
    return (date.today() - timedelta(days=n)).isoformat()


def birth_for_age(age):
    return (date.today() - timedelta(days=int(age * 365.25) + 30)).isoformat()


def add_user(db, name, phone, password, role):
    cur = db.execute(
        "INSERT INTO users (full_name, phone, password_hash, role) VALUES (?, ?, ?, ?)",
        (name, phone, generate_password_hash(password), role),
    )
    return cur.lastrowid


# فصائل الدم: A+=1 A-=2 B+=3 B-=4 AB+=5 AB-=6 O+=7 O-=8
# (الاسم، الفصيلة، المنطقة، الجنس، العمر، الوزن، آخر تبرع منذ كم يوم، متاح؟)
DONORS = [
    ("أحمد حسن",     8, 1, "male",   28, 78, None, 1),   # O-  : حساب العرض الرئيسي
    ("سارة علي",     7, 1, "female", 25, 62, None, 1),   # O+
    ("محمد كريم",    1, 2, "male",   31, 85, 200,  1),   # A+  : تبرع قبل 200 يوم
    ("زينب حسين",    2, 1, "female", 35, 64, None, 1),   # A-
    ("عمر خالد",     3, 3, "male",   22, 70, None, 1),   # B+
    ("ليلى أحمد",    4, 4, "female", 29, 58, 150,  1),   # B-
    ("يوسف طه",      5, 1, "male",   40, 90, None, 1),   # AB+
    ("نور الهدى",    7, 5, "female", 27, 60, None, 1),   # O+
    ("حسن جاسم",     8, 2, "male",   33, 82, 30,   1),   # O- : تبرع قبل 30 يومًا (لن يُطابَق)
    ("رنا سامي",     1, 1, "female", 24, 48, None, 1),   # A+ : وزنها أقل من 50 (لن تُطابَق)
    ("كرار عباس",    3, 1, "male",   45, 88, None, 0),   # B+ : غير متاح (لن يُطابَق)
    ("مصطفى نوري",   7, 1, "male",   19, 72, None, 1),   # O+
    ("هبة محمود",    1, 6, "female", 30, 66, None, 1),   # A+
    ("علي صباح",     6, 1, "male",   52, 80, None, 1),   # AB-
]


def populate(db=None):
    db = db or get_db()
    with db:
        # ---- المدير ----
        add_user(db, "مدير النظام", "07700000000", "admin123", "admin")

        # ---- المستشفيات ----
        hosp = {}
        for key, name, phone, district, approved in [
            ("general", "مستشفى كركوك العام",     "07701000001", 1, 1),
            ("azadi",   "مستشفى آزادي التعليمي", "07701000002", 2, 1),
            ("hawija",  "مستشفى الحويجة العام",  "07701000003", 6, 0),   # بانتظار الموافقة
        ]:
            uid = add_user(db, name, phone, "hosp123", "hospital")
            cur = db.execute(
                "INSERT INTO hospitals (user_id, name, district_id, address, phone, is_approved) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (uid, name, district, "كركوك", phone, approved),
            )
            hosp[key] = {"id": cur.lastrowid, "user_id": uid}

        # ---- المتبرعون ----
        donor_ids = []
        for i, (name, bt, dist, gender, age, kg, last, avail) in enumerate(DONORS, start=1):
            uid = add_user(db, name, f"0770200{i:04d}", "donor123", "donor")
            cur = db.execute(
                "INSERT INTO donors (user_id, blood_type_id, district_id, gender, birth_date, "
                "weight_kg, last_donation_date, is_available) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (uid, bt, dist, gender, birth_for_age(age), kg,
                 days_ago(last) if last else None, avail),
            )
            donor_ids.append(cur.lastrowid)
            if last:   # سجل تبرع قديم يظهر في "سجل تبرعاتك"
                db.execute(
                    "INSERT INTO donations (donor_id, hospital_id, request_id, donated_at) VALUES (?, ?, NULL, ?)",
                    (cur.lastrowid, hosp["general"]["id"], days_ago(last) + " 10:00:00"),
                )

        # ---- طلبات مفتوحة (يطابقها النظام تلقائيًا) ----
        r1 = db.execute(
            "INSERT INTO blood_requests (hospital_id, blood_type_id, units_needed, urgency, notes) "
            "VALUES (?, 1, 3, 'critical', 'عملية جراحية عاجلة في قسم الطوارئ')",
            (hosp["general"]["id"],),
        ).lastrowid                       # مريض A+
        create_matches(db, r1)

        r2 = db.execute(
            "INSERT INTO blood_requests (hospital_id, blood_type_id, units_needed, urgency, notes) "
            "VALUES (?, 3, 2, 'normal', 'مريض غسيل كلى')",
            (hosp["azadi"]["id"],),
        ).lastrowid                       # مريض B+
        create_matches(db, r2)

        # ---- طلب قديم مكتمل (يُنشأ أخيرًا ليبقى رقما الطلبين المفتوحين 1 و 2) ----
        db.execute(
            "INSERT INTO blood_requests (hospital_id, blood_type_id, units_needed, units_received, "
            "urgency, status, created_at) VALUES (?, 1, 2, 2, 'urgent', 'fulfilled', ?)",
            (hosp["general"]["id"], days_ago(200) + " 09:00:00"),
        )

        # ---- سارة (O+) وافقت مسبقًا على الطلب الحرج: المستشفى يرى رقمها ويؤكد التبرع ----
        db.execute(
            "UPDATE request_matches SET status = 'accepted', responded_at = CURRENT_TIMESTAMP "
            "WHERE request_id = ? AND donor_id = ?", (r1, donor_ids[1]),
        )
        notify(db, hosp["general"]["user_id"], "متبرع جديد وافق على طلب فصيلة A+")


if __name__ == "__main__":
    from app import create_app
    from db import init_db

    app = create_app()
    path = app.config["DATABASE"]
    if os.path.exists(path):
        os.remove(path)
    with app.app_context():
        init_db()
        populate()
    print("Demo data created.\n")
    print("Admin     07700000000 / admin123")
    print("Hospital  07701000001 / hosp123   (Kirkuk General, approved)")
    print("Hospital  07701000002 / hosp123   (Azadi, approved)")
    print("Hospital  07701000003 / hosp123   (Hawija, PENDING approval)")
    print("Donor     07702000001 / donor123  (Ahmed O-, has a pending request)")
    print("Donor     07702000002 / donor123  (Sara O+, already accepted)")
