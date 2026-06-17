# -*- coding: utf-8 -*-
"""
الصفحة الرئيسية — أحمد المعمري للاستشارات والخدمات الهندسية
تطبيق محلي 100% بدون أي اعتماد على واجهات برمجية خارجية.
"""

import re
from datetime import datetime
from urllib.parse import quote

import streamlit as st

from utils.database import initialize_db, save_request

# ==================================================================
# الإعدادات العامة
# ==================================================================
# رقم واتساب الأعمال بالصيغة الدولية بدون + (مثال: 9665XXXXXXXX).
# عند النشر: يُقرأ من Secrets أولاً؛ القيمة أدناه هي الافتراضية للتشغيل المحلي.
DEFAULT_WHATSAPP_NUMBER = "966533665005"


def _get_whatsapp_number() -> str:
    """رقم واتساب من st.secrets عند توفره، وإلا القيمة الافتراضية."""
    try:
        if "contact" in st.secrets and st.secrets["contact"].get("whatsapp_number"):
            return str(st.secrets["contact"]["whatsapp_number"]).strip()
    except Exception:
        pass
    return DEFAULT_WHATSAPP_NUMBER


WHATSAPP_NUMBER = _get_whatsapp_number()

SERVICES = [
    "— اختر نوع الخدمة —",
    "العطاءات وإعداد العروض الفنية (Tendering & Technical Proposals)",
    "الاستشارات الهندسية المدنية (Civil Engineering Consultation)",
    "التنسيق المعماري والإنشائي (Architectural / Construction Coordination)",
    "مراجعة جداول الكميات ونطاق العمل (BOQ & Scope Review)",
    "منهجيات التنفيذ والتوثيق الفني (Method Statements & Documentation)",
    "مراجعة المخاطر التعاقدية وفق منظور فيديك (FIDIC Risk Review)",
    "دعم المقاولات الخاص والحكومي (Private / Public Contracting Support)",
    "أخرى",
]

PHONE_RE = re.compile(r"^[+]?[0-9\s\-]{8,15}$")
EMAIL_RE = re.compile(r"^[\w.+-]+@[\w-]+\.[\w.-]+$")

