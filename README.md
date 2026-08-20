# QLDA Xây dựng V6.0 — Google Drive Direct Upload 2GB

> Bản V6.0: File Hồ sơ/Bản vẽ tải trực tiếp từ trình duyệt lên Google Drive bằng resumable upload, tối đa 2 GB/file. Không truyền file qua Streamlit/SQLite/Apps Script Base64. Xem `README_V5_0.md` và `DEPLOY_V5_0_STEP_BY_STEP.md`.

# QLDA Xây dựng V4.1.1 — Drive Only

## V4.1.1 — Google Drive tự tạo + tự phân file + RBAC, không Google Cloud Console
- Streamlit không dùng Google OAuth Client, Service Account hay Google Cloud Console.
- Dùng Google Apps Script Web App trong `google_drive_appscript/Code.gs` làm cổng Drive.
- Tự tạo thư mục `QLDA Xây dựng` trên My Drive của chủ Apps Script.
- File hồ sơ/bản vẽ tự phân theo Dự án → Nhóm → Loại → Mã hồ sơ/bản vẽ.
- File trùng tên tự đưa bản cũ vào `_Lich_su`.
- Phân quyền app: Chỉ đọc / Cập nhật / Admin; đồng thời chia sẻ thư mục Drive Viewer/Editor tương ứng.
- Xem `README_V4_1_1_DRIVE_ONLY.md` để triển khai từng bước.

## V4.0.9 - Đồng bộ Thư Viện Pháp Luật
- Thêm nút **📚 Cập nhật TVPL** và đưa TVPL vào **Cập nhật tất cả**.
- Tìm theo nhiều nhóm nghiệp vụ QLDA XD, chống trùng, enrich metadata có giới hạn.
- TVPL luôn là **nguồn tham khảo**; ưu tiên đối chiếu cùng số hiệu với nguồn chính thức trong database.
- Giữ toàn bộ chẩn đoán OpenAI API của V4.0.8 và các tính năng trước.

## V4.0.8 - Chẩn đoán lỗi OpenAI API

- Nút **Kiểm tra AI** phân biệt: hoạt động, hết quota/credit, rate limit, API key sai, thiếu quyền/model, timeout/mạng và lỗi dịch vụ.
- `insufficient_quota` được giải thích bằng tiếng Việt và **không retry vô ích**.
- Thông báo lỗi không hiển thị API key; key/Bearer token được che trước khi đưa lên giao diện.
- Desktop hiển thị trạng thái nhanh ngay cạnh nút Kiểm tra AI.
- Streamlit có nút **🩺 Kiểm tra OpenAI API** trong sheet **⚙ Cài đặt → AI**.
- Giữ nguyên toàn bộ V4.0.7: tiến độ, ngày trễ, hồ sơ, bản vẽ, báo cáo, văn bản online, Google/trang chỉ định, AI và Cài đặt tập trung.

## V4.0.7 - Sheet Cài đặt tập trung
- Thêm sheet cấp 1 **⚙ Cài đặt** trên Desktop và Streamlit.
- Cấu hình OpenAI API/model/Web Search được chuyển khỏi sheet Trợ lý AI.
- Cấu hình Google API key/CX được chuyển khỏi sheet Văn bản.
- Danh sách website cho nút **Tìm trang chỉ định** có thể thêm/xóa ngay trên giao diện, không cần sửa code.
- Desktop lưu cấu hình tại `~/.qlda_xaydung/app_settings.json` (ngoài project/GitHub).
- Streamlit ưu tiên **Secrets**; cài đặt nhập tay chỉ giữ trong session.
- Tự di chuyển cấu hình Google cũ từ `google_search.json` khi có.

## V4.0.6 - Google Search Integration

Sheet **Văn bản QLDA XD** có tìm kiếm Google/web rộng. App không còn tự thêm `site:` để giới hạn vào các cổng đã chỉ định. Các nguồn chính thức chỉ được ưu tiên xếp hạng.

- Desktop: cấu hình tại **⚙ Cài đặt → Google Search**, hoặc dùng **Mở Google toàn web** mà không cần API.
- Streamlit: cấu hình `GOOGLE_SEARCH_API_KEY` và `GOOGLE_SEARCH_CX` trong Secrets.
- Nếu Google API không có, app tự fallback sang engine tìm kiếm rộng hiện có.
- Với TCVN/QCVN, VSQI vẫn được tra cứu trực tiếp và ghép vào kết quả.

**Lưu ý chính sách Google 2026:** Custom Search JSON API đã đóng cho khách hàng mới; khách hàng hiện hữu có thời hạn chuyển đổi đến 01/01/2027. Công cụ tìm kiếm mới của Google cũng không còn chế độ full-web như trước. Vì vậy nút **Mở Google toàn web** là cách không cần API để sử dụng Google Search trực tiếp; việc nhập kết quả Google tự động vào app cần API/CX hợp lệ.

Xem `README_GOOGLE.md` để cấu hình.

# QLDA Xây dựng V4.0.4 AI

## V4.0.4 - Tìm kiếm online tổng hợp

