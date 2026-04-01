from dataclasses import dataclass, field
from typing import List, Optional, Tuple
from datetime import date
import copy

PRIORITY_SCORES = {"high": 3, "medium": 2, "low": 1}
TIME_SLOTS = {"morning": 1, "afternoon": 2, "evening": 3, None: 4}


@dataclass
class PetTask:
    title: str
    duration_minutes: int
    priority: str                          # must be "low", "medium", or "high"
    description: str = ""
    frequency: str = "daily"              # "daily", "weekly", "as_needed"
    preferred_time: Optional[str] = None  # "morning", "afternoon", "evening"
    start_time: Optional[str] = None      # exact clock time, e.g. "08:00"
    completed: bool = False
    last_completed_date: Optional[date] = None

    def __post_init__(self):
        """Validate priority and start_time fields after dataclass initialization."""
        if self.priority not in PRIORITY_SCORES:
            raise ValueError(
                f"Invalid priority '{self.priority}'. "
                f"Must be one of: {list(PRIORITY_SCORES)}"
            )
        if self.start_time is not None:
            try:
                hour, minute = self.start_time.split(":")
                if not (0 <= int(hour) <= 23 and 0 <= int(minute) <= 59):
                    raise ValueError()
            except (ValueError, AttributeError):
                raise ValueError(
                    f"Invalid start_time '{self.start_time}'. "
                    f"Expected 'HH:MM' format, e.g. '08:30'."
                )

    def is_high_priority(self) -> bool:
        """Return True if this task's priority is high."""
        return self.priority == "high"

    def priority_score(self) -> int:
        """Return a numeric score for the task's priority level."""
        return PRIORITY_SCORES[self.priority]

    def time_slot(self) -> int:
        """Return a numeric sort key for the preferred time of day."""
        return TIME_SLOTS.get(self.preferred_time, 4)

    def mark_complete(self) -> None:
        """Mark this task as completed and record today's date."""
        self.completed = True
        self.last_completed_date = date.today()

    def reset(self) -> None:
        """Reset this task to incomplete."""
        self.completed = False

    def next_occurrence(self) -> "PetTask":
        """Return a fresh copy of this task for the next scheduling cycle."""
        new_task = copy.copy(self)
        new_task.completed = False
        # last_completed_date stays as today so frequency filter works correctly
        new_task.last_completed_date = date.today()
        return new_task


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

    def get_pet_tasks(self) -> List[Tuple[Pet, PetTask]]:
        """Return all (Pet, PetTask) pairs across every pet owned by this owner."""
        pairs = []
        for pet in self.pets:
            for task in pet.tasks:
                pairs.append((pet, task))
        return pairs


