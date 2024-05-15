import os
import time
import transformers
import torch
from transformers.tools.agents import resolve_tools, evaluate, get_tool_creation_code, StopSequenceCriteria
import transformers.tools.agents
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers.generation import StoppingCriteriaList
from tts import Synthesizer
import logging
import sounddevice as sd
import threading
from threading import Event
from queue import Queue
logging.basicConfig(level=logging.INFO)
tts_rate = 22050
prompt_path = r".\Prompts"
script_location = os.path.dirname(os.path.realpath(__file__))
os.chdir(script_location)
with open(f"{prompt_path}\Lucid_prompt_card.txt", 'r', encoding='utf-8') as f:
    Lucid_prompt_card = f.read()
# ===== ===== ===== #
# Utility functions

# Single Turn Conversation

device_for_tools = "cuda:1" if torch.cuda.is_available() else "cpu"

small_model = AutoModelForCausalLM.from_pretrained("unsloth/Phi-3-mini-4k-instruct-bnb-4bit", device_map="cuda:1", trust_remote_code=True)
small_tokenizer = AutoTokenizer.from_pretrained("unsloth/Phi-3-mini-4k-instruct-bnb-4bit")

model = AutoModelForCausalLM.from_pretrained("unsloth/llama-3-8b-Instruct-bnb-4bit", device_map="cuda:0")
tokenizer = AutoTokenizer.from_pretrained("unsloth/llama-3-8b-Instruct-bnb-4bit")
tokenizer_with_prefix_space = AutoTokenizer.from_pretrained("unsloth/llama-3-8b-Instruct-bnb-4bit", add_prefix_space=True)

def single_turn_conversation(prompt, model, tokenizer, max_new_tokens=256, temperature=0.85, top_k=50, top_p=0.95):
    global device_for_tools
    # Encode the prompt
    prompt_as_messages = [
        {"role": "user", "content": prompt},
    ]
    stopping_criteria = StoppingCriteriaList([StopSequenceCriteria(["<|end|>"], tokenizer)])
    inputs = tokenizer.apply_chat_template(prompt_as_messages, tokenize=False, add_generation_prompt=False )
    encoded_inputs = tokenizer(inputs, return_tensors="pt").to(device_for_tools)
    src_len = encoded_inputs["input_ids"].shape[1]
    # Generate the response
    outputs = model.generate(encoded_inputs["input_ids"],
                             max_new_tokens=max_new_tokens,
                             temperature=temperature,
                             top_k=top_k,
                             top_p=top_p,
                             do_sample=True,
                             stopping_criteria=stopping_criteria,)
    # Decode the response
    return tokenizer.decode(outputs[0].tolist()[src_len:-1])

def respond_or_not(conversation: dict) -> bool:
    """This function takes a conversation (The dictionary type with user, system, assistant...) and decides whether to respond or not."""
    conversation_string = "The following is a conversation between an AI assistant and a User:\n"
    for i in conversation:
        if i["role"] == "user":
            conversation_string += f"User: {i['content']}\n"
        elif i["role"] == "system":
            conversation_string += f"System: {i['content']}\n"
        elif i["role"] == "assistant":
            conversation_string += f"Assistant: {i['content']}\n"
    conversation_string += "\nWould the AI respond to this conversation, or stay silent? Please answer with a simple 'Yes.' for respond and 'No.' for staying silent."
    response = single_turn_conversation(conversation_string, small_model, small_tokenizer)
    logging.info(f"Conversation: \n{conversation_string}\n<End Of Conversation String>\n")
    logging.info(f"\nAI Response: \n{response}")
    if response[:3].lower() == "yes":
        logging.info("AI will respond.")
        return True
    else:
        logging.info("AI will not respond.")
        return False

# ===== ===== ===== #

