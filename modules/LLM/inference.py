from ollama import Client
from llama_cpp import Llama

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from setting_loader import load_settings


class LMEngine():
    def __init__(self, service_type = "llama_cpp", override_preset={}):
        self.service_type = service_type
        self.overrider_preset = override_preset
        self.settings = load_settings()
        
        
        if service_type == "ollama":
            self.ollama_init()
        elif service_type == "llama_cpp":
            self.llama_cpp_init()
        else:
            ValueError(f"Unknown service_type: {service_type}")
            
    def ollama_init(self):    
        self.ollama_client = Client(host="http://localhost:11434")
        self.ollama_model = "qwen3:14b"
    
    def llama_cpp_init(self):
        self.llama_cpp_model = "Qwen3-14B-Q4_K_M"
        self.llama_cpp_lm =  Llama(
            model_path=str(Path(__file__).resolve().parent.parent.parent/"models"/"LLM"/(self.llama_cpp_model+".gguf")),
            n_gpu_layers=-1
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
            print(response)
            return response['response']
        
        elif self.service_type == "llama_cpp":
            response = self.llama_cpp_lm(
                prompt=prompt,
                max_tokens=max_tokens,
                stop=options["stop"]
            )
            print(response)
            return response



if __name__ == "__main__":
    lm = LMEngine()
    #print("Started lm.")
    print(lm.gen("This is a story"))