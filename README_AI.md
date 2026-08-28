# QLDA Xây dựng V4.1.0 AI

## V4.0.8 - Chẩn đoán API

Khi bấm **Kiểm tra AI**, app thực hiện một request rất nhỏ và phân loại lỗi thành:

- `✅ OPENAI API HOẠT ĐỘNG`
- `⚠️ API key hợp lệ nhưng đã hết quota/credit` (`insufficient_quota`)
- `⏱️ Đang chạm giới hạn tốc độ API`
- `❌ API key không hợp lệ hoặc đã bị thu hồi`
- `🔒 API key không có quyền thực hiện yêu cầu`
- `🧩 Model không tồn tại hoặc Project chưa được cấp quyền`
- `🌐 Không kết nối được / timeout`
- `🛠️ Dịch vụ OpenAI lỗi tạm thời`

App không tự retry khi `insufficient_quota`; cần xử lý Billing/Usage Limits trước.


V4.0 bổ sung sheet **🤖 Trợ lý AI** cho cả Desktop và Streamlit Community Cloud. Toàn bộ chức năng quản lý của V3.7 vẫn được giữ nguyên.

## 5 chức năng AI đầu tiên

1. **Chat với dự án**: AI nhận snapshot có kiểm soát từ SQLite gồm tiến độ, hồ sơ, bản vẽ và metadata văn bản. Có thể hỏi: công việc nào trễ nhất, RFI nào quá hạn, VO nào có time impact, bản vẽ nào chưa chấp thuận...
2. **Phân tích rủi ro tiến độ**: xếp hạng công việc theo ngày trễ, Critical, Slack và chênh lệch TT-KH; AI tạo nhận xét và đề xuất hành động 7 ngày tới.
3. **Dự thảo báo cáo tuần/tháng**: tự tổng hợp KPI, công việc rủi ro, hồ sơ, bản vẽ và action list.
4. **Đọc/tóm tắt hồ sơ đính kèm**: chọn file đã lưu trong hồ sơ hoặc upload file cho AI; AI tóm tắt, trích dữ liệu quan trọng, điểm cần kiểm tra. V4.0 giới hạn 25 MB/file.
5. **AI tra cứu văn bản QLDA**: ưu tiên kho `legal_documents` đã cập nhật online; có tùy chọn Web Search khi cần kiểm tra thêm nguồn online. AI phải phân biệt metadata và nội dung toàn văn.

> AI **không tự phê duyệt** bản vẽ, nghiệm thu, đóng NCR/RFI/RFA/VO hoặc đưa ra quyết định thay PM/kỹ sư. Kết quả AI là dự thảo/đề xuất để người dùng kiểm tra.

## Cấu hình OpenAI API

### Desktop Windows

Cách 1 (Desktop): nhập API key tại **⚙ Cài đặt → AI**. Cấu hình được lưu ngoài project tại `~/.qlda_xaydung/app_settings.json`. Có thể dùng biến môi trường thay vì lưu key cục bộ.

Cách 2: cấu hình biến môi trường:

```bat
set OPENAI_API_KEY=sk-...
set OPENAI_MODEL=gpt-5-mini
python main.py
```

### Streamlit Community Cloud

Không commit API key lên GitHub. Vào **App settings → Secrets** và thêm:

```toml
OPENAI_API_KEY = "sk-..."
OPENAI_MODEL = "gpt-5-mini"
```

Sau khi Save, app sẽ tự rerun/redeploy. Có thể nhập key trực tiếp trong tab AI để thử, nhưng Secrets là phương án phù hợp cho triển khai lâu dài.

## OpenAI API

V4.0 dùng SDK `openai` và **Responses API**. Các request được đặt `store=False` trong code. Model mặc định là `gpt-5-mini`, có thể đổi qua biến `OPENAI_MODEL` hoặc **⚙ Cài đặt → AI**.

API key/billing của OpenAI API là phần cấu hình riêng của ứng dụng; app vẫn chạy bình thường khi không có API key, chỉ các nút AI bị thiếu kết nối.

## Dữ liệu gửi cho AI

- Chat/Risk/Report: chỉ gửi snapshot rút gọn từ dự án, không tự gửi toàn bộ file đính kèm.
- Đọc hồ sơ: chỉ gửi file mà người dùng chủ động chọn.
- Legal AI: gửi metadata văn bản phù hợp; khi bật Web Search, model có thể tra cứu web.
- Không gửi `OPENAI_API_KEY` vào prompt.

## File mới

- `ai_service.py`: OpenAI client + xây dựng context dự án + phân tích file.
- `ai_manager.py`: giao diện AI cho PySide6 Desktop.
- `README_AI.md`: hướng dẫn cấu hình AI.

## Cài đặt

Desktop:

```bat
pip install -r requirements_desktop.txt
python main.py
```

Streamlit:

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## V6.0 — OpenAI + Google Gemini

Ứng dụng hỗ trợ chọn một trong hai nhà cung cấp AI tại **⚙ Cài đặt → AI**:

- OpenAI: `OPENAI_API_KEY`, `OPENAI_MODEL`
- Google Gemini: `GEMINI_API_KEY`, `GEMINI_MODEL`
- Nhà cung cấp mặc định khi deploy: `AI_PROVIDER=openai` hoặc `AI_PROVIDER=gemini`
- Tìm kiếm web cho phần pháp lý: `AI_WEB_SEARCH=true|false`

Cấu hình mẫu cho Railway/Render:

```env
AI_PROVIDER=gemini
GEMINI_API_KEY=YOUR_KEY
GEMINI_MODEL=gemini-2.5-flash
AI_WEB_SEARCH=true
```

Gemini dùng SDK `google-genai`. Chức năng Chat dự án, phân tích rủi ro, soạn báo cáo, đọc file và tra cứu văn bản dùng chung snapshot/luật an toàn với OpenAI.

