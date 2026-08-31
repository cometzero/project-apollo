from __future__ import annotations

from pathlib import Path
import re


class ModeValidationError(ValueError):
    pass


def validate(log: Path, mode: str, probe_sha256: str) -> None:
    raw = log.read_text(encoding="utf-8", errors="replace")
    clean = re.sub(r"\x1b\[[0-?]*[ -/]*[@-~]", "", raw).replace("\r", "")
    events: dict[str, list[dict[str, str]]] = {}
    for line in clean.splitlines():
        if not line.startswith("APOLLO_IRQ|"):
            continue
        fields: dict[str, str] = {}
        for token in line.removeprefix("APOLLO_IRQ|").split("|"):
            if "=" not in token:
                raise ModeValidationError("mode_extra_malformed")
            key, value = token.split("=", 1)
            fields[key] = value
        events.setdefault(fields.get("event", ""), []).append(fields)
    states = events.get("msi_state", [])
    if len(states) != 1:
        raise ModeValidationError("msi_state")
    try:
        count = int(states[0].get("count", ""), 10)
    except ValueError as error:
        raise ModeValidationError("msi_state") from error
    if mode == "intx" and count != 0:
        raise ModeValidationError("intx_msi_irqs")
    if mode == "msix" and count <= 0:
        raise ModeValidationError("msix_msi_irqs")
    embedded = events.get("embedded_probe", [])
    if len(embedded) != 1:
        raise ModeValidationError("embedded_probe")
    if (
        embedded[0].get("path") != "/usr/bin/apollo-pcie-its-guest"
        or embedded[0].get("sha256") != probe_sha256
        or embedded[0].get("bounded_commands") != "ping-udhcpc"
    ):
        raise ModeValidationError("embedded_probe")
