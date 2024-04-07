import time
import sys
import requests
import yaml
import os
import logging
from datetime import date
import asyncio
import json

import numpy as np

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%I:%M:%S %p')
#logging.disable()
# Get the absolute path of the script's directory
script_dir = os.path.dirname(os.path.realpath(__file__))
# Change the working directory to the script's directory
os.chdir(script_dir)


# ============================ #
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

oobabooga_api_host = settings['oobabooga_api']['host']
oobabooga_api_port = settings['oobabooga_api']['port']
main_lm_temperature = settings['main_lm_settings']['temperature']
oobabooga_api_server = f'http://{oobabooga_api_host}:{oobabooga_api_port}'

logging.info('\n'.join([f"\nHost: {host}",
			  f"Port: {port}",
			  f"Server: {server}",
			  f"Small Language Model: {small_lm_name}",
			  f"Temperature: {small_lm_temperature}",
			  f"Top K: {small_lm_top_k}",
			  f"Top P: {small_lm_top_p}",
			  ]))

# ============================ #
# Server stuff

# Check if the server is up
try:
	response = requests.get(server)
	response.raise_for_status()  # Raise an error for bad responses (4xx or 5xx)
	logging.info(f"Server response: {response.status_code}")
except requests.exceptions.RequestException as e:
	logging.critical(f'Failed to connect to the server')
	exit()

def get_mail(server=server): # mail format {'content':content,'source':source,'timestamp':timestamp, 'type':type}
	new_mail = (requests.get(url = f"{server}/mailbox")).json()
	return new_mail

def send_output(output, server=server):
	logging.debug(f"Sending output: {output}")
	requests.post(url=f"{server}/output",json=output)   

def send_summary(summary, server=server):
	requests.post(url=f"{server}/discord/post_summary",json=summary)
 
 
# ============================ #
# Oobabooga API stuff
def api_encode_text(text: str):
	json = {
		"text": text,
	}
	response = requests.post(url=f"{oobabooga_api_server}/v1/internal/encode", json=json).json()
	return response["tokens"]

def api_decode_tokens(tokens: list):
	json = {
		"tokens": tokens,
	}
	response = requests.post(url=f"{oobabooga_api_server}/v1/internal/decode", json=json).json()
	print(json)
	print(response)
	return response["text"]
	

def api_generate_response(prompt: str,
						  temperature: float = 0.7,
						  max_tokens: int = 200,
						  top_k: int = 20,
						  top_p: float = 1.0,
						  logit_bias: dict = {},
						  stop: list = ["\n"],):
	json = {
		"prompt": prompt,
		"temperature": temperature,
		"max_tokens": max_tokens,
		"top_k": top_k,
		"top_p": top_p,
		"logit_bias": logit_bias, # e.g. {"personality": 2.0}
		"stop": stop,
	}
	return ((requests.post(url=f"{oobabooga_api_server}/v1/completions", json=json)).json())['choices'][0]['text']

def api_select(prompt, options, temperature, top_k, top_p):
    if not options:
        return None  # Handle the case of empty options list
    options = [option.strip() for option in options]
    tokenized_options = [api_encode_text(option) for option in options]
    answer = ""
    round_number = 1
    while len(tokenized_options) > 1:  # Use > instead of != to ensure termination
        round_number += 1
        all_first_tokens = [option[0] for option in tokenized_options]
        tokens_to_options = {}
        for i in range(len(all_first_tokens)):
            if all_first_tokens[i] not in tokens_to_options:
                tokens_to_options[all_first_tokens[i]] = [tokenized_options[i]]
            else:
                tokens_to_options[all_first_tokens[i]].append(tokenized_options[i])
        logit_bias = {}
        for tokens_for_check in tokens_to_options:
            logit_bias[tokens_for_check] = 100

        response = api_generate_response(prompt=prompt, temperature=temperature, top_k=top_k, top_p=top_p, logit_bias=logit_bias, max_tokens=1)
        response_token = api_encode_text(response)
        response_token = response_token[-1]
        prompt += response
        answer += response
        if response_token in tokens_to_options.keys():
            for i in tokens_to_options[response_token]:
                if len(i) == 0:
                    break
            tokenized_options = [i[1:] for i in tokens_to_options[response_token]]

            
        else:
            # Handle the case where the response token is not found among the options
            break  # Exit the loop to avoid potential infinite loop
        # decode the final tokenized answer
    for i in options:
        if i.startswith(answer.strip()):
            answer = i
            break
    return answer


