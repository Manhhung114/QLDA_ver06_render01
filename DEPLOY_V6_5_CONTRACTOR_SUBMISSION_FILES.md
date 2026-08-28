# Triển khai V6.5 - Tệp trình duyệt Nhà thầu

## Nếu đang chạy V6.4 trên Railway
1. Thay source bằng bộ V6.5.
2. Giữ nguyên các Environment Variables hiện tại.
3. Redeploy Railway.
4. Không cần xóa SQLite/database.
5. Không cần deploy lại Google Apps Script nếu V6.2/V6.4 hiện đang upload file bình thường.

## Phân quyền Nhà thầu
Trong Cài đặt → Google Drive & quyền:
- Quyền hệ thống: `Cập nhật`.
- Phân loại duyệt: `Nhà thầu`.

Sau khi đổi quyền, người dùng nên đăng xuất và đăng nhập lại.

## Cách dùng RFA/RFI/Shopdrawing
1. Nhà thầu nhập thông tin hồ sơ.
2. Bấm `Lưu & tải tệp trình duyệt`.
3. Chọn file trong vùng upload Google Drive.
4. Bấm `Hoàn tất & cập nhật File DB` / làm mới danh sách file.
5. Kiểm tra file xuất hiện trong danh sách.
6. Chọn người duyệt và bấm `Trình phê duyệt`.
7. Ban điều hành → TVGS → Ban QLDA mở/xem file phía trên rồi mới phê duyệt.

## Lưu ý
RFA, RFI và Shopdrawing không thể trình/phê duyệt nếu danh sách file hiện hành đang trống.
