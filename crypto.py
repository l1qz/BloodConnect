"""
Field-level encryption helpers (opt-in) for PII / medical columns.

  * Fernet (AES-128-CBC + HMAC-SHA256) with MultiFernet => key rotation without downtime.
  * blind_index(): deterministic HMAC so you can still look a row up by phone number
    (login) while the phone itself is stored encrypted.

Keys come from the environment, never from source control:
    FIELD_ENCRYPTION_KEYS = key_new,key_old      (comma separated, newest first)
    BLIND_INDEX_KEY       = 32+ random chars     (different from SECRET_KEY)
Generate:  flask --app app generate-keys
"""
import hashlib
import hmac
import os

from cryptography.fernet import Fernet, InvalidToken, MultiFernet


class FieldCipher:
    def __init__(self, encryption_keys, index_key):
        keys = [k.strip() for k in encryption_keys if k and k.strip()]
        if not keys:
            raise RuntimeError("FIELD_ENCRYPTION_KEYS is empty")
        if not index_key or len(index_key) < 32:
            raise RuntimeError("BLIND_INDEX_KEY must be at least 32 characters")
        self._fernet = MultiFernet([Fernet(k.encode()) for k in keys])
        self._index_key = index_key.encode()

    @classmethod
    def from_env(cls):
        return cls(os.environ.get("FIELD_ENCRYPTION_KEYS", "").split(","),
                   os.environ.get("BLIND_INDEX_KEY", ""))

    def encrypt(self, plaintext):
        if plaintext is None:
            return None
        return self._fernet.encrypt(plaintext.encode("utf-8")).decode("ascii")

    def decrypt(self, token):
        if token is None:
            return None
        try:
            return self._fernet.decrypt(token.encode("ascii")).decode("utf-8")
        except InvalidToken as exc:
            raise ValueError("cannot decrypt value (wrong key or tampered data)") from exc

    def rotate(self, token):
        """Re-encrypt with the newest key (run over all rows after adding a new key)."""
        return self._fernet.rotate(token.encode("ascii")).decode("ascii")

    def blind_index(self, value):
        normalized = value.strip().lower().encode("utf-8")
        return hmac.new(self._index_key, normalized, hashlib.sha256).hexdigest()


def generate_keys():
    return {"FIELD_ENCRYPTION_KEYS": Fernet.generate_key().decode(),
            "BLIND_INDEX_KEY": os.urandom(32).hex()}
