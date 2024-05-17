import re
import subprocess
from typing import List, Optional
import os

import numpy as np
import onnxruntime
import sounddevice as sd

from piper import PiperVoice

import threading
from threading import Event, Thread
from queue import Queue

import time
from datetime import datetime
import logging
logging.basicConfig(level=logging.INFO)

script_location = os.path.dirname(os.path.realpath(__file__))
os.chdir("C:\Program Files\eSpeak NG")
# Constants
MAX_WAV_VALUE = 32767.0
RATE = 22050

# Settings
MODEL_PATH = f"{script_location}\\tts\models\glados.onnx"
USE_CUDA = False

# Conversions
PAD = "_"  # padding (0)
BOS = "^"  # beginning of sentence
EOS = "$"  # end of sentence
PHONEME_ID_MAP = {
    " ": [3],
    "!": [4],
    '"': [150],
    "#": [149],
    "$": [2],
    "'": [5],
    "(": [6],
    ")": [7],
    ",": [8],
    "-": [9],
    ".": [10],
    "0": [130],
    "1": [131],
    "2": [132],
    "3": [133],
    "4": [134],
    "5": [135],
    "6": [136],
    "7": [137],
    "8": [138],
    "9": [139],
    ":": [11],
    ";": [12],
    "?": [13],
    "X": [156],
    "^": [1],
    "_": [0],
    "a": [14],
    "b": [15],
    "c": [16],
    "d": [17],
    "e": [18],
    "f": [19],
    "g": [154],
    "h": [20],
    "i": [21],
    "j": [22],
    "k": [23],
    "l": [24],
    "m": [25],
    "n": [26],
    "o": [27],
    "p": [28],
    "q": [29],
    "r": [30],
    "s": [31],
    "t": [32],
    "u": [33],
    "v": [34],
    "w": [35],
    "x": [36],
    "y": [37],
    "z": [38],
    "æ": [39],
    "ç": [40],
    "ð": [41],
    "ø": [42],
    "ħ": [43],
    "ŋ": [44],
    "œ": [45],
    "ǀ": [46],
    "ǁ": [47],
    "ǂ": [48],
    "ǃ": [49],
    "ɐ": [50],
    "ɑ": [51],
    "ɒ": [52],
    "ɓ": [53],
    "ɔ": [54],
    "ɕ": [55],
    "ɖ": [56],
    "ɗ": [57],
    "ɘ": [58],
    "ə": [59],
    "ɚ": [60],
    "ɛ": [61],
    "ɜ": [62],
    "ɞ": [63],
    "ɟ": [64],
    "ɠ": [65],
    "ɡ": [66],
    "ɢ": [67],
    "ɣ": [68],
    "ɤ": [69],
    "ɥ": [70],
    "ɦ": [71],
    "ɧ": [72],
    "ɨ": [73],
    "ɪ": [74],
    "ɫ": [75],
    "ɬ": [76],
    "ɭ": [77],
    "ɮ": [78],
    "ɯ": [79],
    "ɰ": [80],
    "ɱ": [81],
    "ɲ": [82],
    "ɳ": [83],
    "ɴ": [84],
    "ɵ": [85],
    "ɶ": [86],
    "ɸ": [87],
    "ɹ": [88],
    "ɺ": [89],
    "ɻ": [90],
    "ɽ": [91],
    "ɾ": [92],
    "ʀ": [93],
    "ʁ": [94],
    "ʂ": [95],
    "ʃ": [96],
    "ʄ": [97],
    "ʈ": [98],
    "ʉ": [99],
    "ʊ": [100],
    "ʋ": [101],
    "ʌ": [102],
    "ʍ": [103],
    "ʎ": [104],
    "ʏ": [105],
    "ʐ": [106],
    "ʑ": [107],
    "ʒ": [108],
    "ʔ": [109],
    "ʕ": [110],
    "ʘ": [111],
    "ʙ": [112],
    "ʛ": [113],
    "ʜ": [114],
    "ʝ": [115],
    "ʟ": [116],
    "ʡ": [117],
    "ʢ": [118],
    "ʦ": [155],
    "ʰ": [145],
    "ʲ": [119],
    "ˈ": [120],
    "ˌ": [121],
    "ː": [122],
    "ˑ": [123],
    "˞": [124],
    "ˤ": [146],
    "̃": [141],
    "̧": [140],
    "̩": [144],
    "̪": [142],
    "̯": [143],
    "̺": [152],
    "̻": [153],
    "β": [125],
    "ε": [147],
    "θ": [126],
    "χ": [127],
    "ᵻ": [128],
    "↑": [151],
    "↓": [148],
    "ⱱ": [129],
}


