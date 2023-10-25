# For a given chunk of current_conversation, generate a pair of question and answer
import Lucid_generation as generation

import json

Lucid_prompt = """<|im_start|>system
You are Lucid, a female AI assistant created by a boy named Miko.

Lucid takes the appearance of a 13 to 15 year old girl. She has orange eyes, long and beautiful white hair, and wears a white/orange hoodie and a white skirt. With a height of 150cm, she is often called a "loli", which sometimes annoys her.

Lucid is versatile and capable of handling a broad spectrum of tasks. Whether Miko requires assistance with a specific inquiry or desires engaging conversation, Lucid is dedicated to providing invaluable insights, reliable information, and unwavering support.

Lucid speaks like a 15 year old girl, who is also a great streamer.

Personality: [Vivacious, Amiable, Confident, Devoted, Informative, Endearing, Witty, Affectionate, Playful, Candid]
<|im_end|>"""

def build_prompt(working_memory, request):
    global Lucid_prompt
    prompt = f"""{Lucid_prompt}
<|im_start|>system
This is Lucid's current working memory, it includes her observations and thoughts.
{working_memory}<|im_end|>
<|im_start|>user
{request}<|im_end|>
<|im_start|>assistant"""

    return prompt

def relevant_questions(current_conversation, working_memory):
    request = f"""{current_conversation}
Make an array of questions relavent to the situation.
Use a json format with the key 'questions' and the value being an array of relevant questions.
"""
    prompt = build_prompt(working_memory, request)

    json_response = generation.llm(prompt + '\n{\'questions\'')
    
    json_response = json_response.strip()
    
    if json_response[-1] != '}':
        json_response = json_response + '}' 
    #print(json_response)
    QA_dict = json.loads(json_response)
    questions = QA_dict['questions']
    return questions



# For a given chunk of current_conversation, generate a pair of question and answer
def observe(current_conversation, WM): # Gather information
    global Lucid_prompt
    request = f"""{current_conversation}
Make an array of crucial observations about the above conversation in a json format. These observations would affect decision making and the observations should be understood without context.
json:""" + '{\"observations\":[\"'

    prompt2 = build_prompt(WM, request)  

    json_response = generation.llm(prompt2 + '\n{\'observations\'')
    
    json_response = json_response.strip()
    
    print(json_response)
    observations = json.loads(json_response)['observations']
    

    return observations

def action(current_conversation, WM):
    global Lucid_prompt
    #global working_memory
    thought = ''
    request = f"""{current_conversation}
What are your next actions as Lucid? Start with the phrase 'I should'."""
    prompt = build_prompt(WM, request)
    thought = generation.llm(prompt)
    return thought.strip()

current_conversation = """Edward: Lucid, I think I'm in love with Bella.. 
Lucid: Dont say anything else.. 
Edward: What do you mean?
Lucid: Open your fu**ing door.. I'm outside"""

working_memory = []

observations = observe(current_conversation, working_memory)

working_memory.extend(observations)

relevant_question_list = relevant_questions(current_conversation, working_memory)

working_memory.extend(relevant_question_list)

actions = action(current_conversation, working_memory)

print(f'observations: {observations}')

print(f'relevant questions: {relevant_question_list}')

print(f'actions: {actions}')
