from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_vscode_configs_match_local_debug_endpoints() -> None:
    launch = json.loads((ROOT / ".vscode/launch.json").read_text())
    configs = {item["name"]: item for item in launch["configurations"]}
    expected = {
        "Apollo QBox: host": ("127.0.0.1:12339", "qbox-host.gdb"),
        "Apollo QBox: RSE": ("127.0.0.1:12340", "domain-rse.gdb"),
        "Apollo QBox: SI0": ("127.0.0.1:12341", "domain-si0.gdb"),
        "Apollo QBox: SI1": ("127.0.0.1:12342", "domain-si1.gdb"),
        "Apollo QBox: AP": ("127.0.0.1:12343", "domain-ap.gdb"),
    }

    for name, (endpoint, script) in expected.items():
        config = configs[name]
        assert config["miDebuggerServerAddress"] == endpoint
        assert any(script in item["text"] for item in config["setupCommands"])

    ap = configs["Apollo QBox: AP"]
    assert ap["preLaunchTask"] == "Apollo QBox: wait for AP safe point"
    early_configs = {
        "Apollo QBox: RSE early",
        "Apollo QBox: SI0 early (SCP)",
        "Apollo QBox: SI1 early (Zephyr)",
        "Apollo QBox: AP early (TF-A)",
    }
    assert early_configs <= configs.keys()
    for name in early_configs:
        assert configs[name]["preLaunchTask"].endswith("GDB")

    for name in ("Apollo QBox: RSE", "Apollo QBox: SI0", "Apollo QBox: SI1"):
        assert configs[name]["preLaunchTask"] == "Apollo QBox: wait for AP safe point"

    compounds = {item["name"]: item for item in launch["compounds"]}
    assert set(compounds["Apollo QBox: all domains"]["configurations"]) == set(expected)


def test_vscode_recommends_cpp_debugger_and_start_task() -> None:
    extensions = json.loads((ROOT / ".vscode/extensions.json").read_text())
    tasks = json.loads((ROOT / ".vscode/tasks.json").read_text())
    labels = {task["label"] for task in tasks["tasks"]}

    assert "ms-vscode.cpptools" in extensions["recommendations"]
    assert "Apollo QBox: start debug servers" in labels
    assert "Apollo QBox: wait for AP safe point" in labels

    ap_wait = next(
        task
        for task in tasks["tasks"]
        if task["label"] == "Apollo QBox: wait for AP safe point"
    )
    assert "--wait-log-marker-only" in ap_wait["args"]
    assert "PFDI: OoR tests on core 3 succeeded." in ap_wait["args"]
