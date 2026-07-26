from __future__ import annotations

from pathlib import Path
import re
import subprocess
from typing import Iterable, Mapping, TypedDict

from local_debug_components import Component, ComponentRecord


class ElfSections(TypedDict):
    symtab: bool
    debug_info: bool
    debug_line: bool


def run_text(command: list[str]) -> str:
    return subprocess.check_output(command, text=True, errors="replace")


def first_existing(root: Path, patterns: Iterable[str]) -> Path | None:
    for pattern in patterns:
        for match in sorted(root.glob(pattern)):
            if match.is_file():
                return match.resolve()
    return None


def resolve_elf(root: Path, local_build: Path, component: Component) -> Path | None:
    elf = first_existing(local_build, component.elf_candidates)
    if elf is not None:
        return elf
    return first_existing(root, component.workspace_candidates)


def elf_sections(elf: Path) -> ElfSections:
    try:
        output = run_text(["readelf", "-S", str(elf)])
    except (OSError, subprocess.CalledProcessError):
        return {"symtab": False, "debug_info": False, "debug_line": False}
    return {
        "symtab": ".symtab" in output,
        "debug_info": ".debug_info" in output,
        "debug_line": ".debug_line" in output,
    }


def elf_arch(elf: Path) -> str:
    try:
        output = run_text(["file", "--brief", str(elf)]).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"
    if "ELF 32-bit" in output and "ARM" in output:
        return "arm"
    if "ELF 64-bit" in output and "aarch64" in output:
        return "aarch64"
    if "ELF 64-bit" in output and "x86-64" in output:
        return "x86_64"
    return "unknown"


def defined_symbols(elf: Path) -> dict[str, int]:
    symbols: dict[str, int] = {}
    try:
        output = run_text(["nm", "-n", "--defined-only", str(elf)])
    except (OSError, subprocess.CalledProcessError):
        return symbols
    for line in output.splitlines():
        fields = line.split()
        if len(fields) < 3 or fields[1].lower() not in {"t", "w"}:
            continue
        try:
            symbols.setdefault(fields[2], int(fields[0], 16))
        except ValueError:
            continue
    return symbols


def elf_build_id(elf: Path) -> str | None:
    try:
        output = run_text(["readelf", "-n", str(elf)])
    except (OSError, subprocess.CalledProcessError):
        return None
    match = re.search(r"Build ID:\s*([0-9a-fA-F]+)", output)
    return match.group(1).lower() if match else None


def elf_text_address(elf: Path) -> str:
    try:
        output = run_text(["readelf", "-WS", str(elf)])
    except (OSError, subprocess.CalledProcessError):
        return "0x0"
    match = re.search(r"\]\s+\.text\s+\S+\s+([0-9a-fA-F]+)\s+", output)
    return f"0x{int(match.group(1), 16):x}" if match else "0x0"


def symbol_source_locations(
    elf: Path, symbols: Mapping[str, str]
) -> dict[str, str]:
    locations: dict[str, str] = {}
    for name, address in symbols.items():
        try:
            output = run_text(["addr2line", "-e", str(elf), address]).strip()
        except (OSError, subprocess.CalledProcessError):
            continue
        if output and not output.startswith("??"):
            locations[name] = output
    return locations


