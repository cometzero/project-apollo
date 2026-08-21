from __future__ import annotations

from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts/setup"))

from scripts.setup import fvp_tap_admin  # noqa: E402


def test_validator_uses_python_for_non_executable_script(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Given: the repository validator's normal data-file permissions and no
    # shebang, with an argument-sensitive success result.
    validator = tmp_path / "validator.py"
    validator.write_text(
        "import sys\n"
        "expected = ['--verify', '--owner-uid', '1000']\n"
        "raise SystemExit(0 if sys.argv[1:] == expected else 9)\n",
        encoding="utf-8",
    )
    validator.chmod(0o644)
    monkeypatch.setattr(fvp_tap_admin, "VALIDATOR", validator)

    # When/Then: the admin helper launches it through the active interpreter
    # instead of asking the kernel to execute a non-executable Python file.
    assert fvp_tap_admin._validator(1000, "--verify")
