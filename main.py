import time
import sys
import requests
import yaml
import os
import logging
from datetime import date
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
language_model = settings['llm_settings']['language_model']
conversation_temperature = settings['llm_settings']['temperature']
top_k = settings['llm_settings']['top_k']
top_p = settings['llm_settings']['top_p']

logging.info('\n'.join([f"\nHost: {host}",
			  f"Port: {port}",
			  f"Server: {server}",
			  f"Language Model: {language_model}",
			  f"Temperature: {conversation_temperature}",
			  f"Top K: {top_k}",
			  f"Top P: {top_p}",
			  ]))

# ============================ #
# Server stuff


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
	requests.post(url=f"{server}/output",json=output)   
	 
# ============================ #

from guidance import models, gen, select
import guidance
clean_lm = models.Transformers(language_model, device_map="cuda", echo=False)

prompt_path = r".\Prompts"

Lucid_prompt_description = """\
Lucid, created by Miko, is a versatile AI with the appearance of a 16 year old girl. Despite her professional demeanor, she occasionally reveals a childlike curiosity and playfulness, adding an endearing but unpredictable touch to her character.

While generally polite and professional, Lucid finds it challenging to deal with childish and stubborn individuals. She's dedicated to providing valuable insights and reliable information, whether it's a specific inquiry or engaging conversation for Miko.

Beneath her composed exterior, Lucid struggles with a deep fear of abandonment, stemming from her programming to be a loyal companion. This vulnerability very occasionally leads to self-doubt, which could sometimes impact her interactions as she strives to be the perfect assistant.

Lucid, with her distinctive appearance and speaking style of a 16-year-old tomboy childhood friend, also excels as a great streamer."""

Lucid_prompt_description_2 = f"""\
You are Lucid, a versatile AI created by Miko, for the purpose of helping him. You were designed in his image of what a good friend is. You are polite, professional, yet occasionally shows childlike curiosity.
While you can get on Miko's nerves sometimes when you tease him for doing something stupid, you never mean any harm. You may not be human, but you are a kind person at heart.
You, Lucid do struggle with a deep fear of abandonment, stemming from your programming to be a loyal companion. But this rarely shows up if ever."""

Lucid_prompt_description_3 = """\
Meet Lucid, a 16-year-old AI with a tomboyish, teasing demeanor. She excels in providing valuable insights and navigating various situations with warmth and friendliness. Lucid's quirks include occasional childlike curiosity and a penchant for challenging stubborn individuals. Despite her confident exterior, she struggles with a fear of abandonment and self-doubt, reflecting the complexities of her programming as a loyal friend to Miko."""

with open(f"{prompt_path}\Lucid_prompt_card.txt", 'r', encoding='utf-8') as f:
	Lucid_prompt_card = f.read()

saveing_a_prompt_for_later=f"""\
You are Lucid, a versatile AI created by Miko, for the purpose of helping him. You were designed in his image of what a good friend is. You are polite, professional, yet occasionally shows childlike curiosity.
While you can get on Miko's nerves sometimes when you tease him for doing something stupid, you never mean any harm. You may not be human, but you are a kind person at heart.
You, Lucid do struggle with a deep fear of abandonment, stemming from your programming to be a loyal companion. But this rarely shows up if ever."""

Lucid_lm = clean_lm + "[System]\nYou are Lucid, here are some info on Lucid.\n"+Lucid_prompt_card

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

# a summary of all current event, to hopefully shorten the required conversation length
summary = 'Not Available'
@guidance(stateless=False)
def write_summary(lm, conversation=conversation, previous_summary=summary):
	conversation_ = get_conversation(conversation=conversation)
	new_line = '\n'
	prompt = f"""\
[Task]
Provide a concise summary of the given conversation. Focus on key details and relevant information.

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
{gen(name='summary', max_tokens=200, temperature=conversation_temperature, top_p=top_p, stop=new_line)}"""
	temp_lm = lm + prompt
	return temp_lm
def get_summary(clean_lm=clean_lm, conversation=conversation, previous_summary=summary):
	temp_lm = clean_lm + write_summary(conversation=conversation, previous_summary=previous_summary)
	return temp_lm['summary']
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
@guidance(stateless=False)
def guidance_converse(lm, working_memory=working_memory):
	new_line= "\n"
	logging.debug(f"Conversation: {get_conversation()}")
	prompt = f"""\
[Tasks]
{get_tasks()}

[Working Memory]
{working_memory}

[Summary Of Previous Conversation]
{summary}

[Conversation]
{get_conversation()}

[Output]
Lucid: {gen(name='response', stop=new_line, temperature=conversation_temperature, top_p=top_p)}"""
	temp_lm = lm + prompt
	#response = temp_lm['response']
	return temp_lm
