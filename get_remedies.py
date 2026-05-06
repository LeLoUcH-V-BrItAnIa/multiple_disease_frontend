import os
import streamlit as st
import json
import re
import google.generativeai as genai
from dotenv import load_dotenv
from db_utils import get_user_records

# Load API key 
load_dotenv()
API_KEY = st.secrets["GEMINI_API_KEY"] #os.getenv("GEMINI_API_KEY") # Fix It
# genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
genai.configure(api_key=API_KEY)#Fix It


# Load Gemini model
model = genai.GenerativeModel("models/gemma-4-31b-it")


def ai_suggest_username(email):
    prompt = f"Suggest a short, cool username based on this email: {email}. Only return username, no explanation."

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except:
        return "Error" # fallback

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

def build_leukemia_interpretation_prompt(inputs):
    fields = "\n".join([f"{k}: {v}" for k, v in inputs.items()])
    return f"""
        You are a medical assistant AI.

        IMPORTANT:
        Respond ONLY in valid JSON format.
        DO NOT add any explanation outside JSON.

        FORMAT:
        {{
        "summary": "...",
        "key_points": ["...", "..."]
        }}

        DATA:
        {fields}
        """
                


def get_cbc_interpretation(inputs):
    prompt = build_leukemia_interpretation_prompt(inputs)

    response = model.generate_content(prompt)
    print(response.text)
    try:
        text = response.text.strip()

        # 🔥 Extract JSON from messy response
        json_match = re.search(r"\{.*\}", text, re.DOTALL)

        if json_match:
            return json.loads(json_match.group())
        else:
            raise ValueError("No JSON found")

    except Exception as e:
        return {
            "summary": "AI could not properly interpret the report.",
            "key_points": [
                "Try again or check input values.",
                "Ensure values are realistic.",
                "AI response format was invalid."
            ]
        }
    
# -------- Prompt Builders --------

def build_kidney_prompt(inputs, prediction, history_summary):
        condition = "has kidney disease" if prediction == 1 else "does not have kidney disease"
        fields = "\n".join([f"{k}: {v}" for k, v in inputs.items()])

        return f"""
        You are an advanced AI health advisor.

        CURRENT PATIENT DATA:
        {fields}

        CURRENT PREDICTION:
        The person {condition}.

        PATIENT HISTORY:
        {history_summary}

        TASK:
        - Give 2 diet tips
        - 2 lifestyle improvements
        - 1 long-term kidney health advice

        Respond in JSON:
        {{
        "diet_tips": [],
        "lifestyle_tips": [],
        "notes": []
        }}
        """


def build_thyroid_prompt(inputs, prediction, history_summary):
    condition = "has thyroid disorder" if prediction == 1 else "has normal thyroid function"
    fields = "\n".join([f"{k}: {v}" for k, v in inputs.items()])

    return f"""
        You are an advanced AI health advisor.

        CURRENT PATIENT DATA:
        {fields}

        CURRENT PREDICTION:
        The person {condition}.

        PATIENT HISTORY:
        {history_summary}

        TASK:
        - Give 2 diet tips
        - 2 lifestyle improvements
        - 1 long-term thyroid health advice

        Respond in JSON:
        {{
        "diet_tips": [],
        "lifestyle_tips": [],
        "notes": []
        }}
        """

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
    elif disease == "kidney":
        prompt = build_kidney_prompt(user_inputs, prediction, history_summary)

    elif disease == "thyroid":
        prompt = build_thyroid_prompt(user_inputs, prediction, history_summary)
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
    
import re
import re

def clean_dashboard_response(text):

    # Find ALL sections starting with 🔹
    matches = re.findall(r"(🔹.*?💡.*?)(?=\n\n|$)", text, re.DOTALL)

    # Return LAST valid section only
    if matches:
        return matches[-1].strip()

    return text.strip()

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
        You are a smart health dashboard AI.

        Analyze the user's health prediction summary below.

        {summary}

        IMPORTANT RULES:
        - ONLY give final insights
        - DO NOT explain your thinking
        - DO NOT mention words like:
        "Role", "Input Data", "Requirements", "Formatting", "Check"
        - Keep response short and clean
        - Maximum 4 bullet points
        - Friendly and professional tone

        Format:
        🔹 Insight 1
        🔹 Insight 2
        🔹 Insight 3
        💡 Advisory Note
        """

    model = genai.GenerativeModel("models/gemma-4-31b-it")
    response = model.generate_content(prompt)

    cleaned = clean_dashboard_response(response.text)
    return cleaned