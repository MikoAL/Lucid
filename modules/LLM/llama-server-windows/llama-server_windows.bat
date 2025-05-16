@ECHO OFF
SET llama-server-path=C:\Users\Miko_AL\Desktop\Projects\Lucid\modules\LLM\llama-server-windows\llama-server.exe

SET model_path=C:\Users\Miko_AL\Desktop\Projects\Lucid\models\LLM\Qwen3-0.6B-Q8_0.gguf

%llama-server-path% -m %model_path% --port 8080