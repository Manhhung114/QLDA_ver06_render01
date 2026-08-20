# Triển khai V6.0 từ V5.0

## 1. GitHub / Streamlit

Thay toàn bộ source bằng V6.0 hoặc tối thiểu thay:

- `streamlit_app.py`
- `drive_gateway.py`

Commit lên branch đang được Streamlit sử dụng. Streamlit sẽ redeploy; nếu chưa cập nhật hãy vào **Manage app → Reboot**.

## 2. Google Apps Script

Mở project `QLDA Drive Gateway`, thay `Code.gs` bằng file V6.0.

Giữ lại `API_TOKEN` và `BOOTSTRAP_CODE` thật của hệ thống hiện tại; không commit chúng lên GitHub public.

Chạy thủ công `authorizeV60_()` một lần nếu Google yêu cầu cấp lại quyền.

Sau đó:

**Triển khai → Quản lý hoạt động triển khai → Chỉnh sửa → Phiên bản mới → Triển khai**.

Nếu cập nhật deployment hiện có thì URL `/exec` giữ nguyên.

## 3. Streamlit Secrets

Có thể giữ Secrets V5:

```toml
QLDA_DRIVE_WEBAPP_URL = "https://script.google.com/macros/s/.../exec"
QLDA_DRIVE_API_TOKEN = "TOKEN_TRUNG_CODE_GS"
QLDA_DRIVE_ENFORCE_RBAC = "true"
QLDA_DRIVE_DIRECT_MAX_UPLOAD_MB = "2048"
QLDA_DRIVE_LEGACY_MAX_UPLOAD_MB = "30"
QLDA_DRIVE_TIMEOUT = "90"
```

## 4. Kiểm tra

- Vào một sheet Bản vẽ hoặc Hồ sơ.
- Chọn bản ghi.
- Xác nhận hai nút nằm cạnh nhau: **Đính kèm file** và **Cập nhật**.
- Bấm Đính kèm file → uploader xuất hiện trong trang.
- Chọn file → uploader tự chạy.
- Bấm Cập nhật → danh sách Drive hiển thị file.
- Admin tick file → **Xóa file đã chọn**.
- User Cập nhật phải thấy tick bị khóa và không xóa được.
