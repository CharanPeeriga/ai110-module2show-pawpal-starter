# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

There were four classes chosen: PetTask, Pet, Owner, Scheduler. 

PetTask will contain the task title, duration, priority, and preferred_time (optional). This class is responsible for denoting priority for each task.

Pet will contain the name, species, age, and contain a list of PetTask objects. This class will have the ability to add and remove tasks

Owner will contain name, available_minutes, and pet (object of Pet class). This class will denote availability and retrieve pet tasks.

Scheduler will contain owner, schedule, and reasoning. This class is responsible for building a plan based on priority, availability of owner, and records the reasoning. 

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

The design was initially not as detailed, specifically the scheduler which was not as fleshed out. After Claude feedback, it was changed to be a more impactful task that essentially builds the plan with the objects from other classes.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
