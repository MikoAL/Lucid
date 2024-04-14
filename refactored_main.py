import time
import sys
import httpx
import yaml
import os
import logging
from datetime import date
import asyncio
import json
import re
import numpy as np
import transformers
transformers.utils.logging.disable_default_handler

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%I:%M:%S %p')
#logging.disable()
# Get the absolute path of the script's directory
script_dir = os.path.dirname(os.path.realpath(__file__))
# Change the working directory to the script's directory
os.chdir(script_dir)


# ===== ===== ===== #
# Settings

# Reading from a YAML file
with open('settings.yaml', 'r') as file:
	settings = yaml.safe_load(file)

host = settings['host']
port = settings['port']
server = f'http://{host}:{port}'
small_lm_name = settings['small_lm_settings']['language_model']
small_lm_temperature = settings['small_lm_settings']['temperature']
small_lm_top_k = settings['small_lm_settings']['top_k']
small_lm_top_p = settings['small_lm_settings']['top_p']

device_for_tools = "cuda:1" #settings['device_for_tools']

prompt_path = r".\Prompts"

with open(f"{prompt_path}\Lucid_prompt_card.txt", 'r', encoding='utf-8') as f:
	Lucid_prompt_card = f.read()
with open(f"{prompt_path}\Lucid_example_dialogue.txt", 'r', encoding='utf-8') as f:
	Lucid_example_dialogue = f.read()

with open(f"{prompt_path}\council_example_prompt.txt", 'r', encoding='utf-8') as f:
	council_example_prompt = f.read()

# Load council members' data from JSON file
with open(f"{prompt_path}\Council_Members.json", 'r', encoding='utf-8') as f:
	AI_Council_data = json.load(f)
# ===== ===== ===== #
# Server Handler
class ServerHandler():
    def __init__(self, server):
        self.server = server
        self.read_mails = []
        self.unread_mails = []
    
    def check_mailbox(self)->None:
        new_mails = (httpx.get(f'{self.server}/mailbox')).json()
        if new_mails != []:
            self.unread_mails.extend(new_mails)
    
    def get_unread_mails(self)->list:
        self.check_mailbox()
        temp_unread_mails = self.unread_mails.copy()
        self.read_mails.extend(self.unread_mails)
        self.unread_mails = []
        return temp_unread_mails
    
    def send_discord_message(self, message):
        httpx.post(f'{self.server}/discord/send_message', json={'message': message})

# ===== ===== ===== #
# Chroma stuff
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer, CrossEncoder
cross_encoder = CrossEncoder("cross-encoder/stsb-distilroberta-base", device=device_for_tools)
sentence_transformer = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2', device=device_for_tools)
chromadb_client = chromadb.Client(Settings(anonymized_telemetry=False))
short_term_memory = chromadb_client.create_collection("short_term_memory")
short_term_memory_uid = 1

"""
This is what a Info Block should look like
{
  'object_type' : 'entity',
  'object_name' : 'Miko',
  'content' : 'Miko like Nintendo games.',
  'timestamp' : '2021-10-15 17:37:00',
  'vector': array([[-4.39221077e-02, -1.25277145e-02,  2.93133650e-02,]], dtype=float32),
}    
"""


# ===== ===== ===== #
# Lucid Agents
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, LocalAgent, GPTQConfig, Tool, pipeline
class LucidAgent(LocalAgent):
        def __init__(self, model, tokenizer, chat_prompt_template=None, run_prompt_template=None, additional_tools=None):
            
            
            super().__init__(model = model,
                             tokenizer = tokenizer,
                             chat_prompt_template = chat_prompt_template,
                             run_prompt_template = run_prompt_template,
                             additional_tools = additional_tools)

# ===== ===== ===== #
# Lucid Council

from transformers.tools.agents import resolve_tools, evaluate, get_tool_creation_code, StopSequenceCriteria
from transformers.generation import StoppingCriteriaList

