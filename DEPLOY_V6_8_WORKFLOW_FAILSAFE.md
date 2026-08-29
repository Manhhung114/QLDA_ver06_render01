# Deploy V6.8 - Workflow fail-safe

## Railway
1. Thay toàn bộ source hiện tại bằng gói V6.8.
2. Kiểm tra Dockerfile vẫn chạy: `streamlit run streamlit_app.py`.
3. Commit/push đúng branch mà Railway service đang theo dõi.
4. Railway -> Deployments -> Redeploy deployment mới nhất.
5. Mở RFA/RFI. Ngay dưới 3 KPI phải thấy dòng: `Approval UI / Workflow engine: V6.8`.

Nếu KHÔNG thấy dòng V6.8 thì Railway vẫn đang chạy source cũ; không phải lỗi database.

## Apps Script
V6.8 không còn bắt buộc endpoint `approval_users` để tạo workflow. Nếu hệ thống hiện tại đã upload Drive và phân quyền hoạt động thì không bắt buộc cập nhật lại Apps Script chỉ để sửa lỗi `Chưa trình duyệt`.

## Hồ sơ cũ đang kẹt
Sau khi V6.8 chạy:
- vào RFA/RFI/Shopdrawing;
- app tự phát hiện hồ sơ có file nhưng chưa workflow;
- tự tạo workflow và đổi trạng thái thành `Đang duyệt - Ban điều hành`;
- Ban điều hành tick hồ sơ -> Mở/xử lý -> Phê duyệt/Yêu cầu chỉnh sửa.

Không xóa database và không xóa file Drive.
