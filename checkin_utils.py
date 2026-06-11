import hmac
import hashlib
import time
from flask import current_app

TOKEN_TTL = 1800  # 30 minutes


def make_token(user_id, event_id):
    """Return a signed check-in token string: 'uid:eid:timestamp:sig'."""
    ts = int(time.time())
    msg = f"{user_id}:{event_id}:{ts}"
    sig = hmac.new(
        current_app.secret_key.encode(),
        msg.encode(),
        hashlib.sha256,
    ).hexdigest()[:16]
    return f"{user_id}:{event_id}:{ts}:{sig}"


def verify_token(raw):
    """Verify and decode a token. Returns (user_id, event_id) or raises ValueError."""
    parts = raw.strip().split(":")
    if len(parts) != 4:
        raise ValueError("invalid format")
    uid, eid, ts_s, sig = parts
    try:
        ts = int(ts_s)
    except ValueError:
        raise ValueError("invalid format")
    if int(time.time()) - ts > TOKEN_TTL:
        raise ValueError("token expired — ask the student to refresh their screen")
    msg = f"{uid}:{eid}:{ts_s}"
    expected = hmac.new(
        current_app.secret_key.encode(),
        msg.encode(),
        hashlib.sha256,
    ).hexdigest()[:16]
    if not hmac.compare_digest(sig, expected):
        raise ValueError("invalid signature")
    return int(uid), int(eid)
