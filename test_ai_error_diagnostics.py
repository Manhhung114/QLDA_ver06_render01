from ai_service import classify_openai_error, _redact_secret

class FakeError(Exception):
    def __init__(self, message, status_code=None, body=None):
        super().__init__(message)
        self.status_code=status_code
        self.body=body

cases = [
    (FakeError("You exceeded your current quota", 429, {"error":{"type":"insufficient_quota","code":"insufficient_quota"}}), "insufficient_quota"),
    (FakeError("Rate limit reached", 429, {"error":{"code":"rate_limit_exceeded"}}), "rate_limit"),
    (FakeError("Incorrect API key provided: sk-abcdefghijklmnopqrstuvwxyz", 401), "invalid_api_key"),
    (FakeError("Forbidden", 403), "permission_denied"),
    (FakeError("model_not_found", 404), "model_not_found"),
    (FakeError("Connection timed out"), "timeout"),
    (FakeError("SSL CERTIFICATE_VERIFY_FAILED"), "network"),
    (FakeError("Internal server error", 500), "server_error"),
]

for exc, expected in cases:
    info=classify_openai_error(exc)
    assert info.code == expected, (expected, info)
assert "abcdefghijklmnopqrstuvwxyz" not in _redact_secret("key sk-abcdefghijklmnopqrstuvwxyz")
print("AI error diagnostics: OK")
