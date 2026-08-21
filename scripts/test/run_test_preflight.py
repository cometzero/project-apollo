from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
import shutil
import socket
from typing import Final

from run_test_fvp_tap_network import tap_network_preflight


type JsonValue = None | bool | int | float | str | list[JsonValue] | dict[str, JsonValue]
type JsonObject = dict[str, JsonValue]

DEFAULT_TARGET_IP: Final = "127.0.0.1:2222"
FVP_IMAGE_SUFFIXES: Final = (
    ".bin",
    ".cpio",
    ".cpio.gz",
    ".dtb",
    ".efi",
    ".ext4",
    ".img",
    ".verity",
    ".wic",
)
IMAGE_FSTYPES_TO_CHECK: Final = {"wic", "ext4", "ext4.verity"}


@dataclass(frozen=True, slots=True)
class PreflightInputs:
    root: Path
    build_dir: Path
    machine: str
    image: str = "nexios-image"
    fvpconf_path: Path | None = None


@dataclass(frozen=True, slots=True)
class CheckResult:
    name: str
    status: str
    path: str
    reason: str = ""


def _read_json(path: Path) -> JsonObject:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        return data
    return {}


def _str_value(value: JsonValue) -> str:
    return value if isinstance(value, str) else ""


def _str_list(value: JsonValue) -> list[str]:
    return [item for item in value if isinstance(item, str)] if isinstance(value, list) else []


def _str_dict(value: JsonValue) -> dict[str, str]:
    return {key: item for key, item in value.items() if isinstance(item, str)} if isinstance(value, dict) else {}


def _resolve(root: Path, path: Path) -> Path:
    return path if path.is_absolute() else root / path


def _resolve_artifact(inputs: PreflightInputs, path: Path) -> Path:
    if path.is_absolute():
        return path
    first = path.parts[0] if path.parts else ""
    if first == inputs.build_dir.name:
        return inputs.root / path
    if first == "tmp_baremetal":
        return inputs.root / inputs.build_dir / path
    return inputs.root / path


def _deploy_dir(inputs: PreflightInputs) -> Path:
    return inputs.root / inputs.build_dir / "tmp_baremetal/deploy/images" / inputs.machine


def _select_fvpconf(inputs: PreflightInputs) -> Path:
    if inputs.fvpconf_path is not None:
        return _resolve(inputs.root, inputs.fvpconf_path)
    deploy_dir = _deploy_dir(inputs)
    stable = deploy_dir / f"{inputs.image}-{inputs.machine}.fvpconf"
    if stable.exists():
        return stable
    latest = sorted(deploy_dir.glob(f"{inputs.image}-{inputs.machine}-*.fvpconf"))
    if latest:
        return latest[-1]
    return stable


def _blocker(reason: str, path: Path, name: str) -> JsonObject:
    return {"reason": reason, "path": str(path), "name": name}


def _file_check(name: str, path: Path, reason: str) -> tuple[CheckResult, JsonObject | None]:
    if path.is_file():
        return CheckResult(name=name, status="ok", path=str(path)), None
    return CheckResult(name=name, status="blocked", path=str(path), reason=reason), _blocker(reason, path, name)


def _path_check(name: str, path: Path, reason: str) -> tuple[CheckResult, JsonObject | None]:
    if path.is_file() or path.is_dir():
        return CheckResult(name=name, status="ok", path=str(path)), None
    return CheckResult(name=name, status="blocked", path=str(path), reason=reason), _blocker(reason, path, name)


def _check_tool(root: Path) -> tuple[CheckResult, JsonObject | None]:
    path = root / "layers/meta-arm/scripts/runfvp"
    return _file_check("runfvp", path, "blocked_missing_runfvp")


def _check_telnet() -> tuple[CheckResult, JsonObject | None]:
    found = shutil.which("telnet")
    if found:
        return CheckResult(name="telnet", status="ok", path=found), None
    return CheckResult(name="telnet", status="blocked", path="", reason="blocked_missing_telnet"), {
        "reason": "blocked_missing_telnet",
        "path": "",
        "name": "telnet",
    }


def _resolve_bindir_path(inputs: PreflightInputs, raw_path: str, bindir: str) -> Path:
    path = Path(raw_path)
    if path.is_absolute():
        return path
    bindir_path = Path(bindir)
    if bindir:
        return _resolve_artifact(inputs, bindir_path) / path
    return _resolve_artifact(inputs, path)


def _plugin_paths(inputs: PreflightInputs, args: list[str], bindir: str) -> list[Path]:
    paths: list[Path] = []
    index = 0
    while index < len(args):
        arg = args[index]
        if arg == "--plugin" and index + 1 < len(args):
            paths.append(_resolve_bindir_path(inputs, args[index + 1], bindir))
            index += 2
            continue
        if arg.startswith("--plugin="):
            paths.append(_resolve_bindir_path(inputs, arg.removeprefix("--plugin="), bindir))
        elif arg.endswith(".so"):
            paths.append(_resolve_bindir_path(inputs, arg, bindir))
        index += 1
    return paths


def _artifact_from_data(entry: str) -> Path | None:
    if "=" not in entry:
        return None
    raw_path = entry.split("=", 1)[1].split("@", 1)[0]
    return Path(raw_path) if raw_path else None


def _looks_like_artifact(value: str) -> bool:
    return value not in {"", "<default>"} and ("/" in value or value.endswith(FVP_IMAGE_SUFFIXES))


