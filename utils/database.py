# -*- coding: utf-8 -*-
"""
طبقة التخزين الموحدة لطلبات الاستشارات — بوضعين تلقائيين:

1) Google Sheets (للنشر السحابي):
   يُفعَّل تلقائياً عند توفر [gcp_service_account] و [sheets] في st.secrets.
   كل طلب يُضاف صفاً دائماً في جدولك — لا يُفقد عند إعادة تشغيل التطبيق.

2) SQLite محلي (للتشغيل على جهازك):
   الوضع الاحتياطي عند غياب إعدادات السحابة — ملف داخل مجلد data/.

قاعدة أمان مقصودة: إذا كانت إعدادات Google Sheets موجودة لكن الاتصال فشل،
نرفع خطأً واضحاً ولا نتحول بصمت إلى SQLite — حتى لا تُحفظ طلبات العملاء
في تخزين مؤقت يُمسح على المنصة السحابية دون أن تشعر.

واجهة الاستخدام ثابتة في كل التطبيق:
initialize_db() / save_request(...) / get_all_requests() / get_backend_name()
"""

import sqlite3
from datetime import datetime
from pathlib import Path

import pandas as pd

COLUMNS = ["id", "created_at", "name", "email", "phone",
           "service_type", "details", "pdpl_consent"]

DB_DIR = Path(__file__).resolve().parent.parent / "data"
DB_PATH = DB_DIR / "consultation_requests.db"
TABLE_NAME = "consultation_requests"

# تخزين مؤقت لاتصال ورقة العمل على مستوى العملية (يتجنب إعادة المصادقة مع كل تفاعل)
_WS_CACHE = {"ws": None}


# ==================================================================
# اكتشاف الوضع السحابي
# ==================================================================
def _load_sheets_secrets():
    """يعيد (بيانات حساب الخدمة، مفتاح الجدول) أو None عند غياب الإعدادات."""
    try:
        import streamlit as st
        secrets = st.secrets  # قد يرفع استثناء محلياً عند غياب secrets.toml
        if "gcp_service_account" in secrets and "sheets" in secrets:
            sa_info = dict(secrets["gcp_service_account"])
            key = str(secrets["sheets"].get("spreadsheet_key", "")).strip()
            if sa_info and key:
                return sa_info, key
    except Exception:
        pass
    return None


