import pandas as pd
import numpy as np
from nearby_doctor import show_nearby_doctors
import matplotlib.pyplot as plt
import os
import pickle
import streamlit as st
from streamlit_lottie import st_lottie
from streamlit_option_menu import option_menu
import requests
from get_remedies import get_remedies
import google.generativeai as genai
from dotenv import load_dotenv
from pymongo import MongoClient
import bcrypt
import re
from dotenv import load_dotenv
from db_utils import get_user_records,save_prediction
import shap
# ---------------- Environment & MongoDB Setup ----------------
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI") #st.secrets["MONGO_URI"]  Fix It  
try:
    client = MongoClient(MONGO_URI)
    client.admin.command('ping')
except Exception as e:
    st.error("MongoDB connection failed. Check your URI!")

db = client["pulse_db"]
users_collection = db["users"]
# ---------------- Session State ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "page" not in st.session_state:
    st.session_state.page = "login"  # default page

# ---------------- Auth Functions ----------------
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def is_valid_password(password):
    pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*])[A-Za-z\d!@#$%^&*]{8,}$'
    return re.match(pattern, password) is not None

def register_user(username, email, password):
    if users_collection.find_one({"username": username}):
        return False, "Username already exists!"
    if not is_valid_email(email):
        return False, "Invalid email format!"
    if not is_valid_password(password):
        return False, "Password must be at least 8 characters long, include uppercase, lowercase, number, and special character!"
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    users_collection.insert_one({"username": username, "email": email, "password": hashed_pw})
    return True, "User registered successfully!"

def login_user(username, password):
    user = users_collection.find_one({"username": username})
    if user and bcrypt.checkpw(password.encode('utf-8'), user["password"]):
        return True, user
    return False, None

def show_login_register_page():
    st.set_page_config(page_title="Pulse Auth", layout="wide", page_icon="🩺")
    
    # Gradient background and form styling
    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(-45deg, #0D1B2A, #1B263B, #415A77, #0A1128);
        background-size: 500% 500%;
        animation: gradientBG 12s ease infinite;
        color:white;
    }
    @keyframes gradientBG {
        0% {background-position:0% 50%;}
        50% {background-position:100% 50%;}
        100% {background-position:0% 50%;}
    }
    .form-box {
        background: rgba(255,255,255,0.1); 
        padding:30px; 
        border-radius:15px; 
        box-shadow:0 8px 25px rgba(0,0,0,0.5);
    }
    input {padding:10px; margin:5px 0; width:100%; border-radius:5px; border:none;}
    button {padding:10px; width:100%; border-radius:5px; border:none; background:#00FFAA; color:black; font-weight:bold; cursor:pointer;}
    button:hover {background:#00cc88;}
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 style='text-align:center; font-size:3rem;'>PULSE 🩺<br>Predictive Understanding for Lifestyle & Smart Evaluation</h1>", unsafe_allow_html=True)

    # Lottie animation
    def load_lottie(url):
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    
    animation_url = "https://assets9.lottiefiles.com/packages/lf20_qp1q7mct.json"
    lottie_anim = load_lottie(animation_url)
    st_lottie(lottie_anim, height=250)

    # Login/Register form
    with st.sidebar:
        selected = option_menu(
        'PULSE HUB 🧠',
        ['Login','Register'],
        menu_icon='hospital-fill',
        icons=['activity', 'heart'],
        default_index=0
    )
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("auth_form"):
            if selected == "Register":
                st.subheader("📝 Register")
                reg_username = st.text_input("Username", key="reg_user")
                reg_email = st.text_input("Email", key="reg_email")
                reg_password = st.text_input("Password", type="password", key="reg_pass")
                reg_confirm = st.text_input("Confirm Password", type="password", key="reg_confirm")
                submit = st.form_submit_button("Register")
                if submit:
                    if reg_username and reg_email and reg_password and reg_confirm:
                        if reg_password != reg_confirm:
                            st.error("❌ Passwords do not match")
                        else:
                            success, msg = register_user(reg_username, reg_email, reg_password)
                            if success:
                                st.success(msg + " You can now login.")
                            else:
                                st.error(msg)
                    else:
                        st.warning("Please fill all fields")
                
            else:
                st.subheader("🔑 Login")
                username = st.text_input("Username", key="login_user")
                password = st.text_input("Password", type="password", key="login_pass")
                submit = st.form_submit_button("Login")
                if submit:
                    if username and password:
                        success, user = login_user(username, password)
                        if success:
                            st.session_state.logged_in = True
                            st.session_state.username = username
                            st.session_state.page = "home"
                            st.rerun()
                        else:
                            st.error("❌ Invalid username or password")
                    else:
                        st.warning("Enter both username and password")
# ---------------- Router ----------------
if not st.session_state.logged_in:
    show_login_register_page()
    st.stop()  # Prevent rest of the code from running

if "page" not in st.session_state:
    st.session_state.page = "home"
if "prediction_log" not in st.session_state:
    st.session_state["prediction_log"] = []
# Set page configuration
st.set_page_config(page_title="Health Assistant",
                   layout="wide",
                   page_icon="🧑‍⚕️")
st.markdown("""
    <style>
    
    /* Full-page gradient background */
                
    .stApp {
        background: linear-gradient(-45deg, #0D1B2A, #1B263B, #415A77, #0A1128);
        background-size: 500% 500%;
        animation: gradientBG 12s ease infinite;
        color: white !important;
    }
    /* Animate the gradient */
    @keyframes gradientBG {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }
    .fade-title {
    font-size: 2.2em;
    font-weight: bold;
    color: white;
    text-align: left;
    animation: fadeIn 1.2s ease-in-out;
    text-shadow: 2px 2px 8px rgba(0,0,0,0.4);
    }
    @keyframes fadeIn {
    0% { opacity: 0; transform: translateY(-10px); }
    100% { opacity: 1; transform: translateY(0); }
    }
""", unsafe_allow_html=True)

# Get current working directory
working_dir = os.path.dirname(os.path.abspath(__file__))

# Load models
diabetes_model_new = pickle.load(open(f'{working_dir}/saved_models/diabetes_model_new.sav', 'rb'))
diabetes_model = pickle.load(open(f'{working_dir}/saved_models/diabetes_model.sav', 'rb'))
heart_disease_model = pickle.load(open(f'{working_dir}/saved_models/heart_disease_model.sav', 'rb'))
parkinsons_model = pickle.load(open(f'{working_dir}/saved_models/parkinsons_model.sav', 'rb'))
leukemia_model = pickle.load(open(f'{working_dir}/saved_models/leukimia_model.sav', 'rb'))

# ✅ Homepage Section
if st.session_state.page == "home":
    import streamlit as st
    from streamlit_lottie import st_lottie
    import requests

    # 🔹 Function to load Lottie animation
    def load_lottie(url):
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()

    # 🔹 Load animations
    health_animation = load_lottie("https://assets9.lottiefiles.com/packages/lf20_qp1q7mct.json")
    diabetes_animation = load_lottie("https://assets10.lottiefiles.com/packages/lf20_1pxqjqps.json")
    heart_animation = load_lottie("https://assets9.lottiefiles.com/packages/lf20_ydo1amjm.json")
    parkinsons_animation = load_lottie("https://assets7.lottiefiles.com/packages/lf20_mjlh3hcy.json")
    # 🎨 CSS for animated gradient title
    st.markdown("""
    <style>
    
    /* Full-page gradient background */
                
    .stApp {
        background: linear-gradient(-45deg, #0D1B2A, #1B263B, #415A77, #0A1128);
        background-size: 500% 500%;
        animation: gradientBG 12s ease infinite;
        color: white !important;
    }

    /* Animate the gradient */
    @keyframes gradientBG {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }

    /* Make text readable */
    h1, h2, h3, h4, p, div {
        color: white !important;
    }
    .lottie-container {
        display: inline-block;
        border-radius: 25px;
        box-shadow: 0 6px 18px rgba(0,0,0,0.3);
        margin-bottom: 20px;
        overflow: hidden; /* Ensures rounded edges clip the animation */
    }
    /* Import a clean Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500&family=Quicksand:wght@400;500&family=Exo+2:wght@500&family=Nunito:wght@400&family=Audiowide&family=Karla:wght@400&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@600&family=Raleway:wght@500&display=swap');
    /* Common Card Styling */
        .disease-card {
            background: rgba(255,255,255,0.08);
            border-radius: 18px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 8px 25px rgba(0,0,0,0.35);
            backdrop-filter: blur(6px);
            margin: 15px;
            transition: transform 0.3s ease;
        }
        .disease-card:hover {
            transform: scale(1.04);
        }

        /* Diabetes Column */
        .diabetes-title {
            font-family: 'Orbitron', sans-serif;
            font-size: 1.8rem;
            color: #ff6b6b;
            text-shadow: 2px 2px 10px rgba(0,0,0,0.6);
        }
        .diabetes-text {
            font-family: 'Quicksand', sans-serif;
            font-size: 1rem;
            color: #fff;
            text-shadow: 1px 1px 6px rgba(0,0,0,0.5);
        }

        /* Heart Column */
        .heart-title {
            font-family: 'Exo 2', sans-serif;
            font-size: 1.8rem;
            color: #ff3d68;
            text-shadow: 2px 2px 10px rgba(0,0,0,0.6);
        }
        .heart-text {
            font-family: 'Nunito', sans-serif;
            font-size: 1rem;
            color: #fff;
            text-shadow: 1px 1px 6px rgba(0,0,0,0.5);
        }

        /* Parkinson's Column */
        .parkinsons-title {
            font-family: 'Audiowide', sans-serif;
            font-size: 1.8rem;
            color: #00f5d4;
            text-shadow: 2px 2px 10px rgba(0,0,0,0.6);
        }
        .parkinsons-text {
            font-family: 'Karla', sans-serif;
            font-size: 1rem;
            color: #fff;
            text-shadow: 1px 1px 6px rgba(0,0,0,0.5);
        }
    /* Title Styling */
    .homepage-title {
        font-family: 'Poppins', sans-serif;
        font-size: 3rem;
        text-align: center;
        color: #ffffff;
        text-shadow: 2px 2px 15px rgba(0,0,0,0.6);
        animation: fadeIn 2s ease-in-out;
    }
    @keyframes fadeIn {
            0% { opacity: 0; transform: translateY(30px); }
            100% { opacity: 1; transform: translateY(0); }
        }

        .fade-title {
            animation: fadeIn 1.2s ease-in-out forwards;
            opacity: 0;
            font-size: 2.5rem;
            color: #ffffff;
            text-shadow: 2px 2px 12px rgba(0,0,0,0.6);
            text-align: center;
        }

        .fade-subheading {
            animation: fadeIn 1.5s ease-in-out forwards;
            animation-delay: 0.6s;
            opacity: 0;
            font-size: 1.3rem;
            color: #f1f1f1;
            text-shadow: 1px 1px 8px rgba(0,0,0,0.6);
            text-align: center;
            margin-top: 10px;
        }
    </style>
""", unsafe_allow_html=True)

    # 🏥 Title 🏥 CareIQ: Predict Prevent Personalize 🧠
    st.markdown("<h1 style='text-align: center;background-size: 600% 600%;font-size: 50px;font-weight: 800;animation: fadeIn 1.5s ease-in-out forwards;animation-delay: 0.6s;opacity: 0;'>🏥 PULSE: Predict Prevent Personalize 🧠</h1>", unsafe_allow_html=True)
#     st.markdown("""
#     <h1 style="
#         background: linear-gradient(270deg, #FF4B4B, #4CAF50, #2196F3);
#         background-size: 600% 600%;
#         -webkit-background-clip: text;
#         -webkit-text-fill-color: transparent;
#         animation: gradientMove 8s ease infinite;
#         text-align: center;
#         font-size: 50px;
#         font-weight: 800;
#     ">
#         🏥 Multiple Disease Prediction System
#     </h1>

#     <style>
#     @keyframes gradientMove {
#         0% {background-position: 0% 50%;}
#         50% {background-position: 100% 50%;}
#         100% {background-position: 0% 50%;}
#     }
#     </style>
# """, unsafe_allow_html=True)

    st.markdown('<div class="fade-subheading">🧠An AI-powered health diagnostic and advisory system 🤖💊 that predicts Diabetes, Heart Disease, and Parkinson’s Disease and more based on clinical parameters.</div>',unsafe_allow_html=True)
    # Animation
    with st.container():
        st.markdown('<div class="lottie-container">', unsafe_allow_html=True)
        st_lottie(health_animation, height=250, key="health")
        st.markdown('</div>', unsafe_allow_html=True)

    # Project Overview
    # 🌟 Animated Project Overview Title
    st.markdown("""
    <h2 style='text-align:center; color:#00FFAA; animation: fadeIn 1s ease-in-out;'>
    🔬 Project Overview
    </h2>
    <p style='text-align:center; color:#f1f1f1; font-size:18px; animation: fadeInText 1.5s ease-in-out;'>
    This AI-powered health assistant can predict:<br>
    🩸 <b>Diabetes</b> | ❤️ <b>Heart Disease</b> | 🧠 <b>Parkinson’s Disease And More</b><br><br>
    It also provides <b>AI-powered diet & lifestyle recommendations</b>.
    </p>
    <style>
    @keyframes fadeIn {
        0% {opacity:0; transform: translateY(-20px);}
        100% {opacity:1; transform: translateY(0);}
    }
    @keyframes fadeInText {
        0% {opacity:0; transform: translateY(10px);}
        100% {opacity:1; transform: translateY(0);}
    }
    </style>
    """, unsafe_allow_html=True)

    # 🏗️ 3 Animated Columns Section
    col1, col2, col3 = st.columns(3)

    with col1:
        if diabetes_animation:
            st_lottie(diabetes_animation, height=200, key="diabetes")
        st.markdown("""
        <div style='animation: fadeInCard 1s ease-in-out; background: rgba(255,255,255,0.05); padding:10px; border-radius:12px;'>
        <h3 style='color:#FF6B6B;'>🩸 Diabetes</h3>
        <p style='color:#ddd;'>Detects diabetes using:<br>
        • Glucose levels<br>• BMI & Insulin<br>• Pregnancies count<br><br>
        Provides <b>AI-based diet & lifestyle suggestions</b>.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        if heart_animation:
            st_lottie(heart_animation, height=200, key="heart")
        st.markdown("""
        <div style='animation: fadeInCard 1.2s ease-in-out; background: rgba(255,255,255,0.05); padding:10px; border-radius:12px;'>
        <h3 style='color:#FF4B4B;'>❤️ Heart Disease</h3>
        <p style='color:#ddd;'>Predicts heart disease using:<br>
        • Cholesterol & BP<br>• ECG & Heart Rate<br>• Age, gender & chest pain type<br><br>
        Offers <b>personalized heart-health recommendations</b>.</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        if parkinsons_animation:
            st_lottie(parkinsons_animation, height=200, key="parkinsons")
        st.markdown("""
        <div style='animation: fadeInCard 1.4s ease-in-out; background: rgba(255,255,255,0.05); padding:10px; border-radius:12px;'>
        <h3 style='color:#4CAF50;'>🧠 Parkinson's</h3>
        <p style='color:#ddd;'>Analyzes voice patterns like:<br>
        • Jitter & Shimmer<br>• HNR & RPDE<br>• PPE & DFA metrics<br><br>
        Suggests <b>early interventions & exercises</b>.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # 🔹 Sample Health Insights Title
    st.markdown("""
    <h3 style='text-align:left; color:#FFD700; animation: fadeIn 1.2s ease-in-out; padding-top:50px;'>
    📈 Sample Health Data Insights
    </h3>
    """, unsafe_allow_html=True)

    # 🔹 Sample Diabetes Data (Pie Chart using matplotlib)
    diabetes_data = pd.DataFrame({
        "Result": ["Diabetic", "Non-Diabetic"],
        "Count": [45, 120]
    })
    fig1, ax1 = plt.subplots()
    ax1.pie(diabetes_data["Count"], labels=diabetes_data["Result"], autopct='%1.1f%%',
            startangle=90, colors=['#FF6B6B', '#6BCB77'])
    ax1.axis('equal')

    # 🔹 Sample Heart Disease Data (Bar Chart)
    heart_data = pd.DataFrame({
        "Feature": ["Age", "Cholesterol", "BP", "Max Heart Rate"],
        "Average": [52, 240, 130, 150]
    })

    # 🔹 Sample Parkinson's Data (Line Chart)
    parkinsons_data = pd.DataFrame({
        "Sample": list(range(1, 11)),
        "Fo": [120, 125, 123, 119, 122, 121, 124, 126, 125, 123]
    })

    # 🔹 Display in 3 columns
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("📊 Diabetes Distribution")
        st.pyplot(fig1)

    with col2:
        st.subheader("❤️ Heart Disease Data")
        st.bar_chart(heart_data.set_index("Feature"))

    with col3:
        st.subheader("🧠 Parkinson's Frequency Trend")
        st.line_chart(parkinsons_data.set_index("Sample"))

    st.info("💡 Use this Button to test predictions and explore features!")

    if st.button("🚀 Launch Health Assistant"):
        st.session_state.page = "app"  # ✅ Switch to main app
        st.rerun()

    # 🔻 Footer
    st.markdown("""
        <hr style="margin-top:40px;">
        <div style="text-align:center; font-size: 14px; color: #888;">
            <b>🧠 Multiple-Disease Diagnostic AI</b><br>
            Built with ❤️ using <span style="color:#FF4B4B;">Python</span>, <span style="color:#2196F3;">Streamlit</span>, 
            <span style="color:#4CAF50;">Scikit-Learn</span> & <span style="color:#FF9800;">Gemini AI</span><br>
            © 2025 Kaustav Mondal | For educational & research purposes only
        </div>
    """, unsafe_allow_html=True)
    
    st.stop()

# Sidebar
if st.session_state.page == "app":
    with st.sidebar:
        selected = option_menu(
        'PULSE Hub 🧠',
        ['Diabetes Prediction', 'Heart Disease Prediction','Leukimia Risk Prediction', 'Parkinsons Prediction', 'AI-Based Health Assistant','📊 Dashboard',
         'Nearby Doctors','AI Chat Assistant','About & Developer','My Records','Logout'],
        menu_icon='hospital-fill',
        icons=['activity', 'heart', 'person', 'robot','chat-dots-fill','geo-alt','info-circle'],
        default_index=0
    )
    if selected == "Logout":
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.page = "login"
        st.rerun()
# Database records page  
    if selected == "My Records":
        st.title("📋 My Health Reports")
        records = get_user_records(st.session_state.username)
        print(get_user_records(st.session_state.username))
        if records:
            for r in records:
                st.markdown(f"### 🧩 {r['disease']}")
                st.json(r)
        else:
            st.info("No records found yet.")
# AI-Based Health Assistant Page
    if selected == 'AI-Based Health Assistant':
        # st.title("🧠 AI-Based Health Assistant")
        st.markdown("""
        <style>
        .tip-card {
            background: rgba(255,255,255,0.08);
            border-radius: 12px;
            padding: 15px;
            margin-bottom: 12px;
            color: white;
            animation: fadeInUp 0.8s ease-in-out;
            backdrop-filter: blur(6px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        }
        .tip-title {
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 8px;
            text-shadow: 1px 1px 4px rgba(0,0,0,0.5);
        }
        @keyframes fadeInUp {
            0% {opacity: 0; transform: translateY(10px);}
            100% {opacity: 1; transform: translateY(0);}
        }
        .fade-title {
        font-size: 2.2em;
        font-weight: bold;
        padding-bottom: 20px;
        color: white;
        text-align: left;
        animation: fadeIn 1.2s ease-in-out;
        text-shadow: 2px 2px 8px rgba(0,0,0,0.4);
        }
        @keyframes fadeIn {
        0% { opacity: 0; transform: translateY(-10px); }
        100% { opacity: 1; transform: translateY(0); }
        }
        </style>
        """, unsafe_allow_html=True)
        st.markdown("<div class='fade-title'>🧠AI-Based Health Assistan</div>", unsafe_allow_html=True)
        st.markdown("Enter your basic health info and current symptoms:")

        mood = st.selectbox("Current Mood", ["Happy", "Tired", "Sad", "Stressed", "Calm"])
        age = st.text_input("Age")
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        symptoms = st.multiselect("Select Symptoms", [
            "Fatigue", "Headache", "Nausea", "Blurred Vision", "Frequent Urination",
            "Weight Loss", "Thirst", "Sweating", "Palpitations", "Body Pain"])
        
        if st.button("Get AI Health Recommendations"):
            if not symptoms or not age:
                st.warning("Please fill all required fields.")
            else:
                payload = {
                    "symptoms": symptoms,
                    "mood": mood,
                    "age": age,
                    "gender": gender
                }
                with st.spinner("Getting AI Suggestions ..."):
                    try:
                        res = requests.post("https://multiple-desease-backend.onrender.com/recommend", json=payload)
                        if res.status_code == 200:
                            result = res.json()
                            st.success("✅ Gemini AI Suggestions")
                            diet_tips = result.get("diet_tips", [])
                            lifestyle_tips = result.get("lifestyle_tips", [])
                            notes = result.get("notes", [])

                            st.markdown(f"""
                            <div class="tip-card">
                                <div class="tip-title">🍽 Diet Tips:</div>
                                <div>{'<br>'.join(diet_tips) if diet_tips else 'No tips available.'}</div>
                            </div>
                            <div class="tip-card">
                                <div class="tip-title">🏃 Lifestyle Tips:</div>
                                <div>{'<br>'.join(lifestyle_tips) if lifestyle_tips else 'No tips available.'}</div>
                            </div>
                            <div class="tip-card">
                                <div class="tip-title">💬 Notes:</div>
                                <div>{'<br>'.join(notes) if notes else 'No notes available.'}</div>
                            </div>
                            """, unsafe_allow_html=True)
                            # 🔹 Save prediction record for logged-in user
                            if st.session_state.logged_in:
                                record_data = {
                                    "symptoms": symptoms,
                                    "mood": mood,
                                    "age": age,
                                    "gender": gender
                                }
                                save_prediction(
                                    username=st.session_state.username,
                                    disease="General Health Recommendation",
                                    input_data=record_data,
                                    result="AI Suggestions Provided",
                                    ai_suggestions={
                                        "diet_tips": diet_tips,
                                        "lifestyle_tips": lifestyle_tips,
                                        "notes": notes
                                    }
                                )
                                st.info("✅ Your AI health recommendation has been saved to your history.")

                        else:
                            st.error("❌ Error from backend")
                            st.text(res.text)
                    except Exception as e:
                        st.error(f"❌ Request failed: {str(e)}")
                    
    # Leukimia Risk Prediction Page

    elif selected == 'Leukimia Risk Prediction':
        st.markdown("""
        <style>
        @keyframes fadeIn {
            0% { opacity: 0; transform: translateY(20px); }
            100% { opacity: 1; transform: translateY(0); }
        }

        @keyframes glowPulse {
            0% { box-shadow: 0 0 10px #FF4B4B, 0 0 20px #4CAF50, 0 0 30px #2196F3; }
            50% { box-shadow: 0 0 20px #FF4B4B, 0 0 30px #4CAF50, 0 0 40px #2196F3; }
            100% { box-shadow: 0 0 10px #FF4B4B, 0 0 20px #4CAF50, 0 0 30px #2196F3; }
        }

        .ai-card {
            background: rgba(0, 0, 0, 0.45);
            border-radius: 18px;
            padding: 22px;
            margin-top: 20px;
            color: #fff;
            animation: fadeIn 1s ease-in-out, glowPulse 3s infinite alternate;
            border: 2px solid rgba(255,255,255,0.2);
        }

        .ai-title {
            text-align: center;
            background: linear-gradient(270deg, #FF4B4B, #4CAF50, #2196F3);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 24px;
            font-weight: bold;
            text-shadow: 2px 2px 8px rgba(0,0,0,0.6);
        }

        .tip-title {
            font-size: 18px;
            color: #00FFEA;
            margin-top: 15px;
            font-weight: 600;
        }
        ul { margin-left: 20px; padding-left: 10px; list-style-type: disc; }

        ul li {
            opacity: 0;
            animation: fadeIn 0.6s forwards;
        }

        ul li:nth-child(1) { animation-delay: 0.3s; }
        ul li:nth-child(2) { animation-delay: 0.6s; }
        ul li:nth-child(3) { animation-delay: 0.9s; }
        ul li:nth-child(4) { animation-delay: 1.2s; }
        ul li:nth-child(5) { animation-delay: 1.5s; }
        </style>
    """, unsafe_allow_html=True)

        st.markdown("<div class='fade-title'>🧬 Leukemia Risk Prediction using ML</div>", unsafe_allow_html=True)

        # ---------- INPUT FIELDS ----------
        col1, col2, col3 = st.columns(3)

        with col1:
            age = st.number_input("Age", min_value=0, max_value=120, value=30)
            country = st.number_input("Country (numeric encoded)", min_value=0, value=1000)
            wbc = st.number_input("WBC Count", min_value=0, value=5000)
            rbc = st.number_input("RBC Count", min_value=0.0, value=5.0, step=0.01)
            platelet = st.number_input("Platelet Count", min_value=0, value=250000)
            hemoglobin = st.number_input("Hemoglobin Level", min_value=0.0, value=13.0, step=0.1)

        with col2:
            blast = st.number_input("Bone Marrow Blasts", min_value=0, value=50)
            bmi = st.number_input("BMI", min_value=0.0, value=22.0, step=0.1)
            ses = st.number_input("Socioeconomic Status", min_value=0, value=1)
            wbc_rbc_ratio = st.number_input("WBC/RBC Ratio", min_value=0.0, value=1000.0, step=0.1)
            bmi_con = st.number_input("BMI_con (encoded)", min_value=0, value=1)
            harmful = st.number_input("Harmful Habits", min_value=0, value=0)

        with col3:
            genetic_cond = st.number_input("Genetic Condition", min_value=0, value=0)
            eth_a = np.log1p(st.number_input("Ethnicity Group A", min_value=0, value=0))
            eth_b = np.log1p(st.number_input("Ethnicity Group B", min_value=0, value=0))
            eth_c = np.log1p(st.number_input("Ethnicity Group C", min_value=0, value=0))

        # Boolean features in two columns
        st.subheader("Additional Factors")
        colb1, colb2 = st.columns(2)
        with colb1:
            gender = 1 if st.checkbox("Gender Male") else 0
            genetic = np.log1p(1 if st.checkbox("Genetic Mutation Yes") else 0)
            family = 1 if st.checkbox("Family History Yes") else 0
            smoking = 1 if st.checkbox("Smoking Status Yes") else 0
            alcohol = 1 if st.checkbox("Alcohol Consumption Yes") else 0
        with colb2:
            radiation = np.log1p(1 if st.checkbox("Radiation Exposure Yes") else 0)
            infection = np.log1p(1 if st.checkbox("Infection History Yes") else 0)
            chronic = 1 if st.checkbox("Chronic Illness Yes") else 0
            immune = np.log1p(1 if st.checkbox("Immune Disorders Yes") else 0)
            urban = 1 if st.checkbox("Urban Area") else 0

        # Collect features in correct order
        leukemia_features = [[
            age, country, wbc, rbc, platelet, hemoglobin, blast, bmi, ses,
            eth_a, eth_b, eth_c, gender, genetic, family, smoking, alcohol,
            radiation, infection, chronic, immune, urban,
            wbc_rbc_ratio, bmi_con, harmful, genetic_cond
        ]]

        # ---------- PREDICTION & AI RECOMMENDATIONS ----------
        if st.button("Leukemia Test Result"):
            with st.spinner("Analyzing risk..."):
                leukemia_prediction = leukemia_model.predict(leukemia_features)[0]

            # Show prediction result
            if leukemia_prediction == 1 or leukemia_prediction == "True":
                diagnosis = "⚠️ High risk of Leukemia detected!"
                st.warning(diagnosis)
                st.session_state.prediction_log.append(("Leukemia", "High Risk"))
            else:
                diagnosis = "✅ Low risk of Leukemia"
                st.success(diagnosis)
                st.session_state.prediction_log.append(("Leukemia", "Low Risk"))
            
            user_data = {
                "Age": (age or 0),
                "WBC": (wbc or 0),
                "RBC": (rbc or 0),
                "Platelet": (platelet  or 0),
                "Hemoglobin": (hemoglobin  or 0),
                "Bone Marrow Blasts": (blast  or 0),
                "BMI": (bmi or 0),
                "Socioeconomic Status": (ses  or 0),
                "WBC/RBC Ratio": (wbc_rbc_ratio  or 0),
                "Harmful Habits": (harmful  or 0)
            }

            df = pd.DataFrame(list(user_data.items()), columns=['Feature', 'Value'])
            df = df.set_index('Feature')  # st.bar_chart needs an index

            st.subheader("📊 User Input Summary")
            st.bar_chart(df)

            # Prepare user inputs for AI suggestions
            user_inputs_dict_for_leukemia = {
                "Age": age,
                "WBC": wbc,
                "RBC": rbc,
                "Platelet": platelet,
                "Hemoglobin": hemoglobin,
                "Bone Marrow Blasts": blast,
                "BMI": bmi,
                "Socioeconomic Status": ses,
                "WBC/RBC Ratio": wbc_rbc_ratio,
                "Harmful Habits": harmful
            }

            # Call Gemini API for AI-based suggestions
            with st.spinner("Fetching AI health recommendations..."):
                ai_response = get_remedies(user_inputs_dict_for_leukemia, leukemia_prediction, disease="leukemia")

            # Format AI suggestions into animated HTML card
            diet_list = "".join([f"<li>{tip}</li>" for tip in ai_response.get("diet_tips", [])])
            lifestyle_list = "".join([f"<li>{tip}</li>" for tip in ai_response.get("lifestyle_tips", [])])
            notes_list = "".join([f"<li>{tip}</li>" for tip in ai_response.get("notes", [])])

            card_html = f"""
            <div class="ai-card">
                <div class="ai-title">💡 AI-Powered Health Suggestions</div>
                <div class="tip-title">🍽 Diet Tips:</div>
                <ul>{diet_list}</ul>
                <div class="tip-title">🏃 Lifestyle Tips:</div>
                <ul>{lifestyle_list}</ul>
                <div class="tip-title">🧘 Notes:</div>
                <ul>{notes_list}</ul>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
            # 🔹 Save prediction record for logged-in user
            if st.session_state.logged_in:
                record_data = user_inputs_dict_for_leukemia
                save_prediction(
                username=st.session_state.username,
                disease="Leukemia Risk Prediction",
                input_data=record_data,
                result=int(leukemia_prediction),
                ai_suggestions=ai_response
                )
                st.info("✅ Your AI health recommendation has been saved to your history.")





    # Diabetes Prediction Page
    elif selected == 'Diabetes Prediction':
        st.markdown("<div class='fade-title'>🩸Diabetes Prediction using ML</div>", unsafe_allow_html=True)
        st.markdown("""
            <style>
            @keyframes fadeIn {
                0% { opacity: 0; transform: translateY(20px); }
                100% { opacity: 1; transform: translateY(0); }
            }

            @keyframes glowPulse {
                0% { box-shadow: 0 0 10px #FF4B4B, 0 0 20px #4CAF50, 0 0 30px #2196F3; }
                50% { box-shadow: 0 0 20px #FF4B4B, 0 0 30px #4CAF50, 0 0 40px #2196F3; }
                100% { box-shadow: 0 0 10px #FF4B4B, 0 0 20px #4CAF50, 0 0 30px #2196F3; }
            }

            .ai-card {
                background: rgba(0, 0, 0, 0.45);
                border-radius: 18px;
                padding: 22px;
                margin-top: 20px;
                color: #fff;
                animation: fadeIn 1s ease-in-out, glowPulse 3s infinite alternate;
                border: 2px solid rgba(255,255,255,0.2);
            }

            .ai-title {
                text-align: center;
                background: linear-gradient(270deg, #FF4B4B, #4CAF50, #2196F3);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                font-size: 24px;
                font-weight: bold;
                text-shadow: 2px 2px 8px rgba(0,0,0,0.6);
            }

            .tip-title {
                font-size: 18px;
                color: #00FFEA;
                margin-top: 15px;
                font-weight: 600;
            }
            ul { margin-left: 20px; padding-left: 10px; list-style-type: disc; }

            ul li {
                opacity: 0;
                animation: fadeIn 0.6s forwards;
            }

            /* Staggered delay */
            ul li:nth-child(1) { animation-delay: 0.3s; }
            ul li:nth-child(2) { animation-delay: 0.6s; }
            ul li:nth-child(3) { animation-delay: 0.9s; }
            ul li:nth-child(4) { animation-delay: 1.2s; }
            ul li:nth-child(5) { animation-delay: 1.5s; }
            </style>
        """, unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            Pregnancies = st.text_input('Number of Pregnancies')
        with col2:
            Glucose = st.text_input('Glucose Level')
        with col3:
            BloodPressure = st.text_input('Blood Pressure value')
        with col1:
            SkinThickness = st.text_input('Skin Thickness value')
        with col2:
            Insulin = st.text_input('Insulin Level')
        with col3:
            BMI = st.text_input('BMI value')
        with col1:
            DiabetesPedigreeFunction = st.text_input('Diabetes Pedigree Function value')
        with col2:
            Age = st.text_input('Age of the Person')

        # Predict Button

        if st.button('Diabetes Test Result'):
            user_input_list = [Pregnancies, Glucose, BloodPressure, SkinThickness, Insulin,
                            BMI, DiabetesPedigreeFunction, Age]
            # Changing the values to float 
            user_input_list = [float(x) for x in user_input_list]
            # Prediction Code 
            diab_prediction = diabetes_model.predict([user_input_list])
            # Synthetic data 
            background_data = np.random.rand(50,8)
            # Shap explainer 
            explainer = shap.KernelExplainer(diabetes_model.decision_function, background_data)
            input_array = np.array([user_input_list])
            shap_values = explainer.shap_values(input_array)
            shap_values = shap_values[0]
            feature_names = [
                "Pregnancies", "Glucose", "BloodPressure", "SkinThickness",
                "Insulin", "BMI", "DiabetesPedigreeFunction", "Age"
            ]
            # print(shap_values)
            # Printed values 
            # [ 0.38705078  5.75635319 -1.03095822  0.00808619 -0.31521563  2.68560051
            #   0.24937503  0.3377738 ]
            shap_dict = {}
            for i in range(len(feature_names)):
                shap_dict[feature_names[i]] = shap_values[i]
            # print(shap_dict)
            # Sorting 
            sorted_features = sorted(shap_dict.items(), key=lambda x: abs(x[1]), reverse=True)
            top_features = sorted_features[:5]
            max_val = max(abs(v) for _, v in top_features)
            normalized = [(f, v, abs(v)/max_val) for f, v in top_features]

         
            if diab_prediction[0] == 0:
                diab_diagnosis = '✅ The person is not diabetic'
                st.success(diab_diagnosis)
                st.session_state.prediction_log.append(("Diabetes", "Non-Diabetic"))
            else:
                diab_diagnosis = "⚠️ The person is diabetic"
                st.warning(diab_diagnosis)
                st.session_state.prediction_log.append(("Diabetes", "Diabetic"))
            # Showing shap analyzed details
            st.markdown("""
                <div style="
                    background: rgba(0,0,0,0.4);
                    padding: 20px;
                    width = 100%;
                    border-radius: 15px;
                    box-shadow: 0 6px 20px rgba(0,0,0,0.3);
                ">
                <h3 style="color:#00FFAA;">🧠 AI Diagnosis Insight</h3>
                </div>
                """, unsafe_allow_html=True)

            for feature, value, norm in normalized:
                bar_length = int(norm * 20)  # max 20 blocks
                bar = "█" * bar_length

                if value > 0:
                    st.markdown(
                        f"<span style='color:#ff4b4b'><b>{feature}</b></span> "
                        f"{bar} +{round(value,2)} ↑",
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f"<span style='color:#4CAF50'><b>{feature}</b></span> "
                        f"{bar} {round(value,2)} ↓",
                        unsafe_allow_html=True
                    )
            top_feature = top_features[0][0]
            st.info(f"📌 Major contributing factor: **{top_feature}**")
            # Optional Graph
            st.subheader("📊 Feature Impact Visualization")
            import matplotlib.pyplot as plt
            plt.clf()
            shap.summary_plot(shap_values.reshape(1,-1), input_array, feature_names=feature_names, show=False)
            st.pyplot(plt.gcf())
            # User input summary plot --------------------------------------------------------------------------------------
            user_data = {
                "Pregnancies": float(Pregnancies or 0),
                "Glucose": float(Glucose or 0),
                "BloodPressure": float(BloodPressure or 0),
                "BMI": float(BMI or 0),
                "Age": float(Age or 0)
            }
            risk_limits = {
                "Glucose": 140,
                "BloodPressure": 80,
                "BMI": 30,
                "Age": 45
            }
            df = pd.DataFrame(list(user_data.items()), columns=['Feature', 'Value'])
            df = df.set_index('Feature')  # st.bar_chart needs an index
            # st.subheader("📊 User Input Summary")
            # st.bar_chart(df)
            # Your data
            df = pd.DataFrame(list(user_data.items()), columns=['Feature', 'Value'])
            # Risk limits (define once)
            risk_limits = {
                "Glucose": 140,
                "BloodPressure": 80,
                "BMI": 30,
                "Age": 45
            }
            # Prepare data
            features = df['Feature']
            user_values = df['Value']
            risk_values = [risk_limits.get(f, 0) for f in features]
            x = np.arange(len(features))
            width = 0.35
            st.subheader("📊 User vs Risk Comparison")
            plt.figure(figsize=(6,4))
            # Bars
            plt.bar(x - width/2, user_values, width, label='Your Value')
            plt.bar(x + width/2, risk_values, width, label='Risk Limit')

            # Labels
            plt.xticks(x, features, rotation=30)
            plt.ylabel("Value")
            plt.title("Health Parameter Comparison")
            plt.legend()
            st.pyplot(plt)
            # Ai API -----------------------------------------------------------------------------------------------------------------
            user_inputs_dict_for_diab = {
                "Pregnancies": Pregnancies,
                "Glucose": Glucose,
                "BloodPressure": BloodPressure,
                "SkinThickness": SkinThickness,
                "Insulin": Insulin,
                "BMI": BMI,
                "DiabetesPedigreeFunction": DiabetesPedigreeFunction,
                "Age": Age
            }
            with st.spinner("Fetching health suggestions..."):
                ai_response = get_remedies(user_inputs_dict_for_diab, diab_prediction[0],disease="diabetes")

            # Build the HTML content for the card
            diet_list = "".join([f"<li>{tip}</li>" for tip in ai_response.get("diet_tips", [])])
            lifestyle_list = "".join([f"<li>{tip}</li>" for tip in ai_response.get("lifestyle_tips", [])])
            notes_list = "".join([f"<li>{tip}</li>" for tip in ai_response.get("notes", [])])

            card_html = f"""
            <div class="ai-card">
                <div class="ai-title">💡 AI-Powered Health Suggestions</div>
                <div class="tip-title">🍽 Diet Tips:</div>
                <ul>{diet_list}</ul>
                <div class="tip-title">🏃 Lifestyle Tips:</div>
                <ul>{lifestyle_list}</ul>
                <div class="tip-title">🧘 Notes:</div>
                <ul>{notes_list}</ul>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
            # 🔹 Save prediction record for logged-in user
            if st.session_state.logged_in:
                record_data = user_inputs_dict_for_diab
                save_prediction(
                username=st.session_state.username,
                disease="Diabetes Prediction",
                input_data=record_data,
                result=int(diab_prediction[0]),
                ai_suggestions= ai_response
                )
                st.info("✅ Your AI health recommendation has been saved to your history.")

    
    

    # Heart Disease Prediction Page
    elif selected == 'Heart Disease Prediction':
        st.markdown("<div class='fade-title'>❤️Heart Disease Prediction using ML</div>", unsafe_allow_html=True)
        st.markdown("""
            <style>
            @keyframes fadeIn {
                0% { opacity: 0; transform: translateY(20px); }
                100% { opacity: 1; transform: translateY(0); }
            }

            @keyframes glowPulse {
                0% { box-shadow: 0 0 10px #FF4B4B, 0 0 20px #4CAF50, 0 0 30px #2196F3; }
                50% { box-shadow: 0 0 20px #FF4B4B, 0 0 30px #4CAF50, 0 0 40px #2196F3; }
                100% { box-shadow: 0 0 10px #FF4B4B, 0 0 20px #4CAF50, 0 0 30px #2196F3; }
            }

            .ai-card {
                background: rgba(0, 0, 0, 0.45);
                border-radius: 18px;
                padding: 22px;
                margin-top: 20px;
                color: #fff;
                animation: fadeIn 1s ease-in-out, glowPulse 3s infinite alternate;
                border: 2px solid rgba(255,255,255,0.2);
            }

            .ai-title {
                text-align: center;
                background: linear-gradient(270deg, #FF4B4B, #4CAF50, #2196F3);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                font-size: 24px;
                font-weight: bold;
                text-shadow: 2px 2px 8px rgba(0,0,0,0.6);
            }

            .tip-title {
                font-size: 18px;
                color: #00FFEA;
                margin-top: 15px;
                font-weight: 600;
            }
            ul { margin-left: 20px; padding-left: 10px; list-style-type: disc; }

            ul li {
                opacity: 0;
                animation: fadeIn 0.6s forwards;
            }

            /* Staggered delay */
            ul li:nth-child(1) { animation-delay: 0.3s; }
            ul li:nth-child(2) { animation-delay: 0.6s; }
            ul li:nth-child(3) { animation-delay: 0.9s; }
            ul li:nth-child(4) { animation-delay: 1.2s; }
            ul li:nth-child(5) { animation-delay: 1.5s; }
            </style>
        """, unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            age = st.text_input('Age')
        with col2:
            sex = st.text_input('Sex')
        with col3:
            cp = st.text_input('Chest Pain types')
        with col1:
            trestbps = st.text_input('Resting Blood Pressure')
        with col2:
            chol = st.text_input('Serum Cholestoral in mg/dl')
        with col3:
            fbs = st.text_input('Fasting Blood Sugar > 120 mg/dl')
        with col1:
            restecg = st.text_input('Resting Electrocardiographic results')
        with col2:
            thalach = st.text_input('Maximum Heart Rate achieved')
        with col3:
            exang = st.text_input('Exercise Induced Angina')
        with col1:
            oldpeak = st.text_input('ST depression induced by exercise')
        with col2:
            slope = st.text_input('Slope of the peak exercise ST segment')
        with col3:
            ca = st.text_input('Major vessels colored by flourosopy')
        with col1:
            thal = st.text_input('thal: 0 = normal; 1 = fixed defect; 2 = reversable defect')

        if st.button('Heart Disease Test Result'):
            user_input = [age, sex, cp, trestbps, chol, fbs, restecg, thalach,
                        exang, oldpeak, slope, ca, thal]
            user_input = [float(x) for x in user_input]

            heart_prediction = heart_disease_model.predict([user_input])

            if heart_prediction[0] == 1:
                st.warning('⚠️ The person is having heart disease')
                st.session_state.prediction_log.append(("Heart Disease", "Positive"))
            else:
                st.success('✅ The person does not have any heart disease')
                st.session_state.prediction_log.append(("Heart Disease", "Negative"))
             # ✅ Create summary chart
            heart_data = {
                "Age": float(age or 0),
                "Sex": float(sex or 0),
                "Chest Pain": float(cp or 0),
                "Cholesterol": float(chol or 0),
                "Max HR": float(thalach or 0),
                "Oldpeak": float(oldpeak or 0)
            }

            heart_df = pd.DataFrame(list(heart_data.items()), columns=['Feature', 'Value'])
            heart_df = heart_df.set_index('Feature')

            st.subheader("📊 Heart Disease Input Summary")
            st.bar_chart(heart_df)
            user_inputs_dict_for_heart = {
                        "age": age,
                        "sex": sex,
                        "cp": cp,
                        "trestbps": trestbps,
                        "chol": chol,
                        "fbs": fbs,
                        "restecg": restecg,
                        "thalach": thalach,
                        "exang": exang,
                        "oldpeak": oldpeak,
                        "slope": slope,
                        "ca": ca,
                        "thal": thal
            }

            with st.spinner("Fetching health suggestions..."):
                ai_response = get_remedies(user_inputs_dict_for_heart, heart_prediction[0],disease="heart")

                # ✅ Convert Heart AI suggestions into animated HTML lists
                heart_diet_list = "".join([f"<li>{tip}</li>" for tip in ai_response.get("diet_tips", [])])
                heart_lifestyle_list = "".join([f"<li>{tip}</li>" for tip in ai_response.get("lifestyle_tips", [])])
                # heart_notes_list = "".join([f"<li>{tip}</li>" for tip in ai_response.get("notes", [])])
                heart_notes_list = ai_response.get("notes", [])

                # ✅ Render animated card for Heart
                heart_card_html = f"""
                <div class="ai-card">
                    <div class="ai-title">💡 AI-Powered Heart Health Suggestions</div>
                    <div class="tip-title">🍽 Diet Tips:</div>
                    <ul>{heart_diet_list}</ul>
                    <div class="tip-title">🏃 Lifestyle Tips:</div>
                    <ul>{heart_lifestyle_list}</ul>
                    <div class="tip-title">🧘 Notes:</div>
                    <ul>{heart_notes_list}</ul>
                </div>
                """

                st.markdown(heart_card_html, unsafe_allow_html=True)
                # 🔹 Save prediction for logged-in user
                if st.session_state.logged_in:
                    save_prediction(
                        username=st.session_state.username,
                        disease="Heart Disease",
                        input_data=user_inputs_dict_for_heart,
                        result=int(heart_prediction[0]),
                        ai_suggestions=ai_response
                    )
                    st.info("✅ Your Heart Disease prediction and AI suggestions have been saved.")

                
    # nearby doctor's page'
    elif selected == "Nearby Doctors":
        show_nearby_doctors()


    # Parkinson's Disease Prediction Page
    elif selected == "Parkinsons Prediction":
        st.markdown("<div class='fade-title'>🧠Parkinson's Disease Prediction using ML</div>", unsafe_allow_html=True)
        st.markdown("""
            <style>
            @keyframes fadeIn {
                0% { opacity: 0; transform: translateY(20px); }
                100% { opacity: 1; transform: translateY(0); }
            }

            @keyframes glowPulse {
                0% { box-shadow: 0 0 10px #FF4B4B, 0 0 20px #4CAF50, 0 0 30px #2196F3; }
                50% { box-shadow: 0 0 20px #FF4B4B, 0 0 30px #4CAF50, 0 0 40px #2196F3; }
                100% { box-shadow: 0 0 10px #FF4B4B, 0 0 20px #4CAF50, 0 0 30px #2196F3; }
            }

            .ai-card {
                background: rgba(0, 0, 0, 0.45);
                border-radius: 18px;
                padding: 22px;
                margin-top: 20px;
                color: #fff;
                animation: fadeIn 1s ease-in-out, glowPulse 3s infinite alternate;
                border: 2px solid rgba(255,255,255,0.2);
            }

            .ai-title {
                text-align: center;
                background: linear-gradient(270deg, #FF4B4B, #4CAF50, #2196F3);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                font-size: 24px;
                font-weight: bold;
                text-shadow: 2px 2px 8px rgba(0,0,0,0.6);
            }

            .tip-title {
                font-size: 18px;
                color: #00FFEA;
                margin-top: 15px;
                font-weight: 600;
            }
            ul { margin-left: 20px; padding-left: 10px; list-style-type: disc; }

            ul li {
                opacity: 0;
                animation: fadeIn 0.6s forwards;
            }

            /* Staggered delay */
            ul li:nth-child(1) { animation-delay: 0.3s; }
            ul li:nth-child(2) { animation-delay: 0.6s; }
            ul li:nth-child(3) { animation-delay: 0.9s; }
            ul li:nth-child(4) { animation-delay: 1.2s; }
            ul li:nth-child(5) { animation-delay: 1.5s; }
            </style>
        """, unsafe_allow_html=True)

        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            fo = st.text_input('MDVP:Fo(Hz)')
        with col2:
            fhi = st.text_input('MDVP:Fhi(Hz)')
        with col3:
            flo = st.text_input('MDVP:Flo(Hz)')
        with col4:
            Jitter_percent = st.text_input('MDVP:Jitter(%)')
        with col5:
            Jitter_Abs = st.text_input('MDVP:Jitter(Abs)')
        with col1:
            RAP = st.text_input('MDVP:RAP')
        with col2:
            PPQ = st.text_input('MDVP:PPQ')
        with col3:
            DDP = st.text_input('Jitter:DDP')
        with col4:
            Shimmer = st.text_input('MDVP:Shimmer')
        with col5:
            Shimmer_dB = st.text_input('MDVP:Shimmer(dB)')
        with col1:
            APQ3 = st.text_input('Shimmer:APQ3')
        with col2:
            APQ5 = st.text_input('Shimmer:APQ5')
        with col3:
            APQ = st.text_input('MDVP:APQ')
        with col4:
            DDA = st.text_input('Shimmer:DDA')
        with col5:
            NHR = st.text_input('NHR')
        with col1:
            HNR = st.text_input('HNR')
        with col2:
            RPDE = st.text_input('RPDE')
        with col3:
            DFA = st.text_input('DFA')
        with col4:
            spread1 = st.text_input('spread1')
        with col5:
            spread2 = st.text_input('spread2')
        with col1:
            D2 = st.text_input('D2')
        with col2:
            PPE = st.text_input('PPE')

        if st.button("Parkinson's Test Result"):
            user_input = [fo, fhi, flo, Jitter_percent, Jitter_Abs, RAP, PPQ, DDP,
                        Shimmer, Shimmer_dB, APQ3, APQ5, APQ, DDA, NHR, HNR,
                        RPDE, DFA, spread1, spread2, D2, PPE]
            user_input = [float(x) for x in user_input]

            parkinsons_prediction = parkinsons_model.predict([user_input])

            if parkinsons_prediction[0] == 1:
                st.warning("⚠️ The person has Parkinson's disease")
                st.session_state.prediction_log.append(("Parkinson's", "Positive"))
            else:
                st.success("✅ The person does not have Parkinson's disease")
                st.session_state.prediction_log.append(("Parkinson's", "Negative"))
            # chart
            parkinsons_data = {
                "Fo": float(fo or 0),
                "Fhi": float(fhi or 0),
                "Flo": float(flo or 0),
                "Jitter(%)": float(Jitter_percent or 0),
                "Shimmer": float(Shimmer or 0),
                "HNR": float(HNR or 0),
                "RPDE": float(RPDE or 0),
                "PPE": float(PPE or 0)
            }

            parkinsons_df = pd.DataFrame(list(parkinsons_data.items()), columns=['Feature', 'Value'])
            parkinsons_df = parkinsons_df.set_index('Feature')

            st.subheader("📊 Parkinson's Input Summary")
            st.bar_chart(parkinsons_df)
            user_inputs_dict_for_parkinsons = {
        "fo": fo,
        "fhi": fhi,
            "flo": flo,
            "Jitter_percent": Jitter_percent,
                "Jitter_Abs": Jitter_Abs,
        "RAP": RAP,
        "PPQ": PPQ,
            "DDP": DDP,
            "Shimmer": Shimmer,
                "Shimmer_dB": Shimmer_dB,
        "APQ3": APQ3,
        "APQ5": APQ5,
            "APQ": APQ,
            "DDA": DDA,
                "NHR": NHR,
                "HNR": HNR,
        "RPDE": RPDE,
        "DFA": DFA,
            "spread1": spread1,
            "spread2": spread2,
                "D2": D2,
                "PPE": PPE
                }       
            with st.spinner("Fetching health suggestions..."):
                ai_response = get_remedies(user_inputs_dict_for_parkinsons, parkinsons_prediction[0], disease="parkinsons")

            # ✅ Convert Parkinson’s AI suggestions into animated HTML lists
                parkinsons_diet_list = "".join([f"<li>{tip}</li>" for tip in ai_response.get("diet_tips", [])])
                parkinsons_lifestyle_list = "".join([f"<li>{tip}</li>" for tip in ai_response.get("lifestyle_tips", [])])
                parkinsons_notes_list = "".join([f"<li>{tip}</li>" for tip in ai_response.get("notes", [])])

                # ✅ Render animated card for Parkinson's
                parkinsons_card_html = f"""
                <div class="ai-card">
                    <div class="ai-title">💡 AI-Powered Parkinson's Health Suggestions</div>
                    <div class="tip-title">🍽 Diet Tips:</div>
                    <ul>{parkinsons_diet_list}</ul>
                    <div class="tip-title">🏃 Lifestyle Tips:</div>
                    <ul>{parkinsons_lifestyle_list}</ul>
                    <div class="tip-title">🧘 Notes:</div>
                    <ul>{parkinsons_notes_list}</ul>
                </div>
                """

                st.markdown(parkinsons_card_html, unsafe_allow_html=True)
                # 🔹 Save prediction for logged-in user
                if st.session_state.logged_in:
                    save_prediction(
                        username=st.session_state.username,
                        disease="Parkinson's",
                        input_data=user_inputs_dict_for_parkinsons,
                        result=int(parkinsons_prediction[0]),
                        ai_suggestions=ai_response
                    )
                    st.info("✅ Your Parkinson's prediction and AI suggestions have been saved.")

    elif selected == "AI Chat Assistant":
        st.title("🤖 AI Health Expert Chatbot")

        # Load API key securely
        API_KEY = os.getenv("GEMINI_API_KEY")
        if not API_KEY:
            st.error("🔑 API Key is missing. Please check your .env file.")
        else:
            import google.generativeai as gen_ai
            gen_ai.configure(api_key=API_KEY)

            try:
                # You can change the model if needed
                model = gen_ai.GenerativeModel("models/gemma-3n-e2b-it")  # Recommended stable model
            except Exception as e:
                st.error(f"Error loading Gemini model: {e}")
                st.stop()

            # Initialize chat session
            if "chat_session" not in st.session_state:
                st.session_state.chat_session = model.start_chat(history=[])

            st.markdown("💬 Ask me anything about diseases, symptoms, fitness, diet, or mental health.")

            # Show chat history
            for message in st.session_state.chat_session.history:
                with st.chat_message(message.role):
                    st.markdown(message.parts[0].text)

            # Chat input
            user_prompt = st.chat_input("💬 Ask your health question...")
        if user_prompt:
            # User message bubble
            st.markdown(f"""
                <div style='background:#4CAF50; color:white; padding:10px 15px; border-radius:15px; 
                            max-width:70%; margin:10px 0; float:right;'>
                    {user_prompt}
                </div>
                <div style='clear:both;'></div>
            """, unsafe_allow_html=True)

            try:
                gemini_response = st.session_state.chat_session.send_message(
                    f"You are a medical assistant. Answer the following in health-expert tone:\n{user_prompt}"
                )

                if gemini_response and hasattr(gemini_response, "text"):
                    # Assistant message bubble
                    st.markdown(f"""
                        <div style='background:#222; color:#FFD700; padding:10px 15px; border-radius:15px; 
                                    max-width:70%; margin:10px 0; float:left;'>
                            {gemini_response.text}
                        </div>
                        <div style='clear:both;'></div>
                    """, unsafe_allow_html=True)
                else:
                    st.error("⚠️ No valid response received.")
            except Exception as e:
                st.error(f"❌ API response error: {e}")
        
    # About & Developer Page
    elif selected == "About & Developer":
        st.markdown("""
        <style>
        /* Fade-in animation */
        @keyframes fadeIn {
            0% {opacity: 0; transform: translateY(15px);}
            100% {opacity: 1; transform: translateY(0);}
        }

        /* Gradient animated title */
        @keyframes gradientMove {
            0% {background-position: 0% 50%;}
            100% {background-position: 100% 50%;}
        }

        .about-title {
            font-size: 42px;
            font-weight: bold;
            text-align: center;
            background: linear-gradient(270deg, #FF4B4B, #4CAF50, #2196F3);
            background-size: 200% 200%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: gradientMove 4s linear infinite, fadeIn 1s ease-in-out;
            margin-bottom: 30px;
        }

        /* Section container */
        .about-section {
            background: rgba(255,255,255,0.08);
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            animation: fadeIn 1s ease-in-out;
            margin-bottom: 20px;
            color: white;
        }

        /* Developer Info Styling */
        .dev-info {
            background: rgba(255,255,255,0.05);
            padding: 15px;
            border-radius: 10px;
            animation: fadeIn 1.5s ease-in-out;
            color: white;
        }
        .dev-info strong {
            color: #FFD700;
        }
        </style>

        <div class="about-title">📖 About This Project</div>

        <div class="about-section">
            <h3>🧠 Multi-Disease Diagnostic AI</h3>
            <p>This is a health-focused machine learning web application built with <b>Streamlit</b>, designed to:</p>
            <ul>
                <li>🔬 Predict the likelihood of <b>Diabetes</b>, <b>Heart Disease</b>, and <b>Parkinson’s Disease</b></li>
                <li>🤖 Offer <b>AI-powered lifestyle and diet recommendations</b> based on model results</li>
                <li>💬 Provide a real-time <b>AI Health Assistant Chatbot</b> powered by Gemini</li>
            </ul>
            <p>🌟 The app aims to <b>bridge the gap between early prediction and preventive healthcare</b> using machine learning and generative AI.</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("### 🛠 Tech Stack Used")
        st.write("""
        - 🐍 Python  
        - ⚙️ Scikit-Learn  
        - 💾 Pickle  
        - 🎨 Streamlit  
        - 🌐 Flask  
        - 🤖 Google Gemini API  
        - 🧠 DeepFace (for future emotion integration)
        """)

        st.markdown("### 📬 Contact")
        st.write("""
        📧 **Email:** kaustavmondal60@gmail.com  
        💼 **GitHub:** [github.com/kaustavmondal](https://github.com/LeLoUcH-V-BrItAnIa)  
        🌐 **LinkedIn:** [linkedin.com/in/kaustavmondal](https://www.linkedin.com/in/kaustav-mondal-7a2702240)
        """)
        st.markdown("""<div style="text-align:center; color:white; margin-top:20px; font-style:italic;">
            💡 Built with dedication and the goal of making healthcare smarter through AI.
        </div>
        """, unsafe_allow_html=True)
        

    elif selected == "📊 Dashboard":
        st.title("📊 Prediction Dashboard")

        if "prediction_log" not in st.session_state or len(st.session_state.prediction_log) == 0:
            st.info("No predictions yet. Run some tests first!")
        else:
            df = pd.DataFrame(st.session_state.prediction_log, columns=["Disease", "Result"])

            # ✅ Pie Chart for Prediction Result Distribution
            result_counts = df["Result"].value_counts()
            fig1, ax1 = plt.subplots()
            ax1.pie(result_counts.values, labels=result_counts.index, autopct='%1.1f%%', startangle=90, 
                    colors=['#FF6B6B', '#6BCB77'])
            ax1.axis('equal')
            st.subheader("📌 Prediction Result Distribution")
            st.pyplot(fig1)

            # ✅ Bar Chart: Predictions Per Disease
            disease_counts = df["Disease"].value_counts().reset_index()
            disease_counts.columns = ["Disease", "Count"]
            st.subheader("📌 Predictions Per Disease")
            st.bar_chart(disease_counts.set_index("Disease"))

            # ✅ Summary Metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Predictions", len(df))
            with col2:
                st.metric("Diabetes Cases", len(df[df["Disease"] == "Diabetes"]))
            with col3:
                st.metric("Heart Disease Cases", len(df[df["Disease"] == "Heart Disease"]))
            with col4:
                st.metric("Parkinson's Cases", len(df[df["Disease"] == "Parkinson's"]))

    # Footer
    if selected != "AI Chat Assistant":
        # 🔻 Footer
        st.markdown("""
        <hr style="margin-top:40px;">
        <div style="text-align:center; font-size: 14px; color: #888;">
            <b>🧠 Multi-Disease Diagnostic AI</b><br>
            Built with ❤️ using <span style="color:#FF4B4B;">Python</span>, <span style="color:#2196F3;">Streamlit</span>, 
            <span style="color:#4CAF50;">Scikit-Learn</span> & <span style="color:#FF9800;">Gemini AI</span><br>
            © 2025 Kaustav Mondal | For educational & research purposes only
        </div>
        """, unsafe_allow_html=True)
