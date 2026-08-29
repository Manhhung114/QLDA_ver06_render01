# V6.9 - Sửa tải lại file khi hồ sơ bị trả về

## Lỗi đã sửa
- Hồ sơ/bản vẽ đã bị Ban điều hành, TVGS hoặc Ban QLDA yêu cầu chỉnh sửa có thể mở lại nhưng nút **Đính kèm file** đôi khi không mở uploader mới.
- Nguyên nhân: vùng upload của vòng chỉnh sửa tái sử dụng session key/ticket của lần trình trước.
- Có thể vô tình bấm trình lại khi chưa tải file phiên bản mới vì hệ thống chỉ kiểm tra thư mục đã có file cũ.

## Điều chỉnh V6.9
1. Mỗi vòng chỉnh sửa có `panel_key` upload riêng theo workflow revision + cấp trả hồ sơ.
2. Khi bấm **Đính kèm file**, app luôn tạo ticket mới và `st.rerun()` ngay để hiển thị iframe/link uploader ổn định.
3. Trước khi mở uploader, app ghi snapshot các file ID hiện có; sau upload chỉ khi phát hiện file ID mới thì nút **Lưu hồ sơ/Lưu bản vẽ** mới được mở ở vòng chỉnh sửa.
4. Bỏ nút **Trình lại** riêng cho Nhà thầu. Luồng bắt buộc là:
   - Mở hồ sơ bị trả về
   - Cập nhật nội dung
   - Đính kèm file phiên bản mới
   - Bấm Lưu
   - Hệ thống tự trình lại đúng cấp đã trả hồ sơ.
5. File mới trùng tên file cũ được Apps Script tự đưa file cũ vào `_Lich_su`.
6. Áp dụng thống nhất cho toàn bộ đầu mục đang bật phê duyệt online:
   - RFA
   - RFI
   - Shopdrawing
   - Bản vẽ hoàn công (AS_BUILT)
7. Bản vẽ hoàn công được đưa vào cùng UI phân vai/phê duyệt online thay vì dùng form bản vẽ chung.

## Kiểm tra
- Python compile: OK.
- Bộ test workflow V6.1 -> V6.9 liên quan phê duyệt: 29/29 passed.
- Một số test legacy toàn project vẫn có lỗi/skip độc lập (COM trên Linux và các static test giao diện V6.0 cũ); không liên quan thay đổi V6.9.
