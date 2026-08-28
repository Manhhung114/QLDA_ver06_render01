# V6.2 - Sửa phân quyền phê duyệt người dùng

## Lỗi đã sửa

- Sửa lỗi chọn **Phân loại phê duyệt** nhưng sau khi cập nhật bảng lại hiện **Không tham gia duyệt**.
- Nguyên nhân: các bản V6.0 cũ dùng `approval_group` với mã `none/contractor/site_management/tvgs/bqlda`, trong khi V6.1 dùng `approval_role` với mã `CONTRACTOR/SITE_MANAGEMENT/CONSULTANT/PROJECT_MANAGEMENT`.

## Cách xử lý V6.2

- `drive_gateway.py` gửi đồng thời cả `approval_role` và `approval_group` để tương thích backend cũ lẫn mới.
- `streamlit_app.py` đọc được cả hai trường và chuẩn hóa về một bộ mã duy nhất.
- Admin nếu dữ liệu cũ chưa có phân loại duyệt sẽ mặc định là **Ban QLDA** (`PROJECT_MANAGEMENT` / `bqlda`).
- Form quản lý người dùng được viết lại:
  - Chọn trực tiếp người dùng hiện có để cập nhật.
  - Tự nạp lại tên, quyền hệ thống và phân loại phê duyệt hiện tại.
  - Không còn phải nhập lại email thủ công khi sửa người cũ.
  - Sau khi lưu, app kiểm tra lại giá trị backend đã lưu; không báo thành công giả.
  - Nếu Apps Script quá cũ và không hỗ trợ phân loại duyệt, app báo rõ cần deploy `Code.gs` mới.
- `Code.gs` V6.2 đọc/ghi tương thích cả `approval_role` và `approval_group`.

## Quy ước Admin

- Admin luôn có tối thiểu vai trò phê duyệt **Ban QLDA** nếu chưa chọn phân loại khác.
- Dữ liệu Admin cũ đang trống sẽ được hiển thị là Ban QLDA trong app V6.2.

## Kiểm thử

- `python -m py_compile streamlit_app.py drive_gateway.py cloud_db.py`: đạt.
- `node --check Code.gs`: đạt.
- `pytest -q test_v61_online_approval_workflow.py test_v62_approval_permission_compat.py`: **3 passed**.
