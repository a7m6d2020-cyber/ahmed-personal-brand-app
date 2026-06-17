# -*- coding: utf-8 -*-
"""صفحة دراسات الحالة (Portfolio) — نماذج أعمال معمّمة بدون أي بيانات سرية."""

import sys
from datetime import datetime
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

st.set_page_config(
    page_title="دراسات الحالة | أحمد المعمري",
    page_icon="📂",
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
    .stMarkdown p, .stMarkdown li, label { color: #1E2A38; }

    [data-testid="stSidebar"] { background-color: #F5EFE4; border-left: 1px solid #E8DFD0; }
    [data-testid="stSidebar"] * { color: #1E2A38; }

    .gold-divider { height: 2px; background: linear-gradient(90deg, transparent, #C5A880, transparent); margin: 1.3rem 0; border: none; }

    .case-card {
        background: #FFFFFF; border: 1px solid #E8DFD0;
        border-right: 4px solid #C5A880; border-radius: 10px;
        padding: 26px 30px; margin-bottom: 22px;
        box-shadow: 0 1px 4px rgba(30, 42, 56, 0.05);
    }
    .case-card h3 { margin-top: 0; color: #1E2A38; }
    .card-label { color: #A8854F; font-weight: 700; margin: 10px 0 2px 0; font-size: 0.95rem; }
    .case-card p { line-height: 1.95; margin: 2px 0 6px 0; color: #1E2A38; }

    .footer-disclaimer {
        margin-top: 48px; padding: 18px 10px 6px 10px;
        border-top: 1px solid #E8DFD0; color: #7A7265;
        font-size: 0.84rem; text-align: center; line-height: 1.9;
    }
</style>
"""
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

st.markdown("## 📂 دراسات حالة مختارة")
st.caption(
    "نماذج أعمال معروضة بصورة عامة ومعمّمة، دون أي أسماء عملاء أو مشاريع أو بيانات سرية — "
    "التزاماً بالسرية المهنية."
)
st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)

CASE_STUDIES = [
    {
        "icon": "📊",
        "title": "مراجعة جدول كميات لمشروع بنية تحتية",
        "challenge": (
            "جدول كميات (BOQ - Bill of Quantities) لمشروع بنية تحتية متعدد الشبكات، "
            "ظهرت فيه مؤشرات فروقات بين الكميات المطروحة والمخططات، مع ضيق المدة المتاحة قبل إقفال التسعير."
        ),
        "methodology": (
            "مطابقة بنود الجدول مع المخططات والمواصفات الفنية بنداً بنداً، وترتيب البنود الحرجة "
            "وفق أثرها المالي (مبدأ باريتو 80/20)، ثم حصر الفروقات والبنود الناقصة والمكررة، "
            "وإعداد قائمة استفسارات فنية (TQs - Technical Queries) رسمية قبل الموعد النظامي."
        ),
        "result": (
            "رُصدت فروقات كمية في بنود حرجة ذات أثر مالي مباشر، وقُدمت الاستفسارات في وقتها النظامي، "
            "ما مكّن الإدارة من تسعير مبني على أساس فني موثق وخفّض هامش المخاطرة في العطاء."
        ),
    },
    {
        "icon": "📑",
        "title": "تحليل نطاق عمل لمنافسة حكومية",
        "challenge": (
            "كراسة شروط ومواصفات لمنافسة حكومية بنطاق عمل متشعب وواجهات (Interfaces) غير واضحة "
            "بين المقاول وجهات خدمية متعددة، مع التباس في حدود المسؤوليات."
        ),
        "methodology": (
            "تفكيك نطاق العمل إلى حزم أعمال محددة الحدود، وبناء مصفوفة واجهات توضح نقاط التقاطع "
            "بين الأطراف، وتمييز المتطلبات الإلزامية عن التفضيلية، ورصد مواطن الغموض والتعارض "
            "داخل مستندات المنافسة مع مرجعية دقيقة لكل ملاحظة."
        ),
        "result": (
            "وضوح كامل لحدود المسؤوليات قبل التسعير، وقائمة استفسارات رسمية عالجت أبرز مواطن الالتباس، "
            "ما قلّص الافتراضات التسعيرية ورفع جودة قرار المشاركة في المنافسة."
        ),
    },
    {
        "icon": "🏗️",
        "title": "إعداد منهجية تنفيذ لأعمال مدنية",
        "challenge": (
            "متطلب تعاقدي بتقديم منهجية تنفيذ (Method Statement) متكاملة لأعمال مدنية ضمن العرض الفني، "
            "خلال مدة تقديم قصيرة وباشتراطات توثيق دقيقة من صاحب العمل."
        ),
        "methodology": (
            "صياغة المنهجية بهيكل عشري مرقم يغطي التسلسل المنطقي للتنفيذ خطوة بخطوة، "
            "مع جداول الموارد والمعدات والطواقم، ومتطلبات ضبط الجودة بنقاط الإيقاف والحضور "
            "(Hold & Witness Points)، واشتراطات السلامة والصحة المهنية الخاصة بكل نشاط."
        ),
        "result": (
            "منهجية جاهزة للتقديم الحكومي اعتُمدت ضمن العرض الفني من المراجعة الأولى دون ملاحظات جوهرية، "
            "وأصبحت قالباً معتمداً يعاد استخدامه في عطاءات لاحقة."
        ),
    },
    {
        "icon": "⚖️",
        "title": "تحليل مخاطر تعاقدية وفق منظور FIDIC",
        "challenge": (
            "مسودة عقد بشروط خاصة (Particular Conditions) معدلة جوهرياً عن النموذج الأساس، "
            "تضمنت بنوداً تنقل مخاطر غير متوازنة إلى المقاول قبيل مرحلة التوقيع."
        ),
        "methodology": (
            "مقارنة الشروط الخاصة مع الشروط العامة المرجعية وفق منظور عقود الفيديك (FIDIC) بنداً بنداً، "
            "مع التركيز على مدد الإشعارات وسقوط الحق (Time Bars)، وأوامر التغيير (VO)، وسقف المسؤولية، "
            "ثم بناء سجل مخاطر مصنف بالاحتمالية والأثر مع صياغة تحفظات تفاوضية لكل بند حرج."
        ),
        "result": (
            "سجل مخاطر تعاقدية واضح الأولويات سلّم للإدارة قبل التوقيع، مكّن من التفاوض على تعديل "
            "البنود الأعلى خطورة وتوثيق التحفظات، وخفض التعرض التعاقدي للمشروع بصورة ملموسة."
        ),
    },
]

for case in CASE_STUDIES:
    st.markdown(
        f"""
        <div class="case-card">
            <h3>{case['icon']} {case['title']}</h3>
            <div class="card-label">المشكلة (The Challenge)</div>
            <p>{case['challenge']}</p>
            <div class="card-label">المنهجية (Methodology)</div>
            <p>{case['methodology']}</p>
            <div class="card-label">النتيجة (Result)</div>
            <p>{case['result']}</p>
        </div>
        """,
        unsafe_allow_html=True,
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
