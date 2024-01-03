
import time
from datetime import date
import json
import logging
import random

import Lucid_think as think
import Lucid_classification as classification
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
#print(dictionary)
def save_dictionary():
    global dictionary_path
    global dictionary
    with open(dictionary_path, 'w', encoding='utf-8') as f:
        json.dump(dictionary, f, ensure_ascii=False, indent=4)
        
class conversation_message:
    def __init__(self, text, source, type):
        self.text = text
        self.source = source
        self.keywords = classification.keyword_extractor(text)
        self.timestamp = time.time()
        self.type = type
        logging.info(f'keywords: {self.keywords}')
        self.extract_info_on_keywords()
        
    def extract_info_on_keywords(self):
        global dictionary
        if len(self.keywords) != 0:
            for keyword in self.keywords:
  
                if keyword in list(dictionary):
                    dictionary[keyword]['recall_counter'] += 1
                    description = think.keyword_description_from_passage(keyword, f"[{date.fromtimestamp(self.timestamp)}]{self.source}: {self.text}", previous_description=dictionary[keyword]['description'])
                else:
                    description = think.keyword_description_from_passage(keyword, f"[{date.fromtimestamp(self.timestamp)}]{self.source}: {self.text}")
                print(keyword)
                dictionary[keyword] = {'recall_counter':0, 'description':description}
                logging.info(f'info for the word \"{keyword}\" found:\n{description}')
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
        
def current_conversation_style_convertor(conversation_message_list, style):
    global dictionary
    key_list = []
    dictionary_prompt = ''
    if type(conversation_message_list) != list:
        conversation_message_list = [conversation_message_list]
    for i in conversation_message_list:
        #print(i)
        key_list.extend(i.keywords)
    if len(key_list) != 0:
        key_list = list(set(key_list))
        dictionary_prompt = '<|im_start|>system\nDictionary. Entries may contain inaccurate definitions.\n'
        for key in key_list:
            dictionary_prompt += f'{key}\n: {dictionary[key]}\n\n'
        dictionary_prompt += '<|im_end|>\n'
        
    
    match style:
        case 'chatml':
            conversation_chatml = '\n'
            for i in conversation_message_list:
                conversation_chatml += f"""<|im_start|>[{date.fromtimestamp(i.timestamp)}]{i.source}:\n{i.text}<|im_end|>\n"""
            return (dictionary_prompt + conversation_chatml).strip()
        case 'prompt':
            conversation_prompt = ''
            for i in conversation_message_list:
                conversation_prompt += f"""[{date.fromtimestamp(i.timestamp)}]{i.source}: {i.text}\n"""
            return (dictionary_prompt + conversation_prompt).strip()
    return
                
def make_decision(options):
    global working_memory
    global current_conversation
    global notes
    predicted_results = []
    for i in options:
        option_result = think.predict_option_result(current_conversation=current_conversation,
                                                          WM=working_memory,
                                                          notes=notes,
                                                          option_candidate=i)
        predicted_results.append({'option':i,'prediction':option_result})
    final_option_llm_response = think.decide_final_option(predicted_results)
    final_option = classification.zeroshot_classification(sentence = final_option_llm_response,labels=options)
    return final_option
        
        
        
        

def say_out(text):
    print(f"Lucid: {text}")
                
def input_from_miko():
    global mailbox
    miko_input = input('Miko: ')
    miko_mail = conversation_message(miko_input,'Miko', 'message')
    #print('> mail sent.')
    mailbox.append(miko_mail)



running = True
mailbox = []
state = ''
working_memory = []
current_conversation = []
current_sentence_plan = ''
notes = ''
options = ['talk', 'stay silent'] # will appear as "Lucid decided to {option}."
while running:
    input_from_miko()
    if len(mailbox) != 0:
        new_messages = []
        for mail in mailbox:
            if mail.type == 'message':
                new_messages.append(mail)
        # process all types of mail
            
        mailbox = []
    if len(new_messages) != 0:
        state = 'generating_response'
        for msg in new_messages:
            current_conversation.append(msg)
            #action_results = random_action()
            #working_memory.append(action_results['content'])
        new_messages = []
        notes = ''
        notes = think.take_notes(current_conversation=current_conversation_style_convertor(current_conversation, 'chatml'), WM=working_memory, notes=notes)

        # Make decision from options
        chosen_option = make_decision(options=options)
        match chosen_option:
            case 'talk':
                think.plan_sentence(current_conversation=current_conversation)
                current_sentence_plan = think.plan_sentence(WM=working_memory, current_conversation=current_conversation_style_convertor(current_conversation, 'chatml'))
                working_memory.append(current_sentence_plan)
                temp = current_conversation_style_convertor(current_conversation, 'chatml')
                temp = think.converse(temp, working_memory)
                state = 'stating_response'
                say_out(temp)
            case 'stay silent':
                pass

        working_memory = []
        current_conversation.append(conversation_message(text=temp, source='Lucid', type='message'))
        while len(current_conversation) > 4:
            current_conversation.pop(0)
            
    else:
        state = 'idle'
    
        