Ô tra cứu trong **Văn bản QLDA XD** không còn giới hạn TCVN. Có thể nhập số hiệu hoặc câu mô tả như `Thông tư 06/2021/TT-BXD phân cấp công trình xây dựng`, `TCVN 5575`, `QCVN 06`. App tìm trên web đã được công cụ tìm kiếm lập chỉ mục, ưu tiên các nguồn chính thức và lưu metadata/link để mở kiểm tra.

> Lưu ý: "toàn web" nghĩa là các trang đã được công cụ tìm kiếm lập chỉ mục, không thể bảo đảm bao phủ 100% mọi trang trên Internet. Kết quả pháp lý phải được kiểm tra tại nguồn gốc trước khi áp dụng.

# QLDA Xây dựng V4.0.2 AI

**Hotfix online văn bản:** nguồn CSDL VBPL Bộ Xây dựng có thể trả HTTP 403 cho request tự động. V4.0.2 ưu tiên VBPL; nếu bị 403/không có dữ liệu, app tự chuyển sang **Hệ thống văn bản Cổng TTĐT Chính phủ** (nguồn chính thức), sau đó tiếp tục đồng bộ.

## Hotfix V4.0.2 - TCVN/Bộ Xây dựng

- TCVN được đồng bộ theo các nhóm ICS xây dựng chính thức trên VSQI (91.040, 91.060, 91.080, 91.100, 91.120, 91.140, 91.160, 91.200, 93.010, 93.020, 13.220, 23.120), tránh lỗi 0 bản ghi do lọc từ khóa.
- Văn bản pháp lý: VBPL -> Cổng Bộ Xây dựng -> Cổng Chính phủ.
- Dự thảo BXD dùng `www.moc.gov.vn`, quét các nhóm chuyên ngành xây dựng; nếu máy Windows báo lỗi chuỗi chứng thư, chỉ riêng tên miền chính thức `moc.gov.vn` mới được fallback TLS.
- Thêm `certifi` vào requirements.

**Mới trong V4.0:** thêm sheet **🤖 Trợ lý AI** gồm Chat với dự án, phân tích rủi ro tiến độ, dự thảo báo cáo, đọc/tóm tắt hồ sơ đính kèm và AI tra cứu văn bản. Xem `README_AI.md` để cấu hình OpenAI API.


Ứng dụng desktop quản lý dự án xây dựng bằng Python + PySide6 + SQLite.

## Cấu trúc V3.5

### Sheet 1 - Quản lý tiến độ
Giữ nguyên chức năng V3/V2.3:
- Quản lý nhiều dự án.
- Liên kết và đồng bộ Microsoft Project `.mpp` qua COM trên Windows.
- WBS, Task ID, Unique ID, Start, Finish, Duration.
- Baseline Start/Finish, Predecessor, Resources, Critical, Total Slack.
- Gantt Chart.
- Nhập trực tiếp `TT %` để so sánh với `KH %` và tự báo Nhanh/Đúng/Chậm.
- TT% nhập tay được giữ khi đồng bộ lại MPP.
- Nhập/xuất Excel.

### Sheet 2 - Quản lý hồ sơ
Có 4 sheet nhỏ:
- NCR
- RFA
- RFI
- VO
- Hồ sơ nghiệm thu công việc (NTCV)
- Hồ sơ nghiệm thu vật liệu đầu vào (NTVL)
- Hồ sơ kiểm định vật tư (KDVT)

Mỗi loại hồ sơ có trạng thái, hạn xử lý, WBS/Task liên quan, cảnh báo quá hạn và file đính kèm. VO có thêm giá trị phát sinh và ảnh hưởng tiến độ.

### Sheet 3 - Quản lý bản vẽ
Có 4 sheet nhỏ:

#### 1. Shopdrawing
Theo dõi bản vẽ shopdrawing theo mã, tên, bộ môn, revision, ngày nhận, trạng thái và file.

#### 2. BV phát hành TKTC
Quản lý bản vẽ phát hành thiết kế thi công chính thức, gồm ngày nhận, ngày phát hành, revision và file phát hành.

#### 3. BV cập nhật
Theo dõi các bản vẽ/revision cập nhật và bản vẽ thay thế.

#### 4. BV hoàn công
Quản lý bản vẽ hoàn công theo mã bản vẽ, khu vực/hệ thống, revision, ngày nhận, trạng thái kiểm tra và file hoàn công đính kèm.

### Trường dữ liệu bản vẽ
- Mã bản vẽ.
- Tên bản vẽ.
- Bộ môn/Hệ.
- Revision.
- Đơn vị phát hành.
- Người nhận.
- **Ngày nhận**.
- Ngày phát hành.
- Trạng thái.
- WBS/Task liên quan.
- Tham chiếu / bản vẽ bị thay thế.
- Số file đính kèm.
- **Cập nhật file gần nhất**.
- Ghi chú.

### File đính kèm bản vẽ
Mỗi bản vẽ có thể gắn nhiều file như PDF, DWG, DXF, IFC, RVT, Excel, Word, ZIP/RAR...

