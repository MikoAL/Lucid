@echo off
call conda activate Lucid

set UVICORN_CMD=uvicorn
set APP_MODULE=server_websockets:app
set RELOAD_OPTION=--reload

%UVICORN_CMD% %APP_MODULE% %RELOAD_OPTION%
