import sqlite3
from flask import g, current_app


def get_db():
    """اتصال واحد بقاعدة البيانات لكل طلب (request)."""
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row            # للوصول للأعمدة بالاسم: row["name"]
        g.db.execute("PRAGMA foreign_keys = ON")  # تفعيل المفاتيح الأجنبية
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """ينشئ الجداول من schema.sql."""
    db = get_db()
    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf-8"))


def lookups():
    """فصائل الدم والمناطق، تُستخدم في القوائم المنسدلة بالنماذج."""
    db = get_db()
    blood_types = db.execute("SELECT * FROM blood_types ORDER BY id").fetchall()
    districts = db.execute("SELECT * FROM districts ORDER BY id").fetchall()
    return blood_types, districts
