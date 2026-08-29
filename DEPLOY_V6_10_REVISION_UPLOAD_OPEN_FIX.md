# Triển khai V6.10

1. Cập nhật toàn bộ source V6.10 lên repository/branch Railway đang sử dụng.
2. Railway -> Deployments -> Redeploy.
3. Mở RFA/RFI/Shopdrawing/Bản vẽ hoàn công và kiểm tra dòng `Approval UI / Workflow engine: V6.10`.
4. Với hồ sơ bị trả về, Nhà thầu chọn hồ sơ -> Mở/xử lý. Vùng tải file phải được tạo sẵn; có nút `Mở trình tải file ở tab riêng` và iframe uploader.
5. Tải file mới -> bấm `Hoàn tất & cập nhật File DB` hoặc `Làm mới file / File DB` -> khi phát hiện file mới, nút Lưu được mở -> Lưu để trình lại đúng cấp trả hồ sơ.

Không cần cập nhật Code.gs nếu direct upload Google Drive hiện tại vẫn hoạt động ở lần trình đầu.
