# Triển khai QLDA V5.0 — từng bước

## A. Cập nhật Apps Script

1. Mở project `QLDA Drive Gateway` trên script.google.com.
2. Thay toàn bộ `Code.gs` bằng `google_drive_appscript/Code.gs` của V5.0.
3. Giữ/đặt `API_TOKEN` và `BOOTSTRAP_CODE` bí mật. Nếu đang nâng từ V4.1.1 và muốn giữ đăng nhập hiện tại, có thể giữ cùng API_TOKEN; session cũ vẫn nên đăng nhập lại sau deploy.
4. Chọn hàm `authorizeV50_` trên thanh Run và bấm **Chạy** một lần.
5. Chấp nhận quyền Google Drive và external request mà Google yêu cầu.
6. Deploy → Manage deployments → Edit → New version → Deploy.
7. Giữ URL `/exec` hiện tại nếu cập nhật deployment cũ.

## B. Cập nhật GitHub / Streamlit

1. Upload toàn bộ source V5.0 lên branch `main`.
2. Streamlit sẽ redeploy; nếu không, Manage app → Reboot.
3. Secrets:

```toml
QLDA_DRIVE_WEBAPP_URL = "https://script.google.com/macros/s/.../exec"
QLDA_DRIVE_API_TOKEN = "..."
QLDA_DRIVE_ENFORCE_RBAC = "true"
QLDA_DRIVE_DIRECT_MAX_UPLOAD_MB = "2048"
QLDA_DRIVE_LEGACY_MAX_UPLOAD_MB = "30"
QLDA_DRIVE_TIMEOUT = "90"
```

## C. Sử dụng upload 2 GB

1. Tạo/Lưu Hồ sơ hoặc Bản vẽ trước.
2. Chọn đúng bản ghi đã lưu.
3. Trong `File trên Google Drive — Direct Upload V5.0`, bấm **Tạo phiên tải trực tiếp**.
4. Bấm **Mở cửa sổ upload 2GB**.
5. Chọn file và bấm **Bắt đầu tải**.
6. Theo dõi progress. Khi xong có nút **Mở file trên Drive**.
7. Quay lại Streamlit, bấm **Làm mới danh sách**.

## D. Kiểm tra đúng kiến trúc

Khi upload file lớn, Streamlit không nhận file bytes. Vì vậy không còn lỗi `DriveGatewayError: File ... vượt giới hạn 20/30 MB` ở luồng mới.
