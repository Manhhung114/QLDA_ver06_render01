# V4.0.8 - AI Error Diagnostics

## Thay đổi chính

- Phân loại HTTP 429 `insufficient_quota` riêng với rate limit.
- Phân loại API key sai/401, permission/403, model/404, input quá lớn/400, timeout, network/SSL/DNS, 5xx.
- Nút **Kiểm tra AI** hiển thị trạng thái ngắn ngay trên Desktop.
- Streamlit có nút **Kiểm tra OpenAI API** tại **Cài đặt → AI**.
- Che API key/Bearer token khỏi thông báo lỗi.
- Không tự retry lỗi hết quota/credit.

## Tương thích

Giữ nguyên database và cấu hình của V4.0.7. Có thể copy `qlda_tiendo_v2.db` sang thư mục V4.0.8 hoặc chạy trực tiếp với database hiện có.
