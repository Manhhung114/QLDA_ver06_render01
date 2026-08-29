# V6.12 - Native Contractor Upload Panel

## Sửa lỗi
- Bỏ phụ thuộc vào nút tạo ticket + iframe đối với thao tác đính kèm của Nhà thầu.
- RFA/RFI/Shopdrawing/Hoàn công hiển thị khung mở rộng `Đính kèm file` dùng `st.file_uploader` native.
- File <= giới hạn legacy (mặc định 30 MB/file) tải trực tiếp từ app lên Google Drive.
- File lớn vẫn có link resumable Google Drive được chuẩn bị tự động.
- Hồ sơ bị trả về bắt buộc phát hiện file mới trước khi cho Lưu/Trình lại.
- Không thay đổi chuỗi Ban điều hành -> TVGS -> Ban QLDA.

## Lý do
Ở V6.9-V6.11, thao tác mở uploader còn phụ thuộc session ticket/iframe và rerun của Streamlit. Trên một số deployment Railway/trình duyệt, nút hiển thị nhưng iframe không mở. V6.12 dùng file uploader native làm đường chính nên thao tác chọn file luôn xuất hiện trong app.
