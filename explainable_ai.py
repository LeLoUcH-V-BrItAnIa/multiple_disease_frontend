import shap
import numpy as np

def get_shap_explanation(model, input_list, feature_names):
    
    input_array = np.array([input_list])

    # background data
    background_data = np.random.rand(50, len(feature_names))

    # explainer (works for SVC)
    explainer = shap.KernelExplainer(
        model.decision_function,
        background_data
    )

    shap_values = explainer.shap_values(input_array)

    if isinstance(shap_values, list):
        shap_values = shap_values[0]

    # flatten
    shap_values = shap_values[0]

    # create dict
    shap_dict = {}
    for i in range(len(feature_names)):
        shap_dict[feature_names[i]] = shap_values[i]

    # sort
    sorted_features = sorted(shap_dict.items(), key=lambda x: abs(x[1]), reverse=True)
    

    return sorted_features[:5],shap_values