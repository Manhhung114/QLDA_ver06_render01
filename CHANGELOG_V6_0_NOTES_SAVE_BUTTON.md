# V6.0 – Ghi chú + bỏ nút Tải lên màu đỏ

- Bỏ nút `⬆️ Tải lên` màu đỏ trong form Hồ sơ/Bản vẽ.
- Nút bên phải đổi thành `💾 Lưu hồ sơ / 💾 Lưu bản vẽ` khi tạo mới và `💾 Cập nhật` khi chỉnh sửa.
- `📎 Đính kèm file` là thao tác riêng để mở vùng upload Google Drive.
- Bổ sung trường `Ghi chú` cho toàn bộ sheet Hồ sơ, Bản vẽ và Nhật ký công trường.
- Bổ sung cột `Ghi chú` trong bảng Hồ sơ/Bản vẽ/Nhật ký và đưa Ghi chú vào tìm kiếm.
- SQLite tự migrate cột `documents.note`; dữ liệu cũ được giữ nguyên.
