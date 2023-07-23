import Lucid_generation as generation
import Lucid_preprocess as preprocess
import Lucid_postprocess as postprocess
import Lucid_memory as memory



def main():
    
    history = []

    history_counter = 0 # Saves every time this counter hits 4.
    
    memory.init_session()
        
    while True:
        user_input= input('Miko: ')
        
        
        
        preprocessed_text = preprocess.preprocess(user_input,history)
        llm_response = generation.llm(preprocessed_text)
        llm_response = postprocess.postprocess(llm_response)
        history.append(f'Lucid: {llm_response}')
        history_counter += 2
        
        print(f'Lucid: {llm_response}')
        
        if history_counter == 4:
            history_counter = 0
            memory.save_history(history[-4:])
        if len(history) == 12:
            del history[:2]
        
            
            
main()
        
        

