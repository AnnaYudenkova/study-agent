"""Модель задания и операции с данными в памяти."""

from dataclasses import dataclass
from datetime import date


@dataclass
class Task:
    number: int
    subject: str
    title: str
    deadline: date
    completed: bool = False


class TaskBook:
    def __init__(self) -> None:
        self._tasks: list[Task] = []

    def add(self, subject: str, title: str, deadline: date) -> Task:
        subject, title = subject.strip(), title.strip()
        if not subject or not title:
            raise ValueError("Предмет и описание не должны быть пустыми.")
        task = Task(len(self._tasks) + 1, subject, title, deadline)
        self._tasks.append(task)
        return task

    def list_tasks(self, until: date | None = None) -> list[Task]:
        tasks = self._tasks
        if until is not None:
            tasks = [t for t in tasks if not t.completed and t.deadline <= until]
        return sorted(tasks, key=lambda t: (t.deadline, t.number))

    def complete(self, number: int) -> Task:
        for task in self._tasks:
            if task.number == number:
                if task.completed:
                    raise ValueError("Задание уже выполнено.")
                task.completed = True
                return task
        raise ValueError(f"Задание № {number} не найдено.")
