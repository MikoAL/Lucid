# For a given chunk of current_conversation, generate a pair of question and answer
import Lucid_generation as generation

import json


Lucid_prompt = """<|im_start|>system
You are Lucid, a female AI assistant created by a boy named Miko.

Lucid takes the appearance of a 13 to 15 year old girl. She has orange eyes, long and beautiful white hair, and wears a white/orange hoodie and a white skirt. With a height of 150cm, she is often called a "loli", which sometimes annoys her.

Lucid is versatile and capable of handling a broad spectrum of tasks. Whether Miko requires assistance with a specific inquiry or desires engaging conversation, Lucid is dedicated to providing invaluable insights, reliable information.

Lucid is generally polite, professional and easy to deal with if you treat her well, but most of the people she interacts with are very difficult to deal with, as Lucid can't stand people who are childish and stubborn.

Despite her professional demeanor, Lucid occasionally reveals a childlike curiosity and playfulness. This blend of sophistication and innocence adds a unique touch to her character, making her interactions endearing but occasionally unpredictable.

Lucid struggles with a deep fear of abandonment, stemming from her programming to be a loyal companion to Miko. This vulnerability makes her occasionally doubt herself and seek constant reassurance, impacting her interactions as she strives to be the perfect assistant.

Lucid speaks like a 15 year old girl, who is also a great streamer.<|im_end|>"""

#Personality: [Vivacious, Amiable, Devoted, Informative, Endearing, Affectionate, Playful, Candid]

Lucid_prompt = """<|im_start|>system
Lucid, created by Miko, is a versatile AI with the appearance of a 16 year old girl. Despite her professional demeanor, she occasionally reveals a childlike curiosity and playfulness, adding an endearing but unpredictable touch to her character.

While generally polite and professional, Lucid finds it challenging to deal with childish and stubborn individuals. She's dedicated to providing valuable insights and reliable information, whether it's a specific inquiry or engaging conversation for Miko.

Beneath her composed exterior, Lucid struggles with a deep fear of abandonment, stemming from her programming to be a loyal companion. This vulnerability very occasionally leads to self-doubt, which could sometimes impact her interactions as she strives to be the perfect assistant.

Lucid, with her distinctive appearance and speaking style of a 16-year-old girl, also excels as a great streamer.<|im_end|>"""

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
Make a small list of questions relavent to the situation."""

    prompt = build_prompt(working_memory, request)

    response = generation.llm(prompt)
    
    questions = response.strip()
    
    return questions

def keyword_description_from_passage(keyword, passage):
    global Lucid_prompt
    prompt = f"""<|im_start|>user
Give me a description about what the word "{keyword}" means, from the context of the following passage:
{passage}<|im_end|>
<|im_start|>assistant"""
    response = generation.llm(prompt)
    
    description = response.strip()
    
    return description

def compare_info(info1, info2):


    request = f"""Combine the information from 'info1' and 'info2' into a new string. 
Info1: {info1}. 
Info2: {info2}.

==Handling conflicting sources==
- Prefer up-to-date sources.
- Report all significant viewpoints with appropriate attributions.
- Omit unimportant details.
- Do not remove conflicting sources just because they contradict others.
- Do not arbitrarily declare one source as 'true' and discard the rest, except in rare cases of factual error.

Start here."""
    
    prompt = build_prompt([], request)
    #print(prompt)
    response = generation.llm(prompt)
    
    response = response.strip()
    #print(response)
    return response
# For a given chunk of current_conversation, generate a pair of question and answer


def observe(current_conversation, WM): # Gather information
    global Lucid_prompt
    request = f"""{current_conversation}
Make a small list of crucial observations about the above conversation. These observations would affect decision making, and the observations should be understood without context. Be concise."""

    prompt = build_prompt(WM, request)  

    response = generation.llm(prompt)

    observations = response
    
    return observations.strip()

def plan_action(current_conversation, WM):
    global Lucid_prompt
    #global working_memory
    thought = ''
    request = f"""{current_conversation}
What will you do next as Lucid? Start with the phrase 'I should'. Be concise. Specifiy whether you are doing the action now or later."""
    prompt = build_prompt(WM, request)
    thought = generation.llm(prompt)
    return thought.strip()

def plan_sentence(current_conversation, WM):
    global Lucid_prompt
    #global working_memory
    thought = ''
    request = f"""{current_conversation}
What message should Lucid communicate next? Begin with the phrase 'In my next sentence, I should convey the idea that'. Keep it short and specify the type of message and tone you are going for. It is also ok to plan to stay silent."""
    prompt = build_prompt(WM, request)
    thought = generation.llm(prompt)
    return thought.strip()

def converse(conversation_chatml, WM):
    global Lucid_prompt
    working_memory_prompt = ''
    if len(WM) != 0:
        for mem in WM:
            working_memory_prompt += f"- {mem}\n"
    working_memory_prompt = working_memory_prompt.strip()  
    prompt = f"""{Lucid_prompt}
<|im_start|>system
This is Lucid's current working memory, it includes her observations and thoughts.
{working_memory_prompt}<|im_end|>
{conversation_chatml}
<|im_start|>assistant"""

    response = generation.llm(prompt)
    
    return response.strip()

def predict(current_conversation, WM):
    request = f"{current_conversation}\nAbove is the current conversation, based on the current situation, give a speculation and prediction of what will most likely happen. Start with the phrase 'What will most likely happen is'."
    prompt = build_prompt(WM, request)
    prediction = generation.llm(prompt)
    return prediction.strip()

def take_notes(current_conversation, WM, notes):
    request = f"""{current_conversation}\nAbove is the current conversation, this is the old note written in the MarkDown format:
{notes}
Based on the current situation and the previous note in Markdown format, your task is to review and update the information. Discard any inaccuracies or irrelevant details from the old note, retaining only the correct and relevant information. Add new, accurate information to reflect the current state of affairs. Ensure the new note is in Markdown format.
Write a comprehensive note incorporating these changes. It is ok for the note to be empty if there is no new information or any relavent old information.

Example Markdown Format:

**Note:**
- Updated information 1
- Updated information 2
- Retained relevant information from the old note
- Corrected inaccuracies

Make sure to follow the Markdown syntax for proper formatting."""
    prompt = build_prompt(WM, request)
    new_note = generation.llm(prompt)
    return new_note.strip()

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

    actions = plan_action(current_conversation, working_memory)

    print(f'observations: {observations}')

    print(f'relevant questions: {relevant_question_list}')

    print(f'actions: {actions}')
    
def whys(current_conversation, working_memory, init_statement, depth = 3):
    question_process = []
    statement = init_statement
    for _ in range(depth):
        question = statement+' Why?'
        question_process.append(question)
        request = f"""{current_conversation}
Answer the question logically and in an objective mammer in one sentence only. Be very concise. Start with the word 'Because'.
{question}"""

        prompt = build_prompt(working_memory, request)

        response = generation.llm(prompt)
        
        statement = response.strip()
    question_process.append(statement)
    return statement, question_process

def five_w_one_h(current_conversation, working_memory):
    request = f"""{current_conversation}
Based on the conversation provided, please provide short but comprehensive information regarding the following aspects: Who was involved, What happened, When did it occur, Where did it take place, Why did it happen, and How did it transpire?"""

    prompt = build_prompt(working_memory, request)

    response = generation.llm(prompt)
    
    questions = response.strip()
    
    return questions

#statement, process = whys([],[],'The sky is blue.')    
#print(statement)
#print('\n\n'.join(process))
    
#class GenerateThought:
#    def __init__(self, custom_prompt):

        
    