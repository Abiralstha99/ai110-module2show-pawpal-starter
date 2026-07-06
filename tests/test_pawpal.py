"""
Simple tests for PawPal Task Scheduling System
"""

import pytest
from datetime import date, time
from pawpal_system import Task, Pet, Owner


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
