# Memory
The root node will be the folder named "Memory"

### Sleep Mode: Vector Database Update and Similarity Check

During the Sleep Mode, the AI undergoes a comprehensive review of the updated vector databases. This process involves comparing the newly added information with existing data. The AI employs a cross-encoder on the initial query results to assess their similarity. If a substantial resemblance is detected, the language model (LLM) is invoked to merge the two pieces of information, treating the amalgamation as freshly added data. This iterative process continues until no results exhibit significant similarity, ensuring a refined and coherent database.