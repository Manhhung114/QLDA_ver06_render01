# V6.0 — Gemini 503 Resilience

- Tự retry Gemini khi gặp 429/500/503/504, timeout hoặc lỗi mạng.
- Exponential backoff + jitter; mặc định 3 lần/model.
- Nếu một model vẫn quá tải, tự chuyển sang model Gemini khác mà API key được phép dùng.
- Refresh danh sách model sau lỗi model đầu tiên để tránh alias/routing cũ.
- Biến môi trường tùy chọn:
  - GEMINI_RETRY_ATTEMPTS=3
  - GEMINI_RETRY_BASE_SECONDS=0.8
  - GEMINI_MAX_FALLBACK_MODELS=4
