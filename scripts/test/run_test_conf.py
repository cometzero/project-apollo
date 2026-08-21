from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
import sys
from typing import assert_never, Final, Literal, Protocol

from run_test_fvp_config import fvp_config_assignments
from run_test_profile_network_conf import device_assignments, tap_network_values
from run_test_suite_plan import resolve_plan


type JsonValue = None | bool | int | float | str | list[JsonValue] | dict[str, JsonValue]
type JsonObject = dict[str, JsonValue]
type ConfKind = Literal["current", "functional", "power", "extended", "extra"]

DEFAULT_TEST_OVERALL_TIMEOUT: Final = "10800"
SELECTED_SUITES_ENV: Final = "APOLLO_VALIDATION_TEST_SUITES"
SELECTED_TARGET_ENV: Final = "APOLLO_VALIDATION_TEST_TARGET"
BITBAKE_RECIPE_NAME: Final = re.compile(r"[a-z0-9][a-z0-9+.-]*")


class ConfInputError(ValueError):
    pass


class WriteConfArgs(Protocol):
    build_dir: Path
    machine: str
    image: str
    run_dir: Path
    kind: ConfKind
    test_overall_timeout: str


@dataclass(frozen=True, slots=True)
class ConfRequest:
    root: Path
    build_dir: Path
    machine: str
    run_dir: Path
    kind: ConfKind
    image: str = "nexios-image"
    test_overall_timeout: str = DEFAULT_TEST_OVERALL_TIMEOUT


@dataclass(frozen=True, slots=True)
class PublicRunRequest:
    root: Path
    build_dir: Path
    run_dir: Path


@dataclass(frozen=True, slots=True)
class ConfWriteResult:
    status: str
    conf_path: Path | None
    message: str


@dataclass(frozen=True, slots=True)
class AssignmentScope:
    machine: str
    distro: str
    image: str


def _resolve_under_root(root: Path, path: Path) -> Path:
    if path.is_absolute():
        return path.resolve()
    return (root / path).resolve()


def _protected_build_conf(root: Path, build_dir: Path) -> Path:
    return _resolve_under_root(root, build_dir) / "conf"


def _active_build_conf(root: Path) -> Path:
    return _resolve_under_root(root, Path("build/conf"))


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def _rejection_message(request: ConfRequest) -> str | None:
    run_dir = _resolve_under_root(request.root, request.run_dir)
    project_root = request.root.resolve()
    if run_dir == project_root:
        return f"refusing to write temporary test conf at project root {project_root}"
    active_conf = _active_build_conf(request.root).resolve()
    if run_dir == active_conf or _is_relative_to(run_dir, active_conf):
        return f"refusing to write temporary test conf under protected {active_conf}"
    protected = _protected_build_conf(request.root, request.build_dir).resolve()
    if run_dir == protected or _is_relative_to(run_dir, protected):
        return f"refusing to write temporary test conf under protected {protected}"
    return None


def public_run_rejection_message(request: PublicRunRequest) -> str | None:
    run_dir = _resolve_under_root(request.root, request.run_dir)
    project_root = request.root.resolve()
    active_conf = _active_build_conf(request.root).resolve()
    build_dir = _resolve_under_root(request.root, request.build_dir)
    tests_dir = _resolve_under_root(request.root, Path("build/tests"))
    if build_dir == active_conf or _is_relative_to(build_dir, active_conf):
        return f"refusing to use protected build directory {active_conf}"
    if run_dir == project_root:
        return f"refusing to write public test artifacts at project root {project_root}"
    if run_dir == active_conf or _is_relative_to(run_dir, active_conf):
        return f"refusing to write public test artifacts under protected {active_conf}"
    if run_dir == tests_dir or not _is_relative_to(run_dir, tests_dir):
        return f"refusing to write public test artifacts outside {tests_dir}"
    return None


def _lane_name(kind: ConfKind) -> str:
    match kind:
        case "current":
            return "current"
        case "functional":
            return "functional"
        case "power":
            return "power"
        case "extended":
            return "extended"
        case "extra":
            return "extra"
        case unreachable:
            assert_never(unreachable)


def _suite_assignment(
    kind: ConfKind,
    manifest: JsonObject,
    scope: AssignmentScope,
) -> str | None:
    match kind:
        case "current" | "extra":
            return None
        case "functional" | "power" | "extended":
            selected = os.environ.get(SELECTED_SUITES_ENV)
            if selected is not None:
                loaded = json.loads(selected)
                if not isinstance(loaded, list) or not all(isinstance(item, str) for item in loaded):
                    raise ConfInputError(f"{SELECTED_SUITES_ENV} must be a JSON string list")
                tests = loaded
            else:
                plan = resolve_plan(manifest)
                included = plan.get("included", {})
                if not isinstance(included, dict):
                    return ""
                suite_key = f"validation_{kind}" if kind != "functional" else "validation_current"
                suite = included.get(suite_key, [])
                if not isinstance(suite, list):
                    return ""
                tests = [item for item in suite if isinstance(item, str)]
            suite_value = " ".join(tests)
            return "\n".join(
                _image_scoped_assignments("TEST_SUITES", suite_value, scope)
            )
        case unreachable:
            assert_never(unreachable)


