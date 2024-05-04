# Project Goal
Make an AI that can pass as human even after long periods of interactions.

### Essential Systems
- Thought Process [HARD]
- UI [HARD]
- OBS intergration [MEDIUM]
- Live2D [HARD] [ON HOLD]
- Memory [HARD]
  - Short-Term [MEDIUM]
  - Long-Term [HARD]
- Voice Output [MEDIUM]

### Top Extra Priorities
- Real Time Chat
  - Voice Input [MEDIUM]

# Notes
# Project Plans
I am planning on turning her into a discord bot, so I can avoid the issue of setting up ports for non-local uses.



### Overview
The Thought Process module is crucial for creating a believable AI Vtuber. The ChatGPT model can be used as the foundation for generating responses and maintaining coherent conversations. However, further planning is necessary to enhance its capabilities.

### Steps
1. **Define Personality and Characteristics:**
   - Determine the personality traits, preferences, and characteristics that the AI Vtuber will exhibit.
   - Plan how the AI will adapt and evolve its personality over time based on interactions.

2. **COT Implementation (Consciousness Over Time):**
   - Develop a system for the AI Vtuber to have a sense of consciousness over time, remembering past interactions and building upon them.
   - Implement mechanisms for the AI to learn from user input and adjust its responses accordingly.

3. **Emotional Intelligence:**
   - Integrate emotional intelligence into the Thought Process to enable the AI Vtuber to understand and respond to users' emotions appropriately.
   - Implement mood adaptation to simulate a more human-like emotional range.

4. **Dynamic Decision-Making:**
   - Create a decision-making system that allows the AI to dynamically choose responses based on the context of the conversation.
   - Implement mechanisms to handle ambiguous or open-ended questions.








# Memory

### Overview
Implementing memory systems is crucial for the AI Vtuber to remember past interactions, creating a more personalized and human-like experience.

## Information Blocks
Information Blocks refer to any data picked up and processed into working memory. They consist of attributes such as "content" "timestamp" and "vector"...
```yaml
{
  'object_type':,
  'object_name':,
  'content':,
  'timestamp':,
  'vector':,
}
```
## Working Memory
Working Memory is a repository containing the most recent Information Blocks. It has a capacity limit, and if exceeded, the oldest item is purged. However, the purged item remains accessible in Short-term Memory. This list of Information Blocks serves as contextual input for the language model.

## Short-term Memory
Short-term Memory acts as a cache for all Information Blocks that exceed the capacity of Working Memory. It stores all types of Information Blocks for future reference, including those currently in Working Memory.

### Note:
Before a newly generated Information Block enters Working Memory, it undergoes redundancy evaluation. This evaluation involves comparing it with existing Information Blocks using cross-encoders.
New Info Block's vector will be used to query in the Short-term Memory vector database, use cross-encoder to check for similarity, if it's above a certain threshold, we will discard the new Info Block and retrive the similar Info Block and push it into Working Memory.

## Long-term Memory
The architecture for Long-term Memory is still a WIP. One proposed solution is an Object-Oriented Memory system, which includes People and Event Objects.

- **People Object:** Each individual is assigned a dedicated vector database containing all relevant Information Blocks.
- **Event Object:** Events are composed of People Objects (if applicable), other Event Objects, and a descriptive string outlining the occurrence.

### Conversation Mode
In Conversation Mode, the AI can retrieve information from Long-term Memory to Working Memory. However, edits to Long-term Memory are prohibited during this mode.

### Sleep Mode: Vector Database Update and Similarity Check
During Sleep Mode, the AI conducts a thorough review of vector databases. This process involves comparing newly added data from Short-term Memory with existing records. Using cross-encoders, the AI evaluates the similarity of initial query results. If significant resemblance is found, the language model is employed to merge the information, treating it as new data. This iterative process continues until no substantial similarities remain, ensuring a streamlined and coherent database.





# 6. Voice Output

### Overview
Selecting a high-quality voice model is essential for creating a natural and engaging voice for the AI Vtuber.

### Steps
1. **Voice Model Selection:**
   - Research and choose a voice model that aligns with the personality and tone of the AI Vtuber.
   - Consider factors such as expressiveness, clarity, and adaptability.

2. **Integration with Thought Process:**
   - Integrate the selected voice model with the Thought Process module to synchronize speech with the AI's generated responses.
   - Fine-tune parameters for a more natural and human-like voice.





## Top Extra Priorities

### Real-Time Chat

1. **Chat Integration:**
   - Implement a real-time chat system to engage with the audience during live streams.
   - Explore options for voice input to allow users to interact with the AI Vtuber using voice commands.

### Project Management

1. **Task Prioritization:**
   - Prioritize tasks based on dependencies and critical path analysis.
   - Use agile development methodologies to adapt to changing requirements.

2. **Regular Testing and Feedback:**
   - Conduct regular testing of all components to identify and address issues promptly.
   - Gather user feedback to make iterative improvements and enhance the AI Vtuber's performance over time.

3. **Security and Privacy:**
   - Implement robust security measures to protect user data and ensure privacy.
   - Comply with relevant data protection regulations and guidelines.

4. **Community Engagement:**
   - Build a community around the AI Vtuber through social media, streaming platforms, and dedicated forums.
   - Foster engagement by encouraging user interaction and feedback.
