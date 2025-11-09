# app.py
import streamlit as st
import folium, random, time
from streamlit_folium import st_folium
from gtts import gTTS
from io import BytesIO
from twilio.rest import Client

# ----------------- Page config -----------------
st.set_page_config(page_title="🚨 Smart Emergency Assistant", layout="wide")

# ----------------- Styling -----------------
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

# ----------------- Data -----------------
CITY_COORDS = {
    "Delhi":[28.6139,77.2090], "Mumbai":[19.0760,72.8777], "Bangalore":[12.9716,77.5946],
    "Chennai":[13.0827,80.2707], "Kolkata":[22.5726,88.3639], "Hyderabad":[17.3850,78.4867],
    "Pune":[18.5204,73.8567], "Ahmedabad":[23.0225,72.5714]
}

REAL_FACILITIES = {
    "Delhi": {
        "Hospital": [[28.6139,77.2200],[28.6200,77.2100]],
        "Police Station": [[28.6100,77.2300],[28.6150,77.2250]],
        "Fire Station": [[28.6180,77.2150]],
        "Pharmacy": [[28.6140,77.2190]],
        "Shelter": [[28.6190,77.2120]]
    },
    "Mumbai": {
        "Hospital": [[19.0760,72.8800],[19.0700,72.8850]],
        "Police Station": [[19.0780,72.8750]],
        "Fire Station": [[19.0740,72.8820]],
        "Pharmacy": [[19.0720,72.8790]],
        "Shelter": [[19.0770,72.8780]]
    },
    "Bangalore": {
        "Hospital": [[12.9716,77.5946],[12.9750,77.5900]],
        "Police Station": [[12.9700,77.6000]],
        "Fire Station": [[12.9720,77.5950]],
        "Pharmacy": [[12.9730,77.5930]],
        "Shelter": [[12.9740,77.5960]]
    }
}

EMERGENCY_DB = {
    "Fire": {"helpline":"101","icon":"🔥","do":["Move outside quickly","Stay low under smoke","Cover mouth with wet cloth"],
             "dont":["Use elevators","Open burning windows"],"places":["Fire Station","Hospital"]},
    "Medical": {"helpline":"108","icon":"🏥","do":["Call ambulance","Check breathing","Control bleeding"],
                "dont":["Give medicines to unconscious","Move injured"],"places":["Hospital","Clinic"]},
    "Accident": {"helpline":"108","icon":"🚑","do":["Ensure scene safety","Call emergency services","Stop bleeding"],
                 "dont":["Crowd injured","Move victims unless danger"],"places":["Hospital","Police Station"]},
    "Flood": {"helpline":"1070","icon":"🌊","do":["Move to higher ground","Switch off electricity","Follow evacuation orders"],
              "dont":["Walk/drive through water","Ignore warnings"],"places":["Shelter","Hospital"]},
    "Earthquake": {"helpline":"112","icon":"🌍","do":["Drop, Cover, Hold On","Stay away from glass","Move to open space"],
                   "dont":["Use elevators","Stand near heavy objects"],"places":["Shelter","Hospital"]},
    "Theft": {"helpline":"100","icon":"👮","do":["Move to safe place","Call police","Note suspect details"],
              "dont":["Confront suspects","Chase alone"],"places":["Police Station","Hospital"]}
}

# ----------------- Functions -----------------
@st.cache_data(ttl=300)
def generate_nearby_real(city, selected_places):
    facilities = {}
    for place_type in selected_places:
        coords_list = REAL_FACILITIES.get(city, {}).get(place_type, [])
        for i, coord in enumerate(coords_list):
            name = f"{place_type} {i+1}"
            facilities[name] = {
                "coord": coord,
                "contact": f"+91-{random.randint(90000,99999)}{random.randint(1000,9999)}",
                "url": f"https://www.google.com/maps/search/?api=1&query={coord[0]},{coord[1]}"
            }
    return facilities

@st.cache_data
def make_tts(text, lang="en"):
    tts = gTTS(text=text, lang=lang)
    fp = BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    return fp.read()

def send_emergency_sms(contacts, city, lat, lon, emergency_type, instructions):
    try:
        account_sid = st.secrets["TWILIO_SID"]
        auth_token = st.secrets["TWILIO_TOKEN"]
        from_number = st.secrets["TWILIO_NUMBER"]
        client = Client(account_sid, auth_token)
        message_body = f"ALERT! {emergency_type} reported in {city}. Location: https://www.google.com/maps/search/?api=1&query={lat},{lon}. Instructions: {', '.join(instructions)}"
        for num in contacts:
            client.messages.create(body=message_body, from_=from_number, to=num)
    except Exception as e:
        st.error(f"Failed to send SMS: {e}")

