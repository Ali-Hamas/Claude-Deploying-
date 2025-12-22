@echo off
echo ================================================
echo Starting Todo Backend Server
echo ================================================
echo.
echo Port: 8000
echo URL: http://127.0.0.1:8000
echo.
echo Press CTRL+C to stop the server
echo.
echo ================================================
echo.

cd backend
uvicorn main:app --reload --port 8000
