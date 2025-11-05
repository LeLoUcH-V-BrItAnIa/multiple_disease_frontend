from pymongo import MongoClient
import bcrypt
import os
from dotenv import load_dotenv
import streamlit as st

# Load local .env if exists
load_dotenv()

# Use Streamlit secrets if running in cloud
MONGO_URI = st.secrets["MONGO_URI"] #os.getenv("MONGO_URI")  

# Connect to MongoDB Atlas
try:
    client = MongoClient(MONGO_URI)
    client.admin.command('ping')  # Test connection
    print("✅ Connected to MongoDB Atlas successfully!")
except Exception as e:
    print("❌ MongoDB connection failed:", e)
    st.error("MongoDB connection failed. Check your URI!")

# Database & Collections
db = client["pulse_db"]
users_collection = db["users"]
records_collection = db["records"]

# def register_user(username, email, password):
#     if users_collection.find_one({"username": username}):
#         return False, "Username already exists!"
#     hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
#     users_collection.insert_one({"username": username, "email": email, "password": hashed_pw})
#     return True, "User registered successfully!"

# def login_user(username, password):
#     user = users_collection.find_one({"username": username})
#     if user and bcrypt.checkpw(password.encode('utf-8'), user["password"]):
#         return True, user
#     return False, None

# -------------------------------
# Prediction Data Functions
# -------------------------------

def save_prediction(username, disease, input_data, result, ai_suggestions):
    records_collection.insert_one({
        "username": username,
        "disease": disease,
        "inputs": input_data,
        "result": result,
        "ai_suggestions": ai_suggestions
    })

def get_user_records(username):
    return list(records_collection.find({"username": username}, {"_id": 0}))