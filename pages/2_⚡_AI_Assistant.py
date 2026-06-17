# -*- coding: utf-8 -*-
"""
المساعد الذكي (Prompt Generator) — يعمل محلياً 100%.
يولّد قوالب أوامر احترافية جاهزة للنسخ واستخدامها مع Claude أو ChatGPT.
"""

import sys
from datetime import datetime
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.prompts_bank import PROMPTS_BANK

st.set_page_config(
    page_title="المساعد الذكي | أحمد المعمري",
    page_icon="⚡",
    layout="centered",
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

    .stSelectbox div[data-baseweb="select"] > div { background-color: #FFFFFF; border-radius: 8px; }

    .stButton > button, .stDownloadButton > button {
        background-color: #C5A880 !important; color: #1E2A38 !important;
        font-weight: 700 !important; border: none !important;
        border-radius: 8px !important; padding: 0.55rem 2.2rem !important;
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        background-color: #B08D5F !important; color: #FFFFFF !important;
    }

    /* عرض الأوامر العربية داخل صندوق الكود باتجاه RTL مع التفاف الأسطر */
    [data-testid="stCode"] pre, [data-testid="stCodeBlock"] pre, .stCode pre {
        direction: rtl; text-align: right; white-space: pre-wrap;
        background-color: #F5EFE4 !important; border: 1px solid #E0D6C3; border-radius: 8px;
    }

    .gold-divider { height: 2px; background: linear-gradient(90deg, transparent, #C5A880, transparent); margin: 1.3rem 0; border: none; }

    .use-case-box {
        background: #FFFFFF; border: 1px solid #E8DFD0; border-right: 4px solid #C5A880;
        border-radius: 10px; padding: 16px 22px; margin: 12px 0 18px 0; line-height: 1.9;
    }

    .footer-disclaimer {
        margin-top: 48px; padding: 18px 10px 6px 10px;
        border-top: 1px solid #E8DFD0; color: #7A7265;
        font-size: 0.84rem; text-align: center; line-height: 1.9;
    }
</style>
"""
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

st.markdown("## ⚡ المساعد الذكي — مولّد الأوامر الاحترافية")
st.caption(
    "قوالب أوامر (Prompts) هندسية مُحكمة الصياغة، جاهزة للنسخ واللصق في Claude أو ChatGPT "
    "مع مستنداتك — دون أي اتصال خارجي من هذا التطبيق."
)
st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)

# اختيار الخدمة
service_names = list(PROMPTS_BANK.keys())
selected = st.selectbox("اختر الخدمة الهندسية المطلوبة:", service_names, index=0)

entry = PROMPTS_BANK[selected]

st.markdown(
    f"""
    <div class="use-case-box">
        <b>{entry['icon']} متى تستخدم هذا القالب؟</b><br/>{entry['use_case']}
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("#### نص الأمر الجاهز")
st.caption("اضغط أيقونة النسخ 📋 أعلى يسار الصندوق لنسخ النص كاملاً بضغطة واحدة.")

# st.code يوفر زر نسخ مدمجاً (مكوّن أصلي) يعمل دون إنترنت
st.code(entry["prompt"], language=None)

st.download_button(
    label="⬇️ تنزيل الأمر كملف نصي (TXT)",
    data=entry["prompt"].encode("utf-8"),
    file_name=f"prompt_{service_names.index(selected) + 1}.txt",
    mime="text/plain",
    use_container_width=True,
)

with st.expander("📌 طريقة الاستخدام الصحيحة"):
    st.markdown(
        """
1. انسخ نص الأمر كاملاً بزر النسخ أعلى الصندوق.
2. الصقه في محادثة جديدة مع Claude أو ChatGPT.
3. استبدل الحقول بين الأقواس 【...】 بمعلومات مشروعك الفعلية.
4. أرفق مستنداتك (جدول الكميات، الكراسة، مسودة العقد...) في نفس المحادثة.
5. راجع المخرجات بعين المهندس — الذكاء الاصطناعي أداة مساندة ولا يغني عن الحكم الفني المتخصص.
        """
    )

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
