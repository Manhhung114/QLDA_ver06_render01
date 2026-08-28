# Deploy V6.7 - Bắt buộc cập nhật Railway + Apps Script

## Bước 1 - Cập nhật Google Apps Script
1. Mở Apps Script đang dùng cho QLDA.
2. Thay toàn bộ `Code.gs` bằng file `google_drive_appscript/Code.gs` trong gói V6.7.
3. Không đổi `API_TOKEN`, `BOOTSTRAP_CODE` và cấu hình thư mục hiện tại.
4. Chọn **Deploy -> Manage deployments -> Edit**.
5. Chọn **New version -> Deploy**.
6. Giữ nguyên URL `/exec` nếu cập nhật cùng deployment.

> V6.7 thêm action `approval_users`. Nếu không deploy Code.gs mới, Nhà thầu có thể vẫn không tự chuyển hồ sơ sang Ban điều hành.

## Bước 2 - Cập nhật Railway
1. Đưa source V6.7 lên repository/Railway.
2. Redeploy service.
3. Không xóa database.
4. Không xóa dữ liệu Google Drive.

## Bước 3 - Kiểm tra phân quyền
Trong Cài đặt -> Google Drive & quyền, phải có ít nhất:
- 01 Nhà thầu
- 01 Ban điều hành
- 01 TVGS
- 01 Ban QLDA

Admin có thể đồng thời là Ban QLDA.

## Bước 4 - Kiểm tra nghiệp vụ
### Hồ sơ mới
Nhà thầu:
1. Nhập RFA/RFI/Shopdrawing.
2. Đính kèm file.
3. Bấm Lưu.
4. Bảng phải hiện `Đang duyệt - Ban điều hành`.

Ban điều hành:
1. Tick hồ sơ.
2. Bấm `Mở / xử lý hồ sơ`.
3. Phải thấy vùng `Ý kiến / Kết quả phê duyệt` và nút `Phê duyệt / Yêu cầu chỉnh sửa`.

### Hồ sơ V6.6 cũ bị kẹt
Nếu hồ sơ đã có file nhưng hiện `Chưa trình duyệt`, Ban điều hành chỉ cần mở hồ sơ một lần sau khi nâng V6.7. App sẽ tự tạo workflow nếu phân quyền đã khai báo đầy đủ.
