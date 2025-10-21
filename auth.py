import streamlit as st
from streamlit_lottie import st_lottie
import requests
from pymongo import MongoClient
import bcrypt
import os
from dotenv import load_dotenv

# ---------------- Environment & MongoDB Setup ----------------
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")  # or st.secrets["MONGO_URI"]

try:
    client = MongoClient(MONGO_URI)
    client.admin.command('ping')
    print("✅ Connected to MongoDB Atlas successfully!")
except Exception as e:
    print("❌ MongoDB connection failed:", e)
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

# ---------------- Functions ----------------
def register_user(username, email, password):
    if users_collection.find_one({"username": username}):
        return False, "Username already exists!"
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    users_collection.insert_one({"username": username, "email": email, "password": hashed_pw})
    return True, "User registered successfully!"

def login_user(username, password):
    user = users_collection.find_one({"username": username})
    if user and bcrypt.checkpw(password.encode('utf-8'), user["password"]):
        return True, user
    return False, None

def load_lottie(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# ---------------- Page Setup ----------------
st.set_page_config(page_title="Pulse", page_icon="🩺", layout="wide")

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

st.markdown("<h1 style='text-align:center; font-size:3rem;'>Pulse 🩺<br>Predictive Understanding for Lifestyle & Smart Evaluation</h1>", unsafe_allow_html=True)

# ---------------- Lottie Animation ----------------
animation_url = "https://assets9.lottiefiles.com/packages/lf20_qp1q7mct.json"
lottie_anim = load_lottie(animation_url)
st_lottie(lottie_anim, height=250)

# ---------------- Page Logic ----------------
def show_login_register_page():
    tab = st.radio("Choose Option", ["Login", "Register"], horizontal=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("auth_form"):
            if tab == "Register":
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
                            st.success(f"Welcome {username}! Redirecting...")
                            st.session_state.page = "home"  # redirect to home
                            st.rerun()
                        else:
                            st.error("❌ Invalid username or password")
                    else:
                        st.warning("Enter both username and password")

# ---------------- Home Page ----------------
def show_home_page():
    st.title(f"Welcome, {st.session_state.username}!")
    st.subheader("🏠 Home Page of PULSE")

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.page = "login"
        st.rerun()

    st.write("Here goes your main app content…")

# ---------------- Router ----------------
if st.session_state.logged_in:
    st.session_state.page = "home"

if st.session_state.page == "login":
    show_login_register_page()
elif st.session_state.page == "home":
    show_home_page()