class Synthesizer:
    """Synthesizer, based on the VITS model.

    Trained using the Piper project (https://github.com/rhasspy/piper)

    Attributes:
    -----------
    session: onnxruntime.InferenceSession
        The loaded VITS model.
    id_map: dict
        A dictionary mapping phonemes to ids.

    Methods:
    --------
    __init__(self, model_path, use_cuda):
        Initializes the Synthesizer class, loading the VITS model.

    _initialize_session(self, model_path, use_cuda):
        Initializes the VITS model.

    generate_speech_audio(self, text):
        Generates speech audio from the given text.

    _phonemizer(self, input_text):
        Converts text to phonemes using espeak-ng.

    _phonemes_to_ids(self, phonemes):
        Converts the given phonemes to ids.

    _synthesize_ids_to_raw(self, phoneme_ids, speaker_id, length_scale, noise_scale, noise_w):
        Synthesizes raw audio from phoneme ids.

    say_phonemes(self, phonemes):
        Converts the given phonemes to audio.
    """

    def __init__(self, model_path: str, use_cuda: bool):
        self.session = self._initialize_session(model_path, use_cuda)
        self.id_map = PHONEME_ID_MAP

    def _initialize_session(
        self, model_path: str, use_cuda: bool
    ) -> onnxruntime.InferenceSession:
        providers = ["CPUExecutionProvider"]
        if use_cuda:
            providers = ["CUDAExecutionProvider"]

        return onnxruntime.InferenceSession(
            str(model_path),
            sess_options=onnxruntime.SessionOptions(),
            providers=providers,
        )

    def generate_speech_audio(self, text: str) -> np.ndarray:
        phonemes = self._phonemizer(text)
        audio = []
        for sentence in phonemes:
            audio_chunk = self._say_phonemes(sentence)
            audio.append(audio_chunk)
        if audio:
            return np.concatenate(audio, axis=1).T
        return np.array([])

    def _phonemizer(self, input_text: str) -> List[str]:
        """Converts text to phonemes using espeak-ng."""

        try:
            # Prepare the command to call espeak with the desired flags
            command = [
                "espeak-ng",  # 'C:\Program Files\eSpeak NG\espeak-ng.exe',
                "--ipa=2",  # Output phonemes in IPA format
                "-q",  # Quiet, no output except the phonemes
                "--stdout",  # Output the phonemes to stdout
                input_text,
            ]

            # Execute the command and capture the output
            result = subprocess.run(
                command, capture_output=True, text=True, check=True, encoding="utf-8"
            )

            phonemes = result.stdout.strip().replace("\n", ".").replace("  ", " ")
            phonemes = re.sub(r"_+", "_", phonemes)
            phonemes = re.sub(r"_ ", " ", phonemes)
            return phonemes.splitlines()

        except subprocess.CalledProcessError as e:
            print("Error in phonemization:", str(e))
            return []

    def _phonemes_to_ids(self, phonemes: str) -> List[int]:
        """Phonemes to ids."""

        ids: List[int] = list(self.id_map[BOS])

        for phoneme in phonemes:
            if phoneme not in self.id_map:
                continue

            ids.extend(self.id_map[phoneme])
            ids.extend(self.id_map[PAD])
        ids.extend(self.id_map[EOS])

        return ids

    def _synthesize_ids_to_raw(
        self,
        phoneme_ids: List[int],
        length_scale: Optional[float] = 1.0,
        noise_scale: Optional[float] = 0.667,
        noise_w: Optional[float] = 0.8,  # 0.8
    ) -> bytes:
        """Synthesize raw audio from phoneme ids."""

        phoneme_ids_array = np.expand_dims(np.array(phoneme_ids, dtype=np.int64), 0)
        phoneme_ids_lengths = np.array([phoneme_ids_array.shape[1]], dtype=np.int64)

        scales = np.array(
            [noise_scale, length_scale, noise_w],
            dtype=np.float32,
        )

        # Synthesize through Onnx
        audio = self.session.run(
            None,
            {
                "input": phoneme_ids_array,
                "input_lengths": phoneme_ids_lengths,
                "scales": scales,
            },
        )[0].squeeze((0, 1))

        return audio

    def _say_phonemes(self, phonemes: str) -> bytes:
        """Say phonemes."""

        phoneme_ids = self._phonemes_to_ids(phonemes)
        audio = self._synthesize_ids_to_raw(phoneme_ids)

        return audio
