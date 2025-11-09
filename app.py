# app.py
import streamlit as st
import folium
from streamlit_folium import st_folium
from gtts import gTTS
from io import BytesIO
import base64
import random
from typing import Dict, List, Any

# -------------------------
# Page config
# -------------------------
st.set_page_config(page_title="Smart Emergency Assistant",
                   page_icon="🚨", layout="wide")

# -------------------------
# Simple CSS for nicer UI
# -------------------------
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {background: linear-gradient(135deg,#ff6b6b,#ffd166); background-attachment: fixed;}
.header {background: linear-gradient(90deg,#ff416c,#ffcc66); padding:18px; border-radius:12px; color:white; text-align:center; box-shadow:0 6px 20px rgba(0,0,0,0.12);}
.card {background: rgba(255,255,255,0.96); padding:14px; border-radius:12px; box-shadow: 0 6px 20px rgba(0,0,0,0.06); margin-bottom:12px;}
.big-button {width:100%; padding:12px; border-radius:12px; font-weight:700; font-size:16px; border:none; color:white; background: linear-gradient(90deg,#ff6b6b,#ff8a4b);}
.small-muted {color:#555; font-size:13px;}
.btn-row {display:flex; gap:10px;}
</style>
""", unsafe_allow_html=True)

# -------------------------
# Data (emergency DB + cities)
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

EMERGENCY_DB: Dict[str, Dict[str, Any]] = {
    "Fire": {
        "helpline": "101",
        "do": ["Move outside quickly", "Stay low to avoid smoke", "Cover mouth with wet cloth"],
        "dont": ["Use elevators", "Open burning windows"],
        "places": ["Fire Station", "Hospital"]
    },
    "Medical": {
        "helpline": "108 / 102",
        "do": ["Call ambulance", "Check airway and breathing", "Control severe bleeding"],
        "dont": ["Give oral medicines to unconscious people", "Move seriously injured unnecessarily"],
        "places": ["Hospital", "Clinic", "Pharmacy"]
    },
    "Accident": {
        "helpline": "108 / 103",
        "do": ["Ensure scene safety", "Call emergency services", "Stop severe bleeding"],
        "dont": ["Crowd the injured", "Move victims unless immediate danger"],
        "places": ["Hospital", "Police Station"]
    },
    "Flood": {
        "helpline": "1070",
        "do": ["Move to higher ground", "Switch off electricity if safe", "Follow official evacuation orders"],
        "dont": ["Walk/drive through flood water", "Ignore warnings"],
        "places": ["Shelter", "Hospital"]
    },
    "Earthquake": {
        "helpline": "112",
        "do": ["Drop, Cover and Hold On", "Stay away from glass", "Move to open space after shaking stops"],
        "dont": ["Use elevators", "Stand near heavy objects"],
        "places": ["Shelter", "Hospital"]
    },
    "Theft": {
        "helpline": "100",
        "do": ["Move to a safe place", "Call the police", "Note suspect details"],
        "dont": ["Confront suspects", "Chase alone"],
        "places": ["Police Station", "Hospital"]
    }
}

# -------------------------
# Cache: generate nearby facilities (lightweight)
# -------------------------
@st.cache_data(ttl=300)
def generate_nearby(lat: float, lon: float, places: List[str]) -> Dict[str, Dict]:
    out = {}
    for i, name in enumerate(places):
        f_lat = lat + random.uniform(-0.006, 0.006)
        f_lon = lon + random.uniform(-0.006, 0.006)
        out[f"{name} {i+1}"] = {
            "coord": [f_lat, f_lon],
            "contact": f"+91-{random.randint(90000,99999)}{random.randint(1000,9999)}",
            "url": f"https://www.google.com/maps/search/?api=1&query={f_lat},{f_lon}"
        }
    return out

# -------------------------
# TTS: safe cached generator
# -------------------------
@st.cache_data(show_spinner=False)
def make_tts_audio_bytes(text: str, lang: str = "en") -> bytes:
    try:
        tts = gTTS(text=text, lang=lang)
        fp = BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp.read()
    except Exception:
        return b""

# -------------------------
# Simple rule-based classifier (AI-style)
# -------------------------
def classify_text_to_emergency(text: str) -> str:
    t = (text or "").lower()
    mapping = {
        "fire": ["smoke", "fire", "flames", "burn"],
        "medical": ["faint", "bleed", "injury", "hurt", "chest pain", "unconscious"],
        "flood": ["flood", "water", "inundated", "submerged"],
        "earthquake": ["earthquake", "quake", "tremor", "shake"],
        "theft": ["robbery", "stolen", "theft", "thief", "attack"],
        "accident": ["accident", "crash", "hit", "car accident"]
    }
    for cat, keys in mapping.items():
        if any(k in t for k in keys):
            return cat.capitalize()
    return ""

# -------------------------
# UI header
# -------------------------
st.markdown('<div class="header"><h2 style="margin:0">🚨 Smart Emergency & Safety Assistant</h2>'
            '<div class="small-muted">Fast guidance • Nearby facilities • On-demand voice</div></div>', unsafe_allow_html=True)
st.write("")

# -------------------------
# Layout: sidebar + main
# -------------------------
with st.sidebar:
    st.header("Quick Controls")
    city = st.selectbox("City", list(CITY_COORDS.keys()), index=0)
    st.markdown("---")
    st.markdown("Describe your situation (optional):")
    user_text = st.text_area("Type here (e.g. 'There is smoke in my kitchen')", height=80)
    st.markdown("---")
    if st.button("🔴 PANIC — Show urgent instructions"):
        st.session_state["selected"] = st.session_state.get("selected", "")  # no-op, just visual
        st.warning("Panic activated! Call local emergency services now and follow the instructions shown.")
    st.markdown("App works best on desktop and mobile. Tap Play to hear guidance (no autoplay).")

# If classifier finds an emergency, set selection
detected = classify_text_to_emergency(user_text)
if detected:
    st.success(f"Detected emergency: **{detected}** (from your description)")
    st.session_state["selected"] = detected

# Buttons row (big)
cols = st.columns(3)
if cols[0].button("🔥 FIRE"):
    st.session_state["selected"] = "Fire"
if cols[1].button("🏥 MEDICAL"):
    st.session_state["selected"] = "Medical"
if cols[2].button("🚓 POLICE"):
    st.session_state["selected"] = "Theft"

cols2 = st.columns(3)
if cols2[0].button("🌊 FLOOD"):
    st.session_state["selected"] = "Flood"
if cols2[1].button("🌍 EARTHQUAKE"):
    st.session_state["selected"] = "Earthquake"
if cols2[2].button("🚗 ACCIDENT"):
    st.session_state["selected"] = "Accident"

selected = st.session_state.get("selected", None)

# -------------------------
# If nothing selected: show guidance
# -------------------------
if not selected:
    st.info("Select an emergency from the buttons above or type your situation in the sidebar to auto-detect.")
    st.stop()

# -------------------------
# Show emergency card
# -------------------------
db = EMERGENCY_DB.get(selected, {})
helpline = db.get("helpline", "N/A")
dos = db.get("do", [])
donts = db.get("dont", [])
places = db.get("places", [])

st.markdown(f"<div class='card'><h3 style='margin:0'>{selected} Emergency</h3>"
            f"<p class='small-muted' style='margin:0'>Helpline: <b>{helpline}</b></p></div>", unsafe_allow_html=True)

# copy number button
if st.button("📋 Copy Helpline to Clipboard"):
    try:
        st.experimental_set_clipboard(helpline)
        st.success("Helpline copied to clipboard")
    except Exception:
        st.error("Unable to copy to clipboard in this browser.")

# Do / Don't lists
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.markdown("**✔️ What TO DO**")
for i, t in enumerate(dos, 1):
    st.markdown(f"{i}. {t}")
st.markdown("**✖️ What NOT to do**")
for i, t in enumerate(donts, 1):
    st.markdown(f"{i}. {t}")
st.markdown("</div>", unsafe_allow_html=True)

# -------------------------
# Nearby facilities & map (cached)
# -------------------------
lat, lon = CITY_COORDS.get(city, [20.5937, 78.9629])
nearby = generate_nearby(lat, lon, places)

st.markdown("<div class='card'>", unsafe_allow_html=True)
st.markdown("### 🗺️ Nearby Facilities (approximate)")
m = folium.Map(location=[lat, lon], zoom_start=12, control_scale=True)
folium.Marker([lat, lon], popup="You are here", icon=folium.Icon(color="green")).add_to(m)
colors = ["red", "blue", "purple", "orange", "darkred", "cadetblue"]
for i, (name, data) in enumerate(nearby.items()):
    folium.Marker(location=data["coord"],
                  popup=f"{name} — ☎️ {data['contact']}<br><a href='{data['url']}' target='_blank'>Open in Maps</a>",
                  icon=folium.Icon(color=colors[i % len(colors)])).add_to(m)

# show map with st_folium; wrapped in try/except to avoid crashes
try:
    st_folium(m, width=720, height=420)
except Exception as e:
    st.error("Map rendering failed in this session. Try refreshing the page.")

st.markdown("</div>", unsafe_allow_html=True)

# -------------------------
# Voice guidance (play & download)
# -------------------------
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.markdown("### 🔊 Voice Guidance (on-demand)")
short_advice = f"{selected} emergency. Call {helpline}. " + (" ".join(dos[:3]) if dos else "")
col_play, col_dl = st.columns([1, 1])
if col_play.button("▶️ Play Guidance (safe)"):
    audio_bytes = make_tts_audio_bytes(short_advice)
    if audio_bytes:
        st.audio(audio_bytes, format="audio/mp3")
    else:
        st.error("Voice generation failed. Try again shortly.")
if col_dl.button("⬇️ Download MP3"):
    audio_bytes = make_tts_audio_bytes(short_advice)
    if audio_bytes:
        st.download_button(label="Download MP3", data=audio_bytes, file_name=f"{selected}_guidance.mp3", mime="audio/mp3")
    else:
        st.error("Unable to generate audio.")
st.markdown("</div>", unsafe_allow_html=True)

# -------------------------
# Quick transport links and final footer
# -------------------------
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.markdown("### 🚖 Quick Transport & Actions")
st.write(f"- Helpline: **{helpline}** — call from mobile or copy above")
c1, c2 = st.columns(2)
c1.markdown("[🚕 Book Ola](https://www.olacabs.com/)")
c2.markdown("[🚗 Book Uber](https://www.uber.com/in/en/)")
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")
st.markdown("<div class='small-muted' style='text-align:center'>Made with ❤️ • Keep local helplines updated • For SMS/call automation integrate a telephony backend (Twilio)</div>", unsafe_allow_html=True)