def gdb_quote(path: Path) -> str:
    escaped = str(path).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def qbox_context_commands(root: Path, component: Component) -> list[str]:
    roots = [
        str((root / source).resolve())
        for source in component.source_roots
        if (root / source).exists()
    ]
    return [
        "python",
        "import gdb",
        "import os",
        "import time",
        "",
        "class QBoxContext:",
        "    def __init__(self, roots):",
        "        self.roots = tuple(os.path.realpath(root) + os.sep for root in roots)",
        "        self.stopped_at_ns = None",
        "",
        "    def on_stop(self, _event):",
        "        self.stopped_at_ns = time.monotonic_ns()",
        "        for thread in gdb.selected_inferior().threads():",
        "            try:",
        "                thread.switch()",
        "                frame = gdb.newest_frame()",
        "            except gdb.error:",
        "                continue",
        "            while frame is not None:",
        "                sal = frame.find_sal()",
        "                if sal.symtab is not None:",
        "                    source = os.path.realpath(sal.symtab.fullname())",
        "                    if source.startswith(self.roots):",
        "                        frame.select()",
        '                        gdb.write("\\nQBox source context:\\n")',
        '                        gdb.execute("frame")',
        '                        gdb.execute("list")',
        "                        return",
        "                frame = frame.older()",
        '        gdb.write("\\nNo source-backed QBox frame; host thread heads:\\n")',
        '        gdb.execute("thread apply all bt 3")',
        "",
        "    def compensate(self):",
        "        if self.stopped_at_ns is None:",
        "            return",
        "        elapsed_ns = time.monotonic_ns() - self.stopped_at_ns",
        "        self.stopped_at_ns = None",
        "        adjusted = set()",
        '        symbols = list(gdb.lookup_static_symbols("timers_state"))',
        '        global_symbol = gdb.lookup_global_symbol("timers_state")',
        "        if global_symbol is not None:",
        "            symbols.append(global_symbol)",
        "        for symbol in symbols:",
        "            try:",
        "                state = symbol.value()",
        '                if int(state["cpu_ticks_enabled"]) == 0:',
        "                    continue",
        '                offset = state["cpu_clock_offset"]',
        "                address = int(offset.address)",
        "                if address in adjusted:",
        "                    continue",
        "                offset.assign(int(offset) - elapsed_ns)",
        "                adjusted.add(address)",
        "            except (gdb.error, TypeError, ValueError):",
        "                continue",
        "        if adjusted:",
        "            gdb.write(",
        '                "QBox debugger pause compensation: "',
        '                f"{elapsed_ns / 1_000_000_000:.3f}s across "',
        '                f"{len(adjusted)} QEMU clock(s)\\n"',
        "            )",
        "",
        "class QBoxCompensate(gdb.Command):",
        "    def __init__(self, context):",
        '        super().__init__("qbox-compensate-pause", gdb.COMMAND_SUPPORT)',
        "        self.context = context",
        "",
        "    def invoke(self, _argument, _from_tty):",
        "        self.context.compensate()",
        "",
        f"qbox_context = QBoxContext({roots!r})",
        "qbox_compensate = QBoxCompensate(qbox_context)",
        "gdb.events.stop.connect(qbox_context.on_stop)",
        "end",
        "define hook-continue",
        "  qbox-compensate-pause",
        "end",
    ]


def shared_library_paths(root: Path, local_build: Path) -> tuple[Path, ...]:
    qbox_build = local_build / "work/qbox-platform"
    candidates = {
        qbox_build,
        qbox_build / "qbox-core",
        root
        / "build/tmp_baremetal/sysroots-components/x86_64/"
        "qbox-libqemu-native/usr/lib",
    }
    candidates.update(
        root.glob(
            "build/tmp_baremetal/work/x86_64-linux/qbox-libqemu-native/"
            "*/recipe-sysroot-native/usr/lib"
        )
    )
    candidates.update(path.parent for path in qbox_build.glob("*.so"))
    return tuple(sorted(path.resolve() for path in candidates if path.is_dir()))