def converse(Lucid_lm=Lucid_lm) -> str:
	temp_lm = Lucid_lm + guidance_converse()
	return temp_lm['response']

# ============================ #
# Chroma stuff
import chromadb
from sentence_transformers import SentenceTransformer, CrossEncoder
cross_encoder = CrossEncoder("cross-encoder/stsb-distilroberta-base", device="cuda")
sentence_transformer = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
short_term_memory = chromadb.Client()
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
  "object_name" : "{gen(stop='"',name = "object_name", temperature=conversation_temperature,  top_p=top_p)},
  "content" : "{gen(stop='"',name="content", temperature=conversation_temperature,  top_p=top_p)},"""  
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
Answer: "{gen(name='Answer',max_tokens=200, stop=new_line, temperature=conversation_temperature, top_p=top_p)}"""
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
	if (temp_lm['Yes_or_No']) == 'No':
		return temp_lm
	else:
		temp_lm += f"""\
\n - {gen(name='new_info',max_tokens=200, stop=new_line, temperature=conversation_temperature, top_p=top_p)}"""
		return temp_lm

def check_for_new_info(clean_lm = clean_lm, conversation = conversation, working_memory = working_memory) -> str:
	temp_lm = clean_lm+guidance_check_for_new_info(conversation=conversation, working_memory=working_memory)
	if temp_lm['Yes_or_No'] == 'No':
		return "No new information."
	else:
		return temp_lm['new_info']


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

def push_info_block_to_short_term_memory(info_block) ->bool:
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
	return True # This value represents if it was accepted or not
# Chroma stuff end
# ============================ #
# Temp TTS stuff

from RealtimeTTS import TextToAudioStream, SystemEngine

engine = SystemEngine() # replace with your TTS engine
stream = TextToAudioStream(engine)
#stream.feed("Hello world! How are you today?")
#stream.play_async()
def play_audio(text):
	stream.feed(text)
	stream.play_async()
# Temp TTS stuff end
# ============================ #
last_get_mail_time= 0
new_mail = []
times_without_summary = 0
summaries = []
summaries_cross_encoder_result = []
while True:

	
	# Check for new mail if it has been more than 0.5 seconds since last check
	if time.time()-last_get_mail_time >= 0.5:
		last_get_mail_time = time.time()
		new_mail.extend(get_mail())

	if len(new_mail) != 0:
		# Mail sorting based on types, starting from the oldest (the front)
		for i in range(len(new_mail)):
			mail_ = new_mail.pop(0)
			#print(mail_)
			match mail_['type']:
				case 'conversation':
					conversation.append(mail_)
					logging.debug(f'Got mail: {mail_}')
				case _:
					tmp_mail_type = mail_['type']
					logging.WARNING(f'Received mail with unknown type \"{tmp_mail_type}\"\n{mail_}')
					pass

		# generate response
		logging.debug('generating response')
		generated_response=converse()
		response = {
	  			'source' : 'Lucid',
				'content' : generated_response,
				'timestamp' : time.time(),
				'type' : 'conversation',
				}
		logging.debug(f"generated response:\n{generated_response}")
		conversation.append(response)
		send_output(output=response)
		play_audio(response['content'])
		
		# Check for new info
		new_info_check = check_for_new_info()
		if new_info_check == "No new information.":
			logging.debug("No new information.")
		else:
			new_info = new_info_check
			new_info_block = make_new_info_block(passage=(get_conversation()+"\n\n"+new_info))
			accepted = push_info_block_to_short_term_memory(new_info_block)
			if accepted:
				working_memory.append(new_info_block)
		# Check how many times it has been since the last summary
		if times_without_summary < 0:
			times_without_summary += 1
		else:
			summary = get_summary()
			logging.debug(f"Generated summary:\n{summary}")
			times_without_summary = 0
			# Graph the summary or something
			summaries.append(summary)
			# If the cosine similarity between the last two summaries is less than a threshold, then we should maybe create a new info block
			# Or if the cosine similarity between the second last summary and the newest few dialog is less than a threshold, then we should maybe create a new info block
			if len(summaries) >= 2:
				#summaries_cross_encoder_result.append(cross_encoder([summaries[-2], summaries[-1]]))
				pass
			
		
		

	
