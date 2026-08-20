# V4.0.9 - Thư Viện Pháp Luật Sync

## Mới
- Nút **📚 Cập nhật TVPL** trong sheet Văn bản QLDA XD.
- **Cập nhật tất cả** nay chạy: VBPL/Chính phủ → VSQI → Dự thảo BXD → TVPL.
- TVPL tìm theo bộ từ khóa nghiệp vụ QLDA xây dựng: QLDA, chất lượng, thi công, nghiệm thu, phân cấp, hợp đồng, chi phí, định mức, an toàn, PCCC, vật liệu, QCVN/TCVN, nhà ở và quy hoạch.
- Fallback site-search qua Google API/Bing/DuckDuckGo khi trang tìm trực tiếp TVPL trả ít kết quả.
- Chống trùng theo số hiệu → URL → tiêu đề.
- Enrich có giới hạn từ trang chi tiết để lấy loại văn bản, cơ quan, ngày ban hành/hiệu lực khi truy cập được.
- Đối chiếu số hiệu TVPL với nguồn chính thức đã có trong database và ghi chú kết quả đối chiếu.

## Nguyên tắc nguồn
TVPL được gắn trạng thái **Nguồn tham khảo TVPL - cần đối chiếu nguồn chính thức**. App chỉ lưu metadata và link; không sao chép toàn văn.

## Tương thích
Dùng trực tiếp database V4.0.8/V4.0.7. Không cần migration mới.
