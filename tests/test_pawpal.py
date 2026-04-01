import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from pawpal_system import Pet, PetTask, Owner, Scheduler


# ──────────────────────────────────────────────────────────────────────
# Existing tests (kept intact)
# ──────────────────────────────────────────────────────────────────────

def test_mark_complete_changes_status():
    task = PetTask(title="Morning Walk", duration_minutes=30, priority="high")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_count():
    pet = Pet(name="Buddy", species="Dog", age=3)
    assert len(pet.tasks) == 0
    pet.add_task(PetTask(title="Walk", duration_minutes=20, priority="medium"))
    assert len(pet.tasks) == 1
    pet.add_task(PetTask(title="Feed", duration_minutes=5, priority="high"))
    assert len(pet.tasks) == 2


# ──────────────────────────────────────────────────────────────────────
# Validation tests
# ──────────────────────────────────────────────────────────────────────

def test_invalid_priority_raises():
    """Creating a task with an unsupported priority string should raise ValueError."""
    with pytest.raises(ValueError, match="Invalid priority"):
        PetTask(title="Nap", duration_minutes=10, priority="critical")


def test_invalid_start_time_raises():
    """Creating a task with a malformed start_time should raise ValueError."""
    with pytest.raises(ValueError, match="Invalid start_time"):
        PetTask(title="Walk", duration_minutes=20, priority="high", start_time="25:00")


def test_valid_start_time_accepted():
    """A correctly formatted start_time should be stored without error."""
    task = PetTask(title="Walk", duration_minutes=20, priority="high", start_time="08:30")
    assert task.start_time == "08:30"


# ──────────────────────────────────────────────────────────────────────
# Sorting correctness
# ──────────────────────────────────────────────────────────────────────