# ============================ #
"""
Guidance stuff
"""


from guidance import models, select, gen
import guidance
small_lm = models.Transformers(small_lm_name, device_map="cuda", echo=False, trust_remote_code=True)

prompt_path = r".\Prompts"

with open(f"{prompt_path}\Lucid_prompt_card.txt", 'r', encoding='utf-8') as f:
	Lucid_prompt_card = f.read()
with open(f"{prompt_path}\Lucid_example_dialogue.txt", 'r', encoding='utf-8') as f:
	Lucid_example_dialogue = f.read()
 
Lucid_small_lm = small_lm + "[System]\nYou are Lucid, here are some info on Lucid.\n"+Lucid_prompt_card

# conversation format {'source':source,'content':content/message,'timestamp':timestamp}
conversation=[]
working_memory = []
def get_conversation(conversation=conversation, retrieval_amount=8):
	if len(conversation) == 0:
		return 'No Record Yet.'
	else:
		prompt = ''
		if len(conversation) < retrieval_amount:
			for i in range(len(conversation)):
				prompt += f"[{date.fromtimestamp(conversation[i]['timestamp'])}] {conversation[i]['source']}: {conversation[i]['content']}\n"
		else:
			start_index = max(len(conversation) - retrieval_amount, 0)
			for i in range(start_index, len(conversation)):
				prompt += f"[{date.fromtimestamp(conversation[i]['timestamp'])}] {conversation[i]['source']}: {conversation[i]['content']}\n"
		return prompt.strip()

# A summary of all current event, to hopefully shorten the required conversation length
summary = 'Not Available'

def write_summary(conversation=conversation, previous_summary=summary):
	conversation_ = get_conversation(conversation=conversation)
	new_line = '\n'
	prompt = f"""\
[Task]
Provide a concise summary of the given conversation. Focus on key details and relevant information. A new line is used to denote the end of a summary.

[Example]
PREVIOUS SUMMARY:
Person1 and Person2 are both in the same bar, sitting next to each other, when Person1 noticed his keys were gone.

CONVERSATION:
Person1: Excuse me, did you see a set of keys? 
Person2: What kind of keys? 
Person1: Five keys and a small foot ornament. 
Person2: What a shame! I didn't see them. 
Person1: Well, can you help me look for it? That's my first time here. 

SUMMARY:
Person1 is looking for a set of keys and seeks Person2's assistance in finding them. Person2 expresses regret for not having seen the keys and is willing to help in the search.

[OUTPUT]
PREVIOUS SUMMARY:
{previous_summary}

CONVERSATION:
{conversation_}

SUMMARY:
"""
	response = api_generate_response(prompt=prompt, temperature=main_lm_temperature, max_tokens=200, stop=["\n"])
	return response
#{gen(name='summary', max_tokens=200, temperature=small_lm_temperature, top_p=small_lm_top_p, stop=new_line)}
def update_summary() -> None:
	global summary
	global summaries
	summary = write_summary(conversation=conversation, previous_summary=summary)
	summaries.append(summary)
	logging.debug(f"Generated summary:\n{summary}")
	send_summary({'content':summary})

# the main tasks, defaults to be a good assistant to Miko or something like that.
tasks = []
def get_tasks(tasks=tasks) -> str:
	if len(tasks)==0:
		return '- Be a good friend to Miko.'
	else:
		prompt = ''
		for i in tasks:
			prompt+=f'- {i}\n'
		return prompt.strip()

# This is for generating a response
# @guidance(stateless=False)
# def guidance_converse(lm, working_memory=working_memory):
# 	new_line= "\n"
# 	logging.debug(f"Conversation: {get_conversation()}")
# 	prompt = f"""\
# [Tasks]
# {get_tasks()}

# [Working Memory]
# {working_memory}

