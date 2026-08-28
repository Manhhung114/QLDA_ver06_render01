# V6.0 - AI Server Shared Configuration

## Mục tiêu
API key AI được cấu hình một lần trên máy chủ và dùng chung cho PC, điện thoại, tablet. Không còn nhập API key theo từng phiên trình duyệt.

## Thay đổi
- `OPENAI_API_KEY` và `GEMINI_API_KEY` chỉ đọc từ Environment Variables hoặc Streamlit Secrets.
- Không còn fallback sang `st.session_state` cho API key, provider, model hay AI Web Search.
- Sheet `⚙️ Cài đặt → 🤖 AI` không còn ô nhập API key.
- Admin chỉ thấy trạng thái cấu hình, provider/model/web search và nút kiểm tra kết nối.
- Người dùng Read/Update không cần biết hoặc nhập API key.
- API key không được hiển thị xuống trình duyệt.
- Thông báo lỗi AI hướng dẫn Admin kiểm tra Railway/Render Variables thay vì nhập lại trên thiết bị.

## Railway Variables khuyến nghị
```env
AI_PROVIDER=gemini
GEMINI_API_KEY=YOUR_GEMINI_KEY
GEMINI_MODEL=auto
AI_WEB_SEARCH=true

# Optional fallback / OpenAI
OPENAI_API_KEY=YOUR_OPENAI_KEY
OPENAI_MODEL=gpt-5-mini
```

Sau khi thay Variables, chọn Deploy/Redeploy để container mới nhận cấu hình.
