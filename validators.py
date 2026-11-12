"""Strict server-side input validation. Every function raises ValueError on bad input."""
import math
import re
import unicodedata
from datetime import date

_CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_PHONE = re.compile(r"^07\d{9}$")                       # Iraqi mobile: 07XXXXXXXXX
_FORBIDDEN_IN_NAMES = set("<>\"`{}\\")


def clean_text(value, max_len, *, min_len=0, multiline=False):
    if value is None:
        value = ""
    if not isinstance(value, str):
        raise ValueError("text expected")
    value = unicodedata.normalize("NFC", value)
    value = _CONTROL.sub("", value)
    if not multiline:
        value = re.sub(r"\s+", " ", value)
    value = value.strip()
    if not (min_len <= len(value) <= max_len):
        raise ValueError("length")
    return value


def clean_name(value, *, max_len=100):
    value = clean_text(value, max_len, min_len=2)
    if any(ch in _FORBIDDEN_IN_NAMES for ch in value):
        raise ValueError("characters")
    return value


def clean_phone(value):
    value = clean_text(value, 20)
    value = re.sub(r"[ \-()]", "", value)
    if value.startswith("+964"):
        value = "0" + value[4:]
    elif value.startswith("00964"):
        value = "0" + value[5:]
    if not _PHONE.match(value):
        raise ValueError("phone")
    return value


def clean_password(value, *, min_len=8, phone=None):
    if not isinstance(value, str) or not (min_len <= len(value) <= 128):
        raise ValueError("length")
    if not (re.search(r"[^\W\d_]", value) and re.search(r"\d", value)):
        raise ValueError("letters and digits required")
    if phone and phone in value:
        raise ValueError("contains phone")
    return value


def parse_choice(value, allowed):
    """value must be one of `allowed` (ids or strings); returns the matching allowed item."""
    for item in allowed:
        if str(item) == str(value):
            return item
    raise ValueError("choice")


def parse_int(value, lo, hi):
    try:
        number = int(str(value).strip())
    except (TypeError, ValueError):
        raise ValueError("int")
    if not lo <= number <= hi:
        raise ValueError("range")
    return number


def parse_birth_date(value):
    try:
        parsed = date.fromisoformat(str(value).strip())
    except ValueError:
        raise ValueError("date")
    if not (date(1900, 1, 1) <= parsed <= date.today()):
        raise ValueError("date range")
    return parsed.isoformat()


def parse_weight(value, lo=20.0, hi=300.0):
    try:
        number = float(str(value).strip())
    except (TypeError, ValueError):
        raise ValueError("weight")
    if not math.isfinite(number) or not lo <= number <= hi:
        raise ValueError("weight range")
    return number