def _fvp_artifacts(fvpconf: JsonObject) -> list[Path]:
    artifacts: list[Path] = []
    for key, value in _str_dict(fvpconf.get("parameters")).items():
        if key.endswith(".fnameWrite"):
            continue
        if _looks_like_artifact(value):
            artifacts.append(Path(value))
    for entry in _str_list(fvpconf.get("data")):
        artifact = _artifact_from_data(entry)
        if artifact is not None:
            artifacts.append(artifact)
    return artifacts


def _testdata_artifacts(inputs: PreflightInputs, deploy_dir: Path, testdata: JsonObject) -> list[Path]:
    artifacts: list[Path] = []
    image_rootfs = _str_value(testdata.get("IMAGE_ROOTFS"))
    if image_rootfs:
        artifacts.append(_resolve_artifact(inputs, Path(image_rootfs)))
    image_link = _str_value(testdata.get("IMAGE_LINK_NAME"))
    fstypes = set(_str_value(testdata.get("IMAGE_FSTYPES")).split())
    for fstype in sorted(fstypes & IMAGE_FSTYPES_TO_CHECK):
        artifacts.append(deploy_dir / f"{image_link}.{fstype}")
    return artifacts


def _dedupe(paths: list[Path]) -> list[Path]:
    seen: set[str] = set()
    unique: list[Path] = []
    for path in paths:
        key = str(path)
        if key in seen:
            continue
        seen.add(key)
        unique.append(path)
    return unique


def _json_values(values: list[JsonObject]) -> list[JsonValue]:
    return [value for value in values]


def _port_in_use(target_ip: str) -> bool:
    host, _, raw_port = target_ip.partition(":")
    if host != "127.0.0.1" or not raw_port.isdigit():
        return False
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.settimeout(0.2)
        return probe.connect_ex((host, int(raw_port))) == 0


def _append_check(
    checks: list[CheckResult],
    blockers: list[JsonObject],
    result: tuple[CheckResult, JsonObject | None],
) -> None:
    check, blocker = result
    checks.append(check)
    if blocker is not None:
        blockers.append(blocker)


def run_preflight(inputs: PreflightInputs) -> JsonObject:
    checks: list[CheckResult] = []
    blockers: list[JsonObject] = []
    deploy_dir = _deploy_dir(inputs)
    fvpconf_path = _select_fvpconf(inputs)
    testdata_path = fvpconf_path.with_suffix(".testdata.json")
    _append_check(checks, blockers, _check_tool(inputs.root))
    _append_check(checks, blockers, _check_telnet())
    tap_check = tap_network_preflight()
    if tap_check.interface_name:
        if tap_check.reason is None:
            checks.append(
                CheckResult(
                    name="fvp_tap_network",
                    status="ok",
                    path=tap_check.interface_name,
                )
            )
        else:
            checks.append(
                CheckResult(
                    name="fvp_tap_network",
                    status="blocked",
                    path=tap_check.interface_name,
                    reason=tap_check.reason,
                )
            )
            blockers.append(
                {
                    "reason": tap_check.reason,
                    "name": "fvp_tap_network",
                    "interface_name": tap_check.interface_name,
                    "host_ip": tap_check.host_ip,
                    "target_ip": tap_check.target_ip,
                    "hint": tap_check.hint,
                }
            )
    _append_check(checks, blockers, _file_check("fvpconf", fvpconf_path, "blocked_missing_fvpconf"))
    _append_check(checks, blockers, _file_check("testdata", testdata_path, "blocked_missing_testdata"))
    fvpconf = _read_json(fvpconf_path) if fvpconf_path.is_file() else {}
    testdata = _read_json(testdata_path) if testdata_path.is_file() else {}
    bindir = _str_value(fvpconf.get("fvp-bindir"))
    executable = _resolve_bindir_path(inputs, _str_value(fvpconf.get("exe")), bindir)
    _append_check(checks, blockers, _file_check("fvp_executable", executable, "blocked_missing_fvp_executable"))
    for plugin in _plugin_paths(inputs, _str_list(fvpconf.get("args")), bindir):
        reason = "blocked_missing_crypto_plugin" if plugin.name == "Crypto.so" else "blocked_missing_fvp_plugin"
        _append_check(checks, blockers, _file_check(f"plugin:{plugin.name}", plugin, reason))
    raw_artifacts = _fvp_artifacts(fvpconf) + _testdata_artifacts(inputs, deploy_dir, testdata)
    artifacts = _dedupe([_resolve_artifact(inputs, artifact) for artifact in raw_artifacts])
    for artifact in artifacts:
        _append_check(checks, blockers, _path_check(f"artifact:{artifact.name}", artifact, "blocked_missing_runtime_artifact"))
    target_ip = _str_value(testdata.get("TEST_TARGET_IP")) or DEFAULT_TARGET_IP
    if _port_in_use(target_ip):
        checks.append(CheckResult(name="runtime_port", status="blocked", path=target_ip, reason="blocked_port_in_use"))
        blockers.append({"reason": "blocked_port_in_use", "path": target_ip, "name": "runtime_port"})
    else:
        checks.append(CheckResult(name="runtime_port", status="ok", path=target_ip))
    return {
        "status": "blocked" if blockers else "ok",
        "machine": inputs.machine,
        "fvpconf": str(fvpconf_path),
        "testdata": str(testdata_path),
        "checks": [asdict(check) for check in checks],
        "blockers": _json_values(blockers),
    }
