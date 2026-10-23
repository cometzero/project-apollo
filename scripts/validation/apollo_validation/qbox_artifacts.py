from __future__ import annotations

from pathlib import Path

from .evidence import JsonObject


def qbox_artifacts(
    out_dir: Path,
    test_profile: str | None,
) -> list[JsonObject]:
    qbox_dir = out_dir / "qbox"
    artifacts: list[JsonObject] = [
        {"kind": "qbox_result", "path": str(qbox_dir / "result.json")},
        {"kind": "qbox_summary", "path": str(qbox_dir / "summary.txt")},
    ]
    for name in (
        "qbox-platform.log",
        "qbox-rse.log",
        "qbox-safety-island-cl0.log",
        "qbox-safety-island-cl1.log",
        "qbox-secure-console.log",
        "qbox-primary-console.log",
    ):
        artifacts.append(
            {"kind": "qbox_console", "path": str(qbox_dir / name)}
        )
    if test_profile == "platform-devices":
        artifacts.append(
            {
                "kind": "network_lifecycle",
                "path": str(out_dir / "logs/platform-network.jsonl"),
            }
        )
    return artifacts
