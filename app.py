import streamlit as st
import pandas as pd
from streamlit_folium import st_folium
import folium

# --------------------
# PAGE CONFIG
# --------------------
st.set_page_config(
    page_title="Smart Emergency Assistant 🚨",
    page_icon="🚨",
    layout="wide"
)

# --------------------
# CUSTOM CSS
# --------------------
st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #FF416C, #FF4B2B);
    font-family: 'Segoe UI', sans-serif;
}
.main {
    background-color: rgba(255,255,255,0.93);
    border-radius: 20px;
    padding: 2rem;
    box-shadow: 0 8px 20px rgba(0,0,0,0.15);
}
h1 {
    color: #FF4B2B;
    text-align: center;
    font-size: 2.5em;
}
h2 {
    color: #333;
    text-align: center;
}
.card {
    background: white;
    border-radius: 16px;
    padding: 1rem;
    margin-bottom: 1rem;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
.stButton>button {
    background: linear-gradient(90deg, #ff512f, #dd2476);
    color: white;
    border-radius: 10px;
    padding: 10px;
    border: none;
    font-weight: bold;
    transition: 0.3s;
}
.stButton>button:hover {
    background: linear-gradient(90deg, #dd2476, #ff512f);
    transform: scale(1.03);
}
</style>
""", unsafe_allow_html=True)

# --------------------
# HEADER
# --------------------
st.markdown("<h1>🚨 Smart Emergency & Safety Assistant</h1>", unsafe_allow_html=True)
st.markdown("<h2>AI-Powered Safety & Real-Time Support</h2>", unsafe_allow_html=True)
st.write("Stay safe during accidents, fires, floods, or medical emergencies — with real-time help, verified helplines, and smart assistance.")

# --------------------
# SIDEBAR
# --------------------
st.sidebar.header("⚙️ Select Details")
city = st.sidebar.selectbox("🏙️ Select Your City", ["Delhi", "Mumbai", "Bangalore", "Chennai", "Kolkata", "Hyderabad", "Pune", "Ahmedabad"])
etype = st.sidebar.selectbox("🚨 Emergency Type", ["Medical", "Fire", "Accident", "Flood", "Earthquake", "Theft"])

# --------------------
# EMERGENCY DATABASE
# --------------------
info = {
    "Medical": {"emoji": "🏥", "helpline": "108 / 102", "tip": "Call an ambulance and keep the patient calm."},
    "Fire": {"emoji": "🔥", "helpline": "101", "tip": "Evacuate immediately and stay low under smoke."},
    "Accident": {"emoji": "🚗", "helpline": "103", "tip": "Move injured people safely and call emergency services."},
    "Flood": {"emoji": "🌊", "helpline": "1070", "tip": "Move to higher ground and avoid flooded roads."},
    "Earthquake": {"emoji": "🌍", "helpline": "112", "tip": "Drop, cover, and hold until shaking stops."},
    "Theft": {"emoji": "👮", "helpline": "100", "tip": "Call the police and stay in a secure area."}
}

# --------------------
# SHOW EMERGENCY CARD
# --------------------
sel = info[etype]
st.markdown(f"""
<div class="card">
    <h2>{sel['emoji']} {etype} Emergency</h2>
    <b>Helpline:</b> {sel['helpline']}<br>
    <b>Safety Tip:</b> {sel['tip']}
</div>
""", unsafe_allow_html=True)

# --------------------
# LIVE MAP
# --------------------
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

lat, lon = CITY_COORDS[city]
st.markdown("### 🗺️ Nearby Emergency Facilities")

m = folium.Map(location=[lat, lon], zoom_start=12)
folium.Marker([lat, lon], popup="You are here", icon=folium.Icon(color="green")).add_to(m)
st_folium(m, width=700, height=450)

# --------------------
# TRANSPORT LINKS
# --------------------
st.markdown("### 🚖 Quick Transport")
col1, col2 = st.columns(2)
col1.link_button("🚕 Book Ola", "https://www.olacabs.com/")
col2.link_button("🚗 Book Uber", "https://www.uber.com/in/en/")

# --------------------
# FOOTER
# --------------------
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Made with ❤️ for safety — Powered by Streamlit</p>", unsafe_allow_html=True)