def test_schedule_sorted_by_priority_desc():
    """Tasks should appear in the schedule ordered high → medium → low priority."""
    owner = Owner(name="Alex", available_minutes=120)
    pet = Pet(name="Buddy", species="Dog", age=3)
    # Add in reverse priority order to prove sorting, not insertion order
    pet.add_task(PetTask(title="Low Task",    duration_minutes=10, priority="low",    frequency="as_needed"))
    pet.add_task(PetTask(title="High Task",   duration_minutes=10, priority="high",   frequency="as_needed"))
    pet.add_task(PetTask(title="Medium Task", duration_minutes=10, priority="medium", frequency="as_needed"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner=owner)
    scheduler.build_plan()

    titles = [task.title for _, task in scheduler.get_schedule()]
    assert titles.index("High Task") < titles.index("Medium Task")
    assert titles.index("Medium Task") < titles.index("Low Task")


def test_schedule_secondary_sort_by_time_slot():
    """Within the same priority, morning tasks should appear before afternoon tasks."""
    owner = Owner(name="Alex", available_minutes=120)
    pet = Pet(name="Buddy", species="Dog", age=3)
    # Add afternoon before morning to prove sorting
    pet.add_task(PetTask(title="Afternoon High", duration_minutes=10, priority="high",
                         preferred_time="afternoon", frequency="as_needed"))
    pet.add_task(PetTask(title="Morning High",   duration_minutes=10, priority="high",
                         preferred_time="morning",   frequency="as_needed"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner=owner)
    scheduler.build_plan()

    titles = [task.title for _, task in scheduler.get_schedule()]
    assert titles.index("Morning High") < titles.index("Afternoon High")


# ──────────────────────────────────────────────────────────────────────
# Recurrence logic
# ──────────────────────────────────────────────────────────────────────

def test_mark_task_complete_creates_next_occurrence_for_daily():
    """Completing a daily task via the Scheduler should add a new task copy to the pet."""
    owner = Owner(name="Alex", available_minutes=120)
    pet = Pet(name="Buddy", species="Dog", age=3)
    pet.add_task(PetTask(title="Walk", duration_minutes=30, priority="high", frequency="daily"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner=owner)
    scheduler.build_plan()

    task_count_before = len(pet.tasks)
    scheduler.mark_task_complete("Walk")
    task_count_after = len(pet.tasks)

    assert task_count_after == task_count_before + 1


def test_mark_task_complete_creates_next_occurrence_for_weekly():
    """Completing a weekly task via the Scheduler should also add a new task copy."""
    owner = Owner(name="Alex", available_minutes=120)
    pet = Pet(name="Luna", species="Cat", age=5)
    pet.add_task(PetTask(title="Flea Treatment", duration_minutes=15, priority="medium",
                         frequency="weekly"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner=owner)
    scheduler.build_plan()

    task_count_before = len(pet.tasks)
    scheduler.mark_task_complete("Flea Treatment")
    task_count_after = len(pet.tasks)

    assert task_count_after == task_count_before + 1


def test_next_occurrence_is_not_completed():
    """next_occurrence() should return a fresh, incomplete copy of the task."""
    task = PetTask(title="Feed", duration_minutes=10, priority="high", frequency="daily")
    task.mark_complete()
    next_task = task.next_occurrence()

    assert next_task.completed is False
    assert next_task.title == "Feed"


def test_mark_task_complete_no_next_occurrence_for_as_needed():
    """Completing an as_needed task should NOT add a new task to the pet."""
    owner = Owner(name="Alex", available_minutes=120)
    pet = Pet(name="Buddy", species="Dog", age=3)
    pet.add_task(PetTask(title="Vet Visit", duration_minutes=60, priority="high",
                         frequency="as_needed"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner=owner)
    scheduler.build_plan()

    task_count_before = len(pet.tasks)
    scheduler.mark_task_complete("Vet Visit")
    task_count_after = len(pet.tasks)

    # as_needed tasks do not auto-generate a next occurrence
    assert task_count_after == task_count_before


# ──────────────────────────────────────────────────────────────────────
# Conflict detection
# ──────────────────────────────────────────────────────────────────────

def test_conflict_detected_for_same_start_time():
    """Two tasks pinned to the same clock time should produce a CONFLICT warning."""
    owner = Owner(name="Alex", available_minutes=120)

    pet1 = Pet(name="Buddy", species="Dog", age=3)
    pet1.add_task(PetTask(title="Morning Feed", duration_minutes=10, priority="high",
                          start_time="08:00", frequency="as_needed"))

    pet2 = Pet(name="Luna", species="Cat", age=5)
    pet2.add_task(PetTask(title="Morning Feed", duration_minutes=10, priority="high",
                          start_time="08:00", frequency="as_needed"))

    owner.add_pet(pet1)
    owner.add_pet(pet2)

    scheduler = Scheduler(owner=owner)
    scheduler.build_plan()

    conflict_warnings = [r for r in scheduler.explain_plan() if "CONFLICT" in r]
    assert len(conflict_warnings) >= 1
    assert "08:00" in conflict_warnings[0]


def test_no_conflict_for_different_start_times():
    """Tasks at distinct clock times should NOT produce any CONFLICT warning."""
    owner = Owner(name="Alex", available_minutes=120)
    pet = Pet(name="Buddy", species="Dog", age=3)
    pet.add_task(PetTask(title="Morning Walk", duration_minutes=10, priority="high",
                         start_time="08:00", frequency="as_needed"))
    pet.add_task(PetTask(title="Evening Walk", duration_minutes=10, priority="medium",
                         start_time="18:00", frequency="as_needed"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner=owner)
    scheduler.build_plan()

    conflict_warnings = [r for r in scheduler.explain_plan() if "CONFLICT" in r]
    assert len(conflict_warnings) == 0


# ──────────────────────────────────────────────────────────────────────
# Edge cases
# ──────────────────────────────────────────────────────────────────────

def test_pet_with_no_tasks_produces_empty_schedule():
    """An owner with a pet that has no tasks should yield an empty schedule."""
    owner = Owner(name="Alex", available_minutes=60)
    pet = Pet(name="Goldfish", species="Fish", age=1)
    owner.add_pet(pet)

    scheduler = Scheduler(owner=owner)
    scheduler.build_plan()

    assert scheduler.get_schedule() == []


def test_task_skipped_when_exceeds_available_time():
    """A task too long for the remaining time budget should be skipped, not scheduled."""
    owner = Owner(name="Alex", available_minutes=20)
    pet = Pet(name="Buddy", species="Dog", age=3)
    pet.add_task(PetTask(title="Short Task", duration_minutes=15, priority="high",
                         frequency="as_needed"))
    pet.add_task(PetTask(title="Long Task",  duration_minutes=60, priority="medium",
                         frequency="as_needed"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner=owner)
    scheduler.build_plan()

    scheduled_titles = [task.title for _, task in scheduler.get_schedule()]
    assert "Short Task" in scheduled_titles
    assert "Long Task" not in scheduled_titles

    skipped_notes = [r for r in scheduler.explain_plan() if "Skipped" in r and "Long Task" in r]
    assert len(skipped_notes) == 1


def test_daily_task_excluded_if_already_completed_today():
    """A completed daily task should be filtered out and not re-scheduled."""
    owner = Owner(name="Alex", available_minutes=120)
    pet = Pet(name="Buddy", species="Dog", age=3)
    task = PetTask(title="Walk", duration_minutes=30, priority="high", frequency="daily")
    task.mark_complete()          # marks completed=True and last_completed_date=today
    pet.add_task(task)
    owner.add_pet(pet)

    scheduler = Scheduler(owner=owner)
    scheduler.build_plan()

    scheduled_titles = [t.title for _, t in scheduler.get_schedule()]
    assert "Walk" not in scheduled_titles


def test_get_schedule_for_pet_filters_correctly():
    """get_schedule_for_pet should return only tasks belonging to the named pet."""
    owner = Owner(name="Alex", available_minutes=120)

    pet1 = Pet(name="Buddy", species="Dog", age=3)
    pet1.add_task(PetTask(title="Walk", duration_minutes=20, priority="high",
                          frequency="as_needed"))

    pet2 = Pet(name="Luna", species="Cat", age=5)
    pet2.add_task(PetTask(title="Playtime", duration_minutes=15, priority="medium",
                          frequency="as_needed"))

    owner.add_pet(pet1)
    owner.add_pet(pet2)

    scheduler = Scheduler(owner=owner)
    scheduler.build_plan()

    buddy_schedule = scheduler.get_schedule_for_pet("Buddy")
    assert all(pet.name == "Buddy" for pet, _ in buddy_schedule)
    assert any(task.title == "Walk" for _, task in buddy_schedule)
