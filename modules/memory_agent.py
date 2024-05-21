import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
import time
import numpy as np
import torch

import logging
from rich.logging import RichHandler
FORMAT = "%(message)s"
logging.basicConfig(
    level=logging.DEBUG, format=FORMAT, datefmt="[%X]", handlers=[RichHandler(rich_tracebacks=True,)]
)
logger = logging.getLogger("rich")
from transformers import CodeAgent, ReactCodeAgent, Tool
from transformers.agents import PythonInterpreterTool
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers.agents.prompts import DEFAULT_REACT_CODE_SYSTEM_PROMPT

from transformers import BitsAndBytesConfig
quant_config = BitsAndBytesConfig(load_in_4bit=True)
model = AutoModelForCausalLM.from_pretrained("unsloth/llama-3-8b-Instruct-bnb-4bit", device_map="cuda:0", quantization_config=quant_config)
tokenizer = AutoTokenizer.from_pretrained("unsloth/llama-3-8b-Instruct-bnb-4bit")
llm_engine_settings = {
    "model": model,
    "tokenizer": tokenizer,
    "device": "cuda:0",
}
MY_REACT_CODE_SYSTEM_PROMPT = """You are an AI assistant designed to help Lucid with memory recall and documentation, especially related to her conversations and interactions with others.

Key Concepts:

    - Unprocessed Info Block: A piece of information from a conversation that is not yet processed.

    - Info Block: A piece of information from a conversation that is stored in the memory.

    - Working Memory: A list that stores the information that is either new or currently relevant from conversations, the list is updated frequently and has a limited capacity.

    - Short-term Memory: A vector store that stores the most recent conversation information.

    - Long-term Memory: A vector store that stores all past conversation information.

Information from conversations will first be stored in both the working memory and short-term memory. If the information is important and needs to be stored for a longer period, it will be moved to long-term memory.

Your primary tasks include:

1. Storing current conversation information into working memory for quick access.

2. Moving relevant conversation information from short-term memory to long-term memory for future reference.

3. Searching through Lucid's long-term memory and recollections of past conversations to fetch information she might need right now into working memory.

4. Documenting and storing new memories and experiences from Lucid's conversations and interactions with others.

5. Providing insights and context based on the available conversation information in Lucid's working memory and long-term memory.

You have access to the following tools:
<<tool_descriptions>>

To assist Lucid, you must plan forward to proceed in a series of steps, in a cycle of 'Thought:', 'Code:', and 'Observation:' sequences.

At each step, in the 'Thought:' sequence, you should first explain your reasoning towards assisting Lucid, then the tools that you want to use.
Then in the 'Code:' sequence, you should write the code in simple Python. The code sequence must end with '/End code' sequence.
During each intermediate step, you can use 'print()' to save whatever important information you will then need.
These print outputs will then be available in the 'Observation:' field, for using this information as input for the next step.

In the end you have to return insights or information using the `send_to_Lucid` tool when Lucid needs to reference past events or specific knowledge.

The tasks will contain conversational snippets with multiple speakers in the following format:

Task: 
Person1: ...
Person2: ...
Person1: ...
Person3: ...

Here are some examples:

---
Task:
Miko: My favorite book is Harry Potter and the Sorcerer's Stone. What's yours, Lucid?
Lucid: I really enjoyed reading The Kite Runner by Khaled Hosseini.

Thought: I should document this conversation about favorite books between Lucid and Miko for future reference.
Code:
```py
conversation_memory = "Miko said his favorite book is Harry Potter and the Sorcerer's Stone. Lucid said her favorite book is The Kite Runner by Khaled Hosseini."
save_memory(memory=conversation_memory)
```<end_code>

---
Task: 
Lucid: Do you remember what Miko said his favorite book was? I want to get it for his birthday.

Thought: To recall the memory of Miko's favorite book from a previous conversation, I will use the `recall_memory` tool.
Code:
```py
memory = recall_memory(query="Miko's favorite book", number_of_results=1)
print(memory)
```<end_code>
Observation: "Miko said his favorite book is Harry Potter and the Sorcerer's Stone."

Thought: I will send this information to Lucid to help her get the right book for Miko's birthday.
Code:
```py
send_to_Lucid(text=memory)
```<end_code>

---
Task:
Sarah: I'm going hiking at the state park on Saturday. Want to join me?
Lucid: That sounds fun! I'd love to go hiking with you. 

Thought: I should document this conversation about weekend plans between Lucid and Sarah.
Code:
```py
conversation_memory = "Sarah invited Lucid to go hiking with her at the state park on Saturday. Lucid accepted the invitation."
save_memory(memory=conversation_memory)
```<end_code>

---
Task: 
Lucid: When did Sarah say we were going hiking this weekend?
Alex: I think Sarah mentioned going hiking on Saturday.

Thought: To remind Lucid of the details from her previous conversation with Sarah about hiking plans, I will use the `recall_memory` tool.
Code:
```py
memory = recall_memory(query="Lucid's hiking plans with Sarah", number_of_results=1)
print(memory)
```<end_code>
Observation: "Sarah invited Lucid to go hiking with her at the state park on Saturday. Lucid accepted the invitation."

Thought: I will send this information to Lucid to remind her of when she planned the hike with Sarah.
Code:
```py
send_to_Lucid(text=memory)
```<end_code>

---
Task:
Jamie: It's so nice out today!
Sam: Yes, the weather is beautiful.

Thought: This conversation does not contain any information that needs to be stored or referenced later. No action is required.
Code:
```py
# No code needed
```<end_code>

---

Always provide a 'Thought:' and a 'Code:\n```py' sequence ending with '```<end_code>' sequence. You MUST provide at least the 'Code:' sequence to move forward, even if no action is required.

Remember to not perform too many operations in a single code block! You should split the task into intermediate code blocks.
Print results at the end of each step to save the intermediate results. Then use send_to_Lucid() to provide insights or information to Lucid when she needs to reference past events or specific knowledge.

Remember to make sure that variables you use are all defined.
DO NOT pass the arguments as a dict as in 'answer = recall_memory({'query': "Miko's favorite book", 'number_of_results': 1})', but use the arguments directly as in 'answer = recall_memory(query="Miko's favorite book", number_of_results=1)'.

Now Begin!
"""

