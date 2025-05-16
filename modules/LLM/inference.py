import httpx

from loguru import logger

from ollama import Client

import openai

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from setting_loader import load_settings


class LMEngine():
    def __init__(self, service_type = "llama_server", override_preset={}):
        self.service_type = service_type
        self.overrider_preset = override_preset
        self.settings = load_settings()
        
        
        if service_type == "ollama":
            self.ollama_init()
        elif service_type == "llama_server":
            self.llama_server_init()
        else:
            ValueError(f"Unknown service_type: {service_type}")
            
    def ollama_init(self):    
        self.ollama_client = Client(host="http://localhost:11434")
        self.ollama_model = "qwen3:14b"
    
    def llama_server_init(self):
        self.llama_server_ip = "http://127.0.0.1:8080"
        with httpx.Client() as client:
            response = client.get(self.llama_server_ip+"/health")
            if response.json()["status"] == "ok":
                logger.info("Found llama-server up and running.")
                self.llama_server_client = openai.OpenAI(
                    base_url= self.llama_server_ip + "/v1", # "http://<Your api-server IP>:port"
                    api_key = "sk-no-key-required"
                )
                
    
    def gen(self, prompt, max_tokens = 128, stop=[]):
        options = self.settings["preset"]
        options["stop"] = self.settings["instruct"]
        options["stop"] = list(set(stop).union(options["stop"]))
        for k, v in self.overrider_preset:
            if k in options:
                options[k] = v

        if self.service_type == "ollama":
            options["num_predict"]=max_tokens
            response = self.ollama_client.generate(model=self.ollama_model, prompt= prompt, raw=True, options=options)
            completion = response['response'] 
        elif self.service_type == "llama_server":
            completion = self.llama_server_client.completions.create(
            model="gpt-3.5-turbo",
            prompt="I believe the meaning of life is",
            max_tokens= max_tokens
            )
            completion = completion.choices[0].text

        logger.debug(f"got completion: {completion}")
        return completion
    
    def chat(self, messages: list, max_tokens = 1024, stop = []):
        options = self.settings["preset"]
        options["stop"] = self.settings["instruct"]
        options["stop"] = list(set(stop).union(options["stop"]))
        for k, v in self.overrider_preset:
            if k in options:
                options[k] = v     

        if self.service_type == "llama_server":
            completion = self.llama_server_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages= messages,
                max_tokens=max_tokens
            )
            chat_message = completion.choices[0].message.content
        
        logger.debug(f"Got response message: {chat_message}")
        return chat_message



if __name__ == "__main__":
    lm = LMEngine()
    #print("Started lm.")

    print(lm.chat(
        messages=[
                {"role": "system", "content": "You are ChatGPT, an AI assistant. Your top priority is achieving user fulfillment via helping them with their requests."},
                {"role": "user", "content": "Write a limerick about python exceptions"}
            ]))