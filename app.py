import streamlit as st
import folium
from streamlit_folium import st_folium
from gtts import gTTS
from io import BytesIO
import base64

# ---------------------------------------------
# 🎨 APP CONFIG
# ---------------------------------------------
st.set_page_config(
    page_title="Smart Emergency Assistant",
    page_icon="🚨",
    layout="wide"
)

# ---------------------------------------------
# 💫 CUSTOM CSS STYLES
# ---------------------------------------------
st.markdown("""
    <style>
        body {
            background: linear-gradient(135deg, #ff4b4b, #ff9900, #ffc300);
            background-attachment: fixed;
        }
        .main {
            background: rgba(255,255,255,0.85);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 0 25px rgba(0,0,0,0.15);
        }
        h1 {
            text-align: center;
            color: white;
            text-shadow: 2px 2px 8px rgba(0,0,0,0.3);
        }
        h3 {
            color: #FF4B4B;
        }
        .stButton>button {
            width: 100%;
            border-radius: 12px;
            font-size: 18px !important;
            background: linear-gradient(90deg, #ff4b4b, #ff9900);
            color: white;
            border: none;
            height: 3em;
            transition: 0.4s;
        }
        .stButton>button:hover {
            transform: scale(1.05);
            background: linear-gradient(90deg, #ff9900, #ff4b4b);
        }
        .card {
            background: #fff8f0;
            padding: 15px;
            border-radius: 15px;
            box-shadow: 0 3px 8px rgba(0,0,0,0.1);
            margin-bottom: 15px;
        }
        audio {
            width: 100%;
        }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------
# 🚨 HEADER
# ---------------------------------------------
st.markdown("""
    <h1>🚨 Smart Emergency Assistant</h1>
    <p style='text-align:center; color:#fff; font-size:18px;'>
        AI-powered real-time emergency help, maps, and voice guidance.
    </p>
""", unsafe_allow_html=True)

# ---------------------------------------------
# 📍 USER INPUT
# ---------------------------------------------
st.markdown("### 🧭 Enter Your Details")
col1, col2 = st.columns(2)
city = col1.text_input("🏙️ Enter your city", placeholder="e.g. Delhi, Mumbai, Bengaluru")
emergency = col2.selectbox(
    "⚠️ Choose the type of emergency",
    ["Select...", "Fire", "Medical", "Police", "Flood", "Earthquake", "Road Accident"]
)

# ---------------------------------------------
# 🔊 VOICE FUNCTION
# ---------------------------------------------
def speak_once(message):
    if "spoken" not in st.session_state:
        st.session_state["spoken"] = True
        try:
            tts = gTTS(message)
            fp = BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            b64 = base64.b64encode(fp.read()).decode()
            audio_html = f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}"></audio>'
            st.markdown(audio_html, unsafe_allow_html=True)
        except Exception:
            st.warning("🔇 Voice unavailable. Please check your connection.")

# ---------------------------------------------
# 🚑 RESPONSE SECTION
# ---------------------------------------------
if city and emergency != "Select...":
    st.markdown(f"## ✅ Assistance for {emergency} emergency in {city}")
    speak_once(f"Detected your location in {city}. Providing help for {emergency} emergency.")

    # Map
    st.markdown("### 🗺️ Nearby Emergency Facilities")
    map_obj = folium.Map(location=[20.5937, 78.9629], zoom_start=5)

    folium.Marker([28.6139, 77.2090],
                  popup="Nearest Hospital 🏥",
                  tooltip="Hospital",
                  icon=folium.Icon(color='red')).add_to(map_obj)

    st_folium(map_obj, width=700, height=450)

    # Information cards
    st.markdown("### 🚨 Emergency Tips & Contacts")

    if emergency == "Fire":
        st.markdown("""
            <div class='card'>
                <h3>🔥 Fire Emergency</h3>
                <b>Helpline:</b> 101<br>
                <b>Tips:</b> Evacuate immediately, avoid elevators, and cover your mouth with a cloth.
            </div>
        """, unsafe_allow_html=True)

    elif emergency == "Medical":
        st.markdown("""
            <div class='card'>
                <h3>🏥 Medical Emergency</h3>
                <b>Helpline:</b> 108 / 102<br>
                <b>Tips:</b> Keep calm, apply first aid, and call for medical help immediately.
            </div>
        """, unsafe_allow_html=True)

    elif emergency == "Police":
        st.markdown("""
            <div class='card'>
                <h3>👮 Police Emergency</h3>
                <b>Helpline:</b> 100<br>
                <b>Tips:</b> Move to a safe area and contact authorities quickly.
            </div>
        """, unsafe_allow_html=True)

    elif emergency == "Flood":
        st.markdown("""
            <div class='card'>
                <h3>🌊 Flood Situation</h3>
                <b>Helpline:</b> 1078<br>
                <b>Tips:</b> Move to higher ground and avoid flooded roads.
            </div>
        """, unsafe_allow_html=True)

    elif emergency == "Earthquake":
        st.markdown("""
            <div class='card'>
                <h3>🌍 Earthquake Alert</h3>
                <b>Helpline:</b> 112<br>
                <b>Tips:</b> Drop, cover, and hold on. Stay away from glass and heavy structures.
            </div>
        """, unsafe_allow_html=True)

    elif emergency == "Road Accident":
        st.markdown("""
            <div class='card'>
                <h3>🚗 Road Accident</h3>
                <b>Helpline:</b> 103 / 108<br>
                <b>Tips:</b> Move to a safe zone, call ambulance, and document details safely.
            </div>
        """, unsafe_allow_html=True)

    st.markdown("### 🚖 Quick Transport Links")
    colA, colB = st.columns(2)
    colA.link_button("🚕 Book Ola", "https://www.olacabs.com/")
    colB.link_button("🚗 Book Uber", "https://www.uber.com/in/en/")

# ---------------------------------------------
# ⚙️ FOOTER
# ---------------------------------------------
st.markdown("""
<hr>
<p style='text-align:center; color:gray;'>
Developed with ❤️ using Streamlit • Stay Safe Always 🌍
</p>
""", unsafe_allow_html=True)
