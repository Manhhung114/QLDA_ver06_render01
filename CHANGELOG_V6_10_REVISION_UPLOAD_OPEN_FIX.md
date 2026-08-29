# V6.10 - Revision Upload Open Fix

## Lỗi sửa
Ở V6.9, khi hồ sơ đã bị Ban điều hành/TVGS/Ban QLDA trả về Nhà thầu, nút Đính kèm file có thể hiển thị nhưng uploader không xuất hiện sau thao tác nút trên một số trình duyệt/deployment Streamlit.

## Thay đổi
- Hồ sơ đang ở `current_stage=CONTRACTOR` tự tạo upload ticket khi Nhà thầu mở hồ sơ.
- Không còn phụ thuộc `button -> st.rerun() -> render iframe` để mở uploader.
- Nút ở vòng chỉnh sửa đổi thành `Tạo lại phiên đính kèm file` để cấp ticket mới thủ công khi cần.
- Luôn hiển thị link `Mở trình tải file ở tab riêng` trước iframe để có đường dự phòng khi trình duyệt chặn iframe.
- Ticket phía Streamlit có thời điểm phát hành; ticket gần/hết hạn được tự tạo lại.
- Vẫn snapshot danh sách file cũ và chỉ cho Lưu/Trình lại khi phát hiện file ID mới.
- Áp dụng chung cho RFA, RFI, SHOPDRAWING và AS_BUILT.
- Không thay đổi luồng: trả ở cấp nào thì sau khi Nhà thầu tải file mới + Lưu sẽ trình lại đúng cấp đó.
