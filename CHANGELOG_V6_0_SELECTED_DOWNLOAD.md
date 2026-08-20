# V6.0 Render — tải xuống bản vẽ đã chọn

- Cột `Chọn` nằm trước ID được dùng cho cả tải xuống và xóa.
- Chỉ đọc / Cập nhật / Admin đều có thể tick bản vẽ và bấm `⬇️ Tải bản vẽ đã chọn`.
- Sau khi bấm tải, app đọc file hiện hành trực tiếp từ Google Drive theo từng bản vẽ và hiển thị nút `⬇️ Tải xuống` cho từng file.
- File tải trực tiếp từ Google Drive, không đi qua RAM/disk của Render; phù hợp file lớn tới 2 GB.
- Nếu một bản vẽ có nhiều file, tất cả file hiện hành đều được liệt kê.
- Admin vẫn có nút `🗑 Xóa bản vẽ đã chọn`; Cập nhật/Chỉ đọc không được xóa.
- Giữ nguyên cột File DB `✅ Có file (n)`.
- Không cần thay Code.gs/Google Apps Script cho thay đổi này.
