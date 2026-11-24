"""Check dependency phases without installing host tools."""

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class CiInstallerTests(unittest.TestCase):
    def run_installer(self, **variables):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            log = path / "calls"
            for name in ("sudo", "python"):
                fake = path / name
                fake.write_text(f'#!/bin/sh\nprintf "%s\\n" "{name} $*" >> "$CALLS"\n')
                fake.chmod(0o755)
            env = os.environ.copy()
            for key in ("CI_SYSTEM_DEPS_ONLY", "CI_SYSTEM_DEPS_READY", "GITHUB_PATH"):
                env.pop(key, None)
            env.update(PATH=f"{path}:{env['PATH']}", CALLS=str(log), **variables)
            result = subprocess.run(
                [str(ROOT / "install-ci-deps.sh")],
                cwd=ROOT,
                env=env,
                capture_output=True,
                text=True,
            )
            return result, log.read_text().splitlines()

    def test_system_phase_excludes_python_installation(self):
        result, calls = self.run_installer(CI_SYSTEM_DEPS_ONLY="1")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(all(call.startswith("sudo ") for call in calls))
        self.assertIn("sudo apt-get install -y python3-venv", calls)

    def test_reviewer_installs_only_python_dependencies(self):
        result, calls = self.run_installer(CI_SYSTEM_DEPS_READY="1")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(calls, ["python -m pip install -r requirements-test.txt"])
