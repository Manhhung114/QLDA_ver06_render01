# V6.5 - Contractor Submission Files

## Mục tiêu
Bổ sung tệp trình duyệt cho Nhà thầu trong các luồng phê duyệt online RFA, RFI và Shopdrawing.

## Nhà thầu
- RFA/RFI có thêm nút `Lưu & tải tệp trình duyệt` ngay trong form.
- Shopdrawing có thêm nút `Lưu & tải tệp trình duyệt` ngay trong form.
- Sau khi hồ sơ đã được lưu, luôn hiện nút riêng:
  - `Tải tệp trình duyệt lên` cho RFA/RFI.
  - `Tải tệp Shopdrawing trình duyệt lên` cho Shopdrawing.
- Nếu chọn `Lưu & tải tệp trình duyệt`, app tự lưu hồ sơ rồi mở ngay vùng upload Google Drive.
- File được lưu theo đúng Dự án → loại hồ sơ/bản vẽ → mã hồ sơ.

## Người phê duyệt
- Ban điều hành, TVGS và Ban QLDA thấy danh sách tệp trình duyệt trước phần xử lý phê duyệt.
- Có nút `Xem`, `Drive`, `Tải` cho từng file.
- App hiển thị số lượng tệp trình duyệt hiện hành.
- Nút `Phê duyệt` bị khóa nếu chưa có tệp trình duyệt.
- Vẫn cho phép `Yêu cầu chỉnh sửa` khi thiếu file.

## Ràng buộc workflow
- RFA, RFI và Shopdrawing phải có ít nhất 01 tệp trình duyệt trước khi Nhà thầu bấm `Trình phê duyệt`.
- Khi hồ sơ bị trả về chỉnh sửa, phải còn/có ít nhất 01 tệp trình duyệt trước khi `Trình lại`.
- File trong `_Lich_su` không được tính là file hiện hành để mở khóa phê duyệt.

## Quyền hệ thống
- Tài khoản phân loại Nhà thầu vẫn cần quyền hệ thống `Cập nhật` để tạo/sửa hồ sơ và tạo ticket upload theo cơ chế Drive hiện tại.
- Tài khoản Update/Admin không phải Nhà thầu vẫn có nút `Tải file lên lưu` độc lập với quyền phê duyệt.

## Kiểm thử
- V6.1 workflow
- V6.2 permission compatibility
- V6.3 RFA/RFI role UI
- V6.4 Shopdrawing role UI
- V6.5 contractor submission files
- Kết quả: 13 tests passed.
