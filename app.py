import streamlit as st
from pawpal_system import PetTask, Pet, Owner, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.divider()

st.subheader("Owner & Pet")
owner_name = st.text_input("Owner name", value="Jordan")
available_minutes = st.number_input("Available time (minutes)", min_value=1, max_value=480, value=60)
pet_name = st.text_input("Pet name", value="Mochi")
pet_age = st.number_input("Pet age", min_value=0, max_value=30, value=3)
species = st.selectbox("Species", ["dog", "cat", "other"])

st.markdown("### Tasks")

if "tasks" not in st.session_state:
    st.session_state.tasks = []

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

if st.button("Add task"):
    st.session_state.tasks.append(
        {"title": task_title, "duration_minutes": int(duration), "priority": priority}
    )

if st.session_state.tasks:
    st.write("Current tasks:")
    st.table(st.session_state.tasks)
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")

if st.button("Generate schedule"):
    # Build Owner and Pet from inputs
    owner = Owner(name=owner_name, available_minutes=int(available_minutes))
    pet = Pet(name=pet_name, species=species, age=int(pet_age))

    for t in st.session_state.tasks:
        pet.add_task(PetTask(
            title=t["title"],
            duration_minutes=t["duration_minutes"],
            priority=t["priority"],
        ))

    owner.add_pet(pet)

    # Run scheduler
    scheduler = Scheduler(owner=owner)
    scheduler.build_plan()

    scheduled = scheduler.get_schedule()
    reasoning = scheduler.explain_plan()
    total = scheduler.total_scheduled_time()

    if scheduled:
        st.success(f"Schedule built — {total} min of {int(available_minutes)} min used.")
        st.markdown("#### Scheduled Tasks")
        st.table([
            {"pet": pet.name, "title": task.title, "duration_minutes": task.duration_minutes, "priority": task.priority}
            for pet, task in scheduled
        ])
        st.markdown("#### Reasoning")
        for note in reasoning:
            st.write(f"- {note}")
    else:
        st.warning("No tasks could be scheduled. Check your available time or add tasks.")
        for note in reasoning:
            st.write(f"- {note}")
