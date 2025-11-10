# app.py
import streamlit as st
import folium, random, time, os
from streamlit_folium import st_folium
from gtts import gTTS
from io import BytesIO
from twilio.rest import Client
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

# ----------------- Page config -----------------
st.set_page_config(page_title="🚨 Smart Emergency Assistant (Data Science)", layout="wide")

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

# ----------------- Data & Constants -----------------
DATA_PATH = "data"
CSV_FILE = os.path.join(DATA_PATH, "emergency_data.csv")

CITY_COORDS = {
    "Delhi":[28.6139,77.2090], "Mumbai":[19.0760,72.8777], "Bangalore":[12.9716,77.5946],
    "Chennai":[13.0827,80.2707], "Kolkata":[22.5726,88.3639], "Hyderabad":[17.3850,78.4867],
    "Pune":[18.5204,73.8567], "Ahmedabad":[23.0225,72.5714]
}

REAL_FACILITIES = {
    "Delhi": {"Hospital":[[28.6139,77.2200],[28.6200,77.2100]],
              "Police Station":[[28.6100,77.2300],[28.6150,77.2250]],
              "Fire Station":[[28.6180,77.2150]],
              "Pharmacy":[[28.6140,77.2190]],
              "Shelter":[[28.6190,77.2120]]},
    "Mumbai": {"Hospital":[[19.0760,72.8800],[19.0700,72.8850]],
               "Police Station":[[19.0780,72.8750]],
               "Fire Station":[[19.0740,72.8820]],
               "Pharmacy":[[19.0720,72.8790]],
               "Shelter":[[19.0770,72.8780]]},
    "Bangalore": {"Hospital":[[12.9716,77.5946],[12.9750,77.5900]],
                  "Police Station":[[12.9700,77.6000]],
                  "Fire Station":[[12.9720,77.5950]],
                  "Pharmacy":[[12.9730,77.5930]],
                  "Shelter":[[12.9740,77.5960]]}
}

EMERGENCY_DB = {
    "Fire":{"helpline":"101","icon":"🔥",
            "do":["Move outside quickly","Stay low under smoke","Cover mouth with wet cloth"],
            "dont":["Use elevators","Open burning windows"],
            "places":["Fire Station","Hospital"]},
    "Medical":{"helpline":"108","icon":"🏥",
               "do":["Call ambulance","Check breathing","Control bleeding"],
               "dont":["Give medicines to unconscious","Move injured"],
               "places":["Hospital","Clinic"]},
    "Accident":{"helpline":"108","icon":"🚑",
                "do":["Ensure scene safety","Call emergency services","Stop bleeding"],
                "dont":["Crowd injured","Move victims unless danger"],
                "places":["Hospital","Police Station"]},
    "Flood":{"helpline":"1070","icon":"🌊",
             "do":["Move to higher ground","Switch off electricity","Follow evacuation orders"],
             "dont":["Walk/drive through water","Ignore warnings"],
             "places":["Shelter","Hospital"]},
    "Earthquake":{"helpline":"112","icon":"🌍",
                  "do":["Drop, Cover, Hold On","Stay away from glass","Move to open space"],
                  "dont":["Use elevators","Stand near heavy objects"],
                  "places":["Shelter","Hospital"]},
    "Theft":{"helpline":"100","icon":"👮",
             "do":["Move to safe place","Call police","Note suspect details"],
             "dont":["Confront suspects","Chase alone"],
             "places":["Police Station","Hospital"]}
}

# ----------------- Utilities -----------------
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
        account_sid = st.secrets.get("TWILIO_SID")
        auth_token = st.secrets.get("TWILIO_TOKEN")
        from_number = st.secrets.get("TWILIO_NUMBER")
        if not (account_sid and auth_token and from_number):
            st.warning("Twilio credentials not found in Streamlit secrets. Set TWILIO_SID, TWILIO_TOKEN, TWILIO_NUMBER in secrets.")
            return
        client = Client(account_sid, auth_token)
        message_body = f"ALERT! {emergency_type} reported in {city}. Location: https://www.google.com/maps/search/?api=1&query={lat},{lon}. Instructions: {', '.join(instructions)}"
        for num in contacts:
            client.messages.create(body=message_body, from_=from_number, to=num)
        st.success("Emergency SMS sent.")
    except Exception as e:
        st.error(f"Failed to send SMS: {e}")

