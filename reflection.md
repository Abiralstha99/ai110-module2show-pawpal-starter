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

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

Yes, the design changed after copilot gave me some suggestions.

1. Added id field to Task
   Each task now gets a unique UUID automatically. This prevents bugs when two tasks share the same name (e.g. "walk" appearing twice). remove_task and edit_task now look up by id instead of name.

2. Added ScheduledTask dataclass
   A new dataclass that wraps a Task with a start_time and end_time. Without this, the daily plan had no way to record when each task happens — just what tasks exist.

3. Changed time fields from str to datetime.time
   available_hours in Owner and time_constraint in Task were plain strings like "8am". These are now proper datetime.time values so the scheduler can compare and calculate times without parsing strings every time.

4. Changed TaskManager storage from list to dict
   Tasks are now stored as {id: Task} instead of a flat list. This makes finding, editing, and removing a task instant (O(1)) rather than scanning the whole list every time.
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
