import streamlit as st
import requests
import pandas as pd
from geopy.distance import geodesic

# -------------------------------
# Get user location (manual input)
# -------------------------------
def get_location():

    lat = st.number_input("Latitude", value=22.57)   # Default Kolkata
    lon = st.number_input("Longitude", value=88.36)
    

    return lat, lon


# -------------------------------
# Fetch doctors from OSM (Overpass API)
# -------------------------------
def fetch_doctors(lat, lon, radius=3000, specialist="All"):
    url = "https://overpass.kumi.systems/api/interpreter"

    query = f"""
    [out:json];
    (
      node["amenity"="hospital"](around:{radius},{lat},{lon});
      node["amenity"="clinic"](around:{radius},{lat},{lon});
      node["amenity"="doctors"](around:{radius},{lat},{lon});
    );
    out;
    """
    for _ in range(2):
        try:
            response = requests.get(url, params={'data': query}, timeout=10)

            if response.status_code != 200:
                st.error("❌ Overpass API error. Try again later.")
                return pd.DataFrame()

            data = response.json()

        except requests.exceptions.Timeout:
            st.error("⏳ Request timed out. Try again.")
            return pd.DataFrame()

        except Exception as e:
            st.error(f"⚠️ Unexpected error: {str(e)}")
            return pd.DataFrame()
    

    doctors = []

    for element in data['elements']:
        tags = element.get('tags', {})
        name = tags.get('name', 'Unknown').lower()

        lat_d = element['lat']
        lon_d = element['lon']

        distance = geodesic((lat, lon), (lat_d, lon_d)).km

        doctors.append({
            "Name": name.title(),
            "Latitude": lat_d,
            "Longitude": lon_d,
            "Distance (km)": round(distance, 2),
            "Tags": str(tags).lower()
        })

    df = pd.DataFrame(doctors)

    # -------------------------------
    # 🔍 FILTER LOGIC
    # -------------------------------
    if specialist != "All" and not df.empty:

        keywords = {
            "Cardiologist ❤️": ["cardio", "heart"],
            "Diabetologist 🩸": ["diabetes", "endocrine"],
            "Neurologist 🧠": ["neuro", "brain"],
            "General Physician 🏥": ["clinic", "doctor", "general"]
        }

        selected_keywords = keywords.get(specialist, [])

        df = df[
            df["Name"].str.contains('|'.join(selected_keywords)) |
            df["Tags"].str.contains('|'.join(selected_keywords))
        ]

    return df


# -------------------------------
# MAIN FUNCTION
# -------------------------------
def show_nearby_doctors():
    lat, lon = get_location()
    specialist = st.selectbox("🧠 Select Specialist", [
        "All",
        "Cardiologist ❤️",
        "Diabetologist 🩸",
        "Neurologist 🧠",
        "General Physician 🏥"
    ])

    if st.button("🔍 Find Doctors"):
        with st.spinner("Fetching nearby doctors..."):
            df = fetch_doctors(lat, lon, specialist=specialist)

        if df.empty:
            st.warning("No doctors found nearby.")
            return

        # Sort by distance
        df = df.sort_values(by="Distance (km)")

        # -------------------------------
        # 📊 Map View
        # -------------------------------
        st.subheader("🗺 Map View")
        st.map(df.rename(columns={"Latitude": "lat", "Longitude": "lon"}))

        # -------------------------------
        # 📋 List View
        # -------------------------------
        st.subheader("📋 Doctor List")

        for _, row in df.iterrows():
            st.markdown(f"""
            <div style="
                background: rgba(255,255,255,0.08);
                padding: 15px;
                border-radius: 12px;
                margin-bottom: 10px;
            ">
            <b>🏥 {row['Name']}</b><br>
            📏 Distance: {row['Distance (km)']} km
            </div>
            """, unsafe_allow_html=True)