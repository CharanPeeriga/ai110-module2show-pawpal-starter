from pawpal_system import Owner, Pet, PetTask, Scheduler

# --- Create Owner ---
owner = Owner(name="Alex", available_minutes=90)

# --- Create Pets ---
dog = Pet(name="Buddy", species="Dog", age=3)
cat = Pet(name="Luna", species="Cat", age=5)

# --- Add Tasks to Buddy (Dog) ---
dog.add_task(PetTask(
    title="Morning Walk",
    duration_minutes=30,
    priority="high",
    description="Walk around the block",
    frequency="daily",
    preferred_time="morning"
))
dog.add_task(PetTask(
    title="Brush Teeth",
    duration_minutes=10,
    priority="medium",
    description="Use dog toothbrush and paste",
    frequency="daily"
))

# --- Add Tasks to Luna (Cat) ---
cat.add_task(PetTask(
    title="Clean Litter Box",
    duration_minutes=5,
    priority="high",
    description="Scoop and replace litter",
    frequency="daily"
))
cat.add_task(PetTask(
    title="Playtime",
    duration_minutes=20,
    priority="low",
    description="Feather wand and toy mouse",
    frequency="daily",
    preferred_time="evening"
))
cat.add_task(PetTask(
    title="Flea Treatment",
    duration_minutes=15,
    priority="medium",
    description="Apply monthly flea prevention",
    frequency="weekly"
))

# --- Add Pets to Owner ---
owner.add_pet(dog)
owner.add_pet(cat)

# --- Build Schedule ---
scheduler = Scheduler(owner=owner)
scheduler.build_plan()

# --- Print Today's Schedule ---
print("=" * 40)
print("       PAWPAL+ TODAY'S SCHEDULE")
print("=" * 40)
print(f"Owner : {owner.name}")
print(f"Available time: {owner.available_minutes} min")
print("-" * 40)

schedule = scheduler.get_schedule()
if schedule:
    for i, task in enumerate(schedule, 1):
        time_label = f"[{task.preferred_time}]" if task.preferred_time else ""
        print(f"{i}. {task.title} — {task.duration_minutes} min  "
              f"(priority: {task.priority}) {time_label}")
else:
    print("No tasks scheduled.")

print("-" * 40)
print(f"Total scheduled time: {scheduler.total_scheduled_time()} min")
print()
print("Scheduling Reasoning:")
for note in scheduler.explain_plan():
    print(f"  • {note}")
print("=" * 40)
