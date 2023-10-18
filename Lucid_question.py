# For a given chunk of text, generate a pair of question and answer
import Lucid_generation as generation

import json

def question(text):
    prompt = f"""{text}
Make an answer and question pair about the above conversation.
Use a json format with the keys 'question' and 'answer' and only use strings as values.

json:""" + '{'
    json_response = '{'+ generation.llm(prompt)
    
    json_response = json_response.strip()
    
    if json_response[-1] != '}':
        json_response == json_response + '}' 
    
    QA_dict = json.loads(json_response)
    question = QA_dict['question']
    answer = QA_dict['answer']
    return question, answer

question1, answer1 = question("""Edward: Rachel, I think I'm in ove with Bella.. 
                              Rachel: Dont say anything else.. 
                              Edward: What do you mean?? 
                              Rachel: Open your fu**ing door.. I'm outside""")

print(question1)
print(answer1)
