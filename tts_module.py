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
from threading import Event, Thread
from queue import Queue
script_location = os.path.dirname(os.path.realpath(__file__))
#os.chdir(script_location)
logging.basicConfig(level=logging.INFO)

class TTSEngine:
    def __init__(self, synthesizer, tts_rate):
        self.synthesizer = synthesizer
        self.tts_rate = tts_rate
        self.tts_text_queue = Queue()
        self.tts_audio_queue = Queue()
        self.interrupt_tts = False
        self.tts_is_playing = False


    def thread_logic(self):
        while True:
            
            start_time = time.time()
            logging.info(f"tts_text_queue: {(self.tts_text_queue)}\ntts_audio_queue: {(self.tts_audio_queue)}")
            while not (self.tts_text_queue.empty() and self.tts_audio_queue.empty() and not self.tts_is_playing):
                
                try:
                    sd_status = sd.get_status()
                    self.tts_is_playing = True
                except RuntimeError as e:
                    if str(e) == "play()/rec()/playrec() was not called yet":
                        self.tts_is_playing = False
                logging.info(f"tts_is_playing: {self.tts_is_playing}, interrupt_tts: {self.interrupt_tts}")
                if self.interrupt_tts:
                    sd.stop()
                    with self.tts_audio_queue.mutex:
                        self.tts_audio_queue.queue.clear()
                    with self.tts_text_queue.mutex:
                        self.tts_text_queue.queue.clear()
                    self.interrupt_tts = False

                if not self.tts_is_playing:
                    with self.tts_text_queue.mutex:
                        if not self.tts_text_queue.empty():
                            response = self.tts_text_queue.get()
                            audio = self.synthesizer.generate_speech_audio(response)
                            with self.tts_audio_queue.mutex:
                                self.tts_audio_queue.put(audio)

                    if not self.tts_audio_queue.empty():
                        with self.tts_audio_queue.mutex:
                            audio = self.tts_audio_queue.get()
                        stream = sd.play(audio, self.tts_rate)

                        # Wait for the audio playback to finish
                        while stream.active:
                            time.sleep(0.1)

            logging.info(f"\nTotal response time: {(time.time() - start_time):.2f} seconds.")

    def add_to_queue(self, text):
        logging.info(f"Adding '{text}' to the TTS queue.")
        self.tts_text_queue.put(text)

    def interrupt_tts_playback(self):
        self.interrupt_tts = True
        
if __name__ == "__main__":
    # Create a dummy Synthesizer instance
    print(sd.get_status)
    synthesizer = Synthesizer(model_path=f"{script_location}/tts/models/glados.onnx", use_cuda=False)

    # Create a TTS engine instance
    tts_engine = TTSEngine(synthesizer, tts_rate=22050)

    logging.info("Test starting...")

    logging.info("Testing Synthesizer.")

    text="Hello, world!"
    audio = synthesizer.generate_speech_audio(text)
    sd.play(audio, 22050)

    threading.Thread(target=tts_engine.thread_logic).start()
    # Add some responses to the queue
    tts_engine.add_to_queue("Hello, this is a test.")
    tts_engine.add_to_queue("I am trying to synthesize speech.")
    tts_engine.add_to_queue("This is the third response.")
    logging.info("Responses added to the queue.")
    # Wait for a few seconds to allow the TTS engine to process the responses
    time.sleep(5)

    # Interrupt the TTS playback
    logging.info("Interrupting TTS playback.")
    tts_engine.interrupt_tts_playback()


    print("Test completed.")