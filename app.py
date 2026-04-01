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

col1, col2, col3, col4 = st.columns(4)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
with col4:
    preferred_time_input = st.selectbox("Preferred time", ["(none)", "morning", "afternoon", "evening"])

PRIORITY_BADGE = {"high": "🔴 High", "medium": "🟡 Medium", "low": "🟢 Low"}

if st.button("Add task"):
    pref = None if preferred_time_input == "(none)" else preferred_time_input
    st.session_state.tasks.append({
        "title": task_title,
        "duration_minutes": int(duration),
        "priority": priority,
        "preferred_time": pref,
    })

if st.session_state.tasks:
    display_tasks = [
        {
            "Title": t["title"],
            "Duration (min)": t["duration_minutes"],
            "Priority": PRIORITY_BADGE[t["priority"]],
            "Preferred Time": t.get("preferred_time") or "—",
        }
        for t in st.session_state.tasks
    ]
    st.write("Current tasks:")
    st.table(display_tasks)
    if st.button("Clear all tasks"):
        st.session_state.tasks = []
        st.rerun()
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")

if st.button("Generate schedule"):
    owner = Owner(name=owner_name, available_minutes=int(available_minutes))
    pet = Pet(name=pet_name, species=species, age=int(pet_age))

    for t in st.session_state.tasks:
        pet.add_task(PetTask(
            title=t["title"],
            duration_minutes=t["duration_minutes"],
            priority=t["priority"],
            preferred_time=t.get("preferred_time"),
        ))

    owner.add_pet(pet)
    scheduler = Scheduler(owner=owner)
    scheduler.build_plan()

    scheduled = scheduler.get_schedule()
    reasoning = scheduler.explain_plan()
    total = scheduler.total_scheduled_time()

    conflicts   = [r for r in reasoning if r.startswith("CONFLICT")]
    slot_warns  = [r for r in reasoning if r.startswith("Warning")]
    skipped     = [r for r in reasoning if r.startswith("Skipped")]
    added       = [r for r in reasoning if r.startswith("Added")]

    if scheduled:
        pct = int((total / int(available_minutes)) * 100)
        st.success(f"Schedule built — {total} min of {int(available_minutes)} min used ({pct}%).")
        st.progress(min(pct, 100) / 100)

        if conflicts:
            for c in conflicts:
                st.error(f"⚠️ {c}")

        if slot_warns:
            for w in slot_warns:
                st.warning(f"📋 {w}")

        st.markdown("#### Scheduled Tasks (sorted by priority)")
        schedule_display = [
            {
                "Pet": p.name,
                "Task": task.title,
                "Duration (min)": task.duration_minutes,
                "Priority": PRIORITY_BADGE[task.priority],
                "Preferred Time": task.preferred_time or "—",
            }
            for p, task in scheduled
        ]
        st.table(schedule_display)

        if skipped:
            with st.expander(f"⏭️ {len(skipped)} task(s) skipped — not enough time"):
                for note in skipped:
                    st.write(f"- {note}")

        with st.expander("📝 Full scheduling reasoning"):
            for note in added:
                st.write(f"- {note}")
    else:
        st.warning("No tasks could be scheduled. Check your available time or add tasks.")
        for note in reasoning:
            if note.startswith("CONFLICT"):
                st.error(f"⚠️ {note}")
            elif note.startswith("Warning"):
                st.warning(f"📋 {note}")
            else:
                st.write(f"- {note}")