@dataclass
class Scheduler:
    owner: Owner
    schedule: List[Tuple[Pet, PetTask]] = field(default_factory=list)
    reasoning: List[str] = field(default_factory=list)
    slot_warning_threshold: int = 3    # warn when N+ tasks share a time slot
    slot_duration_threshold: int = 45  # warn when a slot's total minutes exceeds this

    def build_plan(self) -> None:
        """Build a prioritized schedule fitting within the owner's available time."""
        self.schedule = []
        self.reasoning = []
        today = date.today()

        # Apply frequency filter to produce candidates
        candidates: List[Tuple[Pet, PetTask]] = []
        for pet, task in self.owner.get_pet_tasks():
            if task.completed:
                continue

            if task.frequency == "daily":
                include = task.last_completed_date != today
            elif task.frequency == "weekly":
                include = (
                    task.last_completed_date is None
                    or (today - task.last_completed_date).days >= 7
                )
            else:  # "as_needed" or unrecognized → always include
                include = True

            if include:
                candidates.append((pet, task))

        # Primary sort: priority DESC; secondary sort: time slot ASC
        candidates.sort(key=lambda pt: (-pt[1].priority_score(), pt[1].time_slot()))

        time_remaining = self.owner.available_minutes

        for pet, task in candidates:
            if task.duration_minutes <= time_remaining:
                self.schedule.append((pet, task))
                time_remaining -= task.duration_minutes
                self.reasoning.append(
                    f"Added '{task.title}' for {pet.name} "
                    f"({task.duration_minutes} min, priority={task.priority}). "
                    f"Time remaining: {time_remaining} min."
                )
            else:
                self.reasoning.append(
                    f"Skipped '{task.title}' for {pet.name} "
                    f"({task.duration_minutes} min) — "
                    f"not enough time remaining ({time_remaining} min)."
                )

        self._detect_conflicts()
        self._detect_time_conflicts()

    def _detect_time_conflicts(self) -> None:
        """Warn when two or more scheduled tasks share the same exact start_time.

        This is advisory only — it appends warning strings to self.reasoning
        and never raises or removes tasks from the schedule.
        """
        from collections import defaultdict

        # Only consider tasks that have an explicit start_time set
        by_time: dict = defaultdict(list)  # "HH:MM" -> [(pet_name, task_title)]
        for pet, task in self.schedule:
            if task.start_time is not None:
                by_time[task.start_time].append((pet.name, task.title))

        for start_time, entries in sorted(by_time.items()):
            if len(entries) < 2:
                continue
            labels = ", ".join(
                f"'{title}' ({pet_name})" for pet_name, title in entries
            )
            self.reasoning.append(
                f"CONFLICT at {start_time}: {len(entries)} tasks overlap — {labels}. "
                f"Consider staggering their start times."
            )

    def _detect_conflicts(self) -> None:
        """Append advisory warnings for time-slot crowding, overflow, and duplicate titles."""
        from collections import defaultdict

        slot_counts: dict = defaultdict(int)
        slot_durations: dict = defaultdict(int)
        slot_entries: dict = defaultdict(list)  # slot -> [(pet_name, title)]

        for pet, task in self.schedule:
            slot = task.preferred_time or "unspecified"
            slot_counts[slot] += 1
            slot_durations[slot] += task.duration_minutes
            slot_entries[slot].append((pet.name, task.title))

        for slot, count in slot_counts.items():
            if count >= self.slot_warning_threshold:
                self.reasoning.append(
                    f"Warning: {count} tasks assigned to '{slot}' — "
                    f"consider spreading across the day."
                )

        for slot, total_dur in slot_durations.items():
            if total_dur > self.slot_duration_threshold:
                self.reasoning.append(
                    f"Warning: '{slot}' tasks total {total_dur} min — "
                    f"exceeds the {self.slot_duration_threshold}-min threshold."
                )

        for slot, entries in slot_entries.items():
            titles = [title for _, title in entries]
            flagged: set = set()
            for title in titles:
                if titles.count(title) > 1 and title not in flagged:
                    flagged.add(title)
                    self.reasoning.append(
                        f"Warning: Duplicate task title '{title}' in '{slot}' slot — "
                        f"possible scheduling collision."
                    )

    # ------------------------------------------------------------------ #
    # Schedule accessors                                                   #
    # ------------------------------------------------------------------ #

    def get_schedule(self) -> List[Tuple[Pet, PetTask]]:
        """Return the full schedule as (Pet, PetTask) pairs."""
        return self.schedule

    def get_schedule_for_pet(self, pet_name: str) -> List[Tuple[Pet, PetTask]]:
        """Return scheduled (Pet, PetTask) pairs belonging to the named pet."""
        return [(pet, task) for pet, task in self.schedule if pet.name == pet_name]

    def get_pending_tasks(self) -> List[Tuple[Pet, PetTask]]:
        """Return scheduled tasks that are not yet completed."""
        return [(pet, task) for pet, task in self.schedule if not task.completed]

    def get_completed_tasks(self) -> List[Tuple[Pet, PetTask]]:
        """Return scheduled tasks that have been completed."""
        return [(pet, task) for pet, task in self.schedule if task.completed]

    def explain_plan(self) -> List[str]:
        """Return the list of reasoning notes generated during plan building."""
        return self.reasoning

    def mark_task_complete(self, title: str) -> None:
        """Mark the scheduled task with the given title as complete.

        For daily and weekly tasks, a fresh next-occurrence instance is
        automatically added back to the pet so it will reappear in the
        next build_plan call when the frequency window reopens.
        """
        for pet, task in self.schedule:
            if task.title == title:
                task.mark_complete()
                if task.frequency in ("daily", "weekly"):
                    pet.add_task(task.next_occurrence())
                break

    def total_scheduled_time(self) -> int:
        """Return the total duration in minutes of all scheduled tasks."""
        return sum(task.duration_minutes for _, task in self.schedule)