def _scoped_assignments(key: str, value: str, manifest: JsonObject) -> list[str]:
    assignments = [f'{key} = "{value}"']
    machine = manifest.get("machine", "")
    distro = manifest.get("distro", "")
    if isinstance(machine, str) and machine and isinstance(distro, str) and distro:
        assignments.append(f'{key}:{machine}:{distro} = "{value}"')
    return assignments


def _assignment_scope(request: ConfRequest, manifest: JsonObject) -> AssignmentScope:
    if BITBAKE_RECIPE_NAME.fullmatch(request.image) is None:
        raise ConfInputError(f"invalid BitBake recipe name: {request.image}")
    machine = manifest.get("machine", "")
    distro = manifest.get("distro", "")
    return AssignmentScope(
        machine=machine if isinstance(machine, str) else "",
        distro=distro if isinstance(distro, str) else "",
        image=request.image,
    )


def _image_scoped_assignments(
    key: str,
    value: str,
    scope: AssignmentScope,
) -> list[str]:
    assignments = [f'{key} = "{value}"']
    if scope.machine and scope.distro:
        assignments.append(f'{key}:{scope.machine}:{scope.distro} = "{value}"')
        assignments.append(
            f'{key}:{scope.machine}:pn-{scope.image}:{scope.distro} = "{value}"'
        )
    return assignments


def _conf_text(request: ConfRequest, manifest: JsonObject) -> str:
    lane = _lane_name(request.kind)
    scope = _assignment_scope(request, manifest)
    oeqa_dir = _resolve_under_root(request.root, request.run_dir) / "oeqa" / lane
    lines = [
        "# Generated by scripts/test/run_test_manifest.py write-conf.",
        f'TEST_LOG_DIR = "{oeqa_dir / "logs"}"',
        f'OEQA_JSON_RESULT_DIR = "{oeqa_dir / "results"}"',
        f'OEQA_ARTEFACT_DIR = "{oeqa_dir / "artifacts"}"',
        f'TEST_OVERALL_TIMEOUT = "{request.test_overall_timeout}"',
        f'MACHINE = "{request.machine}"',
    ]
    lines += device_assignments(manifest, _scoped_assignments)
    lines += fvp_config_assignments(request.machine)
    tap_values = tap_network_values(request.machine)
    if tap_values is not None:
        tap_assignments, target_ip, server_ip = tap_values
        lines += tap_assignments
        lines += _image_scoped_assignments("TEST_TARGET_IP", target_ip, scope)
        lines += _image_scoped_assignments("TEST_SERVER_IP", server_ip, scope)
    selected_target = os.environ.get(SELECTED_TARGET_ENV)
    if selected_target:
        lines.extend(
            _image_scoped_assignments(
                "TEST_TARGET",
                selected_target,
                scope,
            )
        )
    elif request.kind == "functional":
        lines.extend(
            _image_scoped_assignments(
                "TEST_TARGET",
                "HSOCSingleSessionFVPTarget",
                scope,
            )
        )
    suite = _suite_assignment(request.kind, manifest, scope)
    if suite is not None:
        lines.append(suite)
    return "\n".join(lines) + "\n"


def write_conf(request: ConfRequest, manifest: JsonObject) -> ConfWriteResult:
    run_dir = _resolve_under_root(request.root, request.run_dir)
    rejected = _rejection_message(request)
    if rejected is not None:
        return ConfWriteResult(
            status="rejected",
            conf_path=None,
            message=rejected,
        )
    conf_path = run_dir / "conf" / f"oeqa-{_lane_name(request.kind)}.conf"
    conf_path.parent.mkdir(parents=True, exist_ok=True)
    conf_path.write_text(_conf_text(request, manifest), encoding="utf-8")
    return ConfWriteResult(status="ok", conf_path=conf_path, message=str(conf_path))


def run_write_conf(args: WriteConfArgs) -> int:
    from run_test_manifest import inspect_manifest, ManifestInputs

    request = ConfRequest(
        root=Path.cwd(),
        build_dir=args.build_dir,
        machine=args.machine,
        run_dir=args.run_dir,
        kind=args.kind,
        image=args.image,
        test_overall_timeout=args.test_overall_timeout,
    )
    rejected = _rejection_message(request)
    if rejected is not None:
        print(rejected, file=sys.stderr)
        return 64
    manifest = inspect_manifest(
        ManifestInputs(
            root=request.root,
            build_dir=request.build_dir,
            machine=request.machine,
            image=request.image,
        )
    )
    if manifest.get("status") == "blocked":
        print(manifest.get("message", "manifest inspection blocked"), file=sys.stderr)
        return 2
    result = write_conf(request, manifest)
    print(result.message)
    return 0
