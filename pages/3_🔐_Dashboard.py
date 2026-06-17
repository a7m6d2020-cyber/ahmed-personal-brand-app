# -*- coding: utf-8 -*-
"""
لوحة التحكم (Admin Dashboard) — محمية بكلمة مرور لمستخدم واحد.
عرض طلبات الاستشارات وتصديرها كملف CSV/Excel محلياً.
"""

import io
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.database import get_all_requests, get_backend_name

# ==================================================================
# ⚠️ أمن الوصول: غيّر كلمة المرور التالية قبل أي استخدام فعلي،
# ولا تشارك ملف الكود مع أي طرف بعد تغييرها.
# ==================================================================
def _get_admin_password() -> str:
    """كلمة مرور اللوحة من st.secrets عند توفرها، وإلا القيمة الافتراضية المحلية.
    عند النشر اضبط [admin] password في Secrets ولا تترك الافتراضية."""
    try:
        if "admin" in st.secrets and st.secrets["admin"].get("password"):
            return str(st.secrets["admin"]["password"])
    except Exception:
        pass
    return "Admin@2026"


ADMIN_PASSWORD = _get_admin_password()

st.set_page_config(
    page_title="لوحة التحكم | أحمد المعمري",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded",
)

GLOBAL_CSS = """
<style>
    .stApp { background-color: #FDFBF7; }
    [data-testid="stHeader"] { background-color: #FDFBF7; }
    #MainMenu, footer { visibility: hidden; }

    html, body, .stApp, .stMarkdown, [data-testid="stSidebar"] {
        direction: rtl;
        font-family: "IBM Plex Sans Arabic", "Tajawal", "Segoe UI", Tahoma, Arial, sans-serif;
    }
    h1, h2, h3, h4, h5, h6 { color: #1E2A38 !important; text-align: right; }
    .stMarkdown p, .stMarkdown li, label, [data-testid="stWidgetLabel"] p { color: #1E2A38; }

    [data-testid="stSidebar"] { background-color: #F5EFE4; border-left: 1px solid #E8DFD0; }
    [data-testid="stSidebar"] * { color: #1E2A38; }

    .stTextInput input {
        direction: rtl; text-align: right;
        background-color: #FFFFFF; color: #1E2A38;
        border: 1px solid #E0D6C3; border-radius: 8px;
    }

    .stButton > button, .stDownloadButton > button {
        background-color: #C5A880 !important; color: #1E2A38 !important;
        font-weight: 700 !important; border: none !important;
        border-radius: 8px !important; padding: 0.55rem 2.2rem !important;
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        background-color: #B08D5F !important; color: #FFFFFF !important;
    }

    [data-testid="stMetric"] {
        background: #FFFFFF; border: 1px solid #E8DFD0; border-radius: 10px;
        padding: 14px 18px;
    }
    [data-testid="stMetricLabel"] p { color: #8C7A5B !important; }

    .gold-divider { height: 2px; background: linear-gradient(90deg, transparent, #C5A880, transparent); margin: 1.3rem 0; border: none; }

    .footer-disclaimer {
        margin-top: 48px; padding: 18px 10px 6px 10px;
        border-top: 1px solid #E8DFD0; color: #7A7265;
        font-size: 0.84rem; text-align: center; line-height: 1.9;
    }
</style>
"""
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

COLUMN_LABELS = {
    "id": "رقم الطلب",
    "created_at": "تاريخ الطلب",
    "name": "الاسم",
    "email": "البريد الإلكتروني",
    "phone": "رقم الجوال",
    "service_type": "نوع الخدمة",
    "details": "تفاصيل الطلب",
    "pdpl_consent": "موافقة PDPL",
}


