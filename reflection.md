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

The scheduler considers three constraints: task priority (high/medium/low), owner availability in minutes, and task frequency (daily, weekly, as_needed). Tasks are sorted first by priority descending, then by preferred time slot ascending, and are only included if they fit within the owner's remaining time. Priority ended up being the most important constraint because missing a high-priority task like giving medication is a bigger deal than missing a low-priority one, no matter what the timing preference is.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

The scheduler greedily picks tasks in priority order and skips any task that does not fit in the remaining time, even if a lower-priority task would fit. This means a long high-priority task can end up blocking several shorter lower-priority ones. That feels like the right call here though, because the whole point is to make sure the most critical pet care tasks always get done first. Leaving something low-priority unscheduled is a much safer outcome than squeezing it in at the cost of missing something that actually matters.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

Claude was used throughout pretty much every phase of the project. In the design phase, I used it to brainstorm class responsibilities and spot gaps in the UML before writing any code. During implementation, it helped fill in repetitive boilerplate like `__init__` methods and property accessors, which let me focus more on the actual scheduling logic. When something was not working right, I would ask Claude to explain what a piece of code was doing and that usually helped me spot the issue faster than just staring at the traceback.

The prompts that worked best were the ones that were specific and gave Claude something concrete to work with. Asking "given this class structure, what edge cases should `build_plan` handle?" got much more useful answers than something like "how should I build the scheduler?" I also found that pasting in the existing class signatures each time kept Claude from suggesting things that clashed with what was already there.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

When I was working on the Scheduler class, Claude suggested putting the scheduling reasoning and the actual schedule building all inside one big `build_plan` method that would also print results directly to the console. I did not go with that because it would have made testing a nightmare. A method that prints to the console cannot really be checked in a unit test in any clean way. So instead I split it up: `build_plan` just updates the internal state, `explain_plan` returns the reasoning as a list, and `get_schedule` returns the scheduled tasks. The Streamlit UI then picks up each piece separately. To check that the split actually worked, I just ran each method on its own and made sure I could assert against the outputs without any side effects getting in the way.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

The tests focused on the core things the scheduler is supposed to do: making sure high-priority tasks always show up before low-priority ones, that tasks too long to fit in the remaining time get skipped rather than partially added, that the reasoning log captures both what was added and what was skipped, and that passing in an empty task list does not break anything. These were important to test because a bug in the scheduling logic would not crash the program, it would just produce a quietly wrong plan. Without explicit assertions there would be no way to know something was off.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

I feel pretty good about the scenarios the tests actually cover. The greedy priority sort is simple enough that it is not hard to follow the logic through. Where I am less sure is the edge cases, like what happens when two tasks have the same priority and the same duration. I am not totally confident the tie-breaking behavior is deterministic or even desirable right now. If I had more time I would write tests for a list where every task has equal priority, an owner with zero available minutes, and a case where a lower-priority task fits exactly in the leftover time but still gets blocked by a higher-priority task that does not fit.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

The separation between the scheduling logic and the Streamlit UI turned out cleaner than I expected. Because `Scheduler` has separate methods for the schedule, the reasoning list, and the total time, the UI could handle each piece on its own. Conflicts showed up as error messages, skipped tasks went into a collapsible expander, added tasks had their own section. The UI did not need to know anything about how the schedule was actually built, it just consumed the outputs. That made both sides a lot easier to work with.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

The priority system right now is just a three-level string. I would want to replace it with a numeric weight so there is more flexibility, and so that partial scheduling could be an option. For example, instead of skipping a low-priority task entirely, it might make sense to fit in a shorter version of it if there is a little time left. Supporting multiple pets per owner is also something that feels like an obvious next step. The `Owner` class is kind of set up for it already, but the Scheduler only looks at one pet's tasks right now.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

The biggest thing I took away from this is that Claude works a lot better when you already have a clear design in place. When the classes had defined responsibilities and clean boundaries, the suggestions it gave actually fit into what I was building and things moved fast. When the design was still fuzzy, the suggestions would introduce inconsistencies that needed to be cleaned up later. Being the lead architect meant making the structural decisions myself first and then using Claude to help fill in the details, not the other way around. When I tried handing over too much of the design thinking to the AI, the output got harder to follow and harder to test. Claude is genuinely useful, but it needs something solid to build off of.