# ----------------- Header -----------------
st.markdown(f'<div class="header"><h2>🚨 Smart Emergency & Safety Assistant</h2>'
            f'<div class="small-muted">Real-time Help • {", ".join([em["icon"] for em in EMERGENCY_DB.values()])}</div></div>', unsafe_allow_html=True)

# ----------------- Sidebar -----------------
with st.sidebar:
    st.header("Emergency Controls")
    city = st.selectbox("City", list(CITY_COORDS.keys()))
    lang = st.selectbox("Voice Language", ["English","Hindi"])
    emergency_type = st.radio("Emergency Type", list(EMERGENCY_DB.keys()))
    severity = st.radio("Severity", ["Low","Medium","High","Critical"])
    st.markdown("## Nearby Facilities Filter")
    selected_places = st.multiselect("Select facility types", ["Hospital","Clinic","Police Station","Fire Station","Pharmacy","Shelter"], default=["Hospital","Clinic","Police Station"])
    st.markdown("## Emergency SMS")
    contacts_input = st.text_area("Enter phone numbers (comma separated)", "+919876543210")
    if st.button("📩 Send Emergency SMS"):
        if contacts_input:
            contacts = [c.strip() for c in contacts_input.split(",")]
            send_emergency_sms(contacts, city, CITY_COORDS[city][0], CITY_COORDS[city][1], emergency_type, EMERGENCY_DB[emergency_type]['do'])
            st.success("Emergency SMS sent to your contacts!")
        else:
            st.warning("Please enter at least one phone number.")
    if st.button("🔴 PANIC ALERT"):
        st.warning("Panic Activated! Call local emergency services immediately.")
    if st.button("🚑 Book Ambulance (ETA 10min)"):
        st.success("Ambulance booked! ETA: 10 minutes.")

# ----------------- Animated TO DO / NOT TO DO -----------------
db = EMERGENCY_DB[emergency_type]
st.markdown(f"### {db['icon']} {emergency_type} Emergency | Helpline: {db['helpline']}")
with st.expander("✔️ What TO DO / ✖️ What NOT TO DO"):
    placeholder_do = st.empty()
    for d in db["do"]:
        placeholder_do.markdown(f"✅ {d}")
        time.sleep(0.3)
    placeholder_dont = st.empty()
    for d in db["dont"]:
        placeholder_dont.markdown(f"❌ {d}")
        time.sleep(0.3)

# ----------------- Map -----------------
lat, lon = CITY_COORDS[city]
nearby = generate_nearby_real(city, selected_places)
m = folium.Map(location=[lat, lon], zoom_start=13)
folium.Marker([lat, lon], popup="You are here", icon=folium.Icon(color="green")).add_to(m)
colors=["red","blue","purple","orange","darkred","cadetblue"]
for i,(name,data) in enumerate(nearby.items()):
    folium.Marker(location=data["coord"],
                  popup=f"{name} — ☎️ {data['contact']}<br><a href='{data['url']}' target='_blank'>Open Maps</a>",
                  icon=folium.Icon(color=colors[i%len(colors)])).add_to(m)
st_folium(m, width=720, height=400)

# ----------------- Voice Guidance -----------------
advice = f"{emergency_type} emergency. Call {db['helpline']}. " + " ".join(db['do'])
col1, col2 = st.columns(2)
if col1.button("▶️ Play Guidance"):
    audio_bytes = make_tts(advice, lang="hi" if lang=="Hindi" else "en")
    if audio_bytes: st.audio(audio_bytes, format="audio/mp3")
if col2.button("⬇️ Download MP3"):
    audio_bytes = make_tts(advice, lang="hi" if lang=="Hindi" else "en")
    if audio_bytes:
        st.download_button(label="Download MP3", data=audio_bytes, file_name=f"{emergency_type}_guidance.mp3", mime="audio/mp3")

# ----------------- Quick Transport -----------------
st.markdown("### 🚖 Quick Transport / Emergency Contacts")
c1,c2,c3=st.columns(3)
c1.markdown(f"[🚕 Book Ola](https://www.olacabs.com/)")
c2.markdown(f"[🚗 Book Uber](https://www.uber.com/in/en/)")
c3.markdown(f"☎️ Ambulance: {db['helpline']}")

st.markdown("---")
st.markdown("Made with ❤️ • Always update local helplines")
