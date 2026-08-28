# Triển khai V6.2 - Sửa phân quyền phê duyệt

## Trường hợp 1 - Apps Script hiện tại là bản Online Approval V6.0

V6.2 đã tương thích ngược với `approval_group`, vì vậy trước tiên chỉ cần cập nhật source Railway/Render bằng gói V6.2 và redeploy app.

Sau khi app chạy lại:
1. Đăng nhập Admin.
2. Vào **Cài đặt → Google Drive & quyền**.
3. Chọn **Cập nhật người dùng hiện có**.
4. Chọn người dùng.
5. Chọn **Phân loại phê duyệt**: Nhà thầu / Ban điều hành / Tư vấn giám sát / Ban QLDA.
6. Bấm **Lưu phân quyền người dùng**.
7. Kiểm tra ngay cột **Phân loại duyệt** bên dưới.

## Trường hợp 2 - App báo Apps Script quá cũ

Thay file `google_drive_appscript/Code.gs` bằng bản V6.2 trong gói này.

Trong Google Apps Script:
1. Giữ nguyên `API_TOKEN` và `BOOTSTRAP_CODE` thật đang dùng.
2. Dán Code.gs V6.2.
3. **Deploy → Manage deployments → Edit**.
4. Chọn **New version**.
5. Bấm **Deploy**.
6. Giữ nguyên URL `/exec` nếu cập nhật cùng deployment.

Sau đó quay lại Railway/Render và thử cập nhật người dùng lại.

## Lưu ý

- Không cần xóa users.json.
- Không cần tạo lại tài khoản.
- Không cần đổi URL Apps Script nếu deploy New version trên deployment hiện có.
