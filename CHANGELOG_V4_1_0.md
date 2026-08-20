# V4.1.0 - Google Drive Storage & RBAC

- Google Drive OAuth Desktop.
- Tạo/liên kết thư mục gốc và mở link trực tiếp.
- Tự upload file đính kèm Hồ sơ/Bản vẽ lên Drive.
- Cấu trúc thư mục theo Dự án / Loại hồ sơ-bản vẽ / Mã.
- ACL và role: reader=Chỉ đọc, writer=Cập nhật, owner/organizer=Admin.
- My Drive: một Owner; Shared Drive: nhiều Manager/Admin.
- Desktop khóa chức năng cập nhật/xóa theo role.
- Streamlit hỗ trợ Shared Drive + service account và OIDC email/RBAC.
- Cloud DB hỗ trợ attachment metadata `drive_file_id`, `drive_web_url`, `storage_backend`.
