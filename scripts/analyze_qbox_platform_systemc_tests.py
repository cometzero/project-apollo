#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
COMPONENTS_DIR = ROOT / "hsoc-stack/tools/qbox-platform/systemc-components"
TESTS_DIR = ROOT / "hsoc-stack/tools/qbox-platform/tests/components"
TOP_CMAKE = ROOT / "hsoc-stack/tools/qbox-platform/CMakeLists.txt"
ALL_TESTS_CMAKE = TESTS_DIR / "CMakeLists.txt"


ADD_SUBDIR_RE = re.compile(r"^\s*add_subdirectory\(\s*([^) \t]+)")
ADD_TEST_CALL_RE = re.compile(r"add_test\s*\((.*?)\)", re.DOTALL)
GTEST_RE = re.compile(r"\bTEST(?:_F|_P)?\s*\(\s*([A-Za-z0-9_]+)\s*,\s*([A-Za-z0-9_]+)")
PATH_RE = re.compile(
    r"(?<![A-Za-z0-9_./-])"
    r"((?:hsoc-stack/tools|doc|scripts)/[A-Za-z0-9_./:+@-]+)"
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def list_dirs(path: Path) -> list[str]:
    if not path.is_dir():
        return []
    return sorted(p.name for p in path.iterdir() if p.is_dir())


def cmake_arg_tokens(text: str) -> list[str]:
    tokens = re.findall(r'"[^"]*"|[^\s()]+', text)
    return [token.strip("\"'") for token in tokens if token.strip("\"'")]


def cmake_subdirs(path: Path) -> list[str]:
    if not path.is_file():
        return []
    out: list[str] = []
    for line in read_text(path).splitlines():
        match = ADD_SUBDIR_RE.match(line)
        if match:
            out.append(match.group(1).strip().strip("\"'"))
    return out


def cmake_subdir_names(path: Path) -> list[str]:
    return sorted({Path(item).name for item in cmake_subdirs(path)})


def cmake_list_variable(path: Path, variable: str) -> list[str]:
    if not path.is_file():
        return []

    out: list[str] = []
    collecting = False
    set_re = re.compile(rf"^\s*set\s*\(\s*{re.escape(variable)}(?:\s+|$)")
    for raw_line in read_text(path).splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not collecting:
            if not set_re.match(line):
                continue
            collecting = True
            line = set_re.sub("", line, count=1).strip()

        if ")" in line:
            out.extend(cmake_arg_tokens(line.split(")", 1)[0]))
            break
        out.extend(cmake_arg_tokens(line))
    return out


def cmake_test_targets(test_dir: Path) -> list[str]:
    cmake = test_dir / "CMakeLists.txt"
    if not cmake.is_file():
        return []
    out: list[str] = []
    for match in ADD_TEST_CALL_RE.finditer(read_text(cmake)):
        args = cmake_arg_tokens(match.group(1))
        if len(args) >= 2 and args[0] == "NAME":
            out.append(args[1])
        elif args:
            out.append(args[0])
    return out


def gtest_cases(test_dir: Path) -> dict[str, list[str]]:
    cases: dict[str, list[str]] = {}
    for source in sorted(test_dir.glob("*.cc")):
        names: list[str] = []
        for suite, name in GTEST_RE.findall(read_text(source)):
            names.append(name if suite.endswith("Test") else name)
        if names:
            cases[source.name] = names
    return cases


def analyze() -> dict[str, object]:
    components = list_dirs(COMPONENTS_DIR)
    test_dirs = list_dirs(TESTS_DIR)
    top_registered = set(cmake_subdir_names(TOP_CMAKE))
    top_registered.update(cmake_list_variable(TOP_CMAKE, "QBOX_PLATFORM_SYSTEMC_COMPONENT_TESTS"))
    all_tests_listed = set(cmake_subdir_names(ALL_TESTS_CMAKE))

    rows: list[dict[str, object]] = []
    for component in components:
        test_dir = TESTS_DIR / component
        has_tests = test_dir.is_dir()
        rows.append(
            {
                "component": component,
                "has_test_dir": has_tests,
                "top_registered": component in top_registered,
                "listed_in_tests_components": component in all_tests_listed,
                "targets": cmake_test_targets(test_dir) if has_tests else [],
                "gtests": gtest_cases(test_dir) if has_tests else {},
            }
        )

    matching_test_dirs = {name for name in test_dirs if (COMPONENTS_DIR / name).is_dir()}
    return {
        "component_count": len(components),
        "test_dir_count": len(test_dirs),
        "components": rows,
        "top_registered_component_tests": sorted(set(components) & top_registered),
        "source_listed_component_tests": sorted(set(components) & all_tests_listed),
        "components_without_test_dir": sorted(set(components) - matching_test_dirs),
        "component_tests_not_top_registered": sorted(matching_test_dirs - top_registered),
        "non_platform_test_dirs": sorted(set(test_dirs) - set(components)),
    }


def load_report(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return read_text(path)


def check_coverage(report: Path) -> int:
    data = analyze()
    text = load_report(report)
    missing = []
    for row in component_rows(data):
        component = row["component"]
        if f"`{component}`" not in text:
            missing.append(component)

    print(f"component_count={data['component_count']}")
    print(
        "top_registered_component_tests="
        + ",".join(string_list(data, "top_registered_component_tests"))
    )
    print(
        "components_without_test_dir="
        + ",".join(string_list(data, "components_without_test_dir"))
    )
    print(
        "component_tests_not_top_registered="
        + ",".join(string_list(data, "component_tests_not_top_registered"))
    )
    if missing:
        print("missing_report_components=" + ",".join(missing), file=sys.stderr)
        return 1
    print("PASS: markdown report mentions every current systemc-components directory")
    return 0


def check_stale() -> int:
    data = analyze()
    missing = string_list(data, "components_without_test_dir")
    unregistered = string_list(data, "component_tests_not_top_registered")
    extras = string_list(data, "non_platform_test_dirs")

    print(f"component_count={data['component_count']}")
    print(f"test_dir_count={data['test_dir_count']}")
    print("direct_component_test_dirs=" + str(data["component_count"] - len(missing)))
    print("components_without_test_dir=" + ",".join(missing))
    print("component_tests_not_top_registered=" + ",".join(unregistered))
    print("non_platform_test_dirs_ignored=" + ",".join(extras))
    print("PASS: stale scan completed; gaps are reported above")
    return 0


def referenced_paths(markdown: str) -> Iterable[str]:
    for match in PATH_RE.findall(markdown):
        yield match.rstrip(".,);]")


def strip_final_line_suffix(path_text: str) -> str:
    return re.sub(r":\d+$", "", path_text)


def check_links(report: Path) -> int:
    text = load_report(report)
    missing: list[str] = []
    checked: set[str] = set()
    for ref in referenced_paths(text):
        if "*" in ref or "<" in ref or ">" in ref:
            continue
        path_text = strip_final_line_suffix(ref)
        path = ROOT / path_text
        if path_text in checked:
            continue
        checked.add(path_text)
        if not path.exists():
            missing.append(path_text)

    print(f"checked_local_references={len(checked)}")
    if missing:
        print("missing_local_references=" + ",".join(missing), file=sys.stderr)
        return 1
    print("PASS: markdown local file references resolve")
    return 0


def component_rows(data: dict[str, object]) -> list[dict[str, object]]:
    rows = data["components"]
    if not isinstance(rows, list):
        raise TypeError("components is not a list")
    return rows


def string_list(data: dict[str, object], key: str) -> list[str]:
    values = data[key]
    if not isinstance(values, list) or not all(isinstance(item, str) for item in values):
        raise TypeError(f"{key} is not a string list")
    return values


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--markdown", type=Path, help="coverage markdown report path")
    parser.add_argument("--check-coverage", action="store_true")
    parser.add_argument("--check-stale", action="store_true")
    parser.add_argument("--check-links", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.json:
        print(json.dumps(analyze(), indent=2, sort_keys=True))
        return 0

    if args.check_coverage:
        if not args.markdown:
            parser.error("--check-coverage requires --markdown")
        return check_coverage(args.markdown)

    if args.check_stale:
        return check_stale()

    if args.check_links:
        if not args.markdown:
            parser.error("--check-links requires --markdown")
        return check_links(args.markdown)

    parser.error("select one of --json, --check-coverage, --check-stale, --check-links")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
