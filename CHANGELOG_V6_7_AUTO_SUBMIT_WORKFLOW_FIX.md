# V6.7 - Auto Submit Workflow Fix

## Lỗi được sửa
- Nhà thầu đã nhập hồ sơ và tải file lên Drive nhưng sau khi bấm **Lưu hồ sơ**, workflow vẫn chưa được tạo.
- Ban điều hành mở hồ sơ nhận thông báo: **Hồ sơ chưa được Nhà thầu trình duyệt**.
- Nguyên nhân bổ sung: endpoint `list_users` của Apps Script chỉ cho Admin sử dụng, nên tài khoản Nhà thầu không đọc được danh sách vai trò để định tuyến workflow.

## Thay đổi V6.7
1. **Lưu hồ sơ = Trình duyệt** đối với RFA, RFI và Shopdrawing.
   - Nhập thông tin -> Đính kèm file -> Bấm Lưu.
   - App tự tạo workflow và chuyển sang **Đang duyệt - Ban điều hành**.
2. Không còn bắt Nhà thầu bấm thêm nút `Trình phê duyệt` sau khi lưu.
3. Hồ sơ bị trả chỉnh sửa: Nhà thầu sửa + đính kèm/cập nhật file + bấm Lưu -> tự trình lại đúng cấp đã trả hồ sơ.
4. Hồ sơ cũ V6.6 đã có file nhưng chưa có workflow: khi người duyệt mở, app tự phục hồi workflow và chuyển về Ban điều hành.
5. Khóa nội dung gốc của Nhà thầu sau khi đã trình; chỉ mở sửa khi hồ sơ bị trả về Nhà thầu.
6. Apps Script thêm action `approval_users` cho mọi tài khoản đã đăng nhập. Endpoint chỉ trả `publicUser` (email, tên, quyền/vai trò, trạng thái), không trả salt/hash mật khẩu.

## Kiểm tra
- Python compile: OK.
- Google Apps Script syntax (Node check): OK.
- Test workflow/phân quyền/UI từ V6.1 -> V6.7: 21/21 passed.
