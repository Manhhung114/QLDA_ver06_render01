# V6.0 - Online Approval Workflow

Áp dụng cho RFA, RFI, Shopdrawing và Bản vẽ hoàn công.

## Luồng duyệt
Nhà thầu -> Ban điều hành -> Tư vấn giám sát -> Ban QLDA -> Đã phê duyệt.

- Mỗi bước có người được chỉ định, trạng thái, comment, người thao tác và thời điểm.
- Có hành động Phê duyệt hoặc Yêu cầu chỉnh sửa; yêu cầu chỉnh sửa bắt buộc comment và trả về Nhà thầu.
- Khi duyệt xong bước cuối, trạng thái hồ sơ/bản vẽ đổi thành `Đã phê duyệt`.
- Khi chuyển bước, Apps Script gửi email cho người duyệt tiếp theo; khi bị trả lại hoặc duyệt hoàn tất gửi email cho Nhà thầu.

## Phân loại người dùng
Admin có thể gán thêm `Phân loại phê duyệt`:
- Nhà thầu (`CONTRACTOR`)
- Ban điều hành (`SITE_MANAGEMENT`)
- Tư vấn giám sát (`CONSULTANT`)
- Ban quản lý dự án (`PROJECT_MANAGEMENT`)

Phân loại này tách biệt với quyền hệ thống `read/update/admin`.

## Database
Tự tạo hai bảng mới, không xóa dữ liệu cũ:
- `approval_workflows`
- `approval_steps`

## Email
`Code.gs` dùng `MailApp.sendEmail`. `appsscript.json` được bổ sung scope `script.send_mail`; sau khi cập nhật cần cấp quyền lại cho deployment Apps Script nếu Google yêu cầu.

Nên đặt biến môi trường `QLDA_APP_URL=https://<domain-app>` để link trong email mở đúng app.
