# PawPal+ (Module 2 Project)

**PawPal+** is a Streamlit app that helps a pet owner build a smart daily care schedule for their pets — accounting for time constraints, task priorities, preferred time-of-day slots, and recurring task logic.

## 📸 Demo

<a href="/course_images/ai110/uml.png" target="_blank"><img src='/course_images/ai110/uml.png' title='PawPal App' width='' alt='PawPal App' class='center-block' /></a>

## ✨ Features

- **Owner & pet setup** — Enter your name, daily available minutes, and pet details (name, species, age) before generating a plan.
- **Task management** — Add unlimited care tasks (walks, feeding, meds, grooming, enrichment, etc.) with a title, duration, priority level, and optional preferred time-of-day slot.
- **Priority-based sorting** — Tasks are sorted high → medium → low priority so the most important care always comes first.
- **Time-slot ordering** — Within the same priority tier, tasks are further sorted morning → afternoon → evening, mirroring a natural daily rhythm.
- **Time-budget enforcement** — The scheduler tracks cumulative minutes and automatically skips tasks that would exceed the owner's available time, preventing over-scheduling.
- **Frequency filtering** — Daily and weekly tasks already completed within their recurrence window are excluded from today's plan; `as_needed` tasks are always eligible.
- **Conflict detection** — Warns when two tasks share the exact same clock time (exact overlap), when a single time slot is crowded with too many tasks (slot crowding), or when duplicate task titles are added (duplicate warning).
- **Auto next-occurrence on completion** — Completing a recurring (`daily`/`weekly`) task automatically queues a fresh copy for the next occurrence, so nothing falls through the cracks.
- **Reasoning log** — A collapsible "Full scheduling reasoning" panel shows exactly why each task was added or skipped, making the scheduling logic transparent.
- **Progress indicator** — A visual progress bar shows what percentage of available time has been filled by the generated schedule.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Testing PawPal+

### Running the test suite

```bash
python -m pytest
```

Run with verbose output to see each test by name:

```bash
python -m pytest -v
```

### What the tests cover

- **Validation** — confirms that invalid priority values and malformed `start_time` strings raise errors immediately
- **Sorting correctness** — verifies the schedule is ordered by priority descending (high → medium → low), with morning tasks appearing before afternoon tasks within the same priority
- **Recurrence logic** — confirms that completing a `daily` or `weekly` task automatically adds a fresh next-occurrence to the pet, while `as_needed` tasks do not produce one
- **Conflict detection** — verifies that two tasks pinned to the same clock time produce a `CONFLICT` warning in the reasoning log, and that tasks at different times do not
- **Edge cases** — checks behavior when a pet has no tasks, when a task exceeds the available time budget and is skipped, and when a daily task already completed today is excluded from the plan

### Confidence Level

★★★★☆ (4/5)

The core scheduling behaviors — sorting, recurrence, conflict detection, and time budgeting — are all verified and passing across 17 tests. One star is withheld because the Streamlit UI layer (`app.py`) is not yet covered by automated tests, so end-to-end user interactions remain untested.