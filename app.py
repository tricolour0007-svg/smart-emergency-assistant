# app.py
import streamlit as st
import folium, random
from streamlit_folium import st_folium
from gtts import gTTS
from io import BytesIO
from datetime import datetime, timedelta

st.set_page_config(page_title="Smart Emergency Assistant 🚨",
                   page_icon="🚨", layout="wide")

# -------------------------
# CSS Styling
# -------------------------
st.markdown("""
<style>
body {background: linear-gradient(135deg,#FF6B6B,#FFD166);}
.header {padding:20px; border-radius:15px; color:white; text-align:center;
         background: linear-gradient(135deg,#ff416c,#ffcc66); box-shadow:0 6px 20px rgba(0,0,0,0.12);}
.card {padding:15px; border-radius:12px; color:white; margin-bottom:12px;}
.button {width:100%; padding:12px; border-radius:12px; font-weight:bold; font-size:16px;
         border:none; color:white; background: linear-gradient(90deg,#ff6b6b,#ff8a4b);}
.small-muted {color:#fff;font-size:13px;}
</style>
""", unsafe_allow_html=True)

# -------------------------
# City coordinates
# -------------------------
CITY_COORDS = {
    "Delhi":[28.6139,77.2090], "Mumbai":[19.0760,72.8777],
    "Bangalore":[12.9716,77.5946], "Chennai":[13.0827,80.2707],
    "Kolkata":[22.5726,88.3639], "Hyderabad":[17.3850,78.4867],
    "Pune":[18.5204,73.8567], "Ahmedabad":[23.0225,72.5714]
}

# -------------------------
# Emergency database
# -------------------------
EMERGENCY_DB = {
    "Fire": {"helpline":"101","do":["Move outside quickly","Stay low under smoke","Cover mouth with wet cloth"],
             "dont":["Use elevators","Open burning windows"],"places":["Fire Station","Hospital"]},
    "Medical": {"helpline":"108","do":["Call ambulance","Check breathing","Control bleeding"],
                "dont":["Give medicines to unconscious","Move injured"],"places":["Hospital","Clinic"]},
    "Accident": {"helpline":"108","do":["Ensure scene safety","Call emergency services","Stop bleeding"],
                 "dont":["Crowd injured","Move victims unless danger"],"places":["Hospital","Police Station"]},
    "Flood": {"helpline":"1070","do":["Move to higher ground","Switch off electricity","Follow evacuation orders"],
              "dont":["Walk/drive through water","Ignore warnings"],"places":["Shelter","Hospital"]},
    "Earthquake": {"helpline":"112","do":["Drop, Cover, Hold On","Stay away from glass","Move to open space"],
                   "dont":["Use elevators","Stand near heavy objects"],"places":["Shelter","Hospital"]},
    "Theft": {"helpline":"100","do":["Move to safe place","Call police","Note suspect details"],
              "dont":["Confront suspects","Chase alone"],"places":["Police Station","Hospital"]}
}

# -------------------------
# Cached nearby facilities
# -------------------------
@st.cache_data(ttl=300)
def generate_nearby(lat, lon, places):
    facilities={}
    for i,name in enumerate(places):
        f_lat=lat+random.uniform(-0.006,0.006)
        f_lon=lon+random.uniform(-0.006,0.006)
        facilities[f"{name} {i+1}"]={"coord":[f_lat,f_lon],
                                    "contact":f"+91-{random.randint(90000,99999)}{random.randint(1000,9999)}",
                                    "url":f"https://www.google.com/maps/search/?api=1&query={f_lat},{f_lon}"}
    return facilities

# -------------------------
# TTS function
# -------------------------
@st.cache_data
def make_tts(text, lang="en"):
    try:
        tts=gTTS(text=text, lang=lang)
        fp=BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp.read()
    except:
        return b""

# -------------------------
# Header
# -------------------------
st.markdown('<div class="header"><h2>🚨 Smart Emergency & Safety Assistant</h2>'
            '<div class="small-muted">Real-time Help • Voice Guidance • Nearby Facilities</div></div>', unsafe_allow_html=True)

# -------------------------
# Sidebar controls
# -------------------------
with st.sidebar:
    st.header("Emergency Controls")
    city = st.selectbox("City", list(CITY_COORDS.keys()))
    lang = st.selectbox("Voice Language", ["English","Hindi"])
    emergency_type = st.radio("Emergency Type", list(EMERGENCY_DB.keys()))
    severity = st.radio("Severity", ["Low","Medium","High","Critical"])
    st.markdown("## Nearby Facilities Filter")
    selected_places = st.multiselect("Select facility types", ["Hospital","Clinic","Police Station","Fire Station","Pharmacy","Shelter"], default=["Hospital","Clinic","Police Station"])
    if st.button("🔴 PANIC ALERT"):
        st.warning("Panic Activated! Call local emergency services immediately.")
    if st.button("🚑 Book Ambulance (ETA 10min)"):
        st.success("Ambulance booked! ETA: 10 minutes.")

# -------------------------
# Emergency instructions
# -------------------------
db = EMERGENCY_DB[emergency_type]
st.markdown(f"### 🚨 {emergency_type} Emergency | Helpline: {db['helpline']}")
with st.expander("✔️ What TO DO / ✖️ What NOT TO DO"):
    st.markdown("**TO DO:**")
    for d in db["do"]: st.markdown(f"- {d}")
    st.markdown("**NOT TO DO:**")
    for d in db["dont"]: st.markdown(f"- {d}")

# -------------------------
# Nearby facilities map
# -------------------------
lat, lon = CITY_COORDS[city]
nearby = generate_nearby(lat, lon, selected_places)
m = folium.Map(location=[lat, lon], zoom_start=12)
folium.Marker([lat, lon], popup="You are here", icon=folium.Icon(color="green")).add_to(m)
colors=["red","blue","purple","orange","darkred","cadetblue"]
for i,(name,data) in enumerate(nearby.items()):
    folium.Marker(location=data["coord"],
                  popup=f"{name} — ☎️ {data['contact']}<br><a href='{data['url']}' target='_blank'>Open Maps</a>",
                  icon=folium.Icon(color=colors[i%len(colors)])).add_to(m)
st_folium(m, width=720, height=400)

# -------------------------
# Voice guidance
# -------------------------
advice = f"{emergency_type} emergency. Call {db['helpline']}. " + " ".join(db['do'])
col1, col2 = st.columns(2)
if col1.button("▶️ Play Guidance"):
    audio_bytes = make_tts(advice, lang="hi" if lang=="Hindi" else "en")
    if audio_bytes: st.audio(audio_bytes, format="audio/mp3")
if col2.button("⬇️ Download MP3"):
    audio_bytes = make_tts(advice, lang="hi" if lang=="Hindi" else "en")
    if audio_bytes:
        st.download_button(label="Download MP3", data=audio_bytes, file_name=f"{emergency_type}_guidance.mp3", mime="audio/mp3")

# -------------------------
# Quick Transport & Contacts
# -------------------------
st.markdown("### 🚖 Quick Transport / Emergency Contacts")
c1,c2,c3=st.columns(3)
c1.markdown(f"[🚕 Book Ola](https://www.olacabs.com/)")
c2.markdown(f"[🚗 Book Uber](https://www.uber.com/in/en/)")
c3.markdown(f"☎️ Ambulance: {db['helpline']}")

st.markdown("---")
st.markdown("Made with ❤️ • Always update local helplines")
