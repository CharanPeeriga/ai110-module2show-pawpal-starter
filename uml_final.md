classDiagram
    class Scheduler {
        +Owner owner
        +List~Tuple~ schedule
        +List~str~ reasoning
        +int slot_warning_threshold
        +int slot_duration_threshold
        +build_plan() void
        +explain_plan() List~str~
        +get_schedule() List~Tuple~
        +get_schedule_for_pet(pet_name) List~Tuple~
        +get_pending_tasks() List~Tuple~
        +get_completed_tasks() List~Tuple~
        +mark_task_complete(title) void
        +total_scheduled_time() int
    }

    class Owner {
        +str name
        +int available_minutes
        +List~Pet~ pets
        +add_pet(pet) void
        +remove_pet(name) void
        +set_availability(minutes) void
        +get_pet_tasks() List~Tuple~
    }

    class Pet {
        +str name
        +str species
        +int age
        +List~PetTask~ tasks
        +add_task(task) void
        +remove_task(title) void
        +get_pending_tasks() List~PetTask~
        +get_completed_tasks() List~PetTask~
    }

    class PetTask {
        +str title
        +int duration_minutes
        +str priority
        +str description
        +str frequency
        +str preferred_time
        +str start_time
        +bool completed
        +date last_completed_date
        +is_high_priority() bool
        +priority_score() int
        +time_slot() int
        +mark_complete() void
        +reset() void
        +next_occurrence() PetTask
    }

    Scheduler "1" --> "1" Owner : uses
    Owner "1" --> "many" Pet : has
    Pet "1" --> "many" PetTask : has
