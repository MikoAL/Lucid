
import Lucid_think as think
import Lucid_classification as classification
current_conversation = []
working_memory = []

def cycle(current_conversation, working_memory):
    updated_conversation = ''
    current_conversation_str = ('\n'.join(current_conversation)).strip()
    observations = think.observe(current_conversation_str, working_memory)

    working_memory.append(observations)

    relevant_question_list = think.relevant_questions(current_conversation_str, working_memory)

    working_memory.append(relevant_question_list)

    actions = think.action(current_conversation_str, working_memory)
    
    # pick an action, (based on the response "actions")
    timeframe = classification.zeroshot_classification(actions, ['immediate', 'later'])['labels'][0]
    
    if timeframe == 'later':
        return current_conversation, working_memory
    elif timeframe == 'immediate':
        response = think.converse(current_conversation_str, working_memory)
        updated_conversation = current_conversation.append(f'Lucid: {response}')
    return updated_conversation, working_memory

def demo():
    working_memory = []
    current_conversation = ["Edward: Lucid, I think I'm in love with Bella.. ",
    'Lucid: Dont say anything else..',
    'Edward: What do you mean?',
    "Lucid: Open your fu**ing door.. I'm outside"]
    print(cycle(current_conversation, working_memory))
demo()