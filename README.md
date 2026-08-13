# To-Do List Manager

A simple command-line to-do list app built in Python. This was my final project for Month 2 of the CloudExify Python Internship.

The app lets you add tasks, set priorities and due dates, mark things done, and see stats about your progress. Everything gets saved to a `tasks.json` file, so your list is still there the next time you open it.

## Author

- Name: Muhammad Tayyab
- Registration Number: CX-INT-2026-PY-0139

## Features

- Add a task with a title, priority (High/Medium/Low), category, and due date
- View all tasks, sorted so the important ones show up first
- View only pending tasks, or only high priority ones
- Mark a task as done
- Delete a task (it asks you to confirm first)
- Edit a task if you got something wrong
- Search tasks by keyword
- See which tasks are overdue, and which are due today
- Basic stats — how many tasks total, how many done, completion percentage
- Color-coded output in the terminal so it's easier to read at a glance

## How to run it

You just need Python 3.9+, nothing else to install.

```bash
python3 todo_manager.py
```

The first time you add a task, it creates a `tasks.json` file next to the script. After that, every time you run the app it loads your saved tasks automatically.

## Using the app

When you run it, you get a menu like this:

```
=== TO-DO LIST MANAGER ===
 1. Add task
 2. View all tasks
 3. View pending tasks
 4. View high priority
 5. View overdue tasks
 6. View tasks due today
 7. Search tasks
 8. Mark task as done
 9. Edit task
10. Delete task
11. Show statistics
12. Exit
```

Just type the number for whatever you want to do and follow the prompts.

## What a task looks like (stored in tasks.json)

```json
{
    "id": 1,
    "title": "Complete Python project",
    "priority": "High",
    "due_date": "2026-08-15",
    "status": "Pending",
    "category": "Study",
    "created": "2026-08-13 10:30"
}
```


## Project files

```
.
├── todo_manager.py   # the app
├── tasks.json        # created automatically once you add a task
└── README.md
```