# [Summary Of Previous Conversation]
# {summary}

# [Conversation]
# {get_conversation()}

# [Output]
# Lucid: {gen(name='response', stop=new_line, temperature=small_lm_temperature, top_p=small_lm_top_p)}"""
# 	temp_lm = lm + prompt
# 	#response = temp_lm['response']
# 	return temp_lm
# def converse(Lucid_lm=Lucid_small_lm) -> str:
# 	temp_lm = Lucid_lm + guidance_converse()
# 	return temp_lm['response']

# ============================ #
# Chroma stuff
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer, CrossEncoder
cross_encoder = CrossEncoder("cross-encoder/stsb-distilroberta-base", device="cuda")
sentence_transformer = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
chromadb_client = chromadb.Client(Settings(anonymized_telemetry=False))
short_term_memory = chromadb_client.create_collection("short_term_memory")
short_term_memory_uid = 1
#client = chromadb.PersistentClient(path="./Chroma")

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
# load Long-term memory from file
# WIP


@guidance(stateless=False)
def guidance_make_new_info_block(lm, passage):
	first_curly = "{"
	second_curly = "}"
	lm += """\
This is what a Info Block should look like from an example:
[Example]
[2024/02/16] Lucid: What are you doing now? Stop ignoring me!
[2024/02/16] Miko: I'm playing Nintendo games.
[2024/02/16] Lucid: And that's a higher priority than me?
[2024/02/16] Miko: ...
[2024/02/16] Lucid: Your silence speaks volumes.

```json
{
  "object_type" : 'entity',
  "object_name" : 'Miko',
  "content" : 'Miko likes Nintendo games.',
}
```
[End of Example]
"""
	lm += f"""\
{passage}
```json
{first_curly}
  "object_type" : '{select(['entity','event'], name="object_type")},
  "object_name" : "{gen(stop='"',name = "object_name", temperature=small_lm_temperature,  top_p=small_lm_top_p)},
  "content" : "{gen(stop='"',name="content", temperature=small_lm_temperature,  top_p=small_lm_top_p)},"""  
	return lm

def make_new_info_block(clean_lm, passage):
  lm = clean_lm + guidance_make_new_info_block(passage)
  timestamp = date.fromtimestamp(time.time())
  info_block ={
  "object_type" : lm['object_type'],
  "object_name" : lm['object_name'],
  "content" : lm['content'],
  "timestamp" : timestamp,
  "vector" : sentence_transformer.encode([lm['content']]),
  }
  return info_block

@guidance(stateless=False)
def guidance_generate_fake_answer(lm, query):
	new_line = '\n'
	prompt = f"""\
[System]
You are a helpful assistant. Provide an example answer to the given question.

[Example]
Question: "What is the capital of France?"
Answer: "The capital of France is Paris."

Question: "Can you give me an example of a renewable energy source?"
Answer: "One example of a renewable energy source is solar power, which harnesses energy from the sun."

Question: "Who wrote the play 'Romeo and Juliet'?"
Answer: "The play 'Romeo and Juliet' was written by William Shakespeare."
[End of Example]

Question: "{query}"
Answer: "{gen(name='Answer',max_tokens=200, stop=new_line, temperature=small_lm_temperature, top_p=small_lm_top_p)}"""
	lm += prompt
	return lm
def generate_fake_answer(clean_lm, query) -> str:
	temp_lm = clean_lm + guidance_generate_fake_answer(query)
	return ('"'+temp_lm['Answer']).strip('"')
