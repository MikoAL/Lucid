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
    if working_memory == []:
        prompt= f"""{Lucid_prompt}
<|im_start|>user
{request}<|im_end|>
<|im_start|>assistant"""
        return prompt
    else:
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
Make a small list of questions relavent to the situation."""

    prompt = build_prompt(working_memory, request)

    response = generation.llm(prompt)
    
    questions = response.strip()
    
    return questions

def compare_info(info1, info2):


    request = f"""Combine the information from 'info1' and 'info2' into a single string. Info1: {info1}. Info2: {info2}.
    
    ==Handling conflicting sources==
    - Prefer up-to-date sources.
    - Report all significant viewpoints with appropriate attributions.
    - Omit unimportant details.
    - Do not remove conflicting sources just because they contradict others.
    - Do not arbitrarily declare one source as 'true' and discard the rest, except in rare cases of factual error.
    
    Result:"""
    prompt = build_prompt([], request)

    response = generation.llm(prompt)
    
    response = response.strip()
    
    return response
# For a given chunk of current_conversation, generate a pair of question and answer
def observe(current_conversation, WM): # Gather information
    global Lucid_prompt
    request = f"""{current_conversation}
Make a small list of crucial observations about the above conversation. These observations would affect decision making and the observations should be understood without context. Be concise."""

    prompt = build_prompt(WM, request)  

    response = generation.llm(prompt)

    observations = response
    
    return observations

def action(current_conversation, WM):
    global Lucid_prompt
    #global working_memory
    thought = ''
    request = f"""{current_conversation}
What will you do next as Lucid? Start with the phrase 'I should'. Be concise. Specifiy whether you are doing the action now or later."""
    prompt = build_prompt(WM, request)
    thought = generation.llm(prompt)
    return thought.strip()

def converse(current_conversation, WM):
    
    request = f"{current_conversation}\nAbove is the current conversation, based on the current conversation and Lucid's working memory and personality, generate a response as Lucid."
    prompt = build_prompt(WM, request)
    response = generation.llm(prompt)
    
    return response
def demo():
    current_conversation = """Edward: Lucid, I think I'm in love with Bella.. 
    Lucid: Dont say anything else.. 
    Edward: What do you mean?
    Lucid: Open your fu**ing door.. I'm outside."""

    working_memory = []

    observations = observe(current_conversation, working_memory)

    working_memory.append(observations)

    relevant_question_list = relevant_questions(current_conversation, working_memory)

    working_memory.append(relevant_question_list)

    actions = action(current_conversation, working_memory)

    print(f'observations: {observations}')

    print(f'relevant questions: {relevant_question_list}')

    print(f'actions: {actions}')
    
def whys(current_conversation, working_memory, init_statement, depth = 5):
    question_process = []
    statement = init_statement
    for _ in range(depth):
        question = statement+' Why?'
        question_process.append(question)
        request = f"""{current_conversation}
Answer the question logically in one sentence. 
{question}"""

        prompt = build_prompt(working_memory, request)

        response = generation.llm(prompt)
        
        statement = response.strip()
    question_process.append(statement)
    return statement, question_process

def five_w_one_h(current_conversation, working_memory):
    request = f"""{current_conversation}
Based on the conversation provided, please provide comprehensive information regarding the following aspects: Who was involved, What happened, When did it occur, Where did it take place, Why did it happen, and How did it transpire?"""

    prompt = build_prompt(working_memory, request)

    response = generation.llm(prompt)
    
    questions = response.strip()
    
    return questions
    
    
    
    
#class GenerateThought:
#    def __init__(self, custom_prompt):

        
    