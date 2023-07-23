import chromadb
client = chromadb.PersistentClient(path="./History/chroma",)

from chromadb.utils import embedding_functions

default_ef = embedding_functions.DefaultEmbeddingFunction()
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")





text = ''
session = 1
serial_number = 1

f = open("session_number.txt", "r")
session = int(f.read)
f.close()

f = open("session_number.txt", "w")
f.write(str(session+1))
f.close()

"""
document_example = [text] 
metadata_example = [{'session':session}] 
id_example = [f'{session}-{number}']
"""

collection = client.get_or_create_collection(name="history", embedding_function=sentence_transformer_ef)
def save_history(history: list):
    global serial_number
    global session
    text = '\n'.join(history)
    collection.add(
        documents=[text],
        metadatas=[{'session':session,'serial_number':serial_number}],
        ids=[f"{session}-{serial_number}"]
    )
    serial_number += 1
    return
"""
def get_history(query):
    results = collection.query(
    query_texts=[query],
    n_results=1,
    )
    print(f'query results: {results}')
    
    serial_number = results['metadatas'][0][0]['serial_number']
    session = results['metadatas'][0][0]['session']
    
    lines_before_results = (collection.get(ids=[f'{session}-{serial_number-1}']))
    lines_before_results = lines_before_results['documents'][0]
    
    lines_after_results = (collection.get(ids=[f'{session}-{serial_number+1}']))
    lines_after_results = lines_after_results['documents'][0]

    results = f'{lines_before_results}\n{results}\n{lines_after_results}'
    return results
"""

def get_history(query):
    results = collection.query(
    query_texts=[query],
    n_results=1,
    )
    #print(f'query results: {results}')
    try:
        serial_number = results['metadatas'][0][0]['serial_number']
        session = results['metadatas'][0][0]['session']
    except IndexError:
        pass
    try:
        results = results['documents'][0][0]
    except IndexError:
        results = ''
    return results

