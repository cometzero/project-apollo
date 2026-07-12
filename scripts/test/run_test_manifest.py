#!/usr/bin/env python3

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import re
import sys

from run_test_preflight import PreflightInputs, run_preflight
from run_test_conf import run_write_conf
from run_test_summary import summarize_run
from run_test_suite_plan import resolve_plan


type JsonValue = None | bool | int | float | str | list[JsonValue] | dict[str, JsonValue]
type JsonObject = dict[str, JsonValue]

CONF_PATTERN = re.compile(
    r"^([A-Za-z0-9_]+)(?::([A-Za-z0-9_:+-]+))?\s*(\?\?=|\?=|\+=|=)\s*\"(.*)\"$"
)


@dataclass(frozen=True, slots=True)
class ManifestInputs:
    root: Path
    build_dir: Path
    machine: str


@dataclass(frozen=True, slots=True)
class FvpConfig:
    path: str
    provider: str
    bindir: str
    exe: str
    args: list[str]


def logical_conf_lines(path: Path) -> list[str]:
    lines: list[str] = []
    pending = ""
    for raw in path.read_text(encoding="utf-8").splitlines():
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.endswith("\\"):
            pending += stripped[:-1] + " "
            continue
        lines.append((pending + stripped).strip())
        pending = ""
    if pending:
        lines.append(pending.strip())
    return lines


