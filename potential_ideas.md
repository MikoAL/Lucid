treating each collection as an object that contains information about itself
have multiable ways of accessing the same information

Can we describe any given situation with a vector, and nagivate towards a preferred vector space with actions?

Topics?

Generalise

Graph a conversation

Objects:
  Events
  people
  things?

Events are made out of 
people and smaller events

### Info Blocks
Info Blocks refers to any info picked up and generated into working memory.
Contains the "content", "timestep" and "vector" attributes.

### Working Memory
Working memory is a list containing the most recent Info Blocks, the list will have a limit on how many items it can hold at once, if exceeded, will push the oldest Info Block into Short-term Memory.

### Short-term Memory
This is a vector database where we cache all the info blocks that the working memory couldn't store, all info blocks regardless of types, will be stored inside.

#### Note
Before a freshly generated info block is placed inside the working memory, it will be evaluated for redundent

### Conversation Mode
During Conversation Mode, the AI can retrive info from long-term memory to working memory. 
No edits to the long-term memory will be allowed during Conversation Mode. Instead, we will be making new info pieces in working memory and pushing info blocks that can't fit, into Short-term Memory, and at downtime, go into Sleep Mode.




### Sleep Mode: Vector Database Update and Similarity Check
During the Sleep Mode, the AI undergoes a comprehensive review of the vector databases. This process involves comparing the newly added information committed from Short-term Memory, with existing data. The AI employs a cross-encoder on the initial query results to assess their similarity. If a substantial resemblance is detected, the language model (LLM) is invoked to merge the two pieces of information, treating the amalgamation as freshly added data. This iterative process continues until no results exhibit significant similarity, ensuring a refined and coherent database.

