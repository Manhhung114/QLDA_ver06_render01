# Triển khai V6.9 - Revision Re-upload Fix

## Railway
1. Sao lưu source hiện tại.
2. Thay source bằng bộ V6.9.
3. Push đúng repository/branch Railway đang deploy.
4. Railway -> Deployments -> Redeploy.
5. Mở RFA/RFI/Shopdrawing/BV hoàn công và kiểm tra dòng `Approval UI / Workflow engine: V6.9`.

## Google Apps Script
Không cần thay `Code.gs` nếu upload Drive V6.7/V6.8 đang hoạt động bình thường. V6.9 dùng lại cơ chế resumable upload và `_Lich_su` hiện có.

## Test nghiệp vụ cần thực hiện
1. Nhà thầu tạo hồ sơ + tải file + Lưu.
2. Ban điều hành yêu cầu chỉnh sửa.
3. Nhà thầu tick hồ sơ -> Mở/xử lý.
4. Bấm Đính kèm file: uploader mới phải xuất hiện; nếu iframe không thuận tiện có thể bấm `Mở trình tải ở tab riêng`.
5. Trước khi tải file mới, nút Lưu phải bị khóa ở vòng chỉnh sửa.
6. Tải file mới -> Hoàn tất/cập nhật File DB -> nút Lưu được mở.
7. Bấm Lưu -> hồ sơ tự trở về đúng Ban điều hành.
8. Lặp lại tương tự khi TVGS hoặc Ban QLDA trả hồ sơ.

Không xóa database và không xóa file Drive cũ.
