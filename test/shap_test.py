import shap
import numpy as np
import pickle

# ---------------- LOAD MODEL ----------------
model = pickle.load(open("../saved_models/diabetes_model.sav", "rb"))

# ---------------- SAMPLE INPUT ----------------
# High-risk example
input_data = np.array([[5, 180, 90, 35, 200, 34.5, 0.8, 50]])

# ---------------- BACKGROUND DATA ----------------
# IMPORTANT: must not be same as input
background_data = np.random.rand(50, 8)

# ---------------- CREATE EXPLAINER ----------------
explainer = shap.KernelExplainer(model.decision_function, background_data)

# ---------------- GET SHAP VALUES ----------------
shap_values = explainer.shap_values(input_data)

# ---------------- FEATURE NAMES ----------------
feature_names = [
    "Pregnancies", "Glucose", "BloodPressure", "SkinThickness",
    "Insulin", "BMI", "DiabetesPedigreeFunction", "Age"
]

# ---------------- PRINT RAW OUTPUT ----------------
print("\nSHAP RAW VALUES:")
print(shap_values)

# ---------------- CONVERT TO DICTIONARY ----------------
shap_dict = {}

for i in range(len(feature_names)):
    shap_dict[feature_names[i]] = shap_values[0][i]

# ---------------- SORT FEATURES ----------------
sorted_features = sorted(shap_dict.items(), key=lambda x: abs(x[1]), reverse=True)

# ---------------- PRINT RESULT ----------------
print("\nTop Feature Contributions:")
for feature, value in sorted_features:
    direction = "increased risk" if value > 0 else "decreased risk"
    print(f"{feature}: {round(value, 4)} → {direction}")