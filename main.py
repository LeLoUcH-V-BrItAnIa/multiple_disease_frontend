import os
import pickle
import streamlit as st
from streamlit_option_menu import option_menu
import requests
from get_remedies import get_remedies
import google.generativeai as genai
from dotenv import load_dotenv

# Set page configuration
st.set_page_config(page_title="Health Assistant",
                   layout="wide",
                   page_icon="🧑‍⚕️")

# Get current working directory
working_dir = os.path.dirname(os.path.abspath(__file__))

# Load models
diabetes_model = pickle.load(open(f'{working_dir}/saved_models/diabetes_model.sav', 'rb'))
heart_disease_model = pickle.load(open(f'{working_dir}/saved_models/heart_disease_model.sav', 'rb'))
parkinsons_model = pickle.load(open(f'{working_dir}/saved_models/parkinsons_model.sav', 'rb'))

# Sidebar
with st.sidebar:
    selected = option_menu(
        'Multi-Disease Diagnostic AI',
        ['Diabetes Prediction', 'Heart Disease Prediction', 'Parkinsons Prediction', 'AI-Based Health Assistant','AI Chat Assistant','About & Developer'],
        menu_icon='hospital-fill',
        icons=['activity', 'heart', 'person', 'robot','chat-dots-fill','info-circle'],
        default_index=0
    )

# AI-Based Health Assistant Page
if selected == 'AI-Based Health Assistant':
    st.title("🧠 AI-Based Health Assistant")
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
                    res = requests.post("https://multiple-desease-backend.onrender.com/recommend", json=payload,timeout=20)
                    if res.status_code == 200:
                        result = res.json()
                        st.success("✅ Gemini AI Suggestions")
                        st.write("**🍽 Diet Tips:**", result.get("diet_tips", []))
                        st.write("**🏃 Lifestyle Tips:**", result.get("lifestyle_tips", []))
                        st.write("**💬 Notes:**", result.get("notes", []))
                    else:
                        st.error("❌ Error from backend")
                        st.text(res.text)
                except Exception as e:
                    st.error(f"❌ Request failed: {str(e)}")
                    

# Diabetes Prediction Page
elif selected == 'Diabetes Prediction':
    st.title('Diabetes Prediction using ML')

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

    if st.button('Diabetes Test Result'):
        user_input_list = [Pregnancies, Glucose, BloodPressure, SkinThickness, Insulin,
                           BMI, DiabetesPedigreeFunction, Age]
        user_input_list = [float(x) for x in user_input_list]

        diab_prediction = diabetes_model.predict([user_input_list])

        if diab_prediction[0] == 0:
            diab_diagnosis = '✅ The person is not diabetic'
            st.success(diab_diagnosis)
        else:
            diab_diagnosis = "⚠️ The person is diabetic"
            st.warning(diab_diagnosis)

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

        st.subheader("💡 AI-Powered Health Suggestions")
        st.write("**🍽 Diet Tips:**", ai_response.get("diet_tips", []))
        st.write("**🏃 Lifestyle Tips:**", ai_response.get("lifestyle_tips", []))
        st.write("**🧘 Notes:**", ai_response.get("notes", []))

# Heart Disease Prediction Page
elif selected == 'Heart Disease Prediction':
    st.title('Heart Disease Prediction using ML')

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
            st.warning('⚠️The person is having heart disease')
        else:
            st.success('✅The person does not have any heart disease')
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

        st.subheader("💡 AI-Powered Health Suggestions")
        st.write("**🍽 Diet Tips:**", ai_response.get("diet_tips", []))
        st.write("**🏃 Lifestyle Tips:**", ai_response.get("lifestyle_tips", []))
        st.write("**🧘 Notes:**", ai_response.get("notes", []))


# Parkinson's Disease Prediction Page
elif selected == "Parkinsons Prediction":
    st.title("Parkinson's Disease Prediction using ML")

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
            st.warning("⚠️The person has Parkinson's disease")
        else:
            st.success("✅The person does not have Parkinson's disease")
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

        st.subheader("💡 AI-Powered Health Suggestions")
        st.write("**🍽 Diet Tips:**", ai_response.get("diet_tips", []))
        st.write("**🏃 Lifestyle Tips:**", ai_response.get("lifestyle_tips", []))
        st.write("**🧘 Notes:**", ai_response.get("notes", []))

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
        user_prompt = st.chat_input("Ask your health question...")
        if user_prompt:
            st.chat_message("user").markdown(user_prompt)
            try:
                gemini_response = st.session_state.chat_session.send_message(
                    f"You are a medical assistant. Answer the following in health-expert tone:\n{user_prompt}"
                )
                if gemini_response and hasattr(gemini_response, "text"):
                    with st.chat_message("assistant"):
                        st.markdown(gemini_response.text)
                else:
                    st.error("⚠️ No valid response received.")
            except Exception as e:
                st.error(f"❌ API response error: {e}")
    
# About & Developer Page
elif selected == "About & Developer":
    st.title("📖 About This Project")

    st.markdown("""
    ### 🧠 Multi-Disease Diagnostic AI

    This is a health-focused machine learning web application built with **Streamlit**, designed to:
    - Predict the likelihood of **Diabetes**, **Heart Disease**, and **Parkinson’s Disease**
    - Offer **AI-powered lifestyle and diet recommendations** based on model results
    - Provide a real-time **AI Health Assistant Chatbot** powered by **Gemini**
    
    The app aims to **bridge the gap between early prediction and preventive healthcare** using machine learning and generative AI.
    """)

    st.markdown("---")

    st.subheader("👨‍💻 Developer Info")
    st.markdown("""
    **Name:** Kaustav Mondal  
    **Role:** MCA Student | AI & HealthTech Enthusiast  
    **Project Type:** Academic Research & Practical Implementation  
    **Tech Stack Used:**  
    - Python, Scikit-Learn, Pickle  
    - Streamlit, Flask, Google Gemini API  
    - DeepFace (for future emotion integration)  

    **Contact:**  
    - 📧 Email: kaustavmondal60@gmail.com  
    - 💼 GitHub: [github.com/kaustavmondal](https://github.com/LeLoUcH-V-BrItAnIa)  
    - 🌐 LinkedIn: [linkedin.com/in/kaustavmondal](www.linkedin.com/in/kaustav-mondal-7a2702240)
    """)

    st.markdown("---")
    st.markdown("💡 _Built with dedication and the goal of making healthcare smarter through AI._")
            

                

# Footer
if selected != "AI Chat Assistant":
    st.markdown("""
<hr style="margin-top:30px">
<div style="text-align:center; font-size: 14px;">
    🧠 Built with ❤️ by <b>Kaustav Mondal</b> | Powered by Gemini API<br>
    © 2025 | For educational and research purposes only
</div>
""", unsafe_allow_html=True)
