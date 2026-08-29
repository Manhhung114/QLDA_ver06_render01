# Deploy V6.12

1. Cập nhật toàn bộ source V6.12 lên repository/branch Railway đang sử dụng.
2. Redeploy Railway.
3. Đăng xuất và đăng nhập lại.
4. Kiểm tra màn hình có `Approval UI / Workflow engine: V6.12`.
5. Với Nhà thầu quyền hệ thống `Cập nhật`, KHÔNG bắt buộc cập nhật Code.gs nếu upload hiện tại đang hoạt động.
6. Nếu Nhà thầu chỉ có quyền `Chỉ đọc`, dùng Code.gs đi kèm V6.12 (kế thừa quyền upload giới hạn từ V6.11) và deploy New version trên Google Apps Script.

Thao tác hồ sơ bị trả về: Mở/xử lý -> mở `Đính kèm file cập nhật / trình lại` -> chọn file -> `Tải file đã chọn lên Google Drive` -> Lưu hồ sơ.