class LucidCouncil(LocalAgent):
    def __init__(self, model, tokenizer, members: dict, additional_tools=None, council_example_prompt=council_example_prompt):
        self.members = members
        stop_conditions = ["\n\n", "=====", "System:"]
        #for member in self.members:
        #    stop_conditions.append(f"{member['name']}:")
        self.stop_conditions = stop_conditions
        self.chat_turn_counter = 0
        council_member_prompt = ""
        for member in self.members:
            council_member_prompt += f"[{member['name']}]\n- {member['personality_prompt']}\n\n"
        council_prompt_template = f"""\
Below are a series of dialogues between Lucid and her inner council.

Here are some information on Lucid:
{Lucid_prompt_card.strip()}

The council members are as follow:
{council_member_prompt.strip()}

The job of the council is to help Lucid come up with a series of simple commands in Python that will help her respond to situations.
To help Lucid come up with the best commands, each council member will discuss and give their opinion on the best way to solve the problem.
Also to help Lucid, Lucid has access to a set of tools. Each tool is a Python function and has a description explaining the task it performs, the inputs it expects and the outputs it returns.
Lucid will first explain the tools she will use to perform the task and for what reason, then write the code in Python.
Each instruction in Python should be a simple assignment. Lucid can print intermediate results if it makes sense to do so.

Tools:
<<all_tools>>

{council_example_prompt.strip()}

=====

"""

        super().__init__(model, tokenizer, chat_prompt_template=council_prompt_template, run_prompt_template=None, additional_tools=additional_tools)
        
    def generate_one(self, prompt, stop, max_new_tokens=200):
        encoded_inputs = self.tokenizer(prompt, return_tensors="pt").to(self._model_device)
        src_len = encoded_inputs["input_ids"].shape[1]
        stopping_criteria = StoppingCriteriaList([StopSequenceCriteria(stop, self.tokenizer)])
        outputs = self.model.generate(
            encoded_inputs["input_ids"], max_new_tokens=max_new_tokens, stopping_criteria=stopping_criteria
        )

        result = self.tokenizer.decode(outputs[0].tolist()[src_len:])
        # Inference API returns the stop sequence
        for stop_seq in stop:
            if result.endswith(stop_seq):
                result = result[: -len(stop_seq)]
        return result.strip()
    
    def format_prompt(self, chat_mode=False):
        # TODO: Actually implement the chat mode
        description = "\n".join([f"- {name}: {tool.description}" for name, tool in self.toolbox.items()])
        if chat_mode:
            if self.chat_history is None:
                prompt = self.chat_prompt_template.replace("<<all_tools>>", description) + "\n\n"
            else:
                prompt = self.chat_history + "\n\n"
            # prompt += CHAT_MESSAGE_PROMPT.replace("<<task>>", task)
        return prompt
    
    def start_new_chat(self, problem):
        self.prepare_for_new_chat()
        self.chat_turn_counter = 0
        prompt = self.format_prompt(chat_mode=True)
        self.chat_history = prompt + "System: "+ problem
    
    def add_system_message(self, message):
        logging.info(f"Adding system message: {message}")
        if self.chat_turn_counter != 0:
            self.chat_history += "\n\nSystem: "+ message
        else:
            self.start_new_chat(message)
            
    def chat(self, *, return_code=False, remote=False, **kwargs):
        """
        Sends a new request to the council in a chat. Will use the previous ones in its history.

        Args:
            task (`str`): The task to perform
            return_code (`bool`, *optional*, defaults to `False`):
                Whether to just return code and not evaluate it.
            remote (`bool`, *optional*, defaults to `False`):
                Whether or not to use remote tools (inference endpoints) instead of local ones.
            kwargs (additional keyword arguments, *optional*):
                Any keyword argument to send to the agent when evaluating the code.

        Example:

        ```py
        from transformers import HfAgent

        agent = HfAgent("https://api-inference.huggingface.co/models/bigcode/starcoder")
        agent.chat("Draw me a picture of rivers and lakes")

        agent.chat("Transform the picture so that there is a rock in there")
        ```
        """
        prompt = self.format_prompt(chat_mode=True)

        result = self.generate_one(prompt, stop=self.stop_conditions)
        self.chat_history = (prompt + result).strip()
        self.chat_turn_counter += 1
        code = self.clean_code_for_chat(result)

        self.log(f"==Response from the agent==\n{result}") 

        if code is not None:
            self.log(f"\n\n==Code generated by the agent==\n{code}")
            if not return_code:
                self.log("\n\n==Result==")
                self.cached_tools = resolve_tools(code, self.toolbox, remote=remote, cached_tools=self.cached_tools)
                self.chat_state.update(kwargs)
                return evaluate(code, self.cached_tools, self.chat_state, chat_mode=True)
            else:
                tool_code = get_tool_creation_code(code, self.toolbox, remote=remote)
                return f"{tool_code}\n{code}"
            

        
    def clean_code_for_chat(self, result):
        # This is my own version that will replace the one in Agent.py
        """Extracts the code section surrounded by ```python and ``` from a string."""
        start_marker = "```python"
        end_marker = "```"
        start_idx = result.find(start_marker)
        if start_idx == -1:
            return None  # No code section found
        start_idx += len(start_marker) + 1  # Move past the marker and newline
        end_idx = result.find(end_marker, start_idx)
        if end_idx == -1:
            return None  # No closing marker found
        code_section = result[start_idx:end_idx].strip()
        return code_section

        """ This is the old version of the code that I am replacing
        
        lines = result.split("\n")
        idx = 0
        while idx < len(lines) and not lines[idx].lstrip().startswith("```"):
            idx += 1
        explanation = "\n".join(lines[:idx]).strip()
        if idx == len(lines):
            return explanation, None

        idx += 1
        start_idx = idx
        while not lines[idx].lstrip().startswith("```"):
            idx += 1
        code = "\n".join(lines[start_idx:idx]).strip()

        return explanation, code"""
    def run(self):
        raise NotImplementedError("The council does not have a run method. It is only for chatting.")

