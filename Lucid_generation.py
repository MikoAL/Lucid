# Use a pipeline as a high-level helper
import torch
import requests

# For local streaming, the websockets are hosted without ssl - http://
host = 'localhost:5000'
url = f"http://{host}/v1/completions"
headers = {
    "Content-Type": "application/json"
}

# For reverse-proxied streaming, the remote will likely host with ssl - https://
# URI = 'https://your-uri-here.trycloudflare.com/api/v1/generate'

def llm(prompt,temperature=1.5):
    global host, url, headers
    request = {
    "prompt": prompt,
    "max_tokens": 2000,
    "temperature": temperature,
    "top_p": 0.9,
    "seed": 10,
    "stream": False,
}


    response = requests.post(url, headers=headers, json=request, verify=False, stream=False)


    if response.status_code == 200:
        result = response.json()['choices'][0]['text']
        return result


"""
from transformers import AutoTokenizer, pipeline, logging,  AutoModelForCausalLM
from auto_gptq import AutoGPTQForCausalLM, BaseQuantizeConfig

model_name_or_path = "TheBloke/MythoLogic-Mini-7B-GPTQ"
model_basename = "gptq_model-4bit-128g"

use_triton = False

tokenizer = AutoTokenizer.from_pretrained(model_name_or_path, use_fast=True)
model = AutoModelForCausalLM.from_pretrained(model_name_or_path, torch_dtype=torch.float16, device_map="auto")
#model = AutoGPTQForCausalLM.from_quantized(model_name_or_path,
#        model_basename=model_basename,
#        use_safetensors=True,
#        trust_remote_code=False,
#        device="cuda:0",
#        use_triton=use_triton,
#        quantize_config=None)


prompt = "Tell me about AI"
prompt_template=f'''Below is an instruction that describes a task. Write a response that appropriately completes the request.

### Instruction: {prompt}

### Response:
'''

#print("\n\n*** Generate:")

#input_ids = tokenizer(prompt_template, return_tensors='pt').input_ids.cuda()
#output = model.generate(inputs=input_ids, temperature=0.7, max_new_tokens=512)
#print(tokenizer.decode(output[0]))

# Inference can also be done using transformers' pipeline

# Prevent printing spurious transformers error when using pipeline with AutoGPTQ
logging.set_verbosity(logging.CRITICAL)

#print("*** Pipeline:")


#print(pipe(prompt_template)[0]['generated_text'])
def llm(text):
    pipe = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    max_new_tokens=512,
    temperature=0.7,
    top_p=0.95,
    repetition_penalty=1.15,
    )
    return pipe(text)[0]['generated_text']
#print('ready')
"""