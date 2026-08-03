from __future__ import annotations

import json
import fcntl
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
WRAPPER = ROOT / "scripts/build/run_gic720ae_qbox_platform_tests.py"


def make_sources(tmp_path: Path) -> tuple[Path, Path, Path]:
    tmp_path.mkdir(parents=True, exist_ok=True)
    sources = (
        tmp_path / "qbox-platform",
        tmp_path / "qbox",
        tmp_path / "qemu",
    )
    for source in sources:
        source.mkdir()
        (source / "CMakeLists.txt").write_text("project(fixture)\n", encoding="utf-8")
    return sources


def make_fake_tools(
    tmp_path: Path, *, tests: tuple[str, ...] = ("alpha-tests",)
) -> Path:
    tools = tmp_path / "tools"
    tools.mkdir()
    cmake = tools / "cmake"
    cmake.write_text(
        """#!/usr/bin/env python3
import os
from pathlib import Path
import sys
import time

log = Path(os.environ["FAKE_TOOL_LOG"])
with log.open("a", encoding="utf-8") as handle:
    handle.write("cmake " + repr(sys.argv[1:]) + "\\n")
if os.environ.get("FAKE_CMAKE_HANG") == "1":
    Path(os.environ["FAKE_HANG_PID"]).write_text(str(os.getpid()), encoding="utf-8")
    time.sleep(60)
args = sys.argv[1:]
if "--build" in args:
    build = Path(args[args.index("--build") + 1])
    target = args[args.index("--target") + 1]
    executable = build / "tests" / target
    executable.parent.mkdir(parents=True, exist_ok=True)
    executable.write_text(
        "#!/usr/bin/env python3\\n"
        "import json, os, pathlib, sys\\n"
        "pathlib.Path(os.environ['FAKE_EXEC_LOG']).write_text("
        "json.dumps(sys.argv[1:]), encoding='utf-8')\\n",
        encoding="utf-8",
    )
    executable.chmod(0o755)
    raise SystemExit(0)
build = Path(args[args.index("-B") + 1])
source = Path(args[args.index("-S") + 1]).resolve()
values = {
    "BUILD_TESTING": ("BOOL", "ON"),
    "CMAKE_HOME_DIRECTORY": ("INTERNAL", str(source)),
}
for arg in args:
    if not arg.startswith("-D") or "=" not in arg:
        continue
    key, value = arg[2:].split("=", 1)
    values[key] = ("PATH" if key.endswith("_DIR") else "UNINITIALIZED", value)
build.mkdir(parents=True, exist_ok=True)
(build / "CMakeCache.txt").write_text(
    "".join(f"{key}:{kind}={value}\\n" for key, (kind, value) in values.items()),
    encoding="utf-8",
)
""",
        encoding="utf-8",
    )
    cmake.chmod(0o755)
    ctest = tools / "ctest"
    ctest.write_text(
        """#!/usr/bin/env python3
import json
import os
from pathlib import Path
import sys

build = Path(sys.argv[sys.argv.index("--test-dir") + 1])
names = json.loads(os.environ["FAKE_TEST_NAMES"])
tests = [
    {
        "name": name,
        **({} if os.environ.get("FAKE_OMIT_COMMANDS") == "1" else {
            "command": [str(build / "tests" / name)]
        }),
        "properties": [],
    }
    for name in names
]
print(json.dumps({"kind": "ctestInfo", "version": {"major": 1, "minor": 0}, "tests": tests}))
""",
        encoding="utf-8",
    )
    ctest.chmod(0o755)
    git = tools / "git"
    git.write_text(
        """#!/usr/bin/env python3
import os
import sys

if "rev-parse" in sys.argv:
    print("0123456789abcdef0123456789abcdef01234567")
elif "status" in sys.argv and os.environ.get("FAKE_GIT_DIRTY") == "1":
    print(" M fixture")
""",
        encoding="utf-8",
    )
    git.chmod(0o755)
    return tools


def run_wrapper(
    tmp_path: Path,
    arguments: list[str],
    *,
    tests: tuple[str, ...] = ("alpha-tests",),
    dirty: bool = False,
    omit_commands: bool = False,
    hang: bool = False,
) -> subprocess.CompletedProcess[str]:
    qbox_platform, qbox, qemu = make_sources(tmp_path)
    tools = make_fake_tools(tmp_path, tests=tests)
    build = tmp_path / "gic720ae-qbox-platform-tests"
    env = os.environ.copy()
    env.update(
        {
            "PATH": f"{tools}:{env['PATH']}",
            "FAKE_TOOL_LOG": str(tmp_path / "tools.log"),
            "FAKE_EXEC_LOG": str(tmp_path / "exec.json"),
            "FAKE_TEST_NAMES": json.dumps(tests),
            "FAKE_GIT_DIRTY": "1" if dirty else "0",
            "FAKE_OMIT_COMMANDS": "1" if omit_commands else "0",
            "FAKE_CMAKE_HANG": "1" if hang else "0",
            "FAKE_HANG_PID": str(tmp_path / "hang.pid"),
        }
    )
    command = [
        sys.executable,
        str(WRAPPER),
        "--build-dir",
        str(build),
        "--qbox-platform-source",
        str(qbox_platform),
        "--qbox-source",
        str(qbox),
        "--qemu-source",
        str(qemu),
        *arguments,
    ]
    return subprocess.run(command, cwd=ROOT, env=env, text=True, capture_output=True)


