"""Разбор команд и консольный интерфейс."""

import shlex
from datetime import date

from study_agent.tasks import Task, TaskBook

HELP = """Команды:
  add "Предмет" "Описание" ГГГГ-ММ-ДД — добавить задание
  list — показать все задания со статусами по сроку сдачи
  due ГГГГ-ММ-ДД — показать невыполненные задания до даты включительно
  done НОМЕР — отметить задание выполненным
  help — показать справку
  exit — завершить работу
Аргументы с пробелами заключайте в прямые двойные кавычки.
Данные хранятся только в памяти и теряются после выхода."""


def parse_date(value: str) -> date:
    if len(value) != 10 or value[4] != "-" or value[7] != "-":
        raise ValueError("Дата должна иметь вид ГГГГ-ММ-ДД.")
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise ValueError("Укажите существующую дату в виде ГГГГ-ММ-ДД.") from None


def show_tasks(tasks: list[Task]) -> None:
    if not tasks:
        print("Заданий нет.")
    for task in tasks:
        status = "выполнено" if task.completed else "не выполнено"
        print(
            f"{task.number} | {task.subject} | {task.title} | "
            f"{task.deadline.isoformat()} | {status}"
        )


def execute(line: str, book: TaskBook) -> bool:
    """Выполнить команду; вернуть False, если запрошен выход."""
    words = shlex.split(line)
    if not words:
        return True
    command, *args = words
    if command == "add" and len(args) == 3:
        task = book.add(args[0], args[1], parse_date(args[2]))
        print(f"Добавлено задание № {task.number}.")
    elif command == "list" and not args:
        show_tasks(book.list_tasks())
    elif command == "due" and len(args) == 1:
        show_tasks(book.list_tasks(until=parse_date(args[0])))
    elif command == "done" and len(args) == 1:
        try:
            number = int(args[0])
        except ValueError:
            raise ValueError(
                "Номер задания должен быть целым положительным числом."
            ) from None
        if number <= 0:
            raise ValueError("Номер задания должен быть целым положительным числом.")
        task = book.complete(number)
        print(f"Задание № {task.number} выполнено.")
    elif command == "help" and not args:
        print(HELP)
    elif command == "exit" and not args:
        return False
    elif command in {"add", "list", "due", "done", "help", "exit"}:
        raise ValueError("Неверное количество аргументов. Введите help.")
    else:
        raise ValueError("Неизвестная команда. Введите help.")
    return True


def main() -> None:
    book = TaskBook()
    print("Учебный помощник. Введите help для справки.")
    while True:
        try:
            line = input("> ")
            if not execute(line, book):
                break
        except ValueError as error:
            print(f"Ошибка: {error}")
        except EOFError, KeyboardInterrupt:
            print()
            break
    print("До свидания!")
