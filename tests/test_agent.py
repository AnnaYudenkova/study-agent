import io
import json
import os
import runpy
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch


class AgentTest(unittest.TestCase):
    def setUp(self):
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.addCleanup(os.chdir, Path.cwd())
        os.chdir(directory.name)
        self.path = Path("data/tasks.json")

    def run_agent(self, *commands, expected_code=0):
        output = io.StringIO()
        with (
            patch("builtins.input", side_effect=commands),
            redirect_stdout(output),
            self.assertRaises(SystemExit) as result,
        ):
            runpy.run_module("study_agent", run_name="__main__")
        self.assertEqual(result.exception.code, expected_code)
        return output.getvalue()

    def test_records_and_status_survive_restart(self):
        output = self.run_agent(
            "list",
            'add "Физика" "Отчёт" 2026-11-25',
            'add "Математика" "Задачи" 2026-11-24',
            "exit",
        )
        self.assertIn("Заданий нет.", output)
        original = json.loads(self.path.read_text(encoding="utf-8"))
        output = self.run_agent("list", "done 1", "due 2026-11-24", "exit")
        self.assertIn("1 | Физика | Отчёт | 2026-11-25 | не выполнено", output)
        self.assertIn("Задание № 1 выполнено.", output)
        output = self.run_agent("list", "exit")
        self.assertIn("1 | Физика | Отчёт | 2026-11-25 | выполнено", output)
        self.assertIn("2 | Математика | Задачи | 2026-11-24 | не выполнено", output)
        saved = json.loads(self.path.read_text(encoding="utf-8"))
        self.assertEqual(saved, [dict(original[0], completed=True), original[1]])

    def test_bad_commands_leave_state_unchanged(self):
        output = self.run_agent(
            "help",
            "",
            "unknown",
            "add",
            'add "Физика" "Отчёт" 2026-02-30',
            'add "Физика" "Отчёт" 30.02.2026',
            'add "" "Отчёт" 2026-11-25',
            'add "Физика',
            "done abc",
            "done 0",
            "done 1",
            "list",
            EOFError,
        )
        self.assertIn("Команды:", output)
        self.assertEqual(output.count("Ошибка:"), 9)
        self.assertIn("Заданий нет.", output)
        self.assertEqual(self.path.read_text(encoding="utf-8"), "[]")

    def test_damaged_storage_is_not_overwritten(self):
        self.path.parent.mkdir()
        for contents in ("{", "{}", "[{}]"):
            with self.subTest(contents=contents):
                self.path.write_text(contents, encoding="utf-8")
                output = self.run_agent(expected_code=1)
                self.assertIn("Не удалось загрузить", output)
                self.assertEqual(self.path.read_text(encoding="utf-8"), contents)

    def test_save_error_is_reported(self):
        with patch("pathlib.Path.replace", side_effect=PermissionError("запрещено")):
            output = self.run_agent("exit", expected_code=1)
        self.assertIn("Не удалось сохранить", output)
        self.assertEqual(list(self.path.parent.iterdir()), [])
