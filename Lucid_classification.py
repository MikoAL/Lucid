

from transformers import pipeline
classifier = pipeline("zero-shot-classification", model="MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli")

from transformers import (
    TokenClassificationPipeline,
    AutoModelForTokenClassification,
    AutoTokenizer,
)
from transformers.pipelines import AggregationStrategy
import numpy as np

# Define keyphrase extraction pipeline
class KeyphraseExtractionPipeline(TokenClassificationPipeline):
    def __init__(self, model, *args, **kwargs):
        super().__init__(
            model=AutoModelForTokenClassification.from_pretrained(model),
            tokenizer=AutoTokenizer.from_pretrained(model),
            *args,
            **kwargs
        )

    def postprocess(self, all_outputs):
        results = super().postprocess(
            all_outputs=all_outputs,
            aggregation_strategy=AggregationStrategy.SIMPLE,
        )
        return np.unique([result.get("word").strip() for result in results])

# Load pipeline
model_name = "ml6team/keyphrase-extraction-kbir-inspec"
keyword_extractor = KeyphraseExtractionPipeline(model=model_name)

#keywords = pipeline("token-classification", model="ml6team/keyphrase-extraction-kbir-inspec")

def zeroshot_classification(sentence: str, labels: list, multi_label=False):
    sequence_to_classify = sentence
    output = classifier(sequence_to_classify,labels, multi_label=multi_label)
    return output

def message_type_classification(sentence: str):
    message_types = ["command", "chit-chat", "question", "greeting", "feedback", "information", "problem"]
    return  zeroshot_classification(sentence, message_types)['labels'][0]

def positive_negative_classification(sentence: str):
    types = ['positive','neutral','negative']
    return zeroshot_classification(sentence, types)['labels'][0] 

#print(keyword_extractor('New systems are online now, yay, I hope so anyways, it is a keyword extraction system thingy'))
    