import Lucid_think as think
import Lucid_classification as classification

from qdrant_client import models, QdrantClient
from sentence_transformers import SentenceTransformer

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
    for hit in hits:
        info2 = hit.payload['text']
        score = hit.score
        info2_id = hit.id
    
    if score >= threshold:
        combined = think.compare_info(info1, info2)
        working_memory_vector.upload_records(
        collection_name="working_memory",
        records=[
            models.Record(
                id=info2_id, # Replacing info2 completely
                vector=encoder.encode(combined).tolist(),
                payload= {'text':combined}
            ) 
        ]
    )
        return 
    else:
        add_working_memory(the_memory)
        return
    
    

def add_working_memory(the_memory):
    global working_memory_vector
    global working_memory_idx
    working_memory_vector.upload_records(
        collection_name="working_memory",
        records=[
            models.Record(
                id=working_memory_idx,
                vector=encoder.encode(the_memory).tolist(),
                payload= {'text':the_memory}
            ) 
        ]
    )
    working_memory_idx += 1


def thinking_cycle(current_conversation, working_memory):
    updated_conversation = current_conversation
    current_conversation_str = ('\n'.join(current_conversation)).strip()
    #observations = think.observe(current_conversation_str, working_memory)
    five_w_one_h = think.five_w_one_h(current_conversation_str, working_memory)
    working_memory.append(five_w_one_h)
    add_working_memory(five_w_one_h)
    
    observations = think.observe(current_conversation_str, working_memory)
    working_memory.append(observations)
    add_working_memory(observations)
    
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


def main():
    working_memory = []
    current_conversation = []
    while True:
        user_input = input('Say: ')
        current_conversation.append(f'Miko: {user_input}')
        current_conversation, working_memory = thinking_cycle(current_conversation, working_memory)
        print(current_conversation[-1])
        
        
current_conversation, working_memory = thinking_cycle(current_conversation, working_memory)
    