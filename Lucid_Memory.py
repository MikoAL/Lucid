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

class memory:
    def __init__(self, text):
        self.text = text
        self.recall_count = 0
        self.last_recall_time = time.time()
        #global working_memory_vector
    def upload_update_vector(self):
        global working_memory_idx
        working_memory_vector.upload_records(
        collection_name="working_memory",
        records=[
            models.Record(
                id=working_memory_idx,
                vector=encoder.encode(self.text).tolist(),
                payload= {'full_memory':self}
            ) 
        ]
        )
        working_memory_idx += 1
    def check_and_upload_to_vector(self, threshold = 0.75):
        global working_memory_idx
        # Check for simulars first
        global working_memory_vector
        hits = working_memory_vector.search(
        collection_name="working_memory",
        query_vector=encoder.encode(self.text).tolist(),
        limit=1
        )
        if len(hits) == 0:
            self.upload_update_vector()
        for hit in hits:
            info2 = hit.payload['full_memory']
            score = hit.score
            info2_id = hit.id
        
        if score >= threshold:
            combined = think.compare_info(self.text, info2.text)
            self.recalled()
            self.replace(combined, info2_id)
        else:
            self.upload_update_vector()
    
    def recalled(self):
        self.recall_count += 1
        self.last_recall_time = time.time()
    
    def replace(self, new_text, idx):
        working_memory_vector.upload_records(
        collection_name="working_memory",
        records=[
            models.Record(
                id=idx, # Replacing info2 completely
                vector=encoder.encode(new_text).tolist(),
                payload= {'full_memory':self}
            ) 
        ]
    )
        

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
            info = hit.payload['full_memory']
            new_working_memory.append(info.text)
            delta_time = time.time() - info.last_recall_time
            if delta_time >= 15.0:
                info.recalled()
                info.upload_update_vector()
    return new_working_memory

    
def make_observations_to_working_memory(current_conversation, working_memory):
    current_conversation_str = ('\n'.join(current_conversation)).strip()
    observations = think.observe(current_conversation_str, working_memory)
    observations = memory(observations)
    working_memory.append(observations.text)
    return working_memory

