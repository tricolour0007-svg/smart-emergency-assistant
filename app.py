import streamlit as st
import folium
from streamlit_folium import st_folium
from gtts import gTTS
from io import BytesIO
import base64

# ---------------------------
# PAGE CONFIG
# ---------------------------
st.set_page_config(page_title="Smart Emergency Assistant", page_icon="🚨", layout="wide")

# ---------------------------
# STYLE
# ---------------------------
st.markdown("""
    <style>
        [data-testid="stAppViewContainer"] {
            background: linear-gradient(120deg,#ff4b4b,#ff9900,#ffc300);
            background-attachment: fixed;
        }
        .main {
            background: rgba(255,255,255,0.85);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 0 25px rgba(0,0,0,0.1);
        }
        .stButton>button {
            width: 100%;
            background: linear-gradient(90deg,#ff4b4b,#ff9900);
            border: none;
            color: white;
            border-radius: 12px;
            height: 3em;
            font-size: 18px !important;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            transform: scale(1.05);
            background: linear-gradient(90deg,#ff9900,#ff4b4b);
        }
        .card {
            background: #fffaf0;
            padding: 15px;
            border-radius: 15px;
            box-shadow: 0 3px 8px rgba(0,0,0,0.1);
            margin-bottom: 10px;
        }
        h1 {text-align:center; color:white;}
        h3 {color:#ff4b4b;}
        audio {width:100%;}
    </style>
""", unsafe_allow_html=True)

# ---------------------------
# HEADER
# ---------------------------
st.markdown("<h1>🚨 Smart Emergency Assistant</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:white;'>AI-powered help, live maps & voice alerts</p>", unsafe_allow_html=True)

# ---------------------------
# INPUTS
# ---------------------------
st.markdown("### 🧭 Enter Your Details")
col1, col2 = st.columns(2)
city = col1.text_input("🏙️ City", placeholder="e.g. Delhi, Mumbai, Bengaluru")
emergency = col2.selectbox("⚠️ Select Emergency Type",
                           ["Select...", "Fire", "Medical", "Police", "Flood", "Earthquake", "Accident"])

# ---------------------------
# VOICE
# ---------------------------
def speak_once(text):
    if "spoken" not in st.session_state:
        st.session_state["spoken"] = True
        try:
            tts = gTTS(text)
            fp = BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            b64 = base64.b64encode(fp.read()).decode()
            st.markdown(f"<audio autoplay='true' src='data:audio/mp3;base64,{b64}'></audio>", unsafe_allow_html=True)
        except:
            st.warning("🔇 Voice playback not available.")

# ---------------------------
# MAIN ACTION
# ---------------------------
if city and emergency != "Select...":
    st.success(f"✅ Assistance ready for {emergency} emergency in {city}")
    speak_once(f"Detected your location in {city}. Providing help for {emergency} emergency.")

    # Map
    m = folium.Map(location=[20.5937, 78.9629], zoom_start=5)
    folium.Marker([28.6139,77.2090], popup="Nearest Hospital 🏥", icon=folium.Icon(color="red")).add_to(m)
    st_folium(m, width=700, height=450)

    st.markdown("### 🚨 Emergency Info")

    info = {
        "Fire": ("🔥 Fire Department", "101", "Evacuate immediately and avoid elevators."),
        "Medical": ("🏥 Ambulance", "102 / 108", "Apply first aid and call medical help."),
        "Police": ("👮 Police", "100", "Stay safe and report immediately."),
        "Flood": ("🌊 Disaster Helpline", "1078", "Move to higher ground and avoid water."),
        "Earthquake": ("🌍 Helpline", "112", "Drop, cover, and hold until shaking stops."),
        "Accident": ("🚓 Traffic Helpline", "103", "Call ambulance and document details safely.")
    }

    if emergency in info:
        title, contact, tip = info[emergency]
        st.markdown(f"<div class='card'><h3>{title}</h3><b>Helpline:</b> {contact}<br><b>Tips:</b> {tip}</div>", unsafe_allow_html=True)

    st.markdown("### 🚖 Quick Transport Links")
    colA, colB = st.columns(2)
    colA.link_button("🚕 Book Ola", "https://www.olacabs.com/")
    colB.link_button("🚗 Book Uber", "https://www.uber.com/in/en/")

st.markdown("<hr><p style='text-align:center;color:gray;'>Developed with ❤️ using Streamlit • Stay Safe</p>", unsafe_allow_html=True)
