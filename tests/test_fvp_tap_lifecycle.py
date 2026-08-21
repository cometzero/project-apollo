from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.setup.fvp_tap_lifecycle import ManagedChild  # noqa: E402


def _stand_in() -> list[str]:
    return [sys.executable, "-c", "import time; time.sleep(30)"]


@pytest.mark.parametrize("fail_after", ["spawn", "provisional"])
def test_failure_after_spawn_reaps_child_and_removes_task_files(
    tmp_path: Path,
    fail_after: str,
) -> None:
    # Given: a safe stand-in child and named task-owned state files.
    child = ManagedChild(
        _stand_in(),
        tmp_path / "pid",
        tmp_path / "lease",
        tmp_path / "state",
    )

    # When: setup fails immediately after spawn or provisional publication.
    with pytest.raises(RuntimeError, match=fail_after):
        child.run(
            lambda identity: f"PID={identity.pid}\n",
            lambda stage: (_ for _ in ()).throw(RuntimeError(stage))
            if stage == fail_after
            else None,
        )

    # Then: the exact Popen child is reaped and every task file is removed.
    assert child.process is not None
    assert child.process.poll() is not None
    assert not (tmp_path / "pid").exists()
    assert not (tmp_path / "lease").exists()
    assert not (tmp_path / "state").exists()


def test_cleanup_does_not_signal_foreign_process(tmp_path: Path) -> None:
    # Given: an unrelated safe stand-in process beside a failing setup child.
    foreign = subprocess.Popen(_stand_in())
    child = ManagedChild(_stand_in(), tmp_path / "pid", tmp_path / "lease", tmp_path / "state")

    # When: provisional state publication raises after the owned child starts.
    with pytest.raises(RuntimeError, match="provisional"):
        child.run(
            lambda _identity: (_ for _ in ()).throw(RuntimeError("provisional")),
            lambda _stage: None,
        )

    # Then: cleanup reaps only the owned handle and leaves the foreign child alive.
    assert child.process is not None and child.process.poll() is not None
    assert foreign.poll() is None
    foreign.terminate()
    assert foreign.wait(timeout=5) == 0 - 15


def test_ready_child_remains_owned_until_explicit_cleanup(tmp_path: Path) -> None:
    # Given: a successful safe stand-in setup with an atomic provisional state.
    child = ManagedChild(
        _stand_in(),
        tmp_path / "pid",
        tmp_path / "lease",
        tmp_path / "state",
    )

    # When: setup completes without an injected lifecycle failure.
    identity = child.run(lambda value: f"PID={value.pid}\n", lambda _stage: None)

    # Then: readiness retains the owned child until explicit deterministic cleanup.
    assert child.process is not None and child.process.poll() is None
    assert (tmp_path / "state").read_text(encoding="utf-8") == f"PID={identity.pid}\n"
    child.cleanup()
    assert child.process.poll() is not None
    assert not any((tmp_path / name).exists() for name in ("pid", "lease", "state"))
