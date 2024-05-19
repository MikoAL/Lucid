





def single_turn_conversation(prompt, model, tokenizer, max_length=256, temperature=0.85, top_k=50, top_p=0.95):
    global device_for_tools
    # Encode the prompt
    prompt_as_messages = [
        {"role": "user", "content": prompt},
    ]
    #stopping_criteria = StoppingCriteriaList([StopSequenceCriteria(["<|end|>"], tokenizer)])
    inputs = tokenizer.apply_chat_template(prompt_as_messages, tokenize=False, add_generation_prompt=False )
    encoded_inputs = tokenizer(inputs, return_tensors="pt").to(device_for_tools)
    src_len = encoded_inputs["input_ids"].shape[1]
    # Generate the response
    outputs = model.generate(encoded_inputs["input_ids"],
                             max_length=max_length,
                             temperature=temperature,
                             top_k=top_k,
                             top_p=top_p,
                             do_sample=True,)
                             #stopping_criteria=stopping_criteria,)
    # Decode the response
    return tokenizer.decode(outputs[0].tolist()[src_len:-1])
def respond_or_not(conversation: dict, model, tokenizer) -> bool:
    """This function takes a conversation (The dictionary type with user, system, assistant...) and decides whether to respond or not."""
    conversation_string = "The following is a conversation between an AI assistant and a User:\n"
    for i in conversation:
        if i["role"] == "user":
            conversation_string += f"User: {i['content']}\n"
        elif i["role"] == "system":
            conversation_string += f"System: {i['content']}\n"
        elif i["role"] == "assistant":
            conversation_string += f"Assistant: {i['content']}\n"
        conversation_string += "\nWould the AI respond to this conversation, or stay silent? Please answer with a simple 'Yes' for respond and 'No' for staying silent."
    response = single_turn_conversation(conversation_string, model, tokenizer)
    if response[:3].lower() == "yes":
        return True
    else:
        return False
def select(prompt, options, model, tokenizer, does_the_model_add_a_token_before_generating=True): 

    if not options:
        return None  # Handle the case of empty options list
    #options = [option.strip() for option in options]
    
    if does_the_model_add_a_token_before_generating:
        tokenized_options = [tokenizer(option, return_tensors="pt").to("cuda:0")["input_ids"].tolist()[0][1:] for option in options]
    else:
        tokenized_options = [tokenizer(option, return_tensors="pt").to("cuda:0")["input_ids"].tolist()[0] for option in options]
    full_tokenized_options = tokenized_options.copy()
    #print(tokenized_options)
    round_number = 0
    answer = []
    while len(tokenized_options) > 1:  # Use > instead of != to ensure termination
        round_number += 1
        #print(f"round number: {round_number}")
        #print(f"tokenized options: {tokenized_options}")
        all_first_tokens = [option[0] for option in tokenized_options]
        #print(f"all first tokens: {all_first_tokens}")
        tokens_to_options = {}
        for i in range(len(all_first_tokens)):
            if all_first_tokens[i] not in tokens_to_options:
                tokens_to_options[all_first_tokens[i]] = [tokenized_options[i]]
            else:
                tokens_to_options[all_first_tokens[i]].append(tokenized_options[i])
        logit_bias = {}
        for tokens_for_check in tokens_to_options:

            logit_bias[tuple([tokens_for_check])] = 100.0
        encoded_inputs = tokenizer(prompt, return_tensors="pt").to("cuda:0")
        src_len = encoded_inputs["input_ids"].shape[1]
        #print(logit_bias)
        response = model.generate(
            encoded_inputs["input_ids"],
            max_new_tokens=3,
            temperature=0.85,
            sequence_bias=logit_bias,
            renormalize_logits = True,
            output_scores = True,
            do_sample=True,
        )
        #print(f"response: {response.tolist()}\nend of response")
        response_token = response[0].tolist()[src_len:][0]
        response_word = tokenizer.decode(response_token)
        #print(f"response word: {response_word}")
        prompt += response_word
        answer.append(response_token)
        #print(f"checking if {response_token} is in {tokens_to_options.keys()}")
        if response_token in tokens_to_options.keys():
            for i in tokens_to_options[response_token]:
                #print(f"all options: {i}")
                if len(i) == 0:
                    break
            tokenized_options = [i[1:] for i in tokens_to_options[response_token]]
            #print(f"tokenized options: {tokenized_options}")


        else:
            # Handle the case where the response token is not found among the options
            break  # Exit the loop to avoid potential infinite loop
        # decode the final tokenized answer
    for i in range(len(full_tokenized_options)):
        if full_tokenized_options[i][:len(answer)] == answer:
            answer_idx = i
            break
    return options[answer_idx]

