# V6.0 – Attachment Only + Upload Ticket Fix

- Bỏ nút `Cập nhật/Lưu hồ sơ/Lưu bản vẽ` nằm cạnh nút `Đính kèm file` ở toàn bộ sheet Hồ sơ/Bản vẽ.
- Chỉ giữ một nút `📎 Đính kèm file`; khi bấm, app lưu/cập nhật metadata hiện tại rồi tạo một phiên upload Google Drive mới.
- Mỗi lần bấm `Đính kèm file` đều hủy ticket cũ trong session và tạo ticket mới.
- Chuyển upload-ticket storage của Google Apps Script từ `CacheService` sang `PropertiesService` kèm `expires_at`, tránh ticket bị Cache thu hồi sớm và hiện lỗi “Phiên tải file không hợp lệ hoặc đã hết hạn”.
- Nút `⬆ Tải lên` vẫn nằm trong trình chọn file của Google Apps Script uploader.
- Giữ nguyên quyền RBAC, Google Drive 2 GB, cấu trúc thư mục theo tháp và dữ liệu cũ.
