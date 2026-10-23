"""Run the guest shell probe against the Linux QoS clamp contract."""

import os
from pathlib import Path
import shlex
import subprocess
import sys

import pytest

from scripts.run.qbox_cpufreq_commands import CPUFREQ_ROOT, cpufreq_probe_commands


def run_boundary(tmp_path: Path, mode: str):
    policy = tmp_path / "policy0"
    policy.mkdir()
    for name, value in (("scaling_min_freq", "1800000"), ("scaling_max_freq", "2500000"),
                        ("scaling_governor", "schedutil")):
        (policy / name).write_text(value + "\n")
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    cat = bin_dir / "cat"
    cat.write_text(f"#!{sys.executable}\n" + '''
import os
from pathlib import Path
import sys
path = Path(sys.argv[1])
if path.name not in ("scaling_min_freq", "scaling_max_freq"):
    print(path.read_text().strip())
    raise SystemExit
minimum = int((path.parent / "scaling_min_freq").read_text())
maximum = int((path.parent / "scaling_max_freq").read_text())
mode = os.environ["CPUFREQ_FIXTURE_MODE"]
if mode == "unclamped":
    print(minimum if path.name == "scaling_min_freq" else maximum)
elif mode == "ignored":
    print(1800000 if path.name == "scaling_min_freq" else 2500000)
else:
    counter = path.parent / "reads"
    reads = int(counter.read_text()) if counter.exists() else 0
    if mode == "delayed" and minimum == 2600000 and reads < 2:
        counter.write_text(str(reads + 1))
        minimum = 1800000
    maximum = max(1800000, min(maximum, 2500000))
    minimum = max(1800000, min(minimum, maximum))
    print(minimum if path.name == "scaling_min_freq" else maximum)
''')
    cat.chmod(0o755)
    script = (cpufreq_probe_commands()[-1]
              .replace(f"root={CPUFREQ_ROOT}", f"root={shlex.quote(str(tmp_path))}")
              .replace("nproc --all", "printf '4\\n'"))
    prelude = "sleep() { :; }; "
    if mode in ("write-failure", "restore-failure"):
        rejected = "2600000" if mode == "write-failure" else "schedutil"
        prelude += f'''printf() {{
            if test "${{2:-}}" = {rejected}; then
                echo "fixture write failure: $2" >&2; return 7;
            fi;
            command printf "$@";
        }}; '''
    result = subprocess.run(
        ["sh", "-c", prelude + script], capture_output=True, text=True, timeout=15,
        env={**os.environ, "PATH": str(bin_dir) + os.pathsep + os.defpath,
             "CPUFREQ_FIXTURE_MODE": mode},
    )
    return result, policy


@pytest.mark.parametrize("mode", ["clamped", "delayed"])
def test_boundary_probe_accepts_exact_clamping_and_restores_original_requests(tmp_path, mode):
    result, policy = run_boundary(tmp_path, mode)
    assert result.returncode == 0, result.stderr
    assert "requested_min=2600000 requested_max=1700000" in result.stdout
    assert "high_min=2500000 high_max=2500000 low_min=1800000 low_max=1800000" in result.stdout
    assert "restored=1" in result.stdout
    assert (policy / "scaling_min_freq").read_text() == "1800000\n"
    assert (policy / "scaling_max_freq").read_text() == "2500000\n"
    assert (policy / "scaling_governor").read_text() == "schedutil\n"


@pytest.mark.parametrize("mode", ["unclamped", "ignored", "write-failure"])
def test_boundary_probe_rejects_bad_limits_or_write_failure_and_restores(tmp_path, mode):
    result, policy = run_boundary(tmp_path, mode)
    assert result.returncode != 0
    assert "CPUFREQ_NEGATIVE" not in result.stdout
    assert "restored=1" in result.stdout
    assert (policy / "scaling_min_freq").read_text() == "1800000\n"
    assert (policy / "scaling_max_freq").read_text() == "2500000\n"


def test_boundary_probe_does_not_hide_cleanup_write_failure(tmp_path):
    result, _ = run_boundary(tmp_path, "restore-failure")
    assert result.returncode != 0
    assert "restored=0" in result.stdout
    assert "fixture write failure: schedutil" in result.stderr
