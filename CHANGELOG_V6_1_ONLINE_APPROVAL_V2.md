# V6.1 - Online Approval Workflow V2

## Thay đổi chính

- Viết lại luồng phê duyệt online cho RFA, RFI, Shopdrawing và Bản vẽ hoàn công.
- Luồng chính: Nhà thầu → Ban điều hành → TVGS → Ban QLDA → Đã phê duyệt.
- Khi yêu cầu chỉnh sửa, hồ sơ quay về Nhà thầu.
- Sau khi chỉnh sửa, hồ sơ trình lại đúng cấp đã trả hồ sơ thay vì luôn chạy lại từ Ban điều hành.
- Không còn xóa lịch sử bước duyệt khi trình lại.
- Thêm bảng `approval_history` để lưu toàn bộ nhật ký workflow.
- Thêm `revision_no` và `return_stage` cho `approval_workflows`.
- Kiểm tra chặt bước đang xử lý và email người được chỉ định để tránh duyệt sai lượt.
- Bổ sung giao diện sơ đồ trạng thái 5 bước và bảng lịch sử phê duyệt.
- Email thông báo vẫn được gửi khi chuyển bước, yêu cầu chỉnh sửa, trình lại và hoàn tất.

## Kiểm thử

- `python -m compileall -q .`: đạt.
- `test_v61_online_approval_workflow.py`: đạt.
- Bộ test legacy toàn project có một số test lỗi sẵn/không tương thích môi trường Linux và giao diện hiện tại; không phát sinh từ thay đổi workflow V2.
