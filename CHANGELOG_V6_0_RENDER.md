# V6.0 Render Edition

- Chuyển host Streamlit từ Community Cloud sang Render Web Service.
- Bổ sung Dockerfile với Java cho MPXJ/Microsoft Project.
- Bổ sung `render.yaml` production (Starter + Persistent Disk `/var/data`).
- Bổ sung `render-free.yaml` demo không persistent.
- Render Environment Variables được ưu tiên hơn `st.secrets`.
- SQLite mặc định trên Render: `/var/data/qlda_cloud.db`.
- SQLite bật WAL, busy_timeout 60s và synchronous=NORMAL.
- Giao diện Cài đặt hiển thị trạng thái Render/Persistent Disk.
- Google Drive direct upload 2GB và RBAC V6 giữ nguyên.
- TVPL clickable và các chức năng nghiệp vụ V6 giữ nguyên.
