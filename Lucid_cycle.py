import Lucid_think as think
import Lucid_classification as classification

from qdrant_client import models, QdrantClient
from sentence_transformers import SentenceTransformer

import time

working_memory_vector = QdrantClient(":memory:") # Create in-memory Qdrant instance, for testing, CI/CD
current_conversation = []
working_memory = []
working_memory_idx = 0
encoder = SentenceTransformer('all-MiniLM-L6-v2') # Model to create embeddings

working_memory_vector.recreate_collection(
    collection_name="working_memory",
    vectors_config=models.VectorParams(
        size=encoder.get_sentence_embedding_dimension(), # Vector size is defined by used model
        distance=models.Distance.COSINE
    )
)

def compare_add_working_memory(the_memory, threshold = 0.75):
    global working_memory_vector
    info1 = the_memory
    hits = working_memory_vector.search(
    collection_name="working_memory",
    query_vector=encoder.encode(the_memory).tolist(),
    limit=1
)
    if len(hits) == 0:
        add_working_memory(the_memory)
        return the_memory
    for hit in hits:
        info2 = hit.payload['text']
        score = hit.score
        info2_id = hit.id
        info2_recall_count = hit.payload['recall_count']
    
    if score >= threshold:
        combined = think.compare_info(info1, info2)
        working_memory_vector.upload_records(
        collection_name="working_memory",
        records=[
            models.Record(
                id=info2_id, # Replacing info2 completely
                vector=encoder.encode(combined).tolist(),
                payload= {'text':combined, 'recall_count':info2_recall_count+1, 'last_recall':time.time()}
            ) 
        ]
    )
        return combined
    else:
        add_working_memory(the_memory)
        return the_memory
    
    

def add_working_memory(the_memory):
    global working_memory_vector
    global working_memory_idx
    working_memory_vector.upload_records(
        collection_name="working_memory",
        records=[
            models.Record(
                id=working_memory_idx,
                vector=encoder.encode(the_memory).tolist(),
                payload= {'text':the_memory, 'recall_count': 0, 'last_recall':time.time()}
            ) 
        ]
    )
    working_memory_idx += 1

def recall_working_memory(current_conversation):
    global working_memory_vector
    new_working_memory = []
    current_conversation_str = '\n'.join(current_conversation)
    hits = working_memory_vector.search(
    collection_name="working_memory",
    query_vector=encoder.encode(current_conversation_str).tolist(),
    limit=4
)
    if len(hits) != 0:    
        for hit in hits:
            info = hit.payload['text']
            new_working_memory.append(info)
            delta_time = time.time() - hit.payload['last_recall']
            if delta_time >= 15.0:
                recall_count = hit.payload['recall_count']+1
            else:
                recall_count = hit.payload['recall_count']
            working_memory_vector.set_payload(
                collection_name="working_memory",
                payload={'recall_count':recall_count, 'last_recall':time.time()},
                points=hit.vector
            )
    return new_working_memory

    
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

# events
# - init
# - idle
# - thinking
# - user_input

def main():
    state = 'init'
    working_memory = []
    current_conversation = []
    match state:
        case 'init':
            state = 'idle'
            working_memory = []
            current_conversation = []
        case 'idle':
            current_conversation, working_memory = thinking_cycle(current_conversation, working_memory)
            #print(current_conversation[-1])
        case 'action':
            pass
        
from collections import deque
#current_conversation, working_memory = thinking_cycle(current_conversation, working_memory)
priority_queue = deque(['init'])
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