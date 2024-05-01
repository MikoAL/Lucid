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

#os.environ['TRANSFORMERS_OFFLINE']="1"

import transformers
import rich
import websockets
transformers.utils.logging.disable_default_handler()
from rich.logging import RichHandler
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%I:%M:%S %p', handlers=[RichHandler(rich_tracebacks=True)])
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

"""
small_lm_name = settings['small_lm_settings']['language_model']
small_lm_temperature = settings['small_lm_settings']['temperature']
small_lm_top_k = settings['small_lm_settings']['top_k']
small_lm_top_p = settings['small_lm_settings']['top_p']
"""
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
    def __init__(self, host, port):
        self.uri = f"ws://{host}:{port}/ws/main_script"
        self.server_websocket = None
        self.read_mails = []
        self.unread_mails = []

    async def connect(self):
        self.server_websocket = await websockets.connect(self.uri)
        await self.send_information({"type": "log", "content": "main_script connected?"})
    
    async def send_information(self, information: dict):
        await self.server_websocket.send(json.dumps(information))
        await asyncio.sleep(0.1)
    
    async def send_discord_message(self, message: str):
        await self.send_information({"type": "Lucid_output", "output_type":"discord_message","content": message})
    
    def get_unread_mails(self)->list:
        temp_unread_mails = self.unread_mails.copy()
        self.read_mails.extend(self.unread_mails)
        self.unread_mails = []
        return temp_unread_mails
    

# ===== ===== ===== #
# Chroma stuff

"""

This is what a Info Block should look like
{
  'object_type' : 'entity',
  'object_name' : 'Miko',
  'content' : 'Miko like Nintendo games.',
  'timestamp' : a float number,
  'vector': array([[-4.39221077e-02, -1.25277145e-02,  2.93133650e-02,]], dtype=float32),
}

This is what an unprocessed Info Block should look like
{
    'content' : 'Miko like Nintendo games.',
    'timestamp' : a float number,
    'vector': array([[-4.39221077e-02, -1.25277145e-02,  2.93133650e-02,]], dtype=float32),
}    
"""

class Memory():
    
    def __init__(self, device_for_tools=device_for_tools):
        import chromadb
        from chromadb.config import Settings
        from sentence_transformers import SentenceTransformer, CrossEncoder
        self.cross_encoder = CrossEncoder("cross-encoder/stsb-distilroberta-base", device=device_for_tools)
        self.sentence_transformer = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2', device=device_for_tools)
        self.chromadb_client = chromadb.Client(Settings(anonymized_telemetry=False))
        self.short_term_memory_chroma_collection = self.chromadb_client.create_collection("short_term_memory")
        self.short_term_memory_uid = 1

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
        return {k: v for k, v in d.items() if k not in keys}

    
    def display_working_memory(self) -> str:
        if len(self.working_memory) == 0:
            return "\n# Working Memory\nEmpty"
        else:
            working_memory_str = "\n# Working Memory\n"
            for i in range(len(self.working_memory)):
                working_memory_str += f"{i+1}. {self.working_memory[i]['content']}\n"
            return working_memory_str
    
    def add_working_memory(self, information: str) -> None:
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
        for i in range(len(self.working_memory)):
            self.delete_working_memory(1)
    
    def add_to_short_term_memory(self, unprocessed_info_block: dict):
        info_block = self.process_unprocessed_info_block(unprocessed_info_block)
        info_block_no_vector = self.without_keys(info_block, ['vector'])
        self.short_term_memory_chroma_collection.add(
            ids=[self.short_term_memory_uid],
            documents=[info_block],
            embeddings=[info_block['vector']],
            metadata=[info_block_no_vector],
        )
        self.short_term_memory_uid += 1
        
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
import transformers.tools.agents
from transformers.generation import StoppingCriteriaList


