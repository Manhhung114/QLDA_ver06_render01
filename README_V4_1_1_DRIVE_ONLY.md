# QLDA Xây dựng V4.1.1 - Google Drive Only

## Kiến trúc

V4.1.1 dùng **Google Apps Script Web App** làm cổng lưu file vào Google Drive. Cách này không yêu cầu tạo Project/OAuth/Service Account trong Google Cloud Console.

Luồng:

`Streamlit → HTTPS → Apps Script Web App → Google Drive của chủ script`

Apps Script chạy bằng tài khoản đã triển khai script và tự tìm/tạo thư mục `QLDA Xây dựng`.

## 1. Tạo Drive Gateway (không dùng Google Cloud Console)

1. Đăng nhập Google bằng tài khoản sẽ làm chủ kho QLDA.
2. Trong Google Drive chọn **Mới → Thêm → Google Apps Script**. Nếu menu không hiện, mở `script.google.com` bằng cùng tài khoản.
3. Tạo project tên `QLDA Drive Gateway`.
4. Mở file `google_drive_appscript/Code.gs` trong gói V4.1.1, copy toàn bộ và dán vào Apps Script.
5. Đổi 2 dòng ở đầu file:

```javascript
const API_TOKEN = 'mot-token-rat-dai-ngau-nhien';
const BOOTSTRAP_CODE = 'mot-ma-khoi-tao-admin-rat-dai';
```

6. Bấm **Save**.
7. Bấm **Deploy → New deployment → Web app**.
8. Chọn:
   - Execute as: **Me**
   - Who has access: **Anyone**
9. Bấm **Deploy** và chấp nhận quyền Drive mà Google yêu cầu cho chính script.
10. Copy URL có dạng `https://script.google.com/macros/s/.../exec`.

> Endpoint được công khai để Streamlit server gọi được, nhưng mọi POST của V4.1.1 đều phải có `API_TOKEN`. Không chia sẻ token này công khai.

## 2. Cấu hình Streamlit Secrets

Vào Streamlit Community Cloud → app → Settings → Secrets và dán:

```toml
QLDA_DRIVE_WEBAPP_URL = "https://script.google.com/macros/s/.../exec"
QLDA_DRIVE_API_TOKEN = "mot-token-rat-dai-ngau-nhien"
QLDA_DRIVE_ENFORCE_RBAC = "true"
QLDA_DRIVE_MAX_UPLOAD_MB = "20"
QLDA_DRIVE_TIMEOUT = "90"
```

`QLDA_DRIVE_API_TOKEN` phải trùng `API_TOKEN` trong `Code.gs`.

Không cần:
- `GOOGLE_DRIVE_ROOT_FOLDER_ID`
- Google OAuth Client ID/Secret
- Service Account JSON
- Google Cloud Console

## 3. Khởi tạo Admin lần đầu

Mở app Streamlit. Nếu Drive Gateway chưa có user, app hiển thị form khởi tạo Admin.

Nhập:
- Email Admin
- Tên Admin
- Mật khẩu (>= 8 ký tự)
- `BOOTSTRAP_CODE` đã đặt trong `Code.gs`

Sau khi tạo Admin thành công, bootstrap tự khóa và lần sau chỉ còn màn hình đăng nhập.

## 4. Phân quyền

Admin vào **⚙ Cài đặt → ☁ Google Drive & quyền** để thêm user.

- **Chỉ đọc**: xem app; Apps Script chia sẻ folder `QLDA Xây dựng` dạng Viewer.
- **Cập nhật**: được sửa dữ liệu/upload/xóa file; được chia sẻ folder dạng Editor.
- **Admin**: toàn quyền trong app + quản lý user; trên Drive là Editor. Owner Drive vẫn là tài khoản đã deploy Apps Script.

Mỗi user có email + mật khẩu QLDA. Password chỉ được lưu dạng SHA-256 + salt trong thư mục riêng `QLDA_XayDung_SYSTEM_PRIVATE` trên Drive; thư mục này không nằm dưới thư mục `QLDA Xây dựng` được chia sẻ.

## 5. Tự phân file

Ứng dụng tự tạo cấu trúc:

```text
QLDA Xây dựng/
├── MA_DU_AN_01/
│   ├── 02_Ho_so/
│   │   ├── NCR/NCR-001/
│   │   ├── RFI/RFI-001/
│   │   ├── RFA/RFA-001/
│   │   ├── NTCV/NTCV-001/
│   │   ├── NTVL/NTVL-001/
│   │   └── KDVT/KDVT-001/
│   ├── 03_Ban_ve/
│   │   ├── SHOPDRAWING/SD-001/
│   │   ├── ISSUED_DESIGN/...
│   │   ├── UPDATED/...
│   │   └── AS_BUILT/...
│   └── 04_Phat_sinh_VO/
│       └── VO/VO-001/
```

Nếu file mới có cùng tên trong cùng hồ sơ/bản vẽ:
- file cũ tự chuyển vào `_Lich_su/`
- tên file cũ thêm timestamp
- file mới giữ tên gốc và trở thành bản hiện hành.

## 6. Lưu ý

- V4.1.1 dùng Drive làm kho file đính kèm và nguồn phân quyền. SQLite vẫn là database nghiệp vụ runtime của Streamlit hiện tại.
- Các file lớn qua Apps Script bị giới hạn bởi cấu hình `QLDA_DRIVE_MAX_UPLOAD_MB`; mặc định gói là 20 MB để tránh timeout/payload quá lớn.
- Khi thay đổi `Code.gs`, hãy tạo **New deployment** hoặc cập nhật deployment để URL `/exec` chạy code mới.
- Không commit API token, OpenAI key hoặc các secret thật lên GitHub.
