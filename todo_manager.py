"""
To-Do List Manager
CloudExify Python Internship — Month 2, Project 4 (Final Project)

A JSON-backed CLI task manager. Implements all core features plus the
bonus challenges: overdue tasks, edit task, keyword search, tasks due
today, and task categories.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict, field
from datetime import datetime, date
from typing import Optional

FILE = "tasks.json"
PRIORITIES = ("High", "Medium", "Low")
PRIORITY_ORDER = {p: i for i, p in enumerate(PRIORITIES)}
CATEGORIES = ("Work", "Study", "Personal", "Other")


# --------------------------------------------------------------------------
# Terminal colors (ANSI escape codes — no extra library needed)
# --------------------------------------------------------------------------

class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[97m"
    BG_BLUE = "\033[44m"


PRIORITY_COLOR = {"High": C.RED, "Medium": C.YELLOW, "Low": C.GREEN}
CATEGORY_COLOR = {"Work": C.BLUE, "Study": C.MAGENTA, "Personal": C.CYAN, "Other": C.DIM}


def colorize(text: str, color: str) -> str:
    return f"{color}{text}{C.RESET}"


# Enable ANSI colors on Windows terminals too
if os.name == "nt":
    os.system("")


# --------------------------------------------------------------------------
# Data model
# --------------------------------------------------------------------------

@dataclass
class Task:
    id: int
    title: str
    priority: str = "Medium"
    due_date: str = "No due date"        # "YYYY-MM-DD" or "No due date"
    status: str = "Pending"              # "Pending" | "Done"
    category: str = "Other"
    created: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))

    @property
    def is_overdue(self) -> bool:
        if self.status == "Done" or self.due_date == "No due date":
            return False
        try:
            return datetime.strptime(self.due_date, "%Y-%m-%d").date() < date.today()
        except ValueError:
            return False

    @property
    def is_due_today(self) -> bool:
        if self.due_date == "No due date":
            return False
        try:
            return datetime.strptime(self.due_date, "%Y-%m-%d").date() == date.today()
        except ValueError:
            return False


# --------------------------------------------------------------------------
# Persistence + in-memory manager
# --------------------------------------------------------------------------

class TaskManager:
    """Owns the task list and all persistence/business logic."""

    def __init__(self, filepath: str = FILE):
        self.filepath = filepath
        self.tasks: list[Task] = self._load()
        self._next_id = (max((t.id for t in self.tasks), default=0)) + 1

    # ---- persistence -----------------------------------------------------
    def _load(self) -> list[Task]:
        if not os.path.exists(self.filepath):
            return []
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                raw = json.load(f)
            return [Task(**item) for item in raw]
        except (json.JSONDecodeError, TypeError, OSError) as e:
            print(f"⚠️  Could not read {self.filepath} ({e}). Starting with an empty list.")
            return []

    def save(self) -> None:
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump([asdict(t) for t in self.tasks], f, indent=4)

    # ---- CRUD --------------------------------------------------------------
    def add(self, title: str, priority: str, due_date: str, category: str) -> Task:
        task = Task(
            id=self._next_id,
            title=title,
            priority=priority,
            due_date=due_date or "No due date",
            category=category,
        )
        self.tasks.append(task)
        self._next_id += 1
        self.save()
        return task

    def find(self, task_id: int) -> Optional[Task]:
        return next((t for t in self.tasks if t.id == task_id), None)

    def mark_done(self, task_id: int) -> tuple[bool, str]:
        task = self.find(task_id)
        if task is None:
            return False, f"No task found with ID {task_id}."
        if task.status == "Done":
            return False, "Task is already done!"
        task.status = "Done"
        self.save()
        return True, f"Task '{task.title}' marked as done!"

    def delete(self, task_id: int) -> Optional[Task]:
        task = self.find(task_id)
        if task is None:
            return None
        self.tasks.remove(task)
        self.save()
        return task

    def edit(self, task_id: int, *, title=None, priority=None, due_date=None, category=None) -> bool:
        task = self.find(task_id)
        if task is None:
            return False
        if title:
            task.title = title
        if priority:
            task.priority = priority
        if due_date:
            task.due_date = due_date
        if category:
            task.category = category
        self.save()
        return True

    # ---- queries -----------------------------------------------------------
    def filtered(self, status=None, priority=None, category=None,
                 overdue=False, due_today=False, keyword=None) -> list[Task]:
        result = self.tasks
        if status:
            result = [t for t in result if t.status == status]
        if priority:
            result = [t for t in result if t.priority == priority]
        if category:
            result = [t for t in result if t.category == category]
        if overdue:
            result = [t for t in result if t.is_overdue]
        if due_today:
            result = [t for t in result if t.is_due_today]
        if keyword:
            k = keyword.lower()
            result = [t for t in result if k in t.title.lower()]
        return sorted(result, key=lambda t: PRIORITY_ORDER.get(t.priority, 99))

    def stats(self) -> dict:
        total = len(self.tasks)
        done = sum(1 for t in self.tasks if t.status == "Done")
        pending = total - done
        high_pending = sum(1 for t in self.tasks if t.priority == "High" and t.status == "Pending")
        overdue = sum(1 for t in self.tasks if t.is_overdue)
        pct = (done / total * 100) if total else 0.0
        return {
            "total": total, "done": done, "pending": pending,
            "high_pending": high_pending, "overdue": overdue, "pct": pct,
        }


# --------------------------------------------------------------------------
# Presentation / CLI layer
# --------------------------------------------------------------------------

def print_table(tasks: list[Task]) -> None:
    if not tasks:
        print(colorize("\nNo tasks found!", C.YELLOW))
        return
    header = f"{'ID':<5}{'Title':<26}{'Priority':<10}{'Category':<10}{'Status':<8}{'Due Date':<12}"
    print(colorize(f"\n{header}", C.BOLD + C.WHITE))
    print(colorize("-" * 75, C.DIM))
    def pad_colored(text: str, color: str, width: int) -> str:
        """Pad first (plain text), then color — so ANSI codes don't break alignment."""
        return colorize(text.ljust(width), color)

    for t in tasks:
        title = (t.title[:23] + "...") if len(t.title) > 25 else t.title
        p_color = PRIORITY_COLOR.get(t.priority, C.RESET)
        c_color = CATEGORY_COLOR.get(t.category, C.RESET)

        if t.status == "Done":
            mark_text, mark_color = "DONE", C.GREEN + C.BOLD
        elif t.is_overdue:
            mark_text, mark_color = "LATE", C.RED + C.BOLD
        else:
            mark_text, mark_color = "...", C.DIM

        row = (
            f"{str(t.id).ljust(5)}"
            f"{title.ljust(26)}"
            f"{pad_colored(t.priority, p_color, 10)}"
            f"{pad_colored(t.category, c_color, 10)}"
            f"{pad_colored(mark_text, mark_color, 8)}"
            f"{t.due_date.ljust(12)}"
        )
        print(row)