class TTSEngine:
    def __init__(self, synthesizer, tts_rate):
        self.synthesizer = synthesizer
        self.tts_rate = tts_rate
        self.tts_text_queue = []
        self.tts_audio_queue = []
        self.tts_is_playing = False
        self.tts_audio_queue_text = []
        self.current_audio_start_time = 0
        self.current_audio_estimated_end_time = 0
        self.current_audio_text = ""

    def thread_logic(self):
        while True:
            start_time = time.time()
            time.sleep(0.01)
            #logging.info(f"tts_text_queue: {self.tts_text_queue}\ntts_audio_queue: {self.tts_audio_queue}")
            
            if time.time() > self.current_audio_estimated_end_time:
                self.tts_is_playing = False
            else:
                self.tts_is_playing = True


            if (not self.tts_is_playing) and self.tts_audio_queue:
                audio = self.tts_audio_queue.pop(0)
                self.current_audio_text = self.tts_audio_queue_text.pop(0)
                self.current_audio_start_time = time.time()
                sd.play(audio, self.tts_rate)
                self.current_audio_estimated_end_time = (time.time() + (len(audio) / self.tts_rate)*1.1)
                self.tts_is_playing = True
                logging.info(f"Estimated end time: {datetime.fromtimestamp(self.current_audio_estimated_end_time)}")

                
            if self.tts_text_queue:
                response = self.tts_text_queue.pop(0)
                logging.info(f"Generating audio for '{response}'.")
                audio = self.synthesizer.generate_speech_audio(response)
                self.tts_audio_queue.append(audio)
                self.tts_audio_queue_text.append(response)
                logging.info(f"Added '{response}' to the TTS audio queue.")

            #logging.info(f"\nTotal response time: {(time.time() - start_time):.2f} seconds.")

    def add_to_queue(self, text):
        """Adds the given text to the TTS queue."""
        #logging.info(f"Adding '{text}' to the TTS queue.")
        self.tts_text_queue.append(text)
        logging.info(f"Successfully added '{text}' to the TTS queue.")

    def interrupt_tts_playback(self):
        """Interrupts the TTS playback and returns the last played text."""
        logging.info("Interrupting TTS playback.")
        logging.info(f"Skipped Text Queue: {self.tts_text_queue}\nSkipped Audio Queue: {self.tts_audio_queue_text}")
        self.tts_audio_queue.clear()
        self.tts_text_queue.clear()
        self.tts_is_playing = False
        sd.stop()
        logging.info(f"Last played text: {self.current_audio_text}")
        
        last_played_text = self.current_audio_text
        logging.info(f"Played {(time.time() - self.current_audio_start_time):.2f} seconds of audio.")
        #logging.info(f"Start Time: {self.current_audio_start_time}\nEnd Time: {self.current_audio_estimated_end_time}")
        #logging.info(f"Estimated time needed: {(self.current_audio_estimated_end_time - self.current_audio_start_time):.2f} seconds.")
        try:
            played_percentage = (time.time() - self.current_audio_start_time) / (self.current_audio_estimated_end_time - self.current_audio_start_time)
        except ZeroDivisionError:
            played_percentage = 0
        full_index = len(last_played_text)
        logging.info(f"Played Percentage: {played_percentage}")
        played_index = round(full_index * played_percentage)
        #logging.info(f"Played Index: {played_index}")
        if played_index > full_index:
            played_index = full_index
            
        self.tts_text_queue = []
        self.tts_audio_queue = []
        self.tts_is_playing = False
        self.tts_audio_queue_text = []
        self.current_audio_start_time = 0
        self.current_audio_estimated_end_time = 0
        self.current_audio_text = ""
        logging.info(f"Played text: {last_played_text[:played_index]}")
        return last_played_text[:played_index]


if __name__ == "__main__":
    
    # Create a Synthesizer instance
    synthesizer = Synthesizer(model_path=f"{script_location}/models/glados.onnx", use_cuda=False)

    # Create a TTS engine instance
    tts_engine = TTSEngine(synthesizer, tts_rate=22050)

    logging.info("Test starting...")

    logging.info("Testing Synthesizer.")

    text="Hello, world!"
    audio = synthesizer.generate_speech_audio(text)
    duration = len(audio) / 22050.0
    logging.info(f"Audio duration: {duration:.2f} seconds.")
    sd.play(audio, 22050)

    threading.Thread(target=tts_engine.thread_logic).start()
    # Add some responses to the queue
    tts_engine.add_to_queue("Hello, this is a test.")
    #time.sleep(5)
    logging.info("Adding more responses to the queue.")
    tts_engine.add_to_queue("I am trying to synthesize speech.")
    tts_engine.add_to_queue("This is the third response.")
    logging.info("Responses added to the queue.")
    # Wait for a few seconds to allow the TTS engine to process the responses
    logging.info("Waiting for the TTS engine to process the responses.")
    #time.sleep(15)
    logging.info("Adding more responses to the queue.")
    tts_engine.interrupt_tts_playback()
    # Interrupt the TTS playback
    tts_engine.add_to_queue("This will get interrupted. I think, I am not sure.")
    time.sleep(2.5)
    logging.info("Interrupting TTS playback.")
    logging.info(f"Played Text: {tts_engine.interrupt_tts_playback()}")


    print("Test completed.")