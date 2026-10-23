"""Exercise scope selection and image gating with the real pytest plugin."""

import json
import os
from pathlib import Path
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[2]


def run_cases(tmp_path, source, *options):
    tests = tmp_path / "tests"
    tests.mkdir()
    (tests / "conftest.py").write_text('''
from pathlib import Path
import pytest
from test_automation.pytest_plugin import *
from test_automation import reporting
reporting.TESTS_ROOT = Path(__file__).parent

@pytest.fixture(scope="session")
def platform_bundle():
    raise AssertionError("must not start a device for an incompatible image")
''')
    for relative, content in source.items():
        path = tests / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    (tmp_path / "pytest.ini").write_text(
        "[pytest]\njunit_family=xunit1\nmarkers=\n    image(scope): test image scope\n"
    )
    env = {**os.environ, "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
           "PYTHONPATH": os.pathsep.join(str(ROOT / path) for path in (
               "qa-tests", "scripts/validation", "scripts/run", "."))}
    env.pop("PYTEST_ADDOPTS", None)
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "--run-dir", str(tmp_path / "report"), *options],
        cwd=tmp_path, env=env, capture_output=True, text=True, timeout=30,
    )
    return result, json.loads((tmp_path / "report/results.json").read_text())


SCOPED_CASES = '''
import pytest
@pytest.mark.image("bsp-only")
def test_bsp(): pass
@pytest.mark.image("product-only")
def test_product(): pass
@pytest.mark.image("any")
def test_any(): pass
def test_default(): pass
'''


@pytest.mark.parametrize("image", ["bsp", "product"])
def test_scope_gate_applies_without_platform_fixture_and_is_reported(tmp_path, image):
    result, report = run_cases(tmp_path, {"ap/boot/test_scope.py": SCOPED_CASES}, "--image", image)
    assert result.returncode == 0, result.stdout + result.stderr
    assert report["counts"]["passed"] == 3
    assert report["counts"]["skipped"] == 1
    assert report["image_scopes"] == {"bsp-only": 1, "product-only": 1, "any": 2}
    for case in report["tests"]:
        assert case["image_scope"] == dict(case["user_properties"])["image_scope"]
        if case["status"] == "SKIP":
            assert f"selected --image={image}" in case["phases"]["setup"]["longrepr"]
    for name in ("report.md", "report.html", "junit.xml"):
        text = (tmp_path / "report" / name).read_text()
        assert "bsp-only" in text and "product-only" in text and "any" in text


@pytest.mark.parametrize("scope,count", [("bsp-only", 1), ("product-only", 1), ("any", 2)])
def test_exact_scope_selection_and_collect_only_do_not_launch_qbox(tmp_path, scope, count):
    result, report = run_cases(tmp_path, {"ap/boot/test_scope.py": SCOPED_CASES},
                               "--test-scope", scope, "--collect-only")
    assert result.returncode == 0, result.stdout + result.stderr
    assert report["counts"]["selected"] == count
    assert report["counts"]["deselected"] == 4 - count
    assert report["counts"]["executed"] == 0
    assert {case["image_scope"] for case in report["tests"]} == {scope}


def test_incompatible_image_skips_before_platform_fixture(tmp_path):
    result, report = run_cases(tmp_path, {"ap/power/test_scope.py": '''
import pytest
@pytest.mark.image("bsp-only")
def test_bsp(platform_bundle): pass
'''}, "--image=product")
    assert result.returncode == 0, result.stdout + result.stderr
    assert report["counts"]["skipped"] == 1
    assert report["counts"]["errors"] == 0


@pytest.mark.parametrize("marker", ['"product"', '"all"', '', '"any", "bsp-only"', 'name="any"'])
def test_invalid_scope_is_rejected_during_collection(tmp_path, marker):
    result, report = run_cases(tmp_path, {"ap/boot/test_scope.py": f'''
import pytest
@pytest.mark.image({marker})
def test_invalid(): pass
'''})
    assert result.returncode == 4, result.stdout + result.stderr
    assert "image marker must be one of" in result.stderr
    assert report["status"] == "ERROR"
    assert report["counts"]["collection_errors"] == 1
    assert "image marker must be one of" in report["collection_errors"][0]["longrepr"]
    assert "image marker must be one of" in (tmp_path / "report/report.html").read_text()


def test_all_boot_cases_precede_other_domains_runtime_cases(tmp_path):
    result, report = run_cases(tmp_path, {
        "ap/power/test_power.py": "def test_power(): pass\n",
        "rse/boot/test_boot.py": "def test_boot(): pass\n",
    }, "--collect-only")
    assert result.returncode == 0, result.stdout + result.stderr
    assert [case["category"] for case in report["tests"]] == ["boot", "power"]
