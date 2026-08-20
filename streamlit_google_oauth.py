from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import time
from dataclasses import dataclass
from typing import Any

DRIVE_SCOPE = "https://www.googleapis.com/auth/drive"
STATE_MAX_AGE_SECONDS = 15 * 60


class StreamlitGoogleOAuthError(RuntimeError):
    pass


@dataclass
class GoogleOAuthConfig:
    client_id: str
    client_secret: str
    redirect_uri: str
    state_secret: str

    def validate(self) -> None:
        missing = []
        if not self.client_id:
            missing.append("GOOGLE_OAUTH_CLIENT_ID")
        if not self.client_secret:
            missing.append("GOOGLE_OAUTH_CLIENT_SECRET")
        if not self.redirect_uri:
            missing.append("GOOGLE_OAUTH_REDIRECT_URI")
        if missing:
            raise StreamlitGoogleOAuthError("Thiếu Streamlit Secrets: " + ", ".join(missing))
        if not self.redirect_uri.startswith("https://") and not self.redirect_uri.startswith("http://localhost"):
            raise StreamlitGoogleOAuthError("GOOGLE_OAUTH_REDIRECT_URI phải dùng HTTPS (trừ localhost khi chạy local).")

    @property
    def signing_secret(self) -> str:
        # Dedicated state secret is recommended; client_secret is a safe fallback.
        return self.state_secret or self.client_secret

    def client_config(self) -> dict[str, Any]:
        return {
            "web": {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "redirect_uris": [self.redirect_uri],
            }
        }


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _b64url_decode(value: str) -> bytes:
    pad = "=" * ((4 - len(value) % 4) % 4)
    return base64.urlsafe_b64decode(value + pad)


def make_signed_state(secret_value: str) -> str:
    if not secret_value:
        raise StreamlitGoogleOAuthError("Thiếu secret để ký OAuth state.")
    payload = {
        "ts": int(time.time()),
        "nonce": secrets.token_urlsafe(18),
    }
    body = _b64url(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    sig = hmac.new(secret_value.encode("utf-8"), body.encode("ascii"), hashlib.sha256).digest()
    return f"{body}.{_b64url(sig)}"


def verify_signed_state(state: str, secret_value: str, max_age_seconds: int = STATE_MAX_AGE_SECONDS) -> bool:
    try:
        body, sig = str(state or "").split(".", 1)
        expected = hmac.new(secret_value.encode("utf-8"), body.encode("ascii"), hashlib.sha256).digest()
        if not hmac.compare_digest(_b64url_decode(sig), expected):
            return False
        payload = json.loads(_b64url_decode(body).decode("utf-8"))
        ts = int(payload.get("ts") or 0)
        now = int(time.time())
        return 0 <= now - ts <= max_age_seconds
    except Exception:
        return False


def build_flow(config: GoogleOAuthConfig, state: str | None = None):
    config.validate()
    try:
        from google_auth_oauthlib.flow import Flow
    except Exception as exc:
        raise StreamlitGoogleOAuthError(
            "Thiếu google-auth-oauthlib. Hãy kiểm tra requirements.txt."
        ) from exc
    flow = Flow.from_client_config(config.client_config(), scopes=[DRIVE_SCOPE], state=state)
    flow.redirect_uri = config.redirect_uri
    return flow


def authorization_url(config: GoogleOAuthConfig) -> tuple[str, str]:
    state = make_signed_state(config.signing_secret)
    flow = build_flow(config, state=state)
    url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )
    return url, state


def exchange_code(config: GoogleOAuthConfig, code: str, state: str) -> str:
    if not verify_signed_state(state, config.signing_secret):
        raise StreamlitGoogleOAuthError("OAuth state không hợp lệ hoặc đã hết hạn. Hãy đăng nhập lại Google.")
    flow = build_flow(config, state=state)
    try:
        flow.fetch_token(code=code)
        return flow.credentials.to_json()
    except Exception as exc:
        raise StreamlitGoogleOAuthError(f"Không đổi được mã Google OAuth thành token: {exc}") from exc
