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
    expected_compound = set(expected) - {"Apollo QBox: host"}
    expected_compound.add("Apollo QBox: host run")
    assert set(compounds["Apollo QBox: all domains"]["configurations"]) == (
        expected_compound
    )


def test_vscode_recommends_cpp_debugger_and_start_task() -> None:
    extensions = json.loads((ROOT / ".vscode/extensions.json").read_text())
    tasks = json.loads((ROOT / ".vscode/tasks.json").read_text())
    labels = {task["label"] for task in tasks["tasks"]}

    assert "ms-vscode.cpptools" in extensions["recommendations"]
    assert "Apollo QBox: start debug servers" in labels
    assert "Apollo QBox: wait for AP safe point" in labels

    start = next(
        task
        for task in tasks["tasks"]
        if task["label"] == "Apollo QBox: start debug servers"
    )
    assert "--replace-session" in start["args"]

    ap_wait = next(
        task
        for task in tasks["tasks"]
        if task["label"] == "Apollo QBox: wait for AP safe point"
    )
    assert "--wait-log-marker-only" in ap_wait["args"]
    assert "PFDI: OoR tests on core 3 succeeded." in ap_wait["args"]


def test_vscode_tmux_console_task_is_interactive() -> None:
    # Given: the repository VS Code task configuration.
    tasks = json.loads((ROOT / ".vscode/tasks.json").read_text())

    # When: the QBox tmux console task is selected.
    console = next(
        task
        for task in tasks["tasks"]
        if task["label"] == "Apollo QBox: open tmux console"
    )

    # Then: VS Code opens the fixed debug session in a focused terminal.
    assert console["command"] == "tmux"
    assert console["args"] == [
        "attach-session",
        "-t",
        "apollo-qbox-debug-vscode",
    ]
    assert console["presentation"] == {
        "reveal": "always",
        "panel": "dedicated",
        "focus": True,
        "clear": True,
    }


def test_vscode_compound_starts_servers_before_domain_attach() -> None:
    # Given: the repository VS Code launch configuration.
    launch = json.loads((ROOT / ".vscode/launch.json").read_text())

    # When: the all-domain compound and host configuration are selected.
    compound = next(
        item
        for item in launch["compounds"]
        if item["name"] == "Apollo QBox: all domains"
    )
    host = next(
        item
        for item in launch["configurations"]
        if item["name"] == "Apollo QBox: host"
    )

    # Then: one compound barrier starts QBox before any child can attach.
    assert compound["preLaunchTask"] == "Apollo QBox: start debug servers"
    assert "preLaunchTask" not in host


def test_vscode_compound_host_does_not_block_domain_startup() -> None:
    # Given: the all-domain compound and its host debugger configuration.
    launch = json.loads((ROOT / ".vscode/launch.json").read_text())
    configs = {item["name"]: item for item in launch["configurations"]}
    compound = next(
        item
        for item in launch["compounds"]
        if item["name"] == "Apollo QBox: all domains"
    )

    # When: the host configuration used by the compound is inspected.
    compound_host = configs["Apollo QBox: host run"]
    setup_commands = [item["text"] for item in compound_host["setupCommands"]]

    # Then: compound startup removes entry breakpoints before continuing QBox.
    assert "Apollo QBox: host run" in compound["configurations"]
    assert "Apollo QBox: host" not in compound["configurations"]
    assert "delete breakpoints" in setup_commands
    assert all(
        item["text"] != "delete breakpoints"
        for item in configs["Apollo QBox: host"]["setupCommands"]
    )
