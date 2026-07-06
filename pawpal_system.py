"""
PawPal Task Scheduling System
Classes for managing pet care tasks and scheduling
"""

from datetime import date, time, timedelta
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass, field, replace
import uuid


class Pet:
    """Represents a pet owned by an owner."""

    def __init__(self, name: str, species: str, age: int, pet_id: str, special_needs: List[str]):
        """Initialize a pet with details and an empty task list."""
        self.name = name
        self.species = species
        self.age = age
        self.pet_id = pet_id
        self.special_needs = special_needs
        self.tasks: List['Task'] = []

    def get_care_requirements(self) -> dict:
        """Get care requirements for this pet."""
        return {
            "species": self.species,
            "age": self.age,
            "special_needs": list(self.special_needs),
        }

    def add_task(self, task: 'Task') -> None:
        """Add a task for this pet."""
        self.tasks.append(task)

    def remove_task(self, task_id: str) -> bool:
        """Remove a task for this pet by id."""
        for i, task in enumerate(self.tasks):
            if task.id == task_id:
                self.tasks.pop(i)
                return True
        return False

    def get_tasks(self) -> List['Task']:
        """Get all tasks for this pet."""
        return self.tasks


class Owner:
    """Represents an owner with pets and availability."""

    def __init__(self, name: str, available_hours: Tuple[time, time], preferences: dict, pets: List['Pet']):
        """Initialize an owner with pets and availability constraints."""
        self.name = name
        # Tuple of (start_time, end_time)
        self.available_hours = available_hours
        self.preferences = preferences
        self.pets = pets

    def get_available_slots(self) -> List[dict]:
        """Get available time slots for this owner."""
        if not self.available_hours:
            return []

        start_time, end_time = self.available_hours
        return [{
            "start": start_time.strftime("%H:%M"),
            "end": end_time.strftime("%H:%M")
        }]

    def update_preferences(self, new_preferences: dict) -> None:
        """Update owner's preferences."""
        self.preferences.update(new_preferences)


@dataclass
class Task:
    """Represents one pet care activity that may be scheduled."""

    name: str
    duration_minutes: int
    priority: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    pet_id: str = ""
    time_constraint: Optional[time] = None
    is_completed: bool = False
    frequency: str = "once"
    due_date: date = field(default_factory=date.today)
    next_task: Optional['Task'] = None
    category: str = "general"

    def mark_complete(self) -> Optional['Task']:
        """Mark this task as completed and return the next occurrence when recurring."""
        self.is_completed = True
        self.next_task = self.next_occurrence()
        return self.next_task

    def next_occurrence(self) -> Optional['Task']:
        """Return next recurring task, or None for one-time tasks."""
        frequency = self.frequency.strip().lower()
        if frequency == "once":
            return None

        days_to_add = 1 if frequency == "daily" else 7 if frequency == "weekly" else None
        if days_to_add is None:
            return None

        return Task(
            name=self.name,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            pet_id=self.pet_id,
            time_constraint=self.time_constraint,
            is_completed=False,
            frequency=self.frequency,
            due_date=date.today() + timedelta(days=days_to_add),
            category=self.category,
        )

    def is_time_sensitive(self) -> bool:
        """Return True if this task has a fixed or narrow time requirement."""
        return self.time_constraint is not None

    def to_dict(self) -> Dict[str, Any]:
        """Return a dictionary representation of this task."""
        return {
            "id": self.id,
            "name": self.name,
            "duration_minutes": self.duration_minutes,
            "priority": self.priority,
            "pet_id": self.pet_id,
            "time_constraint": self.time_constraint.isoformat() if self.time_constraint else None,
            "is_completed": self.is_completed,
            "frequency": self.frequency,
            "due_date": self.due_date.isoformat(),
            "category": self.category,
        }


