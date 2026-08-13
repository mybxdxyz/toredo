import threading
from datetime import datetime
from typing import Callable

from model import Task

try:
    from plyer import notification
    NOTIFICATIONS_AVAILABLE = True
except Exception:
    NOTIFICATIONS_AVAILABLE = False


def check_reminders(tasks: list[Task], on_fire: Callable[[Task], None]) -> None:
    now = datetime.now()
    for task in tasks:
        if task.due and not task.status and not task.notified and now >= task.due:
            if NOTIFICATIONS_AVAILABLE:
                try:
                    notification.notify(
                        title="Нагадування",
                        message=f"Не забудьте: {task.desc}!",
                        timeout=10,
                    )
                except Exception:
                    pass
            task.notified = True
            on_fire(task)


class ReminderLoop:
    """Repeatedly checks for due tasks in the background while the app is open."""

    def __init__(self, tasks: list[Task], on_fire: Callable[[Task], None], interval: float = 20.0):
        self.tasks = tasks
        self.on_fire = on_fire
        self.interval = interval
        self._timer: threading.Timer | None = None
        self._running = False

    def _tick(self) -> None:
        if not self._running:
            return
        check_reminders(self.tasks, self.on_fire)
        self._timer = threading.Timer(self.interval, self._tick)
        self._timer.daemon = True
        self._timer.start()

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._tick()

    def stop(self) -> None:
        self._running = False
        if self._timer:
            self._timer.cancel()