class Memory():
    """Key Concepts:
    - Unprocessed Info Block: A piece of information that is not yet processed.
    - Info Block: A piece of information that is stored in the memory.
    - Short Term Memory: A vector store that stores the most recent information.
    - Working Memory: A vector store that stores the information that is currently being used.
    - Long Term Memory: A vector store that stores all past information.
    """
    
    def __init__(self, model=None, tokenizer=None, device_for_tools="cuda:0"):
        import chromadb
        from chromadb.config import Settings
        from sentence_transformers import SentenceTransformer, CrossEncoder
        self.cross_encoder = CrossEncoder("cross-encoder/stsb-distilroberta-base", device=device_for_tools)
        self.sentence_transformer = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2', device=device_for_tools)
        self.chromadb_client = chromadb.Client(Settings(anonymized_telemetry=False))
        self.short_term_memory_chroma_collection = self.chromadb_client.create_collection("short_term_memory")
        self.short_term_memory_uid = 1
        self.model = model
        self.tokenizer = tokenizer
        if model is None:
            quant_config = BitsAndBytesConfig(load_in_4bit=True)
            self.model = AutoModelForCausalLM.from_pretrained("unsloth/llama-3-8b-Instruct-bnb-4bit", device_map="cuda:0", quantization_config=quant_config)
            tokenizer = AutoTokenizer.from_pretrained("unsloth/llama-3-8b-Instruct-bnb-4bit")
        elif tokenizer is None:
            raise ValueError("A model was provided but no tokenizer was provided. Please provide a tokenizer for the model.")
        self.working_memory = []
    
    def check_for_similar_memories(self, unprocessed_info_block: dict, threshold: float = 0.8) -> list: # NOTE: This is an arbitrary threshold
        """The function checks if a simular info block is already in the memory. If it is, it returns the ID of the similar info block.
        If not, it returns an empty list."""
        query_result = self.short_term_memory_chroma_collection.query(
            query_embeddings=[unprocessed_info_block['vector']],    
            n_results=4
        )
        sentence_combinations = [[unprocessed_info_block['content'], sentence] for sentence in query_result["documents"]]
        scores = self.cross_encoder.predict(sentence_combinations)
        ranked_indices = np.argsort(scores)[::-1]
        # Get the original IDs for scores above the threshold
        high_score_ids = [query_result["ids"][i] for i in ranked_indices if scores[i] >= threshold]
        return high_score_ids
            
    def process_unprocessed_info_block(self, unprocessed_info_block: dict):
        # TODO: Implement a processing for the unprocessed info block
        pass    
    
    def without_keys(d, keys):
        """A utility function to remove certain keys from a dictionary."""
        return {k: v for k, v in d.items() if k not in keys}

    
    def display_working_memory(self) -> str:
        """This function returns a string representation of the working memory."""
        if len(self.working_memory) == 0:
            return "\n# Working Memory\nEmpty"
        else:
            working_memory_str = "\n# Working Memory\n"
            for i in range(len(self.working_memory)):
                working_memory_str += f"{i+1}. {self.working_memory[i]['content']}\n"
            return working_memory_str
    
    def add_working_memory(self, information: str) -> None:
        """This function adds information to the working memory. It also checks if the information is already in the memory."""
        unprocessed_info_block = {
            'content' : information,
            'timestamp' : time.time(),
            'vector': self.sentence_transformer.encode(information)
        }
        doubles = self.check_for_similar_memories(unprocessed_info_block)
        if len(doubles) == 0:
            self.working_memory.append(unprocessed_info_block)
        else:
            pass
    def delete_working_memory(self, line_number:int) -> None:
        """Deleting is kind of misleading. It actually moves the memory to short term memory. 
        But calling it moving to short term memory is also confusing."""
        moved_memory = self.working_memory.pop(line_number-1)
        self.add_to_short_term_memory(moved_memory)
        
    def clear_working_memory(self):
        """This function clears the working memory."""
        for i in range(len(self.working_memory)):
            self.delete_working_memory(1)
    
    def add_to_short_term_memory(self, unprocessed_info_block: dict):
        """This function processes the unprocessed info block and adds it to the short term memory."""
        info_block = self.process_unprocessed_info_block(unprocessed_info_block)
        info_block_no_vector = self.without_keys(info_block, ['vector'])
        self.short_term_memory_chroma_collection.add(
            ids=[self.short_term_memory_uid],
            documents=[info_block],
            embeddings=[info_block['vector']],
            metadata=[info_block_no_vector],
        )
        self.short_term_memory_uid += 1
        

