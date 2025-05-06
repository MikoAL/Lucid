import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from setting_loader import load_settings

from LLM.inference import LMEngine

from transformers import AutoTokenizer

from pydantic import BaseModel

class MemoryAgent():
    def __init__(self, lm: LMEngine, path_to_lorebook: Path):
        self.lm = lm
        self.path_to_lorebook = path_to_lorebook
        pass
    
    def process_new_input(self, input_text):
        """1. Are there any info worth saving? Did we learn anything new?
            If yes, what is the info? Output it. Respond using JSON
        
        class Information(BaseModel):
            worth_saving: bool
            info: Optional[str] = None
        
        "format": {
            "type": "object",
            "properties": {
                "worth_saving": {
                    "type":"boolean"
                },
                
                "info": {
                    "type": "string"
                }
            "required": [
                "worth_saving"
            ]
        }
        
        response = chat(
            model = "qwen3:0.6b",
            format = Information.model_json_schema(),
            messages=[
                
            ])
            
            """
        pass
    
    def save_to_lorebook(self):
        pass


if __name__ == "__main__":
    lm = LMEngine()
    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B")
    print("Model loaded.")
    prompt = "Who are you?"
    messages = [
        {"role": "user", "content": prompt}
    ]
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=False # Switches between thinking and non-thinking modes. Default is True.
    )
    print(lm.gen(text))
