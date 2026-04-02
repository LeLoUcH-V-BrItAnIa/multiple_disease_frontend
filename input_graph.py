import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

def plot_user_vs_risk(user_data, risk_limits, title="📊 User vs Risk Comparison"):
    
    df = pd.DataFrame(list(user_data.items()), columns=['Feature', 'Value'])
    
    features = df['Feature']
    user_values = df['Value']
    risk_values = [risk_limits.get(f, 0) for f in features]

    x = np.arange(len(features))
    width = 0.35

    st.subheader(title)

    plt.figure()

    plt.bar(x - width/2, user_values, width, label='Your Value')
    plt.bar(x + width/2, risk_values, width, label='Risk Limit')

    plt.xticks(x, features, rotation=30)
    plt.ylabel("Value")
    plt.legend()

    st.pyplot(plt)