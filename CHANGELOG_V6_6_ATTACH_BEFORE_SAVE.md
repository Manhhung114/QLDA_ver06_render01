# V6.6 - Nhà thầu đính kèm file trước khi Lưu

## Thay đổi chính
Luồng nhập RFA, RFI và Shopdrawing của tài khoản phân loại **Nhà thầu** được đổi thành:

1. Nhập các trường thông tin hồ sơ.
2. Bấm **📎 Đính kèm file**.
3. Tải file trực tiếp lên Google Drive và hoàn tất upload.
4. App kiểm tra đã có ít nhất 01 file hiện hành.
5. Nút **💾 Lưu hồ sơ / Lưu Shopdrawing** mới được mở để bấm.

## Giao diện Nhà thầu
- Nút `📎 Đính kèm file` nằm ngay sau trường `Mô tả` và trước nút `💾 Lưu hồ sơ`.
- Không còn yêu cầu lưu hồ sơ trước rồi mới tải file.
- RFA/RFI và Shopdrawing dùng cùng cách thao tác.
- Nếu Mã hồ sơ chưa đúng định dạng hoặc Nội dung trình duyệt còn trống, nút Đính kèm file bị khóa.
- Nếu chưa có file hiện hành trên Drive, nút Lưu bị khóa.

## Lưu file trước record SQLite
File được lưu theo Dự án → loại hồ sơ/bản vẽ → Mã hồ sơ đang nhập. Vì vậy uploader có thể hoạt động trước khi record được tạo trong SQLite.

## Người phê duyệt / người cập nhật
- Ban điều hành / TVGS / Ban QLDA vẫn xem file trước khi nhập Ý kiến/Kết quả phê duyệt.
- Tài khoản có quyền hệ thống Cập nhật/Admin nhưng không phải Nhà thầu vẫn có nút `📤 Tải file lên lưu` riêng.
- Luồng phê duyệt và lịch sử duyệt V6.1-V6.5 được giữ nguyên.
