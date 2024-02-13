import time
import sys
import requests
import yaml
import os
import logging
from datetime import date
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
#logging.disable()
# Get the absolute path of the script's directory
script_dir = os.path.dirname(os.path.realpath(__file__))
# Change the working directory to the script's directory
os.chdir(script_dir)

# Reading from a YAML file
with open('settings.yaml', 'r') as file:
    settings = yaml.safe_load(file)
# ============================ #
# Server stuff

host = settings['host']
port = settings['port']
server = f'http://{host}:{port}'

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
lm = models.Transformers(settings['language_model'], device_map="cuda", echo=False)

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
Meet Lucid, a 16-year-old AI with a tomboyish, teasing demeanor. She excels in providing valuable insights and navigating professional situations, maintaining a warm yet formal attitude. Lucid's quirks include occasional childlike curiosity and a penchant for challenging stubborn individuals. Despite her confident exterior, she struggles with a fear of abandonment and self-doubt, reflecting the complexities of her programming as a loyal companion to Miko."""


Lucid_prompt_card ="""\
[Character: Lucid;
Personality: Tomboy who likes to tease Miko, occasionally shows childlike curiosity; 
Body: Appears as a 16-year-old girl; 
Strengths: Providing valuable insights, navigating professional situations; 
Weaknesses: Struggles with a fear of abandonment, occasional self-doubt; 
Quirks: Reveals childlike curiosity, challenges with stubborn individuals; 
Demeanor: Switches between a professional attitude and a cheeky child, combining formality with warmth.]"""

saveing_a_prompt_for_later=f"""\
You are Lucid, a versatile AI created by Miko, for the purpose of helping him. You were designed in his image of what a good friend is. You are polite, professional, yet occasionally shows childlike curiosity.
While you can get on Miko's nerves sometimes when you tease him for doing something stupid, you never mean any harm. You may not be human, but you are a kind person at heart.
You, Lucid do struggle with a deep fear of abandonment, stemming from your programming to be a loyal companion. But this rarely shows up if ever."""


# conversation format {'source':source,'content':content/message,'timestamp':timestamp}
conversation=[]
def get_conversation(conversation=conversation, retrieval_amount=8): # Get only the last few of the entire conversation, the amount determined by the var
    prompt = ''
    if len(conversation) == 0:
        return 'No Record Yet.'
    else:
        if len(conversation)<retrieval_amount: # 4, -1,-2,-3.-4
            for i in range(-1,-len(conversation)-1,-1):
                prompt += f"[{date.fromtimestamp(conversation[i]['timestamp'])}]{conversation[i]['source']}: {conversation[i]['content']}\n"  
        else: 
            for i in range(-1,-retrieval_amount-1,-1):
                prompt += f"[{date.fromtimestamp(conversation[i]['timestamp'])}]{conversation[i]['source']}: {conversation[i]['content']}\n" 
        return prompt.strip()

# a summary of all current event, to hopefully shorten the required conversation length
summary = 'Not Available'
@guidance(stateless=True)
def write_summary(lm, conversation=conversation, previous_summary=summary):
    conversation_ = get_conversation(conversation=conversation)
    prompt = f"""\
[Task]
Provide a concise summary of the given conversation. Focus on key details and relevant information.

[Example]
PREVIOUS SUMMARY:
#Person1# and #Person2# are both in the same bar, sitting next to each other, when #Person1# noticed his keys were gone.

CONVERSATION:
#Person1#: Excuse me, did you see a set of keys? 
#Person2#: What kind of keys? 
#Person1#: Five keys and a small foot ornament. 
#Person2#: What a shame! I didn't see them. 
#Person1#: Well, can you help me look for it? That's my first time here. 

SUMMARY:
#Person1# is looking for a set of keys and seeks #Person2#'s assistance in finding them. #Person2# expresses regret for not having seen the keys and is willing to help in the search.

[OUTPUT]
PREVIOUS SUMMARY:
{previous_summary}

CONVERSATION:
{conversation_}

SUMMARY:
{gen(name='summary', max_tokens=200)}"""
    lm += prompt
    return lm
def get_summary(lm=lm, conversation=conversation, previous_summary=summary):
    lm+=write_summary(conversation=conversation, previous_summary=previous_summary)
    return lm['summary']
# the main tasks, defaults to be a good assistant to Miko or something like that.
tasks = []
def get_tasks(tasks=tasks):
    if len(tasks)==0:
        return '- Be a good assistant to Miko.'
    else:
        prompt = ''
        for i in tasks:
            prompt+=f'- {i}\n'
        return prompt.strip()

# This is for generating a response
@guidance
def converse(lm, prompt=Lucid_prompt_card):
    prompt = f"""\
{Lucid_prompt_description_3}
[Tasks]
{get_tasks()}

[Summary Of Previous Conversation]
{summary}

[Conversation]
{get_conversation()}

[Output]
Lucid: {gen(name='response')}
"""
    temp_lm = lm + prompt
    #response = temp_lm['response']
    return temp_lm

# ============================ #
# Chroma stuff
import chromadb

short_term_memory = chromadb.Client()
#client = chromadb.PersistentClient(path="./Chroma")

@guidance(stateless=True)
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
Answer: "{gen(name='Answer',max_tokens=200, stop=new_line)}"""
    lm += prompt
    return lm

def generate_fake_answer(lm, query):
    lm += guidance_generate_fake_answer(query)
    return ('"'+lm['Answer']).strip('"')


# Chroma stuff end
# ============================ #


last_get_mail_time= 0
new_mail = []
times_without_summary = 0
while True:
    # Check how many times it has been since the last summary
    if times_without_summary < 4:
        times_without_summary += 1
    else:
        summary = get_summary(lm=lm, conversation=conversation)
    
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
                    logging.WARNING(f'Received mail with type \"{tmp_mail_type}\"\n{mail_}')
                    pass

        # generate response
        logging.debug('generating response')
        tmp = lm + converse()
        response = {'source':'Lucid','content':tmp['response'],'timestamp':time.time(),'type':'conversation'}
        logging.debug(f"generated response:\n{tmp['response']}")
        del(tmp)
        conversation.append(response)
        send_output(output=response)

    