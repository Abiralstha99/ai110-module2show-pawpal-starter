# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

- Set up their pet profile : Enter basic info about the owner and pet (name, species, age, any special needs)
- Add and manage care tasks : Create tasks like "morning walk," "medication," or "grooming," each with a duration, priority level, and any time constraints (e.g., meds must happen at 8am).
- Generate and view today's plan — With one click, produce a scheduled daily plan that fits the tasks into the owner's available time, ordered by priority, with a short explanation of why the plan looks the way it does

**Building Blocks**

- Owner
  Holds info about the person using the app.
  Attributes: name, available_hours (e.g. 8am–6pm), preferences (e.g. prefers morning walks)
  Methods: get_available_slots(), update_preferences()

- Pet
  Holds info about the animal being cared for.
  Attributes: name, species, age, special_needs (e.g. diabetic, senior, anxious)
  Methods: get_care_requirements() — returns any constraints driven by the pet's profile (e.g. senior dog needs shorter, more frequent walks)

- Task
  Represents one care activity.
  Attributes: name, duration_minutes, priority (high/medium/low), time_constraint (optional fixed time like 8am), is_completed, category (walk, feeding, meds, grooming, etc.)
  Methods: mark_complete(), is_time_sensitive(), to_dict() (for saving/displaying)

- Scheduler
  The brain of the app — takes tasks and constraints and produces a plan.
  Attributes: owner, pet, task_manager
  Methods: generate_plan(), sort_by_priority(), fit_within_available_time(), explain_plan()

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

My scheduler considers three constraints:

Time — tasks with a fixed time are placed first because they cannot move
Priority — high priority tasks are scheduled before medium and low priority ones
Owner availability — tasks only get scheduled within the owner's available hours (e.g. 8am to 6pm)

I decided time constraints mattered most because missing a fixed-time task (like insulin) has real consequences. Priority comes second because it reflects the owner's own judgement about what matters. Availability comes last because it is more of a hard outer boundary than a sorting rule.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

Original: A simple nested loop that compares every possible pair of tasks. Very easy to read and reason about, but it is fully pairwise — every task is compared to every other task, giving O(n²) complexity.

Revised: First, sort tasks by start time. Then, when comparing them, stop checking as soon as you know they can’t overlap anymore. It also safely skips tasks with missing times instead of crashing. Slightly more complex to read, but gives better performance

## For a small pet care app with fewer than 20 tasks, both versions run instantly, so speed doesn’t really matter. The new version was chosen not because it’s faster, but because it prevents crashes (like when time is missing) and avoids using exceptions in important parts of the code.

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

During design I used it to brainstorm objects and catch gaps in my class structure. It pointed out that I had no way to represent when a task actually happens inside the daily plan, which led to adding ScheduledTask. During implementation I used Inline Chat to fill in individual methods one at a time.I would highlight a method stub, describe what it should do, and review what came back. For bigger changes that touched multiple files, like adding pet_id across Pet, Task, and TaskManager, I used Agent Mode.

The prompts that worked best were specific and scoped. Providing enough context and setting what type of output you want in return helped the agent to give good output

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

In the first version of detect_conflicts(), Copilot wrote it with a try/except block inside the comparison loop to handle None time values. It worked but using exceptions for normal flow felt like the wrong approach, especially inside a loop that runs on every task pair. My general verification process was to read the generated code line by line before accepting it, check that it matched the class design we had already agreed on, and run the tests.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

I wrote test covering these areas:

a. Recurring task lifecycle, checking that daily tasks produce a
next occurrence with the correct due date, that one-time tasks
produce nothing, and that the original task fields are not
changed by next_occurrence().

b. Priority and time sorting, verifying that tasks come out in the
right order and that edge cases like unknown priority values and
empty lists do not crash anything.

c. Task filtering, confirming that completed tasks are excluded from
pending results and that get_tasks_for_owner() correctly uses
pet.pet_id and not pet.id, which was a real bug we caught during
the design review.

d. Conflict detection, testing that overlapping windows produce a
warning, that boundary-touching tasks are not falsely flagged,
and that unsorted input is handled correctly since the method
sorts internally.

e. End-to-end plan generation, checking that generate_plan() returns
a valid DailyPlan and that conflicts surface in the explanation
field.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

I would say 4 out of 5 for the core scheduling logic. The sorting, filtering, recurring tasks, and conflict detection all have tests
and are passing. The areas I am less confident about are fit_within_available_time(), which handles fitting tasks into the owner's available hours, and the Streamlit UI layer, neither of which has automated tests yet.

If I had more time I would test these edge cases next:

- Owner with zero available hours, all tasks should go to unscheduled
- A task longer than any available slot, should be skipped cleanly without crashing

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

The part I am most satisfied with is the design review process we did before writing any logic. Going through the class skeleton line by line and asking what is missing caught real structural problems early, like the missing ScheduledTask, the string time fields, and the lack of pet_id linkage. Fixing those at the skeleton stage was much easier than fixing them after the logic was written.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

I would add a proper data persistence layer. Right now everything lives in st.session_state and disappears when the browser tab closes. Even a simple JSON file save would make the app actually usable day to day.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

The most important thing I learned is that AI tools are good at writing code but they do not know what you are trying to build. They will give you working code that solves the wrong problem if you are not specific enough about the design.