def is_authenticated() -> bool:
    """بوابة دخول بكلمة مرور لمستخدم واحد عبر حالة الجلسة."""
    if st.session_state.get("dashboard_auth"):
        return True

    st.markdown("## 🔐 لوحة التحكم — منطقة محمية")
    st.caption("هذه الصفحة مخصصة لمالك التطبيق فقط.")
    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)

    with st.form("auth_form"):
        password = st.text_input("كلمة المرور", type="password", placeholder="••••••••")
        login = st.form_submit_button("دخول")

    if login:
        if password == ADMIN_PASSWORD:
            st.session_state["dashboard_auth"] = True
            st.rerun()
        else:
            st.error("كلمة المرور غير صحيحة. حاول مرة أخرى.")
    return False


if is_authenticated():
    st.markdown("## 📋 لوحة متابعة طلبات الاستشارات")
    st.caption(f"مصدر التخزين الحالي: {get_backend_name()}")
    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)

    try:
        df = get_all_requests()
    except RuntimeError as exc:
        st.error(str(exc))
        st.stop()

    if df.empty:
        st.info("لا توجد طلبات مسجلة حتى الآن. ستظهر الطلبات هنا فور وصولها من نموذج الصفحة الرئيسية.")
    else:
        # مؤشرات سريعة
        today_str = datetime.now().strftime("%Y-%m-%d")
        total_requests = len(df)
        today_requests = int(df["created_at"].astype(str).str.startswith(today_str).sum())
        latest_at = str(df["created_at"].iloc[0])

        m1, m2, m3 = st.columns(3)
        m1.metric("إجمالي الطلبات", f"{total_requests}")
        m2.metric("طلبات اليوم", f"{today_requests}")
        m3.metric("آخر طلب", latest_at)

        st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)

        # تجهيز جدول العرض بأسماء أعمدة عربية
        df_display = df.rename(columns=COLUMN_LABELS).copy()
        df_display["موافقة PDPL"] = df_display["موافقة PDPL"].map({1: "نعم ✅", 0: "لا ❌"})

        st.dataframe(df_display, use_container_width=True, hide_index=True)

        st.markdown("### ⬇️ تصدير البيانات")
        export_date = datetime.now().strftime("%Y-%m-%d")
        col_csv, col_xlsx = st.columns(2)

        # CSV بترميز utf-8-sig ليُفتح في Excel بالعربية دون تشويه الأحرف
        csv_bytes = df_display.to_csv(index=False).encode("utf-8-sig")
        col_csv.download_button(
            label="تصدير البيانات كملف Excel / CSV",
            data=csv_bytes,
            file_name=f"consultation_leads_{export_date}.csv",
            mime="text/csv",
            use_container_width=True,
        )

        # تصدير XLSX أصلي إن توفرت مكتبة openpyxl
        try:
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                df_display.to_excel(writer, index=False, sheet_name="طلبات الاستشارات")
            col_xlsx.download_button(
                label="تصدير كملف Excel أصلي (XLSX)",
                data=buffer.getvalue(),
                file_name=f"consultation_leads_{export_date}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
        except ImportError:
            col_xlsx.caption("لتفعيل تصدير XLSX الأصلي ثبّت مكتبة openpyxl: pip install openpyxl")

    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
    c1, c2 = st.columns([1, 5])
    if c1.button("🔄 تحديث البيانات"):
        st.rerun()
    if c2.button("🚪 تسجيل الخروج"):
        st.session_state["dashboard_auth"] = False
        st.rerun()

with st.sidebar:
    st.markdown("#### أحمد المعمري")
    st.caption("استشارات وخدمات هندسية مستقلة — الرياض")

year = datetime.now().year
st.markdown(
    f"""
    <div class="footer-disclaimer">
        المحتوى المنشور يقدم خدمات استشارية مهنية مستقلة ولا يمثل أي جهة عمل.
        أي استشارة تفصيلية تعتمد على المستندات والمعلومات المقدمة من العميل.<br/>
        © {year} أحمد المعمري للاستشارات والخدمات الهندسية — جميع الحقوق محفوظة.
    </div>
    """,
    unsafe_allow_html=True,
)
