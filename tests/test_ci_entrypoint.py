"""Check the restricted test entry point without starting containers."""

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class CiEntrypointTests(unittest.TestCase):
    def run_script(self, *arguments, status=0):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copy2(ROOT / "runtests", root / "runtests")
            (root / "tests").mkdir()
            (root / "tests" / "runtests.py").write_text(
                "import unittest\n"
                "class TestExample(unittest.TestCase):\n"
                "    def test_example(self): pass\n"
                "class TestHelper:\n"
                "    def test_action(self): pass\n"
            )
            fake = root / "make"
            fake.write_text('#!/bin/sh\nprintf "%s\\n" "$@"\nexit "$STATUS"\n')
            fake.chmod(0o755)
            return subprocess.run(
                [str(root / "runtests"), *arguments],
                cwd=root,
                env={
                    **os.environ,
                    "PATH": f"{root}:{os.environ['PATH']}",
                    "STATUS": str(status),
                },
                capture_output=True,
                text=True,
            )

    def test_default_and_focused_labels(self):
        result = self.run_script("TestExample.test_example", "-q")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            result.stdout.splitlines(),
            ["develop-pythontests", "TEST_LABELS=TestExample.test_example -q"],
        )

    def test_rejects_unsafe_arguments_and_non_test_classes(self):
        for argument in (
            "--locals",
            "TestExample.setUpClass",
            "TestHelper.test_action",
            "../test.py",
        ):
            with self.subTest(argument=argument):
                result = self.run_script(argument)
                self.assertEqual(result.returncode, 2)
                self.assertIn("unsupported", result.stderr.lower())
                self.assertEqual(result.stdout, "")

    def test_returns_runner_status(self):
        self.assertEqual(self.run_script(status=17).returncode, 17)
