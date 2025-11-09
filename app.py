import streamlit as st
import folium, random
from streamlit_folium import st_folium
from gtts import gTTS
from io import BytesIO
from base64 import b64encode

# --------------------------
# 🗺️ City Coordinates
# --------------------------
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

# --------------------------
# 🚨 Emergency Info
# --------------------------
EMERGENCY_INFO = {
    "Accident": {
        "contacts": {"🚑 Ambulance": "108", "👮 Police": "100"},
        "message": [
            "Stop bleeding and keep the injured person still.",
            "Call for medical help immediately."
        ],
        "places": ["Hospital", "Clinic", "Police Station", "Pharmacy"],
        "transport": ["Ambulance", "Private Vehicle", "Taxi"]
    },
    "Fire": {
        "contacts": {"🔥 Fire Dept": "101", "👮 Police": "100"},
        "message": [
            "Use nearest exit and stay low under smoke.",
            "Avoid elevators and cover your nose with a wet cloth."
        ],
        "places": ["Fire Station", "Hospital", "Clinic", "Pharmacy"],
        "transport": ["Fire Truck", "Private Vehicle"]
    },
    "Flood": {
        "contacts": {"🌊 Disaster Helpline": "1070", "🏛️ Municipal Control": "155303"},
        "message": [
            "Move to higher ground immediately.",
            "Avoid flooded areas and turn off electricity."
        ],
        "places": ["Shelter", "Hospital", "Police Station", "Pharmacy"],
        "transport": ["Boat", "Private Vehicle"]
    },
    "Earthquake": {
        "contacts": {"🌍 Disaster Helpline": "1070"},
        "message": [
            "Drop, Cover, and Hold On if indoors.",
            "Stay away from buildings and power lines."
        ],
        "places": ["Shelter", "Hospital", "Fire Station", "Emergency Kit"],
        "transport": ["Walk", "Private Vehicle"]
    },
    "Medical": {
        "contacts": {"🚑 Ambulance": "108", "🏥 Hospital": "102"},
        "message": [
            "Call an ambulance immediately.",
            "Keep the person comfortable and check vital signs."
        ],
        "places": ["Hospital", "Pharmacy", "Clinic"],
        "transport": ["Ambulance", "Private Vehicle", "Taxi"]
    },
    "Theft": {
        "contacts": {"👮 Police": "100"},
        "message": [
            "Move to a safe and visible area.",
            "Call the police immediately and stay calm."
        ],
        "places": ["Police Station", "Hospital", "Safe Zone"],
        "transport": ["Walk", "Taxi", "Bus"]
    }
}

# --------------------------
# 🗣️ Voice Assistant
# --------------------------
def speak(text):
    tts = gTTS(text=text, lang='en')
    fp = BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    audio_bytes = fp.read()
    st.audio(audio_bytes, format="audio/mp3")

# --------------------------
# 🏥 Generate Facilities
# --------------------------
def generate_facilities(lat, lon, facility_list):
    facilities = {}
    for name in facility_list:
        f_lat = lat + random.uniform(-0.005, 0.005)
        f_lon = lon + random.uniform(-0.005, 0.005)
        facilities[name] = {
            "coord": [f_lat, f_lon],
            "contact": f"+91-{random.randint(10000,99999)}{random.randint(10000,99999)}",
            "url": f"https://www.google.com/maps/search/?api=1&query={f_lat},{f_lon}"
        }
    return facilities

# --------------------------
# 🌟 Streamlit UI
# --------------------------
st.set_page_config(page_title="Smart Emergency Assistant", layout="wide")

st.markdown("<h1 style='text-align:center;color:red;'>🚨 Smart Emergency & Safety Assistant 🚨</h1>", unsafe_allow_html=True)

city = st.selectbox("🏙️ Select your city:", list(CITY_COORDS.keys()))
emergency = st.selectbox("⚠️ Select type of emergency:", list(EMERGENCY_INFO.keys()))

if st.button("🔍 Get Emergency Assistance"):
    lat, lon = CITY_COORDS.get(city, [28.6139, 77.2090])
    info = EMERGENCY_INFO[emergency]

    st.success(f"📍 Detected Location: {city}")
    speak(f"Detected your location in {city}")

    nearby = generate_facilities(lat, lon, info["places"])

    st.subheader("🏥 Nearby Facilities")
    for name, data in nearby.items():
        st.markdown(f"**{name}** — ☎️ {data['contact']} — [📍 Open in Google Maps]({data['url']})")
    speak(f"Nearby facilities include {', '.join(nearby.keys())}.")

    st.subheader("✅ Safety Instructions")
    for step in info["message"]:
        st.markdown(f"- {step}")
    speak(" ".join(info["message"]))

    st.subheader("📞 Emergency Contacts")
    for name, num in info["contacts"].items():
        st.markdown(f"**{name}:** {num}")
    speak("Emergency contact numbers displayed on screen.")

    # Map
    m = folium.Map(location=[lat, lon], zoom_start=14)
    folium.Marker([lat, lon], popup="📍 You Are Here", icon=folium.Icon(color="green")).add_to(m)
    for name, data in nearby.items():
        folium.Marker(location=data["coord"],
                      popup=f"<b>{name}</b><br>☎️ {data['contact']}",
                      icon=folium.Icon(color="red")).add_to(m)
    st_data = st_folium(m, width=700, height=450)
