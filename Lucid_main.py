import Lucid_generation as generation
import Lucid_preprocess as preprocess
import Lucid_postprocess as postprocess
import Lucid_memory as memory
import Lucid_emotion_detection as emotion_detection
import Lucid_autistic as autisitc


from flask import Flask, request, jsonify

incognito = True

history = []

history_counter = 0 # Saves every time this counter hits 4.

working_memory = []


if incognito != True:
    memory.init_session()

autisitc.init_classify_sentence()    

import time

#print('1')
app = Flask(__name__)

    

@app.route('/message', methods=['POST'])
def handle_message():
    global history_counter
    global incognito
    global history
    global working_memory
    
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
    emotion = emotion_detection.emotion_dectection(response_message)
    #time.sleep(5)
    
    print(jsonify({'response': response_message,'emotion':emotion}))
    return jsonify({'response': response_message,'emotion':emotion})

if __name__ == "__main__":
    app.run(port=5001)





    

