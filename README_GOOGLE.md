# Cấu hình Google Search cho QLDA V4.0.9

## 1. Hai chế độ Google

### A. Mở Google toàn web — không cần API
Nhập nội dung cần tìm và bấm **Mở Google toàn web**. App mở `google.com/search` bằng trình duyệt mặc định. Đây là Google Search thông thường và không bị app giới hạn domain.

### B. Lấy kết quả Google tự động vào app — cần API + CX
V4.0.9 hỗ trợ **Google Custom Search JSON API** chính thức. Cần:
- Google API key có quyền Custom Search JSON API
- Programmable Search Engine ID (`cx`)

Desktop: **⚙ Cài đặt → Google Search**. Cấu hình được lưu cục bộ tại `~/.qlda_xaydung/app_settings.json`, ngoài repository.

Streamlit: App Settings → Secrets:
```toml
GOOGLE_SEARCH_API_KEY = "YOUR_KEY"
GOOGLE_SEARCH_CX = "YOUR_CX"
```

## 2. Giới hạn của Google từ 2026
Google thông báo Custom Search JSON API đóng với khách hàng mới. Khách hàng hiện hữu có thể dùng đến 01/01/2027. Từ 20/01/2026, Programmable Search Engine mới phải dùng Sites to search (tối đa 50 domain); chế độ Search entire web chỉ còn cho engine cũ đã bật trước thời điểm chuyển đổi.

Vì vậy V4.0.9 không scrape HTML kết quả Google. Nếu không có API/CX hợp lệ, dùng **Mở Google toàn web** hoặc engine fallback của app.

## 3. Phạm vi tìm kiếm của app
App không tự thêm `site:...` vào truy vấn. Kết quả từ `gov.vn`, `vbpl.vn`, `vsqi.gov.vn`... chỉ được cộng điểm để xuất hiện cao hơn, nhưng kết quả từ các website khác vẫn được nhận.
