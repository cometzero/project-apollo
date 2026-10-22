"""Host checks for the owned lat_mem_rd duration-option patch."""
import os
from pathlib import Path
import re
import shutil
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / "hsoc-stack/yocto/meta-hsoc-auto-solutions/recipes-benchmark/lmbench/files/0001-lat-mem-rd-add-sample-duration-option.patch"


@pytest.fixture(scope="module")
def binary(tmp_path_factory):
    supplied = os.environ.get("LMBENCH_SOURCE")
    candidates = sorted((ROOT / "build/tmp_baremetal/work").glob("*/lmbench/*/lmbench-*"))
    if not supplied and not candidates:
        pytest.skip("set LMBENCH_SOURCE to an unpacked lmbench tree")
    source = Path(supplied) if supplied else candidates[-1]
    include = Path(os.environ.get("TIRPC_INCLUDE", "/usr/include/tirpc"))
    if not (include / "rpc/rpc.h").exists():
        headers = sorted((ROOT / "build/tmp_baremetal/work").glob("*/lmbench/*/recipe-sysroot/usr/include/tirpc/rpc/rpc.h"))
        if not headers:
            pytest.skip("host compiler requires libtirpc headers")
        include = headers[-1].parent.parent
    if not shutil.which("cc") or not shutil.which("patch"):
        pytest.skip("host cc and patch required")
    work = tmp_path_factory.mktemp("lmbench") / "source"
    shutil.copytree(source, work, ignore=shutil.ignore_patterns(".git", "bin"))
    target = work / "src/lat_mem_rd.c"
    timing = (work / "src/lib_timing.c").read_bytes()
    if "static int sample_usec" in target.read_text():
        subprocess.run(["patch", "-R", "-p1", "-i", str(PATCH)], cwd=work, check=True, capture_output=True)
    subprocess.run(["patch", "-p1", "-i", str(PATCH)], cwd=work, check=True, capture_output=True)
    assert (work / "src/lib_timing.c").read_bytes() == timing
    assert "static int sample_usec = 100000;" in target.read_text()
    files = ["lat_mem_rd.c", "lib_timing.c", "lib_mem.c", "lib_stats.c", "lib_debug.c", "lib_sched.c", "getopt.c"]
    executable = work / "lat_mem_rd"
    subprocess.run(["cc", "-O2", "-D_GNU_SOURCE", "-DHAVE_off64_t", "-DHAVE_socklen_t", "-DHAVE_uint",
                    "-I" + str(include), "-I" + str(work / "src"),
                    *(str(work / "src" / name) for name in files), "-lm", "-o", str(executable)],
                   check=True, capture_output=True)
    return executable


def run(binary, *args, enough=None):
    env = os.environ.copy()
    for key in ("ENOUGH", "TIMING_O", "LOOP_O"):
        env.pop(key, None)
    if enough:
        env["ENOUGH"] = enough
    return subprocess.run([str(binary), *args], text=True, capture_output=True, env=env, timeout=15)


@pytest.mark.parametrize("value", ["", "0", "199", "-200", "+200", " 200", "200 ", "200us", "200.5", "0x1000", "2147483648", "999999999999999999999"])
def test_invalid_duration(binary, value):
    result = run(binary, "-E", value, "1", "64")
    assert result.returncode != 0
    assert "usage" in result.stderr.lower()


def test_missing_duration(binary):
    assert run(binary, "-E").returncode != 0


def test_default_has_no_override(binary):
    # Zero upper working set avoids running the unchanged long default here.
    result = run(binary, "0", "64")
    assert result.returncode == 0
    assert "sample-usec" not in result.stderr


def test_maximum_duration_parses_without_measuring(binary):
    result = run(binary, "-E", "2147483647", "0", "64")
    assert result.returncode == 0
    assert "sample-usec=2147483647" in result.stderr


@pytest.mark.parametrize("duration", ["200", "1000"])
def test_full_working_set_sweep(binary, duration):
    # A pre-existing longer ENOUGH must not defeat the explicit short option.
    result = run(binary, "-N", "1", "-E", duration, "1", "64", enough="10000000")
    assert result.returncode == 0, result.stderr
    assert f"modified lmbench lat_mem_rd: sample-usec={duration}" in result.stderr
    rows = re.findall(r"^([0-9]+\.[0-9]+) ([0-9]+\.[0-9]+)$", result.stderr, re.M)
    assert len(rows) == 21
    assert float(rows[0][0]) == 0.00049
    assert float(rows[-1][0]) == 1.0
    assert all(float(latency) > 0 for _, latency in rows)
