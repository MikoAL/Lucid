# Decision Making

To make a decision you need to:
1. Know all of your available options.
  - preset some options (talk, stay silent)
  - let llm decide on the available options (ones that can be executed)
  - use zeroshot_classification to understand what options the llm chose (to avoid command formatting errors)
2. Predict all options' results and consequences.
  - prompt the llm to predict
3. Evaluate said results and consequences.
  - prompt llm to evaluate results
  - use zeroshot_classification to understand what option the llm chose (to avoid command formatting errors)
4. Make the final decision.
  - execute action