def write_gdb_script(
    out: Path,
    root: Path,
    debug_dir: Path,
    component: Component,
    elf: Path,
    symbols: Mapping[str, int],
    solib_paths: tuple[Path, ...],
) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "set pagination off",
        "set confirm off",
        "set breakpoint pending on",
        "set auto-solib-add on",
        "set debuginfod enabled off",
        f"set debug-file-directory {debug_dir}",
        f"# {component.label}",
        f"# Debug target: {component.target}",
    ]
    if solib_paths:
        joined = ":".join(str(path) for path in solib_paths)
        lines.append(f"set solib-search-path {joined}")
        if component.debugger == "gdb":
            lines.append(f"set environment LD_LIBRARY_PATH {joined}")
            lines.append("set sysroot /")
    for source in component.source_roots:
        source_path = root / source
        if source_path.exists():
            lines.append(f"directory {gdb_quote(source_path)}")
    lines.append(f"file {gdb_quote(elf)}")
    if component.runtime_text_address is not None:
        linked_text_address = int(elf_text_address(elf), 16)
        load_offset = component.runtime_text_address - linked_text_address
        lines.append(
            f"symbol-file -o {load_offset:#x} {gdb_quote(elf)}"
        )
    lines.append("info files")
    available_default_symbols = [
        name for name in component.default_symbols if name in symbols
    ]
    entry_symbols = (
        available_default_symbols[:1]
        if component.name == "qbox-host"
        else available_default_symbols
    )
    for name in entry_symbols:
        breakpoint = "tbreak" if component.name == "qbox-host" else "break"
        lines.extend(
            (f"info address {name}", f"info line {name}", f"{breakpoint} {name}")
        )
    if entry_symbols:
        lines.append(f"list {entry_symbols[0]}")
    if component.name == "qbox-host":
        lines.extend(qbox_context_commands(root, component))
    else:
        lines.extend(
            (
                "define hook-stop",
                "  echo \\nStopped at ",
                "  info symbol $pc",
                "  info line *$pc",
                "  list *$pc",
                "end",
            )
        )
    if component.debugger == "gdb-multiarch":
        lines.extend(("", "# Use --remote HOST:PORT for a QEMU GDB stub."))
    else:
        lines.extend(("", "# Use --attach PID for a running QBox host process."))
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")


def install_build_id_debug_file(out_dir: Path, elf: Path) -> tuple[str, Path] | None:
    build_id = elf_build_id(elf)
    if not build_id or len(build_id) < 3:
        return None
    debug_file = out_dir / ".build-id" / build_id[:2] / f"{build_id[2:]}.debug"
    debug_file.parent.mkdir(parents=True, exist_ok=True)
    debug_file.unlink(missing_ok=True)
    debug_file.symlink_to(elf)
    return build_id, debug_file


def write_readme(
    out_dir: Path,
    manifest: Path,
    components: Mapping[str, ComponentRecord],
) -> None:
    component_lines = []
    for name, info in sorted(components.items()):
        symbols = ", ".join(info["symbols"]) or "no default symbol"
        component_lines.append(
            f"- `{name}`: `{info['elf']}` using `{info['debugger']}`; "
            f"symbols {symbols}"
        )
    readme = (
        "# Apollo Local GDB Environment\n\n"
        "Generated by `scripts/setup/setup_local_debug_env.py`.\n\n"
        "Buildroot is intentionally excluded. QBox, its component plugins, "
        "libqemu, TF-M, SCP-firmware, Zephyr, TF-A, OP-TEE, U-Boot, and Linux "
        f"are inventoried in `{manifest.name}`. The `gdb/` directory contains "
        "one command file per artifact.\n\n"
        "```bash\n"
        f"scripts/debug/run_local_gdb.py --manifest {manifest} --list\n"
        f"scripts/debug/run_local_gdb.py --manifest {manifest} "
        "qbox-host --attach PID\n"
        f"scripts/debug/run_local_gdb.py --manifest {manifest} linux \\\n"
        "  --remote localhost:12341 --break start_kernel\n"
        "```\n\n"
        "FVP live control still uses `scripts/debug/local_debug_iris.py` "
        "because the model exposes Iris instead of a GDB remote stub.\n\n"
        "## Components\n\n"
        + "\n".join(component_lines)
        + "\n"
    )
    (out_dir / "README.md").write_text(readme, encoding="utf-8")
