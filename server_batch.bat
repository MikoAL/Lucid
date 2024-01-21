@echo off
call conda activate Lucid
start cmd /k uvicorn server:app --reload --port 8001
::timeout /t 1 /nobreak >nul
::start cmd /k python.exe client.py
::start cmd /k python.exe main.py
