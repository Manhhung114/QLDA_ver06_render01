# QLDA Xây dựng V6.0

## Giao diện đính kèm file mới

- Nút **📎 Đính kèm file** nằm ngay bên cạnh **💾 Cập nhật / Lưu mới**.
- Khi bấm Đính kèm file, V6 lưu thông tin bản ghi trước để có mã đích, tạo ticket Drive và mở uploader ngay trong trang Streamlit.
- Uploader Google Apps Script cho phép chọn nhiều file, tối đa **2 GB/file**, dùng resumable upload/chunk thích nghi và tự bắt đầu tải sau khi chọn file.
- File không đi qua SQLite và không đi qua Python Streamlit server.
- Sau khi tải hoàn tất, bấm **Cập nhật** để chốt dữ liệu và làm mới danh sách file.

## Xóa file bằng tick

- Mỗi file Drive có ô tick **Xóa**.
- Admin tick một hoặc nhiều file và bấm **🗑 Xóa file đã chọn**.
- Quyền **Cập nhật** và **Chỉ đọc** không được xóa file; backend Apps Script vẫn bắt buộc role admin cho `trash_file`.

## Tải xuống

- Mỗi file có nút **⬇️ Tải xuống** và **☁ Mở**.
- Áp dụng đồng nhất cho: NCR, RFA, RFI, VO, NTCV, NTVL, KDVT, Shopdrawing, BV phát hành TKTC, BV cập nhật, BV hoàn công.

## Tương thích

- Giữ nguyên SQLite schema V5/V4; không xóa dữ liệu cũ.
- File legacy vẫn được hiển thị/tải xuống.
- `authorizeV50_()` được giữ làm alias cho `authorizeV60_()` để dễ nâng cấp Apps Script.
