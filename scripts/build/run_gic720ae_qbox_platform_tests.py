#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
# noqa: SIZE_OK - Task 6 requires one auditable wrapper for configure, provenance, and CTest.

# ─── How to run ───
# 1. Install uv (if not installed):
#      curl -LsSf https://astral.sh/uv/install.sh | sh
# 2. Run:
#      uv run scripts/build/run_gic720ae_qbox_platform_tests.py --list
# 3. Or make executable and run:
#      chmod +x scripts/build/run_gic720ae_qbox_platform_tests.py
#      ./scripts/build/run_gic720ae_qbox_platform_tests.py --list
# ──────────────────

from __future__ import annotations

import argparse
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
from typing import Final

ROOT: Final = Path(__file__).resolve().parents[2]
BUILD_NAME: Final = "gic720ae-qbox-platform-tests"
DEFAULT_BUILD: Final = ROOT / f"build/{BUILD_NAME}"
PRODUCTION_BUILD: Final = ROOT / "build/local-apollo-qvp/work/qbox-platform"
SAFE_TARGET: Final = re.compile(r"^[A-Za-z0-9_.+-]+$")
SAFE_REGEX: Final = re.compile(r"^[A-Za-z0-9_.+*?^$(){}\[\]|\\-]+$")
SAFE_ARGUMENT: Final = re.compile(r"^[A-Za-z_][A-Za-z0-9_.-]*=[A-Za-z0-9_./:=,+@%-]+$")


@dataclass(frozen=True, slots=True)
class Options:
    build: Path
    platform: Path
    qbox: Path
    qemu: Path
    list_tests: bool
    target: str | None
    test_regex: str | None
    test_arguments: tuple[str, ...]
    output: Path
    jobs: int
    timeout: int


class WrapperError(RuntimeError):
    def __init__(self, message: str, exit_code: int = 1) -> None:
        super().__init__(message)
        self.exit_code = exit_code


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_cache(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line and not line.startswith(("#", "//")) and "=" in line:
            key_type, value = line.split("=", 1)
            values[key_type.split(":", 1)[0]] = value
    return values


def expected_cache(options: Options) -> dict[str, str]:
    return {
        "BUILD_TESTING": "ON",
        "CMAKE_HOME_DIRECTORY": str(options.platform),
        "QBOX_CORE_SOURCE_DIR": str(options.qbox),
        "QBOX_QEMU_SOURCE_DIR": str(options.qemu),
        "QEMU_SOURCE_DIR": str(options.qemu),
        "FETCHCONTENT_SOURCE_DIR_QEMU": str(options.qemu),
        "FETCHCONTENT_SOURCE_DIR_LIBQEMU": str(options.qemu),
        "qemu_SOURCE_DIR": str(options.qemu),
        "libqemu_SOURCE_DIR": str(options.qemu),
        "QBOX_USE_SYSTEM_LIBQEMU": "OFF",
    }


def check_cache(cache: dict[str, str], options: Options) -> None:
    mismatches = [
        f"{key}={cache.get(key)!r}, expected {value!r}"
        for key, value in expected_cache(options).items()
        if cache.get(key) != value
    ]
    if mismatches:
        raise WrapperError("stale or unsafe CMake cache: " + "; ".join(mismatches), 2)


def source_state(path: Path) -> dict[str, str | bool]:
    head = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "HEAD"],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).stdout.strip()
    status = subprocess.run(
        ["git", "-C", str(path), "status", "--porcelain=v1"],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).stdout
    return {
        "path": str(path),
        "head": head,
        "dirty": bool(status),
        "status_sha256": hashlib.sha256(status.encode()).hexdigest(),
    }


@contextmanager
def exclusive_build(lock_path: Path) -> Iterator[None]:
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("w", encoding="utf-8") as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise WrapperError(
                f"build directory is already in use: {lock_path}", 2
            ) from error
        yield


