import base64
import hashlib
import hmac
import time
import urllib.parse


def verify_callback(timestamp: str, sign: str, secret: str, *, now: int | None = None, max_skew_seconds: int = 60) -> bool:
    try:
        timestamp_ms = int(timestamp)
    except ValueError:
        return False
    current_ms = int((now if now is not None else time.time()) * 1000)
    if abs(current_ms - timestamp_ms) > max_skew_seconds * 1000:
        return False
    string_to_sign = f"{timestamp}\n{secret}".encode()
    digest = base64.b64encode(hmac.new(secret.encode(), string_to_sign, hashlib.sha256).digest()).decode()
    return hmac.compare_digest(urllib.parse.unquote(sign), digest)


class DingTalkMessenger:
    def __init__(self, sender) -> None:
        self.sender = sender

    def deliver(self, recipient: str, message: str) -> None:
        self.sender(recipient, message)