def prompt_choice(label: str, options: tuple[str, ...]) -> str:
    print(label)
    for i, opt in enumerate(options, 1):
        print(f"  {i}) {opt}")
    while True:
        choice = input(f"Select (1-{len(options)}): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return options[int(choice) - 1]
        print(f"Enter a number between 1 and {len(options)}!")


def prompt_valid_date(label: str) -> str:
    while True:
        raw = input(label).strip()
        if not raw:
            return "No due date"
        try:
            datetime.strptime(raw, "%Y-%m-%d")
            return raw
        except ValueError:
            print("Invalid format — use YYYY-MM-DD (or leave blank to skip).")


def prompt_int(label: str) -> Optional[int]:
    raw = input(label).strip()
    if not raw.isdigit():
        print("Please enter a valid number!")
        return None
    return int(raw)


def action_add(mgr: TaskManager) -> None:
    print("\n--- ADD NEW TASK ---")
    title = input("Task title: ").strip()
    if not title:
        print("Title cannot be empty!")
        return
    priority = prompt_choice("Priority:", PRIORITIES)
    category = prompt_choice("Category:", CATEGORIES)
    due_date = prompt_valid_date("Due date (YYYY-MM-DD) or leave blank: ")
    task = mgr.add(title, priority, due_date, category)
    print(colorize(f"✅ Task added! ID: {task.id}", C.GREEN + C.BOLD))


def action_mark_done(mgr: TaskManager) -> None:
    print_table(mgr.filtered(status="Pending"))
    task_id = prompt_int("\nEnter task ID to mark done: ")
    if task_id is None:
        return
    ok, msg = mgr.mark_done(task_id)
    color = C.GREEN + C.BOLD if ok else C.YELLOW
    print(colorize(("✅ " if ok else "⚠️  ") + msg, color))


def action_delete(mgr: TaskManager) -> None:
    print_table(mgr.tasks)
    task_id = prompt_int("\nEnter task ID to delete: ")
    if task_id is None:
        return
    task = mgr.find(task_id)
    if task is None:
        print(f"No task found with ID {task_id}")
        return
    confirm = input(f"Delete '{task.title}'? (yes/no): ").strip().lower()
    if confirm in ("yes", "y"):
        mgr.delete(task_id)
        print(colorize("🗑️  Task deleted!", C.RED))
    else:
        print(colorize("Cancelled — task kept.", C.DIM))


def action_edit(mgr: TaskManager) -> None:
    print_table(mgr.tasks)
    task_id = prompt_int("\nEnter task ID to edit: ")
    if task_id is None:
        return
    task = mgr.find(task_id)
    if task is None:
        print(f"No task found with ID {task_id}")
        return
    print("Leave a field blank to keep it unchanged.")
    new_title = input(f"New title [{task.title}]: ").strip()
    new_priority = input(f"New priority (High/Medium/Low) [{task.priority}]: ").strip().title()
    new_priority = new_priority if new_priority in PRIORITIES else None
    new_due = input(f"New due date (YYYY-MM-DD) [{task.due_date}]: ").strip()
    mgr.edit(task_id, title=new_title or None, priority=new_priority, due_date=new_due or None)
    print(colorize("✏️  Task updated!", C.CYAN + C.BOLD))


def action_search(mgr: TaskManager) -> None:
    keyword = input("\nSearch keyword: ").strip()
    if not keyword:
        print("Please enter a keyword.")
        return
    print_table(mgr.filtered(keyword=keyword))


def action_stats(mgr: TaskManager) -> None:
    s = mgr.stats()
    print(colorize("\n=== TASK STATISTICS ===", C.BOLD + C.WHITE))
    print(f"Total Tasks     : {colorize(str(s['total']), C.CYAN)}")
    print(f"Completed       : {colorize(str(s['done']), C.GREEN)}")
    print(f"Pending         : {colorize(str(s['pending']), C.YELLOW)}")
    print(f"High Priority   : {colorize(str(s['high_pending']) + ' pending', C.RED)}")
    print(f"Overdue         : {colorize(str(s['overdue']), C.RED + C.BOLD)}")
    pct_text = f"{s['pct']:.0f}%"
    print(f"Completion      : {colorize(pct_text, C.GREEN + C.BOLD)}")


MENU = f"""
{C.BOLD}{C.CYAN}=== TO-DO LIST MANAGER ==={C.RESET}
 1. Add task
 2. View all tasks
 3. View pending tasks
 4. View {colorize('high priority', C.RED)}
 5. View {colorize('overdue', C.RED + C.BOLD)} tasks
 6. View tasks due today
 7. Search tasks
 8. Mark task as {colorize('done', C.GREEN)}
 9. Edit task
10. {colorize('Delete task', C.RED)}
11. Show statistics
12. Exit
"""

ACTIONS = {
    "1": lambda m: action_add(m),
    "2": lambda m: print_table(m.filtered()),
    "3": lambda m: print_table(m.filtered(status="Pending")),
    "4": lambda m: print_table(m.filtered(priority="High")),
    "5": lambda m: print_table(m.filtered(overdue=True)),
    "6": lambda m: print_table(m.filtered(due_today=True)),
    "7": lambda m: action_search(m),
    "8": lambda m: action_mark_done(m),
    "9": lambda m: action_edit(m),
    "10": lambda m: action_delete(m),
    "11": lambda m: action_stats(m),
}


def main() -> None:
    mgr = TaskManager()
    print(colorize(f"Loaded {len(mgr.tasks)} task(s) from '{mgr.filepath}'.", C.DIM))

    while True:
        print(MENU)
        choice = input(colorize("Choose (1-12): ", C.BOLD)).strip()
        if choice == "12":
            print(colorize("Goodbye! 👋", C.CYAN + C.BOLD))
            break
        action = ACTIONS.get(choice)
        if action:
            action(mgr)
        else:
            print(colorize("Invalid choice!", C.RED))


if __name__ == "__main__":
    main()