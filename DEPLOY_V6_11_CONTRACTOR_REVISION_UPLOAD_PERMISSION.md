# Deploy V6.11

V6.11 **bắt buộc cập nhật cả Railway và Google Apps Script** vì lỗi nằm ở quyền upload phía `Code.gs`.

1. Thay source Railway bằng toàn bộ source V6.11 và Redeploy.
2. Google Apps Script: thay `google_drive_appscript/Code.gs` bằng file V6.11.
3. Chọn **Deploy → Manage deployments → Edit → New version → Deploy**. Giữ nguyên URL `/exec` hiện tại.
4. Nhà thầu đăng xuất rồi đăng nhập lại.
5. Mở hồ sơ `Chờ Nhà thầu chỉnh sửa` → Mở/xử lý.
6. Có 2 cách tải file:
   - `Mở trình tải file ở tab riêng` / iframe: dùng cho file lớn.
   - `Tải file cập nhật trực tiếp trong app`: dự phòng, tối đa theo `QLDA_DRIVE_LEGACY_MAX_UPLOAD_MB` (mặc định 30 MB/file).
7. Sau khi file mới xuất hiện, bấm Lưu hồ sơ/Lưu bản vẽ để tự trình lại đúng cấp đã trả.

Không xóa database và không xóa file cũ. File trùng tên được đưa vào `_Lich_su`.
