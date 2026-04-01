import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pawpal_system import Pet, PetTask


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
