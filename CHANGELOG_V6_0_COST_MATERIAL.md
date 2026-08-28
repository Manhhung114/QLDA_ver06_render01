# V6.0 - Cost & Material Management

Bổ sung 6 sheet nghiệp vụ:

## Quản lý chi phí
- Chi phí dự toán (BOQ & BAC)
- Thanh toán & giải ngân
- Chi phí phát sinh (VO)

## Vật tư & thiết bị
- Danh mục vật tư/thiết bị (BOM)
- Tiến độ mua sắm & cung ứng
- Nhập - Xuất - Tồn & Kiểm định

Mọi sheet liên kết Snapshot tiến độ bằng `[TASK:ID/WBS]`. Procurement tự cảnh báo ngày giao hàng trễ so với ngày bắt đầu Task. Dữ liệu mới được đưa vào Snapshot AI cho OpenAI/Gemini. Database SQLite tự tạo bảng mới, không xóa dữ liệu cũ.
