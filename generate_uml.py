import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import os

def draw_uml_class(ax, x, y, width, class_name, attributes, methods,
                   header_color='#1a3a5c', attr_color='#f0f4f8', method_color='#ffffff',
                   line_height=0.32, padding=0.18, font_size=8.5):
    """Draw a UML class box. Returns total height of box."""
    title_h = 0.55
    attr_h = len(attributes) * line_height + 2 * padding
    method_h = len(methods) * line_height + 2 * padding
    total_h = title_h + attr_h + method_h

    # Header
    header = FancyBboxPatch((x, y - title_h), width, title_h,
                             boxstyle="square,pad=0", linewidth=1.5,
                             edgecolor='#1a3a5c', facecolor=header_color)
    ax.add_patch(header)
    ax.text(x + width / 2, y - title_h / 2, class_name,
            ha='center', va='center', fontsize=font_size + 1.5,
            fontweight='bold', color='white', fontfamily='monospace')

    # Attributes section
    attr_box = FancyBboxPatch((x, y - title_h - attr_h), width, attr_h,
                               boxstyle="square,pad=0", linewidth=1.5,
                               edgecolor='#1a3a5c', facecolor=attr_color)
    ax.add_patch(attr_box)
    for i, attr in enumerate(attributes):
        ay = y - title_h - padding - (i + 0.5) * line_height
        ax.text(x + 0.15, ay, f'+ {attr}', ha='left', va='center',
                fontsize=font_size, fontfamily='monospace', color='#1a1a2e')

    # Methods section
    method_box = FancyBboxPatch((x, y - title_h - attr_h - method_h), width, method_h,
                                 boxstyle="square,pad=0", linewidth=1.5,
                                 edgecolor='#1a3a5c', facecolor=method_color)
    ax.add_patch(method_box)
    for i, method in enumerate(methods):
        my = y - title_h - attr_h - padding - (i + 0.5) * line_height
        ax.text(x + 0.15, my, f'+ {method}', ha='left', va='center',
                fontsize=font_size, fontfamily='monospace', color='#1a1a2e')

    return total_h


def draw_arrow(ax, x1, y1, x2, y2, label, label_side='right'):
    """Draw a downward arrow with label."""
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color='#1a3a5c',
                                lw=1.8, connectionstyle='arc3,rad=0'))
    mid_y = (y1 + y2) / 2
    offset = 0.35 if label_side == 'right' else -0.35
    ax.text(x1 + offset, mid_y, label, ha='center', va='center',
            fontsize=8, color='#444', style='italic',
            bbox=dict(boxstyle='round,pad=0.15', facecolor='white', edgecolor='#ccc', alpha=0.85))


fig, ax = plt.subplots(figsize=(13, 20))
ax.set_xlim(0, 13)
ax.set_ylim(0, 20)
ax.axis('off')
fig.patch.set_facecolor('#f8f9fa')

title_text = 'PawPal+ — UML Class Diagram (Final)'
ax.text(6.5, 19.5, title_text, ha='center', va='center',
        fontsize=14, fontweight='bold', color='#1a3a5c',
        fontfamily='monospace')

W = 9.5   # box width
LX = 1.75  # left x of all boxes
CX = LX + W / 2  # center x

# ── Scheduler ──────────────────────────────────────────────────────────
sched_attrs = [
    'owner: Owner',
    'schedule: List[Tuple[Pet, PetTask]]',
    'reasoning: List[str]',
    'slot_warning_threshold: int',
    'slot_duration_threshold: int',
]
sched_methods = [
    'build_plan() : void',
    'explain_plan() : List[str]',
    'get_schedule() : List[Tuple]',
    'get_schedule_for_pet(pet_name) : List',
    'get_pending_tasks() : List',
    'get_completed_tasks() : List',
    'mark_task_complete(title) : void',
    'total_scheduled_time() : int',
]
sched_top = 19.0
sched_h = draw_uml_class(ax, LX, sched_top, W, 'Scheduler', sched_attrs, sched_methods)
sched_bottom = sched_top - sched_h

# ── Owner ───────────────────────────────────────────────────────────────
owner_attrs = [
    'name: str',
    'available_minutes: int',
    'pets: List[Pet]',
]
owner_methods = [
    'add_pet(pet) : void',
    'remove_pet(name) : void',
    'set_availability(minutes) : void',
    'get_pet_tasks() : List[Tuple[Pet, PetTask]]',
]
gap = 0.9
owner_top = sched_bottom - gap
owner_h = draw_uml_class(ax, LX, owner_top, W, 'Owner', owner_attrs, owner_methods)
owner_bottom = owner_top - owner_h

# ── Pet ─────────────────────────────────────────────────────────────────
pet_attrs = [
    'name: str',
    'species: str',
    'age: int',
    'tasks: List[PetTask]',
]
pet_methods = [
    'add_task(task: PetTask) : void',
    'remove_task(title: str) : void',
    'get_pending_tasks() : List[PetTask]',
    'get_completed_tasks() : List[PetTask]',
]
pet_top = owner_bottom - gap
pet_h = draw_uml_class(ax, LX, pet_top, W, 'Pet', pet_attrs, pet_methods)
pet_bottom = pet_top - pet_h

# ── PetTask ─────────────────────────────────────────────────────────────
task_attrs = [
    'title: str',
    'duration_minutes: int',
    'priority: str',
    'description: str',
    'frequency: str',
    'preferred_time: Optional[str]',
    'start_time: Optional[str]',
    'completed: bool',
    'last_completed_date: Optional[date]',
]
task_methods = [
    'is_high_priority() : bool',
    'priority_score() : int',
    'time_slot() : int',
    'mark_complete() : void',
    'reset() : void',
    'next_occurrence() : PetTask',
]
task_top = pet_bottom - gap
draw_uml_class(ax, LX, task_top, W, 'PetTask', task_attrs, task_methods)

# ── Arrows ──────────────────────────────────────────────────────────────
draw_arrow(ax, CX, sched_bottom, CX, owner_top, '1 uses 1')
draw_arrow(ax, CX, owner_bottom, CX, pet_top, '1 has many')
draw_arrow(ax, CX, pet_bottom, CX, task_top, '1 has many')

out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uml_final.png')
plt.tight_layout()
plt.savefig(out_path, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
plt.close()
print(f"Saved: {out_path}")
