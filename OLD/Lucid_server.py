#import Lucid_generation as generation
import Lucid_preprocess as preprocess
import Lucid_postprocess as postprocess
#import Lucid_memory as memory
#import Lucid_emotion_detection as emotion_detection
#import Lucid_autistic as autisitc

from flask import Flask, request, jsonify

import datetime 

app = Flask(__name__)
new_info = []
def reset_new_info():
    global new_info
    new_info = []

def get_timestamp():
    now = datetime.datetime.now()
    return now.strftime('%Y-%m-%d %H:%M:%S.%f')[:23]

@app.route('/receiver/text',methods = ['POST'])
def receive_text():
    global new_info
    data = request.get_json()
    received_text = data.get('text')
    source = data.get('source')
    timestamp = get_timestamp()
    source_text_timestamp = {'type':'text','source':source,'text':received_text,'timestamp': timestamp}
    new_info.append(source_text_timestamp)
    return jsonify({'conformation':f'received the text: {received_text}\nfrom: {source}\nat:{timestamp}'})

#def send_text_to_backend(source, text):
#    backend_url = 'http://127.0.0.1:5001/receiver/text'  # Replace this with your backend URL
#    response = requests.post(backend_url, json={'source':source, 'text': text})
#    return response.json()['conformation']

@app.route('/mailbox/info',methods = ['GET'])
def give_info():
    global new_info
    info_to_send = new_info
    reset_new_info()
    return jsonify({'info':info_to_send})

app.run(port=5001)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
"""
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

"""