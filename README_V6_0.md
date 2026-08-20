# QLDA Xây dựng V6.0 — Inline Google Drive Attachments

V6.0 kế thừa V5.0 nhưng đơn giản hóa thao tác file:

1. Mở một hồ sơ/bản vẽ hoặc nhập bản ghi mới.
2. Nút **📎 Đính kèm file** nằm ngay cạnh **💾 Cập nhật / Lưu mới**.
3. Bấm **Đính kèm file**. Với bản ghi mới, ứng dụng tự lưu thông tin trước để tạo đích lưu trữ.
4. Uploader Google Drive xuất hiện ngay trong trang. Chọn một hoặc nhiều file; V6 tự bắt đầu resumable upload, tối đa 2 GB/file.
5. Khi uploader báo hoàn thành, bấm **Cập nhật** để chốt thông tin và làm mới danh sách file.
6. Mỗi file có **Mở** và **Tải xuống**. Admin có thể tick nhiều file rồi xóa tập trung.

## Phân quyền

| Role | Xem | Cập nhật | Upload | Download | Xóa |
|---|---:|---:|---:|---:|---:|
| Chỉ đọc | ✅ | ❌ | ❌ | ✅ | ❌ |
| Cập nhật | ✅ | ✅ | ✅ | ✅ | ❌ |
| Admin | ✅ | ✅ | ✅ | ✅ | ✅ |

Google Drive của user `update` vẫn chỉ được Viewer; thao tác upload thực hiện qua Gateway. Vì vậy user update không thể vào Drive và xóa thủ công.

## Các sheet dùng đính kèm Drive

- Hồ sơ: NCR, RFA, RFI, VO, NTCV, NTVL, KDVT.
- Bản vẽ: SHOPDRAWING, ISSUED_DESIGN, UPDATED, AS_BUILT.

## File lớn

Uploader dùng chunk thích nghi 2 MiB → 1 MiB → 512 KiB → 256 KiB khi kênh Apps Script không nhận đủ byte. Mỗi file tối đa 2 GiB theo giới hạn ứng dụng.
