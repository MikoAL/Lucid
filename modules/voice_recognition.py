import queue
from typing import Callable, List
import time
import numpy as np
import sounddevice as sd
from Levenshtein import distance
import whisperx
import logging
from rich.logging import RichHandler
FORMAT = "%(message)s"  
logging.basicConfig(
    level=logging.INFO, format=FORMAT, datefmt="[%X]", handlers=[RichHandler(rich_tracebacks=True,)]
)
logger = logging.getLogger("rich")
import os
from dotenv import load_dotenv

script_dir = r"C:\Users\User\Desktop\Projects\Lucid"
os.chdir(script_dir)
load_dotenv()
os.environ["TF_ENABLE_ONEDNN_OPTS"]='0'

import vad

VAD_MODEL_PATH = r"C:\Users\User\Desktop\Projects\Lucid\modules\models\silero_vad.onnx"
#VAD_MODEL_PATH = r"C:\Users\Miko_AL\Desktop\Projects\Lucid\voice_recognition\models\silero_vad.onnx"
SAMPLE_RATE = 16000  # Sample rate for input stream
VAD_SIZE = 50  # Milliseconds of sample for Voice Activity Detection (VAD)
VAD_THRESHOLD = 0.80  # Threshold for VAD detection
BUFFER_SIZE = 600  # Milliseconds of buffer before VAD detection
PAUSE_LIMIT = 500  # Milliseconds of pause allowed before processing
WAKE_WORD = None  # Wake word for activation
SIMILARITY_THRESHOLD = 2  # Threshold for wake word similarity

import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline


device = "cuda" 
audio_file = r"C:\Users\User\Desktop\Projects\Lucid\Test_Audio.wav"
batch_size = 2 # reduce if low on GPU mem
compute_type = "int8" # change to "int8" if low on GPU mem (may reduce accuracy)

# 1. Transcribe with original whisper (batched)
logger.info(f"Loading whisper models...")
model = whisperx.load_model("Systran/faster-distil-whisper-medium.en", device, compute_type=compute_type)
model_a, metadata = whisperx.load_align_model(language_code="en", device=device)
diarize_model = whisperx.DiarizationPipeline('pyannote/speaker-diarization-3.1', use_auth_token=os.getenv("HUGGINGFACE_READ_KEY"), device=device)
logger.info(f"Models loaded.")

def pipe(audio):
    global model, model_a, metadata
    logger.info(f"Transcribing audio...")
    result = model.transcribe(audio, batch_size=batch_size)
    #logger.info(f"Transcription complete. Aligning...")
    #result = whisperx.align(result["segments"], model_a, metadata, audio, device, return_char_alignments=False)
    text_result = ""
    for i in result["segments"]:
        text_result += i["text"] + " "
    return text_result.strip()
