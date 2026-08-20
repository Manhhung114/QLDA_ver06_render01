# V4.1.0 My Drive OAuth adjustment

- Streamlit Cloud bỏ service account/Shared Drive trong luồng mặc định.
- Google Web OAuth cho từng người dùng; token chỉ giữ trong session Streamlit.
- CSRF state được ký HMAC và có thời hạn.
- RBAC My Drive: Viewer→Read, Editor→Update, Owner→Admin.
- Nhận diện quyền My Drive bằng `ownedByMe` + `capabilities.canEdit`, hỗ trợ cả chia sẻ qua group/domain.
- Owner quản lý Viewer/Editor ngay trong sheet Cài đặt.
- Không tự transfer ownership khi chọn Admin; My Drive chỉ có một Owner.
- Khi RBAC bật mà Drive mất kết nối, upload không fallback local.
