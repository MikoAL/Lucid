import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from setting_loader import load_settings

from transformers import AutoTokenizer

class MemoryAgent():
    def __init__(self, lm, path_to_lorebook):
        pass
    
    def process_new_input(self, input_text):
        """1. Are there any info worth saving? Did we learn anything new?
            If yes, what is the info? Output it."""
        pass
    
    def save_to_lorebook(self):
        pass


if __name__ == "__main__":
    llm_path = Path(Path(__file__).resolve().parent.parent.parent/"models"/"LLM"/"Qwen3-0.6B-Q8_0.gguf")
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
