# QLDA Xây dựng V6.0 — Render Edition

Bản này chạy Streamlit V6.0 trên **Render Web Service** bằng Docker.
Google Drive vẫn dùng **Google Apps Script Gateway** để giữ mô hình không cần Google Cloud Console / Service Account và để file lớn đi trực tiếp từ trình duyệt sang Google Drive, không đi qua Render/SQLite.

## Kiến trúc

```text
Trình duyệt
   ├─ Giao diện nghiệp vụ ──> Render / Streamlit V6.0
   │                         └─ SQLite: /var/data/qlda_cloud.db
   │
   └─ File đính kèm 2GB ───> Google Apps Script uploader
                              └─ Google Drive resumable upload
```

## Khuyến nghị production

Dùng `render.yaml` kèm **Starter web service + Persistent Disk 1 GB** gắn tại `/var/data`.
SQLite chỉ lưu metadata/nghiệp vụ; file đính kèm nằm trên Google Drive nên disk 1 GB thường đủ cho giai đoạn đầu.

Render mặc định dùng filesystem tạm thời. Nếu không gắn Persistent Disk, SQLite có thể mất khi restart/redeploy. File đã tải lên Google Drive không bị mất.

## Deploy bằng Blueprint

1. Đưa toàn bộ thư mục V6 Render lên GitHub.
2. Trên Render chọn **New → Blueprint**.
3. Chọn repository chứa `render.yaml`.
4. Render sẽ yêu cầu nhập các biến `sync: false`:
   - `QLDA_DRIVE_WEBAPP_URL`
   - `QLDA_DRIVE_API_TOKEN`
   - `OPENAI_API_KEY` (có thể để trống nếu chưa dùng AI)
   - `GOOGLE_SEARCH_API_KEY`, `GOOGLE_SEARCH_CX` (có thể để trống)
5. Deploy.
6. Health check dùng `/_stcore/health`.

## Deploy thủ công

Tạo **Web Service** từ GitHub:

- Runtime: Docker
- Region: Singapore
- Dockerfile: `Dockerfile`
- Health Check Path: `/_stcore/health`
- Instance: Starter trở lên nếu cần Persistent Disk
- Persistent Disk: mount `/var/data`, 1 GB

Environment:

```env
QLDA_DB_PATH=/var/data/qlda_cloud.db
QLDA_RENDER_PERSISTENT_DISK=true
QLDA_DRIVE_WEBAPP_URL=https://script.google.com/macros/s/.../exec
QLDA_DRIVE_API_TOKEN=TOKEN_TRUNG_VOI_APPS_SCRIPT
QLDA_DRIVE_ENFORCE_RBAC=true
QLDA_DRIVE_DIRECT_MAX_UPLOAD_MB=2048
QLDA_DRIVE_LEGACY_MAX_UPLOAD_MB=30
QLDA_DRIVE_TIMEOUT=90
```

## Apps Script

Giữ `google_drive_appscript/Code.gs` và deploy Web App:

- Execute as: Me
- Who has access: Anyone
- URL phải kết thúc `/exec`
- `API_TOKEN` trong Code.gs phải trùng `QLDA_DRIVE_API_TOKEN` trên Render.

Sau khi sửa Code.gs, phải tạo **New version** cho deployment.

## Render Free

Có file `render-free.yaml` để tham khảo/demo. Free Web Service không có Persistent Disk; DB SQLite là tạm thời và có thể mất khi service restart/redeploy. Không dùng cấu hình này cho dữ liệu dự án thật.

## MPP

Dockerfile đã cài Java (`default-jre-headless`) để `mpxj` có thể đọc `.mpp` trên Linux/Render.

## Các chức năng V6 giữ nguyên

- Tiến độ/Microsoft Project
- Hồ sơ NCR/RFA/RFI/VO/NTCV/NTVL/KDVT
- Bản vẽ 4 nhóm
- Google Drive 2GB/file, resumable upload
- File DB đồng bộ theo Google Drive
- Tick chọn xóa; chỉ Admin được xóa
- Quyền Chỉ đọc / Cập nhật / Admin
- Báo cáo trực quan
- Văn bản QLDA, TVPL clickable
- Trợ lý AI
