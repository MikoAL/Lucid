import Lucid_templates as templates
import Lucid_memory as memory

def preprocess(input: str, history: list):
    output = ''
    user_input = 'Miko: '+input
    history.append(user_input)
    
    history_str = '\n'.join(history)
    possible_context = memory.get_history(history_str)
    
    output = f"""Below is an instruction that describes a task. Write a response that appropriately completes the request. 
### Instruction: {templates.character}
Info that may be relevant: 
{possible_context}
Overall Goal: {templates.overall_goal}
    
{templates.chat}
    
{history_str}
    
Lucid:### Response: """
    return output