def show_nearby_doctors():
    st.title("🗺️ Find Nearby Doctors")
    st.write("Enter your city/town and search for doctors, clinics, and hospitals near you.")

    location_name = st.text_input("📍 Enter Location (e.g. Kolkata, New York):", "Kolkata")
    specialty = st.text_input("🩺 Doctor Specialty (e.g. diabetes, cardiologist, pediatrician):", "")
    radius = st.slider("Search Radius (meters)", 500, 5000, 2000, step=500)

    lat, lon = geocode_location(location_name)
    if lat is None:
        st.error("⚠️ Could not find that location. Try a more specific name.")
        return

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
                doctors.append({"name": name, "lat": element["lat"], "lon": element["lon"]})
        return doctors

    if st.button("🔍 Search Doctors"):
        doctors = get_doctors(lat, lon, radius, specialty)
        st.session_state.doctors = doctors

    if "doctors" in st.session_state and st.session_state.doctors:
        doctors = st.session_state.doctors
        st.success(f"✅ Found {len(doctors)} doctors/clinics near **{location_name}**!")

        m = folium.Map(location=[lat, lon], zoom_start=13)
        folium.Marker([lat, lon], tooltip=f"📍 {location_name}", icon=folium.Icon(color="red")).add_to(m)

        for d in doctors:
            folium.Marker(
                [d["lat"], d["lon"]],
                tooltip=d["name"],
                icon=folium.Icon(color="blue", icon="plus-sign")
            ).add_to(m)

        st_folium(m, width=700, height=500)

        st.markdown("### 🏥 Nearby Doctors")
        for d in doctors:
            st.write(f"**{d['name']}** - 📍 ({d['lat']}, {d['lon']})")
    else:
        st.info("Enter a location and click Search Doctors to view nearby results.")