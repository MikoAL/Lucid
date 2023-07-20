import Lucid_templates as templates

history = []

def preprocess(input):
    output = ''
    user_input = 'Miko: '+input
    history.append(user_input)
    
    history_str = '\n'.join(history)
    output = f"""Below is an instruction that describes a task. Write a response that appropriately completes the request. 
    ### Instruction: {templates.character}
    Overall Goal: {templates.overall_goal}
    Extra Context:
    
    {templates.chat}
    
    {history_str}
    
    Lucid:### Response: """
    return output