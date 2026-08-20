# QLDA Xây dựng V5.0 — Google Drive Direct Upload 2GB

## Thay đổi lớn

- Loại bỏ upload file Hồ sơ/Bản vẽ qua `st.file_uploader` → Streamlit → Apps Script Base64.
- File mới được upload bằng **Google Drive resumable upload**.
- Apps Script tạo resumable session và giữ OAuth server-side; **file bytes được đọc theo chunk thích nghi 2 MB → 1 MB → 512 KiB → 256 KiB, không đi qua Streamlit, rồi được Apps Script chuyển tiếp vào Google Drive**.
- Giới hạn ứng dụng: **2 GB / file**.
- Upload theo chunk thích nghi 2 MB → 1 MB → 512 KiB → 256 KiB, hỗ trợ HTTP 308 Resume Incomplete và retry khi 5xx.
- Không truyền `ScriptApp.getOAuthToken()` xuống trình duyệt.
- Không cần Google Cloud Console, OAuth Client ID hoặc Service Account.
- File tự phân loại theo:
  - `QLDA Xây dựng / Mã dự án / 02_Ho_so / <loại> / <mã>`
  - `QLDA Xây dựng / Mã dự án / 03_Ban_ve / <loại> / <mã>`
- File trùng tên: bản cũ chuyển vào `_Lich_su`, bản mới là bản hiện hành.
- Streamlit đọc danh sách file trực tiếp từ Drive, có nút mở file, mở thư mục, xóa file.
- Các file legacy V4.x vẫn đọc được để tương thích ngược.
- Thay `use_container_width=True` bằng `width="stretch"` để bỏ cảnh báo Streamlit mới.

## Lý do thay kiến trúc

Apps Script/Streamlit proxy không phù hợp cho file lớn vì request body/Base64, timeout và bộ nhớ. V5.0 chỉ gửi metadata qua Gateway; file dữ liệu đi vào Google Drive bằng resumable session.


## RBAC UPDATE-NO-DELETE patch
- Quyền `update` chỉ được thêm/sửa dữ liệu và upload phiên bản file mới.
- Quyền `update` không được xóa task, hồ sơ, bản vẽ, dự án, attachment hay file Drive.
- `trash_file` trên Apps Script yêu cầu `admin` ở phía server, không chỉ khóa nút UI.
- Người dùng `update` được chia sẻ thư mục Drive ở mức Viewer để không thể xóa trực tiếp trong Google Drive; upload vẫn hoạt động qua Apps Script Gateway chạy dưới quyền chủ sở hữu.
- Khi đăng nhập, Gateway tự đồng bộ lại quyền Drive theo role hiện tại.