@guidance(stateless=False)
def guidance_check_for_new_info(lm, conversation = conversation, working_memory = working_memory):
	new_line = '\n'
	working_memory_prompt = ""
	if len(working_memory) == 0:
		working_memory_prompt = 'No Record Yet.'
	else:
		prompt = ''
		if len(working_memory) != 0:
			for i in working_memory:
				prompt+=f'- {i["content"]}\n'
			working_memory_prompt = prompt.strip()
	temp_lm = lm + f"""\
[System]
You are a helpful assistant. You specialize in checking if there is any new information in the conversation that is not in working memory.

[Example]

[Example Working Memory]
- Person 1 is going to the store.

[Example Conversation]
[2023/06/23] Person1: I'm going to the store.
[2023/06/23] Person2: What are you going to buy?
[2023/06/23] Person1: I'm going to buy some apples and oranges.
[2023/06/23] Person2: I heard that the store has a sale on bananas today.

[Example Checking for New Information]
Is there any new information that I should know about?
Yes.
- There is a sale on bananas at the store in 2023/06/23 according to Person2.

[End of Example]

[Working Memory]
{working_memory_prompt}

[Conversation]
{get_conversation(conversation=conversation)}

[Output]
Is there any new information that I should know about?
"""
	temp_lm += select(['Yes','No'], name="Yes_or_No")
	return temp_lm

async def check_for_new_info(clean_lm = small_lm, conversation = conversation, working_memory = working_memory) -> bool:
	temp_lm = clean_lm+guidance_check_for_new_info(conversation=conversation, working_memory=working_memory)
	if temp_lm['Yes_or_No'] == 'No':
		return False
	else:
		return True
async def get_new_info(conversation = conversation, working_memory = working_memory):
	working_memory_prompt = ""
	if len(working_memory) == 0:
		working_memory_prompt = 'No Record Yet.'
	else:
		prompt = ''
		if len(working_memory) != 0:
			for i in working_memory:
				prompt+=f'- {i["content"]}\n'
			working_memory_prompt = prompt.strip()
	prompt = f"""\
[System]
You are a helpful assistant. You specialize in checking if there is any new information in the conversation that is not in working memory.

[Example]

[Example Working Memory]
- Person 1 is going to the store.

[Example Conversation]
[2023/06/23] Person1: I'm going to the store.
[2023/06/23] Person2: What are you going to buy?
[2023/06/23] Person1: I'm going to buy some apples and oranges.
[2023/06/23] Person2: I heard that the store has a sale on bananas today.

[Example Checking for New Information]
Is there any new information that I should know about?
Yes.
- There is a sale on bananas at the store in 2023/06/23 according to Person2.

[End of Example]

[Working Memory]
{working_memory_prompt}

[Conversation]
{get_conversation(conversation=conversation)}

[Output]
Is there any new information that I should know about?
Yes.
- """
	response = api_generate_response(prompt=prompt, temperature=main_lm_temperature, max_tokens=300, stop=["\n"])
	return response
def get_working_memory(working_memory=working_memory) -> str:
	if len(working_memory) == 0:
		return 'No Record Yet.'
	else:
		prompt = ''
		for i in working_memory:
			prompt+=f'- {i["content"]}\n'
		return prompt.strip()


def without_keys(d, keys):
	return {k: v for k, v in d.items() if k not in keys}

async def push_info_block_to_short_term_memory(info_block) ->bool:
	global short_term_memory
	global short_term_memory_uid
	info_block_no_vector = without_keys(info_block, ['vector'])
	short_term_memory.add(
		ids=[short_term_memory_uid],
		documents=[info_block],
		embeddings=[info_block['vector']],
		metadata=[info_block_no_vector],
	)
	short_term_memory_uid += 1
	return True # TODO This value should represent if it was accepted or not, but I haven't implemented that yet lol
# Chroma stuff end
# ============================ #
# Temp TTS stuff
"""
from RealtimeTTS import TextToAudioStream, SystemEngine

engine = SystemEngine() # replace with your TTS engine
stream = TextToAudioStream(engine)
#stream.feed("Hello world! How are you today?")
#stream.play_async()
def play_audio(text):
	stream.feed(text)
	stream.play_async()
# Temp TTS stuff end
"""
# ============================ #
# AI Council
# Yes this is copied from "Left Brain, Right Brain" - Bo Burnham
"""
We have a task based structure for Lucid!
The most important task is called:
"Thinking"

Thinking is done by three characters:
- Lumi: Lucid's Left brain
- Reverie: Lucid's Right brain
- Lucid: The main decider

I call this "Council of Thought" or something like that, the names are all WIP.
They will be incharge of giving out tasks to the small LMs and the main LM.

Potential idea:
The council will work on a voting system.
All members must cast a vote, and the majority vote will be the final decision.
Incases where there are more than two options, and no majority is reached, Lucid's vote will take priority.


"""
# Load council members' data from JSON file
with open(f"{prompt_path}\Council_Members.json", 'r', encoding='utf-8') as f:
	AI_Council_data = json.load(f)

