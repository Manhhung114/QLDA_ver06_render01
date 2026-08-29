# V6.8 - Workflow fail-safe / sửa hồ sơ có file nhưng Chưa trình duyệt

## Lỗi thực tế
- RFA/RFI/Shopdrawing đã có file trên Drive nhưng cột Duyệt online vẫn hiện `Chưa trình duyệt`.
- Ban điều hành bấm Mở/xử lý nhưng không vào được luồng.
- V6.7 vẫn có thể phụ thuộc endpoint danh bạ người duyệt của Apps Script.

## Sửa V6.8
1. Lưu hồ sơ có file luôn tạo workflow, không bắt buộc phải đọc được danh bạ Ban điều hành/TVGS/Ban QLDA.
2. Workflow định tuyến theo vai trò đăng nhập: SITE_MANAGEMENT -> CONSULTANT -> PROJECT_MANAGEMENT.
3. Người có đúng vai trò có thể nhận/claim bước đang chờ và xử lý; email người xử lý được ghi lại vào approval_steps.
4. Tự quét danh sách RFA/RFI/Shopdrawing: bản ghi nào có file nhưng chưa có workflow sẽ tự tạo `Đang duyệt - Ban điều hành` ngay khi mở trang.
5. Không cần mở từng hồ sơ để sửa các bản ghi V6.6/V6.7 cũ.
6. Hiển thị rõ `Approval UI / Workflow engine: V6.8` trên trang RFA/RFI/Shopdrawing để xác nhận Railway đã chạy đúng source.
7. Luồng tiếp tục: Ban điều hành -> TVGS -> Ban QLDA -> Đã phê duyệt; Yêu cầu chỉnh sửa quay Nhà thầu và trình lại đúng cấp trả hồ sơ.

## Kiểm tra
- py_compile: OK
- Workflow tests V6.1-V6.8: 23/23 passed.
