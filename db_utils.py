from pymongo import MongoClient
import bcrypt
import os
from dotenv import load_dotenv
import streamlit as st
from datetime import datetime

# Load local .env if exists
load_dotenv()

# Use Streamlit secrets if running in cloud
MONGO_URI =  os.getenv("MONGO_URI")  #st.secrets["MONGO_URI"] Fix It


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



# Prediction Data Functions
def save_prediction(username, disease, input_data, result, ai_suggestions):
    records_collection.insert_one({
        "username": username,
        "disease": disease,
        "inputs": input_data,
        "result": int(result),
        "ai_suggestions": ai_suggestions,
        "created_at":datetime.now()
    })
# deletion function 
def delete_old_record(username,keep_latest=5):
    records = list(
        records_collection.find({"username":username}).sort("created_at",-1)
    )
    old_records = records[keep_latest:]

    if old_records:
        ids_to_delete = [r["_id"] for r in old_records]
        records_collection.delete_many({"_id":{"$in":ids_to_delete}})
        return len(ids_to_delete)
    return 0

# get user records 
def get_user_records(username):
    return list(records_collection.find({"username": username}, {"_id": 0}).sort("created_at",-1)) #newest first