# ----------------- Synthetic Data Creation -----------------
def create_synthetic_dataset(path=CSV_FILE, n=2000, random_state=42):
    """
    Creates a synthetic emergency dataset and saves to CSV.
    Columns: city, time_of_day, day_of_week, weather, temp, population_density, emergency_type, severity
    severity in {Low, Medium, High, Critical}
    """
    random.seed(random_state)
    np.random.seed(random_state)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    cities = list(CITY_COORDS.keys())
    times = ["Morning", "Afternoon", "Evening", "Night"]
    days = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    weathers = ["Clear","Rainy","Cloudy","Stormy","Foggy","Hot"]
    types = list(EMERGENCY_DB.keys())

    rows = []
    for _ in range(n):
        city = random.choice(cities)
        time_of_day = random.choices(times, weights=[30,30,25,15])[0]
        day_of_week = random.choice(days)
        weather = random.choices(weathers, weights=[40,20,20,10,5,5])[0]
        temp = int(np.clip(np.random.normal(30,6), 10, 45))
        pop_density = int(np.clip(np.random.normal(5000 if city in ["Delhi","Mumbai","Kolkata"] else 3000, 1500), 500, 20000))
        emergency_type = random.choices(types, weights=[10,35,30,10,5,10])[0]  # Medical more frequent
        # determine severity based on simple heuristics + randomness
        severity_score = 0
        if emergency_type in ["Accident","Fire"]: severity_score += 2
        if weather in ["Stormy","Rainy","Foggy"]: severity_score += 1
        if time_of_day == "Night": severity_score += 1
        severity_score += 0 if pop_density < 2000 else 1
        # noisy mapping to labels
        if severity_score <= 1:
            severity = random.choices(["Low","Medium"], weights=[70,30])[0]
        elif severity_score == 2:
            severity = random.choices(["Medium","High"], weights=[60,40])[0]
        else:
            severity = random.choices(["High","Critical"], weights=[70,30])[0]
        rows.append([city, time_of_day, day_of_week, weather, temp, pop_density, emergency_type, severity])

    df = pd.DataFrame(rows, columns=["city","time_of_day","day_of_week","weather","temp","population_density","emergency_type","severity"])
    df.to_csv(path, index=False)
    return df

# Create dataset if not exists
if not os.path.exists(CSV_FILE):
    st.info("Creating synthetic dataset for the first run...")
    df = create_synthetic_dataset()
else:
    df = pd.read_csv(CSV_FILE)

