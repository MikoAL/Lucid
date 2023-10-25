

from transformers import pipeline
classifier = pipeline("zero-shot-classification", model="MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli")


def zeroshot_classification(sentence: str, labels: list, multi_label=False):
    sequence_to_classify = sentence
    output = classifier(sequence_to_classify,labels, multi_label=multi_label)
    return output

def message_type_classification(sentence: str):
    message_types = ["command", "chit-chat", "question", "greeting", "feedback", "information", "problem"]
    return  zeroshot_classification(sentence, message_types)['labels'][0]

#print(message_type_classification('I\'m so tired.'))


    