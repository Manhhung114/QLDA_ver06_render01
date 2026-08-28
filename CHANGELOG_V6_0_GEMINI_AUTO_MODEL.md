# V6.0 Gemini Auto Model Fix

- GEMINI_MODEL mặc định = `auto`.
- Dùng `client.models.list()` để lấy model `generateContent` mà chính API key hiện tại truy cập được.
- Ưu tiên Gemini 3.7/3.6/3.5 Flash, sau đó 2.5 Flash/Flash-Lite.
- Nếu model cấu hình trả 404, tự refresh danh sách và retry một lần bằng model khác.
- Không còn yêu cầu người dùng đoán model khi API key không được cấp cùng tập model.
