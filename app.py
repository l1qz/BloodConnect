import click
import logging
from flask import Flask, redirect, render_template, request, session, url_for, jsonify
from werkzeug.security import generate_password_hash

import db
from config import Config
from security import init_security, safe_back, wants_json
from services.retention import erase_donor, purge_expired
from routes import auth, donor, hospital, admin, api, features
from translations import current_language, translate, district_label

# ترجمة القيم المخزنة بالإنجليزية إلى العربية للعرض في القوالب
ARABIC_STATUS_TRANSLATIONS = {
    "notified": "بانتظار ردّك", "accepted": "وافقت", "declined": "رفضت", "donated": "تم التبرع",
    "open": "مفتوح", "fulfilled": "مكتمل", "cancelled": "ملغى",
    "critical": "حرجة جدًا", "urgent": "عاجلة", "normal": "عادية",
    "male": "ذكر", "female": "أنثى",
}
KURDISH_STATUS_TRANSLATIONS = {
    "notified": "چاوەڕێی وەڵامەکەتە", "accepted": "قبووڵکراوە", "declined": "ڕەتکراوەتەوە", "donated": "بەخشراوە",
    "open": "کراوە", "fulfilled": "تەواوکراوە", "cancelled": "هەڵوەشێندراوەتەوە",
    "critical": "زۆر فۆری", "urgent": "فۆری", "normal": "ئاسایی",
    "male": "نێر", "female": "مێ",
}
ENGLISH_STATUS_TRANSLATIONS = {
    "notified": "Awaiting your response", "accepted": "Accepted", "declined": "Declined", "donated": "Donated",
    "open": "Open", "fulfilled": "Fulfilled", "cancelled": "Cancelled",
    "critical": "Critical", "urgent": "Urgent", "normal": "Normal",
    "male": "Male", "female": "Female",
}


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if test_config:   
        app.config.update(test_config)

    app.teardown_appcontext(db.close_db)          # يغلق الاتصال بعد كل طلب
    init_security(app)                            # CSRF, rate limits, headers, session checks
    @app.context_processor
    def language_context():
        language = current_language()
        return {
            "language": language,
            "translate": translate,
            "district_label": district_label,
            "T": KURDISH_STATUS_TRANSLATIONS if language == "ku" else (
                ENGLISH_STATUS_TRANSLATIONS if language == "en" else ARABIC_STATUS_TRANSLATIONS
            ),
        }
    app.jinja_env.globals["status_label"] = lambda status: (
        KURDISH_STATUS_TRANSLATIONS if current_language() == "ku" else (
            ENGLISH_STATUS_TRANSLATIONS if current_language() == "en" else ARABIC_STATUS_TRANSLATIONS
        )
    ).get(status, status)

    @app.route("/language/<language>")
    def set_language(language):
        if language not in ("ar", "ku", "en"):
            return redirect(url_for("home"))
        session["language"] = language
        return safe_back("home")

    for module in (auth, donor, hospital, admin, api, features):
        app.register_blueprint(module.bp)

    @app.route("/")
    def home():
        """يوجّه المستخدم إلى لوحته حسب دوره."""
        role = session.get("role")
        if role:
            return redirect(url_for(f"{role}.dashboard"))
        return render_template("landing.html")

    def _error(code, message):
        if wants_json():
            return jsonify(error=message), code
        return render_template("error.html", code=code, message=message), code

    @app.errorhandler(400)
    def bad_request(e):
        return _error(400, translate("Invalid request. Please reload the page and try again."))

    @app.errorhandler(403)
    def forbidden(e):
        return _error(403, translate("You are not allowed to open this page"))

    @app.errorhandler(404)
    def not_found(e):
        return _error(404, translate("Page not found"))

    @app.errorhandler(405)
    def method_not_allowed(e):
        return _error(405, translate("Invalid request. Please reload the page and try again."))

    @app.errorhandler(413)
    def too_large(e):
        return _error(413, translate("Invalid request. Please reload the page and try again."))

    @app.errorhandler(500)
    def server_error(e):
        # details go to the server log only; the user never sees a stack trace
        return _error(500, translate("Something went wrong. Please try again."))

    # ---- أوامر سطر الأوامر ----
    @app.cli.command("init-db")
    def init_db_command():
        db.init_db()
        click.echo("Database initialized.")

    @app.cli.command("create-admin")
    @click.argument("phone")
    @click.argument("password")
    def create_admin(phone, password):
        conn = db.get_db()
        with conn:
            conn.execute(
                "INSERT INTO users (full_name, phone, password_hash, role) "
                "VALUES (?, ?, ?, 'admin')",
                ("Admin", phone, generate_password_hash(password)),
            )
        click.echo("Admin created.")

    @app.cli.command("purge-data")
    def purge_data_command():
        """Retention job: delete expired notifications, audit rows and old closed requests."""
        conn = db.get_db()
        with conn:
            counts = purge_expired(conn, app.config)
        click.echo(f"Purged: {counts}")

    @app.cli.command("erase-user")
    @click.argument("phone")
    def erase_user_command(phone):
        """Right-to-erasure on request of the data subject (verify identity first!)."""
        conn = db.get_db()
        row = conn.execute("SELECT id FROM users WHERE phone = ? AND role = 'donor'", (phone,)).fetchone()
        if row is None:
            raise click.ClickException("No donor with that phone number")
        with conn:
            click.echo(f"Result: {erase_donor(conn, row['id'])}")

    @app.cli.command("generate-keys")
    def generate_keys_command():
        """Print fresh secrets for the environment (SECRET_KEY, field-encryption keys)."""
        import secrets
        from crypto import generate_keys
        click.echo(f"SECRET_KEY={secrets.token_hex(32)}")
        for name, value in generate_keys().items():
            click.echo(f"{name}={value}")

    if not app.debug and not app.testing:
        logging.getLogger("werkzeug").setLevel(logging.WARNING)   # no per-request URL logging

    return app


app = create_app()
