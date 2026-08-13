from dataclasses import dataclass
from datetime import datetime

PRIORITY_ORDER = ["none", "low", "medium", "high"]


@dataclass
class Task:
    desc: str
    due: datetime | None = None
    status: bool = False
    notified: bool = False
    priority: str = "none"

    def toggle_completed(self) -> None:
        self.status = not self.status
        if self.status:
            # a finished task should never fire a reminder afterwards
            self.notified = True

    def is_overdue(self, now: datetime | None = None) -> bool:
        if self.due is None or self.status:
            return False
        now = now or datetime.now()
        return now >= self.due

    def cycle_priority(self) -> None:
        idx = PRIORITY_ORDER.index(self.priority) if self.priority in PRIORITY_ORDER else 0
        self.priority = PRIORITY_ORDER[(idx + 1) % len(PRIORITY_ORDER)]