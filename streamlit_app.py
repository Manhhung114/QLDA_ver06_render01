from __future__ import annotations

import io
import os
import json
import sqlite3
import tempfile
import time
from datetime import date, datetime, timedelta
from pathlib import Path
from urllib.parse import quote_plus

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from cloud_db import CloudDatabase, progress_delta, planned_progress, calculate_delay_days
from mpp_cloud_reader import MppCloudError, read_mpp
from legal_documents import LegalRepository, sync_source, sync_all, search_vsqi, search_online_all, search_online_sites
from settings_store import DEFAULT_SPECIFIED_SEARCH_DOMAINS
from ai_service import AIServiceError, AISettings, OpenAIProjectAssistant, ProjectContextBuilder
from drive_gateway import DriveGateway, DriveGatewayError, config_from_streamlit

try:
    import plotly.express as px
except Exception:
    px = None

APP_DIR = Path(__file__).resolve().parent
DATA_DIR = APP_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
IS_RENDER = str(os.environ.get("RENDER", "")).strip().lower() == "true"
DEPLOY_PLATFORM = "Render" if IS_RENDER else "Streamlit/Local"
DEFAULT_DB_PATH = Path("/var/data/qlda_cloud.db") if IS_RENDER else (DATA_DIR / "qlda_cloud.db")
DB_PATH = Path(os.environ.get("QLDA_DB_PATH", str(DEFAULT_DB_PATH)))
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
LEGAL_CACHE_PATH = APP_DIR / "legal_cache.json"

# V4.0.8 - Google Search credentials on Streamlit are read from Secrets.
# Never commit these values to GitHub.
try:
    if "GOOGLE_SEARCH_API_KEY" in st.secrets:
        os.environ.setdefault("GOOGLE_SEARCH_API_KEY", str(st.secrets["GOOGLE_SEARCH_API_KEY"]))
    if "GOOGLE_SEARCH_CX" in st.secrets:
        os.environ.setdefault("GOOGLE_SEARCH_CX", str(st.secrets["GOOGLE_SEARCH_CX"]))
except Exception:
    pass

DOC_CONFIG = {
    "NCR": {
        "title": "NCR - Non-Conformance Report",
        "statuses": ["Mở", "Đang khắc phục", "Chờ kiểm tra", "Đóng", "Hủy"],
        "done_statuses": ["Đóng", "Hủy"],
        "subject": "Nội dung không phù hợp",
        "code_label": "Mã NCR *",
        "issuer_label": "Người phát hành / trình",
        "assignee_label": "Người / Đơn vị xử lý",
        "response_label": "Biện pháp khắc phục / Kết quả",
    },
    "RFA": {
        "title": "RFA - Request for Approval",
        "statuses": ["Soạn thảo", "Đã gửi", "Chờ duyệt", "Đã duyệt", "Từ chối", "Đóng"],
        "done_statuses": ["Đã duyệt", "Từ chối", "Đóng"],
        "subject": "Nội dung trình duyệt",
        "code_label": "Mã RFA *",
        "issuer_label": "Người trình",
        "assignee_label": "Người / Đơn vị duyệt",
        "response_label": "Ý kiến / Kết quả phê duyệt",
    },
    "RFI": {
        "title": "RFI - Request for Information",
        "statuses": ["Đã gửi", "Chờ phản hồi", "Đã phản hồi", "Đóng", "Hủy"],
        "done_statuses": ["Đã phản hồi", "Đóng", "Hủy"],
        "subject": "Câu hỏi / Nội dung cần làm rõ",
        "code_label": "Mã RFI *",
        "issuer_label": "Người gửi",
        "assignee_label": "Người / Đơn vị phản hồi",
        "response_label": "Nội dung phản hồi",
    },
    "VO": {
        "title": "VO - Variation Order",
        "statuses": ["Dự thảo", "Đã gửi", "Đang thương thảo", "Đã duyệt", "Từ chối", "Đóng"],
        "done_statuses": ["Đã duyệt", "Từ chối", "Đóng"],
        "subject": "Nội dung phát sinh / thay đổi",
        "code_label": "Mã VO *",
        "issuer_label": "Người đề xuất",
        "assignee_label": "Người / Đơn vị phê duyệt",
        "response_label": "Ý kiến / Quyết định",
    },
    "NTCV": {
        "title": "Hồ sơ nghiệm thu công việc",
        "statuses": ["Chuẩn bị hồ sơ", "Đã trình nghiệm thu", "Chờ nghiệm thu", "Yêu cầu sửa", "Đạt", "Không đạt", "Đóng"],
        "done_statuses": ["Đạt", "Không đạt", "Đóng"],
        "subject": "Hạng mục / Công việc nghiệm thu",
        "code_label": "Mã hồ sơ NTCV *",
        "issuer_label": "Người / Đơn vị trình nghiệm thu",
        "assignee_label": "Người / Đơn vị nghiệm thu",
        "issue_date_label": "Ngày trình nghiệm thu",
        "due_date_label": "Ngày dự kiến nghiệm thu",
        "closed_date_label": "Ngày nghiệm thu / đóng",
        "response_label": "Kết quả / Ý kiến nghiệm thu",
    },
    "NTVL": {
        "title": "Hồ sơ nghiệm thu vật liệu đầu vào",
        "statuses": ["Chuẩn bị hồ sơ", "Đã trình", "Chờ kiểm tra", "Yêu cầu bổ sung", "Chấp thuận", "Chấp thuận có điều kiện", "Không chấp thuận", "Đóng"],
        "done_statuses": ["Chấp thuận", "Chấp thuận có điều kiện", "Không chấp thuận", "Đóng"],
        "subject": "Vật liệu / Thiết bị nghiệm thu đầu vào",
        "code_label": "Mã hồ sơ NTVL *",
        "issuer_label": "Nhà thầu / Người trình",
        "assignee_label": "Người / Đơn vị kiểm tra",
        "issue_date_label": "Ngày trình / nhận hồ sơ",
        "due_date_label": "Ngày dự kiến nghiệm thu",
        "closed_date_label": "Ngày nghiệm thu / đóng",
        "response_label": "Kết quả nghiệm thu / Ý kiến",
    },
    "KDVT": {
        "title": "Hồ sơ kiểm định vật tư",
        "statuses": ["Chuẩn bị hồ sơ", "Đã gửi kiểm định", "Đang kiểm định", "Chờ kết quả", "Đạt", "Không đạt", "Đóng"],
        "done_statuses": ["Đạt", "Không đạt", "Đóng"],
        "subject": "Vật tư / Thiết bị kiểm định",
        "code_label": "Mã hồ sơ kiểm định *",
        "issuer_label": "Người / Đơn vị gửi kiểm định",
        "assignee_label": "Đơn vị kiểm định / Người phụ trách",
        "issue_date_label": "Ngày gửi kiểm định",
        "due_date_label": "Hạn trả kết quả",
        "closed_date_label": "Ngày có kết quả / đóng",
        "response_label": "Kết quả kiểm định / Chứng chỉ",
    },
}
PRIORITIES = ["Thấp", "Trung bình", "Cao", "Khẩn"]

DRAWING_TYPES = {
    "SHOPDRAWING": "Shopdrawing",
    "ISSUED_DESIGN": "BV phát hành TKTC",
    "UPDATED": "BV cập nhật",
    "AS_BUILT": "BV hoàn công",
}
DRAWING_STATUSES = [
    "Mới nhận", "Đang kiểm tra", "Chờ phản hồi", "Chấp thuận",
    "Chấp thuận có điều kiện", "Cần sửa", "Thay thế", "Hủy",
]
TASK_STATUSES = ["Tất cả", "Chưa bắt đầu", "Đúng tiến độ", "Nhanh tiến độ", "Chậm tiến độ", "Hoàn thành", "Đang thực hiện", "Chưa xác định"]

st.set_page_config(page_title="QLDA Xây dựng V6.0 • Render • Drive 2GB", page_icon="🏗️", layout="wide")

