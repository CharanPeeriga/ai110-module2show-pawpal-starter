# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

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

### Smart Scheduling
- Frequency filtering — skips tasks already completed within their recurrence window (daily/weekly)
- Priority + time-slot sorting — tasks sorted by priority descending, then morning → afternoon → evening
- Conflict detection — warns on exact-time overlaps, slot crowding, and duplicate task titles
- Auto next-occurrence on completion — completing a recurring task automatically queues the next instance

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