def _get_worksheet():
    """
    إرجاع ورقة العمل الأولى من جدول Google، أو None إذا لم تكن الإعدادات موجودة.
    يرفع RuntimeError برسالة عربية واضحة إذا كانت الإعدادات موجودة والاتصال فشل.
    """
    if _WS_CACHE["ws"] is not None:
        return _WS_CACHE["ws"]

    cfg = _load_sheets_secrets()
    if cfg is None:
        return None  # وضع محلي — SQLite

    try:
        import gspread
        from google.oauth2.service_account import Credentials
    except ImportError as exc:
        raise RuntimeError(
            "إعدادات Google Sheets موجودة في Secrets لكن المكتبات غير مثبتة. "
            "نفّذ: pip install gspread google-auth — أو تأكد من وجودهما في requirements.txt"
        ) from exc

    sa_info, key = cfg
    try:
        creds = Credentials.from_service_account_info(
            sa_info, scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
        client = gspread.authorize(creds)
        ws = client.open_by_key(key).sheet1
        # قراءة تجريبية للتحقق من الصلاحيات قبل اعتماد الاتصال
        ws.get_values("A1")
    except Exception as exc:
        raise RuntimeError(
            "تعذر الاتصال بجدول Google Sheets. راجع بالترتيب: "
            "(1) مشاركة الجدول مع بريد حساب الخدمة client_email بصلاحية Editor، "
            "(2) صحة spreadsheet_key المنسوخ من رابط الجدول، "
            "(3) سلامة private_key في Secrets (يجب أن يبقى \\n كما هو دون أسطر فعلية)."
        ) from exc

    _WS_CACHE["ws"] = ws
    return ws


def get_backend_name() -> str:
    """اسم مصدر التخزين الحالي — يُعرض في لوحة التحكم للتشخيص السريع."""
    try:
        ws = _get_worksheet()
    except RuntimeError:
        return "⚠️ Google Sheets — فشل الاتصال (راجع Secrets)"
    if ws is not None:
        return "Google Sheets — تخزين سحابي دائم ✅"
    return "SQLite — ملف محلي (وضع التشغيل على الجهاز)"


# ==================================================================
# تنفيذ وضع Google Sheets
# ==================================================================
def _sheets_initialize(ws) -> None:
    """إنشاء صف الترويسة إذا كان الجدول فارغاً."""
    if not ws.get_all_values():
        ws.append_row(COLUMNS, value_input_option="RAW")


def _sheets_save(ws, created_at, name, email, phone,
                 service_type, details, pdpl_consent) -> int:
    _sheets_initialize(ws)
    # صف الترويسة = الصف 1، لذا عدد الصفوف الحالي = الرقم التسلسلي التالي
    next_id = len(ws.get_all_values())
    ws.append_row(
        [next_id, created_at, name, email, phone, service_type, details,
         1 if pdpl_consent else 0],
        value_input_option="RAW",  # RAW يحفظ الجوال كنص ويحمي الصفر في بدايته
    )
    return next_id


def _sheets_fetch(ws) -> pd.DataFrame:
    _sheets_initialize(ws)
    records = ws.get_all_records()
    if not records:
        return pd.DataFrame(columns=COLUMNS)
    df = pd.DataFrame(records)
    for col in COLUMNS:
        if col not in df.columns:
            df[col] = ""
    df = df[COLUMNS]
    df["id"] = pd.to_numeric(df["id"], errors="coerce").fillna(0).astype(int)
    df["pdpl_consent"] = pd.to_numeric(df["pdpl_consent"], errors="coerce").fillna(0).astype(int)
    return df.sort_values("id", ascending=False).reset_index(drop=True)


# ==================================================================
# تنفيذ وضع SQLite المحلي
# ==================================================================
def _get_connection() -> sqlite3.Connection:
    DB_DIR.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH, timeout=15)


def _sqlite_initialize() -> None:
    with _get_connection() as conn:
        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at    TEXT    NOT NULL,
                name          TEXT    NOT NULL,
                email         TEXT,
                phone         TEXT    NOT NULL,
                service_type  TEXT    NOT NULL,
                details       TEXT,
                pdpl_consent  INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        conn.commit()


# ==================================================================
# الواجهة الموحدة المستخدمة في بقية التطبيق
# ==================================================================
def initialize_db() -> None:
    """تهيئة وجهة التخزين النشطة (ترويسة الجدول السحابي أو جدول SQLite)."""
    ws = _get_worksheet()
    if ws is not None:
        _sheets_initialize(ws)
        return
    _sqlite_initialize()


def save_request(
    name: str,
    email: str,
    phone: str,
    service_type: str,
    details: str,
    pdpl_consent: bool,
) -> int:
    """حفظ طلب استشارة جديد وإرجاع رقمه التسلسلي المرجعي."""
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    name = (name or "").strip()
    email = (email or "").strip()
    phone = (phone or "").strip()
    service_type = (service_type or "").strip()
    details = (details or "").strip()

    ws = _get_worksheet()
    if ws is not None:
        return _sheets_save(ws, created_at, name, email, phone,
                            service_type, details, pdpl_consent)

    _sqlite_initialize()
    with _get_connection() as conn:
        cursor = conn.execute(
            f"""
            INSERT INTO {TABLE_NAME}
                (created_at, name, email, phone, service_type, details, pdpl_consent)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (created_at, name, email, phone, service_type, details,
             1 if pdpl_consent else 0),
        )
        conn.commit()
        return int(cursor.lastrowid)


def get_all_requests() -> pd.DataFrame:
    """جلب جميع الطلبات مرتبة من الأحدث إلى الأقدم من وجهة التخزين النشطة."""
    ws = _get_worksheet()
    if ws is not None:
        return _sheets_fetch(ws)

    _sqlite_initialize()
    with _get_connection() as conn:
        df = pd.read_sql_query(
            f"SELECT * FROM {TABLE_NAME} ORDER BY id DESC", conn
        )
    return df
