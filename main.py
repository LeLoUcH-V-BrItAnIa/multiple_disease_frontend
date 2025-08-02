import pandas as pd
import matplotlib.pyplot as plt
import os
import pickle
import streamlit as st
from streamlit_option_menu import option_menu
import requests
from get_remedies import get_remedies
import google.generativeai as genai
from dotenv import load_dotenv
if "page" not in st.session_state:
    st.session_state.page = "home"
if "prediction_log" not in st.session_state:
    st.session_state["prediction_log"] = []
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
    st.markdown("<h1 style='text-align: center;background-size: 600% 600%;font-size: 50px;font-weight: 800;'>🏥 CareIQ: Predict Prevent Personalize 🧠</h1>", unsafe_allow_html=True)
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

    st.markdown('<div class="fade-subheading">🧠An AI-powered health diagnostic and advisory system 🤖💊 that predicts Diabetes, Heart Disease, and Parkinson’s Disease based on clinical parameters.</div>',unsafe_allow_html=True)

    # Animation
    with st.container():
        st.markdown('<div class="lottie-container">', unsafe_allow_html=True)
        st_lottie(health_animation, height=250, key="health")
        st.markdown('</div>', unsafe_allow_html=True)

    # Project Overview
    st.markdown("""
    ### 🔬 **Project Overview**
    This AI-powered health assistant can predict:
    - 🩸 **Diabetes**
    - ❤️ **Heart Disease**
    - 🧠 **Parkinson’s Disease**

    It also gives **Gemini AI-powered diet & lifestyle recommendations** based on predictions.
    """)

    # 🏗️ 3 Columns Section
    col1, col2, col3 = st.columns(3)

    with col1:
        if diabetes_animation:
            st_lottie(diabetes_animation, height=200, key="diabetes")
        st.markdown("""
        ### 🩸 **Diabetes**
        Detects diabetes using:
        - Glucose levels  
        - BMI & Insulin  
        - Pregnancies count  
        Provides **AI-based diet & lifestyle suggestions**.
        """)

    with col2:
        if heart_animation:
            st_lottie(heart_animation, height=200, key="heart")
        st.markdown("""
        ### ❤️ **Heart Disease**
        Predicts heart disease using:
        - Cholesterol & BP  
        - ECG & Heart Rate  
        - Age, gender & chest pain type  
        Offers **personalized heart-health recommendations**.
        """)

    with col3:
        if parkinsons_animation:
            st_lottie(parkinsons_animation, height=200, key="parkinsons")
        st.markdown("""
        ### 🧠 **Parkinson's**
        Analyzes voice patterns like:
        - Jitter & Shimmer  
        - HNR & RPDE  
        - PPE & DFA metrics  
        Suggests **early interventions & exercises**.
        """)
    st.subheader("📈 Sample Health Data Insights")

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
    
    st.stop()

# Sidebar
if st.session_state.page == "app":
    with st.sidebar:
        selected = option_menu(
        'Multi-Disease Diagnostic AI',
        ['Diabetes Prediction', 'Heart Disease Prediction', 'Parkinsons Prediction', 'AI-Based Health Assistant','📊 Dashboard','AI Chat Assistant','About & Developer'],
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
                        res = requests.post("https://multiple-desease-backend.onrender.com/recommend", json=payload)
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
                st.session_state.prediction_log.append(("Diabetes", "Non-Diabetic"))
            else:
                diab_diagnosis = "⚠️ The person is diabetic"
                st.warning(diab_diagnosis)
                st.session_state.prediction_log.append(("Diabetes", "Diabetic"))

            user_data = {
                "Pregnancies": float(Pregnancies or 0),
                "Glucose": float(Glucose or 0),
                "BloodPressure": float(BloodPressure or 0),
                "BMI": float(BMI or 0),
                "Age": float(Age or 0)
            }
            user_data = {
                "Pregnancies": float(Pregnancies or 0),
                "Glucose": float(Glucose or 0),
                "BloodPressure": float(BloodPressure or 0),
                "BMI": float(BMI or 0),
                "Age": float(Age or 0)
            }

            df = pd.DataFrame(list(user_data.items()), columns=['Feature', 'Value'])
            df = df.set_index('Feature')  # st.bar_chart needs an index

            st.subheader("📊 User Input Summary")
            st.bar_chart(df)

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
