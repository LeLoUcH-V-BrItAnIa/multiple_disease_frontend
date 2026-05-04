from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Get URI
MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    print("❌ MONGO_URI not found! Check your .env file")
    exit()

try:
    # Connect
    client = MongoClient(MONGO_URI)

    # Test connection
    client.admin.command("ping")
    print("✅ Connected to MongoDB Atlas!")

    # Access DB
    db = client["pulse_db"]
    collection = db["test_collection"]

    # Insert test data
    test_doc = {"name": "Kaustav", "status": "Mongo Working 🚀"}
    result = collection.insert_one(test_doc)

    print(f"✅ Inserted document ID: {result.inserted_id}")

    # Read data
    data = collection.find_one({"_id": result.inserted_id})
    print("📦 Retrieved Data:", data)

    print("\n🎉 EVERYTHING IS WORKING PERFECTLY!")

except Exception as e:
    print("❌ ERROR:", e)