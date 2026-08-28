# Triển khai V6.3

## Railway
Nếu đang chạy V6.2, phần thay đổi chính ở `streamlit_app.py`.

1. Thay source bằng bộ V6.3.
2. Commit/push lên repository Railway đang theo dõi hoặc upload source theo cách đang dùng.
3. Redeploy Railway.
4. Đăng xuất và đăng nhập lại trên điện thoại để nạp lại quyền.

## Google Apps Script
V6.3 không thay đổi schema quyền so với V6.2. Nếu đã cập nhật Code.gs của V6.2 và phân loại duyệt lưu đúng thì không cần deploy Apps Script lại.

## Quyền đề nghị
- Nhà thầu: role=update + approval role=CONTRACTOR
- Ban điều hành: role=update hoặc read + approval role=SITE_MANAGEMENT
- TVGS: role=update hoặc read + approval role=CONSULTANT
- Ban QLDA: role=update/admin + approval role=PROJECT_MANAGEMENT
- Nhân sự chỉ tải file lưu: role=update + không tham gia duyệt

Lưu ý: người duyệt có role=read vẫn duyệt online được theo approval role nhưng không có nút upload file. Muốn người đó upload file, đặt role=update.
