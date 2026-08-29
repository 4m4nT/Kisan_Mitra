@echo off
echo Starting Kisan Mitra AI Crop Doctor...
cd /d "%~dp0"
call venv\Scripts\activate
streamlit run app.py
pause
