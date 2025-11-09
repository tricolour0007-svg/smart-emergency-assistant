# app.py
import streamlit as st
import folium
from streamlit_folium import st_folium
from gtts import gTTS
from io import BytesIO
import random

# -------------------------
# Page config
# -------------------------
st.set_page_config(page_title="Smart Emergency Assistant 🚨",
                   page_icon="🚨", layout="wide")

# -------------------------
# CSS for visuals
# -------------------------
st.markdown("""
<style>
body {background: linear-gradient(135deg,#ff6b6b,#ffd166);}
.header {padding:20px; border-radius:15px; color:white; text-align:center;
         background: linear-gradient(135deg,#ff416c,#ffcc66); box-shadow:0 6px 20px rgba(0,0,0,0.12);}
.card {background: rgba(255,255,255,0.95); padding:15px; border-radius:12px;
       box-shadow:0 6px 20px rgba(0,0,0,0.1); margin-bottom:12px;}
.big-button {width:100%; padding:12px; border-radius:12px; font-weight:700; font-size:16px;
             border:none; color:white; background: linear-gradient(90deg,#ff6b6b,#ff8a4b);}
.small-muted {color:#555; font-size:13px;}
</style>
""", unsafe_allow_html=True)

# -------------------------
# Cities & coordinates
# -------------------------
CITY_COORDS = {
    "Delhi": [28.6139, 77.2090],
    "Mumbai": [19.0760, 72.8777],
    "Bangalore": [12.9716, 77.5946],
    "Chennai": [13.0827, 80.2707],
    "Kolkata": [22.5726, 88.3639],
    "Hyderabad": [17.3850, 78.4867],
    "Pune": [18.5204, 73.8567],
    "Ahmedabad": [23.0225, 72.5714]
}

# -------------------------
# Emergency info
# -------------------------
EMERGENCY_DB = {
    "Fire": {"helpline":"101", "do":["Move outside quickly","Stay low under smoke","Cover mouth with wet cloth"],
             "dont":["Use elevators","Open burning windows"], "places":["Fire Station","Hospital"]},
    "Medical": {"helpline":"108", "do":["Call ambulance","Check breathing","Control severe bleeding"],
                "dont":["Give oral medicines to unconscious people","Move seriously injured"], "places":["Hospital","Clinic"]},
    "Accident": {"helpline":"108", "do":["Ensure scene safety","Call emergency services","Stop severe bleeding"],
                 "dont":["Crowd the injured","Move victims unless danger"], "places":["Hospital","Police Station"]},
    "Flood": {"helpline":"1070", "do":["Move to higher ground","Switch off electricity","Follow evacuation orders"],
              "dont":["Walk/drive through flood water","Ignore warnings"], "places":["Shelter","Hospital"]},
    "Earthquake": {"helpline":"112", "do":["Drop, Cover and Hold On","Stay away from glass","Move to open space"],
                   "dont":["Use elevators","Stand near heavy objects"], "places":["Shelter","Hospital"]},
    "Theft": {"helpline":"100", "do":["Move to safe place","Call police","Note suspect details"],
              "dont":["Confront suspects","Chase alone"], "places":["Police Station","Hospital"]}
}

# -------------------------
# Cached nearby facilities
# -------------------------
@st.cache_data(ttl=300)
def generate_nearby(lat, lon, places):
    facilities = {}
    for i, name in enumerate(places):
        f_lat = lat + random.uniform(-0.006,0.006)
        f_lon = lon + random.uniform(-0.006,0.006)
        facilities[f"{name} {i+1}"] = {
            "coord":[f_lat,f_lon],
            "contact":f"+91-{random.randint(90000,99999)}{random.randint(1000,9999)}",
            "url":f"https://www.google.com/maps/search/?api=1&query={f_lat},{f_lon}"
        }
    return facilities

# -------------------------
# TTS function
# -------------------------
@st.cache_data
def make_tts(text, lang="en"):
    try:
        tts = gTTS(text=text, lang=lang)
        fp = BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp.read()
    except:
        return b""