Nút **Cập nhật file** cho phép:
- thêm file/revision mới;
- bỏ file cũ khỏi danh sách;
- mở file hiện có;
- tự ghi thời gian cập nhật file gần nhất vào cột `Cập nhật file`.

Bản Desktop V3.5 hiện lưu đường dẫn tới file gốc. Vì vậy không nên di chuyển/xóa file gốc sau khi đính kèm.

## Dữ liệu SQLite
V3.5 sử dụng các bảng:
- `drawings`
- `drawing_attachments`

Dữ liệu bản vẽ được liên kết theo `project_id`. Khi chuyển dự án ở bất kỳ sheet nào, lựa chọn dự án được đồng bộ giữa Tiến độ, Hồ sơ và Bản vẽ.

Khóa chống trùng bản vẽ là:
`project_id + loại bản vẽ + mã bản vẽ + revision`.

## Tệp chính
- `main.py`: app chính + quản lý tiến độ + tích hợp 3 sheet cấp 1.
- `document_manager.py`: NCR/RFA/RFI/VO/NTCV/NTVL/KDVT.
- `drawing_manager.py`: Shopdrawing/BV phát hành TKTC/BV cập nhật/BV hoàn công.
- `mpp_reader.py`: đọc Microsoft Project qua COM.
- `test_project_com.py`: kiểm tra COM.
- `requirements.txt`: thư viện.
- `run_windows.bat`: cài và chạy app trên Windows.

## Cài đặt
Windows + Python 3.10+:

```bat
run_windows.bat
```

Hoặc:

```bash
python -m pip install -r requirements.txt
python main.py
```

## Nâng từ V3
Nếu V3 cũ đã có dữ liệu trong `qlda_tiendo_v2.db`, hãy sao chép file database đó vào thư mục V3.5 trước khi chạy. V3.5 tự tạo/giữ các bảng bản vẽ mà không xóa bảng tiến độ/hồ sơ cũ.

### Sheet 4 - 📊 Báo cáo trực quan
- KPI phần trăm: KH trung bình, TT trung bình, công việc chậm, công việc hoàn thành.
- % hồ sơ đã xử lý toàn dự án.
- % bản vẽ đã chấp thuận toàn dự án.
- Đồ thị so sánh KH% và TT%.
- Biểu đồ cơ cấu trạng thái tiến độ.
- Đồ thị % xử lý theo từng loại hồ sơ: NCR, RFA, RFI, VO, NTCV, NTVL, KDVT.
- Đồ thị % chấp thuận theo Shopdrawing, BV phát hành TKTC, BV cập nhật, BV hoàn công.
- Báo cáo tự đồng bộ theo dự án đang chọn; bấm **Làm mới báo cáo** để nạp số liệu mới nhất.


## V3.6 - Ngày trễ tiến độ
- Cột **Ngày trễ** nằm ngay sau **Trạng thái**.
- Nếu TT < 100% và đã vượt ngày Kết thúc: `Ngày trễ = Ngày báo cáo/hiện tại - Ngày Kết thúc`.
- Khi TT đạt 100%: trạng thái là **Hoàn thành**. Nếu hoàn thành sau hạn, số ngày trễ được khóa tại ngày lần đầu đạt 100%.
- Database tự migration thêm `actual_update_date` và `actual_finish_date`, không làm mất dữ liệu cũ.

## V3.7 - Văn bản QLDA Xây dựng

Bổ sung sheet **📚 Văn bản QLDA XD** cho cả Desktop và Streamlit:
- Luật / Nghị định / Thông tư / Quyết định / Nghị quyết
- QCVN / TCVN
- Dự thảo tiêu chuẩn, quy chuẩn và văn bản liên quan
- Cập nhật online từ nguồn chính thức, lọc hiệu lực, tìm kiếm, mở nguồn, xuất Excel
- Tra cứu trực tiếp TCVN trên VSQI
- GitHub Actions tạo cache online hàng ngày cho bản Streamlit Community Cloud

App chỉ lưu metadata/số hiệu/trạng thái/liên kết; không nhúng toàn văn TCVN có bản quyền.

## V4.0.6 - Tìm kiếm các trang chỉ định

- Bổ sung `thuvienphapluat.vn` vào nguồn tra cứu tham khảo về văn bản QLDA xây dựng.
- Thêm nút **Tìm trang chỉ định** trên Desktop và Streamlit.
- Danh sách domain được cấu hình tại `SPECIFIED_SEARCH_DOMAINS` trong `legal_documents.py`.
- Thư Viện Pháp Luật được đánh dấu **nguồn tham khảo**, không thay thế việc đối chiếu văn bản từ cơ quan ban hành/CSDL chính thức.

### Danh sách trang chỉ định mặc định
`SPECIFIED_SEARCH_DOMAINS` hiện gồm Cổng Chính phủ, Công báo, CSDL VBPL, Bộ Xây dựng, VSQI và `thuvienphapluat.vn`. Nút **Tìm trang chỉ định** chạy truy vấn `site:` riêng cho từng domain, đồng thời tra cứu trực tiếp Thư Viện Pháp Luật để tăng khả năng tìm thấy văn bản.
