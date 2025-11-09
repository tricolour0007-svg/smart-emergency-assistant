import streamlit as st
import folium
from streamlit_folium import st_folium
import random
from gtts import gTTS
from io import BytesIO
import base64

# --------------------------
# 🌍 City Coordinates
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
# 🎙️ Voice Helper
# --------------------------
def speak_text(text):
    tts = gTTS(text=text, lang='en')
    mp3_fp = BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    b64 = base64.b64encode(mp3_fp.read()).decode()
    audio_html = f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}"></audio>'
    st.markdown(audio_html, unsafe_allow_html=True)

# --------------------------
# 🏥 Facility Generator
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
# 🎨 App Layout
# --------------------------
st.set_page_config(page_title="Smart Emergency Assistant", page_icon="🚨", layout="wide")

st.markdown("<h1 style='text-align:center;color:red;'>🚨 Smart Emergency & Safety Assistant</h1>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    city = st.selectbox("🏙️ Select Your City", list(CITY_COORDS.keys()))
with col2:
    emergency = st.selectbox("⚠️ Select Emergency Type", list(EMERGENCY_INFO.keys()))

if st.button("🆘 Generate Assistance"):
    lat, lon = CITY_COORDS[city]
    info = EMERGENCY_INFO[emergency]
    
    st.success(f"📍 Location detected: {city}")
    speak_text(f"Detected your location in {city}. Providing help for {emergency}.")
    
    # Display safety instructions
    st.markdown("### ✅ Safety Instructions")
    for msg in info["message"]:
        st.markdown(f"- {msg}")
    speak_text(" ".join(info['message']))
    
    # Display emergency contacts
    st.markdown("### 📞 Emergency Contacts")
    for name, num in info["contacts"].items():
        st.markdown(f"**{name}:** {num}")
    
    # Nearby Facilities
    st.markdown("### 🏥 Nearby Facilities")
    nearby = generate_facilities(lat, lon, info["places"])
    for name, data in nearby.items():
        st.markdown(f"- **{name}** | ☎️ {data['contact']} | [📍 Open in Google Maps]({data['url']})")
    
    # Transport Options
    st.markdown("### 🚗 Transport Options")
    st.markdown(", ".join(info["transport"]))
    
    # Map
    st.markdown("### 🗺️ Emergency Map")
    m = folium.Map(location=[lat, lon], zoom_start=14)
    folium.Marker([lat, lon], popup="📍 You Are Here", icon=folium.Icon(color="green")).add_to(m)
    colors = ["red", "blue", "purple", "orange", "darkred", "cadetblue"]
    for i, (name, data) in enumerate(nearby.items()):
        folium.Marker(
            location=data["coord"],
            popup=f"<b>{name}</b><br>☎️ {data['contact']}<br><a href='{data['url']}' target='_blank'>Open in Google Maps</a>",
            icon=folium.Icon(color=colors[i % len(colors)])
        ).add_to(m)
    st_folium(m, width=700, height=450)

st.markdown("---")
st.markdown("<p style='text-align:center;'>💡 Stay calm, stay safe. Help is on the way.</p>", unsafe_allow_html=True)
