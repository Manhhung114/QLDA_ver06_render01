# Cấu hình AI tập trung trên Railway - QLDA V6.0

Vào Railway → Project → Service `qlda-xaydung-v6` → **Variables**.

Thêm:

```env
AI_PROVIDER=gemini
GEMINI_API_KEY=<API KEY GEMINI>
GEMINI_MODEL=auto
AI_WEB_SEARCH=true

OPENAI_API_KEY=<API KEY OPENAI nếu sử dụng>
OPENAI_MODEL=gpt-5-mini
```

Không ghi key vào GitHub, `streamlit_app.py`, SQLite hoặc trình duyệt.

Sau khi Save Variables:
1. Deploy/Redeploy service.
2. Mở QLDA V6 trên máy tính hoặc điện thoại.
3. `⚙️ Cài đặt → 🤖 AI` phải hiển thị `API key đã cấu hình trên máy chủ`.
4. Admin bấm `Kiểm tra Gemini API` hoặc `Kiểm tra OpenAI API`.

Tất cả thiết bị dùng chung các biến môi trường này.
