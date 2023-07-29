import Lucid_generation as generation
import Lucid_preprocess as preprocess
import Lucid_postprocess as postprocess
import Lucid_memory as memory

from flask import Flask, request, jsonify

incognito = True

history = []

history_counter = 0 # Saves every time this counter hits 4.

if incognito != True:
    memory.init_session()
import time

print('1')
app = Flask(__name__)

    

@app.route('/message', methods=['POST'])
def handle_message():
    global history_counter
    global incognito
    global history
    data = request.get_json()
    message = data.get('message')

    user_input= message
    
    
    
    preprocessed_text = preprocess.preprocess(user_input,history)
    llm_response = generation.llm(preprocessed_text)
    llm_response = postprocess.postprocess(llm_response)
    history.append(f'Lucid: {llm_response}')
    history_counter += 2
    
    #print(f'Lucid: {llm_response}')
    
    if history_counter == 4:
        history_counter = 0
        if incognito != True:
            memory.save_history(history[-4:])
    if len(history) == 12:
        del history[:2]
    
    # Process the message and prepare the response
    response_message = f"{llm_response.strip()}"
    #time.sleep(5)
    print(jsonify({'response': response_message}))
    return jsonify({'response': response_message})

if __name__ == "__main__":
    app.run(port=5001)





    

