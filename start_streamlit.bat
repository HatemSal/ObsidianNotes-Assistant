@echo off
echo Starting RAG Agent with Streamlit Frontend...
echo.

echo Checking for existing processes on port 8000...
call kill_port_8000.bat

echo Starting FastAPI Backend...
start "FastAPI Backend" cmd /k "cd /d %~dp0\src && python fastapi_backend.py"

echo Waiting for backend to start...
timeout /t 3 /nobreak > nul

echo Starting Streamlit Frontend...
start "Streamlit Frontend" cmd /k "cd /d %~dp0 && streamlit run streamlit_app.py"

echo.
echo Both services are starting...
echo FastAPI Backend: http://localhost:8000
echo Streamlit Frontend: http://localhost:8501
echo.
pause