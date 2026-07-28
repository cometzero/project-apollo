from __future__ import annotations

import os
from pathlib import Path
import subprocess
from textwrap import dedent
from typing import Final


ROOT: Final = Path(__file__).resolve().parents[1]


def run_scheduler(script: str, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ("timeout", "5", "bash", "-c", script),
        cwd=ROOT,
        check=False,
        env=os.environ | env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def test_scheduler_runs_ready_components_with_bounded_job_leases(
    tmp_path: Path,
) -> None:
    # Given: two independent roots, one dependent node, and four total jobs.
    start_fifo = tmp_path / "started"
    release_fifo = tmp_path / "release"
    os.mkfifo(start_fifo)
    os.mkfifo(release_fifo)
    event_log = tmp_path / "events.tsv"
    script = dedent(
        """\
        set -euo pipefail
        APOLLO_LOCAL_BUILD_COMMON_SOURCED=1
        source scripts/build/modules/build_scheduler.sh
        run_step() {
            shift
            "$@"
        }
        run_component() {
            local component="$1"
            if [[ "${component}" == qbox || "${component}" == tf-m ]]; then
                printf '%s\\n' "${component}" > "${START_FIFO}"
                read -r _ < "${RELEASE_FIFO}"
            fi
            printf '%s\\t%s\\n' "${component}" "${JOBS}" >> "${EVENT_LOG}"
        }
        (
            read -r _ < "${START_FIFO}"
            read -r _ < "${START_FIFO}"
            printf 'go\\ngo\\n' > "${RELEASE_FIFO}"
        ) &
        coordinator=$!
        JOBS=4
        APOLLO_LOCAL_BUILD_COMPONENT_LANES=2
        run_component_dag build qbox tf-m tf-a
        wait "${coordinator}"
        """
    )

    # When: the scheduler executes the selected DAG.
    result = run_scheduler(
        script,
        {
            "EVENT_LOG": str(event_log),
            "RELEASE_FIFO": str(release_fifo),
            "START_FIFO": str(start_fifo),
        },
    )

    # Then: roots overlap within four jobs and TF-A gets the full later-stage budget.
    assert result.returncode == 0, f"{result.stdout}\n{result.stderr}"
    events = [
        tuple(line.split("\t"))
        for line in event_log.read_text(encoding="utf-8").splitlines()
    ]
    assert set(events[:2]) == {("qbox", "2"), ("tf-m", "2")}
    assert events[2] == ("tf-a", "4")


def test_scheduler_stops_before_downstream_stage_after_failure(
    tmp_path: Path,
) -> None:
    # Given: one failing root and a dependent downstream component.
    event_log = tmp_path / "events.txt"
    script = dedent(
        """\
        set -euo pipefail
        APOLLO_LOCAL_BUILD_COMMON_SOURCED=1
        source scripts/build/modules/build_scheduler.sh
        run_step() {
            shift
            "$@"
        }
        run_component() {
            printf '%s\\n' "$1" >> "${EVENT_LOG}"
            [[ "$1" != qbox ]]
        }
        JOBS=2
        APOLLO_LOCAL_BUILD_COMPONENT_LANES=2
        run_component_dag build qbox tf-m tf-a
        """
    )

    # When: the first stage reports a component failure.
    result = run_scheduler(script, {"EVENT_LOG": str(event_log)})

    # Then: the stage fails and its downstream node is never started.
    assert result.returncode != 0
    events = event_log.read_text(encoding="utf-8").splitlines()
    assert set(events) == {"qbox", "tf-m"}
    assert "tf-a" not in events


def test_scheduler_keeps_non_build_actions_serial(tmp_path: Path) -> None:
    # Given: an ordered clean action across otherwise independent components.
    event_log = tmp_path / "events.txt"
    script = dedent(
        """\
        set -euo pipefail
        APOLLO_LOCAL_BUILD_COMMON_SOURCED=1
        source scripts/build/modules/build_scheduler.sh
        run_step() {
            shift
            "$@"
        }
        run_component() {
            printf '%s\\n' "$1" >> "${EVENT_LOG}"
        }
        JOBS=6
        run_selected_components clean linux qbox u-boot
        """
    )

    # When: the scheduler dispatches a non-build action.
    result = run_scheduler(script, {"EVENT_LOG": str(event_log)})

    # Then: it preserves the caller's exact serial order.
    assert result.returncode == 0, f"{result.stdout}\n{result.stderr}"
    assert event_log.read_text(encoding="utf-8").splitlines() == [
        "linux",
        "qbox",
        "u-boot",
    ]


def test_run_step_preserves_nested_logged_command_failure(tmp_path: Path) -> None:
    script = dedent(
        """\
        set -uo pipefail
        LOCAL_BUILD_DIR="${TEST_LOCAL_BUILD_DIR}"
        source scripts/build/local_build_common.sh
        component() {
            run_logged nested-command bash -c 'exit 7'
            true
        }
        if run_step component-build component; then
            exit 42
        fi
        """
    )

    result = run_scheduler(
        script,
        {"TEST_LOCAL_BUILD_DIR": str(tmp_path / "local-build")},
    )

    assert result.returncode == 0, f"{result.stdout}\n{result.stderr}"
    assert "Failed component-build" in result.stdout
    assert "exit 7" in result.stdout


def test_local_build_entrypoint_uses_configured_component_lanes() -> None:
    result = subprocess.run(
        ("./local_build.sh", "--dry-run", "--jobs", "6"),
        cwd=ROOT,
        check=False,
        env=os.environ | {"APOLLO_LOCAL_BUILD_COMPONENT_LANES": "3"},
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert result.returncode == 0, f"{result.stdout}\n{result.stderr}"
    assert "component lanes: 3" in result.stdout

    entrypoint = (ROOT / "local_build.sh").read_text(encoding="utf-8")
    assert 'source "${ROOT_DIR}/scripts/build/modules/build_scheduler.sh"' in entrypoint
    assert 'run_selected_components "${ACTION}" "${SELECTED_COMPONENTS[@]}"' in entrypoint
