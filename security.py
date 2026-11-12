"""
Security layer: CSRF protection, rate limiting, security headers, session validation,
audit log, and safe redirects. Registered once from app.create_app().
"""
import hmac
import secrets
import threading
import time
from collections import defaultdict, deque
from functools import wraps
from urllib.parse import urlparse

from flask import (abort, current_app, g, jsonify, redirect, render_template,
                   request, session, url_for)
from werkzeug.middleware.proxy_fix import ProxyFix

from db import get_db

CSRF_KEY = "_csrf"
SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}


# --------------------------------------------------------------------------- CSRF
def csrf_token():
    token = session.get(CSRF_KEY)
    if not token:
        token = secrets.token_urlsafe(32)
        session[CSRF_KEY] = token
    return token


def _check_csrf():
    if not current_app.config["CSRF_ENABLED"] or request.method in SAFE_METHODS:
        return
    sent = request.headers.get("X-CSRFToken") or request.form.get("csrf_token", "")
    expected = session.get(CSRF_KEY, "")
    if not expected or not sent or not hmac.compare_digest(str(sent), expected):
        abort(400)


# ----------------------------------------------------------------- rate limiting
class SlidingWindowLimiter:
    """In-memory limiter (per process). For several workers/servers use Redis (Flask-Limiter)."""

    def __init__(self, max_keys=50_000):
        self._hits = defaultdict(deque)
        self._lock = threading.Lock()
        self._max_keys = max_keys

    def _prune(self, key, window, now):
        q = self._hits[key]
        while q and q[0] <= now - window:
            q.popleft()
        return q

    def count(self, key, window):
        with self._lock:
            return len(self._prune(key, window, time.monotonic()))

    def add(self, key):
        with self._lock:
            if len(self._hits) > self._max_keys:
                self._hits.clear()                      # crude memory bound
            self._hits[key].append(time.monotonic())

    def retry_after(self, key, window):
        with self._lock:
            q = self._prune(key, window, time.monotonic())
            return max(1, int(window - (time.monotonic() - q[0]))) if q else 0

    def clear(self, key):
        with self._lock:
            self._hits.pop(key, None)

    def reset_all(self):
        with self._lock:
            self._hits.clear()


limiter = SlidingWindowLimiter()


def client_ip():
    return request.remote_addr or "unknown"


def wants_json():
    return (request.is_json
            or request.path.startswith(("/api/", "/features/chatbot"))
            or "application/json" in request.headers.get("Accept", ""))


def too_many(retry_after=60):
    from translations import translate
    message = translate("Too many attempts. Please try again later.")
    if wants_json():
        resp = jsonify(error=message)
    else:
        resp = current_app.make_response((render_template("error.html", code=429, message=message), 429))
    resp.status_code = 429
    resp.headers["Retry-After"] = str(retry_after)
    return resp


def rate_limit(scope, limit, window, per="ip", methods=None):
    """Decorator: at most `limit` calls per `window` seconds per IP (or per logged-in user).
    `methods` restricts counting to e.g. ("POST",) so that just opening a form is free."""
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if not current_app.config["RATELIMIT_ENABLED"] or (methods and request.method not in methods):
                return view(*args, **kwargs)
            ident = session.get("user_id") if per == "user" and session.get("user_id") else client_ip()
            key = f"{scope}:{ident}"
            if limiter.count(key, window) >= limit:
                return too_many(limiter.retry_after(key, window))
            limiter.add(key)
            return view(*args, **kwargs)
        return wrapped
    return decorator


# ---------------------------------------------------------------------- redirects
def safe_back(default_endpoint="home", **values):
    """Redirect to the Referer only if it is on our own host (no open redirect)."""
    target = request.referrer
    if target:
        parsed = urlparse(target)
        if parsed.netloc == request.host and parsed.scheme in ("http", "https"):
            return redirect(parsed.path + (f"?{parsed.query}" if parsed.query else ""))
    return redirect(url_for(default_endpoint, **values))


# ------------------------------------------------------------------- audit log
_audit_ready = set()


def ensure_security_tables(db):
    path = current_app.config["DATABASE"]
    if path in _audit_ready:
        return
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS audit_log (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER,
            role        TEXT,
            action      TEXT NOT NULL,
            target_type TEXT,
            target_id   INTEGER,
            ip          TEXT,
            created_at  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_audit_created ON audit_log(created_at);
        """
    )
    _audit_ready.add(path)


def audit(db, action, target_type=None, target_id=None, user_id=None):
    """Append-only trail of sensitive actions. Stores ids only, never names/phones/passwords.
    The caller owns the transaction (call inside `with db:`)."""
    ensure_security_tables(db)
    db.execute(
        "INSERT INTO audit_log (user_id, role, action, target_type, target_id, ip) VALUES (?,?,?,?,?,?)",
        (user_id if user_id is not None else session.get("user_id"),
         session.get("role"), action, target_type, target_id, client_ip()),
    )


# ------------------------------------------------------------------ registration
def init_security(app):
    if app.config["TRUST_PROXY"] > 0:
        n = app.config["TRUST_PROXY"]
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=n, x_proto=n, x_host=n)

    @app.context_processor
    def security_context():
        return {"csrf_token": csrf_token,
                "csp_nonce": lambda: g.get("csp_nonce", "")}

    @app.before_request
    def guard():
        if request.endpoint == "static":
            return None
        g.csp_nonce = secrets.token_urlsafe(16)
        _check_csrf()

        uid = session.get("user_id")
        if not uid:
            return None
        now = int(time.time())
        idle = now - session.get("last_seen", now)
        row = get_db().execute(
            "SELECT is_active, role FROM users WHERE id = ?", (uid,)).fetchone()
        if (idle > app.config["SESSION_IDLE_TIMEOUT"] or row is None
                or not row["is_active"] or row["role"] != session.get("role")):
            language = session.get("language", "ar")
            session.clear()
            session["language"] = language
            if wants_json():
                return jsonify(error="unauthenticated"), 401
            return redirect(url_for("auth.login"))
        if request.endpoint != "api.notifications":      # background polling is not "activity"
            session["last_seen"] = now
        return None

    @app.after_request
    def headers(resp):
        h = resp.headers
        h.setdefault("X-Content-Type-Options", "nosniff")
        h.setdefault("X-Frame-Options", "DENY")
        h.setdefault("Referrer-Policy", "same-origin")
        h.setdefault("Permissions-Policy",
                     "camera=(), microphone=(), geolocation=(), payment=(), usb=()")
        h.setdefault("Cross-Origin-Opener-Policy", "same-origin")
        h.setdefault("Cross-Origin-Resource-Policy", "same-origin")

        base = "frame-ancestors 'none'; base-uri 'self'; form-action 'self'; object-src 'none'"
        nonce = g.get("csp_nonce", "")
        strict = (f"default-src 'self'; script-src 'self' 'nonce-{nonce}' https://cdn.tailwindcss.com; "
                  "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
                  "font-src https://fonts.gstatic.com; img-src 'self' data:; connect-src 'self'; " + base)
        if app.config["CSP_STRICT_ENFORCE"]:
            h["Content-Security-Policy"] = strict
        else:
            h["Content-Security-Policy"] = base
            h["Content-Security-Policy-Report-Only"] = strict    # visible in browser console

        if request.is_secure or app.config.get("SESSION_COOKIE_SECURE"):
            h.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
        if request.endpoint != "static" and (session.get("user_id") or request.endpoint == "features.verify_card"):
            h["Cache-Control"] = "no-store"
            h["Pragma"] = "no-cache"
        return resp
