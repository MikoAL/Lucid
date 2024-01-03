# Decision Making

To make a decision you need to:
1. Know all of your available options.
  - present some preset options (talk, stay silent)
  - (SKIP) let llm decide on the available options (ones that can be executed)
  - (SKIP) use zeroshot_classification to understand what options the llm chose (to avoid command formatting errors)

2. Predict all options' results and consequences.
  - prompt the llm to predict

3. Evaluate said results and consequences.
  - prompt llm to evaluate results
  - use zeroshot_classification to understand what option the llm chose (to avoid command formatting errors)

4. Make the final decision.
  - execute action

# Learning

To make sure the system improves, we will use a small llm model (phi-2) for easy and cheap (relatively) RLHF.
The part of the evaluation that will be changed, is the prediction part, hopefully, with training, it can provide more accurate predictions.

1. Everytime we need to make a decision, we save the state given to the llm.
2. When the result comes in, fine tune the model with its old saved state and the correct result.

