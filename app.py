from datetime import date, time

import streamlit as st
from pawpal_system import DailyPlan, Owner, Pet, Scheduler, Task, TaskManager

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Owner and Pet Setup")
owner_name = st.text_input("Owner name", value="Jordan")
owner_start = st.time_input("Available start", value=time(9, 0))
owner_end = st.time_input("Available end", value=time(19, 0))

if "pets" not in st.session_state:
    st.session_state.pets = []

pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])
pet_age = st.number_input("Pet age", min_value=0, max_value=40, value=3)
special_needs = st.text_input("Special needs", value="", help="Separate multiple items with commas")

pet_col1, pet_col2 = st.columns([1, 2])
with pet_col1:
    add_pet = st.button("Add Pet")

if add_pet:
    pet_id = f"pet_{len(st.session_state.pets) + 1:03d}"
    pet = Pet(
        name=pet_name,
        species=species,
        age=int(pet_age),
        pet_id=pet_id,
        special_needs=[item.strip() for item in special_needs.split(",") if item.strip()],
    )
    st.session_state.pets.append(pet)
    st.success(f"Added {pet.name} to the owner profile.")

if st.session_state.pets:
    st.write("Current pets:")
    st.table(
        [
            {
                "pet_id": pet.pet_id,
                "name": pet.name,
                "species": pet.species,
                "age": pet.age,
            }
            for pet in st.session_state.pets
        ]
    )
else:
    st.info("Add at least one pet to start building tasks and schedules.")

st.markdown("### Tasks")
st.caption("Add a task, attach it to a pet, then generate a schedule from the methods in pawpal_system.py.")

if "tasks" not in st.session_state:
    st.session_state.tasks = []
if "task_manager" not in st.session_state:
    st.session_state.task_manager = TaskManager()

if st.session_state.pets:
    pet_options = {f"{pet.name} ({pet.pet_id})": pet.pet_id for pet in st.session_state.pets}
    selected_pet_label = st.selectbox("Assign task to", list(pet_options.keys()))
else:
    pet_options = {}
    selected_pet_label = None

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input(
        "Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

task_time = st.time_input("Time constraint", value=time(8, 0))

if st.button("Add task"):
    if not st.session_state.pets:
        st.warning("Add a pet first so the task can be assigned to it.")
    else:
        selected_pet_id = pet_options[selected_pet_label]
        task = Task(
            name=task_title,
            duration_minutes=int(duration),
            priority=priority,
            pet_id=selected_pet_id,
            time_constraint=task_time,
            due_date=date.today(),
        )
        st.session_state.tasks.append(task)
        st.session_state.task_manager.add_task(task)

        for pet in st.session_state.pets:
            if pet.pet_id == selected_pet_id:
                pet.add_task(task)
                break

        st.success(f"Added '{task.name}' and linked it to the selected pet.")

if st.session_state.tasks:
    st.write("Current tasks:")
    st.table(
        [
            {
                "name": task.name,
                "duration_minutes": task.duration_minutes,
                "priority": task.priority,
                "pet_id": task.pet_id,
                "time_constraint": task.time_constraint.strftime("%H:%M") if task.time_constraint else "",
            }
            for task in st.session_state.tasks
        ]
    )
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("This button now calls Scheduler.generate_plan() and renders the resulting DailyPlan.")

if st.button("Generate schedule"):
    if not st.session_state.pets:
        st.warning("Add at least one pet before generating a schedule.")
    elif not st.session_state.tasks:
        st.warning("Add at least one task before generating a schedule.")
    else:
        owner = Owner(
            name=owner_name,
            available_hours=(owner_start, owner_end),
            preferences={},
            pets=st.session_state.pets,
        )
        scheduler = Scheduler(owner, st.session_state.task_manager)
        plan = scheduler.generate_plan(date.today())

        st.success("Schedule generated.")
        st.write(f"**Plan date:** {plan.plan_date.isoformat()}")
        st.write(f"**Explanation:** {plan.explanation}")

        if plan.scheduled_tasks:
            st.markdown("#### Scheduled tasks")
            for task in plan.scheduled_tasks:
                pet_name_lookup = next(
                    (pet.name for pet in st.session_state.pets if pet.pet_id == task.pet_id),
                    "Unknown",
                )
                st.write(f"- {task.name} ({pet_name_lookup}) - {task.duration_minutes} min [{task.priority}]")

        if plan.unscheduled_tasks:
            st.markdown("#### Unscheduled tasks")
            for task in plan.unscheduled_tasks:
                pet_name_lookup = next(
                    (pet.name for pet in st.session_state.pets if pet.pet_id == task.pet_id),
                    "Unknown",
                )
                st.write(f"- {task.name} ({pet_name_lookup}) - {task.duration_minutes} min [{task.priority}]")
