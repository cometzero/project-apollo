from __future__ import annotations

from pathlib import Path
import importlib.util
import sys
import tempfile
from types import ModuleType

import pytest


ROOT = Path(__file__).resolve().parents[1]
QUALIFIER = ROOT / "scripts/test/run_qbox_apollo_pcie_irq_task9.py"


def load_qualifier_module() -> ModuleType:
    sys.path.insert(0, str(ROOT))
    spec = importlib.util.spec_from_file_location("task9_qualifier", QUALIFIER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_run_root_parser_accepts_direct_and_verifier_roots() -> None:
    qualifier = load_qualifier_module()
    direct = ROOT / ".omo/evidence/apollo-gic-its/task-9/run-20990101T010101Z"
    verifier = (
        ROOT
        / ".omo/evidence/apollo-gic-its/task-9/verifier/fresh-run-20990101T010101Z"
    )

    direct_policy = qualifier.parse_run_root(direct)
    verifier_policy = qualifier.parse_run_root(verifier)

    assert direct_policy.path == direct
    assert direct_policy.layout.value == "direct"
    assert verifier_policy.path == verifier
    assert verifier_policy.layout.value == "verifier"


def test_run_root_parser_rejects_unapproved_shapes() -> None:
    qualifier = load_qualifier_module()
    task9_root = ROOT / ".omo/evidence/apollo-gic-its/task-9"
    rejected = (
        task9_root / "verifier/run-20990101T010101Z",
        task9_root / "other/fresh-run-20990101T010101Z",
        task9_root / "verifier/nested/fresh-run-20990101T010101Z",
        task9_root / "verifier/fresh-run-20990101T010101Z/../escape",
        task9_root / "verifier/fresh-run-20990101T010101Z-nope",
        task9_root / "verifier/fresh-run-20990101T010101.123Z",
    )

    for path in rejected:
        with pytest.raises(qualifier.task9.Task9Error):
            qualifier.parse_run_root(path)


def test_run_root_parser_rejects_symlinked_verifier_and_run_root(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    qualifier = load_qualifier_module()
    with tempfile.TemporaryDirectory(prefix=".task9-root-test-", dir=ROOT) as root:
        evidence = Path(root) / "task-9"
        verifier_target = evidence / "real-verifier"
        verifier_target.mkdir(parents=True)
        (evidence / "verifier").symlink_to(verifier_target, target_is_directory=True)
        (evidence / "run-target").mkdir()
        (evidence / "run-20990101T010101Z").symlink_to(
            evidence / "run-target", target_is_directory=True
        )
        monkeypatch.setattr(qualifier.task9_process, "EVIDENCE_ROOT", evidence)

        with pytest.raises(qualifier.task9.Task9Error, match="run_root_symlink"):
            qualifier.parse_run_root(
                evidence / "verifier/fresh-run-20990101T010101Z"
            )
        with pytest.raises(qualifier.task9.Task9Error, match="run_root_symlink"):
            qualifier.parse_run_root(evidence / "run-20990101T010101Z")


def test_run_root_parser_rejects_stale_verifier_root(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    qualifier = load_qualifier_module()
    with tempfile.TemporaryDirectory(prefix=".task9-root-test-", dir=ROOT) as root:
        evidence = Path(root) / "task-9"
        stale = evidence / "verifier/fresh-run-20990101T010101Z"
        stale.mkdir(parents=True)
        (stale / "msix").mkdir()
        monkeypatch.setattr(qualifier.task9_process, "EVIDENCE_ROOT", evidence)

        with pytest.raises(qualifier.task9.Task9Error, match="stale_run_root"):
            qualifier.parse_run_root(stale)