class TaskManager:
    """Manages task creation, updates, filtering, and retrieval."""

    def __init__(self, tasks: Optional[List[Task]] = None) -> None:
        """Initialize the task manager and optionally populate with existing tasks."""
        self.tasks: Dict[str, Task] = {}
        if tasks:
            for task in tasks:
                self.tasks[task.id] = task

    def add_task(self, task: Task) -> None:
        """Add a new task to the manager."""
        self.tasks[task.id] = task

    def mark_task_complete(self, task_identifier: str) -> Optional[Task]:
        """Mark a task complete and register its next occurrence when it is recurring."""
        task = self.tasks.get(task_identifier)
        if task is None:
            for candidate in self.tasks.values():
                if candidate.name == task_identifier:
                    task = candidate
                    break

        if task is None:
            return None

        next_task = task.mark_complete()
        if next_task is not None:
            self.add_task(next_task)

        return next_task

    def remove_task(self, task_identifier: str) -> bool:
        """Remove a task by id first, then by name if id is not found."""
        if self.tasks.pop(task_identifier, None) is not None:
            return True

        for task_id, task in list(self.tasks.items()):
            if task.name == task_identifier:
                del self.tasks[task_id]
                return True

        return False

    def is_completed(self, task_id: str) -> bool:
        """Check if a specific task is completed."""
        task = self.tasks.get(task_id)
        return task.is_completed if task else False

    def get_pending_tasks(self) -> List[Task]:
        """Return all tasks not yet marked completed."""
        return [task for task in self.tasks.values() if not task.is_completed]

    def get_tasks_by_priority(self, priority: str) -> List[Task]:
        """Return tasks that match a given priority level."""
        normalized = priority.strip().lower()
        return [task for task in self.tasks.values() if task.priority.strip().lower() == normalized]

    def get_time_sensitive_tasks(self) -> List[Task]:
        """Return tasks that should be prioritized due to time constraints."""
        return [task for task in self.tasks.values() if task.is_time_sensitive()]

    def get_tasks_for_owner(self, owner: Owner) -> List[Task]:
        """Return incomplete tasks for pets owned by the given owner."""
        owner_pet_ids = {pet.pet_id for pet in owner.pets}
        return [
            task
            for task in self.tasks.values()
            if (not task.is_completed) and task.pet_id in owner_pet_ids
        ]

    def filter_tasks(
            self,
            is_completed: Optional[bool] = None,
            pet_name: Optional[str] = None,
            owner: Optional[Owner] = None,
    ) -> List[Task]:
        """Filter tasks by completion status and/or the name of the pet they belong to."""
        filtered_tasks = list(self.tasks.values())

        if is_completed is not None:
            filtered_tasks = [
                task for task in filtered_tasks if task.is_completed == is_completed
            ]

        if pet_name is not None:
            if owner is None:
                raise ValueError(
                    "owner is required when filtering tasks by pet_name")

            pet_name_lookup = {
                pet.pet_id: pet.name.strip().lower()
                for pet in owner.pets
            }
            normalized_pet_name = pet_name.strip().lower()
            filtered_tasks = [
                task
                for task in filtered_tasks
                if pet_name_lookup.get(task.pet_id) == normalized_pet_name
            ]

        return filtered_tasks


class DailyPlan:
    """Represents a single day's generated schedule and explanation."""

    def __init__(
            self,
            plan_date: date,
            scheduled_tasks: Optional[List[Task]] = None,
            unscheduled_tasks: Optional[List[Task]] = None,
            explanation: str = "",
    ) -> None:
        """Initialize plan details for one day."""
        self.plan_date = plan_date
        self.scheduled_tasks = scheduled_tasks or []
        self.unscheduled_tasks = unscheduled_tasks or []
        self.explanation = explanation

    def add_scheduled_task(self, task: Task) -> None:
        """Add a task to the scheduled list."""
        self.scheduled_tasks.append(task)

    def add_unscheduled_task(self, task: Task) -> None:
        """Add a task that could not be placed in the schedule."""
        self.unscheduled_tasks.append(task)

    def to_dict(self) -> Dict[str, Any]:
        """Return a dictionary representation of this daily plan."""
        return {
            "plan_date": self.plan_date.isoformat(),
            "scheduled_tasks": [task.to_dict() for task in self.scheduled_tasks],
            "unscheduled_tasks": [task.to_dict() for task in self.unscheduled_tasks],
            "explanation": self.explanation,
        }


@dataclass
class ScheduledTask:
    """Represents a task scheduled at a specific time."""
    task: Task
    start_time: time
    end_time: time


