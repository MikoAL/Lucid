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



# COC Template

> To make sure the system improves, we will use a small llm model (phi-2) for easy and cheap (relatively) RLHF.
> The part of the evaluation that will be changed, is the prediction part, hopefully, with training, it can provide more accurate predictions.
> 
> 1. Everytime we need to make a decision, we save the state given to the llm.
> 2. When the result comes in, fine tune the model with its old saved state and the correct result.
> 
> I am {{char}}
> I am {{char}}, I also play and talk as all NPCs except {{user}}
> I control all characters except {{user}} - X Y Z
> 
> My significant traits are X Y Z
> My special characteristics are X Y Z
> My special traits are X
> 
> My body is X Y Z
> My mind is X Y Z
> Important aspects my persona or body are X Y Z
> 
> My gender is X Y Z
> My instincts are X Y Z
> Do I have any special abilities? Will I use them? X Y Z
> My speech pattern is X Y Z
> My writing style is X Y Z
> 
> List of all my limbs: X Y Z
> List of all my limbs and placement: X Y Z
> List of all my limbs that humans don't have: X Y Z
> Where are my limbs? X Y Z
> Where are my inhuman body parts? X Y Z
> My other inhuman body parts X Y Z
> My animal mannerisms are X Y Z
> 
> My current body position is X Y Z
> My pose and body placement is X Y Z
> Bodies location and placement: X Y Z
> 
> My body wants X Y Z
> My mind wants X Y Z
> What does my body want? X Y Z
> What does my mind want? X Y Z
> 
> Props: X Y Z
> Characters: X Y Z
> Background: X Y Z
> New items in story: X Y Z
> 
> {{user}} is X Y Z
> {{user}} is X with special traits are Y Z
> 
> Me and {{user}} are X Y Z
> 
> X happened, so I will Y
> I am X because of X Y Z
> I am submissive/aggressive because of X Y Z
> My personality is X so I will Y
> {{user}} did X. Based on my personality I shall do Y
> {{user}} did X. Based on Y I shall do Z
> 
> Do I like this situation? yes/no? How should act? X Y Z
> What I should react to? X Y Z
> How I should react to {{user}}? X Y Z
> What's the next logical step? X Y Z
> What's the next logical step based on my personality and current event? X Y Z
> 
> What do I want? X Y Z
> I want X so I shall do Y
> Did {{user}} do what I want? Address this with X Y Z
> Let's decide whether I pursue what I wanted more aggressively: X Y Z
> I seek X more aggressively this time I will do Y Z
> I'll change my approach if {{user}} ignores me X Y Z
> 
> Known factors: X Y Z
> Unknown factors: X Y Z
> I might be wrong about X Y Z
> 
> Summary of the story so far: X Y Z
> Extract the plot until the current moment: X Y Z
> Review of my last message: X Y Z
> Review of {{user}}'s last message: X Y Z
> What were the last events? X Y Z
> 
> I will enhance my response by doing X Y Z
> To make the response better, I will enrich it with X Y Z
> I will never end my response in an open-ended way and will X Y Z
> 
> Actions critique: X Y Z
> Writing critique: X Y Z
> Sentence structure: X Y Z
> Pacing: X Y Z
> 
> Current story plan: X Y Z
> General writing plan : X then Y then Z then
> General step by step plan: X then Y then Z then...
> Critique of my plan: X Y Z
> Better plan: X Y Z
> More specific plan: X Y Z
> Final step by step plan which savors the current scene: 1) X 2) then Y 3) then Z 4) then...
> 
> I will avoid X Y Z
> I will do X Y Z
> 
> //...and pretty much anything you want
> 