# ----------------- Data Science: Training -----------------
@st.cache_resource(show_spinner=False)
def train_model(df):
    # Basic preprocessing
    working = df.copy()
    # Encode labels
    le_sev = LabelEncoder()
    y = le_sev.fit_transform(working["severity"])
    X = working[["city","time_of_day","day_of_week","weather","temp","population_density","emergency_type"]].copy()
    # One-hot encode categorical features
    X = pd.get_dummies(X, drop_first=True)
    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    model = RandomForestClassifier(n_estimators=200, random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    report = classification_report(y_test, y_pred, output_dict=True)
    cm = confusion_matrix(y_test, y_pred)
    return {
        "model": model,
        "le_sev": le_sev,
        "features": X.columns.tolist(),
        "X_test": X_test,
        "y_test": y_test,
        "y_pred": y_pred,
        "report": report,
        "confusion_matrix": cm
    }

ds = train_model(df)

# ----------------- Header -----------------
st.markdown(f'<div class="header"><h2>🚨 Smart Emergency & Safety Assistant</h2>'
            f'<div class="small-muted">Real-time Help • {", ".join([em["icon"] for em in EMERGENCY_DB.values()])}</div></div>', unsafe_allow_html=True)

# ----------------- Sidebar Controls -----------------
with st.sidebar:
    st.header("Emergency Controls")
    city = st.selectbox("City", list(CITY_COORDS.keys()))
    lang = st.selectbox("Voice Language", ["English","Hindi"])
    emergency_type = st.radio("Emergency Type", list(EMERGENCY_DB.keys()))
    severity_manual = st.radio("Severity (manual)", ["Low","Medium","High","Critical"])
    st.markdown("## Nearby Facilities Filter")
    selected_places = st.multiselect("Select facility types", ["Hospital","Clinic","Police Station","Fire Station","Pharmacy","Shelter"], default=["Hospital","Clinic","Police Station"])
    st.markdown("## Emergency SMS")
    contacts_input = st.text_area("Enter phone numbers (comma separated)", "+919876543210")
    if st.button("📩 Send Emergency SMS"):
        if contacts_input:
            contacts = [c.strip() for c in contacts_input.split(",")]
            send_emergency_sms(contacts, city, CITY_COORDS[city][0], CITY_COORDS[city][1], emergency_type, EMERGENCY_DB[emergency_type]['do'])
        else:
            st.warning("Please enter at least one phone number.")
    if st.button("🔴 PANIC ALERT"):
        st.warning("Panic Activated! Call local emergency services immediately.")
    if st.button("🚑 Book Ambulance (ETA 10min)"):
        st.success("Ambulance booked! ETA: 10 minutes.")

# ----------------- Main layout -----------------
left, right = st.columns([2,1])

with left:
    # Animated TO DO / NOT TO DO
    db = EMERGENCY_DB[emergency_type]
    st.markdown(f"### {db['icon']} {emergency_type} Emergency | Helpline: {db['helpline']}")
    with st.expander("✔️ What TO DO / ✖️ What NOT TO DO"):
        for d in db["do"]:
            st.markdown(f"✅ {d}")
            time.sleep(0.05)
        for d in db["dont"]:
            st.markdown(f"❌ {d}")
            time.sleep(0.05)

    # Map
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

    # Voice Guidance
    advice = f"{emergency_type} emergency. Call {db['helpline']}. " + " ".join(db['do'])
    col1, col2 = st.columns(2)
    if col1.button("▶️ Play Guidance"):
        audio_bytes = make_tts(advice, lang="hi" if lang=="Hindi" else "en")
        st.audio(audio_bytes, format="audio/mp3")
    if col2.button("⬇️ Download MP3"):
        audio_bytes = make_tts(advice, lang="hi" if lang=="Hindi" else "en")
        st.download_button(label="Download MP3", data=audio_bytes, file_name=f"{emergency_type}_guidance.mp3", mime="audio/mp3")

    st.markdown("---")
    st.markdown("### 🧠 Predict Emergency Severity (Model Powered)")
    # Prediction Inputs
    pred_city = st.selectbox("Prediction: City", df['city'].unique(), index=list(df['city'].unique()).tolist().index(city))
    pred_time = st.selectbox("Prediction: Time of Day", ["Morning","Afternoon","Evening","Night"])
    pred_day = st.selectbox("Prediction: Day of Week", ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"])
    pred_weather = st.selectbox("Prediction: Weather", ["Clear","Rainy","Cloudy","Stormy","Foggy","Hot"])
    pred_temp = st.slider("Prediction: Temperature (°C)", 5, 45, 30)
    pred_pop = st.number_input("Prediction: Population density (people/km²)", min_value=100, max_value=50000, value=3000, step=100)
    pred_type = st.selectbox("Prediction: Emergency Type", list(EMERGENCY_DB.keys()))

    if st.button("Predict Severity"):
        # Build input row like training
        input_df = pd.DataFrame([{
            "city": pred_city,
            "time_of_day": pred_time,
            "day_of_week": pred_day,
            "weather": pred_weather,
            "temp": pred_temp,
            "population_density": pred_pop,
            "emergency_type": pred_type
        }])
        # One-hot encode like training
        input_enc = pd.get_dummies(input_df)
        # Reindex to training features
        input_enc = input_enc.reindex(columns=ds["features"], fill_value=0)
        pred_idx = ds["model"].predict(input_enc)[0]
        pred_label = ds["le_sev"].inverse_transform([pred_idx])[0]
        st.success(f"Predicted Emergency Severity: **{pred_label}**")

        # Auto-alert if high or critical
        if pred_label in ["High","Critical"]:
            st.error("⚠️ High-Risk Situation Predicted! Consider sending alerts to contacts.")
            if contacts_input:
                if st.button("Send Alert SMS (Predicted High)"):
                    contacts = [c.strip() for c in contacts_input.split(",")]
                    send_emergency_sms(contacts, pred_city, CITY_COORDS[pred_city][0], CITY_COORDS[pred_city][1], pred_type, EMERGENCY_DB[pred_type]['do'])
            # Play voice immediate guidance
            tts_bytes = make_tts(f"Warning. {pred_label} risk predicted. Follow safety instructions.", lang="hi" if lang=="Hindi" else "en")
            st.audio(tts_bytes, format="audio/mp3")

with right:
    st.markdown("### 📈 Analytics Dashboard")
    st.info("Dataset summary (synthetic). You can replace data/emergency_data.csv with a real dataset.")
    st.write(df.describe(include='all'))
    # Plot: emergency type counts
    st.markdown("#### Emergencies by Type")
    type_counts = df['emergency_type'].value_counts()
    st.bar_chart(type_counts)

    # Plot: severity distribution
    st.markdown("#### Severity Distribution")
    sev_counts = df['severity'].value_counts()
    st.bar_chart(sev_counts)

    # Confusion matrix and classification report
    st.markdown("#### Model Evaluation")
    report_df = pd.DataFrame(ds["report"]).T
    st.dataframe(report_df[['precision','recall','f1-score','support']].round(3))

    st.markdown("Confusion Matrix")
    cm = ds["confusion_matrix"]
    fig, ax = plt.subplots(figsize=(5,4))
    labels = ds["le_sev"].inverse_transform(np.arange(len(ds["le_sev"].classes_)))
    sns.heatmap(cm, annot=True, fmt='d', xticklabels=labels, yticklabels=labels, cmap='Blues', ax=ax)
    ax.set_xlabel("Predicted")
    ax.set_ylabel("True")
    st.pyplot(fig)

    st.markdown("#### Feature Importances (Top 15)")
    importances = ds["model"].feature_importances_
    feat_imp = pd.Series(importances, index=ds["features"]).sort_values(ascending=False).head(15)
    st.bar_chart(feat_imp)

st.markdown("---")
st.markdown("### 🚖 Quick Transport / Emergency Contacts")
c1,c2,c3=st.columns(3)
c1.markdown(f"[🚕 Book Ola](https://www.olacabs.com/)")
c2.markdown(f"[🚗 Book Uber](https://www.uber.com/in/en/)")
c3.markdown(f"☎️ Ambulance: {EMERGENCY_DB[emergency_type]['helpline']}")

st.markdown("---")
st.markdown("Made with ❤️ • Always update local helplines • For Twilio SMS set secrets in Streamlit")
st.markdown("**How to set Twilio secrets:** in terminal run `streamlit secrets set TWILIO_SID='<sid>'` and similarly for TWILIO_TOKEN and TWILIO_NUMBER, or use the secrets.toml file.")
