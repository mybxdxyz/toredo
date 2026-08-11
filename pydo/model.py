from dataclasses import dataclass
from datetime import datetime


@dataclass
class Task:
    desc: str
    due: datetime | None = None
    status: bool = False
    notified: bool = False

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
