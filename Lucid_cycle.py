
import time

import json

import random

import Lucid_think as think
import Lucid_classification as classification
import time
import Lucid_memory as memory
#import Lucid_generation as generation
# events
# - init
# - idle
# - thinking
# - user_input
dictionary_path = r"C:\Users\User\Desktop\Projects\Lucid\dictionary\dictionary.json"
f = open(dictionary_path)
dictionary = json.load(f)

def save_dictionary():
    global dictionary_path
    global dictionary
    with open(dictionary_path, 'w', encoding='utf-8') as f:
        json.dump(dictionary, f, ensure_ascii=False, indent=4)
class incoming:
    def __init__(self, text, source):
        self.text = text
        self.source = source
        self.keywords = classification.keywords(text)
        self.timestamp = time.time()
    def extract_info_on_keywords(self):
        global dictionary
        if len(self.keywords) != 0:
            for keyword in self.keywords:
                if keyword in dictionary:
                    dictionary[keyword]['recall_counter'] += 1
                    
                else:
                    description = think.keyword_description_from_passage(keyword, self.text)
                    dictionary[keyword] = {'recall_counter':0, 'description':description}
                save_dictionary()
        else:
            return
        
        
        
class command:
    def __init__(self, state, action):
        self.state = state
        self.action = action
        self.timestamp = time.time()

from collections import deque
#current_conversation, working_memory = thinking_cycle(current_conversation, working_memory)
priority_queue = deque([])
normal_queue = deque([])
# level: system, 
# command: idle, converse, think
def process_queue():
    global priority_queue
    global normal_queue
    global working_memory
    global current_conversation
    
    if len(priority_queue) != 0:
        command = priority_queue.popleft()
    elif len(normal_queue) != 0:
        command = normal_queue.popleft()
    else:
        normal_queue.append('idle')
        return
    
    match command:
        case 'init':
            working_memory = []
            current_conversation = []
            
            pass
        case 'idle':
            normal_queue.append('action')
            pass

def random_action():
    choices = ['observe', 'plan_action', 'predict']
    finale_choice = random.choice(choices)
    match finale_choice:
        case 'observe':
            return {'role': 'system','content':f"""Observation: {think.observe()}"""}
        case 'plan_action':
            return {'role': 'system','content':f"""Action Plan: {think.plan_action()}"""}
        case 'predict':
            return {'role': 'system','content':f"""Prediction: {think.predict()}"""}
    return
        
def style_convertor(conversation_dict_list, style):
    if type(conversation_dict_list) == dict:
        conversation_dict_list = [conversation_dict_list]
    match style:
        case 'chatml':
            conversation_chatml = ''
            for i in conversation_dict_list:
                conversation_chatml += f"""<|im_start|>{i['role']}\n{i['content']}<|im_end|>\n"""
            return conversation_chatml.strip()
        case 'prompt':
            conversation_prompt = ''
            for i in conversation_dict_list:
                conversation_prompt += f"""{i['role']}: {i['content']}\n"""
            return conversation_prompt.strip()
    return
                
def say_out(text):
    print(text)
                
def input_from_miko():
    global mailbox
    miko_input = input('Miko: ')
    mailbox.append({'type':'message','source':'Miko','content':miko_input})



running = True
mailbox = []
state = ''
working_memory = []
current_conversation = []
current_sentence_plan = ''
while running:
    input_from_miko()
    if len(mailbox) != 0:
        new_messages = []
        for mail in mailbox:
            if mail['type'] == 'message':
                new_messages.append({'role':mail['source'], 'content':mail['content']})
        mailbox = []
    if len(new_messages) != 0:
        state = 'generating_response'
        for msg in new_messages:
            current_conversation.append(msg)
            #action_results = random_action()
            #working_memory.append(action_results['content'])
        new_messages = []
        current_sentence_plan = think.plan_sentence(WM=working_memory, current_conversation=current_conversation)
        working_memory.append(current_sentence_plan)
        temp = style_convertor(current_conversation, 'chatml')
        print(temp)
        temp = think.converse(temp, working_memory)
        working_memory.pop(-1)
        state = 'stating_response'
        say_out(temp)
        current_conversation.append({'role':'assistant', 'content':temp})
        while len(current_conversation) > 4:
            current_conversation.pop(0)
            
    else:
        state = 'idle'
    
        
