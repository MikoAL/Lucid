import gradio as gr
import json

import Lucid_think as think
import Lucid_classification as classification
import time
import Lucid_memory as memory
# events
# - init
# - idle
# - thinking
# - user_input
dictionary_path = r"C:\Users\User\Desktop\Projects\Lucid\dictionary\dictionary.json"
f = open(dictionary_path)
dictionary = json.load(f)

def save_dictionary():
    global dictionary_path
    global dictionary
    with open(dictionary_path, 'w', encoding='utf-8') as f:
        json.dump(dictionary, f, ensure_ascii=False, indent=4)
class incoming:
    def __init__(self, text, source):
        self.text = text
        self.source = source
        self.keywords = classification.keywords(text)
        self.timestamp = time.time()
    def extract_info_on_keywords(self):
        global dictionary
        if len(self.keywords) != 0:
            for keyword in self.keywords:
                if keyword in dictionary:
                    dictionary[keyword]['recall_counter'] += 1
                    
                else:
                    description = think.keyword_description_from_passage(keyword, self.text)
                    dictionary[keyword] = {'recall_counter':0, 'description':description}
                save_dictionary()
        else:
            return
def greet(name):
    return "Hello " + name + "!"

def manual_messaging(input_text, source):
    incoming_message = incoming(input_text, source)
    keywords = ', '.join(incoming_message.keywords)
    return incoming_message.text, keywords
with gr.Blocks() as demo:
    demo = gr.Interface(fn=manual_messaging, inputs=["text", "text"], outputs=["text", "text"])
    
if __name__ == "__main__":
    demo.launch(show_api=False)   