@echo off
set SERVER_PATH=C:\Users\Miko_AL\Desktop\Projects\Lucid\modules\LLM\llama-server\llama-server.exe
set MODEL_PATH=C:\Users\Miko_AL\Desktop\Projects\Lucid\models\LLM\Qwen3-0.6B-Q8_0.gguf

"%SERVER_PATH%" -m "%MODEL_PATH%" -ngl 999 --port 8080
