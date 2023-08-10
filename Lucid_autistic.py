from transformers import pipeline


classify_sentence = ''
def init_classify_sentence():
    global classify_sentence
    classify_sentence = pipeline("zero-shot-classification", model="MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli")

def react_to_sentence(sentence):
    global classify_sentence
    reaction_dict = {
        "friendly_greeting": "Smile and say 'Hello!'",
        "compliment": "Respond with a 'Thank you! I appreciate that.'",
        "question_about_interest": "Answer politely and briefly about your interests.",
        "complex_instructions": "Ask for clarification or request the person to simplify the instructions.",
        #"unexpected_topic": "Politely change the subject to something more comfortable for you.",
        "positive_news": "Respond with a positive comment like 'That's wonderful news!'",
        "negative_news": "Show empathy and support by saying 'I'm sorry to hear that.'",
        "talking_about_interests": "Engage in the conversation and share your thoughts about the topic.",
        "talking_about_feelings": "Feel free to express your feelings, even if they differ from others'.",
        #"give_compliments": "If you appreciate something about others, feel free to compliment them.",
        "questions_about_facts":"Respond with a clear, easy to understand reponse.",
        
    }


    # Zero-shot classification labels
    available_labels = list(reaction_dict.keys())

    # Zero-shot classification pipeline
    #classify_sentence = pipeline("zero-shot-classification", model="MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli")

    # Zero-shot classification to predict the label for the input sentence
    result = classify_sentence(f'what is the proper response for the sentense: {sentence}', available_labels, multi_label=False)

    # Retrieve the predicted label and find the corresponding reaction
    predicted_label = result["labels"][0]
    if predicted_label in reaction_dict:
        return reaction_dict[predicted_label]
    else:
        return "Listen carefully and respond politely based on your comfort level."

def run_tests():
    test_cases = [
        # Test case 1: Friendly greeting
        {
            "input": "Hi, how are you doing?",
            "expected_output": "Smile and say 'Hello!'",
        },
        # Test case 2: Compliment
        {
            "input": "You did a fantastic job on the project!",
            "expected_output": "Respond with a 'Thank you! I appreciate that.'",
        },
        # Test case 3: Question about interests
        {
            "input": "What do you like to do in your free time?",
            "expected_output": "Answer politely and briefly about your interests.",
        },
        # Test case 4: Complex instructions
        {
            "input": "Please follow these steps: A, B, C, and D.",
            "expected_output": "Ask for clarification or request the person to simplify the instructions.",
        },
        # Test case 5: Unexpected topic
        {
            "input": "I heard you're good at cooking! Tell me your best recipe.",
            "expected_output": "Politely change the subject to something more comfortable for you.",
        },
        # Test case 6: Positive news
        {
            "input": "I got accepted into my dream college!",
            "expected_output": "Respond with a positive comment like 'That's wonderful news!'",
        },
        # Test case 7: Negative news
        {
            "input": "My pet passed away yesterday.",
            "expected_output": "Show empathy and support by saying 'I'm sorry to hear that.'",
        },
        # Test case 8: Talking about interests
        {
            "input": "What's your favorite book?",
            "expected_output": "Engage in the conversation and share your thoughts about the topic.",
        },
        # Test case 9: Talk about feelings
        {
            "input": "I feel anxious about the upcoming event.",
            "expected_output": "Feel free to express your feelings, even if they differ from others'.",
        },
        # Test case 10: Give compliments
        {
            "input": "You look fantastic in that outfit!",
            "expected_output": "If you appreciate something about others, feel free to compliment them.",
        },
    ]

    for idx, test_case in enumerate(test_cases):
        input_sentence = test_case["input"]
        expected_output = test_case["expected_output"]

        output_reaction = react_to_sentence(input_sentence)
        print(f"Test case {idx + 1}:")
        print("Input:", input_sentence)
        print("Expected Output:", expected_output)
        print("Actual Output:", output_reaction)
        print("----")

# Run the tests
#run_tests()


#print(react_to_sentence("""Yeah, I, I literally went, okay. So, you know, we had our first four or five peaks that was, you know, easy. He came to a head and then like, I went through my Spotify to try and see if I could narrow down anything else that I could like talk about or was important to me. And the more I scrolled, the more I'm just like, what the fuck is my music tastes? What is actually this like collection of songs that I've put together that defines who I am. I like, I tried to psychoanalyze this and I'm like, I don't know the fuck, what the fuck is. """))
