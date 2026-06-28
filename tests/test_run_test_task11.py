from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "run_test.sh"


def run_runner(*args: str, extra_env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        [str(RUNNER), *args],
        cwd=ROOT,
        check=False,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def nonempty_lines(text: str) -> list[str]:
    return [line for line in text.splitlines() if line.strip()]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_fake_python(path: Path) -> None:
    path.write_text(
        """#!/usr/bin/env bash
set -euo pipefail
original=("$@")
if [[ "$1" == "-m" && "$2" == "compileall" ]]; then
  printf 'fake compileall failure\\n' >&2
  exit 9
fi
if [[ "$1" == "scripts/test/run_test_manifest.py" ]]; then
  subcmd="$2"
  out=""
  while (($#)); do
    if [[ "$1" == "--out" ]]; then
      out="$2"
      break
    fi
    shift
  done
  mkdir -p "$(dirname "${out}")"
  case "${subcmd}" in
    inspect)
      printf '{"status":"ok","machine":"apollo-fvp","distro":"auto-ad-nexios","rd_aspen_variant":"cfg2","pc_cpus_count_default":16,"test_suites":"ping ssh","test_target_ip":"127.0.0.1:2222"}\\n' >"${out}"
      ;;
    plan)
      printf '{"included":{"validation_current":["ping"],"validation_extended":["ssh"],"extra":[]},"excluded":[]}\\n' >"${out}"
      ;;
    preflight)
      printf '{"status":"ok","blockers":[]}\\n' >"${out}"
      ;;
    *)
      exec "${REAL_PYTHON}" "${original[@]}"
      ;;
  esac
  printf '%s\\n' "${out}"
  exit 0
fi
if [[ "$1" == scripts/test/validate_qbox_* || "$1" == scripts/test/audit_qbox_* ]]; then
  out=""
  while (($#)); do
    if [[ "$1" == "--out" || "$1" == "--output" ]]; then
      out="$2"
      break
    fi
    shift
  done
  if [[ -n "${out}" ]]; then
    mkdir -p "$(dirname "${out}")"
    printf '{"passed":true}\\n' >"${out}"
  else
    printf '{"passed":true}\\n'
  fi
  exit 0
fi
exec "${REAL_PYTHON}" "${original[@]}"
""",
        encoding="utf-8",
    )
    path.chmod(0o755)


def write_fake_pytest(path: Path) -> None:
    path.write_text("#!/usr/bin/env bash\nprintf 'fake pytest pass\\n'\n", encoding="utf-8")
    path.chmod(0o755)


def write_fake_pytest_with_nested_runner(path: Path) -> None:
    path.write_text(
        """#!/usr/bin/env bash
if [[ "${NESTED_RUN_TEST_DONE:-0}" != "1" ]]; then
  NESTED_RUN_TEST_DONE=1 ./run_test.sh --skip-runtime \
    --stamp task-11-pytest-nested-latest \
    --out-dir build/tests/task-11-pytest-nested-latest >/dev/null 2>&1 || true
fi
printf 'fake pytest pass after nested run_test\\n'
""",
        encoding="utf-8",
    )
    path.chmod(0o755)


def write_fake_timeout(path: Path) -> None:
    path.write_text("#!/usr/bin/env bash\nprintf 'fake oeqa pass\\n'\n", encoding="utf-8")
    path.chmod(0o755)


def test_default_run_reaches_preflight_after_extra_lane_failure(tmp_path: Path) -> None:
    # Given: fake cheap lanes where compileall fails but runtime prerequisites pass.
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    write_fake_python(fake_bin / "python3")
    write_fake_pytest(fake_bin / "pytest")
    write_fake_timeout(fake_bin / "timeout")
    out_dir = Path("build/tests/task-11-pytest-continue-after-extra-fail")

    # When: the default runner executes without --skip-runtime.
    result = run_runner(
        "--stamp",
        "task-11-pytest-continue-after-extra-fail",
        "--out-dir",
        str(out_dir),
        extra_env={
            "PATH": f"{fake_bin}:{os.environ['PATH']}",
            "REAL_PYTHON": sys.executable,
            "RUN_TEST_QBOX_BUILD_DIR": str(tmp_path / "missing-qbox-platform"),
        },
    )

    # Then: it still records later safe validation phases and reports final FAIL.
    assert result.returncode == 1
    lines = nonempty_lines(result.stdout)
    assert lines[-2:] == [
        "RESULT: FAIL",
        "SUMMARY: build/tests/task-11-pytest-continue-after-extra-fail/summary.json",
    ]
    summary = load_json(ROOT / out_dir / "summary.json")
    assert summary["status"] == "FAIL"
    steps = {step["name"]: step for step in summary["steps"]}
    assert steps["extra-static-compileall"]["exit_code"] == 9
    assert steps["preflight"]["status"] == "PASS"
    assert steps["oeqa-current"]["status"] == "PASS"
    assert steps["oeqa-extended"]["status"] == "PASS"


def test_default_run_refreshes_latest_after_nested_selftest_run(tmp_path: Path) -> None:
    # Given: the project pytest lane runs a nested run_test.sh self-test.
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    write_fake_python(fake_bin / "python3")
    write_fake_pytest_with_nested_runner(fake_bin / "pytest")
    write_fake_timeout(fake_bin / "timeout")
    out_dir = Path("build/tests/task-11-parent-latest-after-nested")

    # When: the parent default runner completes after the nested self-test.
    result = run_runner(
        "--stamp",
        "task-11-parent-latest-after-nested",
        "--out-dir",
        str(out_dir),
        extra_env={
            "PATH": f"{fake_bin}:{os.environ['PATH']}",
            "REAL_PYTHON": sys.executable,
            "RUN_TEST_QBOX_BUILD_DIR": str(tmp_path / "missing-qbox-platform"),
        },
    )

    # Then: latest points back to the completed parent run, not the nested run.
    assert result.returncode == 1
    lines = nonempty_lines(result.stdout)
    assert lines[-2:] == [
        "RESULT: FAIL",
        "SUMMARY: build/tests/task-11-parent-latest-after-nested/summary.json",
    ]
    assert os.readlink(ROOT / "build/tests/latest") == "task-11-parent-latest-after-nested"
    summary = load_json(ROOT / out_dir / "summary.json")
    assert summary["status"] == "FAIL"
    assert (ROOT / "build/tests/task-11-pytest-nested-latest/summary.json").is_file()
