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