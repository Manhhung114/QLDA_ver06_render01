from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Signal, QUrl, Qt
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QPushButton, QLineEdit,
    QTextEdit, QCheckBox, QTabWidget, QMessageBox, QFileDialog, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
)

from settings_store import (
    APP_SETTINGS_FILE, CONFIG_DIR, DEFAULT_SPECIFIED_SEARCH_DOMAINS,
    load_app_settings, save_app_settings
)
from google_drive_service import (
    DRIVE_CLIENT_FILE, copy_oauth_client_json, disconnect_desktop_drive,
    extract_drive_id, drive_role_label, GoogleDriveService, GoogleDriveError
)


class SettingsPage(QWidget):
    settingsChanged = Signal()

    def __init__(self, db_path: str | Path, parent=None):
        super().__init__(parent)
        self.db_path = Path(db_path)
        self.drive_service = None
        self.drive_identity = None
        self.drive_root = None
        self.build_ui()
        self.load_values()

    def build_ui(self):
        root = QVBoxLayout(self); root.setContentsMargins(12, 10, 12, 10); root.setSpacing(10)
        title = QLabel("⚙ CÀI ĐẶT ỨNG DỤNG"); title.setObjectName("pageTitle")
        sub = QLabel("AI • Google Search • Google Drive • phân quyền • website tra cứu • hệ thống.")
        sub.setObjectName("subtitle"); sub.setWordWrap(True)
        root.addWidget(title); root.addWidget(sub)

        self.tabs = QTabWidget(); root.addWidget(self.tabs, 1)
        self._build_ai(); self._build_google(); self._build_drive(); self._build_sites(); self._build_system()

        row = QHBoxLayout(); row.addStretch()
        self.btn_reload = QPushButton("↻ Nạp lại"); self.btn_reload.clicked.connect(self.load_values)
        self.btn_save = QPushButton("💾 Lưu tất cả cài đặt"); self.btn_save.clicked.connect(self.save_values)
        row.addWidget(self.btn_reload); row.addWidget(self.btn_save); root.addLayout(row)

    def _build_ai(self):
        page = QWidget(); form = QFormLayout(page)
        info = QLabel("OpenAI API key được lưu trong thư mục cấu hình người dùng, không nằm trong project/GitHub. Biến môi trường OPENAI_API_KEY/OPENAI_MODEL vẫn được ưu tiên nếu có.")
        info.setWordWrap(True); form.addRow(info)
        self.openai_key = QLineEdit(); self.openai_key.setEchoMode(QLineEdit.EchoMode.Password); self.openai_key.setPlaceholderText("sk-...")
        self.openai_model = QLineEdit(); self.openai_model.setPlaceholderText("gpt-5-mini")
        self.openai_web = QCheckBox("Cho phép Web Search khi AI tra cứu pháp lý")
        diag = QLabel("Nút Kiểm tra AI ở sheet Trợ lý AI sẽ chẩn đoán riêng: API key • quota/credit • rate limit • quyền model • mạng/timeout.")
        diag.setWordWrap(True)
        form.addRow("OpenAI API key", self.openai_key); form.addRow("Model", self.openai_model); form.addRow("", self.openai_web); form.addRow("Chẩn đoán", diag)
        self.tabs.addTab(page, "🤖 AI")

    def _build_google(self):
        page = QWidget(); form = QFormLayout(page)
        info = QLabel("Google Search API/CX dùng cho tìm kiếm tự động. Đây là cấu hình tìm kiếm web, tách biệt với Google Drive bên cạnh.")
        info.setWordWrap(True); form.addRow(info)
        self.google_key = QLineEdit(); self.google_key.setEchoMode(QLineEdit.EchoMode.Password); self.google_key.setPlaceholderText("Google API key")
        self.google_cx = QLineEdit(); self.google_cx.setPlaceholderText("Search Engine ID (CX)")
        form.addRow("Google API key", self.google_key); form.addRow("Search Engine ID (CX)", self.google_cx)
        self.tabs.addTab(page, "🔎 Google Search")

    def _build_drive(self):
        page = QWidget(); root = QVBoxLayout(page)
        note = QLabel(
            "Lưu tệp Hồ sơ/Bản vẽ trên Google Drive và dùng ACL Drive để phân quyền. "
            "Chỉ đọc=Viewer • Cập nhật=Editor/Contributor • Admin=Owner (My Drive) hoặc Manager (Shared Drive)."
        )
        note.setWordWrap(True); root.addWidget(note)

        form = QFormLayout()
        self.drive_enabled = QCheckBox("Bật Google Drive làm kho lưu trữ/phân quyền")
        self.drive_auto_upload = QCheckBox("Tự upload tệp đính kèm Hồ sơ/Bản vẽ lên Google Drive")
        self.drive_client = QLineEdit(); self.drive_client.setReadOnly(True)
        b_client = QPushButton("Chọn OAuth JSON"); b_client.clicked.connect(self.choose_drive_client)
        client_row = QHBoxLayout(); client_row.addWidget(self.drive_client, 1); client_row.addWidget(b_client)
        self.drive_root_name = QLineEdit(); self.drive_root_name.setPlaceholderText("QLDA Xây dựng")
        self.drive_root_input = QLineEdit(); self.drive_root_input.setPlaceholderText("Để trống để app tự tạo; hoặc dán URL/ID thư mục Drive")
        form.addRow("", self.drive_enabled); form.addRow("", self.drive_auto_upload)
        form.addRow("OAuth Client JSON", client_row)
        form.addRow("Tên thư mục gốc", self.drive_root_name)
        form.addRow("URL / ID thư mục gốc", self.drive_root_input)
        root.addLayout(form)

        btnrow = QHBoxLayout()
        self.btn_drive_connect = QPushButton("🔐 Kết nối Google"); self.btn_drive_connect.clicked.connect(self.connect_drive)
        self.btn_drive_refresh = QPushButton("↻ Kiểm tra quyền"); self.btn_drive_refresh.clicked.connect(self.refresh_drive_status)
        self.btn_drive_open = QPushButton("☁ Mở thư mục Drive"); self.btn_drive_open.clicked.connect(self.open_drive_folder)
        self.btn_drive_disconnect = QPushButton("Đăng xuất Drive"); self.btn_drive_disconnect.clicked.connect(self.disconnect_drive)
        for b in (self.btn_drive_connect, self.btn_drive_refresh, self.btn_drive_open, self.btn_drive_disconnect): btnrow.addWidget(b)
        btnrow.addStretch(); root.addLayout(btnrow)

        self.drive_status = QLabel("Chưa kết nối"); self.drive_status.setWordWrap(True); root.addWidget(self.drive_status)

        root.addWidget(QLabel("Phân quyền thư mục gốc"))
        self.perm_table = QTableWidget(0, 5)
        self.perm_table.setHorizontalHeaderLabels(["Tên", "Email", "Quyền Drive", "Quyền App", "Permission ID"])
        self.perm_table.setColumnHidden(4, True)
        self.perm_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.perm_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.perm_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        root.addWidget(self.perm_table, 1)

        prow = QHBoxLayout()
        self.perm_email = QLineEdit(); self.perm_email.setPlaceholderText("email@domain.com")
        self.perm_role = QComboBox(); self.perm_role.addItem("Chỉ đọc", "read"); self.perm_role.addItem("Cập nhật", "update"); self.perm_role.addItem("Admin", "admin")
        self.btn_perm_set = QPushButton("Thêm / đổi quyền"); self.btn_perm_set.clicked.connect(self.set_drive_permission)
        self.btn_perm_remove = QPushButton("Xóa quyền"); self.btn_perm_remove.clicked.connect(self.remove_drive_permission)
        prow.addWidget(QLabel("Email:")); prow.addWidget(self.perm_email, 1); prow.addWidget(self.perm_role); prow.addWidget(self.btn_perm_set); prow.addWidget(self.btn_perm_remove)
        root.addLayout(prow)
        warn = QLabel("My Drive chỉ có một Owner nên Admin thực sự là chủ sở hữu. Nếu cần nhiều Admin, dùng Google Workspace Shared Drive; app sẽ dùng role Manager (organizer).")
        warn.setWordWrap(True); root.addWidget(warn)
        self.tabs.addTab(page, "☁ Google Drive & quyền")

    def _build_sites(self):
        page = QWidget(); lay = QVBoxLayout(page)
        note = QLabel("Mỗi dòng là một domain. Nút “Tìm trang chỉ định” ở sheet Văn bản QLDA XD sẽ dùng danh sách này.")
        note.setWordWrap(True); lay.addWidget(note)
        self.sites_edit = QTextEdit(); self.sites_edit.setPlaceholderText("vanban.chinhphu.vn\nthuvienphapluat.vn\n...")
        lay.addWidget(self.sites_edit, 1)
        row = QHBoxLayout(); reset = QPushButton("Khôi phục danh sách mặc định"); reset.clicked.connect(lambda: self.sites_edit.setPlainText("\n".join(DEFAULT_SPECIFIED_SEARCH_DOMAINS)))
        row.addWidget(reset); row.addStretch(); lay.addLayout(row)
        self.tabs.addTab(page, "🌐 Website tra cứu")

    def _build_system(self):
        page = QWidget(); form = QFormLayout(page)
        self.db_label = QLabel(str(self.db_path)); self.cfg_label = QLabel(str(APP_SETTINGS_FILE))
        form.addRow("Database", self.db_label); form.addRow("File cài đặt", self.cfg_label)
        row = QHBoxLayout(); b1 = QPushButton("Mở thư mục cấu hình"); b1.clicked.connect(self.open_config_folder); b2 = QPushButton("Mở thư mục database"); b2.clicked.connect(self.open_db_folder)
        row.addWidget(b1); row.addWidget(b2); row.addStretch(); form.addRow(row)
        warn = QLabel("API key, OAuth token và credentials là dữ liệu nhạy cảm. Không đưa app_settings.json, google_drive_token.json hoặc OAuth JSON lên GitHub.")
        warn.setWordWrap(True); form.addRow(warn)
        self.tabs.addTab(page, "🗄 Hệ thống")

    def load_values(self):
        cfg = load_app_settings()
        self.openai_key.setText(str(cfg.get("openai_api_key", "")))
        self.openai_model.setText(str(cfg.get("openai_model", "gpt-5-mini")))
        self.openai_web.setChecked(bool(cfg.get("openai_web_search", False)))
        self.google_key.setText(str(cfg.get("google_api_key", "")))
        self.google_cx.setText(str(cfg.get("google_cx", "")))
        self.sites_edit.setPlainText("\n".join(cfg.get("specified_search_domains") or DEFAULT_SPECIFIED_SEARCH_DOMAINS))
        self.drive_enabled.setChecked(bool(cfg.get("drive_enabled", False)))
        self.drive_auto_upload.setChecked(bool(cfg.get("drive_auto_upload", False)))
        self.drive_client.setText(str(cfg.get("drive_client_credentials_path", "")))
        self.drive_root_name.setText(str(cfg.get("drive_root_folder_name", "QLDA Xây dựng")))
        self.drive_root_input.setText(str(cfg.get("drive_root_folder_url") or cfg.get("drive_root_folder_id") or ""))
        self.refresh_drive_status(silent=True)

    def save_values(self):
        domains = [x.strip() for x in self.sites_edit.toPlainText().splitlines() if x.strip()]
        root_value = self.drive_root_input.text().strip()
        root_id = extract_drive_id(root_value)
        current = load_app_settings()
        drive_payload = {
            "drive_enabled": self.drive_enabled.isChecked(),
            "drive_auto_upload": self.drive_auto_upload.isChecked(),
            "drive_client_credentials_path": self.drive_client.text().strip(),
            "drive_root_folder_id": root_id,
            "drive_root_folder_url": root_value if root_value.startswith("http") else "",
            "drive_root_folder_name": self.drive_root_name.text().strip() or "QLDA Xây dựng",
        }
        # Khi Drive RBAC đã bật, chỉ Admin được đổi/tắt cấu hình Drive qua UI.
        if current.get("drive_enabled"):
            try:
                rid = extract_drive_id(str(current.get("drive_root_folder_id") or current.get("drive_root_folder_url") or ""))
                ident = GoogleDriveService.desktop(interactive=False).current_identity(rid) if rid else None
                if ident and ident.role != "admin":
                    drive_payload = {k: current.get(k) for k in drive_payload}
            except Exception:
                # Không cho hạ quyền bằng cách tắt Drive khi trạng thái xác thực không rõ.
                drive_payload = {k: current.get(k) for k in drive_payload}
        path = save_app_settings({
            "openai_api_key": self.openai_key.text().strip(),
            "openai_model": self.openai_model.text().strip() or "gpt-5-mini",
            "openai_web_search": self.openai_web.isChecked(),
            "google_api_key": self.google_key.text().strip(),
            "google_cx": self.google_cx.text().strip(),
            "specified_search_domains": domains,
            **drive_payload,
        })
        self.settingsChanged.emit()
        QMessageBox.information(self, "Cài đặt", f"Đã lưu cài đặt tại:\n{path}")

    def choose_drive_client(self):
        path, _ = QFileDialog.getOpenFileName(self, "Chọn OAuth Client JSON của Google", "", "JSON (*.json)")
        if not path:
            return
        try:
            target = copy_oauth_client_json(path)
            self.drive_client.setText(str(target))
            QMessageBox.information(self, "Google Drive", f"Đã lưu OAuth Client tại:\n{target}")
        except Exception as exc:
            QMessageBox.warning(self, "Google Drive", str(exc))

    def connect_drive(self):
        try:
            self.drive_enabled.setChecked(True)
            root_value = self.drive_root_input.text().strip()
            root_id = extract_drive_id(root_value)
            svc = GoogleDriveService.desktop(interactive=True)
            root = svc.ensure_root_folder(root_id, self.drive_root_name.text().strip() or "QLDA Xây dựng")
            url = root.get("webViewLink") or f"https://drive.google.com/drive/folders/{root['id']}"
            save_app_settings({
                "drive_enabled": True,
                "drive_auto_upload": self.drive_auto_upload.isChecked(),
                "drive_root_folder_id": root["id"],
                "drive_root_folder_url": url,
                "drive_root_folder_name": root.get("name") or self.drive_root_name.text().strip() or "QLDA Xây dựng",
            })
            self.drive_root_input.setText(url)
            self.drive_service = svc; self.drive_root = root
            self.refresh_drive_status(silent=False)
            self.settingsChanged.emit()
        except Exception as exc:
            QMessageBox.critical(self, "Google Drive", str(exc))

    def refresh_drive_status(self, silent=False):
        cfg = load_app_settings()
        if not cfg.get("drive_enabled"):
            self.drive_status.setText("Google Drive đang tắt — app dùng lưu trữ local/SQLite như trước.")
            self.perm_table.setRowCount(0)
            return
        root_id = extract_drive_id(str(cfg.get("drive_root_folder_id") or cfg.get("drive_root_folder_url") or self.drive_root_input.text()))
        if not root_id:
            self.drive_status.setText("Đã bật Drive nhưng chưa có thư mục gốc. Bấm Kết nối Google để tạo/liên kết.")
            return
        try:
            svc = GoogleDriveService.desktop(interactive=False)
            root = svc.file_info(root_id)
            ident = svc.current_identity(root_id)
            self.drive_service = svc; self.drive_root = root; self.drive_identity = ident
            mode = "Shared Drive" if ident.shared_drive else "My Drive"
            self.drive_status.setText(
                f"✅ {mode} • {root.get('name','')} • {ident.email or 'Google'} • Quyền: {ident.label} ({drive_role_label(ident.drive_role)})\n"
                f"{root.get('webViewLink') or 'https://drive.google.com/drive/folders/'+root_id}"
            )
            self._fill_permissions(svc.permissions(root_id))
            is_admin = ident.role == "admin"
            self.btn_perm_set.setEnabled(is_admin); self.btn_perm_remove.setEnabled(is_admin)
            self.drive_enabled.setEnabled(is_admin)
            self.drive_auto_upload.setEnabled(is_admin)
            self.drive_root_input.setReadOnly(not is_admin)
            self.drive_root_name.setReadOnly(not is_admin)
        except Exception as exc:
            self.drive_status.setText(f"⚠ Không kết nối được Google Drive: {exc}")
            self.perm_table.setRowCount(0)
            if not silent:
                QMessageBox.warning(self, "Google Drive", str(exc))

    def _fill_permissions(self, perms):
        self.perm_table.setRowCount(len(perms))
        for r, p in enumerate(perms):
            drive_role = str(p.get("role") or "")
            app_role = "Admin" if drive_role in {"owner","organizer"} else ("Cập nhật" if drive_role in {"writer","fileOrganizer"} else "Chỉ đọc")
            vals = [p.get("displayName") or "", p.get("emailAddress") or p.get("type") or "", drive_role_label(drive_role), app_role, p.get("id") or ""]
            for c, v in enumerate(vals):
                self.perm_table.setItem(r, c, QTableWidgetItem(str(v)))

    def set_drive_permission(self):
        if not self.drive_service or not self.drive_root:
            self.refresh_drive_status();
            if not self.drive_service: return
        try:
            self.drive_service.set_user_role(self.drive_root["id"], self.perm_email.text().strip(), str(self.perm_role.currentData()))
            self.refresh_drive_status(silent=True)
            self.settingsChanged.emit()
        except Exception as exc:
            QMessageBox.warning(self, "Phân quyền Google Drive", str(exc))

    def remove_drive_permission(self):
        row = self.perm_table.currentRow()
        if row < 0:
            return
        perm_id_item = self.perm_table.item(row, 4)
        if not perm_id_item or not perm_id_item.text():
            return
        if QMessageBox.question(self, "Xác nhận", "Xóa quyền người dùng đang chọn khỏi thư mục Drive?") != QMessageBox.Yes:
            return
        try:
            self.drive_service.remove_user(self.drive_root["id"], perm_id_item.text())
            self.refresh_drive_status(silent=True); self.settingsChanged.emit()
        except Exception as exc:
            QMessageBox.warning(self, "Phân quyền Google Drive", str(exc))

    def open_drive_folder(self):
        cfg = load_app_settings(); url = str(cfg.get("drive_root_folder_url") or self.drive_root_input.text()).strip()
        rid = extract_drive_id(url)
        if not url.startswith("http") and rid:
            url = f"https://drive.google.com/drive/folders/{rid}"
        if url:
            QDesktopServices.openUrl(QUrl(url))

    def disconnect_drive(self):
        disconnect_desktop_drive(); self.drive_service = None; self.drive_identity = None
        self.drive_status.setText("Đã đăng xuất Google Drive. Cài đặt thư mục vẫn được giữ để đăng nhập lại.")
        self.perm_table.setRowCount(0); self.settingsChanged.emit()

    def open_config_folder(self):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True); QDesktopServices.openUrl(QUrl.fromLocalFile(str(CONFIG_DIR)))

    def open_db_folder(self):
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.db_path.parent)))
