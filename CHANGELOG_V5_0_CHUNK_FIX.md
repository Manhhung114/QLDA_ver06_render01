# V5.0 - Adaptive chunk transport fix

- Sửa lỗi `Chunk giữa phải là bội số 256 KiB`.
- Chunk mặc định giảm từ 4 MiB xuống 2 MiB để an toàn hơn qua `google.script.run`.
- Trình duyệt gửi thêm `expectedChunkSize`; Apps Script xác minh byte thực nhận trước khi gửi sang Google Drive.
- Nếu payload bị hụt, tự giảm chunk 2 MiB → 1 MiB → 512 KiB → 256 KiB và thử lại đúng offset.
- Chunk cuối vẫn được phép nhỏ hơn 256 KiB theo Google Drive resumable upload.
- Không gửi chunk sai kích thước vào Drive, tránh hỏng file.