class Scheduler:
    """Builds a daily plan from owner and task constraints."""

    def __init__(self, owner: Owner, task_manager: TaskManager) -> None:
        """Initialize the scheduler with an owner and task manager."""
        self.owner = owner
        self.task_manager = task_manager

    def get_all_owner_tasks(self) -> List[Task]:
        """Retrieve all tasks linked to the owner's pets."""
        return self.task_manager.get_tasks_for_owner(self.owner)

    def generate_plan(self, plan_date: date) -> DailyPlan:
        """Generate a daily plan by prioritizing and fitting tasks into available time."""
        tasks = self.get_all_owner_tasks()
        prioritized = self.sort_by_priority(tasks)
        ordered = self.sort_by_time(prioritized)
        available_slots = self.owner.get_available_slots()
        scheduled, unscheduled = self.fit_within_available_time(
            ordered, available_slots)

        plan = DailyPlan(
            plan_date=plan_date,
            scheduled_tasks=scheduled,
            unscheduled_tasks=unscheduled,
        )
        plan.explanation = self.explain_plan(plan)
        return plan

    def sort_by_priority(self, tasks: List[Task]) -> List[Task]:
        """Return tasks sorted by priority, highest first."""
        priority_rank = {"high": 0, "medium": 1, "low": 2}
        return sorted(tasks, key=lambda task: priority_rank.get(task.priority.strip().lower(), 3))

    def sort_by_time(self, tasks: List[Task]) -> List[Task]:
        """Return tasks ordered by time constraints and optimal flow."""
        return sorted(
            tasks,
            key=lambda task: (
                task.time_constraint is None,
                task.time_constraint.strftime(
                    "%H:%M") if task.time_constraint else "99:99",
                {"high": 0, "medium": 1, "low": 2}.get(
                    task.priority.strip().lower(), 3),
            ),
        )

    def fit_within_available_time(
            self,
            tasks: List[Task],
            available_slots: List[Dict[str, str]],
    ) -> Tuple[List[Task], List[Task]]:
        """Split tasks into scheduled and unscheduled based on available time."""
        def _to_minutes(value: str) -> int:
            hour_text, minute_text = value.split(":", 1)
            return int(hour_text) * 60 + int(minute_text)

        total_available_minutes = 0
        for slot in available_slots:
            start_raw = slot.get("start")
            end_raw = slot.get("end")
            if not start_raw or not end_raw:
                continue
            try:
                start_minutes = _to_minutes(start_raw)
                end_minutes = _to_minutes(end_raw)
            except ValueError:
                continue

            if end_minutes > start_minutes:
                total_available_minutes += end_minutes - start_minutes

        scheduled: List[Task] = []
        unscheduled: List[Task] = []
        used_minutes = 0

        for task in tasks:
            if task.duration_minutes <= 0:
                scheduled.append(task)
                continue

            if used_minutes + task.duration_minutes <= total_available_minutes:
                scheduled.append(task)
                used_minutes += task.duration_minutes
            else:
                unscheduled.append(task)

        return scheduled, unscheduled

    def explain_plan(self, plan: DailyPlan) -> str:
        """Generate a human-readable explanation of scheduling decisions."""
        return (
            f"Scheduled {len(plan.scheduled_tasks)} task(s); "
            f"left {len(plan.unscheduled_tasks)} unscheduled due to time constraints."
        )

    def detect_conflicts(self, scheduled_tasks: List[ScheduledTask]) -> List[str]:
        """Return warnings describing overlapping scheduled task time windows."""
        warnings: List[str] = []

        ordered = sorted(
            (
                st
                for st in scheduled_tasks
                if st is not None and st.start_time is not None and st.end_time is not None
            ),
            key=lambda st: st.start_time,
        )

        for i, first in enumerate(ordered):
            for second in ordered[i + 1:]:
                # Since tasks are sorted by start time, later tasks cannot overlap past this point.
                if second.start_time >= first.end_time:
                    break

                if first.start_time < second.end_time and second.start_time < first.end_time:
                    warnings.append(
                        "Conflict: "
                        f"{first.task.name} ({first.start_time:%H:%M}-{first.end_time:%H:%M}) "
                        "overlaps with "
                        f"{second.task.name} ({second.start_time:%H:%M}-{second.end_time:%H:%M})."
                    )

        return warnings
