"""
Simple tests for PawPal Task Scheduling System
"""

from datetime import date, time, timedelta
from pawpal_system import ScheduledTask, Scheduler, Task, Pet, Owner, TaskManager


class TestTaskCompletion:
    """Test suite for task completion functionality."""

    def test_mark_complete_changes_status(self):
        """Verify that calling mark_complete() changes the task's is_completed status to True."""
        # Arrange: Create a task with is_completed initially False
        task = Task(
            name="Morning Walk",
            duration_minutes=30,
            priority="high",
            pet_id="pet_001",
            category="exercise"
        )

        # Assert initial state is not completed
        assert task.is_completed is False, "Task should start as incomplete"

        # Act: Mark the task as complete
        task.mark_complete()

        # Assert: Task should now be completed
        assert task.is_completed is True, "Task should be marked as completed after calling mark_complete()"

    def test_daily_task_creates_next_occurrence_when_completed(self):
        """Verify that a daily task returns a new task for tomorrow when completed."""
        task = Task(
            name="Feed Cat",
            duration_minutes=10,
            priority="high",
            pet_id="pet_001",
            frequency="daily",
            due_date=date.today(),
        )

        next_task = task.mark_complete()

        assert task.is_completed is True
        assert next_task is not None, "Daily tasks should create a next occurrence"
        assert next_task is not task, "The next occurrence should be a new Task instance"
        assert next_task.frequency == "daily"
        assert next_task.is_completed is False
        assert next_task.due_date == date.today() + timedelta(days=1)

    def test_weekly_task_manager_registers_next_occurrence(self):
        """Verify that TaskManager stores the next weekly occurrence after completion."""
        task_manager = TaskManager()
        task = Task(
            name="Groom Dog",
            duration_minutes=30,
            priority="medium",
            pet_id="pet_001",
            frequency="weekly",
            due_date=date.today(),
        )
        task_manager.add_task(task)

        next_task = task_manager.mark_task_complete(task.id)

        assert task.is_completed is True
        assert next_task is not None, "Weekly tasks should create a next occurrence"
        assert next_task.due_date == date.today() + timedelta(days=7)
        assert next_task.id in task_manager.tasks, "The new recurring task should be stored in the manager"


class TestTaskAddition:
    """Test suite for adding tasks to pets."""

    def test_add_task_increases_pet_task_count(self):
        """Verify that adding a task to a Pet increases that pet's task count."""
        # Arrange: Create a pet with an empty task list
        pet = Pet(
            name="Buddy",
            species="Golden Retriever",
            age=5,
            pet_id="pet_001",
            special_needs=["joint care"]
        )

        # Create a task
        task = Task(
            name="Morning Walk",
            duration_minutes=30,
            priority="high",
            pet_id="pet_001",
            category="exercise"
        )

        # Assert initial task count is 0
        initial_count = len(pet.tasks)
        assert initial_count == 0, "Pet should start with no tasks"

        # Act: Add the task to the pet
        pet.add_task(task)

        # Assert: Task count should have increased by 1
        final_count = len(pet.tasks)
        assert final_count == initial_count + \
            1, "Task count should increase by 1 after adding a task"
        assert final_count == 1, "Pet should now have 1 task"
        assert pet.tasks[0] == task, "The added task should be retrievable from the pet's tasks"


class TestSchedulerBehavior:
    """Test suite for scheduler ordering and conflict handling."""

    def test_sort_by_time_returns_tasks_in_chronological_order(self):
        """Verify that tasks with time constraints are ordered from earliest to latest."""
        owner = Owner(
            name="Alex",
            available_hours=(time(8, 0), time(18, 0)),
            preferences={},
            pets=[],
        )
        scheduler = Scheduler(owner, TaskManager())

        late_task = Task(
            name="Evening Check-in",
            duration_minutes=15,
            priority="medium",
            pet_id="pet_001",
            time_constraint=time(18, 0),
        )
        morning_task = Task(
            name="Morning Walk",
            duration_minutes=30,
            priority="high",
            pet_id="pet_001",
            time_constraint=time(9, 0),
        )
        midday_task = Task(
            name="Lunch Meds",
            duration_minutes=10,
            priority="low",
            pet_id="pet_001",
            time_constraint=time(12, 0),
        )

        ordered_tasks = scheduler.sort_by_time(
            [late_task, morning_task, midday_task])

        assert ordered_tasks == [morning_task, midday_task, late_task]

    def test_detect_conflicts_flags_duplicate_times(self):
        """Verify that the scheduler warns when two scheduled tasks overlap."""
        owner = Owner(
            name="Alex",
            available_hours=(time(8, 0), time(18, 0)),
            preferences={},
            pets=[],
        )
        scheduler = Scheduler(owner, TaskManager())

        first_task = Task(
            name="Morning Walk",
            duration_minutes=30,
            priority="high",
            pet_id="pet_001",
        )
        second_task = Task(
            name="Duplicate Time Grooming",
            duration_minutes=30,
            priority="medium",
            pet_id="pet_001",
        )

        conflicts = scheduler.detect_conflicts([
            ScheduledTask(first_task, time(10, 0), time(10, 30)),
            ScheduledTask(second_task, time(10, 0), time(10, 30)),
        ])

        assert len(conflicts) == 1
        assert "Conflict:" in conflicts[0]
