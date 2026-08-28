# Triển khai V6.6 - Đính kèm file trước khi Lưu

## Nếu Railway đang chạy V6.4 hoặc V6.5
1. Thay source bằng bộ V6.6.
2. Giữ nguyên Environment Variables hiện tại.
3. Redeploy Railway.
4. Không xóa SQLite/database.
5. Không cần deploy lại Google Apps Script nếu chức năng upload Drive hiện tại đang hoạt động.

## Phân quyền Nhà thầu
- Quyền hệ thống: `Cập nhật`.
- Phân loại duyệt: `Nhà thầu`.

## Cách thao tác mới
### RFA / RFI
Nhập thông tin → `📎 Đính kèm file` → tải file/hoàn tất → `💾 Lưu hồ sơ` → `Trình phê duyệt`.

### Shopdrawing
Nhập thông tin → `📎 Đính kèm file` → tải file/hoàn tất → `💾 Lưu Shopdrawing` → `Trình phê duyệt`.

Nút Lưu chỉ được mở khi Google Drive đã có ít nhất 01 file hiện hành của đúng Mã hồ sơ.
