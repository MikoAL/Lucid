from transformers import pipeline
classifier = pipeline("text-classification",model='bhadresh-savani/distilbert-base-uncased-emotion', top_k=1)
# prediction = classifier("Of course, I can hear you perfectly. How can I help you today, Miko?", )
# print(prediction[0])

def emotion_dectection(text):
    emotion = classifier(text)[0][0]['label']
    
    return emotion

"""[[
{'label': 'sadness', 'score': 0.0006792712374590337}, 
{'label': 'joy', 'score': 0.9959300756454468}, 
{'label': 'love', 'score': 0.0009452480007894337}, 
{'label': 'anger', 'score': 0.0018055217806249857}, 
{'label': 'fear', 'score': 0.00041110432357527316}, 
{'label': 'surprise', 'score': 0.0002288572577526793}
]]"""



