import datetime
from datetime import date
import json
import os
import re
import urllib.parse
import urllib.request
import streamlit as st

# ضبط إعدادات الصفحة ورأس الموقع
st.set_page_config(
    page_title="takotaki 🌸", page_icon="🧸", layout="centered"
)


# دالة إرسال التنبيه الفوري إلى بوت التليجرام
def send_telegram_notification(name, gender, dob):
    try:
        token = st.secrets.get("TELEGRAM_BOT_TOKEN")
        chat_id = st.secrets.get("TELEGRAM_CHAT_ID")
        if token and chat_id:
            text = f"🚨 **زائر جديد في الموقع!**\n\n👤 **الاسم:** {name}\n🚻 **الجنس:** {gender}\n📅 **تاريخ الميلاد:** {dob}"
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            data = urllib.parse.urlencode(
                {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
            ).encode("utf-8")
            req = urllib.request.Request(url, data=data)
            urllib.request.urlopen(req)
    except Exception:
        pass


# تهيئة متغيرات الجلسة (Session State)
if "step" not in st.session_state:
    st.session_state.step = 1
if "visitor_name" not in st.session_state:
    st.session_state.visitor_name = ""
if "visitor_gender" not in st.session_state:
    st.session_state.visitor_gender = "Girl 👧"
if "visitor_dob" not in st.session_state:
    st.session_state.visitor_dob = "2000/01/01"
if "attempts" not in st.session_state:
    st.session_state.attempts = 0

# تصميم الواجهة والتنسيقات البصرية
st.markdown(
    """
<style>
    .stApp {
        background: linear-gradient(135deg, #1a080c 0%, #3d0c1e 50%, #1a080c 100%);
        color: #ffffff;
    }
    .main-title {
        text-align: center;
        color: #ff4d6d;
        font-size: 32px;
        font-weight: bold;
        margin-bottom: 25px;
        text-shadow: 0 0 10px rgba(255, 77, 109, 0.5);
    }
    .custom-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 77, 109, 0.3);
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }
    .sad-box-3d {
        background: rgba(40, 10, 20, 0.85);
        backdrop-filter: blur(10px);
        color: #ff4d6d;
        padding: 30px;
        border-radius: 20px;
        text-align: center;
        border: 2px solid #ff0055;
        box-shadow: 0 0 40px rgba(255, 0, 85, 0.7);
        font-size: 22px;
        font-weight: bold;
        margin-top: 20px;
    }
</style>
""",
    unsafe_allow_html=True,
)

# الصفحة الأولى: نموذج إدخال البيانات
if st.session_state.step == 1:
    st.markdown(
        "<h1 class='main-title'>✨ Welcome to takotaki! ✨</h1>",
        unsafe_allow_html=True,
    )

    with st.container():
        st.markdown("<div class='custom-card'>", unsafe_allow_html=True)

        name_input = st.text_input(
            "Enter Your Name:", placeholder="Type your name here..."
        )

        gender_input = st.radio(
            "Select Your Gender:",
            ["Boy 👦", "Girl 👧"],
            horizontal=True,
            index=1,
        )

        dob_input = st.date_input(
            "Select Your Date of Birth:",
            value=datetime.date(2000, 1, 27),
            min_value=datetime.date(1950, 1, 1),
            max_value=datetime.date.today(),
        )

        submit_btn = st.button("Continue ➔")

        st.markdown("</div>", unsafe_allow_html=True)

        if submit_btn:
            clean_name = name_input.strip()

            # شرط قبول الأحرف اللاتينية (الإنجليزية/الفرنسية) والمسافات الشرطية
            if len(clean_name) >= 2 and re.match(
                r"^[a-zA-Z\s\'-]+$", clean_name
            ):
                st.session_state.visitor_name = clean_name
                st.session_state.visitor_gender = gender_input
                st.session_state.visitor_dob = str(dob_input)

                # إرسال التنبيه إلى تليجرام
                send_telegram_notification(
                    clean_name, gender_input, str(dob_input)
                )

                st.session_state.step = 2
                st.rerun()
            else:
                st.error(
                    "⚠️ Please enter a valid name using Latin characters (e.g., asmaa, soukaina)!"
                )

# الصفحة الثانية: الانتقال التفاعلي وتشغيل الصوت
elif st.session_state.step == 2:
    st.markdown(
        f"<h2 style='text-align: center; color: #ff4d6d;'>Welcome, {st.session_state.visitor_name}! 🎉</h2>",
        unsafe_allow_html=True,
    )

    current_warning = (
        f"Hello {st.session_state.visitor_name}, welcome to takotaki!"
    )

    st.markdown(
        f"""
    <div class="sad-box-3d">
        {current_warning}
    </div>
    """,
        unsafe_allow_html=True,
    )

    # تشغيل الخلفية الصوتية
    st.html(
        """
    <audio id="sadMusic" autoplay loop style="display:none;">
        <source src="https://cdn.pixabay.com/download/audio/2022/01/18/audio_d0a13f69d2.mp3?filename=sad-piano-10811.mp3" type="audio/mpeg">
    </audio>
    <script>
        var audio = document.getElementById("sadMusic");
        if (audio) { audio.play().catch(function(e) { console.log(e); }); }
    </script>
    """
    )

    if st.button("Back 🔄"):
        st.session_state.step = 1
        st.rerun()
