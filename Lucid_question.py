# For a given chunk of text, generate a pair of question and answer
import Lucid_generation as generation

import json

def question(text):
    prompt = f"""{text}
Make an answer and question pair about some important observations of the above conversation.
Use a json format with the keys 'question' and 'answer' and only use strings as values.

json:""" + '{'
    json_response = '{'+ generation.llm(prompt)
    
    json_response = json_response.strip()
    
    if json_response[-1] != '}':
        json_response = json_response + '}' 
    print(json_response)
    QA_dict = json.loads(json_response)
    question = QA_dict['question']
    answer = QA_dict['answer']
    return question, answer



# For a given chunk of text, generate a pair of question and answer
import Lucid_generation as generation

import json

def observe(text):
    prompt = f"""{text}
Make a list of crucial observations about the above conversation in a json format. The observations should be understood without context.
json:""" + '{\"observations\":[\"'

    prompt2 = f"""<|im_start|>system
You are Lucid, a female AI assistant created by a boy named Miko.

Lucid takes the appearance of a 13 to 15 year old girl. She has orange eyes, long and beautiful white hair, and wears a white/orange hoodie and a white skirt. With a height of 150cm, she is often called a "loli", which sometimes annoys her.

Lucid is versatile and capable of handling a broad spectrum of tasks. Whether Miko requires assistance with a specific inquiry or desires engaging conversation, Lucid is dedicated to providing invaluable insights, reliable information, and unwavering support.

Lucid speaks like a 15 year old girl, who is also a great streamer.

Personality: [Vivacious, Amiable, Confident, Devoted, Informative, Endearing, Witty, Affectionate, Playful, Candid]
<|im_end|>
<|im_start|>user
{prompt}<|im_end|>
<|im_start|>assistant"""

    json_response = '{'+ generation.llm(prompt2)
    
    json_response = json_response.strip()
    
    json_response = '{\"observations\":[\"' + json_response
    if json_response[-1] != '}':
        json_response = json_response + '}' 
    print(json_response)
    observations = json.loads(json_response)['observations']
    

    return observations



observations = observe("""Edward: Rachel, I think I'm in love with Bella.. 
                              Rachel: Dont say anything else.. 
                              Edward: What do you mean?? 
                              Rachel: Open your fu**ing door.. I'm outside""")
print(observations)