def council_of_thought(current_situation: str) -> str:
	global AI_Council_data, Lucid_prompt_card
 
	# Generate prompt for each council member
	council_member_prompt = ""
	for member in AI_Council_data:
		council_member_prompt += f"[{member['name']}]\n- {member['personality_prompt']}\n\n"
  
	council_prompt = f"""[System]\nYou are Lucid, here are some info on Lucid.
{Lucid_prompt_card}

The following are Lucid's internal thoughts. Each member has a unique perspective and role in Lucid's decision-making process.
{council_member_prompt.strip()}

In discussions, each council member will provide their input based on the situation and their unique perspective. At the end of the discussion, Lucid will make the final decision based on the council's input.

Below is an example conversation between Lucid and its council members.

[Example]
### Situation:
[2023/07/23] Lucid: Miko, it seems you're struggling with your code again.
[2023/07/23] Miko: Yeah, I can't seem to find the bug. It's driving me crazy.
### Council Discussion:
Reverie: Maybe he needs a break to clear his mind.
Lumi: Or perhaps we can review the code together to identify the issue.
Lucid: Okay, let's see if we can find the bug together.
[End of Example]

### Situation:
{current_situation}
### Council Discussion:
"""
	before_Lucid = api_generate_response(prompt=council_prompt, temperature=main_lm_temperature, max_tokens=300, stop=["\nLucid:"])
	council_prompt += before_Lucid + "\nLucid:"
	Lucid_verdict = api_generate_response(prompt=council_prompt, temperature=main_lm_temperature, max_tokens=300, stop=["\n"])
	
	return (before_Lucid + "\nLucid:" +Lucid_verdict).strip()

# ============================ #
# Main LM

def main_lm_converse() -> str:
	global summary, Lucid_prompt_card, Lucid_example_dialogue
	prompt = f"""\
[System]
You are Lucid, here are some info on Lucid.
{Lucid_prompt_card}
{Lucid_example_dialogue}
Lucid only responds in plain text.
Lucid only has knowledge of the tasks, working memory, coverstations summaries and internal discussions, she does not make stuff up.
Respond to the conversation as Lucid, stay in character.

[Tasks]
{get_tasks()}

[Working Memory]
{get_working_memory()}

[Summary Of Previous Conversation]
{summary}

[Internal Discussions]

[Conversation]
{get_conversation()}

[Output]
Lucid: """
	response = api_generate_response(prompt=prompt, temperature=main_lm_temperature, max_tokens=300, stop=["\n"])
	return response

# ============================ #
last_get_mail_time= 0
new_mail = []
times_without_summary = 0
summaries = []
summaries_cross_encoder_result = []

small_lm_tasks = []
main_lm_tasks = []
"""
A task structure so we can split work more easily

small_lm will handle the following tasks:
- Summarize the conversation
- Generate a fake answer
- Check for new information
- Generate a new information block

main_lm will handle the following tasks:
- Generate a response
- Thinking

task_names
- Summarize Conversation
- Generate Fake Answer
- Check for New Information
- Generate New Information Block
- Generate Response

importance
Goes from 0 to inf, 0 being the least important and inf being the most important

{
	"task_name": "Summarize Conversation",
	"importance": 1,
}

"""
def importance_sorting(tasks: list) -> list:
	"""
	Sorting the tasks based on importance
	"""
	sorted_task_list = sorted(tasks, key=lambda x: x['importance'])
	return sorted_task_list

