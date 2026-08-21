# V6.0 - Tower folders, BBHT and filters

- Ẩn sheet VO khỏi Quản lý hồ sơ; dữ liệu VO cũ không bị xóa khỏi SQLite.
- Thêm sheet `Biên bản hiện trường` (`BBHT`).
- Chuẩn hóa mã hồ sơ/bản vẽ theo `THÁP-BỘMÔN-STT`, ví dụ `S2-MEP-001`.
- Google Drive tạo thư mục tổng theo tháp cho Hồ sơ/Bản vẽ:
  `QLDA Xây dựng / <Dự án> / Tháp S2 / 02_Ho_so|03_Ban_ve / <Loại> / <Mã>`.
- Tương thích file cũ: danh sách/đếm file vẫn kiểm tra cấu trúc Drive V6 cũ không có thư mục Tháp.
- Thêm bộ lọc trên mọi sheet Hồ sơ/Bản vẽ: từ khóa, Tháp, Bộ môn/Hệ, Trạng thái, Có file/Chưa có file.
- Khi mở danh sách tải xuống của các dòng đã tick, có thêm lọc theo tên file.
- Cột tick tiếp tục dùng chung cho Tải xuống và Xóa; chỉ Admin được xóa.
- Loại bỏ các trường Ghi chú khỏi giao diện web nghiệp vụ; dữ liệu cũ vẫn được giữ trong database.
