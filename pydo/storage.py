import json
from datetime import datetime

from model import Task


def task_to_dict(task: Task) -> dict:
    return {
        "desc": task.desc,
        "due": task.due.isoformat() if task.due else None,
        "status": task.status,
        "notified": task.notified,
    }


def dict_to_task(data: dict) -> Task:
    due = datetime.fromisoformat(data["due"]) if data.get("due") else None
    return Task(
        desc=data["desc"],
        due=due,
        status=data.get("status", False),
        notified=data.get("notified", False),
    )


def load_tasks(filename: str) -> list[Task]:
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        # skip corrupt/empty leftover rows from older versions
        return [dict_to_task(item) for item in data if item.get("desc", "").strip()]
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_tasks(tasks: list[Task], filename: str) -> None:
    with open(filename, "w", encoding="utf-8") as f:
        json.dump([task_to_dict(task) for task in tasks], f, indent=4, ensure_ascii=False)


def load_settings(filename: str) -> dict:
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_settings(settings: dict, filename: str) -> None:
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4, ensure_ascii=False)