def direct_communication_logic(new_user_input_event: Event, user_text_queue: Queue, direct_communication_model, direct_communication_tokenizer):
    global device_for_tools, tts_rate, synthesizer, tts_is_playing, tts_audio_queue, tts_text_queue, Lucid_prompt_card
    synthesizer = Synthesizer(model_path="./tts/models/glados.onnx", use_cuda=False)
    tts_is_playing = False
    tts_audio_queue = []
    tts_text_queue = []
    time.sleep(0.03)
    current_conversation = [{'role':'system','content':f"You are Lucid, here are some information on Lucid:\n{Lucid_prompt_card}\nPlease respond as if you were Lucid."}]
    while True:
        # Check for new user input
        if new_user_input_event.is_set():
            new_user_input_event.clear()
            logging.info("New user input detected.")
            start_time = time.time()
            user_input = user_text_queue.get()
            logging.info(f"Got User Input: {user_input}")
            interrupt_tts = True
            current_conversation.append({'role': 'user', 'content': user_input})

            start_respond_or_not = time.time()
            if respond_or_not(current_conversation):
                logging.info(f"\nRespond or Not took {(time.time() - start_respond_or_not):.2f} seconds.")
                stopping_criteria = StoppingCriteriaList([StopSequenceCriteria(["<|end|>"], tokenizer)])
                inputs = direct_communication_tokenizer.apply_chat_template(current_conversation, tokenize=False, add_generation_prompt=True)
                encoded_inputs = direct_communication_tokenizer(inputs, return_tensors="pt").to(device_for_tools)
                src_len = encoded_inputs["input_ids"].shape[1]
                # Generate the response
                start_generate = time.time()
                outputs = direct_communication_model.generate(encoded_inputs["input_ids"],
                                        max_new_tokens=512,
                                        temperature=0.85,
                                        top_k=50,
                                        top_p=0.95,
                                        do_sample=True,
                                        stopping_criteria=stopping_criteria,)
                logging.info(f"\nGenerate took {(time.time() - start_generate):.2f} seconds.")
                # Decode the response
                response = direct_communication_tokenizer.decode(outputs[0].tolist()[src_len:-1])
                logging.info(f"AI Response: {response}")
                tts_text_queue.append(response)
                counter = 0
                while (tts_text_queue != []) or (tts_audio_queue != []):
                    counter += 1
                    try:
                        sd.get_status()
                        tts_is_playing = True
                    except RuntimeError as e:
                        if str(e) == "play()/rec()/playrec() was not called yet":
                            tts_is_playing = False

                    if (tts_is_playing == True) and (interrupt_tts == True):
                        sd.stop()
                        tts_audio_queue = []
                        tts_text_queue = []
                        # Calculate the amount said
                        
                    elif (tts_is_playing == True) and (interrupt_tts == False):
                        audio = synthesizer.generate_speech_audio(tts_text_queue.pop(0))
                        tts_audio_queue.append(audio)
                        
                    elif (tts_is_playing == False) and (interrupt_tts == True):
                        pass
                    elif (tts_is_playing == False) and (interrupt_tts == False):
                        if tts_audio_queue != []:
                            sd.play(tts_audio_queue.pop(0), tts_rate)
                        else:
                            start_synth = time.time()
                            audio = synthesizer.generate_speech_audio(tts_text_queue.pop(0))
                            logging.info(f"\nGenerated audio for '{response}' in {time.time() - start_synth:.2f} seconds.")
                            sd.play(audio, tts_rate)
                    logging.info(f"Counter: {counter}")

                logging.info(f"\nTotal response time: {(time.time() - start_time):.2f} seconds.")
                current_conversation.append({'role':'assistant','content':response})
        

# ===== ===== ===== #
# Main

from voice_recognition import VoiceRecognition


user_text_queue = Queue()
new_user_input_event = Event()
def handle_user_input(text):
    global new_user_input_event, user_text_queue
    logging.info(f"User: {text}")
    user_text_queue.put(text)
    logging.info("User input added to queue.")
    new_user_input_event.set()

microphone = VoiceRecognition(wake_word=None, function=handle_user_input)

# Start microphone
#threading.Thread(target=microphone.start).start()

new_user_input_event.set()
user_text_queue.put("Hello, world!")
threading.Thread(target=direct_communication_logic, args=(new_user_input_event, user_text_queue, model, tokenizer)).start()