import streamlit as st
import requests
import google.generativeai as genai
import os

st.set_page_config(page_title="SitePulse - Website Auditor", page_icon="⚡", layout="wide")

st.title("⚡ SitePulse - AI Website Auditor")
st.write("Enter a website URL to audit performance and SEO using AI.")

# API Keys from Environment or User Input
gemini_key = os.getenv("GEMINI_API_KEY", "")
openrouter_key = os.getenv("OPENROUTER_API_KEY", "")

url = st.text_input("Enter Website URL:", placeholder="https://example.com")

if st.button("Audit Website"):
    if not url:
        st.warning("Please enter a valid URL.")
    else:
        st.info(f"Auditing {url}...")
        try:
            response = requests.get(url, timeout=10)
            st.success(f"Status Code: {response.status_code}")
            st.code(f"Header Response: {dict(list(response.headers.items())[:5])}")
            
            # AI Analysis via Gemini if Key Available
            if gemini_key:
                genai.configure(api_key=gemini_key)
                model = genai.GenerativeModel('gemini-pro')
                ai_res = model.generate_content(f"Analyze this website headers/status for SEO & security: {response.headers}")
                st.subheader("AI Audit Report")
                st.write(ai_res.text)
        except Exception as e:
            st.error(f"Failed to reach website: {e}")