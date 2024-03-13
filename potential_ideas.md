
Generalization, references are all you need.

Segmentation through references, and with that, archive generalization.

Conceptual example:
Observation: 

Combining the idea of self-attention mechanisms



treating each collection as an object that contains information about itself
have multiable ways of accessing the same information

Can we describe any given situation with a vector, and nagivate towards a preferred vector space with actions?

Topics?

Generalise

Graph a conversation

Objects:
  Events
  entities
  things?

Events are made out of 
entities and smaller events

Events can have timelines?

Given a series of conversation, what info can we learn?



1. **Information Blocks:**
   - Attributes: Content, Timestamp, Vector
   - Example with dialogue data and corresponding result

2. **Working Memory:**
   - Repository for recent Information Blocks
   - Capacity limit, purging old items

3. **Short-term Memory:**
   - Cache for Information Blocks exceeding Working Memory capacity
   - Stores all types of Information Blocks for future reference

4. **Redundancy Evaluation:**
   - Cross-encoder comparison for similarity
   - New Info Block's vector query in Short-term Memory
   - Discard if similarity above a threshold, retrieve similar Info Block for Working Memory

5. **Long-term Memory:**
   - Object-Oriented Memory system (Entities and Event Objects)
   - Entity Object: Individual's dedicated vector database
     - Person representation through events
   - Event Object: Composed of Entities and other Event Objects
   - Proposed architecture for Long-term Memory

6. **Conversation Mode:**
   - Retrieval of information from Long-term Memory to Working Memory and Short-term Memory

7. **Sleep Mode: Vector Database Update and Similarity Check:**
   - Thorough review during sleep mode
   - Cross-encoder evaluation of similarity
   - Merge process with the language model for streamlined databases

8. **Summary:**
    - A way for the AI to remember the current conversation
    - Combines summary and most recent dialog
    - Building blocks for Timelines
    - Diary function for storage in Long-term Memory

These components collectively form a comprehensive system for handling information, memory, and interactions within a conversational AI framework.

---
## Information Blocks
Information Blocks refer to any data picked up and processed into working memory. They consist of attributes such as "content" "timestamp" and "vector"...
```
Lucid: What are you doing now? Stop ignoring me!
Miko: I'm playing Nintendo games.
Lucid: And that's a higher priority than me?
Miko: ...
Lucid: Your silence speaks volumes.
```
Result:
```python
{
  "object_type" : 'entity',
  "object_name" : 'Miko',
  "content" : 'Miko likes Nintendo games.',
  "timestamp" : '2021-10-15 17:37:00',
  "vector" : array([[-4.39221077e-02, -1.25277145e-02,  2.93133650e-02,],[...]], dtype=float32),
}
```
## Working Memory
Working Memory is a repository containing the most recent Information Blocks. It has a capacity limit, and if exceeded, the oldest item is purged. However, the purged item remains accessible in Short-term Memory. This list of Information Blocks serves as contextual input for the language model.

## Short-term Memory
Short-term Memory acts as a cache for all Information Blocks that exceed the capacity of Working Memory. It stores all types of Information Blocks for future reference, including those currently in Working Memory.

> **Note:** 
Before a newly generated Information Block enters Working Memory, it undergoes redundancy evaluation. This evaluation involves comparing it with existing Information Blocks using both sentence similarity and cross-encoders.
New Info Block's vector will be used to query in the Short-term Memory vector database, use cross-encoder to check for similarity, if it's above a certain threshold, we will discard the new Info Block and retrive the similar Info Block and push it into Working Memory.

## Long-term Memory
The architecture for Long-term Memory is still a WIP. My proposed solution is an Object-Oriented Memory system, which includes Entities and Event Objects.

- **Entity Object:** Each individual is assigned a dedicated vector database containing all relevant Information Blocks.
  - **Person:** A person is nothing but a collection of events that they participated. By listing out all of the individual's action, we can get a numerical representaion of that person, with more recent events having a higher weight.
- **Event Object:** Events are composed of entities Objects (if applicable), other Event Objects, and a descriptive string outlining the occurrence.

> **Note:** A person's previous interaction will have the sentence structure of "When [INSERT EVENT HERE], [INSERT NAME HERE] decided to ..."

> **Note:** Each entity is but a representation of past interaction and observations.

> **Note:** Each Event Object is but a list of entity interactions.

## Summary
Summary acts as a way for the AI to remember the current conversation without the ENTIRE conversation being loaded, rather, use a combination of both the summary and the most recent dialog.

The second function of having summaries is to act as the building blocks for Timelines, a continuous collection of what is happening within a time window.

Can also acts as a diary of sorts to be stored into Long-Term memory.

## Diary System
Entries are placed on a timeline, with Summaries as entries.
- Memory
  - Date
    - Entry 1
    - Entry 2
    - Entry 3

A seperate Vector database will be used for querying based on events.
Each embedding will represent a single entry.

## Conversation Mode
In Conversation Mode, the AI can retrieve information from Long-term Memory to Working Memory and Short-term Memory.

## Sleep Mode: Vector Database Update and Similarity Check
During Sleep Mode, the AI conducts a thorough review of vector databases. This process involves comparing newly added data from Short-term Memory with existing records. Using cross-encoders, the AI evaluates the similarity of initial query results. If significant resemblance is found, the language model is employed to merge the information, treating it as new data. This iterative process continues until no substantial similarities remain, ensuring a streamlined and coherent database.