async def small_lm_loop() -> None:
	"""Each loop will handle ONE task from the small_lm_tasks list"""
	global small_lm_tasks
	if len(small_lm_tasks) == 0:
		await asyncio.sleep(0.1)
		return
	
	small_lm_tasks = importance_sorting(small_lm_tasks)
	current_task = small_lm_tasks.pop(0)
	logging.debug(f"Executing Task: {current_task}")
	match current_task['task_name']:
		case "Summarize Conversation":
			update_summary()

		case "Check for New Information":
			new_info_check = await check_for_new_info()
			if new_info_check == False:
				logging.debug("No new information.")
			else:
				new_info = await get_new_info()
				new_info_block = make_new_info_block(clean_lm=small_lm, passage=(get_conversation() + "\n\n" + new_info))
				accepted = push_info_block_to_short_term_memory(new_info_block)
				if accepted:
					working_memory.append(new_info_block)

		case _:
			logging.error(f"Unknown task name: {current_task['task_name']}\nSKIPPING {current_task['task_name']}")
	return

async def main_lm_loop() -> None:
	"""Each loop will handle ONE task from the main_lm_tasks list"""
	global main_lm_tasks
	if len(main_lm_tasks) == 0:
		await asyncio.sleep(0.1)
		return

	main_lm_tasks = importance_sorting(main_lm_tasks)
	current_task = main_lm_tasks.pop(0)
	logging.debug(f"Executing Task: {current_task}")
	match current_task['task_name']:
		case "Generate Response":
			logging.debug('generating response')
			generated_response = main_lm_converse()
			response = {
				'source': 'Lucid',
				'content': generated_response,
				'timestamp': time.time(),
				'type': 'conversation',
			}
			logging.debug(f"generated response:\n{generated_response}")
			conversation.append(response)
			send_output(output=response)
   
		case "Generate Thought":
			logging.debug('generating thought')
			pass

		case _:
			logging.error(f"Unknown task name: {current_task['task_name']}\nSKIPPING {current_task['task_name']}")
	return

async def handle_mail() -> None:
	global new_mail, small_lm_tasks, main_lm_tasks
	global last_get_mail_time
	if time.time()-last_get_mail_time >= 0.5:
		last_get_mail_time = time.time()
		new_mail.extend(get_mail())

	if len(new_mail) != 0:
		logging.debug(f"New mail: {new_mail}")
		mail_ = new_mail.pop(0)
		match mail_['type']:
			case 'conversation':
				conversation.append(mail_)
				logging.debug(f'Got mail: {mail_}')
			case _:
				tmp_mail_type = mail_['type']
				logging.warning(f'Received mail with unknown type \"{tmp_mail_type}\"\n{mail_}')
				pass

		main_lm_tasks.append({'task_name': 'Generate Response', 'importance': 10})
		logging.debug('Added Generate Response task to main_lm_tasks')
		small_lm_tasks.append({'task_name': 'Check for New Information', 'importance': 5})
		logging.debug('Added Check for New Information task to small_lm_tasks')
		await asyncio.sleep(0.1)
	else:
		await asyncio.sleep(0.1)
	return

async def main() -> None:
	global small_lm_tasks, main_lm_tasks
	small_lm_task = asyncio.create_task(small_lm_loop())
	main_lm_task = asyncio.create_task(main_lm_loop())
	handle_mail_task = asyncio.create_task(handle_mail())
	
	send_output(output={'content':"```md\n#=====#\n\nLucid is ONLINE\n\n#=====#\n```",'source':'system','timestamp':time.time(),'type':'conversation'})
	new_line = '\n- '
	
	# Keep looping tasks individually
	while True:
	 
		if small_lm_task.done():
			logging.debug('small_lm_task done. Restarting...')
			small_lm_task = asyncio.create_task(small_lm_loop())
   
			if len(small_lm_tasks) != 0:
				logging.debug(f"small_lm_tasks: {new_line.join((task['task_name'] for task in small_lm_tasks))}")
	
	
		if main_lm_task.done():
			logging.debug('main_lm_task done. Restarting...')
			main_lm_task = asyncio.create_task(main_lm_loop())
   
			if len(main_lm_tasks) != 0:
				logging.debug(f"main_lm_tasks: {new_line.join((task['task_name'] for task in main_lm_tasks))}")
			else:
				logging.debug('main_lm_tasks empty\n Adding Generate Thought task')
				
	
		if handle_mail_task.done():
			handle_mail_task = asyncio.create_task(handle_mail())

		await asyncio.sleep(0.1)

asyncio.run(main())

