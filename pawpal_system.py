from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class PetTask:
    title: str
    duration_minutes: int
    priority: str  # "low", "medium", "high"
    preferred_time: Optional[str] = None  # e.g. "morning", "evening"

    def is_high_priority(self) -> bool:
        pass

    def priority_score(self) -> int:
        pass


@dataclass
class Pet:
    name: str
    species: str
    age: int
    tasks: List[PetTask] = field(default_factory=list)

    def add_task(self, task: PetTask) -> None:
        pass

    def remove_task(self, title: str) -> None:
        pass


@dataclass
class Owner:
    name: str
    available_minutes: int
    pet: Pet

    def set_availability(self, minutes: int) -> None:
        pass

    def get_pet_tasks(self) -> List[PetTask]:
        pass


@dataclass
class Scheduler:
    owner: Owner
    schedule: List[PetTask] = field(default_factory=list)
    reasoning: List[str] = field(default_factory=list)

    def build_plan(self) -> None:
        pass

    def explain_plan(self) -> List[str]:
        pass

    def get_schedule(self) -> List[PetTask]:
        pass