# We do this so that the default tools are not initialized
transformers.tools.agents._tools_are_initialized = True

    
def select(prompt, options, model, tokenizer, does_the_model_add_a_token_before_generating=True):
    if not options:
        return None  # Handle the case of empty options list
    #options = [option.strip() for option in options]
    
    if does_the_model_add_a_token_before_generating:
        tokenized_options = [tokenizer(option, return_tensors="pt").to("cuda:0")["input_ids"].tolist()[0][1:] for option in options]
    else:
        tokenized_options = [tokenizer(option, return_tensors="pt").to("cuda:0")["input_ids"].tolist()[0] for option in options]
    full_tokenized_options = tokenized_options.copy()
    #print(tokenized_options)
    round_number = 0
    answer = []
    while len(tokenized_options) > 1:  # Use > instead of != to ensure termination
        round_number += 1
        #print(f"round number: {round_number}")
        #print(f"tokenized options: {tokenized_options}")
        all_first_tokens = [option[0] for option in tokenized_options]
        #print(f"all first tokens: {all_first_tokens}")
        tokens_to_options = {}
        for i in range(len(all_first_tokens)):
            if all_first_tokens[i] not in tokens_to_options:
                tokens_to_options[all_first_tokens[i]] = [tokenized_options[i]]
            else:
                tokens_to_options[all_first_tokens[i]].append(tokenized_options[i])
        logit_bias = {}
        for tokens_for_check in tokens_to_options:

            logit_bias[tuple([tokens_for_check])] = 95.0
        encoded_inputs = tokenizer(prompt, return_tensors="pt").to("cuda:0")
        src_len = encoded_inputs["input_ids"].shape[1]
        #print(logit_bias)
        response = model.generate(
            encoded_inputs["input_ids"],
            max_new_tokens=3,
            temperature=0.0,
            sequence_bias=logit_bias,
            renormalize_logits = True,
            output_scores = True,
        )
        #print(f"response: {response.tolist()}\nend of response")
        response_token = response[0].tolist()[src_len:][0]
        response_word = tokenizer.decode(response_token)
        #print(f"response word: {response_word}")
        prompt += response_word
        answer.append(response_token)
        #print(f"checking if {response_token} is in {tokens_to_options.keys()}")
        if response_token in tokens_to_options.keys():
            for i in tokens_to_options[response_token]:
                #print(f"all options: {i}")
                if len(i) == 0:
                    break
            tokenized_options = [i[1:] for i in tokens_to_options[response_token]]
            #print(f"tokenized options: {tokenized_options}")


        else:
            # Handle the case where the response token is not found among the options
            break  # Exit the loop to avoid potential infinite loop
        # decode the final tokenized answer
    for i in range(len(full_tokenized_options)):
        if full_tokenized_options[i][:len(answer)] == answer:
            answer_idx = i
            break
    return options[answer_idx]

