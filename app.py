import streamlit as st
import pandas as pd

# --- PAGE CONFIG ---
st.set_page_config(page_title="Smart Emergency Assistant", page_icon="🚨", layout="wide")

# --- STYLING ---
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #ff512f, #dd2476);
    background-attachment: fixed;
}
.main {
    background: rgba(255,255,255,0.92);
    border-radius: 25px;
    padding: 40px;
    box-shadow: 0 0 20px rgba(0,0,0,0.2);
}
.stButton>button {
    width: 100%;
    border: none;
    color: white;
    font-size: 18px;
    font-weight: bold;
    background: linear-gradient(90deg, #ff4b1f, #ff9068);
    border-radius: 12px;
    height: 3em;
    transition: 0.3s;
}
.stButton>button:hover {
    transform: scale(1.05);
    background: linear-gradient(90deg, #ff9068, #ff4b1f);
}
.card {
    background: white;
    padding: 15px;
    border-radius: 15px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    margin-bottom: 10px;
}
h1 { text-align:center; color:white; }
h3 { color:#ff4b1f; }
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown("<h1>🚨 Smart Emergency Assistant</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:white;'>Your one-stop platform for quick, verified help during emergencies.</p>", unsafe_allow_html=True)

# --- INPUTS ---
col1, col2 = st.columns(2)
city = col1.text_input("🏙️ Enter City", placeholder="e.g., Delhi, Mumbai, Chennai")
etype = col2.selectbox("⚠️ Select Emergency Type", 
                       ["Select...", "Medical", "Fire", "Police", "Accident", "Flood", "Earthquake"])

# --- ACTION ---
if city and etype != "Select...":
    st.success(f"Showing emergency resources for {etype} in {city}")

    # --- Light map using Streamlit built-in ---
    st.markdown("### 🗺️ Nearby Emergency Centers (approximate)")
    data = pd.DataFrame({
        'lat': [28.61, 19.07, 13.08, 22.57],
        'lon': [77.23, 72.87, 80.27, 88.36],
    })
    st.map(data, zoom=4)

    # --- Info Cards ---
    st.markdown("### 📞 Emergency Contacts")
    info = {
        "Medical": ("🏥 Ambulance", "102 / 108", "Apply first aid and stay calm."),
        "Fire": ("🔥 Fire Department", "101", "Evacuate immediately and avoid elevators."),
        "Police": ("👮 Police", "100", "Stay safe and cooperate with authorities."),
        "Accident": ("🚗 Traffic Helpline", "103", "Call ambulance and document the scene."),
        "Flood": ("🌊 Disaster Helpline", "1078", "Move to higher ground immediately."),
        "Earthquake": ("🌍 Emergency", "112", "Drop, cover, and hold until shaking stops.")
    }

    title, helpline, tip = info[etype]
    st.markdown(f"""
        <div class='card'>
            <h3>{title}</h3>
            <b>Helpline:</b> {helpline}<br>
            <b>Tip:</b> {tip}
        </div>
    """, unsafe_allow_html=True)

    # --- Transport Links ---
    st.markdown("### 🚖 Quick Transport Links")
    colA, colB = st.columns(2)
    colA.link_button("🚕 Book Ola", "https://www.olacabs.com/")
    colB.link_button("🚗 Book Uber", "https://www.uber.com/in/en/")

st.markdown("<hr><p style='text-align:center;color:gray;'>Made with ❤️ using Streamlit — Stay Safe</p>", unsafe_allow_html=True)
