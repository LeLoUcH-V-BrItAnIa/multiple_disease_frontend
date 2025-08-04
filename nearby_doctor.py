import requests
import folium
from streamlit_folium import st_folium
import streamlit as st

def geocode_location(location_name):
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": location_name, "format": "json"}
    headers = {"User-Agent": "CareIQ-App"}

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        try:
            data = response.json()
            if data:
                return float(data[0]["lat"]), float(data[0]["lon"])
            else:
                return None, None
        except requests.exceptions.JSONDecodeError:
            return None, None
    except Exception:
        return None, None


def get_doctors(lat, lon, radius, specialty=""):
    query = f"""
    [out:json];
    (
      node["amenity"="doctors"](around:{radius},{lat},{lon});
      node["healthcare"="doctor"](around:{radius},{lat},{lon});
      node["amenity"="clinic"](around:{radius},{lat},{lon});
      node["amenity"="hospital"](around:{radius},{lat},{lon});
    );
    out center;
    """
    url = "https://overpass-api.de/api/interpreter"

    try:
        response = requests.get(url, params={"data": query}, timeout=20)
        data = response.json()
        doctors = []
        for element in data["elements"]:
            name = element.get("tags", {}).get("name", "Unknown")
            if specialty.lower() in name.lower() or specialty == "":
                doctors.append({"name": name, "lat": element["lat"], "lon": element["lon"]})
        return doctors
    except Exception as e:
        st.error("🛑 Failed to fetch doctor data.")
        return []


def show_nearby_doctors():
    st.title("🗺️ Find Nearby Doctors")
    st.write("Enter your city/town and search for doctors, clinics, and hospitals near you.")

    location_name = st.text_input("📍 Enter Location (e.g. Kolkata, New York):", "Kolkata")
    specialty = st.text_input("🩺 Doctor Specialty (e.g. diabetes, cardiologist, pediatrician):", "")
    radius = st.slider("Search Radius (meters)", 500, 5000, 2000, step=500)

    if st.button("🔍 Search Doctors"):
        lat, lon = geocode_location(location_name)
        if lat is None or lon is None:
            st.error("⚠️ Could not find that location. Try a more specific name.")
            return

        doctors = get_doctors(lat, lon, radius, specialty)
        st.session_state.doctors = doctors
        st.session_state.lat = lat
        st.session_state.lon = lon

        if not doctors:
            st.warning("❌ No doctors or clinics found. Try increasing the radius or changing the specialty.")
        else:
            st.success(f"✅ Found {len(doctors)} doctors/clinics near **{location_name}**!")

    if "doctors" in st.session_state and st.session_state.doctors:
        doctors = st.session_state.doctors
        lat = st.session_state.lat
        lon = st.session_state.lon

        m = folium.Map(location=[lat, lon], zoom_start=13)
        folium.Marker([lat, lon], tooltip=f"📍 {location_name}", icon=folium.Icon(color="red")).add_to(m)

        for d in doctors:
            folium.Marker(
                [d["lat"], d["lon"]],
                tooltip=d["name"],
                icon=folium.Icon(color="blue", icon="plus-sign")
            ).add_to(m)

        st_folium(m, width=700, height=500)

        st.markdown("### 🏥 Nearby Doctors & Clinics")
        for d in doctors:
            st.write(f"**{d['name']}** — 📍 ({d['lat']}, {d['lon']})")
    else:
        st.info("Enter a location and click 'Search Doctors' to view nearby results.")
