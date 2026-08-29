# V6.11 - Contractor Revision Upload Permission Fix

## Lỗi đã xác định
V6.10 hiển thị nút/khung đính kèm cho Nhà thầu nhưng Google Apps Script vẫn chỉ cho `role=update/admin` tạo upload ticket và upload legacy. Vì quyền hệ thống và vai trò phê duyệt là hai lớp độc lập, tài khoản có `role=read` + `approval_role=CONTRACTOR` mở được hồ sơ nhưng không tải được file cập nhật.

## Sửa V6.11
- `Code.gs`: thêm `requireUploadRole_()`.
- `read + CONTRACTOR` được upload **chỉ** khi `upload_purpose=approval_submission` và đầu mục thuộc RFA/RFI/SHOPDRAWING/AS_BUILT.
- Bắt buộc mã hồ sơ theo định dạng THÁP-BỘMÔN-STT.
- `update/admin` giữ nguyên quyền upload hiện tại.
- `drive_gateway.py`: truyền `upload_purpose` cho direct ticket và upload legacy.
- `streamlit_app.py`: khi Nhà thầu đính kèm hồ sơ phê duyệt, tự gửi `approval_submission`.
- Bổ sung **file uploader trực tiếp trong Streamlit** làm đường dự phòng (mặc định tối đa 30 MB/file). File lớn vẫn dùng uploader trực tiếp Google Drive.
- Khi hồ sơ bị trả về, file mới được nhận diện và chỉ khi có file mới mới cho Lưu/Trình lại.

## Phạm vi
RFA, RFI, Shopdrawing, Bản vẽ hoàn công (AS_BUILT).
