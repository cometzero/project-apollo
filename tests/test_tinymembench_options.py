"""Compile the recipe patch against a supplied or existing Yocto source tree."""
import os
from pathlib import Path
import shutil
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / "hsoc-stack/yocto/meta-hsoc-auto-solutions/recipes-benchmark/tinymembench/files/0001-add-runtime-benchmark-parameters.patch"


@pytest.fixture(scope="module")
def binary(tmp_path_factory):
    source = os.environ.get("TINYMEMBENCH_SOURCE")
    if source:
        source = Path(source)
    else:
        candidates = sorted((ROOT / "build/tmp_baremetal/work").glob("*/tinymembench/*/git"))
        if not candidates:
            pytest.skip("set TINYMEMBENCH_SOURCE to an unpacked upstream tree")
        source = candidates[-1]
    if not all(shutil.which(tool) for tool in ("cc", "make", "patch")):
        pytest.skip("host cc, make and patch required")
    work = tmp_path_factory.mktemp("tinymembench") / "source"
    shutil.copytree(source, work, ignore=shutil.ignore_patterns(".git", "*.o", "tinymembench"))
    # Yocto's current tree may already have the owned patch applied.
    if "static int positive_number(" in (work / "main.c").read_text():
        subprocess.run(["patch", "-R", "-p1", "-i", str(PATCH)], cwd=work, check=True, capture_output=True)
    subprocess.run(["patch", "-p1", "-i", str(PATCH)], cwd=work, check=True, capture_output=True)
    subprocess.run(["make", "CC=cc"], cwd=work, check=True, capture_output=True)
    return work / "tinymembench"


def run(binary, *args):
    return subprocess.run([str(binary), *args], text=True, capture_output=True, timeout=10)


def test_help_preserves_upstream_defaults(binary):
    result = run(binary, "--help")
    assert result.returncode == 0
    for value in ("32768", "65536", "500", "10", "10000000"):
        assert f"(default {value})" in result.stdout
    assert "Memory bandwidth tests" not in result.stdout


@pytest.mark.parametrize("option,value", [
    ("--bandwidth-size-kib", "1"),
    ("--bandwidth-size-kib", "3"),
    ("--bandwidth-size-kib", "524290"),
    ("--latency-size-kib", "3"),
    ("--latency-size-kib", "1048576"),
    ("--latency-count", "1"),
    ("--latency-count", "17"),
    ("--latency-count", "2147483647"),
    ("--repeats", "1001"),
    ("--duration-ms", "2147483648"),
    ("--unknown", "1"),
])
def test_option_bounds(binary, option, value):
    result = run(binary, option, value)
    assert result.returncode != 0
    assert "Invalid" in result.stderr
    assert "Memory bandwidth tests" not in result.stdout


@pytest.mark.parametrize("value", ["", "0", "-1", "+1", " 1", "1 ", "1ms", "1.5", "0x10", "999999999999999999999999"])
def test_strict_numeric_parser(binary, value):
    result = run(binary, "--duration-ms", value)
    assert result.returncode != 0
    assert "Invalid" in result.stderr


def test_missing_value(binary):
    assert run(binary, "--duration-ms").returncode != 0


def test_upper_bounds_without_allocating(binary):
    result = run(binary, "--bandwidth-size-kib", "524288", "--latency-size-kib", "524288",
                 "--duration-ms", "2147483647", "--latency-count", "2147483632",
                 "--repeats", "1000", "--help")
    assert result.returncode == 0


def test_small_full_suite(binary):
    result = run(binary, "--bandwidth-size-kib", "2", "--latency-size-kib", "2",
                 "--duration-ms", "1", "--latency-count", "16", "--repeats", "1")
    assert result.returncode == 0, result.stderr
    assert "Settings: bandwidth-size-kib=2 latency-size-kib=2 duration-ms=1 repeats=1 latency-count=16" in result.stdout
    for marker in ("C copy", "standard memcpy", "Memory latency test", "1024 :", "2048 :"):
        assert marker in result.stdout
