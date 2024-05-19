import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

from transformers import CodeAgent, ReactCodeAgent, Tool
from transformers.agents import PythonInterpreterTool
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers import BitsAndBytesConfig
quant_config = BitsAndBytesConfig(load_in_4bit=True)
model = AutoModelForCausalLM.from_pretrained("unsloth/llama-3-8b-Instruct-bnb-4bit", device_map="cuda:0", quantization_config=quant_config)
tokenizer = AutoTokenizer.from_pretrained("unsloth/llama-3-8b-Instruct-bnb-4bit")
llm_engine_settings = {
    "model": model,
    "tokenizer": tokenizer,
    "device": "cuda:0",
}

class MemoryAgent():
    def __init__(self, model, tokenizer, device):
        self.memory = []
        self.model = model
        self.tokenizer = tokenizer
        self.device = device

    def llm_engine(self, messages, stop_sequences=["Task"]) -> str:
        inputs = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)
        encoded_inputs = self.tokenizer(inputs, return_tensors="pt").to(self.device)
        src_len = encoded_inputs["input_ids"].shape[1]
        # Generate the response
        outputs = self.model.generate(encoded_inputs["input_ids"],
                                tokenizer=tokenizer,
                                max_new_tokens=1024,
                                temperature=0.85,
                                top_k=50,
                                top_p=0.95,
                                do_sample=True,
                                pad_token_id=self.tokenizer.eos_token_id,
                                stop_strings=stop_sequences)
        # Decode the response
        return self.tokenizer.decode(outputs[0].tolist()[src_len:-1])

class return_answer(Tool):
    name = "return_answer"
    description = "Used to return the final answer of the task given."
    inputs = {
        "answer": {
            "type": "text",
            "description": "The answer of the task given.",
        },
    }
    output_type = "None"
    

    def forward(self, answer: str):
        print(f">> The Agent's answer is: {answer}")
    
return_answer_tool = return_answer()
agent = ReactCodeAgent(tools=[], llm_engine=llm_engine, add_base_tools=True)

agent.step()
    
class recall_memory(Tool):
    name = "recall_memory"
    description = "Tries to find a related memory from the past."
    inputs = {
        "query": {
            "type": "text",
            "description": "The query to search for in the memory.",
        },
        "number_of_results": {
            "type": "int",
            "description": "The number of results to return. Defaults to 1.",
        },
    }
    output_type = "text"
    

    def forward(self, query: str, number_of_results: int = 1):
        
        return 

#agent = ReactCodeAgent(tools=[PythonInterpreterTool()])
"""You are an agent designed to help Lucid with her memories. You are in charge of helping her recall past events and document current ones."""