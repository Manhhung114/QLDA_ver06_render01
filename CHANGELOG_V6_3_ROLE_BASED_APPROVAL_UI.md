# V6.3 - Giao diện phê duyệt theo vai trò

## RFA/RFI

### 1. Nhà thầu
Chỉ nhập/sửa các trường:
- Mã RFA/RFI
- Nội dung trình duyệt
- Bộ môn / Hệ
- Nhà thầu / Đơn vị
- Mức độ
- Người trình
- Ngày trình
- Hạn xử lý
- Mô tả

Các trường cũ như Người/Đơn vị duyệt, ngày đóng, trạng thái thủ công, WBS, ghi chú, phản hồi không còn hiển thị trong form RFA/RFI. Trạng thái phê duyệt do workflow online quản lý.

Nhà thầu có nút `Lưu hồ sơ`. Sau khi hồ sơ đã được lưu có thể `Tải file lên lưu` nếu tài khoản có quyền hệ thống Update/Admin.

### 2. Người phê duyệt
Áp dụng cho:
- Ban điều hành
- TVGS
- Ban QLDA

Thông tin Nhà thầu trình được hiển thị cùng bố cục nhưng khóa chỉnh sửa. Người duyệt chỉ thao tác tại khối `Ý kiến / Kết quả phê duyệt`:
- Xem các ý kiến/kết quả trước đó
- Nhập ý kiến
- Phê duyệt
- Yêu cầu chỉnh sửa

Admin mặc định thuộc Ban QLDA nếu tài khoản cũ chưa có approval role.

### 3. Người có quyền Cập nhật
Quyền hệ thống `update` hoặc `admin` có nút riêng `Tải file lên lưu` cho hồ sơ đã chọn. Quyền upload file tách độc lập khỏi vai trò Nhà thầu/người duyệt.

### 4. Danh sách
- Giữ checkbox chọn hồ sơ.
- Tick đúng 1 hồ sơ và bấm `Mở / xử lý hồ sơ` để đưa hồ sơ lên vùng chi tiết/phê duyệt.
- Có thể chọn nhiều hồ sơ để tải xuống.
- Chỉ Admin được xóa.
- Bảng RFA/RFI chỉ giữ các cột nghiệp vụ cần thiết + trạng thái duyệt online + File DB.

## Kiểm thử
- Workflow V6.1: pass
- Tương thích phân quyền V6.2: pass
- Giao diện vai trò V6.3: pass
- Tổng test liên quan: 6 passed