# ==================================================================
# تهيئة الصفحة والهوية البصرية
# ==================================================================
st.set_page_config(
    page_title="أحمد المعمري | استشارات هندسية",
    page_icon="🏗️",
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

    .stTextInput input, .stTextArea textarea {
        direction: rtl; text-align: right;
        background-color: #FFFFFF; color: #1E2A38;
        border: 1px solid #E0D6C3; border-radius: 8px;
    }
    .stSelectbox div[data-baseweb="select"] > div { background-color: #FFFFFF; border-radius: 8px; }

    .stButton > button, .stFormSubmitButton > button,
    .stDownloadButton > button, .stLinkButton > a {
        background-color: #C5A880 !important; color: #1E2A38 !important;
        font-weight: 700 !important; border: none !important;
        border-radius: 8px !important; padding: 0.55rem 2.2rem !important;
    }
    .stButton > button:hover, .stFormSubmitButton > button:hover,
    .stDownloadButton > button:hover, .stLinkButton > a:hover {
        background-color: #B08D5F !important; color: #FFFFFF !important;
    }

    .brand-title { font-size: 2.05rem; font-weight: 800; color: #1E2A38; text-align: center; margin-bottom: 0.15rem; }
    .brand-sub { font-size: 1.0rem; color: #8C7A5B; text-align: center; letter-spacing: 1px; }
    .gold-divider { height: 2px; background: linear-gradient(90deg, transparent, #C5A880, transparent); margin: 1.3rem 0; border: none; }

    .badges-wrap { text-align: center; margin: 0.7rem 0 1.1rem 0; }
    .badge {
        display: inline-block; background: #FFFFFF; color: #1E2A38;
        border: 1px solid #C5A880; border-radius: 30px;
        padding: 6px 18px; margin: 4px 6px; font-size: 0.87rem; font-weight: 600;
    }

    .service-chip {
        display: inline-block; background: #F5EFE4; color: #1E2A38;
        border: 1px solid #E0D6C3; border-radius: 8px;
        padding: 9px 15px; margin: 4px; font-size: 0.9rem; font-weight: 600;
    }
    .chips-wrap { text-align: center; margin-bottom: 0.6rem; }

    .footer-disclaimer {
        margin-top: 48px; padding: 18px 10px 6px 10px;
        border-top: 1px solid #E8DFD0; color: #7A7265;
        font-size: 0.84rem; text-align: center; line-height: 1.9;
    }
</style>
"""
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# تهيئة قاعدة البيانات المحلية عند الإقلاع
initialize_db()


def render_footer() -> None:
    """التذييل الموحد مع إخلاء المسؤولية."""
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


# ==================================================================
# الترويسة والهوية
# ==================================================================
st.markdown('<div class="brand-title">أحمد المعمري للاستشارات والخدمات الهندسية</div>', unsafe_allow_html=True)
st.markdown('<div class="brand-sub">Ahmed Al-Maamari Engineering Advisory</div>', unsafe_allow_html=True)
st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)

# الاعتمادات المهنية — بدون أي ذكر لجهة عمل
st.markdown(
    """
    <div class="badges-wrap">
        <span class="badge">PMP®</span>
        <span class="badge">PMI-RMP®</span>
        <span class="badge">عضو الهيئة السعودية للمهندسين (SCE)</span>
        <span class="badge">مهندس فني أول — العطاءات والعروض الفنية<br/>Senior Technical Engineer – Tendering & Technical Proposals</span>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <p style="text-align:center; font-size:1.05rem; line-height:2; max-width:640px; margin:0 auto;">
    استشارات هندسية مستقلة لقطاع المقاولات والتطوير العقاري في المملكة العربية السعودية —
    من تحليل كراسة الشروط وتدقيق جداول الكميات، إلى إعداد العروض الفنية ومنهجيات التنفيذ
    ومراجعة المخاطر التعاقدية قبل التوقيع. <b>قرارك التعاقدي يستحق رأياً فنياً محايداً.</b>
    </p>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)

# نطاقات الخدمة
st.markdown("### نطاقات الخدمة")
st.markdown(
    """
    <div class="chips-wrap">
        <span class="service-chip">📑 العطاءات والعروض الفنية</span>
        <span class="service-chip">🧮 مراجعة جداول الكميات BOQ</span>
        <span class="service-chip">🏗️ منهجيات التنفيذ</span>
        <span class="service-chip">⚖️ المخاطر التعاقدية FIDIC</span>
        <span class="service-chip">📐 الاستشارات المدنية</span>
        <span class="service-chip">🤝 دعم المقاولات الخاص والحكومي</span>
        <span class="service-chip">🗂️ التنسيق المعماري والإنشائي</span>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)

# ==================================================================
# نموذج طلب استشارة (Lead Generation Form)
# ==================================================================
st.markdown("### 📥 اطلب استشارتك الآن")
st.caption("املأ النموذج وسيتم التواصل معك خلال 24 ساعة عمل.")

with st.form("lead_form", clear_on_submit=False):
    col1, col2 = st.columns(2)
    name = col1.text_input("الاسم الكامل *", placeholder="مثال: م. محمد العتيبي")
    phone = col2.text_input("رقم الجوال *", placeholder="05XXXXXXXX")
    email = col1.text_input("البريد الإلكتروني", placeholder="name@example.com")
    service_type = col2.selectbox("نوع الخدمة المطلوبة *", SERVICES, index=0)
    details = st.text_area(
        "وصف موجز للمشروع أو الطلب",
        placeholder="مثال: لدينا منافسة حكومية لمشروع بنية تحتية ونحتاج مراجعة جدول الكميات قبل التسعير...",
        height=140,
    )
    pdpl_consent = st.checkbox(
        "أوافق على سياسة الخصوصية ومعالجة بياناتي لغرض التواصل بشأن طلبي، "
        "وفقاً لنظام حماية البيانات الشخصية (PDPL) في المملكة العربية السعودية. *"
    )
    submitted = st.form_submit_button("إرسال الطلب", use_container_width=True)

if submitted:
    errors = []
    if not name.strip():
        errors.append("• الاسم الكامل مطلوب.")
    if not phone.strip() or not PHONE_RE.match(phone.strip()):
        errors.append("• رقم جوال صحيح مطلوب (8–15 رقماً).")
    if email.strip() and not EMAIL_RE.match(email.strip()):
        errors.append("• صيغة البريد الإلكتروني غير صحيحة.")
    if service_type == SERVICES[0]:
        errors.append("• يرجى اختيار نوع الخدمة.")
    if not pdpl_consent:
        errors.append("• الموافقة على سياسة الخصوصية (PDPL) إلزامية لإرسال الطلب.")

    if errors:
        st.error("يرجى تصحيح ما يلي:\n\n" + "\n".join(errors))
    else:
        try:
            request_id = save_request(name, email, phone, service_type, details, pdpl_consent)
            st.session_state["last_request"] = {
                "id": request_id,
                "name": name.strip(),
                "service": service_type,
            }
        except Exception:
            # لا نكشف تفاصيل تقنية للعميل؛ نوجهه لقناة بديلة مضمونة
            st.error(
                "تعذّر حفظ الطلب حالياً لخلل تقني مؤقت. "
                "يرجى التواصل المباشر عبر واتساب وسنخدمك فوراً."
            )
            st.link_button(
                "📲 التواصل عبر واتساب",
                f"https://wa.me/{WHATSAPP_NUMBER}",
                use_container_width=True,
            )

# زر واتساب الديناميكي — يظهر بعد نجاح الحفظ (خارج النموذج)
if "last_request" in st.session_state:
    req = st.session_state["last_request"]
    st.success(
        f"✅ تم استلام طلبك بنجاح — رقم الطلب المرجعي: **{req['id']}**. "
        "لتسريع التواصل، تابع مباشرة عبر واتساب:"
    )
    wa_message = (
        f"السلام عليكم م. أحمد،\n"
        f"أنا {req['name']}، أرسلت طلب استشارة عبر الموقع.\n"
        f"نوع الخدمة: {req['service']}\n"
        f"رقم الطلب المرجعي: {req['id']}"
    )
    wa_url = f"https://wa.me/{WHATSAPP_NUMBER}?text={quote(wa_message)}"
    st.link_button("📲 متابعة الطلب عبر واتساب", wa_url, use_container_width=True)

# ==================================================================
# الشريط الجانبي
# ==================================================================
with st.sidebar:
    st.markdown("#### أحمد المعمري")
    st.caption("استشارات وخدمات هندسية مستقلة — الرياض")
    st.markdown("---")
    st.caption("تنقّل بين الصفحات من القائمة أعلاه: دراسات الحالة، المساعد الذكي، ولوحة التحكم.")

render_footer()
