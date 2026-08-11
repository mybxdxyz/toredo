from dataclasses import dataclass
from datetime import time


@dataclass
class Task:
    desc: str
    reminder: time | None