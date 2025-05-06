from ollama import Client
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from setting_loader import load_settings


class LMEngine():
    def __init__(self, service_type = "ollama", override_preset={}):
        self.service_type = service_type
        self.overrider_preset = override_preset
        self.settings = load_settings()
        
        
        if service_type == "ollama":
            self.ollama_init()
        else:
            ValueError(f"Unknow service_type: {service_type}")
            
    def ollama_init(self):    
        self.ollama_client = Client(host="http://localhost:11434")
        self.ollama_model = "qwen3:0.6b"
        
    
    def gen(self, prompt, max_tokens = 128, stop=[]):
        if self.service_type == "ollama":
            options = self.settings["preset"]
            for k, v in self.overrider_preset:
                if k in options:
                    options[k] = v
            options["stop"] = self.settings["instruct"]
            options["num_predict"]=max_tokens
            options["stop"] = list(set(stop).union(options["stop"]))
            response = self.ollama_client.generate(model=self.ollama_model, prompt= prompt, raw=True, options=options)
            print(response)
            return response['response']


if __name__ == "__main__":
    lm = LMEngine()
    #print("Started lm.")
    print(lm.gen())