def run(command: Sequence[str], options: Options, log_path: Path) -> str:
    process = subprocess.Popen(
        list(command),
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    try:
        output, _ = process.communicate(timeout=options.timeout)
    except subprocess.TimeoutExpired as error:
        os.killpg(process.pid, signal.SIGTERM)
        try:
            output, _ = process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            output, _ = process.communicate()
        raise WrapperError(
            f"command timed out after {options.timeout}s: {command[0]}"
        ) from error
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(
            json.dumps({"command": list(command), "returncode": process.returncode})
        )
        handle.write("\n" + output)
        if output and not output.endswith("\n"):
            handle.write("\n")
    if process.returncode:
        raise WrapperError(f"command failed ({process.returncode}): {command[0]}")
    return output


def inventory(
    options: Options, log_path: Path
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    output = run(
        ("ctest", "--test-dir", str(options.build), "-N", "--show-only=json-v1"),
        options,
        log_path,
    )
    try:
        decoded = json.loads(output)
        tests = tuple(
            (item["name"], tuple(item.get("command", ()))) for item in decoded["tests"]
        )
    except (json.JSONDecodeError, KeyError, TypeError) as error:
        raise WrapperError("CTest inventory is malformed") from error
    if not tests:
        raise WrapperError("CTest reported zero registered tests")
    return tuple(sorted(tests))


def configure_command(options: Options) -> tuple[str, ...]:
    qemu = str(options.qemu)
    return (
        "cmake",
        "-S",
        str(options.platform),
        "-B",
        str(options.build),
        "-DBUILD_TESTING=ON",
        "-DQBOX_USE_SYSTEM_LIBQEMU=OFF",
        f"-DQBOX_CORE_SOURCE_DIR={options.qbox}",
        f"-DQBOX_QEMU_SOURCE_DIR={qemu}",
        f"-DQEMU_SOURCE_DIR={qemu}",
        f"-DFETCHCONTENT_SOURCE_DIR_QEMU={qemu}",
        f"-DFETCHCONTENT_SOURCE_DIR_LIBQEMU={qemu}",
        f"-Dqemu_SOURCE_DIR={qemu}",
        f"-Dlibqemu_SOURCE_DIR={qemu}",
        f"-DLIBQEMU_GIT=file://{qemu}",
    )


def parse_options(argv: Sequence[str] | None = None) -> Options:
    parser = argparse.ArgumentParser(
        description="Run isolated GIC-720AE QBox component tests"
    )
    parser.add_argument("--build-dir", type=Path, default=DEFAULT_BUILD)
    parser.add_argument(
        "--qbox-platform-source",
        type=Path,
        default=ROOT / "hsoc-stack/tools/qbox-platform",
    )
    parser.add_argument(
        "--qbox-source", type=Path, default=ROOT / "hsoc-stack/tools/qbox"
    )
    parser.add_argument(
        "--qemu-source", type=Path, default=ROOT / "hsoc-stack/tools/qemu"
    )
    parser.add_argument("--list", dest="list_tests", action="store_true")
    parser.add_argument("--target")
    parser.add_argument("--ctest-regex")
    parser.add_argument("--ctest-argument", action="append", default=[])
    parser.add_argument("--output", type=Path)
    parser.add_argument("--jobs", type=int, default=max(1, (os.cpu_count() or 2) // 2))
    parser.add_argument("--timeout", type=int, default=1800)
    args = parser.parse_args(argv)
    build = args.build_dir.resolve()
    platform, qbox, qemu = (
        path.resolve()
        for path in (args.qbox_platform_source, args.qbox_source, args.qemu_source)
    )
    sources = (platform, qbox, qemu)
    if build.name != BUILD_NAME or build == PRODUCTION_BUILD.resolve():
        parser.error(f"--build-dir must be an isolated {BUILD_NAME} directory")
    if any(build == source or source in build.parents for source in sources):
        parser.error("--build-dir must not be a source tree")
    if len(set(sources)) != 3 or any(
        not (source / "CMakeLists.txt").is_file() for source in sources
    ):
        parser.error(
            "qbox-platform, qbox, and qemu must be distinct CMake source trees"
        )
    if args.list_tests == (args.target is not None):
        parser.error("select exactly one of --list or --target")
    if args.target is not None and SAFE_TARGET.fullmatch(args.target) is None:
        parser.error("--target contains unsafe characters")
    test_regex = args.ctest_regex or (
        f"^{re.escape(args.target)}$" if args.target is not None else None
    )
    if test_regex is not None and SAFE_REGEX.fullmatch(test_regex) is None:
        parser.error("--ctest-regex contains unsafe characters")
    if any(SAFE_ARGUMENT.fullmatch(item) is None for item in args.ctest_argument):
        parser.error("--ctest-argument must be a safe key=value")
    if args.list_tests and args.ctest_argument:
        parser.error("--ctest-argument requires --target")
    if args.jobs <= 0 or args.timeout <= 0:
        parser.error("--jobs and --timeout must be positive")
    output = (args.output or build / "wrapper-result.json").resolve()
    return Options(
        build,
        platform,
        qbox,
        qemu,
        args.list_tests,
        args.target,
        test_regex,
        tuple(args.ctest_argument),
        output,
        args.jobs,
        args.timeout,
    )


def execute(options: Options) -> None:
    options.build.mkdir(parents=True, exist_ok=True)
    options.output.parent.mkdir(parents=True, exist_ok=True)
    log_path = options.output.with_suffix(".command.log")
    log_path.write_text("", encoding="utf-8")
    cache_path = options.build / "CMakeCache.txt"
    if cache_path.exists():
        check_cache(read_cache(cache_path), options)
    commands = [list(configure_command(options))]
    run(commands[0], options, log_path)
    cache = read_cache(cache_path)
    check_cache(cache, options)
    tests = inventory(options, log_path)
    target_record = None
    if options.target is not None:
        build_command = [
            "cmake",
            "--build",
            str(options.build),
            "--target",
            options.target,
            "--parallel",
            str(options.jobs),
        ]
        commands.append(build_command)
        run(build_command, options, log_path)
        tests = inventory(options, log_path)
        selected = tuple(
            test for test in tests if re.search(options.test_regex or "", test[0])
        )
        if len(selected) != 1:
            raise WrapperError(
                f"CTest selector matched {len(selected)} tests, expected one"
            )
        if not selected[0][1]:
            raise WrapperError("built CTest registration has no executable command")
        executable = Path(selected[0][1][0]).resolve()
        if not executable.is_file():
            raise WrapperError(f"CTest executable is missing: {executable}")
        target_record = {"path": str(executable), "sha256": sha256(executable)}
        test_command = (
            [*selected[0][1], *options.test_arguments]
            if options.test_arguments
            else [
                "ctest",
                "--test-dir",
                str(options.build),
                "-R",
                options.test_regex or "",
                "--output-on-failure",
                "--no-tests=error",
            ]
        )
        commands.append(test_command)
        run(test_command, options, log_path)
    sources = {
        "qbox_platform": source_state(options.platform),
        "qbox": source_state(options.qbox),
        "qemu": source_state(options.qemu),
    }
    libqemu = (
        options.build / "_deps/libqemu-build/qemu-prefix/lib/libqemu-system-aarch64.so"
    )
    result = {
        "schema_version": 1,
        "status": "pass",
        "mode": "list" if options.list_tests else "test",
        "build_dir": str(options.build),
        "cache_file": {"path": str(cache_path), "sha256": sha256(cache_path)},
        "cache": cache,
        "sources": sources,
        "local_libqemu": {
            "resolved_path": str(libqemu),
            "exists": libqemu.is_file(),
            "sha256": sha256(libqemu) if libqemu.is_file() else None,
            "source_path": str(options.qemu),
            "source_head": sources["qemu"]["head"],
            "source_matches_cache": cache["libqemu_SOURCE_DIR"] == str(options.qemu),
        },
        "tests": [test[0] for test in tests],
        "ctest_regex": options.test_regex,
        "ctest_arguments": list(options.test_arguments),
        "target_executable": target_record,
        "commands": commands,
        "command_log": str(log_path),
    }
    options.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(options.output)


def main() -> int:
    try:
        options = parse_options()
        with exclusive_build(options.build.parent / f".{BUILD_NAME}.lock"):
            execute(options)
    except WrapperError as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return error.exit_code
    except subprocess.CalledProcessError as error:
        print(f"FAIL: git command failed: {error.stderr.strip()}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
