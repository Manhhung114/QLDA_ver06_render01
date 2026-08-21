# V6.0 - Ticket V2 Stateless Fix

- Sửa lỗi iframe báo `Phiên tải file không hợp lệ hoặc đã hết hạn` ngay sau khi bấm Đính kèm file.
- Ticket V2 ký HMAC-SHA256, tự chứa metadata và expires_at; không phụ thuộc Cache/Properties để mở uploader.
- `drive_gateway.py` gửi đúng `QLDA_DRIVE_WEBAPP_URL`; Apps Script dùng chính deployment `/exec` này để tạo URL uploader.
- Vẫn đọc ticket V6 cũ trong ScriptProperties để tương thích khi nâng cấp.
- Giữ upload resumable 2GB và adaptive chunk.
