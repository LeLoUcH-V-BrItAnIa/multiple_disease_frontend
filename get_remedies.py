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
from db_utils import get_user_records

# Load API key 
load_dotenv()
API_KEY = st.secrets["GEMINI_API_KEY"]#os.getenv("GEMINI_API_KEY") Fix It
# genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
genai.configure(api_key=API_KEY)#Fix It


# Load Gemini model
model = genai.GenerativeModel("models/gemma-3n-e2b-it")

# History summary function 
def build_user_history_summary(records):
    if not records:
        return "No previous records."

    summary = ""

    for r in records[:10]:  # last 10 records only
        summary += f"""
Disease: {r.get('disease')}
Result: {r.get('result')}
"""

    return summary

# -------- Prompt Builders --------

def build_diabetes_prompt(inputs, prediction,history_summary):
    condition = "diabetic" if prediction == 1 else "not diabetic"
    fields = "\n".join([f"{k}: {v}" for k, v in inputs.items()])
    
    return f"""
    You are an advanced AI health advisor.

    CURRENT PATIENT DATA:
    {fields}

    CURRENT PREDICTION:
    The person is {condition}.

    PATIENT HISTORY:
    {history_summary}

    TASK:
    1. Analyze trends in the patient's history
    2. Identify if condition is improving or worsening
    3. Give:
    - 2 personalized diet tips
    - 2 lifestyle improvements
    - 1 long-term health insight

    Respond in JSON:
    {{
    "diet_tips": [],
    "lifestyle_tips": [],
    "notes": []
    }}
    """

def build_heart_prompt(inputs, prediction,history_summary):
    condition = "has heart disease" if prediction == 1 else "does not have heart disease"
    fields = "\n".join([f"{k}: {v}" for k, v in inputs.items()])
    
    return f"""
You are an advanced AI health advisor.

CURRENT PATIENT DATA:
{fields}

CURRENT PREDICTION:
The person is {condition}.

PATIENT HISTORY:
{history_summary}

TASK:
1. Analyze trends in the patient's history
2. Identify if condition is improving or worsening
3. Give:
   - 2 personalized diet tips
   - 2 lifestyle improvements
   - 1 long-term health insight

Respond in JSON:
{{
  "diet_tips": [],
  "lifestyle_tips": [],
  "notes": []
}}
"""

def build_parkinsons_prompt(inputs, prediction,history_summary):
    condition = "has Parkinson’s disease" if prediction == 1 else "does not have Parkinson’s disease"
    fields = "\n".join([f"{k}: {v}" for k, v in inputs.items()])
    
    return f"""
You are an advanced AI health advisor.

CURRENT PATIENT DATA:
{fields}

CURRENT PREDICTION:
The person is {condition}.

PATIENT HISTORY:
{history_summary}

TASK:
1. Analyze trends in the patient's history
2. Identify if condition is improving or worsening
3. Give:
   - 2 personalized diet tips
   - 2 lifestyle improvements
   - 1 long-term health insight

Respond in JSON:
{{
  "diet_tips": [],
  "lifestyle_tips": [],
  "notes": []
}}
"""

def build_leukemia_prompt(inputs, prediction,history_summary):
    condition = "has Leukemia" if prediction == 1 else "does not have Leukemia"
    fields = "\n".join([f"{k}: {v}" for k, v in inputs.items()])

    return f"""
You are an advanced AI health advisor.

CURRENT PATIENT DATA:
{fields}

CURRENT PREDICTION:
The person is {condition}.

PATIENT HISTORY:
{history_summary}

TASK:
1. Analyze trends in the patient's history
2. Identify if condition is improving or worsening
3. Give:
   - 2 personalized diet tips
   - 2 lifestyle improvements
   - 1 long-term health insight

Respond in JSON:
{{
  "diet_tips": [],
  "lifestyle_tips": [],
  "notes": []
}}
"""


# -------- Dispatcher Function --------

def get_remedies(user_inputs, prediction, disease , username):
    disease = disease.lower()
    # fetch records 
    records = get_user_records(username)
    history_summary = build_user_history_summary(records)
    
    if disease == "diabetes":
        prompt = build_diabetes_prompt(user_inputs, prediction,history_summary)
    elif disease == "heart":
        prompt = build_heart_prompt(user_inputs, prediction,history_summary)
    elif disease == "parkinsons":
        prompt = build_parkinsons_prompt(user_inputs, prediction,history_summary)
    elif disease == "leukemia":
        prompt = build_leukemia_prompt(user_inputs, prediction,history_summary)
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
# for dashboard insights 
def generate_dashboard_insights(df): 
    # Convert dataframe to summary text
    summary = f"""
    Total Records: {len(df)}

    Disease Counts:
    {df['Disease'].value_counts().to_dict()}

    Result Counts:
    {df['Result'].value_counts().to_dict()}
    """

    prompt = f"""
    You are a health analytics AI.

    Analyze this user's health prediction dashboard data:

    {summary}

    Give:
    - 2-3 short insights about trends or risks
    - 1 motivational or advisory note

    Keep it simple, friendly, and helpful.
    """

    model = genai.GenerativeModel("models/gemma-3n-e2b-it")
    response = model.generate_content(prompt)

    return response.text