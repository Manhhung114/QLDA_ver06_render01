# V6.0 – Nhật ký công trường + xem nhanh bản vẽ mobile

- Thêm main sheet **Báo cáo nhật ký công trường**.
- Kỹ sư hiện trường có thể chụp ảnh trực tiếp bằng `st.camera_input` trên điện thoại.
- Ghi nhận tiến độ %, thời tiết, tình trạng vật tư, sự cố/trở ngại và biện pháp xử lý.
- Ảnh chụp hiện trường được lưu vào Google Drive theo mã `S2-MEP-xxx`, cùng cấu trúc Tháp.
- Tài liệu lớn vẫn dùng direct/resumable upload; file lớn không đi qua Streamlit/Render.
- Bổ sung **Lọc file cần xem** cho khung đính kèm ở mọi sheet.
- Bổ sung **Xem nhanh**: PDF/ảnh mở Drive preview, CAD/BIM mở Drive viewer trong trình duyệt, không tải bytes qua Render.
- Ẩn toàn bộ dòng `caption/ghi chú` trên giao diện để tối ưu màn hình điện thoại.
- Nhật ký có bộ lọc: tìm kiếm, Tháp, Bộ môn, Thời tiết, Sự cố, Có/Chưa có file.
- Dấu tick nhật ký dùng chung cho tải xuống; xóa vẫn chỉ Admin.

## Camera on-demand patch
- Camera mặc định đóng, không khởi tạo `st.camera_input` khi mở sheet.
- Chỉ khi nhấn **📷 Mở camera** mới tạo camera và yêu cầu quyền camera trên thiết bị.
- Có nút **✖ Đóng camera** để tắt camera.
- Ảnh đã chụp chỉ được xử lý khi bấm **💾 Lưu nhật ký** hoặc **📎 Đính kèm file**.
