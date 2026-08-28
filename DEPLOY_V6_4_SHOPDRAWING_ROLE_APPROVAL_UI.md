# Triển khai V6.4 - Shopdrawing Role Based Approval UI

## Railway / Render
1. Upload/commit toàn bộ source V6.4.
2. Redeploy service.
3. Database SQLite hiện tại được migration tự động khi app khởi động; không cần xóa DB.
4. Không cần deploy lại Google Apps Script nếu hệ thống đã dùng V6.2/V6.3 và phần phân quyền phê duyệt hoạt động bình thường.

## Kiểm tra nhanh sau deploy
- Đăng nhập Nhà thầu → Shopdrawing: có thể tạo/sửa các trường trình duyệt và Trình phê duyệt.
- Đăng nhập Ban điều hành/TVGS/Ban QLDA → Shopdrawing: dữ liệu gốc chỉ đọc, có Ý kiến/Kết quả phê duyệt và nút xử lý đúng bước.
- Đăng nhập tài khoản Update/Admin: có nút `Tải file lên lưu`.
- Trong bảng Shopdrawing: tick một dòng → `Mở / xử lý Shopdrawing`.
