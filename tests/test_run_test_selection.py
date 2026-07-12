from __future__ import annotations

import shutil
from pathlib import Path

from run_test_helpers import ROOT, load_commands, load_json, run_runner


REBOOT_TEST = "test_00_rse.RseTest.test_scmi_reboot"
NORMAL_BOOT_TEST = "test_00_rse.RseTest.test_normal_boot"
MEASURED_BOOT_TEST = "test_00_rse.RseTest.test_measured_boot"
LINUX_BOOT_TEST = "test_10_linuxboot.LinuxBootTest.test_linux_boot"
LINUX_LOGIN_TEST = "test_10_linuxlogin.LinuxLoginTest.test_linux_login"


def test_individual_test_runs_transitive_dependencies_first() -> None:
    out_dir = Path("build/tests/ulw-pytest-selection")
    shutil.rmtree(ROOT / out_dir, ignore_errors=True)

    result = run_runner(
        "--test",
        REBOOT_TEST,
        "--dry-run",
        "--stamp",
        "ulw-pytest-selection",
        "--out-dir",
        str(out_dir),
    )

    assert result.returncode == 0, result.stderr
    run_dir = ROOT / out_dir
    selection = load_json(run_dir / "selection.json")
    assert selection["category"] == "power"
    assert selection["requested"] == [REBOOT_TEST]
    assert selection["ordered_tests"] == [
        NORMAL_BOOT_TEST,
        MEASURED_BOOT_TEST,
        REBOOT_TEST,
    ]
    conf = (run_dir / "conf/oeqa-power.conf").read_text(encoding="utf-8")
    assert (
        f'TEST_SUITES = "{NORMAL_BOOT_TEST} {MEASURED_BOOT_TEST} {REBOOT_TEST}"'
        in conf
    )


def test_individual_test_rejects_unknown_name() -> None:
    result = run_runner("--test", "not_a_real_apollo_test", "--dry-run")

    assert result.returncode == 64
    assert "unknown test" in result.stderr


def test_individual_functional_test_skips_unrelated_basic_runtime() -> None:
    out_dir = Path("build/tests/ulw-pytest-functional-selection")
    shutil.rmtree(ROOT / out_dir, ignore_errors=True)

    result = run_runner(
        "--test",
        NORMAL_BOOT_TEST,
        "--dry-run",
        "--stamp",
        "ulw-pytest-functional-selection",
        "--out-dir",
        str(out_dir),
    )

    assert result.returncode == 0, result.stderr
    names = [record["name"] for record in load_commands(ROOT / out_dir)]
    assert "runtime-preflight" in names
    assert "basic-boot" not in names
    assert "oeqa-functional" in names


def test_individual_test_rejects_conflicting_category() -> None:
    result = run_runner(
        "--category",
        "functional",
        "--test",
        REBOOT_TEST,
        "--dry-run",
    )

    assert result.returncode == 64
    assert "belongs to category power" in result.stderr


def test_extended_fwu_test_runs_linux_login_dependencies_first() -> None:
    out_dir = Path("build/tests/ulw-pytest-fwu-selection")
    shutil.rmtree(ROOT / out_dir, ignore_errors=True)

    result = run_runner(
        "--test",
        "test_100_fwu",
        "--dry-run",
        "--stamp",
        "ulw-pytest-fwu-selection",
        "--out-dir",
        str(out_dir),
    )

    assert result.returncode == 0, result.stderr
    selection = load_json(ROOT / out_dir / "selection.json")
    assert selection["category"] == "extended"
    assert selection["ordered_tests"] == [
        LINUX_BOOT_TEST,
        LINUX_LOGIN_TEST,
        "test_100_fwu",
    ]


def test_non_oeqa_catalog_entry_is_not_individually_selectable() -> None:
    result = run_runner("--test", "tftf", "--dry-run")

    assert result.returncode == 64
    assert "not individually selectable" in result.stderr


def test_missing_dry_run_build_dir_preserves_inferred_execution_category() -> None:
    out_dir = Path("build/tests/ulw-pytest-selection-fallback")
    shutil.rmtree(ROOT / out_dir, ignore_errors=True)

    result = run_runner(
        "--build-dir",
        "build/does-not-exist",
        "--test",
        NORMAL_BOOT_TEST,
        "--dry-run",
        "--stamp",
        "ulw-pytest-selection-fallback",
        "--out-dir",
        str(out_dir),
    )

    assert result.returncode == 0, result.stderr
    names = [record["name"] for record in load_commands(ROOT / out_dir)]
    assert "basic-boot" not in names
    assert "oeqa-functional" in names
