"""
Main script to demonstrate the PawPal Task Scheduling System
Creates an owner with pets and tasks, then displays today's schedule
"""

from datetime import date, time, timedelta
from pawpal_system import Pet, Owner, Task, TaskManager, Scheduler, DailyPlan


def main():
    """Run the PawPal scheduling demo."""

    print("=" * 60)
    print("🐾 PawPal Task Scheduling System - Demo 🐾")
    print("=" * 60)

    # Create Pets
    print("\n📋 Creating Pets...")
    buddy = Pet(
        name="Buddy",
        species="Golden Retriever",
        age=5,
        pet_id="pet_001",
        special_needs=["joint care"]
    )
    print(f"  ✓ Created {buddy.name} ({buddy.species})")

    whiskers = Pet(
        name="Whiskers",
        species="Tabby Cat",
        age=3,
        pet_id="pet_002",
        special_needs=["sensitive stomach"]
    )
    print(f"  ✓ Created {whiskers.name} ({whiskers.species})")

    luna = Pet(
        name="Luna",
        species="Siamese Cat",
        age=2,
        pet_id="pet_003",
        special_needs=[]
    )
    print(f"  ✓ Created {luna.name} ({luna.species})")

    # Create Owner with availability hours (9 AM to 7 PM)
    print("\n👤 Creating Owner...")
    owner = Owner(
        name="Alice",
        available_hours=(time(9, 0), time(19, 0)),
        preferences={"likes_morning_walks": True,
                     "outdoor_preference": "park"},
        pets=[buddy, whiskers, luna]
    )
    print(f"  ✓ Created owner: {owner.name}")
    print(
        f"    Available hours: {owner.available_hours[0].strftime('%I:%M %p')} - {owner.available_hours[1].strftime('%I:%M %p')}")

    # Create TaskManager
    print("\n📝 Creating Task Manager...")
    task_manager = TaskManager()
    print("  ✓ Task Manager initialized")

    # Create Tasks with different times
    print("\n🎯 Creating Tasks...")
    today = date.today()

    # Task 1: Morning Walk for Buddy (8 AM - fixed time)
    task1 = Task(
        name="Morning Walk",
        duration_minutes=30,
        priority="high",
        pet_id="pet_001",
        time_constraint=time(8, 0),
        frequency="daily",
        due_date=today,
        category="exercise"
    )
    print(f"  ✓ Task 1: {task1.name} - {task1.name} (Buddy) @ {task1.time_constraint.strftime('%I:%M %p')}, {task1.duration_minutes} min")

    # Task 2: Feeding for Whiskers (12 PM - lunch time)
    task2 = Task(
        name="Lunch & Medication",
        duration_minutes=15,
        priority="high",
        pet_id="pet_002",
        time_constraint=time(12, 0),
        frequency="daily",
        due_date=today,
        category="feeding"
    )
    print(
        f"  ✓ Task 2: {task2.name} (Whiskers) @ {task2.time_constraint.strftime('%I:%M %p')}, {task2.duration_minutes} min")

    # Task 3: Grooming for Luna (3 PM - flexible time)
    task3 = Task(
        name="Grooming & Play",
        duration_minutes=45,
        priority="medium",
        pet_id="pet_003",
        time_constraint=time(15, 0),
        frequency="weekly",
        due_date=today,
        category="grooming"
    )
    print(
        f"  ✓ Task 3: {task3.name} (Luna) @ {task3.time_constraint.strftime('%I:%M %p')}, {task3.duration_minutes} min")

    # Task 4: Evening Walk for Buddy (6 PM)
    task4 = Task(
        name="Evening Walk",
        duration_minutes=30,
        priority="high",
        pet_id="pet_001",
        time_constraint=time(18, 0),
        frequency="daily",
        due_date=today,
        category="exercise"
    )
    print(
        f"  ✓ Task 4: {task4.name} (Buddy) @ {task4.time_constraint.strftime('%I:%M %p')}, {task4.duration_minutes} min")

    # Add tasks to TaskManager
    print("\n📌 Adding tasks to TaskManager...")
    task_manager.add_task(task1)
    task_manager.add_task(task2)
    task_manager.add_task(task3)
    task_manager.add_task(task4)
    print(f"  ✓ Added {4} tasks to manager")

    # Create Scheduler
    print("\n⚙️  Initializing Scheduler...")
    scheduler = Scheduler(owner, task_manager)
    print("  ✓ Scheduler ready")

    # Display Today's Schedule
    print("\n" + "=" * 60)
    print(f"📅 TODAY'S SCHEDULE - {today.strftime('%A, %B %d, %Y')}")
    print("=" * 60)

    print(f"\nOwner: {owner.name}")
    print(f"Pets: {', '.join([pet.name for pet in owner.pets])}")
    print(
        f"Available: {owner.available_hours[0].strftime('%I:%M %p')} - {owner.available_hours[1].strftime('%I:%M %p')}\n")

    # Display tasks by time
    tasks = [task1, task2, task3, task4]
    tasks_sorted = sorted(
        tasks, key=lambda t: t.time_constraint if t.time_constraint else time.max)

    print("📋 Tasks by Time:")
    print("-" * 60)
    for task in tasks_sorted:
        # Find pet name
        pet_name = next(
            (p.name for p in owner.pets if p.pet_id == task.pet_id), "Unknown")
        time_str = task.time_constraint.strftime(
            '%I:%M %p') if task.time_constraint else "No fixed time"
        priority_icon = "🔴" if task.priority == "high" else "🟡" if task.priority == "medium" else "🟢"

        print(f"{priority_icon} {time_str:12} | {task.name:20} ({pet_name})")
        print(
            f"             | Duration: {task.duration_minutes} min | Category: {task.category}")
        print()

    print("=" * 60)
    print("Legend: 🔴 High Priority | 🟡 Medium Priority | 🟢 Low Priority")
    print("=" * 60)


if __name__ == "__main__":
    main()