def parse_conf(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in logical_conf_lines(path):
        match = CONF_PATTERN.match(line)
        if match is None:
            continue
        key, suffix, operator, raw_value = match.groups()
        value = " ".join(raw_value.split())
        if suffix is not None and suffix.endswith("append"):
            values[key] = f"{values.get(key, '')} {value}".strip()
            continue
        if operator == "+=":
            values[key] = f"{values.get(key, '')} {value}".strip()
            continue
        if operator in {"?=", "??="} and key in values:
            continue
        values[key] = value
    return values


def parse_menu_config(path: Path) -> JsonObject:
    menu: JsonObject = {}
    in_menu = False
    for raw in path.read_text(encoding="utf-8").splitlines():
        if raw.strip() == "menu_configuration:":
            in_menu = True
            continue
        if in_menu and raw and not raw.startswith(" "):
            break
        if not in_menu:
            continue
        match = re.match(r"^\s{2}([A-Za-z0-9_]+):\s*(.+)$", raw)
        if match is None:
            continue
        key, raw_value = match.groups()
        menu[key] = parse_yaml_scalar(raw_value)
    return {"menu_configuration": menu}


def parse_yaml_scalar(value: str) -> JsonValue:
    match value:
        case "true":
            return True
        case "false":
            return False
        case _:
            if value.isdigit():
                return int(value)
            return value.strip("\"'")


def read_json_object(path: Path) -> JsonObject:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return data


def str_field(data: JsonObject, key: str) -> str:
    value = data.get(key, "")
    if isinstance(value, str):
        return value
    return str(value)


def words(value: str) -> list[str]:
    return [part for part in value.split() if part]


def json_strings(values: list[str]) -> list[JsonValue]:
    return [value for value in values]


def merged_words(*values: str) -> list[str]:
    merged: list[str] = []
    seen: set[str] = set()
    for value in values:
        for word in words(value):
            if word in seen:
                continue
            merged.append(word)
            seen.add(word)
    return merged


def selected_artifacts(inputs: ManifestInputs, tmpdir: str) -> tuple[Path, Path]:
    tmpdir_name = tmpdir.removeprefix("${TOPDIR}/")
    deploy_dir = inputs.root / inputs.build_dir / tmpdir_name / "deploy/images" / inputs.machine
    testdata = deploy_dir / f"nexios-image-{inputs.machine}.testdata.json"
    fvpconf = deploy_dir / f"nexios-image-{inputs.machine}.fvpconf"
    return testdata, fvpconf


def blocked_missing(inputs: ManifestInputs, path: Path) -> JsonObject:
    return {
        "status": "blocked",
        "reason": "blocked_missing_artifact",
        "machine": inputs.machine,
        "artifact": str(path),
        "message": f"missing required artifact for {inputs.machine}: {path}",
    }


def write_json(path: Path, data: JsonObject) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_fvpconf(path: Path) -> FvpConfig:
    data = read_json_object(path)
    args_value = data.get("args", [])
    args = [str(item) for item in args_value] if isinstance(args_value, list) else []
    return FvpConfig(
        path=str(path),
        provider=str_field(data, "provider"),
        bindir=str_field(data, "fvp-bindir"),
        exe=str_field(data, "exe"),
        args=args,
    )


def inspect_manifest(inputs: ManifestInputs) -> JsonObject:
    local_conf = parse_conf(inputs.root / inputs.build_dir / "conf/local.conf")
    bblayers_conf = parse_conf(inputs.root / inputs.build_dir / "conf/bblayers.conf")
    templateconf = (inputs.root / inputs.build_dir / "conf/templateconf.cfg").read_text(
        encoding="utf-8"
    ).strip()
    config_yaml = parse_menu_config(inputs.root / ".config.yaml")
    tmpdir = local_conf.get("TMPDIR", "${TOPDIR}/tmp_baremetal")
    testdata_path, fvpconf_path = selected_artifacts(inputs, tmpdir)
    if not testdata_path.is_file():
        return blocked_missing(inputs, testdata_path)
    if not fvpconf_path.is_file():
        return blocked_missing(inputs, fvpconf_path)
    testdata = read_json_object(testdata_path)
    distro = local_conf.get("DISTRO", str_field(testdata, "DISTRO"))
    distro_conf = parse_conf(inputs.root / "hsoc-stack/yocto/meta-hsoc-auto-solutions/conf/distro" / f"{distro}.conf")
    fvpconf = load_fvpconf(fvpconf_path)
    return {
        "status": "ok",
        "machine": inputs.machine,
        "distro": distro,
        "rd_aspen_variant": local_conf.get("RD_ASPEN_VARIANT", str_field(testdata, "RD_ASPEN_VARIANT")),
        "pc_cpus_count_default": int(
            local_conf.get("PC_CPUS_COUNT_DEFAULT", "") or str_field(testdata, "PC_CPUS_COUNT_DEFAULT")
        ),
        "tmpdir": tmpdir,
        "extra_image_features": json_strings(
            words(
                f"{local_conf.get('EXTRA_IMAGE_FEATURES', '')} {str_field(testdata, 'EXTRA_IMAGE_FEATURES')}"
            )
        ),
        "image_classes": json_strings(
            words(
                f"{local_conf.get('IMAGE_CLASSES', '')} {str_field(testdata, 'IMAGE_CLASSES')}"
            )
        ),
        "test_suites": json_strings(words(str_field(testdata, "TEST_SUITES"))),
        "hsoc_run_test_skip_suites": json_strings(
            merged_words(
                str_field(testdata, "HSOC_RUN_TEST_SKIP_SUITES"),
                distro_conf.get("HSOC_RUN_TEST_SKIP_SUITES", ""),
            )
        ),
        "hsoc_run_test_skip_extra_lanes": json_strings(
            merged_words(
                str_field(testdata, "HSOC_RUN_TEST_SKIP_EXTRA_LANES"),
                distro_conf.get("HSOC_RUN_TEST_SKIP_EXTRA_LANES", ""),
            )
        ),
        "hsoc_run_test_skip_reason": str_field(testdata, "HSOC_RUN_TEST_SKIP_REASON") or distro_conf.get("HSOC_RUN_TEST_SKIP_REASON", ""),
        "test_fvp_devices": json_strings(
            words(
                distro_conf.get("TEST_FVP_DEVICES", "")
                or str_field(testdata, "TEST_FVP_DEVICES")
            )
        ),
        "test_target": str_field(testdata, "TEST_TARGET"),
        "test_target_ip": str_field(testdata, "TEST_TARGET_IP"),
        "fvp_exe": str_field(testdata, "FVP_EXE") or fvpconf.exe,
        "bblayers": json_strings(words(bblayers_conf.get("BBLAYERS", ""))),
        "templateconf": templateconf,
        "config_yaml": config_yaml,
        "testdata_path": str(testdata_path),
        "fvpconf": {
            "path": fvpconf.path,
            "provider": fvpconf.provider,
            "bindir": fvpconf.bindir,
            "exe": fvpconf.exe,
            "args": json_strings(fvpconf.args),
        },
    }


def run_summarize(args: argparse.Namespace) -> int:
    result, exit_code = summarize_run(args.run_dir)
    write_json(args.out, result)
    print(args.out)
    return exit_code


def run_inspect(args: argparse.Namespace) -> int:
    inputs = ManifestInputs(root=Path.cwd(), build_dir=args.build_dir, machine=args.machine)
    result = inspect_manifest(inputs)
    write_json(args.out, result)
    if result.get("status") == "blocked":
        print(result["message"], file=sys.stderr)
        return 2
    print(args.out)
    return 0


def run_plan(args: argparse.Namespace) -> int:
    inputs = ManifestInputs(root=Path.cwd(), build_dir=args.build_dir, machine=args.machine)
    result = resolve_plan(inspect_manifest(inputs))
    write_json(args.out, result)
    if result.get("status") == "blocked":
        print(result["message"], file=sys.stderr)
        return 2
    print(args.out)
    return 0


def run_preflight_command(args: argparse.Namespace) -> int:
    inputs = PreflightInputs(root=Path.cwd(), build_dir=args.build_dir, machine=args.machine)
    result = run_preflight(inputs)
    write_json(args.out, result)
    if result.get("status") == "blocked":
        print(f"preflight blocked for {args.machine}", file=sys.stderr)
        return 2
    print(args.out)
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspect Apollo FVP validation inputs.")
    subparsers = parser.add_subparsers(dest="subcommand", required=True)
    inspect = subparsers.add_parser("inspect")
    inspect.add_argument("--build-dir", type=Path, default=Path("build"))
    inspect.add_argument("--machine", default="apollo-fvp")
    inspect.add_argument("--out", type=Path, required=True)
    inspect.set_defaults(func=run_inspect)
    plan = subparsers.add_parser("plan")
    plan.add_argument("--build-dir", type=Path, default=Path("build"))
    plan.add_argument("--machine", default="apollo-fvp")
    plan.add_argument("--out", type=Path, required=True)
    plan.set_defaults(func=run_plan)
    preflight = subparsers.add_parser("preflight")
    preflight.add_argument("--build-dir", type=Path, default=Path("build"))
    preflight.add_argument("--machine", default="apollo-fvp")
    preflight.add_argument("--out", type=Path, required=True)
    preflight.set_defaults(func=run_preflight_command)
    summarize = subparsers.add_parser("summarize")
    summarize.add_argument("--run-dir", type=Path, required=True)
    summarize.add_argument("--out", type=Path, required=True)
    summarize.set_defaults(func=run_summarize)
    write_conf = subparsers.add_parser("write-conf")
    write_conf.add_argument("--build-dir", type=Path, default=Path("build"))
    write_conf.add_argument("--machine", default="apollo-fvp")
    write_conf.add_argument("--run-dir", type=Path, required=True)
    write_conf.add_argument(
        "--kind",
        choices=("current", "functional", "power", "extended", "extra"),
        required=True,
    )
    write_conf.add_argument("--test-overall-timeout", default="10800")
    write_conf.add_argument("--out", type=Path)
    write_conf.set_defaults(func=run_write_conf)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
