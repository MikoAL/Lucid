import Lucid_generation as generation
import Lucid_preprocess as preprocess
import Lucid_postprocess as postprocess
import Lucid_memory as memory
import Lucid_emotion_detection as emotion_detection
#import Lucid_autistic as autisitc
#import Lucid_server as server
import Lucid_classification as classification
import Lucid_templates as templates

import requests
#from flask import Flask, request, jsonify

incognito = True

history = []

history_counter = 0 # Saves every time this counter hits 4.

working_memory = []
# 8 items
# show 4 items
# based on an importance value?
# changes based on newest log?

info = []

action_list = []

logs = []
# [{timestamp}]SOURCE: {source}; TYPE: {type}; CONTENT: {text}



if incognito != True:
    memory.init_session()

#autisitc.init_classify_sentence()    

import time

#print('1')
def working_memories_md(wm_list):
    result = ''
    for i in wm_list:
        result += f"- {i}\n"
    return result

def log_to_string(log: dict):
    #return f'[{log["timestamp"]}]SOURCE: {log["source"]}; TYPE: {log["type"]}; CONTENT: {log["text"]}'
    return f'[{log["timestamp"]}]{log["source"]}: {log["text"]}'

def get_newest_info():
    global info
    #info.extend(server.new_info)
    #server.reset_new_info()
    backend_url = 'http://127.0.0.1:5001/mailbox/info'  # Replace this with your backend URL
    response = requests.get(backend_url)
    return response.json()['info']

def decide_action(info):
    
    return
def importance():
    # threat > newest message 
    return

def eval_info(info: list):
    result = []
    for i in info:
        if i['type'] == 'text':
            message_type = classification.message_type_classification(i['text'])
            i['message_type'] = message_type
                
    return info

def cycle():
    info = get_newest_info()
    info = eval_info(info)
    sending_to_llm = ''
    sending_to_llm += templates.Lucid_character
    
    sending_to_llm += "\nLogs:"
    for log in info:
        log_str = log_to_string(log)
        sending_to_llm += f"\n{log_str}"
    print(sending_to_llm)
        
    
    
while True:
    the_input = input("ready?") 
    cycle()  






    

