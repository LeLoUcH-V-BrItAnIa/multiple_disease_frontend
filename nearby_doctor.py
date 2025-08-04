import streamlit as st
import requests
import folium
from streamlit_folium import st_folium

# Geocode function
def geocode_location(location_name):
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": location_name, "format": "json"}
    headers = {"User-Agent": "CareIQ-App"}  # Required
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data:
                return float(data[0]["lat"]), float(data[0]["lon"])
            else:
                return None, None
        else:
            st.error(f"🌐 API Error: {response.status_code}")
            return None, None
    except Exception as e:
        st.error(f"⚠️ Location lookup failed: {e}")
        return None, None

# Doctor data fetching
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
    response = requests.get(url, params={"data": query})
    data = response.json()
    doctors = []
    for element in data.get("elements", []):
        name = element.get("tags", {}).get("name", "Unknown")
        if specialty.lower() in name.lower() or specialty == "":
            doctors.append({
                "name": name,
                "lat": element.get("lat"),
                "lon": element.get("lon")
            })
    return doctors

# Streamlit App UI
def show_nearby_doctors():
    st.title("🗺️ Find Nearby Doctors")
    st.write("Enter your city/town and search for doctors, clinics, and hospitals near you.")

    location_name = st.text_input("📍 Enter Location (e.g. Kolkata, New York):", "Kolkata")
    specialty = st.text_input("🩺 Doctor Specialty (optional):", "")
    radius = st.slider("Search Radius (meters)", 500, 5000, 2000, step=500)

    lat, lon = geocode_location(location_name)
    if lat is None:
        st.warning("⚠️ Could not find that location. Try a more specific name.")
        return

    if st.button("🔍 Find Doctors"):
        doctors = get_doctors(lat, lon, radius, specialty)
        st.session_state["doctors"] = doctors
    else:
        doctors = st.session_state.get("doctors", [])

    if doctors:
        st.success(f"✅ Found {len(doctors)} results near **{location_name}**.")

        # Safe folium map
        m = folium.Map(location=[lat, lon], zoom_start=13)
        folium.Marker([lat, lon], tooltip=f"📍 {location_name}", icon=folium.Icon(color="red")).add_to(m)

        for d in doctors:
            folium.Marker(
                [d["lat"], d["lon"]],
                tooltip=d["name"],
                icon=folium.Icon(color="blue", icon="plus-sign")
            ).add_to(m)

        st_folium(m, width=700, height=500)

        # Doctor list
        st.markdown("### 🏥 Nearby Doctors/Clinics")
        for d in doctors:
            st.write(f"**{d['name']}** — 📍 ({d['lat']:.4f}, {d['lon']:.4f})")
    else:
        st.info("Enter a location and click Find Doctors to view nearby results.")

# Run app
if __name__ == "__main__":
    show_nearby_doctors()