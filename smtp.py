import random
import smtplib
import streamlit as st
from email.mime.text import MIMEText
def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(user_email, otp):
    sender_email = "britanialelouchv6@gmail.com"
    sender_password = "wtrp qcxm hezk erxx"  # Use App Password for Gmail
    subject = "Your OTP Verification Code"
    body = f"Your OTP code is: {otp}"
    message = f"Subject: {subject}\n\n{body}"

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, user_email, message)
    except Exception as e:
        st.error(f"Failed to send email: {e}")