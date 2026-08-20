# QLDA Xây dựng V4.1.1 - Drive Only / No Google Cloud Console

## Mục tiêu
- Dùng Google Drive làm kho file tập trung cho bản Streamlit.
- Không cần Google Cloud Console, OAuth Client ID, Service Account hoặc `GOOGLE_DRIVE_ROOT_FOLDER_ID`.
- Google Apps Script Web App đóng vai trò cổng an toàn giữa Streamlit và Google Drive.
- Phân quyền trong app: Chỉ đọc / Cập nhật / Admin.

## Cơ chế Drive
- Apps Script tự tìm hoặc tạo thư mục `QLDA Xây dựng` trên My Drive của tài khoản triển khai script.
- File upload tự phân theo:
  - `<Mã dự án>/02_Ho_so/<Loại hồ sơ>/<Mã hồ sơ>/...`
  - `<Mã dự án>/03_Ban_ve/<Loại bản vẽ>/<Mã bản vẽ>/...`
  - VO: `<Mã dự án>/04_Phat_sinh_VO/VO/<Mã VO>/...`
- Khi upload file trùng tên, file cũ được chuyển vào `_Lich_su` kèm timestamp rồi mới lưu bản mới.
- Xóa file trong app sẽ đưa file Drive vào Thùng rác trước khi xóa metadata DB.

## Phân quyền
- Chỉ đọc: xem app, mở file; được share Viewer trên thư mục Drive.
- Cập nhật: sửa dữ liệu và upload file; **không được xóa**; được share Viewer trên Drive.
- Admin: toàn quyền quản trị app và người dùng; được share Editor trên Drive. Owner Drive vẫn là tài khoản triển khai Apps Script.
- Tài khoản và password hash/salt được lưu trong thư mục riêng `QLDA_XayDung_SYSTEM_PRIVATE` trên Drive, không nằm dưới thư mục chia sẻ.

## Streamlit Secrets
```toml
QLDA_DRIVE_WEBAPP_URL = "https://script.google.com/macros/s/.../exec"
QLDA_DRIVE_API_TOKEN = "token-giong-API_TOKEN-trong-Code.gs"
QLDA_DRIVE_ENFORCE_RBAC = "true"
QLDA_DRIVE_MAX_UPLOAD_MB = "20"
```