class VoiceRecognition:
    def __init__(
        self, wake_word: str | None = None, function: Callable = print
    ) -> None:
        """
        Initializes the VoiceRecognition class, setting up necessary models, streams, and queues.

        This class is not thread-safe, so you should only use it from one thread. It works like this:
        1. The audio stream is continuously listening for input.
        2. The audio is buffered until voice activity is detected. This is to make sure that the
            entire sentence is captured, including before voice activity is detected.
        2. While voice activity is detected, the audio is stored, together with the buffered audio.
        3. When voice activity is not detected after a short time (the PAUSE_LIMIT), the audio is
            transcribed. If voice is detected again during this time, the timer is reset and the
            recording continues.
        4. After the voice stops, the listening stops, and the audio is transcribed.
        5. If a wake word is set, the transcribed text is checked for similarity to the wake word.
        6. The function is called with the transcribed text as the argument.
        7. The audio stream is reset (buffers cleared), and listening continues.

        Args:
            wake_word (str, optional): The wake word to use for activation. Defaults to None.
            func (Callable, optional): The function to call when the wake word is detected. Defaults to print.
        """

        self._setup_audio_stream()
        self._setup_vad_model()
        #self._setup_asr_model()

        # Initialize sample queues and state flags
        self.samples = []
        self.sample_queue = queue.Queue()
        self.buffer = queue.Queue(maxsize=BUFFER_SIZE // VAD_SIZE)
        self.recording_started = False
        self.gap_counter = 0
        self.wake_word = wake_word
        self.func = function

    def _setup_audio_stream(self):
        """
        Sets up the audio input stream with sounddevice.
        """
        self.input_stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=1,
            callback=self.audio_callback,
            blocksize=int(SAMPLE_RATE * VAD_SIZE / 1000),
        )

    def _setup_vad_model(self):
        """
        Loads the Voice Activity Detection (VAD) model.
        """
        self.vad_model = vad.VAD(model_path=VAD_MODEL_PATH)


    def audio_callback(self, indata, frames, time, status):
        """
        Callback function for the audio stream, processing incoming data.
        """
        data = indata.copy()
        data = data.squeeze()  # Reduce to single channel if necessary
        vad_confidence = self.vad_model.process_chunk(data) > VAD_THRESHOLD
        self.sample_queue.put((data, vad_confidence))

    def start(self):
        """
        Starts the Glados voice assistant, continuously listening for input and responding.
        """
        logger.info("Starting Listening...")
        self.input_stream.start()
        logger.info("Listening Running")
        self._listen_and_respond()

    def _listen_and_respond(self):
        """
        Listens for audio input and responds appropriately when the wake word is detected.
        """
        logger.info("Listening...")
        while True:  # Loop forever, but is 'paused' when new samples are not available
            sample, vad_confidence = self.sample_queue.get()
            self._handle_audio_sample(sample, vad_confidence)

    def _handle_audio_sample(self, sample, vad_confidence):
        """
        Handles the processing of each audio sample.
        """
        if not self.recording_started:
            self._manage_pre_activation_buffer(sample, vad_confidence)
        else:
            self._process_activated_audio(sample, vad_confidence)

    def _manage_pre_activation_buffer(self, sample, vad_confidence):
        """
        Manages the buffer of audio samples before activation (i.e., before the voice is detected).
        """
        if self.buffer.full():
            self.buffer.get()  # Discard the oldest sample to make room for new ones
        self.buffer.put(sample)

        if vad_confidence:  # Voice activity detected
            self.samples = list(self.buffer.queue)
            self.recording_started = True

    def _process_activated_audio(self, sample: np.ndarray, vad_confidence: bool):
        """
        Processes audio samples after activation (i.e., after the wake word is detected).

        Uses a pause limit to determine when to process the detected audio. This is to
        ensure that the entire sentence is captured before processing, including slight gaps.
        """

        self.samples.append(sample)

        if not vad_confidence:
            self.gap_counter += 1
            if self.gap_counter >= PAUSE_LIMIT // VAD_SIZE:
                self._process_detected_audio()
        else:
            self.gap_counter = 0

    def _wakeword_detected(self, text: str) -> bool:
        """
        Calculates the nearest Levenshtein distance from the detected text to the wake word.

        This is used as 'Glados' is not a common word, and Whisper can sometimes mishear it.
        """
        words = text.split()
        closest_distance = min(
            [distance(word.lower(), self.wake_word) for word in words]
        )
        return closest_distance < SIMILARITY_THRESHOLD

    def _process_detected_audio(self):
        """
        Processes the detected audio and generates a response.
        """
        logger.info("Detected pause after speech. Processing...")

        logger.info("Stopping listening...")
        self.input_stream.stop()

        #detected_text = self.asr(self.samples)
        audio = np.concatenate(self.samples)
        
        # self.reset()
        # self.input_stream.start()
        logger.info("Captured audio.")
        start_transcribe = time.time()
        detected_text = pipe(audio)
        logger.info(f"Successfully transcribed: '{detected_text}' in {(time.time() - start_transcribe):.2f} seconds.")
        

        if detected_text:
            logger.info(f"Detected: '{detected_text}'")

            if self.wake_word is not None:
                if self._wakeword_detected(detected_text):
                    logger.info("Wake word detected!")
                    self.func(detected_text)
                else:
                    logger.info("No wake word detected. Ignoring...")
            else:
                self.func(detected_text)

        self.reset()
        self.input_stream.start()


    def reset(self):
        """
        Resets the recording state and clears buffers.
        """
        logger.info("Resetting recorder...")
        self.recording_started = False
        self.samples.clear()
        self.gap_counter = 0
        with self.buffer.mutex:
            self.buffer.queue.clear()


if __name__ == "__main__":
    demo = VoiceRecognition(wake_word=WAKE_WORD)
    demo.start()