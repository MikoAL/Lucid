
import time


    
def make_observations_to_working_memory(current_conversation, working_memory):
    current_conversation_str = ('\n'.join(current_conversation)).strip()
    observations = think.observe(current_conversation_str, working_memory)
    observations = compare_add_working_memory(observations)
    working_memory.append(observations)
    return working_memory

def thinking_cycle(current_conversation, working_memory):
    #updated_conversation = current_conversation
    current_conversation_str = ('\n'.join(current_conversation)).strip()
    #observations = think.observe(current_conversation_str, working_memory)
    five_w_one_h = think.five_w_one_h(current_conversation_str, working_memory)
    five_w_one_h = compare_add_working_memory(five_w_one_h)
    working_memory.append(five_w_one_h)
    
    
    observations = think.observe(current_conversation_str, working_memory)

    observations = compare_add_working_memory(observations)
    working_memory.append(observations)
    #print(f'five_w_one_h: {five_w_one_h}')
    #print(f'observations: {observations}')

    #relevant_question_list = think.relevant_questions(current_conversation_str, working_memory)

    #working_memory.append(relevant_question_list)

    #actions = think.action(current_conversation_str, working_memory)
    
    # pick an action, (based on the response "actions")
    #timeframe = classification.zeroshot_classification(actions, ['immediate', 'later'])['labels'][0]
    #print(actions)
    #print(timeframe)
    
    #if timeframe == 'later':
    #    return current_conversation, working_memory
    #elif timeframe == 'immediate':
    #    response = think.converse(current_conversation_str, working_memory)
    #    updated_conversation.append(f'Lucid: {response}')
    #   return updated_conversation, working_memory

def demo():
    working_memory = []
    current_conversation = ["Edward: Lucid, I think I'm in love with Bella.. ",
    'Lucid: Dont say anything else..',
    'Edward: What do you mean?',
    "Lucid: Open your fu**ing door.. I'm outside"]
    thinking_cycle(current_conversation, working_memory)
    
demo()

import Lucid_think as think
import Lucid_classification as classification
import time
# events
# - init
# - idle
# - thinking
# - user_input

class command:
    def __init__(self, type, action):
        self.type = type
        self.action = action
        self.timestamp = time.time()
from collections import deque
#current_conversation, working_memory = thinking_cycle(current_conversation, working_memory)
priority_queue = deque([])
normal_queue = deque()
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