# Council Tools
class send_discord_message(Tool):
    name = "send_discord_message"
    description = "Sends a message to the discord server"
    inputs = ["message"]
    outputs = []
    
    def __call__(self, message):
        server_handler.send_discord_message(message)

class recall_memory(Tool):
    name = "recall_memory"
    description = "Tries to find a related memory from the past"
    inputs = ["text"]
    outputs = ["memory"]
    
    def __call__(self, text):
        # TODO: Implement a memory system
        memory = "I don't have any memory of that."
        return memory

class save_information(Tool):
    name = "save_information"
    description = "Saves information to memory to be used later."
    inputs = ["information"]
    outputs = []
    
    def __call__(self, information):
        # TODO: Implement a memory system
        pass

class print_tool(Tool):
    name = "print_to_council"
    description = "Prints into the council chat as System."
    inputs = ["string"]
    outputs = ["text"]
    
    def __call__(self, text):
        global Lucid_council
        Lucid_council.add_system_message(f"[result of print_to_council() from python code] {text}")
        return text
        


# ===== ===== ===== #
# Load the model and tokenizer
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, LocalAgent, GPTQConfig, Tool, pipeline

gptq_config = GPTQConfig(bits=4, exllama_config={"version":2})
model = AutoModelForCausalLM.from_pretrained("TheBloke/Mistral-7B-Instruct-v0.2-GPTQ", device_map="cuda:0", quantization_config=gptq_config)
tokenizer = AutoTokenizer.from_pretrained("TheBloke/Mistral-7B-Instruct-v0.2-GPTQ")

server_handler = ServerHandler(server)
send_discord_message_tool = send_discord_message()
print_tool_tool = print_tool()


# Create the Lucid Council
Lucid_council = LucidCouncil(model, tokenizer, AI_Council_data, 
                             additional_tools=[send_discord_message_tool, print_tool_tool])
# Start the loop
last_mail = None
while True:
    new_mails = server_handler.get_unread_mails()
    if new_mails != []:
        logging.info(f"Got new mails: {new_mails}")
        for mail in new_mails:
            # Format the mail
            logging.info(f"Got mail: {mail}")
            match mail['type']:
                case "discord_message":
                    Lucid_council.add_system_message(f"[Discord Message from user {mail['source']}] {mail['content']}")
                    
                
    Lucid_council.chat()
    logging.info(f"{Lucid_council.chat_history}")
    time.sleep(0.2)