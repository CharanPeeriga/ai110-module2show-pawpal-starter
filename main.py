import json
from pawpal_system import Owner, Pet, PetTask, Scheduler


def load_data(filepath: str) -> Owner:
    """Load owner, pets, and tasks from a JSON file."""
    with open(filepath) as f:
        data = json.load(f)

    owner_data = data["owner"]
    owner = Owner(name=owner_data["name"], available_minutes=owner_data["available_minutes"])

    for pet_data in data["pets"]:
        pet = Pet(name=pet_data["name"], species=pet_data["species"], age=pet_data["age"])
        for task_data in pet_data["tasks"]:
            pet.add_task(PetTask(**task_data))
        owner.add_pet(pet)

    return owner


# --- Load from JSON (no hard-coded data in main) ---
owner = load_data("pets_data.json")

# Grab pet references for adding extra tasks
dog = next(p for p in owner.pets if p.name == "Buddy")
cat = next(p for p in owner.pets if p.name == "Luna")

# --- Add tasks OUT OF ORDER to prove the scheduler sorts them correctly ---
# Low-priority task added first, then a high-priority one —
# the scheduler must reorder them: high before low, morning before evening.
dog.add_task(PetTask(
    title="Afternoon Nap Check",
    duration_minutes=5,
    priority="low",
    description="Make sure Buddy is resting comfortably",
    frequency="daily",
    preferred_time="afternoon",
))
cat.add_task(PetTask(
    title="Vet Medication",
    duration_minutes=10,
    priority="high",
    description="Administer prescribed medication",
    frequency="daily",
    preferred_time="morning",
))
dog.add_task(PetTask(
    title="Evening Grooming",
    duration_minutes=15,
    priority="medium",
    description="Brush coat and check paws",
    frequency="weekly",
    preferred_time="evening",
))

# --- Same-time conflict demo ---
# Both tasks are pinned to 08:00 — the scheduler should flag this as a conflict.
dog.add_task(PetTask(
    title="Morning Feed",
    duration_minutes=5,
    priority="high",
    description="Fill Buddy's bowl with kibble",
    frequency="daily",
    preferred_time="morning",
    start_time="08:00",
))
cat.add_task(PetTask(
    title="Morning Feed",
    duration_minutes=5,
    priority="high",
    description="Fill Luna's bowl with wet food",
    frequency="daily",
    preferred_time="morning",
    start_time="08:00",
))

# --- Build Schedule ---
scheduler = Scheduler(owner=owner)
scheduler.build_plan()

# ------------------------------------------------------------------ #
# Full schedule — sorted by (priority DESC, time_slot ASC)
# ------------------------------------------------------------------ #
print("=" * 55)
print("          PAWPAL+ TODAY'S SCHEDULE")
print("=" * 55)
print(f"Owner          : {owner.name}")
print(f"Available time : {owner.available_minutes} min")
print("-" * 55)

schedule = scheduler.get_schedule()
if schedule:
    for i, (pet, task) in enumerate(schedule, 1):
        slot_label = f"[{task.preferred_time}]" if task.preferred_time else ""
        time_label = f" @{task.start_time}" if task.start_time else ""
        print(
            f"{i}. [{pet.name:6}] {task.title:<22} "
            f"{task.duration_minutes:>3} min  "
            f"priority={task.priority:<6} {slot_label}{time_label}"
        )
else:
    print("No tasks scheduled.")

print("-" * 55)
print(f"Total scheduled time: {scheduler.total_scheduled_time()} min")

# ------------------------------------------------------------------ #
# Scheduling reasoning + conflict warnings
# ------------------------------------------------------------------ #
print()
print("Scheduling Reasoning:")
for note in scheduler.explain_plan():
    print(f"  • {note}")
print("=" * 55)

# ------------------------------------------------------------------ #
# Filter: per-pet view
# ------------------------------------------------------------------ #
print()
print("=== Filter: Schedule for Buddy (Dog) ===")
buddy_tasks = scheduler.get_schedule_for_pet("Buddy")
if buddy_tasks:
    for pet, task in buddy_tasks:
        slot = task.preferred_time or "anytime"
        print(f"  - {task.title} ({task.duration_minutes} min, {task.priority}, {slot})")
else:
    print("  No tasks scheduled for Buddy.")

print()
print("=== Filter: Schedule for Luna (Cat) ===")
luna_tasks = scheduler.get_schedule_for_pet("Luna")
if luna_tasks:
    for pet, task in luna_tasks:
        slot = task.preferred_time or "anytime"
        print(f"  - {task.title} ({task.duration_minutes} min, {task.priority}, {slot})")
else:
    print("  No tasks scheduled for Luna.")

# ------------------------------------------------------------------ #
# Filter: pending vs completed
# ------------------------------------------------------------------ #
print()
print("=== Pending Tasks (before any completions) ===")
for pet, task in scheduler.get_pending_tasks():
    print(f"  [{pet.name}] {task.title}")

# ------------------------------------------------------------------ #
# Demo: mark_task_complete triggers next-occurrence auto-creation
# ------------------------------------------------------------------ #
print()
print("=== Demo: Mark 'Morning Walk' Complete ===")
scheduler.mark_task_complete("Morning Walk")
print("  'Morning Walk' marked complete.")

print()
print("=== Completed Tasks ===")
for pet, task in scheduler.get_completed_tasks():
    print(f"  [{pet.name}] {task.title}  (last_completed={task.last_completed_date})")

print()
print("=== Buddy's Full Task List (next occurrence auto-added) ===")
for task in dog.tasks:
    status = "DONE   " if task.completed else "pending"
    print(f"  [{status}] {task.title}  last_completed={task.last_completed_date}")
