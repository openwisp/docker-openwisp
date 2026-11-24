"""Check dependency phases without installing host tools."""

import os
import shutil
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

    def test_ci_creates_and_publishes_the_virtualenv(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            fake = path / "python"
            shutil.copy2(ROOT / "tests" / "scripts" / "ci_fake_python.sh", fake)
            fake.chmod(0o755)
            log = path / "calls"
            github_path = path / "github-path"
            env = {
                **os.environ,
                "PATH": f"{path}:{os.environ['PATH']}",
                "CALLS": str(log),
                "GITHUB_PATH": str(github_path),
                "RUNNER_TEMP": str(path),
                "CI_SYSTEM_DEPS_READY": "1",
                "CI_SYSTEM_DEPS_ONLY": "0",
            }
            result = subprocess.run(
                [str(ROOT / "install-ci-deps.sh")],
                cwd=ROOT,
                env=env,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                log.read_text().splitlines(),
                [
                    f"{fake}: -m venv {path / 'openwisp-venv'}",
                    f"{path / 'openwisp-venv' / 'bin' / 'python'}: "
                    "-m pip install -r requirements-test.txt",
                ],
            )
            self.assertEqual(
                github_path.read_text().strip(), str(path / "openwisp-venv" / "bin")
            )
