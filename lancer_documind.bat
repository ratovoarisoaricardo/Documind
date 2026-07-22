@echo off
cd /d C:\Users\ABCD\OneDrive\Documents\AI\documind-ai
pip install streamlit pypdf >nul 2>&1
streamlit run app.py
pause
