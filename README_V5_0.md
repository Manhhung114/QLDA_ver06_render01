# QLDA Xây dựng V5.0 — Drive Direct 2GB

V5.0 giữ toàn bộ module QLDA V4.x (Tiến độ, Hồ sơ, Bản vẽ, Báo cáo, Văn bản, AI, Cài đặt) và thay hoàn toàn đường upload file Hồ sơ/Bản vẽ.

## Kiến trúc upload

```text
Trình duyệt người dùng
       │
       ├─ metadata / tạo ticket ──> Streamlit ──> Apps Script
       │
       └─ file chunk thích nghi 2 MB → 1 MB → 512 KiB → 256 KiB ──> Apps Script relay ──> Google Drive resumable session
```

File bytes không đi qua Streamlit/SQLite. Apps Script nhận từng chunk thích nghi 2 MB → 1 MB → 512 KiB → 256 KiB và chuyển tiếp ngay vào Drive resumable session; OAuth token không rời Apps Script.

## Giới hạn

- QLDA V5.0: 2 GB / file.
- Google Drive thực tế hỗ trợ file lớn hơn nhiều; giới hạn 2 GB là chính sách của ứng dụng.
- Upload ticket có hạn khoảng 30 phút; Drive resumable session có thời hạn riêng.

## Cấu trúc Drive

```text
QLDA Xây dựng/
└── MA_DU_AN/
    ├── 02_Ho_so/
    │   ├── NCR/NCR-001/
    │   ├── RFI/RFI-001/
    │   ├── RFA/RFA-001/
    │   ├── NTCV/...
    │   ├── NTVL/...
    │   └── KDVT/...
    ├── 03_Ban_ve/
    │   ├── SHOPDRAWING/MEP-01/
    │   ├── ISSUED_DESIGN/...
    │   ├── UPDATED/...
    │   └── AS_BUILT/...
    └── 04_Phat_sinh_VO/VO/...
```

Nếu file trùng tên, file cũ được chuyển vào `_Lich_su`.

## Phân quyền

- Chỉ đọc: `read` → Viewer thư mục Drive + chỉ xem trong app.
- Cập nhật: `update` → Viewer thư mục Drive + được thêm/sửa/upload qua Gateway; **không được xóa**.
- Admin: `admin` → Editor Drive + quản trị tài khoản/quyền + quyền xóa trong app.
- Owner thực của My Drive vẫn là tài khoản đã deploy Apps Script.

## Streamlit Secrets

```toml
QLDA_DRIVE_WEBAPP_URL = "https://script.google.com/macros/s/.../exec"
QLDA_DRIVE_API_TOKEN = "TRUNG_VOI_API_TOKEN_TRONG_Code.gs"
QLDA_DRIVE_ENFORCE_RBAC = "true"
QLDA_DRIVE_DIRECT_MAX_UPLOAD_MB = "2048"
QLDA_DRIVE_LEGACY_MAX_UPLOAD_MB = "30"
QLDA_DRIVE_TIMEOUT = "90"
```

Không cần `GOOGLE_DRIVE_ROOT_FOLDER_ID`, Google OAuth Client hoặc Service Account.
