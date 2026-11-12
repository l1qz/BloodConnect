import os
import secrets
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# APP_ENV=production  ->  strict mode (SECRET_KEY mandatory, Secure cookies, __Host- cookie prefix)
APP_ENV = os.environ.get("APP_ENV", "development").lower()
IS_PROD = APP_ENV == "production"


def _load_secret_key():
    """Never ship a default key: a known key lets anyone forge admin session cookies."""
    key = os.environ.get("SECRET_KEY", "")
    if key:
        if len(key) < 32:
            raise RuntimeError("SECRET_KEY must be at least 32 characters "
                               "(generate one: python -c \"import secrets; print(secrets.token_hex(32))\")")
        return key
    if IS_PROD:
        raise RuntimeError("SECRET_KEY environment variable is required when APP_ENV=production")
    # development / demo: random per-process key (sessions reset on restart, nothing guessable)
    return secrets.token_hex(32)


class Config:
    SECRET_KEY = _load_secret_key()
    DATABASE = os.path.join(BASE_DIR, "blood.db")

    # ---- donation eligibility rules (single place to change them) ----
    DONATION_COOLDOWN_DAYS = 90
    MIN_AGE = 18
    MAX_AGE = 60
    MIN_WEIGHT_KG = 50

    # ---- session / cookies ----
    SESSION_COOKIE_NAME = "__Host-session" if IS_PROD else "session"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = IS_PROD            # requires HTTPS in production
    SESSION_COOKIE_PATH = "/"
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)   # absolute lifetime
    SESSION_IDLE_TIMEOUT = 30 * 60                    # seconds of inactivity
    MAX_CONTENT_LENGTH = 64 * 1024                    # reject oversized bodies (413)

    # ---- security switches (tests may turn them off; never do that in production) ----
    CSRF_ENABLED = True
    RATELIMIT_ENABLED = True
    LOGIN_MAX_FAILURES = 5                            # per phone number
    LOGIN_MAX_FAILURES_PER_IP = 25
    LOGIN_WINDOW_SECONDS = 15 * 60
    TRUST_PROXY = int(os.environ.get("TRUST_PROXY", "0"))   # number of reverse proxies in front
    CSP_STRICT_ENFORCE = False    # True after Tailwind is compiled locally (see SECURITY_AUDIT.md)

    # ---- input policy ----
    MIN_PASSWORD_LENGTH = 8
    MAX_UNITS_PER_REQUEST = 20
    CARD_TOKEN_MAX_AGE_DAYS = 365

    # ---- retention policy (flask purge-data) ----
    NOTIFICATION_RETENTION_DAYS = 90
    AUDIT_RETENTION_DAYS = 365
    CLOSED_REQUEST_RETENTION_DAYS = 730