# -------------------------
# Classifier
# -------------------------
def classify(text):
    text = (text or "").lower()
    mapping = {"fire":["smoke","fire","burn"], "medical":["bleed","hurt","faint"],
               "flood":["flood","water"], "earthquake":["quake","tremor"], 
               "theft":["stolen","robbery"], "accident":["accident","crash"]}
    for k,v in mapping.items():
        if any(word in text for word in v):
            return k.capitalize()
    return ""

# -------------------------
# Header
# -------------------------
st.markdown('<div class="header"><h2>🚨 Smart Emergency & Safety Assistant</h2>'
            '<div class="small-muted">Fast guidance • Nearby facilities • On-demand voice</div></div>', unsafe_allow_html=True)

# -------------------------
# Sidebar
# -------------------------
with st.sidebar:
    st.header("Quick Controls")
    city = st.selectbox("Select City", list(CITY_COORDS.keys()))
    user_text = st.text_area("Describe emergency (optional)")
    if st.button("🔴 PANIC"):
        st.warning("Panic activated! Call local emergency services immediately.")

# -------------------------
# Determine emergency
# -------------------------
detected = classify(user_text)
if detected:
    st.success(f"Detected emergency: {detected}")
    selected = detected
else:
    selected = st.radio("Or choose emergency:", ["Fire","Medical","Accident","Flood","Earthquake","Theft"])

# -------------------------
# Show info card
# -------------------------
db = EMERGENCY_DB[selected]
st.markdown(f"<div class='card'><h3>{selected} Emergency</h3>"
            f"<p class='small-muted'>Helpline: <b>{db['helpline']}</b></p></div>", unsafe_allow_html=True)

# -------------------------
# Do / Don't
# -------------------------
with st.expander("✔️ What TO DO / ✖️ What NOT to do"):
    st.markdown("**TO DO:**")
    for d in db["do"]:
        st.markdown(f"- {d}")
    st.markdown("**NOT TO DO:**")
    for d in db["dont"]:
        st.markdown(f"- {d}")

# -------------------------
# Nearby facilities map
# -------------------------
lat, lon = CITY_COORDS[city]
nearby = generate_nearby(lat, lon, db["places"])
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.markdown("### 🗺️ Nearby Facilities")
m = folium.Map(location=[lat, lon], zoom_start=12)
folium.Marker([lat,lon], popup="You are here", icon=folium.Icon(color="green")).add_to(m)
colors=["red","blue","purple","orange","darkred","cadetblue"]
for i,(name,data) in enumerate(nearby.items()):
    folium.Marker(location=data["coord"], 
                  popup=f"{name} — ☎️ {data['contact']}<br><a href='{data['url']}' target='_blank'>Open Maps</a>",
                  icon=folium.Icon(color=colors[i%len(colors)])).add_to(m)
st_folium(m, width=720, height=400)
st.markdown("</div>", unsafe_allow_html=True)

# -------------------------
# Voice guidance
# -------------------------
advice = f"{selected} emergency. Call {db['helpline']}. " + " ".join(db['do'][:3])
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.markdown("### 🔊 Voice Guidance")
col1, col2 = st.columns(2)
if col1.button("▶️ Play Guidance"):
    audio_bytes = make_tts(advice)
    if audio_bytes:
        st.audio(audio_bytes, format="audio/mp3")
if col2.button("⬇️ Download MP3"):
    audio_bytes = make_tts(advice)
    if audio_bytes:
        st.download_button(label="Download MP3", data=audio_bytes, file_name=f"{selected}_guidance.mp3", mime="audio/mp3")
st.markdown("</div>", unsafe_allow_html=True)

# -------------------------
# Transport / quick actions
# -------------------------
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.markdown("### 🚖 Quick Transport")
st.markdown(f"- Helpline: **{db['helpline']}**")
c1, c2 = st.columns(2)
c1.markdown("[🚕 Book Ola](https://www.olacabs.com/)")
c2.markdown("[🚗 Book Uber](https://www.uber.com/in/en/)")
st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("<div class='small-muted' style='text-align:center'>Made with ❤️ • Keep local helplines updated</div>", unsafe_allow_html=True)
