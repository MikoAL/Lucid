import os
import torch
from openvoice import se_extractor
from openvoice.api import ToneColorConverter
# Get the absolute path of the script's directory
script_dir = os.path.dirname(os.path.realpath(__file__))
# Change the working directory to the script's directory
os.chdir(script_dir)

ckpt_converter = r".\checkpoints_v2\converter"
device = "cuda:0" if torch.cuda.is_available() else "cpu"
output_dir = 'outputs'

tone_color_converter = ToneColorConverter(f'{ckpt_converter}\config.json', device=device)
tone_color_converter.load_ckpt(f'{ckpt_converter}\checkpoint.pth')

os.makedirs(output_dir, exist_ok=True)

reference_speaker = 'resources/Ana.wav' # This is the voice you want to clone
target_se, audio_name = se_extractor.get_se(reference_speaker, tone_color_converter, vad=False)

import time
from openvoice.api import BaseSpeakerTTS, ToneColorConverter

ckpt_base = 'checkpoints/base_speakers/EN'
ckpt_converter = 'checkpoints/converter'
save_path = f'{output_dir}/output_en_default.wav'
base_speaker_tts = BaseSpeakerTTS(f'{ckpt_base}/config.json', device=device)
base_speaker_tts.load_ckpt(f'{ckpt_base}/checkpoint.pth')

def TTS(text):
    src_path = f'{output_dir}/tmp.wav'
    start_time = time.time()
    base_speaker_tts.tts(text, src_path, speaker='default', language='English', speed=1.0)
    print(f"Base speaker TTS time cost: {time.time() - start_time:.2f}s")
    source_se = torch.load(f'{ckpt_base}/en_default_se.pth').to(device)
    # Run the tone color converter
    encode_message = "@MyShell"
    tone_color_converter.convert(
        audio_src_path=src_path, 
        src_se=source_se, 
        tgt_se=target_se, 
        output_path=save_path,
        message=encode_message)
    time_cost = time.time() - start_time
    print(f"Total time cost: {time_cost:.2f}s")
    return save_path

TTS("Hello, my name is Ana.")
TTS("I am a voice clone of Ana.")