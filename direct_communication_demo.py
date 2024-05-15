import os
import time
import transformers
import torch
from transformers.tools.agents import resolve_tools, evaluate, get_tool_creation_code, StopSequenceCriteria
import transformers.tools.agents
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers.generation import StoppingCriteriaList
from .tts import Synthesizer
import logging
import sounddevice as sd
import threading
from queue import Queue

tts_rate = 22050
prompt_path = r".\Prompts"

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

def single_turn_conversation(prompt, model, tokenizer, max_length=256, temperature=0.85, top_k=50, top_p=0.95):
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
                             max_length=max_length,
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
        conversation_string += "\nWould the AI respond to this conversation, or stay silent? Please answer with a simple 'Yes' for respond and 'No' for staying silent."
    response = single_turn_conversation(conversation_string, model, tokenizer)
    if response[:3].lower() == "yes":
        return True
    else:
        return False

# ===== ===== ===== #

def direct_communication_logic(new_user_input, direct_communication_model, direct_communication_tokenizer):
    synthesizer = Synthesizer(model_path="./models/glados.onnx", use_cuda=False)
    tts_is_playing = False
    tts_audio_queue = []
    time.sleep(0.03)
    current_conversation = [{'role':'system','content':f"You are Lucid, here are some information on Lucid:\n{Lucid_prompt_card}\nPlease respond as if you were Lucid."}]
    while True:
        # Check for new user input
        if not new_user_input.empty():
            user_input = new_user_input.get()
            current_conversation.append({'role': 'user', 'content': user_input})

        if respond_or_not(current_conversation):
            stopping_criteria = StoppingCriteriaList([StopSequenceCriteria(["<|end|>"], tokenizer)])
            inputs = direct_communication_tokenizer.apply_chat_template(current_conversation, tokenize=False, add_generation_prompt=False )
            encoded_inputs = direct_communication_tokenizer(inputs, return_tensors="pt").to(device_for_tools)
            src_len = encoded_inputs["input_ids"].shape[1]
            # Generate the response
            outputs = direct_communication_model.generate(encoded_inputs["input_ids"],
                                    max_length=512,
                                    temperature=0.85,
                                    top_k=50,
                                    top_p=0.95,
                                    do_sample=True,
                                    stopping_criteria=stopping_criteria,)
            # Decode the response
            response = direct_communication_tokenizer.decode(outputs[0].tolist()[src_len:-1])
            tts_text_queue.append(response)
            while (tts_text_queue != []) and (tts_audio_queue != []):
                try:
                    sd.get_status()
                    tts_is_playing = True
                except RuntimeError as e:
                    if str(e) == "play()/rec()/playrec() was not called yet":
                        tts_is_playing = False

                if (tts_is_playing == True) and (interrupt_tts == True):
                    sd.stop()
                    tts_audio_queue = []
                    # Calculate the amount said
                elif (tts_is_playing == False):
                    if tts_audio_queue != []:
                        sd.play(tts_audio_queue.pop(0), tts_rate)
                    if tts_text_queue != []:
                        audio = synthesizer.generate_speech_audio(tts_text_queue.pop(0))
                        tts_audio_queue.append(audio)

            current_conversation.append({'role':'assistant','content':response})

# ===== ===== ===== #
# Main

from .voice_recognition.voice_recognition import VoiceRecognition
from threading import Event

user_text_queue = Queue()

def handle_user_input(text):
    logging.info(f"User: {text}")
    user_text_queue.put(text)
    new_user_input.set()

microphone = VoiceRecognition(wake_word=None, function=handle_user_input)
# Start microphone
threading.Thread(target=microphone.start).start()

new_user_input = user_text_queue