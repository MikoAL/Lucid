from transformers import AutoTokenizer, AutoModelForCausalLM
import transformers
import torch
from langchain import HuggingFacePipeline
model = "mosaicml/mpt-7b-8k-instruct"
#model = AutoModelForCausalLM.from_pretrained(r"C:\Users\User\Desktop\Projects\AIGF\LangChain\models\llm\tiiuae_falcon-7b-instruct")
tokenizer = AutoTokenizer.from_pretrained(model)
#input_ids = input_ids.to('cuda')

llm = HuggingFacePipeline.from_model_id(
    model_id=model,
    task="text-generation",
    model_kwargs={
        "temperature": 0.00,
        #"max_length": 2048,
        #"max_new_tokens":512,
        #"min_length": 20,
        "trust_remote_code": True,
        "device_map":"auto",
        "load_in_8bit":True,
        #'top_p': 0.1,
		#'typical_p': 1,
		#'repetition_penalty': 1.30,
        'no_repeat_ngram_size': 3,
        #'bad_words_ids':[[37]],
        #'num_beams':2, this breaks stuff, idk why
        
  },
    
)