st.markdown("""
<style>
.block-container {padding-top: 1.1rem; padding-bottom: 2rem;}
[data-testid="stMetric"] {background: #f7f9fc; border: 1px solid #e5e7eb; padding: 10px 14px; border-radius: 12px;}
.small-note {font-size: 0.86rem; color: #64748b;}
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_db(path: str) -> CloudDatabase:
    return CloudDatabase(path)


db = get_db(str(DB_PATH))


@st.cache_resource
def get_legal_repo(path: str) -> LegalRepository:
    return LegalRepository(path)


legal_repo = get_legal_repo(str(DB_PATH))
if "legal_cache_loaded" not in st.session_state:
    try:
        cache_stats = legal_repo.import_cache(LEGAL_CACHE_PATH)
        st.session_state["legal_cache_stats"] = cache_stats
    except Exception as exc:
        st.session_state["legal_cache_error"] = str(exc)
    st.session_state["legal_cache_loaded"] = True


def iso(d) -> str:
    if not d:
        return ""
    if isinstance(d, str):
        return d
    return d.isoformat()


def parse_date(value: str, fallback: date | None = None) -> date:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except Exception:
        return fallback or date.today()


def rows_to_df(rows) -> pd.DataFrame:
    return pd.DataFrame([dict(r) for r in rows]) if rows else pd.DataFrame()


def uploaded_triplets(files) -> list[tuple[str, str, bytes]]:
    out = []
    for f in files or []:
        out.append((f.name, getattr(f, "type", "") or "application/octet-stream", f.getvalue()))
    return out


def to_excel_bytes(df: pd.DataFrame, sheet_name="Data") -> bytes:
    buff = io.BytesIO()
    with pd.ExcelWriter(buff, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name[:31])
    return buff.getvalue()


def project_selector() -> tuple[int | None, list]:
    projects = db.projects()
    if not projects:
        return None, projects
    labels = {int(p["id"]): f"{p['code']} - {p['name']}" for p in projects}
    ids = list(labels)
    current = st.session_state.get("project_id")
    idx = ids.index(current) if current in ids else 0
    pid = st.sidebar.selectbox("Dự án đang làm việc", ids, index=idx, format_func=lambda x: labels[x], key="global_project")
    st.session_state["project_id"] = pid
    return int(pid), projects


def sidebar_project_tools():
    st.sidebar.markdown("### 🏗️ QLDA Xây dựng V6.0 AI")
    st.sidebar.caption("Render Web Service" if IS_RENDER else "Streamlit / Local")
    with st.sidebar.expander("+ Tạo dự án"):
        with st.form("create_project", clear_on_submit=True):
            code = st.text_input("Mã dự án *")
            name = st.text_input("Tên dự án *")
            c1, c2 = st.columns(2)
            start = c1.date_input("Bắt đầu", value=date.today())
            end = c2.date_input("Kết thúc", value=date.today() + timedelta(days=365))
            manager = st.text_input("Quản lý dự án")
            note = st.text_area("Ghi chú")
            submitted = st.form_submit_button("Tạo dự án", type="primary", disabled=not _is_admin())
            if submitted:
                if not code.strip() or not name.strip():
                    st.error("Cần nhập Mã dự án và Tên dự án.")
                else:
                    try:
                        pid = db.add_project(code, name, iso(start), iso(end), manager, note)
                        st.session_state["project_id"] = pid
                        st.success("Đã tạo dự án.")
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("Mã dự án đã tồn tại.")

    with st.sidebar.expander("💾 Sao lưu / khôi phục"):
        if IS_RENDER and str(os.environ.get("QLDA_RENDER_PERSISTENT_DISK", "false")).lower() in {"1", "true", "yes", "on"}:
            st.caption("Database đang đặt trên Render Persistent Disk. Vẫn nên tải backup định kỳ.")
        elif IS_RENDER:
            st.warning("Render đang chạy KHÔNG có Persistent Disk: SQLite sẽ mất khi service restart/redeploy. File Google Drive không bị ảnh hưởng.")
        else:
            st.caption("Hãy tải backup SQLite định kỳ.")
        backup = db.backup_bytes()
        st.download_button("⬇️ Tải backup SQLite", backup, file_name=f"QLDA_backup_{date.today():%Y%m%d}.db", mime="application/octet-stream", width="stretch")
        restore = st.file_uploader("Khôi phục từ .db", type=["db", "sqlite", "sqlite3"], key="restore_db")
        if st.button("Khôi phục database", disabled=(restore is None or not _is_admin()), width="stretch"):
            try:
                db.restore_bytes(restore.getvalue())
                st.success("Đã khôi phục database.")
                st.rerun()
            except Exception as exc:
                st.error(str(exc))


def render_schedule(pid: int):
    project = db.project(pid)
    st.subheader("📅 Quản lý tiến độ")
    st.caption("MPP • WBS • Baseline • Critical Path • Gantt • KH%/TT% • Nhanh/Chậm")

    cdate, csrc = st.columns([1, 3])
    status_date = cdate.date_input("Ngày báo cáo", value=date.today(), key=f"status_date_{pid}")
    source = project["source_mpp_path"] or "Chưa nhập MPP"
    csrc.info(f"Nguồn tiến độ: **{source}**" + (f" — đồng bộ {project['last_sync']}" if project["last_sync"] else ""))

    rows = db.tasks(pid)
    n = len(rows)
    delayed = sum(1 for r in rows if r["status"] == "Chậm tiến độ")
    critical = sum(1 for r in rows if r["critical"])
    done = sum(1 for r in rows if int(r["actual_progress"] or 0) >= 100)
    avg = round(sum(float(r["actual_progress"] or 0) for r in rows) / n, 1) if n else 0
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Tổng công việc", n)
    k2.metric("Chậm tiến độ", delayed)
    k3.metric("Critical", critical)
    k4.metric("Hoàn thành", done)
    k5.metric("Tiến độ TB", f"{avg}%")

    with st.expander("📂 Nhập / đồng bộ Microsoft Project (.mpp)", expanded=not bool(rows)):
        st.write("Trên Cloud, file MPP được đọc trực tiếp bằng MPXJ; không cần cài Microsoft Project trên server.")
        mpp = st.file_uploader("Chọn file .mpp", type=["mpp"], key=f"mpp_{pid}")
        if st.button("Đọc và đồng bộ MPP", type="primary", disabled=(mpp is None or not _can_update()), key=f"syncmpp_{pid}"):
            suffix = Path(mpp.name).suffix or ".mpp"
            temp_path = None
            try:
                with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
                    tmp.write(mpp.getvalue())
                    temp_path = tmp.name
                with st.spinner("Đang đọc Microsoft Project bằng MPXJ..."):
                    info, tasks = read_mpp(temp_path, status_date=status_date)
                    db.sync_mpp_tasks(pid, tasks, mpp.name, info)
                st.success(f"Đồng bộ thành công {len(tasks):,} công việc từ {mpp.name}.")
                st.rerun()
            except MppCloudError as exc:
                st.error(str(exc))
            except Exception as exc:
                st.exception(exc)
            finally:
                if temp_path:
                    try:
                        Path(temp_path).unlink(missing_ok=True)
                    except Exception:
                        pass

    a1, a2 = st.columns([1, 3])
    if a1.button("Tính lại KH% theo ngày báo cáo", key=f"recalc_{pid}", width="stretch", disabled=not _can_update()):
        db.recalc_planned(pid, status_date)
        st.success(f"Đã tính lại KH% tại ngày {status_date:%d/%m/%Y}.")
        st.rerun()
    a2.caption("KH% tính tuyến tính theo Start–Finish. TT=100% là Hoàn thành; TT<100% sau ngày Kết thúc sẽ tự tính Ngày trễ. TT nhập tay được giữ khi đồng bộ MPP.")

    with st.expander("+ Thêm công việc thủ công"):
        with st.form(f"manual_task_{pid}", clear_on_submit=True):
            c1, c2 = st.columns([1, 3])
            wbs = c1.text_input("WBS")
            name = c2.text_input("Công việc *")
            c1, c2, c3 = st.columns(3)
            start = c1.date_input("Bắt đầu", value=status_date)
            end = c2.date_input("Kết thúc", value=status_date + timedelta(days=7))
            responsible = c3.text_input("Phụ trách")
            c1, c2, c3 = st.columns(3)
            planned = c1.number_input("KH %", 0, 100, value=0)
            actual = c2.number_input("TT %", 0, 100, value=0)
            predecessor = c3.text_input("Predecessor")
            note = st.text_area("Ghi chú")
            submit = st.form_submit_button("Thêm công việc", type="primary", disabled=not _can_update())
            if submit:
                if not name.strip() or end < start:
                    st.error("Tên công việc là bắt buộc và ngày kết thúc không được trước ngày bắt đầu.")
                else:
                    duration = max(1, (end - start).days + 1)
                    db.add_task(pid, dict(wbs=wbs, name=name, responsible=responsible, start_date=iso(start), end_date=iso(end),
                                               duration=duration, planned_progress=planned, actual_progress=actual,
                                               predecessor=predecessor, note=note))
                    st.success("Đã thêm công việc.")
                    st.rerun()

    f1, f2 = st.columns([3, 1])
    keyword = f1.text_input("Tìm WBS / công việc / resource", key=f"task_search_{pid}")
    status_filter = f2.selectbox("Trạng thái", TASK_STATUSES, key=f"task_status_{pid}")
    rows = db.tasks(pid, keyword, status_filter)
    if not rows:
        st.info("Chưa có công việc phù hợp.")
        return

    display = pd.DataFrame([{
        "DB ID": r["id"], "ID": r["source_task_id"] or "", "WBS": r["wbs"], "Công việc": r["name"],
        "Bắt đầu": r["start_date"], "Kết thúc": r["end_date"], "Duration": round(float(r["duration"] or 0), 2),
        "KH %": int(r["planned_progress"] or 0), "TT %": int(r["actual_progress"] or 0),
        "Nhanh / Chậm": progress_delta(r["planned_progress"], r["actual_progress"]), "Trạng thái": r["status"],
        "Ngày trễ": calculate_delay_days(r["end_date"], r["actual_progress"], r["actual_finish_date"] or "", status_date),
        "Predecessor": r["predecessor"], "Resources": r["resource_names"], "Baseline Start": r["baseline_start"],
        "Baseline Finish": r["baseline_finish"], "Slack (ngày)": round(float(r["total_slack"] or 0), 2),
        "Critical": "Có" if r["critical"] else "", "Nguồn": r["source_type"],
    } for r in rows])
    original_tt = dict(zip(display["DB ID"], display["TT %"]))
    disabled_cols = list(display.columns) if not _can_update() else [c for c in display.columns if c != "TT %"]
    edited = st.data_editor(
        display, hide_index=True, width="stretch", disabled=disabled_cols,
        column_config={
            "DB ID": None,
            "TT %": st.column_config.NumberColumn("TT %", min_value=0, max_value=100, step=1, help="Nhập trực tiếp 0–100%"),
            "KH %": st.column_config.ProgressColumn("KH %", min_value=0, max_value=100, format="%d%%"),
            "Nhanh / Chậm": st.column_config.NumberColumn("TT − KH", format="%d%%"),
            "Ngày trễ": st.column_config.NumberColumn("Ngày trễ", format="%d ngày", help="Số ngày vượt ngày Kết thúc; khi TT=100% số ngày trễ được khóa tại ngày đạt 100%."),
        }, key=f"task_editor_{pid}", height=min(700, 80 + 35 * len(display)),
    )
    # Streamlit: tự lưu ngay khi người dùng thay đổi TT %.
    # st.data_editor rerun sau khi Enter/click ra khỏi ô; trên rerun này `edited`
    # chứa giá trị mới, còn `original_tt` vẫn là dữ liệu DB trước khi lưu.
    # So sánh hai giá trị để chỉ ghi đúng các dòng đã đổi, sau đó rerun một lần
    # để cập nhật Nhanh/Chậm, Trạng thái và Ngày trễ ngay trên bảng.
    autosaved = 0
    for _, r in edited.iterrows():
        task_id = int(r["DB ID"])
        try:
            actual = max(0, min(100, int(round(float(r["TT %"])))))
        except Exception:
            continue
        old_actual = int(original_tt.get(task_id, actual))
        if actual != old_actual and _can_update():
            db.set_actual_override(task_id, actual, status_date)
            autosaved += 1

    if autosaved:
        st.toast(f"Đã tự lưu TT% cho {autosaved} công việc", icon="✅")
        st.rerun()

    b1, b2 = st.columns([1, 3])
    b1.caption("TT % tự lưu khi nhấn Enter hoặc click ra khỏi ô.")
    selected_delete = b2.selectbox("Xóa task", [None] + [int(r["id"]) for r in rows], format_func=lambda x: "Chọn..." if x is None else f"#{x}", key=f"delete_task_select_{pid}")
    if st.button("Xóa công việc đã chọn", disabled=(selected_delete is None or not _is_admin()), key=f"delete_task_btn_{pid}"):
        db.delete_task(int(selected_delete))
        st.rerun()

    ex1, ex2 = st.columns(2)
    ex1.download_button("⬇️ Xuất tiến độ Excel", to_excel_bytes(display.drop(columns=["DB ID"]), "TienDo"),
                        file_name=f"TienDo_{project['code']}_{date.today():%Y%m%d}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", width="stretch")
    excel_in = ex2.file_uploader("Nhập công việc từ Excel", type=["xlsx", "xls"], key=f"task_excel_{pid}")
    if excel_in is not None and ex2.button("Nhập Excel", key=f"task_excel_btn_{pid}", width="stretch", disabled=not _can_update()):
        try:
            xdf = pd.read_excel(excel_in)
            aliases = {
                "WBS": "wbs", "Công việc": "name", "Name": "name", "Bắt đầu": "start", "Start": "start",
                "Kết thúc": "end", "Finish": "end", "KH %": "planned", "TT %": "actual", "Phụ trách": "responsible",
                "Predecessor": "predecessor", "Ghi chú": "note",
            }
            normalized = {}
            for col in xdf.columns:
                if str(col).strip() in aliases:
                    normalized[aliases[str(col).strip()]] = col
            required = {"name", "start", "end"}
            if not required.issubset(normalized):
                st.error("Excel cần tối thiểu các cột: Công việc/Name, Bắt đầu/Start, Kết thúc/Finish.")
            else:
                count = 0
                for _, xr in xdf.iterrows():
                    s = pd.to_datetime(xr[normalized["start"]], errors="coerce")
                    e = pd.to_datetime(xr[normalized["end"]], errors="coerce")
                    if pd.isna(s) or pd.isna(e) or not str(xr[normalized["name"]]).strip():
                        continue
                    ps, pe = s.date(), e.date()
                    db.add_task(pid, {
                        "wbs": str(xr[normalized.get("wbs", "")] if "wbs" in normalized else ""),
                        "name": str(xr[normalized["name"]]),
                        "responsible": str(xr[normalized.get("responsible", "")] if "responsible" in normalized else ""),
                        "start_date": iso(ps), "end_date": iso(pe), "duration": max(1, (pe - ps).days + 1),
                        "planned_progress": int(xr[normalized["planned"]]) if "planned" in normalized and pd.notna(xr[normalized["planned"]]) else planned_progress(iso(ps), iso(pe), status_date),
                        "actual_progress": int(xr[normalized["actual"]]) if "actual" in normalized and pd.notna(xr[normalized["actual"]]) else 0,
                        "predecessor": str(xr[normalized.get("predecessor", "")] if "predecessor" in normalized else ""),
                        "note": str(xr[normalized.get("note", "")] if "note" in normalized else ""),
                    })
                    count += 1
                st.success(f"Đã nhập {count} công việc.")
                st.rerun()
        except Exception as exc:
            st.error(f"Không đọc được Excel: {exc}")

    st.markdown("#### Gantt")
    gantt_rows = [r for r in rows if r["start_date"] and r["end_date"]]
    if px is None:
        st.info("Cần package plotly để hiển thị Gantt.")
    elif gantt_rows:
        gdf = pd.DataFrame([{
            "Task": ("   " * max(0, int(r["outline_level"] or 1) - 1)) + f"{r['wbs']} {r['name']}",
            "Start": pd.to_datetime(r["start_date"]), "Finish": pd.to_datetime(r["end_date"]),
            "Status": "Critical" if r["critical"] else r["status"], "TT": int(r["actual_progress"] or 0),
        } for r in gantt_rows])
        fig = px.timeline(gdf, x_start="Start", x_end="Finish", y="Task", color="Status", hover_data=["TT"])
        fig.update_yaxes(autorange="reversed")
        fig.update_layout(height=max(420, min(1400, 26 * len(gdf) + 160)), margin=dict(l=10, r=10, t=20, b=10), legend_title_text="")
        st.plotly_chart(fig, width="stretch")


def document_deadline_label(r, doc_type: str) -> str:
    done_statuses = set(DOC_CONFIG[doc_type].get("done_statuses", ["Đóng", "Hủy"]))
    if r["closed_date"] or r["status"] in done_statuses:
        return "Đã xử lý"
    if not r["due_date"]:
        return ""
    due = parse_date(r["due_date"])
    delta = (due - date.today()).days
    if delta < 0:
        return f"Quá hạn {abs(delta)} ngày"
    if delta <= 7:
        return f"Còn {delta} ngày"
    return "Trong hạn"


def _prepare_inline_upload_ticket(pid: int, *, kind: str, subtype: str, record_code: str, panel_key: str) -> dict:
    """Tạo ticket tải trực tiếp lên Drive cho khung đính kèm V6.0."""
    project = db.project(pid)
    if not project:
        raise RuntimeError("Không tìm thấy dự án.")
    token = _gateway_session_token()
    if not token:
        raise RuntimeError("Phiên Google Drive đã hết hạn. Hãy đăng nhập lại.")
    upload = _drive_gateway().create_upload_ticket(
        token,
        project_code=project["code"],
        kind=kind,
        subtype=subtype,
        record_code=record_code,
    )
    st.session_state[panel_key + "_ticket"] = upload
    st.session_state[panel_key + "_upload_open"] = True
    return upload


def _render_inline_drive_attachments(pid: int, *, kind: str, subtype: str, record_code: str, record_id: int, panel_key: str) -> None:
    """V6.0: file nằm ngay dưới nút Cập nhật, không còn file-manager tách riêng.

    File lớn vẫn đi theo V5 resumable flow: trình duyệt -> Apps Script -> Drive,
    không đi qua Python/SQLite. Quyền update có thể upload/download nhưng không xóa.
    Admin xóa bằng cách tick file cần xóa rồi bấm một nút xóa tập trung.
    """
    st.markdown("##### 📎 File đính kèm")
    project = db.project(pid)
    if not project:
        st.warning("Không tìm thấy dự án.")
        return
    token = _gateway_session_token()
    if not token:
        st.warning("Phiên Google Drive đã hết hạn. Hãy đăng nhập lại.")
        return

    upload = st.session_state.get(panel_key + "_ticket") or {}
    upload_open = bool(st.session_state.get(panel_key + "_upload_open"))
    if upload_open and upload.get("url"):
        st.info(
            "Đã mở vùng **Đính kèm file**. Chọn một hoặc nhiều file, sau đó bấm **⬆ Tải lên** màu xanh trong khung để bắt đầu. "
            "File được tải trực tiếp lên Google Drive, tối đa **2 GB/file**. Khi hoàn tất, bấm **Hoàn tất & cập nhật File DB** bên dưới."
        )
        # Apps Script V6 sets XFrameOptionsMode.ALLOWALL for this short-lived ticket page.
        components.iframe(upload["url"], height=530, scrolling=True)
        u1, u2 = st.columns([1.4, 1])
        u1.link_button("↗️ Mở trình tải ở tab riêng", upload["url"], width="stretch")
        if u2.button("✅ Hoàn tất & cập nhật File DB", key=panel_key + "_close_upload", width="stretch"):
            st.session_state[panel_key + "_upload_open"] = False
            st.session_state[panel_key + "_ticket"] = {}
            st.rerun()

    h1, h2 = st.columns([1, 4])
    if h1.button("🔄 Làm mới file / File DB", key=panel_key + "_refresh_files", width="stretch"):
        st.rerun()
    h2.caption("⬆ Cập nhật/Admin: đính kèm & tải xuống • 🗑 Chỉ Admin được xóa file đã tick.")

    include_history = st.checkbox("Hiện cả _Lich_su", value=False, key=panel_key + "_history")
    try:
        data = _drive_gateway().list_record_files(
            token,
            project_code=project["code"],
            kind=kind,
            subtype=subtype,
            record_code=record_code,
            include_history=include_history,
        )
    except Exception as exc:
        st.error(f"Không đọc được danh sách file Google Drive: {exc}")
        return

    folder = data.get("folder") or {}
    files = data.get("files") or []
    if folder.get("url"):
        st.link_button("📂 Mở thư mục trên Google Drive", folder["url"], width="content")
    if not files:
        st.caption("Chưa có file trên Google Drive. Bấm **📎 Đính kèm file**, chọn tệp rồi bấm **⬆ Tải lên** trong khung Google Drive.")
        return

    st.markdown("**Danh sách file Google Drive**")
    hd0, hd1, hd2, hd3 = st.columns([0.55, 5.4, 1.1, 1.35])
    hd0.caption("Xóa")
    hd1.caption("Tên file")
    hd2.caption("Mở")
    hd3.caption("Tải xuống")

    checked_ids: list[tuple[str, str]] = []
    for idx, item in enumerate(files):
        file_id = str(item.get("id") or "")
        name = str(item.get("name") or "file")
        size = _format_drive_size(item.get("size"))
        modified = str(item.get("modified_time") or "").replace("T", " ").replace("Z", "")[:19]
        history_mark = " 🕘" if item.get("history") else ""
        c0, c1, c2, c3 = st.columns([0.55, 5.4, 1.1, 1.35])
        marked = c0.checkbox(
            "Chọn xóa",
            key=f"{panel_key}_delete_tick_{idx}_{file_id}",
            value=False,
            disabled=not _is_admin(),
            label_visibility="collapsed",
        )
        c1.markdown(f"**{name}**{history_mark}  \n{size}" + (f" • {modified}" if modified else ""))
        if item.get("url"):
            c2.link_button("☁ Mở", item["url"], width="stretch")
        download_url = item.get("download_url") or (
            f"https://drive.google.com/uc?export=download&id={file_id}" if file_id else ""
        )
        if download_url:
            c3.link_button("⬇️ Tải xuống", download_url, width="stretch")
        if marked and file_id:
            checked_ids.append((file_id, name))

    if _is_admin():
        delete_label = f"🗑 Xóa file đã chọn ({len(checked_ids)})"
        if st.button(delete_label, key=panel_key + "_delete_checked", disabled=not checked_ids, type="secondary"):
            deleted = 0
            errors = []
            for file_id, name in checked_ids:
                try:
                    _drive_gateway().trash_file(token, file_id)
                    deleted += 1
                except Exception as exc:
                    errors.append(f"{name}: {exc}")
            if deleted:
                st.success(f"Đã chuyển {deleted} file đã chọn vào Thùng rác Google Drive.")
            if errors:
                st.error("Không xóa được: " + " | ".join(errors))
            st.rerun()
    else:
        st.caption("🔒 Quyền Cập nhật/Chỉ đọc không được xóa file. Ô tick xóa chỉ hoạt động với Admin.")


def _record_drive_counts(pid: int, *, kind: str, subtype: str, record_codes) -> dict[str, dict]:
    """Đọc số file hiện có trên Google Drive theo lô để cột File DB phản ánh file direct-upload."""
    project = db.project(pid)
    token = _gateway_session_token()
    codes = [str(c or "").strip() for c in record_codes if str(c or "").strip()]
    if not project or not token or not codes:
        return {}
    try:
        return _drive_gateway().record_file_counts(
            token,
            project_code=project["code"],
            kind=kind,
            subtype=subtype,
            record_codes=codes,
        )
    except Exception as exc:
        st.caption(f"⚠ Chưa đồng bộ được trạng thái File DB từ Google Drive: {exc}")
        return {}


def _trash_record_drive_files(pid: int, *, kind: str, subtype: str, record_code: str) -> tuple[int, list[str]]:
    """Admin: chuyển toàn bộ file hiện hành + lịch sử của một record vào thùng rác Drive."""
    project = db.project(pid)
    token = _gateway_session_token()
    if not project or not token:
        return 0, ["Không có phiên Google Drive hợp lệ."]
    try:
        data = _drive_gateway().list_record_files(
            token,
            project_code=project["code"],
            kind=kind,
            subtype=subtype,
            record_code=record_code,
            include_history=True,
        )
    except Exception as exc:
        return 0, [str(exc)]
    deleted = 0
    errors: list[str] = []
    seen: set[str] = set()
    for item in data.get("files") or []:
        file_id = str(item.get("id") or "")
        if not file_id or file_id in seen:
            continue
        seen.add(file_id)
        try:
            _drive_gateway().trash_file(token, file_id)
            deleted += 1
        except Exception as exc:
            errors.append(f"{item.get('name') or file_id}: {exc}")
    return deleted, errors


def render_document_type(pid: int, doc_type: str):
    cfg = DOC_CONFIG[doc_type]
    rows = db.documents(pid, doc_type)
    total = len(rows)
    overdue = sum(1 for r in rows if document_deadline_label(r, doc_type).startswith("Quá hạn"))
    done_statuses = set(cfg.get("done_statuses", ["Đóng", "Hủy"]))
    closed = sum(1 for r in rows if r["closed_date"] or r["status"] in done_statuses)
    c1, c2, c3 = st.columns(3)
    c1.metric("Tổng hồ sơ", total)
    c2.metric("Quá hạn", overdue)
    c3.metric("Đã xử lý/đóng", closed)

    options = [None] + [int(r["id"]) for r in rows]
    select_key = f"doc_select_{pid}_{doc_type}"
    pending_key = select_key + "_pending"
    pending = st.session_state.pop(pending_key, None)
    if pending in options:
        st.session_state[select_key] = pending
    selected = st.selectbox(
        "Chọn hồ sơ để sửa / cập nhật",
        options,
        format_func=lambda x: "➕ Thêm mới" if x is None else f"#{x} - {next(r['code'] for r in rows if r['id']==x)}",
        key=select_key,
    )
    record = db.document(selected) if selected else None
    flash_key = f"flash_doc_{pid}_{doc_type}"
    if flash_key in st.session_state:
        st.success(st.session_state.pop(flash_key))
    error_flash = flash_key + "_error"
    if error_flash in st.session_state:
        st.error(st.session_state.pop(error_flash))

    with st.form(f"doc_form_{pid}_{doc_type}_{selected or 'new'}"):
        c1, c2 = st.columns([1, 2])
        code = c1.text_input(cfg.get("code_label", f"Mã {doc_type} *"), value=(record["code"] if record else ""))
        subject = c2.text_input(f"{cfg['subject']} *", value=(record["subject"] if record else ""))
        c1, c2, c3 = st.columns(3)
        discipline = c1.text_input("Bộ môn / Hệ", value=(record["discipline"] if record else ""))
        contractor = c2.text_input("Nhà thầu / Đơn vị", value=(record["contractor"] if record else ""))
        priority_default = PRIORITIES.index(record["priority"]) if record and record["priority"] in PRIORITIES else 1
        priority = c3.selectbox("Mức độ", PRIORITIES, index=priority_default)
        c1, c2 = st.columns(2)
        issuer = c1.text_input(cfg.get("issuer_label", "Người phát hành / trình"), value=(record["issuer"] if record else ""))
        assignee = c2.text_input(cfg.get("assignee_label", "Người / Đơn vị xử lý"), value=(record["assignee"] if record else ""))
        c1, c2, c3 = st.columns(3)
        issue_date = c1.date_input(cfg.get("issue_date_label", "Ngày phát hành"), value=parse_date(record["issue_date"], date.today()) if record else date.today())
        due_date = c2.date_input(cfg.get("due_date_label", "Hạn xử lý"), value=parse_date(record["due_date"], date.today()+timedelta(days=7)) if record else date.today()+timedelta(days=7))
        closed_enabled = c3.checkbox("Đã có ngày đóng", value=bool(record and record["closed_date"]))
        closed_date = c3.date_input(cfg.get("closed_date_label", "Ngày đóng"), value=parse_date(record["closed_date"], date.today()) if record and record["closed_date"] else date.today(), disabled=not closed_enabled)
        status_index = cfg["statuses"].index(record["status"]) if record and record["status"] in cfg["statuses"] else 0
        status = st.selectbox("Trạng thái", cfg["statuses"], index=status_index)
        related_wbs = st.text_input("WBS / Task liên quan", value=(record["related_wbs"] if record else ""))
        description = st.text_area("Mô tả / Ghi chú", value=(record["description"] if record else ""))
        response = st.text_area(cfg.get("response_label", "Phản hồi / Kết quả"), value=(record["response"] if record else ""))
        if doc_type == "VO":
            c1, c2 = st.columns(2)
            cost_impact = c1.number_input("Giá trị phát sinh (đ)", value=float(record["cost_impact"] or 0) if record else 0.0, step=1_000_000.0, format="%.0f")
            time_impact = c2.number_input("Ảnh hưởng tiến độ (ngày)", value=int(record["time_impact_days"] or 0) if record else 0, step=1)
        else:
            cost_impact, time_impact = 0.0, 0

        st.caption("V6.0: **Đính kèm file** nằm cạnh **Tải lên**. Khi vùng đính kèm đã mở: chọn tệp rồi bấm **⬆ Tải lên** màu xanh trong khung Google Drive; không tự tải khi vừa chọn file.")
        existing_panel_key = f"v6_doc_attach_{pid}_{doc_type}_{selected}" if selected else ""
        panel_is_open = bool(existing_panel_key and st.session_state.get(existing_panel_key + "_upload_open"))
        b_attach, b_save = st.columns([1, 1])
        with b_attach:
            attach_clicked = st.form_submit_button("📎 Đính kèm file", disabled=not _can_update(), width="stretch")
        with b_save:
            save_clicked = st.form_submit_button("⬆️ Tải lên", type="primary", disabled=(not _can_update()) or panel_is_open, width="stretch")

        if attach_clicked or save_clicked:
            if not code.strip() or not subject.strip():
                st.error("Mã hồ sơ và nội dung là bắt buộc trước khi đính kèm/cập nhật.")
            else:
                try:
                    doc_id = db.save_document(pid, doc_type, {
                        "code": code, "subject": subject, "discipline": discipline, "contractor": contractor,
                        "issuer": issuer, "assignee": assignee, "issue_date": iso(issue_date), "due_date": iso(due_date),
                        "closed_date": iso(closed_date) if closed_enabled else "", "status": status, "priority": priority,
                        "related_wbs": related_wbs, "description": description, "response": response,
                        "cost_impact": cost_impact, "time_impact_days": time_impact,
                    }, selected)
                    st.session_state[pending_key] = doc_id
                    panel_key = f"v6_doc_attach_{pid}_{doc_type}_{doc_id}"
                    try:
                        _prepare_inline_upload_ticket(
                            pid, kind="document", subtype=doc_type, record_code=code.strip(), panel_key=panel_key
                        )
                        if attach_clicked:
                            st.session_state[flash_key] = "Đã lưu hồ sơ và mở vùng chọn file. Chọn tệp rồi bấm Tải lên trong khung Google Drive."
                        else:
                            st.session_state[flash_key] = "Đã lưu/cập nhật hồ sơ và chuẩn bị vùng tải. Chọn tệp rồi bấm Tải lên trong khung Google Drive."
                    except Exception as exc:
                        st.session_state[error_flash] = f"Đã lưu hồ sơ nhưng chưa mở được vùng tải file: {exc}"
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error(f"Mã {doc_type} đã tồn tại trong dự án.")

    if selected:
        current = db.document(selected)
        if current:
            panel_key = f"v6_doc_attach_{pid}_{doc_type}_{selected}"
            _render_inline_drive_attachments(
                pid,
                kind="document",
                subtype=doc_type,
                record_code=str(current["code"] or ""),
                record_id=int(selected),
                panel_key=panel_key,
            )

        arows = db.document_attachments(selected)
        if arows:
            st.markdown("**File legacy từ V4.x (nếu có)**")
            legacy_delete = []
            for a in arows:
                c0, c1, c2 = st.columns([0.55, 5, 1.5])
                marked = c0.checkbox("Xóa", key=f"legacy_doc_tick_{a['id']}", disabled=not _is_admin(), label_visibility="collapsed")
                content = bytes(a["file_content"] or b"")
                if content:
                    c1.download_button(f"⬇️ {a['file_name']}", content, file_name=a["file_name"], mime=a["mime_type"] or "application/octet-stream", key=f"doc_dl_{a['id']}")
                elif a["drive_web_url"]:
                    c1.link_button(f"☁ {a['file_name']}", a["drive_web_url"])
                    if a["drive_file_id"]:
                        c2.link_button("⬇️ Tải xuống", f"https://drive.google.com/uc?export=download&id={a['drive_file_id']}", width="stretch")
                else:
                    c1.caption(f"{a['file_name']} — file cũ chỉ lưu đường dẫn desktop.")
                if marked:
                    legacy_delete.append(a)
            if _is_admin() and st.button(f"🗑 Xóa file legacy đã tick ({len(legacy_delete)})", disabled=not legacy_delete, key=f"legacy_doc_delete_{selected}"):
                for a in legacy_delete:
                    if a["drive_file_id"]:
                        _trash_drive_file(a["drive_file_id"])
                    db.delete_document_attachment(a["id"])
                st.rerun()

    if rows:
        drive_counts = _record_drive_counts(pid, kind="document", subtype=doc_type, record_codes=[r["code"] for r in rows])
        table_rows = []
        for r in rows:
            info = drive_counts.get(str(r["code"] or ""), {})
            direct_count = int(info.get("count") or 0)
            legacy_count = int(r["attachment_count"] or 0)
            total_files = direct_count + legacy_count
            file_label = f"✅ Có file ({total_files})" if total_files else "—"
            table_rows.append({
                "Chọn": False, "ID": r["id"], "Mã": r["code"], "Nội dung": r["subject"], "Bộ môn": r["discipline"],
                "Nhà thầu": r["contractor"], "Phát hành": r["issue_date"], "Hạn": r["due_date"],
                "Trạng thái": r["status"], "Mức độ": r["priority"], "Theo dõi hạn": document_deadline_label(r, doc_type),
                "WBS/Task": r["related_wbs"], "File DB": file_label,
                **({"Giá trị VO": r["cost_impact"], "Ảnh hưởng ngày": r["time_impact_days"]} if doc_type == "VO" else {}),
            })
        df = pd.DataFrame(table_rows)
        # V6 Render: một cột Chọn dùng chung cho cả Tải xuống và Xóa.
        # Chỉ các cột khác bị khóa; mọi quyền đều được tick để tải file.
        disabled_cols = [c for c in df.columns if c != "Chọn"]
        edited = st.data_editor(
            df,
            hide_index=True,
            width="stretch",
            key=f"doc_select_grid_{pid}_{doc_type}_{len(rows)}_{sum(int(r['id']) for r in rows)}",
            disabled=disabled_cols,
            column_config={
                "Chọn": st.column_config.CheckboxColumn(
                    "☑ Chọn",
                    help="Tick hồ sơ cần tải xuống. Admin cũng dùng chính dấu tick này để xóa.",
                    default=False,
                )
            },
        )
        selected_ids = [int(v) for v in edited.loc[edited["Chọn"] == True, "ID"].tolist()]
        download_state_key = f"doc_download_selected_state_{pid}_{doc_type}"
        d1, d2, d3 = st.columns([1.45, 1.35, 3.6])
        if d1.button(
            f"⬇️ Tải hồ sơ đã chọn ({len(selected_ids)})",
            key=f"doc_download_selected_{pid}_{doc_type}",
            disabled=not selected_ids,
            type="primary",
            width="stretch",
        ):
            st.session_state[download_state_key] = list(selected_ids)

        if d2.button(
            f"🗑 Xóa hồ sơ đã chọn ({len(selected_ids)})",
            key=f"doc_delete_selected_{pid}_{doc_type}",
            disabled=(not _is_admin()) or not selected_ids,
            width="stretch",
        ):
            errors = []
            deleted = 0
            for rid in selected_ids:
                row = db.document(rid)
                if not row:
                    continue
                _, drive_errors = _trash_record_drive_files(pid, kind="document", subtype=doc_type, record_code=str(row["code"] or ""))
                if drive_errors:
                    errors.append(f"#{rid}: " + " | ".join(drive_errors))
                    continue
                db.delete_document(rid)
                deleted += 1
            if selected in selected_ids:
                st.session_state[pending_key] = None
            st.session_state.pop(download_state_key, None)
            if deleted:
                st.success(f"Đã xóa {deleted} hồ sơ đã chọn.")
            if errors:
                st.error("Một số hồ sơ chưa xóa được vì lỗi Google Drive: " + " || ".join(errors))
            st.rerun()
        d3.caption("☑ Một dấu tick dùng chung → **Tải hồ sơ đã chọn**; riêng Admin mới được dùng **Xóa**.")

        download_ids = [int(x) for x in (st.session_state.get(download_state_key) or [])]
        if download_ids:
            _render_selected_document_downloads(pid, doc_type, download_ids, download_state_key)
        export_df = df.drop(columns=["Chọn"])
        st.download_button(f"⬇️ Xuất {doc_type} Excel", to_excel_bytes(export_df, doc_type), file_name=f"{doc_type}_{date.today():%Y%m%d}.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key=f"doc_xlsx_{pid}_{doc_type}")


def render_documents(pid: int):
    st.subheader("📁 Quản lý hồ sơ")
    st.caption("NCR • RFA • RFI • VO • Nghiệm thu công việc • Nghiệm thu vật liệu đầu vào • Kiểm định vật tư • File Google Drive")
    doc_types = ["NCR", "RFA", "RFI", "VO", "NTCV", "NTVL", "KDVT"]
    tab_names = ["NCR", "RFA", "RFI", "VO", "NT công việc", "NT vật liệu đầu vào", "Kiểm định vật tư"]
    tabs = st.tabs(tab_names)
    for tab, doc_type in zip(tabs, doc_types):
        with tab:
            st.markdown(f"### {DOC_CONFIG[doc_type]['title']}")
            render_document_type(pid, doc_type)



def _render_selected_record_downloads(
    pid: int,
    *,
    kind: str,
    subtype: str,
    selected_ids: list[int],
    panel_key: str,
) -> None:
    """Hiển thị file Google Drive của các dòng đã tick để tải trực tiếp.

    Cùng một cột ``Chọn`` được dùng cho cả tải xuống và xóa. Mọi quyền đều có
    thể tick/tải; thao tác xóa vẫn được khóa ở nút + backend cho Admin.
    File tải trực tiếp từ Google Drive, không đi qua RAM/disk của Render.
    """
    if not selected_ids:
        return
    project = db.project(pid)
    token = _gateway_session_token()
    if not project or not token:
        st.error("Không có phiên Google Drive hợp lệ để tải file.")
        return

    is_drawing = kind == "drawing"
    heading = "bản vẽ" if is_drawing else "hồ sơ"
    icon = "📐" if is_drawing else "📁"
    st.markdown(f"#### ⬇️ Tải {heading} đã chọn")
    st.caption(
        "File được tải **trực tiếp từ Google Drive**, không đi qua Render. "
        "Nếu một dòng có nhiều file, bấm **Tải xuống** tương ứng từng file."
    )
    total_files = 0
    missing: list[str] = []
    seen_file_ids: set[str] = set()

    for rid in selected_ids:
        row = db.drawing(int(rid)) if is_drawing else db.document(int(rid))
        if not row:
            continue
        record_code = str(row["drawing_no"] if is_drawing else row["code"] or "").strip()
        if is_drawing:
            revision = str(row["revision"] or "").strip()
            title = str(row["title"] or "").strip()
            label = record_code + (f" • {revision}" if revision else "") + (f" — {title}" if title else "")
        else:
            subject = str(row["subject"] or "").strip()
            label = record_code + (f" — {subject}" if subject else "")

        files_for_record: list[dict] = []
        try:
            data = _drive_gateway().list_record_files(
                token,
                project_code=project["code"],
                kind=kind,
                subtype=subtype,
                record_code=record_code,
                include_history=False,
            )
            for item in data.get("files") or []:
                fid = str(item.get("id") or "")
                if fid and fid in seen_file_ids:
                    continue
                if fid:
                    seen_file_ids.add(fid)
                files_for_record.append({
                    "id": fid,
                    "name": str(item.get("name") or "file"),
                    "size": item.get("size"),
                    "url": str(item.get("url") or ""),
                    "download_url": str(item.get("download_url") or ""),
                })
        except Exception as exc:
            st.warning(f"Không đọc được file Drive của {record_code}: {exc}")

        # Tương thích metadata Drive cũ từng lưu trong SQLite.
        try:
            legacy_rows = db.drawing_attachments(int(rid)) if is_drawing else db.document_attachments(int(rid))
            for a in legacy_rows:
                fid = str(a["drive_file_id"] or "")
                if not fid or fid in seen_file_ids:
                    continue
                seen_file_ids.add(fid)
                files_for_record.append({
                    "id": fid,
                    "name": str(a["file_name"] or "file"),
                    "size": None,
                    "url": str(a["drive_web_url"] or ""),
                    "download_url": f"https://drive.google.com/uc?export=download&id={fid}",
                })
        except Exception:
            pass

        if not files_for_record:
            missing.append(record_code or f"ID {rid}")
            with st.expander(f"{icon} {label} — chưa có file", expanded=False):
                st.caption("Dòng này chưa có file hiện hành trên Google Drive.")
            continue

        total_files += len(files_for_record)
        with st.expander(f"{icon} {label} — {len(files_for_record)} file", expanded=True):
            for item in files_for_record:
                fid = str(item.get("id") or "")
                name = str(item.get("name") or "file")
                size = _format_drive_size(item.get("size")) if item.get("size") is not None else ""
                download_url = str(item.get("download_url") or "") or (
                    f"https://drive.google.com/uc?export=download&id={fid}" if fid else ""
                )
                open_url = str(item.get("url") or "") or (
                    f"https://drive.google.com/file/d/{fid}/view" if fid else ""
                )
                c1, c2, c3 = st.columns([5.4, 1.2, 1.5])
                c1.markdown(f"**{name}**" + (f"  \n{size}" if size else ""))
                if open_url:
                    c2.link_button("☁ Mở", open_url, width="stretch")
                if download_url:
                    c3.link_button("⬇️ Tải xuống", download_url, width="stretch")

    if total_files:
        st.success(f"Đã tìm thấy {total_files} file của {len(selected_ids)} {heading} đã chọn.")
    if missing:
        st.info("Chưa có file Drive: " + ", ".join(missing))
    if st.button("✖ Đóng danh sách tải", key=panel_key + "_close"):
        st.session_state.pop(panel_key, None)
        st.rerun()


def _render_selected_drawing_downloads(pid: int, drawing_type: str, selected_ids: list[int], panel_key: str) -> None:
    _render_selected_record_downloads(
        pid,
        kind="drawing",
        subtype=drawing_type,
        selected_ids=selected_ids,
        panel_key=panel_key,
    )


def _render_selected_document_downloads(pid: int, doc_type: str, selected_ids: list[int], panel_key: str) -> None:
    _render_selected_record_downloads(
        pid,
        kind="document",
        subtype=doc_type,
        selected_ids=selected_ids,
        panel_key=panel_key,
    )

def render_drawing_type(pid: int, drawing_type: str):
    rows = db.drawings(pid, drawing_type)
    total = len(rows)
    approved = sum(1 for r in rows if r["status"] in {"Chấp thuận", "Chấp thuận có điều kiện"})
    need_fix = sum(1 for r in rows if r["status"] == "Cần sửa")
    c1, c2, c3 = st.columns(3)
    c1.metric("Tổng bản vẽ", total)
    c2.metric("Chấp thuận", approved)
    c3.metric("Cần sửa", need_fix)

    options = [None] + [int(r["id"]) for r in rows]
    select_key = f"drawing_select_{pid}_{drawing_type}"
    pending_key = select_key + "_pending"
    pending = st.session_state.pop(pending_key, None)
    if pending in options:
        st.session_state[select_key] = pending
    selected = st.selectbox(
        "Chọn bản vẽ để sửa / cập nhật",
        options,
        format_func=lambda x: "➕ Thêm mới" if x is None else f"#{x} - {next(r['drawing_no'] for r in rows if r['id']==x)} Rev.{next(r['revision'] for r in rows if r['id']==x)}",
        key=select_key,
    )
    record = db.drawing(selected) if selected else None
    flash_key = f"flash_drawing_{pid}_{drawing_type}"
    if flash_key in st.session_state:
        st.success(st.session_state.pop(flash_key))
    error_flash = flash_key + "_error"
    if error_flash in st.session_state:
        st.error(st.session_state.pop(error_flash))

    with st.form(f"drawing_form_{pid}_{drawing_type}_{selected or 'new'}"):
        c1, c2 = st.columns([1, 2])
        number = c1.text_input("Mã bản vẽ *", value=(record["drawing_no"] if record else ""))
        title = c2.text_input("Tên bản vẽ *", value=(record["title"] if record else ""))
        c1, c2, c3 = st.columns(3)
        discipline = c1.text_input("Bộ môn / Hệ", value=(record["discipline"] if record else ""))
        revision = c2.text_input("Revision", value=(record["revision"] if record else ""), placeholder="Rev.00 / A / C01")
        status_index = DRAWING_STATUSES.index(record["status"]) if record and record["status"] in DRAWING_STATUSES else 0
        status = c3.selectbox("Trạng thái", DRAWING_STATUSES, index=status_index)
        c1, c2 = st.columns(2)
        issuer = c1.text_input("Đơn vị phát hành", value=(record["issuer"] if record else ""))
        receiver = c2.text_input("Người nhận", value=(record["receiver"] if record else ""))
        c1, c2 = st.columns(2)
        received = c1.date_input("Ngày nhận *", value=parse_date(record["received_date"], date.today()) if record else date.today())
        issue_enabled = c2.checkbox("Có ngày phát hành", value=bool(record and record["issue_date"]))
        issue = c2.date_input("Ngày phát hành", value=parse_date(record["issue_date"], date.today()) if record and record["issue_date"] else date.today(), disabled=not issue_enabled)
        related_wbs = st.text_input("WBS / Task / Khu vực liên quan", value=(record["related_wbs"] if record else ""))
        reference = st.text_input("Tham chiếu / Bản vẽ bị thay thế", value=(record["reference_no"] if record else ""))
        note = st.text_area("Ghi chú", value=(record["note"] if record else ""))

        st.caption("V6.0: **Đính kèm file** nằm cạnh **Tải lên**. Khi vùng đính kèm đã mở: chọn tệp rồi bấm **⬆ Tải lên** màu xanh trong khung Google Drive; không tự tải khi vừa chọn file.")
        existing_panel_key = f"v6_drawing_attach_{pid}_{drawing_type}_{selected}" if selected else ""
        panel_is_open = bool(existing_panel_key and st.session_state.get(existing_panel_key + "_upload_open"))
        b_attach, b_save = st.columns([1, 1])
        with b_attach:
            attach_clicked = st.form_submit_button("📎 Đính kèm file", disabled=not _can_update(), width="stretch")
        with b_save:
            save_clicked = st.form_submit_button("⬆️ Tải lên", type="primary", disabled=(not _can_update()) or panel_is_open, width="stretch")

        if attach_clicked or save_clicked:
            if not number.strip() or not title.strip():
                st.error("Mã bản vẽ và Tên bản vẽ là bắt buộc trước khi đính kèm/cập nhật.")
            else:
                try:
                    drawing_id = db.save_drawing(pid, drawing_type, {
                        "drawing_no": number, "title": title, "discipline": discipline, "revision": revision,
                        "issuer": issuer, "receiver": receiver, "received_date": iso(received),
                        "issue_date": iso(issue) if issue_enabled else "", "status": status,
                        "related_wbs": related_wbs, "reference_no": reference, "note": note,
                    }, selected)
                    st.session_state[pending_key] = drawing_id
                    panel_key = f"v6_drawing_attach_{pid}_{drawing_type}_{drawing_id}"
                    try:
                        _prepare_inline_upload_ticket(
                            pid, kind="drawing", subtype=drawing_type, record_code=number.strip(), panel_key=panel_key
                        )
                        if attach_clicked:
                            st.session_state[flash_key] = "Đã lưu bản vẽ và mở vùng chọn file. Chọn tệp rồi bấm Tải lên trong khung Google Drive."
                        else:
                            st.session_state[flash_key] = "Đã lưu/cập nhật bản vẽ và chuẩn bị vùng tải. Chọn tệp rồi bấm Tải lên trong khung Google Drive."
                    except Exception as exc:
                        st.session_state[error_flash] = f"Đã lưu bản vẽ nhưng chưa mở được vùng tải file: {exc}"
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error("Mã bản vẽ + Revision này đã tồn tại trong cùng nhóm.")

    if selected:
        current = db.drawing(selected)
        if current:
            panel_key = f"v6_drawing_attach_{pid}_{drawing_type}_{selected}"
            _render_inline_drive_attachments(
                pid,
                kind="drawing",
                subtype=drawing_type,
                record_code=str(current["drawing_no"] or ""),
                record_id=int(selected),
                panel_key=panel_key,
            )

        arows = db.drawing_attachments(selected)
        if arows:
            st.markdown("**File legacy từ V4.x (nếu có)**")
            legacy_delete = []
            for a in arows:
                c0, c1, c2 = st.columns([0.55, 5, 1.5])
                marked = c0.checkbox("Xóa", key=f"legacy_drawing_tick_{a['id']}", disabled=not _is_admin(), label_visibility="collapsed")
                content = bytes(a["file_content"] or b"")
                if content:
                    c1.download_button(f"⬇️ {a['file_name']}", content, file_name=a["file_name"], mime=a["mime_type"] or "application/octet-stream", key=f"drawing_dl_{a['id']}")
                elif a["drive_web_url"]:
                    c1.link_button(f"☁ {a['file_name']}", a["drive_web_url"])
                    if a["drive_file_id"]:
                        c2.link_button("⬇️ Tải xuống", f"https://drive.google.com/uc?export=download&id={a['drive_file_id']}", width="stretch")
                else:
                    c1.caption(f"{a['file_name']} — file cũ chỉ lưu đường dẫn desktop.")
                if marked:
                    legacy_delete.append(a)
            if _is_admin() and st.button(f"🗑 Xóa file legacy đã tick ({len(legacy_delete)})", disabled=not legacy_delete, key=f"legacy_drawing_delete_{selected}"):
                for a in legacy_delete:
                    if a["drive_file_id"]:
                        _trash_drive_file(a["drive_file_id"])
                    db.delete_drawing_attachment(a["id"], selected)
                st.rerun()

    if rows:
        drive_counts = _record_drive_counts(pid, kind="drawing", subtype=drawing_type, record_codes=[r["drawing_no"] for r in rows])
        table_rows = []
        for r in rows:
            info = drive_counts.get(str(r["drawing_no"] or ""), {})
            direct_count = int(info.get("count") or 0)
            legacy_count = int(r["attachment_count"] or 0)
            total_files = direct_count + legacy_count
            file_label = f"✅ Có file ({total_files})" if total_files else "—"
            latest = str(info.get("latest_modified") or "").replace("T", " ").replace("Z", "")[:19] or r["file_updated_at"]
            table_rows.append({
                "Chọn": False, "ID": r["id"], "Mã bản vẽ": r["drawing_no"], "Tên bản vẽ": r["title"], "Bộ môn/Hệ": r["discipline"],
                "Revision": r["revision"], "Đơn vị phát hành": r["issuer"], "Người nhận": r["receiver"],
                "Ngày nhận": r["received_date"], "Ngày phát hành": r["issue_date"], "Trạng thái": r["status"],
                "WBS/Task": r["related_wbs"], "Tham chiếu/Thay thế": r["reference_no"], "File DB": file_label,
                "Cập nhật file gần nhất": latest, "Ghi chú": r["note"],
            })
        df = pd.DataFrame(table_rows)
        # V6 Render: cột Chọn dùng chung cho tải xuống và xóa. Mọi quyền đều được tick để tải;
        # chỉ Admin mới được dùng nút xóa.
        disabled_cols = [c for c in df.columns if c != "Chọn"]
        edited = st.data_editor(
            df, hide_index=True, width="stretch", key=f"drawing_select_grid_{pid}_{drawing_type}_{len(rows)}_{sum(int(r['id']) for r in rows)}",
            disabled=disabled_cols,
            column_config={
                "Chọn": st.column_config.CheckboxColumn(
                    "☑ Chọn",
                    help="Tick bản vẽ cần tải xuống. Admin cũng có thể xóa các bản vẽ đã tick.",
                    default=False,
                )
            },
        )
        selected_ids = [int(v) for v in edited.loc[edited["Chọn"] == True, "ID"].tolist()]
        download_state_key = f"drawing_download_selected_state_{pid}_{drawing_type}"
        d1, d2, d3 = st.columns([1.45, 1.35, 3.6])
        if d1.button(
            f"⬇️ Tải bản vẽ đã chọn ({len(selected_ids)})",
            key=f"drawing_download_selected_{pid}_{drawing_type}",
            disabled=not selected_ids,
            type="primary",
            width="stretch",
        ):
            st.session_state[download_state_key] = list(selected_ids)

        if d2.button(
            f"🗑 Xóa bản vẽ đã chọn ({len(selected_ids)})",
            key=f"drawing_delete_selected_{pid}_{drawing_type}",
            disabled=(not _is_admin()) or not selected_ids,
            width="stretch",
        ):
            errors = []
            deleted = 0
            for rid in selected_ids:
                row = db.drawing(rid)
                if not row:
                    continue
                _, drive_errors = _trash_record_drive_files(pid, kind="drawing", subtype=drawing_type, record_code=str(row["drawing_no"] or ""))
                if drive_errors:
                    errors.append(f"#{rid}: " + " | ".join(drive_errors))
                    continue
                db.delete_drawing(rid)
                deleted += 1
            if selected in selected_ids:
                st.session_state[pending_key] = None
            st.session_state.pop(download_state_key, None)
            if deleted:
                st.success(f"Đã xóa {deleted} bản vẽ đã chọn.")
            if errors:
                st.error("Một số bản vẽ chưa xóa được vì lỗi Google Drive: " + " || ".join(errors))
            st.rerun()
        d3.caption("☑ Một dấu tick dùng chung → **Tải bản vẽ đã chọn**; riêng Admin mới được dùng **Xóa**.")

        download_ids = [int(x) for x in (st.session_state.get(download_state_key) or [])]
        if download_ids:
            _render_selected_drawing_downloads(pid, drawing_type, download_ids, download_state_key)
        export_df = df.drop(columns=["Chọn"])
        st.download_button("⬇️ Xuất Excel", to_excel_bytes(export_df, DRAWING_TYPES[drawing_type]),
                           file_name=f"{drawing_type}_{date.today():%Y%m%d}.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key=f"drawing_xlsx_{pid}_{drawing_type}")


def render_drawings(pid: int):
    st.subheader("📐 Quản lý bản vẽ")
    st.caption("Shopdrawing • BV phát hành TKTC • BV cập nhật • BV hoàn công • Đính kèm Google Drive 2 GB/file")
    keys = ["SHOPDRAWING", "ISSUED_DESIGN", "UPDATED", "AS_BUILT"]
    tabs = st.tabs([DRAWING_TYPES[k] for k in keys])
    for tab, key in zip(tabs, keys):
        with tab:
            render_drawing_type(pid, key)


def render_reports(pid: int):
    st.subheader("📊 Báo cáo trực quan")
    project = db.project(pid)
    if project:
        st.caption(f"Dự án: {project['code']} - {project['name']}")

    tasks = db.tasks(pid)
    total_tasks = len(tasks)
    planned_avg = sum(float(t["planned_progress"] or 0) for t in tasks) / total_tasks if total_tasks else 0
    actual_avg = sum(float(t["actual_progress"] or 0) for t in tasks) / total_tasks if total_tasks else 0
    delayed = sum(1 for t in tasks if (t["status"] or "") == "Chậm tiến độ")
    completed = sum(1 for t in tasks if (t["status"] or "") == "Hoàn thành")
    delay_pct = delayed * 100 / total_tasks if total_tasks else 0
    done_pct = completed * 100 / total_tasks if total_tasks else 0

    doc_summary = []
    doc_total_all = 0
    doc_done_all = 0
    doc_labels = {"NCR":"NCR", "RFA":"RFA", "RFI":"RFI", "VO":"VO", "NTCV":"NT công việc", "NTVL":"NT VL đầu vào", "KDVT":"Kiểm định VT"}
    for doc_type, cfg in DOC_CONFIG.items():
        rows = db.documents(pid, doc_type)
        total = len(rows)
        done_set = set(cfg.get("done_statuses", []))
        done = sum(1 for r in rows if (r["status"] or "") in done_set)
        pct = done * 100 / total if total else 0
        doc_summary.append({"Loại": doc_labels.get(doc_type, doc_type), "% xử lý": pct, "Đã xử lý": done, "Tổng": total})
        doc_total_all += total
        doc_done_all += done
    doc_pct_all = doc_done_all * 100 / doc_total_all if doc_total_all else 0

    approved_statuses = {"Chấp thuận", "Chấp thuận có điều kiện"}
    drawing_summary = []
    drawing_total_all = 0
    drawing_approved_all = 0
    for drawing_type, label in DRAWING_TYPES.items():
        rows = db.drawings(pid, drawing_type)
        total = len(rows)
        approved = sum(1 for r in rows if (r["status"] or "") in approved_statuses)
        pct = approved * 100 / total if total else 0
        drawing_summary.append({"Loại": label, "% chấp thuận": pct, "Chấp thuận": approved, "Tổng": total})
        drawing_total_all += total
        drawing_approved_all += approved
    drawing_pct_all = drawing_approved_all * 100 / drawing_total_all if drawing_total_all else 0

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("KH trung bình", f"{planned_avg:.1f}%")
    c2.metric("TT trung bình", f"{actual_avg:.1f}%", f"{actual_avg-planned_avg:+.1f}% so KH")
    c3.metric("Công việc chậm", f"{delay_pct:.1f}%", f"{delayed}/{total_tasks}")
    c4.metric("Hoàn thành", f"{done_pct:.1f}%", f"{completed}/{total_tasks}")
    c5.metric("Hồ sơ đã xử lý", f"{doc_pct_all:.1f}%", f"{doc_done_all}/{doc_total_all}")
    c6.metric("BV đã chấp thuận", f"{drawing_pct_all:.1f}%", f"{drawing_approved_all}/{drawing_total_all}")

    left, right = st.columns(2)
    with left:
        st.markdown("#### KH % và TT %")
        progress_df = pd.DataFrame({"Chỉ tiêu": ["KH trung bình", "TT trung bình"], "Phần trăm": [planned_avg, actual_avg]})
        if px is not None:
            fig = px.bar(progress_df, x="Chỉ tiêu", y="Phần trăm", text_auto=".1f", range_y=[0, 100])
            fig.update_traces(texttemplate="%{y:.1f}%", textposition="outside")
            fig.update_layout(height=340, margin=dict(l=10, r=10, t=15, b=10), showlegend=False, yaxis_title="%")
            st.plotly_chart(fig, width="stretch")
        else:
            st.bar_chart(progress_df.set_index("Chỉ tiêu"))

    with right:
        st.markdown("#### Cơ cấu trạng thái tiến độ")
        task_status = [
            {"Trạng thái": "Hoàn thành", "Số lượng": completed},
            {"Trạng thái": "Đúng/Nhanh", "Số lượng": sum(1 for t in tasks if (t["status"] or "") in ("Đúng tiến độ", "Nhanh tiến độ"))},
            {"Trạng thái": "Chậm", "Số lượng": delayed},
            {"Trạng thái": "Chưa bắt đầu/Khác", "Số lượng": sum(1 for t in tasks if (t["status"] or "") not in ("Hoàn thành", "Đúng tiến độ", "Nhanh tiến độ", "Chậm tiến độ"))},
        ]
        status_df = pd.DataFrame(task_status)
        if px is not None and status_df["Số lượng"].sum() > 0:
            fig = px.pie(status_df, names="Trạng thái", values="Số lượng", hole=0.52)
            fig.update_traces(textposition="inside", textinfo="percent+label")
            fig.update_layout(height=340, margin=dict(l=10, r=10, t=15, b=10), legend_title_text="")
            st.plotly_chart(fig, width="stretch")
        else:
            st.dataframe(status_df, width="stretch", hide_index=True)

    left2, right2 = st.columns(2)
    with left2:
        st.markdown("#### Tỷ lệ xử lý hồ sơ")
        doc_df = pd.DataFrame(doc_summary)
        if not doc_df.empty and px is not None:
            fig = px.bar(doc_df, x="% xử lý", y="Loại", orientation="h", text_auto=".1f", range_x=[0, 100])
            fig.update_traces(texttemplate="%{x:.1f}%", textposition="outside")
            fig.update_layout(height=390, margin=dict(l=10, r=20, t=15, b=10), yaxis_title="", xaxis_title="%")
            st.plotly_chart(fig, width="stretch")
        else:
            st.dataframe(doc_df, width="stretch", hide_index=True)

    with right2:
        st.markdown("#### Tỷ lệ chấp thuận bản vẽ")
        drawing_df = pd.DataFrame(drawing_summary)
        if not drawing_df.empty and px is not None:
            fig = px.bar(drawing_df, x="% chấp thuận", y="Loại", orientation="h", text_auto=".1f", range_x=[0, 100])
            fig.update_traces(texttemplate="%{x:.1f}%", textposition="outside")
            fig.update_layout(height=390, margin=dict(l=10, r=20, t=15, b=10), yaxis_title="", xaxis_title="%")
            st.plotly_chart(fig, width="stretch")
        else:
            st.dataframe(drawing_df, width="stretch", hide_index=True)

    st.caption("Báo cáo được tính trực tiếp từ dữ liệu dự án hiện tại; khi TT%, hồ sơ hoặc bản vẽ thay đổi, mở lại tab này để xem số liệu mới nhất.")

def _legal_click_url(row) -> str:
    """Luôn trả về URL có thể bấm để xem văn bản; TVPL thiếu link thì fallback sang trang tìm kiếm TVPL."""
    try:
        url = str(row["source_url"] or "").strip()
    except Exception:
        url = str((row or {}).get("source_url", "") or "").strip() if isinstance(row, dict) else ""
    if url.startswith(("http://", "https://")):
        return url
    try:
        source_name = str(row["source_name"] or "")
        number = str(row["number"] or "").strip()
        title = str(row["title"] or "").strip()
    except Exception:
        source_name = str((row or {}).get("source_name", "")) if isinstance(row, dict) else ""
        number = str((row or {}).get("number", "")).strip() if isinstance(row, dict) else ""
        title = str((row or {}).get("title", "")).strip() if isinstance(row, dict) else ""
    q = number or title
    if "Thư Viện Pháp Luật" in source_name and q:
        return "https://thuvienphapluat.vn/page/tim-van-ban.aspx?keyword=" + quote_plus(q)
    if q:
        return "https://www.google.com/search?q=" + quote_plus(q)
    return ""


def render_legal_documents():
    st.subheader("📚 Văn bản QLDA Xây dựng")
    st.caption("Luật • Nghị định • Thông tư • QCVN • TCVN • Quyết định • Dự thảo — TVPL là nguồn tra cứu chính/ưu tiên; luôn giữ link để mở văn bản trực tiếp.")

    last = legal_repo.last_sync()
    if last:
        st.info(f"Cập nhật online gần nhất: **{last['sync_time']}** — {last['source_name']} — {last['status']}")
    else:
        st.info("Chưa có lần cập nhật online. Bấm **Cập nhật tất cả nguồn** để tải danh mục mới nhất.")

    c1, c2, c3, c4, c5 = st.columns(5)
    actions = [
        (c1, "🔄 Cập nhật tất cả", "all"),
        (c2, "⚖️ VBPL / Chính phủ", "vbpl"),
        (c3, "📐 TCVN - VSQI", "vsqi"),
        (c4, "📝 Dự thảo BXD", "moc_drafts"),
        (c5, "📚 Cập nhật TVPL (ưu tiên)", "tvpl"),
    ]
    for col, label, source in actions:
        if col.button(label, width="stretch", key=f"legal_sync_{source}", disabled=not _can_update()):
            with st.spinner("Đang cập nhật metadata online và đường dẫn mở văn bản..."):
                results = sync_all(legal_repo) if source == "all" else [sync_source(legal_repo, source)]
            errors = [r for r in results if r.get("error")]
            total_added = sum(r.get("added", 0) for r in results)
            total_updated = sum(r.get("updated", 0) for r in results)
            crosschecked = sum(r.get("crosschecked", 0) for r in results)
            if errors:
                st.warning("; ".join(f"{r['source']}: {r['error']}" for r in errors))
            msg = f"Cập nhật xong: thêm {total_added} bản ghi, cập nhật {total_updated} bản ghi."
            if crosschecked:
                msg += f" Đã đối chiếu {crosschecked} bản TVPL với nguồn chính thức cùng số hiệu trong kho."
            st.success(msg)
            if source == "tvpl":
                st.session_state["legal_focus_tvpl_after_sync"] = True
            st.rerun()

    with st.expander("🔎 Google / Tìm kiếm online toàn web", expanded=True):
        appcfg = _runtime_app_settings()
        if appcfg.get("google_api_key") and appcfg.get("google_cx"):
            st.success("Google Search API đã cấu hình tại ⚙️ Cài đặt/Secrets. App ưu tiên kết quả Google.")
        else:
            st.info("Google API chưa cấu hình. Tìm tự động dùng engine fallback rộng; có thể cấu hình tại sheet ⚙️ Cài đặt.")
        st.caption("Nguồn chính thức được ưu tiên xếp hạng nhưng KHÔNG giới hạn phạm vi tìm kiếm. Luôn mở nguồn gốc để kiểm tra hiệu lực trước khi áp dụng.")
        st.caption("Trang chỉ định: " + ", ".join(appcfg.get("specified_search_domains", [])) + ". Có thể sửa danh sách tại sheet ⚙️ Cài đặt.")
        q1, q2, qsites, q3 = st.columns([4, 1, 1.2, 1])
        query = q1.text_input("Số hiệu / nội dung cần tìm", placeholder="Ví dụ: Thông tư 06/2021/TT-BXD phân cấp công trình xây dựng; TCVN 5575; QCVN 06", key="legal_web_query")
        if query.strip():
            q3.link_button("Mở Google ↗", f"https://www.google.com/search?q={quote_plus(query.strip())}", width="stretch")
        else:
            q3.button("Mở Google ↗", disabled=True, width="stretch", key="google_disabled")
        if q2.button("Tìm Google/web", type="primary", width="stretch", key="legal_web_search"):
            if not query.strip():
                st.warning("Nhập số hiệu hoặc nội dung cần tìm.")
            else:
                try:
                    with st.spinner("Đang tìm Google / toàn web..."):
                        found = search_online_all(query, google_api_key=appcfg.get("google_api_key"), google_cx=appcfg.get("google_cx"))
                        stats = legal_repo.upsert_many(found, "Tìm kiếm online tổng hợp")
                    st.session_state["legal_web_results"] = found
                    st.session_state["legal_web_results_query"] = query
                    st.success(f"Tìm thấy {len(found)} kết quả; đã thêm {stats['added']}, cập nhật {stats['updated']}.")
                except Exception as exc:
                    st.error(f"Không tìm kiếm online được: {exc}")
        if qsites.button("Tìm trang chỉ định", width="stretch", key="legal_sites_search"):
            if not query.strip():
                st.warning("Nhập số hiệu hoặc nội dung cần tìm.")
            else:
                try:
                    with st.spinner("Đang tìm trong các trang được chỉ định..."):
                        found = search_online_sites(query, domains=appcfg.get("specified_search_domains"), google_api_key=appcfg.get("google_api_key"), google_cx=appcfg.get("google_cx"))
                        stats = legal_repo.upsert_many(found, "Tìm kiếm các trang chỉ định")
                    st.session_state["legal_web_results"] = found
                    st.session_state["legal_web_results_query"] = query + " — các trang chỉ định"
                    st.success(f"Tìm thấy {len(found)} kết quả; đã thêm {stats['added']}, cập nhật {stats['updated']}.")
                except Exception as exc:
                    st.error(f"Không tìm trong các trang chỉ định được: {exc}")

        web_results = st.session_state.get("legal_web_results", [])
        if web_results:
            st.markdown(f"**Kết quả gần nhất:** {st.session_state.get('legal_web_results_query','')}")
            rdf = pd.DataFrame([{
                "Xem": _legal_click_url(d),
                "Loại": d.get("category", ""), "Số hiệu": d.get("number", ""),
                "Tên / trích yếu": d.get("title", ""), "Cơ quan": d.get("issuer", ""),
                "Trạng thái": d.get("status", ""), "Nguồn": d.get("source_name", ""),
                "Mở": d.get("source_url", ""),
            } for d in web_results])
            st.dataframe(rdf, hide_index=True, width="stretch", height=min(500, 80 + 35 * len(rdf)),
                         column_config={
                             "Xem": st.column_config.LinkColumn("Xem", display_text="Mở ↗"),
                             "Mở": st.column_config.LinkColumn("Nguồn", display_text="Mở ↗"),
                         })

    with st.expander("➕ Thêm văn bản tham chiếu thủ công", expanded=False):
        with st.form("manual_legal_doc", clear_on_submit=True):
            a, b = st.columns([1, 2])
            cat = a.selectbox("Loại", ["Luật", "Nghị định", "Thông tư", "Quyết định", "QCVN", "TCVN", "Văn bản khác"])
            number = b.text_input("Số hiệu")
            title = st.text_input("Tên / trích yếu *")
            a, b = st.columns(2)
            issuer = a.text_input("Cơ quan ban hành")
            source_url = b.text_input("Đường dẫn nguồn *")
            if st.form_submit_button("Lưu văn bản", disabled=not _can_update()):
                if not title.strip() or not source_url.strip():
                    st.error("Cần nhập tên văn bản và đường dẫn nguồn.")
                else:
                    legal_repo.upsert_many([{
                        "category": cat, "number": number, "title": title, "issuer": issuer,
                        "issue_date": "", "effective_date": "", "expiry_date": "", "status": "Chưa xác định",
                        "field": "QLDA xây dựng", "source_name": "Thêm thủ công", "source_url": source_url,
                        "is_draft": 0, "note": "Văn bản tham chiếu do người dùng thêm."
                    }])
                    st.success("Đã lưu văn bản tham chiếu.")
                    st.rerun()

    cats = ["Tất cả"] + legal_repo.categories()
    statuses = ["Tất cả"] + legal_repo.statuses()
    sources = ["Tất cả"] + legal_repo.sources()
    if st.session_state.pop("legal_focus_tvpl_after_sync", False):
        tvpl_choice = next((x for x in sources if "Thư Viện Pháp Luật" in x), "Tất cả")
        st.session_state["legal_source"] = tvpl_choice
        st.session_state["legal_keyword"] = ""
    f1, f2, f3, f4 = st.columns([3, 1.2, 1.5, 1.6])
    keyword = f1.text_input("Tìm số hiệu / tên / lĩnh vực", key="legal_keyword")
    category = f2.selectbox("Loại", cats, key="legal_category")
    status = f3.selectbox("Hiệu lực / trạng thái", statuses, key="legal_status")
    source = f4.selectbox("Nguồn", sources, key="legal_source")
    include_drafts = st.checkbox("Hiển thị cả dự thảo đang lấy ý kiến", value=True, key="legal_include_drafts")

    rows = legal_repo.list_documents(keyword, category, status, source, include_drafts)
    total = len(rows)
    active = sum(1 for r in rows if "còn hiệu lực" in (r["status"] or "").lower() and "hết hiệu lực" not in (r["status"] or "").lower())
    drafts = sum(1 for r in rows if r["is_draft"])
    standards = sum(1 for r in rows if r["category"] in ("TCVN", "QCVN", "Dự thảo TCVN", "Dự thảo QCVN"))
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Tổng văn bản", total)
    m2.metric("Còn hiệu lực", active)
    m3.metric("TCVN / QCVN", standards)
    m4.metric("Dự thảo", drafts)

    if not rows:
        st.info("Chưa có dữ liệu phù hợp. Hãy bấm cập nhật online hoặc thay đổi bộ lọc.")
        return

    df = pd.DataFrame([{
        "Xem": _legal_click_url(r),
        "Loại": r["category"], "Số hiệu": r["number"], "Tên / trích yếu": r["title"],
        "Cơ quan": r["issuer"], "Ban hành": r["issue_date"], "Hiệu lực": r["effective_date"],
        "Hết hiệu lực / Hạn góp ý": r["expiry_date"], "Trạng thái": r["status"],
        "Lĩnh vực": r["field"], "Nguồn": r["source_name"], "Mở nguồn": r["source_url"],
        "Cập nhật online": r["online_updated_at"],
    } for r in rows])
    st.dataframe(
        df, hide_index=True, width="stretch", height=min(700, 80 + 35 * len(df)),
        column_config={
            "Xem": st.column_config.LinkColumn("Xem văn bản", display_text="Mở ↗"),
            "Mở nguồn": st.column_config.LinkColumn("Nguồn", display_text="Mở ↗"),
        },
        column_order=["Xem", "Loại", "Số hiệu", "Tên / trích yếu", "Cơ quan", "Ban hành", "Hiệu lực",
                      "Hết hiệu lực / Hạn góp ý", "Trạng thái", "Lĩnh vực", "Nguồn", "Cập nhật online", "Mở nguồn"],
    )
    st.download_button(
        "⬇️ Xuất danh mục Excel", to_excel_bytes(df, "VanBanQLDAXD"),
        file_name=f"Van_ban_QLDA_XD_{date.today():%Y%m%d}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    st.caption("TVPL là nguồn tra cứu pháp luật chính/ưu tiên trong ứng dụng và mỗi bản ghi có nút Xem văn bản. Khi cần viện dẫn pháp lý, nên kiểm tra bản do cơ quan ban hành công bố.")



def _streamlit_secret(name: str, default: str = "") -> str:
    # Render uses Environment Variables. Local/Streamlit can still use st.secrets.
    env_value = os.environ.get(name)
    if env_value is not None and str(env_value).strip() != "":
        return str(env_value)
    try:
        value = st.secrets.get(name, default)
        return str(value or default)
    except Exception:
        return default


def _drive_rbac_enforced() -> bool:
    value = _streamlit_secret("QLDA_DRIVE_ENFORCE_RBAC", "true") or os.environ.get("QLDA_DRIVE_ENFORCE_RBAC", "true")
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _drive_gateway() -> DriveGateway:
    return DriveGateway(config_from_streamlit(st))


def _gateway_session_token() -> str:
    return str(st.session_state.get("qlda_drive_session_token", "") or "")


def _gateway_logout() -> None:
    for key in ("qlda_drive_session_token", "qlda_drive_identity", "qlda_drive_error"):
        st.session_state.pop(key, None)


def _cloud_identity(refresh: bool = False):
    if not _drive_rbac_enforced():
        return {"role": "admin", "email": "", "name": "", "label": "Admin (RBAC tắt)"}
    cached = st.session_state.get("qlda_drive_identity")
    if cached and not refresh:
        return cached
    token = _gateway_session_token()
    if not token:
        return {"role": "unknown", "email": "", "name": "", "label": "Chưa đăng nhập"}
    try:
        data = _drive_gateway().me(token)
        user = dict(data.get("user") or {})
        role = str(user.get("role") or "unknown")
        identity = {
            "role": role,
            "email": str(user.get("email") or ""),
            "name": str(user.get("name") or ""),
            "label": {"read": "Chỉ đọc", "update": "Cập nhật", "admin": "Admin"}.get(role, "Chưa xác định"),
        }
        st.session_state["qlda_drive_identity"] = identity
        st.session_state.pop("qlda_drive_error", None)
        return identity
    except Exception as exc:
        st.session_state["qlda_drive_error"] = str(exc)
        _gateway_logout()
        return {"role": "unknown", "email": "", "name": "", "label": "Chưa đăng nhập"}


def _streamlit_user_email() -> str:
    return str(_cloud_identity().get("email") or "").strip().lower()


def _cloud_access_role() -> str:
    return str(_cloud_identity().get("role") or "unknown")


def _require_cloud_login_and_access():
    """V6.0: app login + Google Drive direct/resumable storage through Apps Script; no Google Cloud Console."""
    if not _drive_rbac_enforced():
        return

    gw = _drive_gateway()
    if not gw.config.configured:
        st.title("🏗️ QLDA Xây dựng V6.0")
        st.error("Chưa cấu hình Google Drive Gateway.")
        st.markdown(
            "V6.0 không dùng Google Cloud Console. Hãy triển khai file `google_drive_appscript/Code.gs` "
            "thành Google Apps Script Web App rồi nhập URL / token vào Render Environment Variables (hoặc st.secrets khi chạy nơi khác)."
        )
        st.code(
            'QLDA_DRIVE_WEBAPP_URL = "https://script.google.com/macros/s/.../exec"\n'
            'QLDA_DRIVE_API_TOKEN = "token-giong-API_TOKEN-trong-Code.gs"\n'
            'QLDA_DRIVE_ENFORCE_RBAC = "true"\n'
            'QLDA_DRIVE_DIRECT_MAX_UPLOAD_MB = "2048"\nQLDA_DRIVE_LEGACY_MAX_UPLOAD_MB = "30"',
            language="toml",
        )
        st.stop()

    try:
        health = gw.health()
    except Exception as exc:
        st.title("🏗️ QLDA Xây dựng V6.0")
        st.error(f"Không kết nối được Google Drive Gateway: {exc}")
        st.caption("Kiểm tra URL phải là deployment /exec và API token phải trùng với Code.gs.")
        st.stop()

    if not bool(health.get("initialized")):
        st.title("🏗️ QLDA Xây dựng V6.0")
        st.info("Lần chạy đầu tiên: tạo tài khoản Admin. Thư mục **QLDA Xây dựng** sẽ tự được tạo trên Google Drive của chủ Apps Script.")
        root = dict(health.get("root") or {})
        if root.get("url"):
            st.link_button("☁ Mở thư mục QLDA Xây dựng", root["url"])
        with st.form("drive_bootstrap_admin"):
            email = st.text_input("Email Admin")
            name = st.text_input("Tên Admin")
            password = st.text_input("Mật khẩu Admin", type="password")
            password2 = st.text_input("Nhập lại mật khẩu", type="password")
            bootstrap = st.text_input("BOOTSTRAP_CODE trong Code.gs", type="password")
            submit = st.form_submit_button("Khởi tạo Admin", type="primary")
        if submit:
            if password != password2:
                st.error("Hai mật khẩu không trùng nhau.")
            else:
                try:
                    gw.bootstrap_admin(email, name, password, bootstrap)
                    st.success("Đã tạo Admin. Hãy đăng nhập.")
                    st.rerun()
                except Exception as exc:
                    st.error(str(exc))
        st.stop()

    if not _gateway_session_token():
        st.title("🏗️ QLDA Xây dựng V6.0")
        st.caption("Google Drive là kho file tập trung. File V6.0 tải trực tiếp theo resumable upload, tối đa 2 GB/file. Không cần Google Cloud Console/OAuth Client/Service Account.")
        with st.form("qlda_drive_login"):
            email = st.text_input("Email")
            password = st.text_input("Mật khẩu", type="password")
            submit = st.form_submit_button("🔐 Đăng nhập", type="primary", width="stretch")
        if submit:
            try:
                result = gw.login(email, password)
                token = str(result.get("session_token") or "")
                if not token:
                    raise DriveGatewayError("Gateway không trả về session token.")
                st.session_state["qlda_drive_session_token"] = token
                st.session_state.pop("qlda_drive_identity", None)
                st.rerun()
            except Exception as exc:
                st.error(str(exc))
        st.caption("Tài khoản do Admin QLDA tạo: Chỉ đọc / Cập nhật / Admin. Quyền Cập nhật chỉ được thêm/sửa/upload; không được xóa. Trên Drive, Read/Update chỉ là Viewer; mọi upload đi qua Gateway.")
        st.stop()

    identity = _cloud_identity(refresh=True)
    if identity.get("role") not in {"read", "update", "admin"}:
        st.title("🏗️ QLDA Xây dựng V6.0")
        st.error(st.session_state.get("qlda_drive_error") or "Phiên đăng nhập không hợp lệ hoặc tài khoản đã bị thu hồi.")
        if st.button("Đăng nhập lại"):
            _gateway_logout()
            st.rerun()
        st.stop()

    with st.sidebar:
        st.caption(f"Người dùng: {identity.get('name') or identity.get('email')}")
        st.caption(f"Email: {identity.get('email')}")
        st.caption("Quyền: " + {"read": "Chỉ đọc", "update": "Cập nhật", "admin": "Admin"}.get(identity.get("role"), ""))
        if st.button("🚪 Đăng xuất", key="qlda_drive_logout"):
            _gateway_logout()
            st.rerun()


def _can_update() -> bool:
    return _cloud_access_role() in {"update", "admin"}


def _is_admin() -> bool:
    return _cloud_access_role() == "admin"


def _trash_drive_file(file_id: str) -> None:
    if not file_id:
        return
    if not _is_admin():
        raise PermissionError("Chỉ Admin mới được xóa file. Quyền Cập nhật chỉ được thêm/sửa/upload.")
    _drive_gateway().trash_file(_gateway_session_token(), file_id)


def _download_drive_file(file_id: str) -> tuple[str, str, bytes]:
    return _drive_gateway().download_bytes(_gateway_session_token(), file_id)


def _upload_doc_files_to_drive(*args, **kwargs):
    raise RuntimeError("V6.0 không nhận file qua Streamlit. Hãy dùng Direct Upload Google Drive.")


def _upload_drawing_files_to_drive(*args, **kwargs):
    raise RuntimeError("V6.0 không nhận file qua Streamlit. Hãy dùng Direct Upload Google Drive.")


def _format_drive_size(value) -> str:
    try:
        n = float(value or 0)
    except Exception:
        n = 0.0
    if n >= 1024 ** 3:
        return f"{n / (1024 ** 3):.2f} GB"
    if n >= 1024 ** 2:
        return f"{n / (1024 ** 2):.1f} MB"
    if n >= 1024:
        return f"{n / 1024:.1f} KB"
    return f"{int(n)} B"


def _render_direct_drive_panel(pid: int, *, kind: str, subtype: str, record_code: str, panel_key: str) -> None:
    """V6.0 file panel: file bytes never pass through Streamlit.

    Streamlit requests a short-lived upload ticket from Apps Script. The user then
    opens the Apps Script uploader, which starts a Google Drive resumable session.
    The browser PUTs chunks straight to that Drive session (up to 2 GB/file).
    """
    st.markdown("#### ☁ File trên Google Drive — Direct Upload V6.0")
    st.caption(
        "Tối đa **2 GB/file**. File không đi qua Streamlit/SQLite và không gửi Base64 qua Apps Script. "
        "File không qua Streamlit/SQLite; Apps Script giữ OAuth và chuyển tiếp chunk thích nghi 2 MB → 1 MB → 512 KiB → 256 KiB vào phiên resumable Google Drive."
    )
    project = db.project(pid)
    if not project:
        st.warning("Không tìm thấy dự án.")
        return
    gw = _drive_gateway()
    token = _gateway_session_token()
    if not token:
        st.warning("Phiên Drive đã hết hạn. Hãy đăng nhập lại.")
        return

    state_key = panel_key + "_ticket"
    upload = st.session_state.get(state_key) or {}

    # Tự tạo ticket khi người dùng có quyền cập nhật để nút upload luôn hiện ngay
    # sau khi lưu/chọn hồ sơ hoặc bản vẽ. File vẫn đi thẳng vào Google Drive.
    if _can_update() and not upload.get("url"):
        try:
            upload = gw.create_upload_ticket(
                token,
                project_code=project["code"],
                kind=kind,
                subtype=subtype,
                record_code=record_code,
            )
            st.session_state[state_key] = upload
        except Exception as exc:
            st.warning(f"Chưa tạo được link tải file: {exc}")
            upload = {}

    c1, c2, c3, c4 = st.columns([1.8, 1, 1, 1])
    if upload.get("url") and _can_update():
        c1.link_button("⬆️ TẢI FILE LÊN GOOGLE DRIVE (2GB)", upload["url"], type="primary", width="stretch")
    else:
        c1.button("⬆️ TẢI FILE LÊN GOOGLE DRIVE (2GB)", disabled=True, key=panel_key + "_upload_disabled", width="stretch")

    if c2.button("🔄 Tạo lại link upload", key=panel_key + "_prepare", disabled=not _can_update(), width="stretch"):
        try:
            upload = gw.create_upload_ticket(
                token,
                project_code=project["code"],
                kind=kind,
                subtype=subtype,
                record_code=record_code,
            )
            st.session_state[state_key] = upload
            st.success("Đã tạo link upload mới, hiệu lực khoảng 30 phút.")
            st.rerun()
        except Exception as exc:
            st.error(f"Không tạo được link tải file: {exc}")

    if c3.button("🔄 Làm mới danh sách", key=panel_key + "_refresh", width="stretch"):
        st.rerun()
    c4.button("⬇️ TẢI XUỐNG", disabled=True, key=panel_key + "_download_hint", help="Các nút tải xuống sẽ hiện bên cạnh từng file Drive ở danh sách phía dưới.", width="stretch")

    include_history = st.checkbox("Hiện cả _Lich_su", value=False, key=panel_key + "_history")
    try:
        data = gw.list_record_files(
            token,
            project_code=project["code"],
            kind=kind,
            subtype=subtype,
            record_code=record_code,
            include_history=include_history,
        )
    except Exception as exc:
        st.error(f"Không đọc được danh sách file trên Drive: {exc}")
        return

    folder = data.get("folder") or {}
    if folder.get("url"):
        st.link_button("📂 Mở đúng thư mục Google Drive", folder["url"], width="content")

    files = data.get("files") or []
    if not files:
        st.info("Thư mục Drive hiện chưa có file. Bấm **⬆️ TẢI FILE LÊN GOOGLE DRIVE (2GB)** để tải trực tiếp.")
        return

    st.caption(f"Drive hiện có {len(files)} file" + (" (gồm lịch sử)" if include_history else ""))
    for idx, item in enumerate(files):
        name = str(item.get("name") or "file")
        size = _format_drive_size(item.get("size"))
        modified = str(item.get("modified_time") or "").replace("T", " ").replace("Z", "")[:19]
        history_mark = " 🕘" if item.get("history") else ""
        a, b, c, d = st.columns([5.4, 1.1, 1.4, 1.1])
        a.markdown(f"**{name}**{history_mark}  \n{size}" + (f" • {modified}" if modified else ""))
        if item.get("url"):
            b.link_button("☁ Mở", item["url"], width="stretch")
        download_url = item.get("download_url") or (
            f"https://drive.google.com/uc?export=download&id={item.get('id','')}" if item.get("id") else ""
        )
        if download_url:
            c.link_button("⬇️ Tải xuống", download_url, width="stretch")
        if d.button("🗑 Xóa", key=f"{panel_key}_trash_{idx}_{item.get('id','')}", disabled=not _is_admin(), width="stretch"):
            try:
                gw.trash_file(token, str(item.get("id") or ""))
                st.success(f"Đã chuyển {name} vào Thùng rác Drive.")
                st.rerun()
            except Exception as exc:
                st.error(str(exc))


def _runtime_app_settings() -> dict:
    """Runtime settings for one Streamlit session. Secrets/env take precedence over manual session values."""
    google_key = (_streamlit_secret("GOOGLE_SEARCH_API_KEY", "") or os.environ.get("GOOGLE_SEARCH_API_KEY", "") or st.session_state.get("cfg_google_api_key", "")).strip()
    google_cx = (_streamlit_secret("GOOGLE_SEARCH_CX", "") or os.environ.get("GOOGLE_SEARCH_CX", "") or st.session_state.get("cfg_google_cx", "")).strip()
    openai_key = (_streamlit_secret("OPENAI_API_KEY", "") or os.environ.get("OPENAI_API_KEY", "") or st.session_state.get("cfg_openai_api_key", "")).strip()
    openai_model = (_streamlit_secret("OPENAI_MODEL", "") or os.environ.get("OPENAI_MODEL", "") or st.session_state.get("cfg_openai_model", "gpt-5-mini") or "gpt-5-mini").strip()
    if "cfg_openai_web_search" not in st.session_state:
        st.session_state["cfg_openai_web_search"] = False
    if "cfg_specified_sites" not in st.session_state:
        st.session_state["cfg_specified_sites"] = "\n".join(DEFAULT_SPECIFIED_SEARCH_DOMAINS)
    domains = []
    for line in str(st.session_state.get("cfg_specified_sites", "")).splitlines():
        d = line.strip().lower().removeprefix("https://").removeprefix("http://").split("/", 1)[0]
        if d.startswith("www."):
            d = d[4:]
        if d and "." in d and d not in domains:
            domains.append(d)
    return {
        "google_api_key": google_key, "google_cx": google_cx,
        "openai_api_key": openai_key, "openai_model": openai_model or "gpt-5-mini",
        "openai_web_search": bool(st.session_state.get("cfg_openai_web_search", False)),
        "specified_search_domains": domains or list(DEFAULT_SPECIFIED_SEARCH_DOMAINS),
    }


def render_settings():
    st.subheader("⚙️ Cài đặt ứng dụng")
    st.caption("Tập trung cấu hình AI • Google Search • Google Drive Gateway/RBAC • website tra cứu. Trên Render, secret đặt tại Service → Environment. Khi chạy nơi khác có thể dùng st.secrets.")
    ai_tab, google_tab, drive_tab, sites_tab, system_tab = st.tabs(["🤖 AI", "🔎 Google Search", "☁ Google Drive & quyền", "🌐 Website tra cứu", "🗄 Hệ thống"])

    with ai_tab:
        secret_ai = bool(_streamlit_secret("OPENAI_API_KEY", "") or os.environ.get("OPENAI_API_KEY", ""))
        if secret_ai:
            st.success("OPENAI_API_KEY đã được cấu hình bằng Secrets/biến môi trường; giá trị không hiển thị trên giao diện.")
        else:
            st.text_input("OpenAI API key", type="password", key="cfg_openai_api_key", help="Chỉ giữ trong session Streamlit; không ghi vào GitHub.")
        default_model = _streamlit_secret("OPENAI_MODEL", "") or os.environ.get("OPENAI_MODEL", "") or st.session_state.get("cfg_openai_model", "gpt-5-mini")
        if "cfg_openai_model" not in st.session_state:
            st.session_state["cfg_openai_model"] = default_model or "gpt-5-mini"
        st.text_input("Model", key="cfg_openai_model")
        st.checkbox("Cho phép Web Search khi AI tra cứu pháp lý", key="cfg_openai_web_search")
        st.caption("Kiểm tra API sẽ phân biệt key sai, hết quota/credit, rate limit, quyền model và lỗi mạng.")
        if st.button("🩺 Kiểm tra OpenAI API", key="settings_test_openai"):
            cfg_now = _runtime_app_settings()
            try:
                test_ai = OpenAIProjectAssistant(DB_PATH, AISettings(
                    api_key=(cfg_now.get("openai_api_key") or "").strip(),
                    model=(cfg_now.get("openai_model") or "gpt-5-mini").strip(),
                    use_web=False,
                ))
                with st.spinner("Đang kiểm tra API key, quota và quyền model..."):
                    msg = test_ai.test_connection()
                st.success(msg)
            except Exception as exc:
                st.error(str(exc))

    with google_tab:
        secret_google = bool((_streamlit_secret("GOOGLE_SEARCH_API_KEY", "") or os.environ.get("GOOGLE_SEARCH_API_KEY", "")) and (_streamlit_secret("GOOGLE_SEARCH_CX", "") or os.environ.get("GOOGLE_SEARCH_CX", "")))
        if secret_google:
            st.success("Google API key và CX đã được cấu hình bằng Secrets/biến môi trường.")
        else:
            st.text_input("Google API key", type="password", key="cfg_google_api_key")
            st.text_input("Search Engine ID (CX)", key="cfg_google_cx")
        st.caption("Nếu không có Google API, app vẫn dùng Bing/DuckDuckGo fallback và có thể mở Google trực tiếp trên trình duyệt.")

    with drive_tab:
        gw = _drive_gateway()
        token = _gateway_session_token()
        ident = _cloud_identity()
        if not gw.config.configured:
            st.error("Chưa cấu hình Drive Gateway. Trên Render hãy đặt QLDA_DRIVE_WEBAPP_URL và QLDA_DRIVE_API_TOKEN tại Service → Environment.")
        elif token and ident.get("role") in {"read", "update", "admin"}:
            try:
                root = dict(gw.root_info(token).get("root") or {})
                st.success(f"Google Drive đã kết nối: {root.get('name') or 'QLDA Xây dựng'}")
                st.write(f"Người dùng: **{ident.get('name') or ident.get('email')}** • Email: **{ident.get('email')}** • Quyền: **{ident.get('label')}**")
                if root.get("url"):
                    st.link_button("☁ Mở thư mục QLDA Xây dựng", root["url"])
                st.caption("File V6.0 tải trực tiếp theo resumable upload, tối đa 2 GB/file. Tự phân loại theo Dự án → Hồ sơ/Bản vẽ → Nhóm → Mã hồ sơ; file trùng tên đưa bản cũ vào _Lich_su.")

                with st.expander("🔑 Đổi mật khẩu của tôi"):
                    with st.form("drive_change_password"):
                        oldp = st.text_input("Mật khẩu hiện tại", type="password", key="drive_oldp")
                        newp = st.text_input("Mật khẩu mới", type="password", key="drive_newp")
                        newp2 = st.text_input("Nhập lại mật khẩu mới", type="password", key="drive_newp2")
                        change = st.form_submit_button("Đổi mật khẩu")
                    if change:
                        if newp != newp2:
                            st.error("Hai mật khẩu mới không trùng nhau.")
                        else:
                            try:
                                gw.change_password(token, oldp, newp)
                                st.success("Đã đổi mật khẩu.")
                            except Exception as exc:
                                st.error(str(exc))

                if ident.get("role") == "admin":
                    st.markdown("### 👥 Phân quyền người dùng")
                    st.caption("Chỉ đọc = Viewer Drive • Cập nhật = Viewer Drive + được thêm/sửa/upload qua app, KHÔNG được xóa • Admin = Editor Drive + toàn quyền quản trị/xóa trong app. Owner Drive vẫn là tài khoản đã deploy Apps Script.")
                    with st.form("drive_user_form"):
                        c1, c2 = st.columns(2)
                        pemail = c1.text_input("Email người dùng")
                        pname = c2.text_input("Tên người dùng")
                        prole = c1.selectbox("Quyền", ["read", "update", "admin"], format_func=lambda x: {"read":"Chỉ đọc","update":"Cập nhật","admin":"Admin"}[x])
                        ppass = c2.text_input("Mật khẩu khởi tạo / mật khẩu mới (để trống nếu không đổi)", type="password")
                        save_user = st.form_submit_button("Thêm / cập nhật người dùng", type="primary")
                    if save_user:
                        try:
                            gw.set_user(token, pemail, pname, prole, ppass)
                            st.success("Đã cập nhật người dùng và quyền Google Drive.")
                            st.rerun()
                        except Exception as exc:
                            st.error(str(exc))

                    try:
                        users = gw.list_users(token)
                    except Exception as exc:
                        users = []
                        st.error(str(exc))
                    if users:
                        udf = pd.DataFrame([{
                            "Tên": u.get("name", ""),
                            "Email": u.get("email", ""),
                            "Quyền": {"read":"Chỉ đọc","update":"Cập nhật","admin":"Admin"}.get(u.get("role", ""), u.get("role", "")),
                            "Hoạt động": "Có" if u.get("active", True) else "Không",
                            "Cập nhật": u.get("updated_at", ""),
                        } for u in users])
                        st.dataframe(udf, hide_index=True, width="stretch")
                        removable = [u for u in users if str(u.get("email") or "").lower() != str(ident.get("email") or "").lower()]
                        if removable:
                            emails = [str(u.get("email") or "") for u in removable]
                            target = st.selectbox("Xóa quyền người dùng", emails, key="drive_delete_user_email")
                            if st.button("🗑️ Xóa người dùng / thu hồi quyền", key="drive_delete_user"):
                                try:
                                    gw.delete_user(token, target)
                                    st.success("Đã xóa người dùng và thu hồi quyền Drive.")
                                    st.rerun()
                                except Exception as exc:
                                    st.error(str(exc))
                else:
                    st.info("Chỉ Admin mới được quản lý tài khoản và phân quyền.")
            except Exception as exc:
                st.error(f"Không đọc được Google Drive Gateway: {exc}")
        else:
            st.info("Chưa có phiên đăng nhập Drive Gateway.")

        st.markdown("### Cấu hình Render Environment")
        st.code(
            'QLDA_DRIVE_WEBAPP_URL = "https://script.google.com/macros/s/.../exec"\n'
            'QLDA_DRIVE_API_TOKEN = "token-giong-API_TOKEN-trong-Code.gs"\n'
            'QLDA_DRIVE_ENFORCE_RBAC = "true"\n'
            'QLDA_DRIVE_DIRECT_MAX_UPLOAD_MB = "2048"\nQLDA_DRIVE_LEGACY_MAX_UPLOAD_MB = "30"',
            language="toml",
        )
        st.caption("Không cần GOOGLE_DRIVE_ROOT_FOLDER_ID, Google OAuth Client, Service Account hay Google Cloud Console. Thư mục QLDA Xây dựng tự được tạo bởi Apps Script.")

    with sites_tab:
        if "cfg_specified_sites" not in st.session_state:
            st.session_state["cfg_specified_sites"] = "\n".join(DEFAULT_SPECIFIED_SEARCH_DOMAINS)
        st.text_area("Website dùng cho nút ‘Tìm trang chỉ định’ — mỗi dòng một domain", key="cfg_specified_sites", height=260)
        c1, c2 = st.columns([1, 4])
        def _reset_sites():
            st.session_state["cfg_specified_sites"] = "\n".join(DEFAULT_SPECIFIED_SEARCH_DOMAINS)
        c1.button("Khôi phục mặc định", width="stretch", on_click=_reset_sites)
        c2.caption("Có thể thêm thuvienphapluat.vn hoặc website tra cứu phù hợp. TVPL được ưu tiên trong sheet Văn bản; link gốc luôn được giữ để mở trực tiếp.")

    with system_tab:
        st.code(str(DB_PATH), language=None)
        if IS_RENDER:
            st.success(f"Đang chạy trên Render • service: {os.environ.get('RENDER_SERVICE_NAME', 'QLDA V6.0')}")
            persistent = str(os.environ.get("QLDA_RENDER_PERSISTENT_DISK", "false")).lower() in {"1", "true", "yes", "on"}
            if persistent and str(DB_PATH).startswith("/var/data/"):
                st.success("SQLite đang dùng Render Persistent Disk tại /var/data.")
            else:
                st.warning("SQLite chưa được xác nhận là persistent. Hãy gắn Render Persistent Disk tại /var/data và đặt QLDA_DB_PATH=/var/data/qlda_cloud.db.")
        st.caption("Trên Render, nên đặt SQLite tại /var/data/qlda_cloud.db và gắn Persistent Disk vào /var/data. Nếu không có disk, filesystem là tạm thời.")
        st.info("Cấu hình bền vững trên Render nên dùng Service → Environment. Không commit API key/token vào GitHub.")

    cfg = _runtime_app_settings()
    st.success(f"Cấu hình hiện tại: AI {'✓' if cfg['openai_api_key'] else '–'} • Google {'✓' if cfg['google_api_key'] and cfg['google_cx'] else '–'} • {len(cfg['specified_search_domains'])} website chỉ định")


def render_ai_assistant(pid: int):
    st.subheader("🤖 Trợ lý AI QLDA")
    st.caption("Chat với dự án • Rủi ro tiến độ • Dự thảo báo cáo • Đọc hồ sơ • Tra cứu văn bản. AI chỉ đưa ra đề xuất; người dùng vẫn là người phê duyệt/kết luận.")

    appcfg = _runtime_app_settings()
    settings = AISettings(
        api_key=(appcfg.get("openai_api_key") or "").strip(),
        model=(appcfg.get("openai_model") or "gpt-5-mini").strip(),
        use_web=bool(appcfg.get("openai_web_search", False)),
    )
    if settings.api_key:
        st.success(f"AI đã cấu hình • Model: {settings.model} • Web Search: {'Bật' if settings.use_web else 'Tắt'} • chỉnh tại sheet ⚙️ Cài đặt")
    else:
        st.warning("Chưa có OPENAI_API_KEY. Vào sheet ⚙️ Cài đặt để cấu hình.")
    ai = OpenAIProjectAssistant(DB_PATH, settings)
    ctx_builder = ProjectContextBuilder(DB_PATH)
    tab_chat, tab_risk, tab_file, tab_legal = st.tabs(["💬 Chat với dự án", "📈 Rủi ro & báo cáo", "📎 Đọc hồ sơ", "⚖️ Văn bản AI"])

    with tab_chat:
        hkey = f"ai_history_{pid}"
        if hkey not in st.session_state:
            st.session_state[hkey] = []
        c1, c2 = st.columns([1, 5])
        if c1.button("Xóa chat", key=f"ai_clear_{pid}", width="stretch"):
            st.session_state[hkey] = []
            st.rerun()
        c2.caption("AI nhận snapshot dự án hiện tại: tiến độ, hồ sơ, bản vẽ và metadata văn bản. Không gửi toàn bộ file đính kèm trừ khi anh yêu cầu ở tab Đọc hồ sơ.")
        for msg in st.session_state[hkey]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
        q = st.chat_input("Hỏi về dự án: công việc trễ, RFI/NCR/VO, bản vẽ, rủi ro...", key=f"ai_chat_{pid}")
        if q:
            previous = list(st.session_state[hkey])
            st.session_state[hkey].append({"role": "user", "content": q})
            with st.chat_message("user"):
                st.markdown(q)
            try:
                with st.chat_message("assistant"):
                    with st.spinner("AI đang phân tích dữ liệu dự án..."):
                        answer = ai.ask_project(pid, q, previous, date.today(), use_web=False)
                    st.markdown(answer)
                st.session_state[hkey].append({"role": "assistant", "content": answer})
            except Exception as exc:
                st.error(str(exc))

    with tab_risk:
        status_date = st.date_input("Ngày báo cáo AI", value=date.today(), key=f"ai_status_date_{pid}")
        r1, r2, r3 = st.columns(3)
        if r1.button("⚠️ Phân tích rủi ro tiến độ", type="primary", width="stretch", key=f"ai_risk_{pid}"):
            try:
                with st.spinner("Đang xếp hạng rủi ro..."):
                    st.session_state[f"ai_analysis_{pid}"] = ai.analyze_schedule_risk(pid, status_date)
            except Exception as exc: st.error(str(exc))
        if r2.button("📝 Soạn báo cáo tuần", width="stretch", key=f"ai_week_{pid}"):
            try:
                with st.spinner("Đang soạn báo cáo tuần..."):
                    st.session_state[f"ai_analysis_{pid}"] = ai.draft_report(pid, "tuần", status_date)
            except Exception as exc: st.error(str(exc))
        if r3.button("📝 Soạn báo cáo tháng", width="stretch", key=f"ai_month_{pid}"):
            try:
                with st.spinner("Đang soạn báo cáo tháng..."):
                    st.session_state[f"ai_analysis_{pid}"] = ai.draft_report(pid, "tháng", status_date)
            except Exception as exc: st.error(str(exc))
        text = st.session_state.get(f"ai_analysis_{pid}", "")
        if text:
            st.markdown(text)
            st.download_button("⬇️ Tải kết quả AI (.md)", text.encode("utf-8"), file_name=f"AI_report_{pid}_{date.today():%Y%m%d}.md", mime="text/markdown", key=f"ai_report_dl_{pid}")

    with tab_file:
        st.info("AI có thể đọc file được chọn và đối chiếu với bối cảnh dự án. V4.0 giới hạn 25 MB/file để kiểm soát thời gian và chi phí.")
        catalog = ctx_builder.attachment_catalog(pid)
        options = [None] + [int(x["id"]) for x in catalog]
        by_id = {int(x["id"]): x for x in catalog}
        selected = st.selectbox(
            "File hồ sơ đã lưu",
            options,
            format_func=lambda x: "— Chọn file đã lưu —" if x is None else f"{by_id[x].get('doc_type','')} {by_id[x].get('code','')} — {by_id[x].get('file_name') or Path(by_id[x].get('file_path') or '').name}",
            key=f"ai_attachment_{pid}",
        )
        upload = st.file_uploader("Hoặc tải file trực tiếp cho AI", type=["pdf","docx","xlsx","xls","txt","csv","png","jpg","jpeg"], key=f"ai_upload_{pid}")
        instruction = st.text_area("Yêu cầu AI", placeholder="Ví dụ: tóm tắt, trích thông số, liệt kê hồ sơ thiếu, các điểm cần kiểm tra...", key=f"ai_file_instruction_{pid}")
        f1, f2 = st.columns(2)
        if f1.button("Phân tích file đã lưu", disabled=selected is None, width="stretch", key=f"ai_saved_file_{pid}"):
            try:
                meta = by_id.get(int(selected), {}) if selected is not None else {}
                if meta.get("drive_file_id"):
                    name, mime, data = _download_drive_file(str(meta.get("drive_file_id")))
                else:
                    name, mime, data = ctx_builder.load_attachment(int(selected))
                with st.spinner(f"AI đang đọc {name}..."):
                    st.session_state[f"ai_file_result_{pid}"] = ai.summarize_file(pid, name, data, instruction, date.today())
            except Exception as exc: st.error(str(exc))
        if f2.button("Phân tích file tải lên", disabled=upload is None, width="stretch", key=f"ai_uploaded_file_{pid}"):
            try:
                with st.spinner(f"AI đang đọc {upload.name}..."):
                    st.session_state[f"ai_file_result_{pid}"] = ai.summarize_file(pid, upload.name, upload.getvalue(), instruction, date.today())
            except Exception as exc: st.error(str(exc))
        file_result = st.session_state.get(f"ai_file_result_{pid}", "")
        if file_result:
            st.markdown(file_result)

    with tab_legal:
        st.caption("AI ưu tiên các văn bản đã đồng bộ trong sheet Văn bản QLDA XD. Nếu bật Web Search, AI có thể kiểm tra thêm nguồn online; vẫn cần mở văn bản gốc để xác nhận điều khoản.")
        lq = st.text_area("Câu hỏi pháp lý/tiêu chuẩn", placeholder="Ví dụ: Các văn bản trong kho liên quan quản lý chất lượng và nghiệm thu vật liệu đầu vào?", key=f"ai_legal_q_{pid}")
        if st.button("Tra cứu văn bản bằng AI", type="primary", disabled=not bool(lq.strip()), key=f"ai_legal_btn_{pid}"):
            try:
                with st.spinner("AI đang tra cứu văn bản..."):
                    st.session_state[f"ai_legal_result_{pid}"] = ai.legal_qa(pid, lq, date.today(), use_web=allow_web)
            except Exception as exc: st.error(str(exc))
        legal_result = st.session_state.get(f"ai_legal_result_{pid}", "")
        if legal_result:
            st.markdown(legal_result)


def render_project_info(pid: int):
    p = db.project(pid)
    st.subheader("⚙️ Thông tin dự án")
    with st.form(f"project_edit_{pid}"):
        c1, c2 = st.columns([1, 2])
        code = c1.text_input("Mã dự án", value=p["code"])
        name = c2.text_input("Tên dự án", value=p["name"])
        c1, c2 = st.columns(2)
        start = c1.date_input("Bắt đầu", value=parse_date(p["start_date"], date.today()))
        end = c2.date_input("Kết thúc", value=parse_date(p["end_date"], date.today()+timedelta(days=365)))
        manager = st.text_input("Quản lý dự án", value=p["manager"] or "")
        note = st.text_area("Ghi chú", value=p["note"] or "")
        if st.form_submit_button("Lưu thông tin", type="primary", disabled=not _is_admin()):
            try:
                db.update_project(pid, code, name, iso(start), iso(end), manager, note)
                st.success("Đã cập nhật dự án.")
                st.rerun()
            except sqlite3.IntegrityError:
                st.error("Mã dự án đã được sử dụng.")
    st.divider()
    st.warning("Xóa dự án sẽ xóa toàn bộ tiến độ, hồ sơ, bản vẽ và file đính kèm thuộc dự án này.")
    confirm = st.checkbox("Tôi xác nhận muốn xóa dự án", key=f"confirm_del_project_{pid}")
    if st.button("🗑️ Xóa dự án", disabled=(not confirm or not _is_admin()), key=f"del_project_{pid}"):
        db.delete_project(pid)
        st.session_state.pop("project_id", None)
        st.rerun()


_require_cloud_login_and_access()
sidebar_project_tools()
pid, projects = project_selector()

st.title("🏗️ QLDA Xây dựng V6.0 • Drive Attach 2GB")
st.caption("File Hồ sơ/Bản vẽ không đi qua Streamlit; Apps Script chuyển tiếp chunk vào Google Drive resumable upload, tối đa 2 GB/file.")
if not pid:
    st.info("Hãy tạo dự án đầu tiên ở thanh bên trái.")
    st.stop()

p = db.project(pid)
st.caption(f"Dự án: **{p['code']} - {p['name']}**")
_role = _cloud_access_role()
_email = _streamlit_user_email()
_role_label = {"read":"Chỉ đọc","update":"Cập nhật","admin":"Admin","unknown":"Chưa xác định"}.get(_role, _role)
st.info(f"Quyền hiện tại: **{_role_label}**" + (f" • {_email}" if _email else ""))

main_tabs = st.tabs(["📅 Quản lý tiến độ", "📁 Quản lý hồ sơ", "📐 Quản lý bản vẽ", "📊 Báo cáo trực quan", "📚 Văn bản QLDA XD", "🤖 Trợ lý AI", "⚙️ Cài đặt", "🏗️ Dự án"])
with main_tabs[0]:
    render_schedule(pid)
with main_tabs[1]:
    render_documents(pid)
with main_tabs[2]:
    render_drawings(pid)
with main_tabs[3]:
    render_reports(pid)
with main_tabs[4]:
    render_legal_documents()
with main_tabs[5]:
    render_ai_assistant(pid)
with main_tabs[6]:
    render_settings()
with main_tabs[7]:
    render_project_info(pid)