def test_list_configures_isolated_local_qemu_cache_and_is_deterministic(
    tmp_path: Path,
) -> None:
    # Given: three explicit sources and an intentionally dirty source state.
    output = tmp_path / "result.json"

    # When: the wrapper lists an unsorted CTest registry.
    completed = run_wrapper(
        tmp_path,
        ["--list", "--output", str(output)],
        tests=("zeta-tests", "alpha-tests"),
        dirty=True,
    )

    # Then: the dedicated cache and evidence retain local provenance and sorted tests.
    assert completed.returncode == 0, completed.stderr
    result = json.loads(output.read_text(encoding="utf-8"))
    assert result["tests"] == ["alpha-tests", "zeta-tests"]
    assert result["cache"]["QBOX_USE_SYSTEM_LIBQEMU"] == "OFF"
    assert result["cache"]["BUILD_TESTING"] == "ON"
    assert result["local_libqemu"]["source_matches_cache"] is True
    assert all(source["dirty"] is True for source in result["sources"].values())


def test_component_arguments_reach_registered_executable_and_hash_is_recorded(
    tmp_path: Path,
) -> None:
    # Given: a registered component test and two conditional contract arguments.
    output = tmp_path / "component.json"

    # When: the wrapper builds and executes the CTest-registered binary.
    completed = run_wrapper(
        tmp_path,
        [
            "--target",
            "alpha-tests",
            "--ctest-regex",
            "^alpha-tests$",
            "--ctest-argument",
            "mode=single",
            "--ctest-argument",
            "cpu_count=5",
            "--output",
            str(output),
        ],
    )

    # Then: arguments and the exact executable digest are evidence.
    assert completed.returncode == 0, completed.stderr
    result = json.loads(output.read_text(encoding="utf-8"))
    assert result["ctest_arguments"] == ["mode=single", "cpu_count=5"]
    assert result["target_executable"]["sha256"]
    assert json.loads((tmp_path / "exec.json").read_text()) == [
        "mode=single",
        "cpu_count=5",
    ]


def test_list_accepts_unbuilt_ctest_registrations_without_commands(
    tmp_path: Path,
) -> None:
    # Given: CTest registrations whose unbuilt executables have no command field.

    # When: the wrapper lists them without requesting a build.
    completed = run_wrapper(tmp_path, ["--list"], omit_commands=True)

    # Then: registered test names are sufficient for deterministic list evidence.
    assert completed.returncode == 0, completed.stderr


def test_rejects_malformed_argument_and_command_injection(tmp_path: Path) -> None:
    # Given: values that are not a key=value contract or safe CTest selector.
    cases = (
        ["--target", "alpha-tests", "--ctest-argument", "missing-value"],
        ["--target", "alpha;touch-pwned"],
        ["--target", "alpha-tests", "--ctest-regex", "alpha;touch-pwned"],
    )

    # When: each malformed boundary value is parsed.
    completed = [
        run_wrapper(tmp_path / str(index), case) for index, case in enumerate(cases)
    ]

    # Then: every invocation fails before a tool can interpret injected text.
    assert all(result.returncode == 2 for result in completed)


def test_rejects_production_build_tree_and_stale_system_qemu_cache(
    tmp_path: Path,
) -> None:
    # Given: the production build path and an isolated cache claiming system libqemu.
    production = subprocess.run(
        [
            sys.executable,
            str(WRAPPER),
            "--list",
            "--build-dir",
            str(ROOT / "build/local-apollo-qvp/work/qbox-platform"),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    stale_dir = tmp_path / "gic720ae-qbox-platform-tests"
    stale_dir.mkdir()
    (stale_dir / "CMakeCache.txt").write_text(
        "QBOX_USE_SYSTEM_LIBQEMU:BOOL=ON\n",
        encoding="utf-8",
    )

    # When: the stale cache is offered to an otherwise valid list invocation.
    stale = run_wrapper(tmp_path, ["--list"])

    # Then: neither production nor stale/system cache state is reconfigured.
    assert production.returncode == 2
    assert stale.returncode == 2


def test_zero_registered_tests_is_a_failure(tmp_path: Path) -> None:
    # Given: CTest exits successfully but reports no registered tests.

    # When: the wrapper lists that misleading registry.
    completed = run_wrapper(tmp_path, ["--list"], tests=())

    # Then: zero tests is a hard failure.
    assert completed.returncode == 1


def test_concurrent_invocation_fails_without_touching_tools(tmp_path: Path) -> None:
    # Given: another wrapper invocation owns the dedicated directory lock.
    lock_path = tmp_path / ".gic720ae-qbox-platform-tests.lock"
    with lock_path.open("w", encoding="utf-8") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)

        # When: a second invocation requests the same build directory.
        completed = run_wrapper(tmp_path, ["--list"])

    # Then: it fails before configure and leaves no tool invocation.
    assert completed.returncode == 2
    assert not (tmp_path / "tools.log").exists()


def test_hung_configure_is_terminated_as_a_process_group(tmp_path: Path) -> None:
    # Given: a configure process that never completes by itself.

    # When: the wrapper's one-second command timeout expires.
    completed = run_wrapper(tmp_path, ["--list", "--timeout", "1"], hang=True)
    pid = int((tmp_path / "hang.pid").read_text(encoding="utf-8"))

    # Then: the wrapper reports failure and no child process survives.
    assert completed.returncode == 1
    assert not Path(f"/proc/{pid}").exists()