class LucidCouncil(LocalAgent):
    def __init__(self, model, tokenizer, members: dict, additional_tools=None, council_example_prompt=council_example_prompt):
        self.members = members
        self.tokenizer = tokenizer
        stop_conditions = ["\n\n", "=====", "System:", "Miko:", "```md\n# Working Memory", "<|im_start|>", "<|im_end|>","<|endoftext|>","<|end_of_text|>","<|eot_id|>"]
        #for member in self.members:
        #    stop_conditions.append(f"{member['name']}:")
        self.stop_conditions = stop_conditions
        self.chat_turn_counter = 0
        council_member_prompt = ""
        for member in self.members:
            council_member_prompt += f"[{member['name']}]\n- {member['personality_prompt']}\n\n"
            
        the_word_summary_in_currly_brackets = "{summary}"
        council_system_prompt_template = f"""\
Below are a series of example dialogues between Lucid and her inner council.
All dialogues are in English.
Always ensure the conversation is moving forward.

Here are some information on Lucid:
{Lucid_prompt_card.strip()}

The council's job is to guide Lucid in breaking down a complex problem into steps and developing a Python program to solve it. This will involve:

1. Multiple viewpoints/approaches from the council members
2. A step-by-step reasoning process shared by Lucid
3. Sharing and critiquing each step by the council  
4. Willingness by Lucid to re-evaluate and course-correct her logic
5. Iterating until a consensus emerges on the best solution

Lucid has access to a set of tools which are Python functions with descriptions of their inputs, outputs, and purposes. To tackle the problem:

1. Lucid will first explain which tools she plans to use and why
2. She will then write Python code with simple assignments for each step
3. Lucid can print intermediate results as needed
4. Lucid will share her thinking process step-by-step
5. The council members will evaluate and critique each step
6. If flaws are identified, Lucid acknowledges and restarts that line of thinking
7. This process continues, building on each other's ideas
8. Until all agree Lucid's Python program is the most sound solution

Lucid will only interact with the outside world through her available tool functions written in Python. 

Lucid will only receive information about the external world from instructions/context provided by "System".

Lucid can only talk to members in the current session.

Lucid can only use the tools available to her in the current session.

Unless within a Python code block, Lucid will communicate only in plain text within the council chat.

All text in the council chat is considered part of the conversation, and will all be from Lucid, council members or System with no exceptions.

Example of a council session:

System: [Discord Message from user miko_al] Lucid, can you recommend some healthy snack ideas?

Lucid: Miko has requested healthy snack recommendations. Let's discuss how to approach this, council.  

Lumi: We could use the `web_search` tool to find reputable sources on nutritious snack options, then summarize the key points.

Reverie: Personalizing the recommendations based on Miko's potential preferences or dietary needs would make them more actionable.

Lucid: Those are excellent suggestions. I will query trusted sources for healthy snack ideas, summarize the findings, and tailor the recommendations for Miko if possible. Here is my plan:

```python
# Ask Miko about dietary preferences/restrictions
send_discord_message(message="Do you have any specific dietary needs I should consider for the snack recommendations?")

# Search Google for reliable healthy snack information
snack_info = web_search(query="healthy snack ideas", num_results=5)

# Summarize key points from search results
summary = summarize(snack_info)
```

Lucid: Now, Let's wait for Miko's response before proceeding with the personalized recommendations.

System: [Discord Message from user miko_al] I don't have any dietary restrictions. Just looking for some tasty but nutritious snack options!

Lumi: Since Miko doesn't have dietary restrictions, we can proceed with the summary from the search results.

System: [Web Search Results]
1. 30 Healthy Snack Ideas - EatingWell
Fruit and veggie snacks: Apple with peanut butter, carrot sticks with hummus, banana with almond butter, cucumber slices with tzatziki dip...
2. 50 Super Healthy Snack Ideas - Cooking Light
Nuts and seeds: Handful of almonds, pumpkin seeds, walnuts. Edamame with sea salt. Energy balls made with oats, nut butter and dried fruit...
3. Healthy Snacks for Weight Loss - WebMD
Greek yogurt with berries, hard boiled eggs, avocado toast on whole grain bread, dark chocolate and nuts, celery with cream cheese...
4. Nutritious Snack Recipes - Mayo Clinic
Baked apple chips, kale chips, energy bites with oats and peanut butter, roasted chickpeas, cottage cheese with fruit...
5.Healthy Office Snacks - Fitbit Blog
Fresh veggies like cherry tomatoes, snap peas with ranch. Whole grain crackers with turkey and cheese. Protein smoothie with greek yogurt and fruit...

Lucid: Wonderful, these search results provide a diverse array of healthy snack ideas from reputable sources. Let me summarize the key points and send it to Miko.

```python
summary = "Here are some tasty and nutritious snack ideas:\n1. Fresh fruits and veggies like apples, bananas, carrot/cucumber sticks with dips like nut butters, hummus, tzatziki\n2. Nuts, seeds, edamame for protein and healthy fats\n3. Greek yogurt, cottage cheese paired with fruit or a bit of honey\n4. Whole grain crackers or bread with nut butters, cheese, turkey slices\n5. Energy bites made with oats, nut butters, dried fruit\n6. Air-fried veggie chips like kale chips or baked apple chips\n7. Hard boiled eggs for a protein boost\n8. A small amount of dark chocolate"

send_discord_message(message=f"Here are some tasty and nutritious snack ideas for you:\n{the_word_summary_in_currly_brackets}")
```

Lumi: Looks good! The summary is concise and covers a variety of snack options.
"""
        Lucid_council_user_prompt = f"""\
This session's members:
{council_member_prompt.strip()}

This session's tools:
<<all_tools>>
"""
        prompt_as_messages= [
            {"role":"system", "content":council_system_prompt_template.strip()},
            {"role":"user", "content":Lucid_council_user_prompt.strip()}
        ]
        Lucid_council_prompt = (self.tokenizer.apply_chat_template(prompt_as_messages, tokenize=False, add_generation_prompt=True)).strip()
        super().__init__(model, tokenizer, chat_prompt_template=Lucid_council_prompt,run_prompt_template=None, additional_tools=additional_tools)
        
    def generate_one(self, prompt, stop, max_new_tokens=2048, temperature=0.4):
        
        encoded_inputs = self.tokenizer(prompt, return_tensors="pt").to(self._model_device)
        src_len = encoded_inputs["input_ids"].shape[1]
        stopping_criteria = StoppingCriteriaList([StopSequenceCriteria(stop, self.tokenizer)])
        outputs = self.model.generate(
            encoded_inputs["input_ids"],
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            stopping_criteria=stopping_criteria,
            do_sample=True,
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
        """This starts a new session of chat with the council. It will start with Lucid stating the problem."""
        self.prepare_for_new_chat()
        self.chat_turn_counter = 0
        prompt = self.format_prompt(chat_mode=True)
        self.chat_history = prompt + "Lucid: "+ problem
    
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
        logging.info(f"Prompt: {prompt}\n<END OF PROMPT>")

        
        # Make sure the first few generated tokens are correct
        acceptable_strings = ["Lucid: ", "```python"]
        for name in self.members:
            acceptable_strings.append(f"{name['name']}: ")
        
        print(f"Acceptable strings: {acceptable_strings}")

        selected_word = select(prompt, acceptable_strings, self.model, self.tokenizer)

        if selected_word == "```python":
            prompt += selected_word + "\n"
            result = self.generate_one(prompt, stop=["```"], max_new_tokens=2048)
            explanation, code = self.clean_code_for_chat(selected_word+"\n"+result)
        else:
            prompt += selected_word
            result = self.generate_one(prompt, stop=self.stop_conditions)
            code = None
        self.chat_history = (prompt + result).strip()
        self.chat_turn_counter += 1
        

        logging.info(f"Result: {prompt}[bold orange3]{result}\n<END OF RESULT>")

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
        """Extracts the explanation and code sections from a string."""
        start_marker = "```python"
        end_marker = "```"
        
        # Find the start and end indices of the code section
        start_idx = result.find(start_marker)
        if start_idx == -1:
            return None, None  # No code section found
        start_idx += len(start_marker) + 1  # Move past the marker and newline
        end_idx = result.find(end_marker, start_idx)
        if end_idx == -1:
            return None, None  # No closing marker found
        
        # Extract the code section
        code_section = result[start_idx:end_idx].strip()
        
        # Extract the explanation section
        explanation_end_idx = result.rfind("\n", 0, start_idx)
        explanation = result[:explanation_end_idx].strip()
        
        return explanation, code_section

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
    description = "Sends a message to the discord server. Takes a string as input. Does not return anything."
    inputs = ["text"]
    outputs = []
    
    def __call__(self, message):
        global server_commands
        logging.info(f"Sending message to discord: {message}")
        server_commands.append({"command_type": "send_discord_message", "content": message})

class recall_memory(Tool):
    name = "recall_memory"
    description = "Tries to find a related memory from the past"
    inputs = ["text"]
    outputs = ["text"]
    
    def __call__(self, text):
        # TODO: Implement a memory system
        memory = "I don't have any memory of that."
        return memory

class save_information(Tool):
    name = "save_information"
    description = "Saves information to memory to be used later."
    inputs = ["text"]
    outputs = []
    
    def __call__(self, information):
        # TODO: Implement a memory system
        pass

class write_to_working_memory(Tool):
    name = "write_to_working_memory"
    description = "Writes information to working_memory to be used later. Takes a string as input."
    inputs = ["text"]
    outputs = []
    
    def __call__(self, information):
        Lucid_memory.add_working_memory(information)
        pass

class print_to_council(Tool):
    name = "print_to_council"
    description = "Prints into the council chat as System. Takes a string as input and returns it as output."
    inputs = ["text"]
    outputs = ["text"]
    
    def __call__(self, text):
        Lucid_council.add_system_message(f"[result of print_to_council() from python code] {text}")
        return text

class print_working_memory(Tool):
    name = "print_working_memory"
    description = "Prints the current working memory into the council chat. Takes no inputs."
    inputs = []
    outputs = ["text"]
    
    def __call__(self):
        Lucid_council.add_system_message(f"[result of print_working_memory() from python code] {Lucid_memory.display_working_memory()}")
        return Lucid_memory.display_working_memory()

class web_search(Tool):
    name = "web_search"
    description = "Searches the web for information. Takes a query and returns the top results."
    inputs = ["text"]
    outputs = ["text"]
    
    def __call__(self, query, num_results=5): 
        pass
# ===== ===== ===== #
# Load the model and tokenizer
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, LocalAgent, GPTQConfig, BitsAndBytesConfig, Tool, pipeline

"""
gptq_config = GPTQConfig(bits=4, exllama_config={"version":2})
model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen1.5-14B-Chat-GPTQ-Int4", device_map="cuda:0", quantization_config=gptq_config)
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen1.5-14B-Chat-GPTQ-Int4")
"""

bnb_config = BitsAndBytesConfig(load_in_4bit=True)
model = AutoModelForCausalLM.from_pretrained("unsloth/llama-3-8b-Instruct-bnb-4bit", device_map="cuda:0", quantization_config=bnb_config)
tokenizer = AutoTokenizer.from_pretrained("unsloth/llama-3-8b-Instruct-bnb-4bit")
tokenizer_with_prefix_space = AutoTokenizer.from_pretrained("unsloth/llama-3-8b-Instruct-bnb-4bit", add_prefix_space=True)
"""
gptq_config = GPTQConfig(bits=8, exllama_config={"version":1})
model = AutoModelForCausalLM.from_pretrained("astronomer/Llama-3-8B-Instruct-GPTQ-8-Bit", device_map="cuda:0", quantization_config=gptq_config)
tokenizer = AutoTokenizer.from_pretrained("astronomer/Llama-3-8B-Instruct-GPTQ-8-Bit")
#model=model.bfloat16()
"""
Lucid_memory = Memory()

send_discord_message_tool = send_discord_message()
print_to_council_tool = print_to_council()
print_working_memory_tool = print_working_memory()

# Create the Lucid Council
Lucid_council = LucidCouncil(model, tokenizer, AI_Council_data, 
                             additional_tools=[
                                 send_discord_message_tool,
                                 print_to_council_tool,
                                 print_working_memory_tool,
                                 ])

server_handler = ServerHandler(host=host, port=port)
server_commands = []

async def passive_memory_documentation():
    global Lucid_memory
    while True:
        pass

async def Lucid_logic():
    global server_handler, Lucid_council, Lucid_memory
    last_mail = None
    last_get_mail_time = 0
    while True:
        if time.time()-last_get_mail_time >= 0.5:
            last_get_mail_time = time.time()
            new_mails = server_handler.get_unread_mails()
        if new_mails != []:
            for mail in new_mails:
                # Format the mail
                match mail['type']:
                    case "discord_user_message":
                        Lucid_council.add_system_message(f"[Discord Message from user {mail['source']}] {mail['content']}")
        else:
            if Lucid_council.chat_history is None:
                Lucid_council.start_new_chat("We currently have nothing to discuss, what should we do in the meantime?")
        #logging.info(f"Chatting with the council")
        Lucid_council.chat()
        logging.info(f"{Lucid_council.chat_history}")
        await asyncio.sleep(0.1)

async def server_logic():
    global server_handler
    global server_commands
    while True:
        logging.info(f"Server commands: {server_commands}")
        if server_commands == []:
            server_commands.append({"type": "command", "command_type":"collect_mailbox"})
        current_command = server_commands.pop(0)
        
        match current_command['command_type']:
            case "collect_mailbox":
                logging.info(f"Collecting mailbox")
                await server_handler.send_information({"type": "command", "command_type":"collect_mailbox"})
                logging.info(f"Sent command to collect mailbox, now waiting for response.")
                new_mails = await server_handler.server_websocket.recv()
                logging.info(f"Got response from server: {new_mails}")
                new_mails = json.loads(new_mails)
                logging.info(f"Got: {new_mails}")
                if new_mails != []:
                    logging.info(f"Got new mails: {new_mails}")
                    server_handler.unread_mails.extend(new_mails)
            
            case "send_discord_message":
                await server_handler.send_discord_message(current_command['content'])
        await asyncio.sleep(0.1)  
        

async def main():
    global server_handler, Lucid_council, Lucid_memory
    # Start the loop

    await server_handler.connect()
    
    Lucid_council.start_new_chat("Miko has asked us what tools he should implement that would enable me, Lucid, to make money on the internet. What should we tell him?")
    
    mail_box_collecting_task = asyncio.create_task(server_logic())
    Lucid_logic_task = asyncio.create_task(Lucid_logic())
    
    await asyncio.gather(mail_box_collecting_task, Lucid_logic_task)

    if mail_box_collecting_task.cancelled():
            raise Exception("Mail box collecting task has been cancelled for some god forsaken reason.")
asyncio.run(main())

# ===== ===== ===== #

