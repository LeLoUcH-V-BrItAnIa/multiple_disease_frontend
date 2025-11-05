# import google.generativeai as genai
# import json, re
# import os
# from dotenv import load_dotenv


# # Load .env file
# load_dotenv()

# # genai.configure(api_key="AIzaSyAYUq-ZAOpOGRjbDZkL4-_o64gE62ZRq0w")
# # Configure Gemini API
# # Set your Gemini API key
# genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
# model = genai.GenerativeModel("models/gemma-3n-e2b-it")

# def build_prompt(inputs, prediction):
#     input_lines = "\n".join([f"{k}: {v}" for k, v in inputs.items()])
#     condition = "diabetic" if prediction == 1 else "not diabetic"

#     return f"""
# You are an AI health advisor.

# The user provided the following medical details:
# {input_lines}

# Prediction: The person is {condition}.

# Based on these values, suggest:
# 1. 2-3 diet tips
# 2. 2-3 lifestyle improvements
# 3. One friendly note or motivational health advice

# Respond in this JSON format only:
# {{
#   "diet_tips": ["...", "..."],
#   "lifestyle_tips": ["...", "..."],
#   "notes": ["..."]
# }}
# """

# def get_remedies(user_inputs, prediction):
#     prompt = build_prompt(user_inputs, prediction)
#     response = model.generate_content(prompt)
#     return extract_json(response.text)

# def extract_json(text):
#     try:
#         json_text = re.search(r"\{.*\}", text, re.DOTALL).group()
#         return json.loads(json_text)
#     except:
#         return {"error": "Could not parse Gemini response", "raw": text}
import os
import streamlit as st
import json
import re
import google.generativeai as genai
from dotenv import load_dotenv

# Load API key
load_dotenv()
API_KEY = st.secrets["GEMINI_API_KEY"]
# genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Load Gemini model
model = genai.GenerativeModel("models/gemma-3n-e2b-it")

# -------- Prompt Builders --------

def build_diabetes_prompt(inputs, prediction):
    condition = "diabetic" if prediction == 1 else "not diabetic"
    fields = "\n".join([f"{k}: {v}" for k, v in inputs.items()])
    
    return f"""
You are a medical AI assistant.

The user provided the following input values related to diabetes:
{fields}

Prediction: The person is {condition}.

Give 2-3 personalized:
- 🍽 Diet Tips
- 🏃 Lifestyle Recommendations
- 💬 A short motivational health note

Return output in JSON format:
{{
  "diet_tips": ["..."],
  "lifestyle_tips": ["..."],
  "notes": ["..."]
}}
"""

def build_heart_prompt(inputs, prediction):
    condition = "has heart disease" if prediction == 1 else "does not have heart disease"
    fields = "\n".join([f"{k}: {v}" for k, v in inputs.items()])
    
    return f"""
You are a heart health advisor.

The following patient data was submitted:
{fields}

Model Prediction: The person {condition}.

Give:
- 🧡 2–3 heart-healthy lifestyle tips
- 🥗 Diet changes to improve heart health
- 💬 One short health note

Respond in JSON format:
{{
  "diet_tips": ["..."],
  "lifestyle_tips": ["..."],
  "notes": ["..."]
}}
"""

def build_parkinsons_prompt(inputs, prediction):
    condition = "has Parkinson’s disease" if prediction == 1 else "does not have Parkinson’s disease"
    fields = "\n".join([f"{k}: {v}" for k, v in inputs.items()])
    
    return f"""
You are a neuro-care AI assistant.

The following voice/vocal features were submitted for Parkinson’s prediction:
{fields}

Prediction: The person {condition}.

Give:
- 🧠 2–3 lifestyle or exercise suggestions for Parkinson’s support
- 🥗 Diet suggestions
- 💬 A short uplifting note for the patient

Respond in JSON format:
{{
  "diet_tips": ["..."],
  "lifestyle_tips": ["..."],
  "notes": ["..."]
}}
"""
def build_leukemia_prompt(inputs, prediction):
    condition = "has Leukemia" if prediction == 1 else "does not have Leukemia"
    fields = "\n".join([f"{k}: {v}" for k, v in inputs.items()])

    return f"""
You are a hematology AI assistant.

The following patient health features were submitted for Leukemia prediction:
{fields}

Prediction: The person {condition}.

Give:
- 🧠 2–3 lifestyle or treatment support suggestions for Leukemia care
- 🥗 Diet and nutrition tips for better immunity
- 💬 A short uplifting note for the patient

Respond in JSON format:
{{
  "diet_tips": ["..."],
  "lifestyle_tips": ["..."],
  "notes": ["..."]
}}
"""


# -------- Dispatcher Function --------

def get_remedies(user_inputs, prediction, disease):
    disease = disease.lower()
    
    if disease == "diabetes":
        prompt = build_diabetes_prompt(user_inputs, prediction)
    elif disease == "heart":
        prompt = build_heart_prompt(user_inputs, prediction)
    elif disease == "parkinsons":
        prompt = build_parkinsons_prompt(user_inputs, prediction)
    elif disease == "leukemia":
        prompt = build_leukemia_prompt(user_inputs, prediction)
    else:
        return {"error": "Unsupported disease type"}

    response = model.generate_content(prompt)
    return extract_json(response.text)

# -------- JSON Parser --------

def extract_json(text):
    try:
        json_text = re.search(r"\{.*\}", text, re.DOTALL).group()
        return json.loads(json_text)
    except Exception as e:
        return {
            "error": "Could not parse Gemini response",
            "raw": text,
            "exception": str(e)
        }