"""Чтение и запись учебных заданий в JSON."""

import json
from datetime import date
from pathlib import Path
from tempfile import NamedTemporaryFile

from study_agent.tasks import Task

DEFAULT_PATH = Path("data/tasks.json")


def load_tasks(path: Path) -> list[Task]:
    try:
        raw = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return []
    rows = json.loads(raw)
    if not isinstance(rows, list):
        raise ValueError("Ожидался список заданий.")
    tasks = []
    for number, row in enumerate(rows, 1):
        if (
            not isinstance(row, dict)
            or type(row.get("number")) is not int
            or row["number"] != number
            or not isinstance(row.get("subject"), str)
            or not row["subject"].strip()
            or not isinstance(row.get("title"), str)
            or not row["title"].strip()
            or not isinstance(row.get("deadline"), str)
            or type(row.get("completed")) is not bool
        ):
            raise ValueError("Некорректная запись задания.")
        tasks.append(
            Task(
                number,
                row["subject"],
                row["title"],
                date.fromisoformat(row["deadline"]),
                row["completed"],
            )
        )
    return tasks


def save_tasks(path: Path, tasks: list[Task]) -> None:
    rows = [
        {
            "number": t.number,
            "subject": t.subject,
            "title": t.title,
            "deadline": t.deadline.isoformat(),
            "completed": t.completed,
        }
        for t in sorted(tasks, key=lambda t: t.number)
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent, delete=False
        ) as stream:
            temporary = Path(stream.name)
            json.dump(rows, stream, ensure_ascii=False, indent=2)
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
