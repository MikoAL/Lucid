# Memory

## Overview

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

### Note on Redundancy Evaluation

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
