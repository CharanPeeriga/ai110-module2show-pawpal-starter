from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class PetTask:
    title: str
    duration_minutes: int
    priority: str                       # "low", "medium", "high"
    description: str = ""
    frequency: str = "daily"            # "daily", "weekly", "as_needed"
    preferred_time: Optional[str] = None  # "morning", "afternoon", "evening"
    completed: bool = False

    def is_high_priority(self) -> bool:
        """Return True if this task's priority is high."""
        return self.priority == "high"

    def priority_score(self) -> int:
        """Return a numeric score for the task's priority level."""
        scores = {"high": 3, "medium": 2, "low": 1}
        return scores.get(self.priority, 0)

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def reset(self) -> None:
        """Reset this task to incomplete."""
        self.completed = False


@dataclass
class Pet:
    name: str
    species: str
    age: int
    tasks: List[PetTask] = field(default_factory=list)

    def add_task(self, task: PetTask) -> None:
        """Add a task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, title: str) -> None:
        """Remove the task matching the given title from this pet's task list."""
        self.tasks = [t for t in self.tasks if t.title != title]

    def get_pending_tasks(self) -> List[PetTask]:
        """Return all tasks that have not been completed."""
        return [t for t in self.tasks if not t.completed]

    def get_completed_tasks(self) -> List[PetTask]:
        """Return all tasks that have been completed."""
        return [t for t in self.tasks if t.completed]


@dataclass
class Owner:
    name: str
    available_minutes: int
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's pet list."""
        self.pets.append(pet)

    def remove_pet(self, name: str) -> None:
        """Remove the pet matching the given name from this owner's pet list."""
        self.pets = [p for p in self.pets if p.name != name]

    def set_availability(self, minutes: int) -> None:
        """Update the owner's available time in minutes."""
        self.available_minutes = minutes

    def get_pet_tasks(self) -> List[PetTask]:
        """Return all tasks across every pet owned by this owner."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.tasks)
        return all_tasks


@dataclass
class Scheduler:
    owner: Owner
    schedule: List[PetTask] = field(default_factory=list)
    reasoning: List[str] = field(default_factory=list)

    def build_plan(self) -> None:
        """Build a prioritized schedule fitting within the owner's available time."""
        self.schedule = []
        self.reasoning = []

        all_tasks = self.owner.get_pet_tasks()
        pending = [t for t in all_tasks if not t.completed]
        sorted_tasks = sorted(pending, key=lambda t: t.priority_score(), reverse=True)

        time_remaining = self.owner.available_minutes

        for task in sorted_tasks:
            if task.duration_minutes <= time_remaining:
                self.schedule.append(task)
                time_remaining -= task.duration_minutes
                self.reasoning.append(
                    f"Added '{task.title}' ({task.duration_minutes} min, priority={task.priority}). "
                    f"Time remaining: {time_remaining} min."
                )
            else:
                self.reasoning.append(
                    f"Skipped '{task.title}' ({task.duration_minutes} min) — "
                    f"not enough time remaining ({time_remaining} min)."
                )

    def explain_plan(self) -> List[str]:
        """Return the list of reasoning notes generated during plan building."""
        return self.reasoning

    def get_schedule(self) -> List[PetTask]:
        """Return the list of tasks included in the current schedule."""
        return self.schedule

    def mark_task_complete(self, title: str) -> None:
        """Mark the scheduled task with the given title as complete."""
        for task in self.schedule:
            if task.title == title:
                task.mark_complete()
                break

    def total_scheduled_time(self) -> int:
        """Return the total duration in minutes of all scheduled tasks."""
        return sum(t.duration_minutes for t in self.schedule)