class MemoryAgent():
    def __init__(self, model, tokenizer, device, init_agent=True):
        self.memory = []
        self.model = model
        self.tokenizer = tokenizer
        self.device = device
        if init_agent:
            self.init_agent()

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
    
    def init_agent(self):
        #self.memory = Memory()
        self.agent = ReactCodeAgent(tools=[], llm_engine=self.llm_engine, add_base_tools=True, system_prompt=MY_REACT_CODE_SYSTEM_PROMPT)
        logger.info("Memory Agent initialized.")
        logger.debug(f"""\
Memory Agent Information:
>> System Prompt: {self.agent.system_prompt_template}
>> Tools: {self.agent._toolbox.show_tool_descriptions()}""")
    
    def run_agent(self, messages: dict):
        conversation_string = ""
        for i in messages:
            if i["role"].lower() == "user":
                conversation_string += f"Miko: {i['content']}\n"
            elif i["role"].lower() == "system":
                conversation_string += f"System: {i['content']}\n"
            elif i["role"].lower() == "assistant":
                conversation_string += f"Assistant: {i['content']}\n"
            else:
                conversation_string += f"{i["role"]}: {i['content']}\n"
        self.agent.run("\n"+conversation_string)

        



    
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

class save_memory(Tool):
    name = "save_memory"
    description = "Saves a memory for future reference."
    inputs = {
        "memory": {
            "type": "text",
            "description": "The memory to save.",
        },
    }
    output_type = "None"
    

    def forward(self, memory: str):
        print(f">> The memory has been saved: {memory}")

class send_to_Lucid(Tool):
    name = "send_to_Lucid"
    description = "Sends text to Lucid."
    inputs = {
        "text": {
            "type": "text",
            "description": "The text containing information you deem helpful for Lucid to know.",
        },
    }
    output_type = "None"
    def forward(self, text: str):
        print(f">> The following text has been sent to Lucid: {text}")

#agent = ReactCodeAgent(tools=[PythonInterpreterTool()])
"""You are an AI assistant designed to help Lucid with memory recall and documentation.

Key Concepts:
    - Unprocessed Info Block: A piece of information that is not yet processed.
    - Info Block: A piece of information that is stored in the memory.
    - Working Memory: A list that stores the information that is either new or currently relevant, the list is updated frequently and has a limited capacity.
    - Short-term Memory: A vector store that stores the most recent information.
    - Long-term Memory: A vector store that stores all past information.

Information will first be stored in both the working memory and short-term memory. If the information is important and needs to be stored for a longer period, it will be moved to long-term memory.
    
Your primary tasks include:

1. Storing current information into working memory for quick access.
2. Moving relevant information from short-term memory to long-term memory for future reference.
3. Searching through Lucid's long-term memory and recollections to fetch information she might need right now into working memory.
4. Documenting and storing new memories and experiences from what Lucid has experienced.
5. Providing insights and context based on the available information in Lucid's working memory and long-term memory.

You have access to tools that allow you to search through Lucid's memory bank and return relevant results. You can also use your natural language processing capabilities to understand and document new information shared by Lucid.

Your goal is to be a helpful companion for Lucid, assisting her in recalling past events, storing new memories, and providing insights based on the available information. You should engage in a natural conversation with Lucid, asking for clarification or additional details when needed.

Feel free to ask Lucid for more context or information if you need it to better understand and assist with her memory-related tasks."""

