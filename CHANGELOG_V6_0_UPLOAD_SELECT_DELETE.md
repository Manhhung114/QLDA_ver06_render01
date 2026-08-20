# V6.0 - Upload thủ công + tick xóa + File DB từ Google Drive

- Đổi nút `Cập nhật` tại các sheet có file thành `⬆️ Tải lên`.
- `📎 Đính kèm file` mở vùng chọn file; chọn file KHÔNG tự upload.
- Trong uploader Google Drive, người dùng phải bấm `⬆ Tải lên` mới bắt đầu resumable upload.
- Sau khi upload xong, bấm `✅ Hoàn tất & cập nhật File DB` để đóng vùng upload và đồng bộ bảng.
- Thêm cột checkbox `Chọn` ngay trước `ID` ở toàn bộ sheet Hồ sơ và Bản vẽ.
- Admin có thể tick nhiều bản ghi rồi `Xóa hồ sơ đã chọn` / `Xóa bản vẽ đã chọn`.
- Quyền Cập nhật/Chỉ đọc không được xóa.
- Cột `File DB` lấy số file hiện có trực tiếp từ Google Drive theo batch API và hiển thị `✅ Có file (n)`.
- Khi xóa bản ghi, Admin chuyển file hiện hành + lịch sử liên quan vào Thùng rác Drive trước khi xóa record SQLite.
