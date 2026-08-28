# V6.4 - Shopdrawing Role Based Approval UI

## Bổ sung
- Shopdrawing dùng cùng cơ chế giao diện phân vai như RFA/RFI.
- Nhà thầu chỉ tạo/cập nhật dữ liệu trình duyệt Shopdrawing.
- Ban điều hành, TVGS và Ban QLDA xem dữ liệu gốc ở chế độ chỉ đọc và xử lý phần Ý kiến/Kết quả phê duyệt.
- Tài khoản quyền hệ thống Update/Admin có nút `Tải file lên lưu` riêng, độc lập với vai trò duyệt.
- Danh sách Shopdrawing có nút `Mở / xử lý Shopdrawing` khi tick đúng 1 dòng.
- Trạng thái trong danh sách lấy trực tiếp từ Online Approval Workflow.

## Trường Shopdrawing trình duyệt
- Mã Shopdrawing
- Nội dung trình duyệt / Tên bản vẽ
- Bộ môn / Hệ
- Nhà thầu / Đơn vị
- Mức độ
- Revision
- Người trình
- Ngày trình
- Hạn xử lý
- Mô tả

## Database
- Tự động migrate bảng `drawings` và bổ sung:
  - `due_date`
  - `priority`
  - `description`
- Không xóa hoặc làm mất dữ liệu bản vẽ cũ.

## Sửa lỗi kèm theo
- Sửa cột `Duyệt online` của bảng bản vẽ để dùng đúng `record_kind="drawing"` và `drawing_type`.

## Kiểm thử
- V6.1 workflow
- V6.2 permission compatibility
- V6.3 RFA/RFI role UI
- V6.4 Shopdrawing role UI
- Kết quả: 9 tests passed.
