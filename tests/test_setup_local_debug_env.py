from __future__ import annotations

import importlib.util
from pathlib import Path
import shutil
import sys
from types import ModuleType


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/setup/setup_local_debug_env.py"


def load_debug_env_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("setup_local_debug_env", SCRIPT)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_si_cl1_zephyr_debug_symbols_prefer_local_deploy() -> None:
    module = load_debug_env_module()

    component = next(
        item for item in module.COMPONENTS if item.name == "si-cl1-zephyr"
    )

    assert component.elf_candidates[0] == "deploy/firmware/zephyr-demos-cl1.elf"


def test_debug_components_exclude_buildroot() -> None:
    module = load_debug_env_module()

    names = {component.name for component in module.COMPONENTS}

    assert "buildroot-busybox" not in names


def test_qbox_and_libqemu_are_debug_components() -> None:
    module = load_debug_env_module()

    names = {component.name for component in module.HOST_COMPONENTS}

    assert {"qbox-host", "qbox-core", "libqemu-aarch64"} <= names


def test_qbox_defaults_to_relwithdebinfo() -> None:
    build_script = ROOT / "scripts/build/modules/build_qbox.sh"

    assert 'QBOX_CMAKE_BUILD_TYPE:-RelWithDebInfo' in build_script.read_text()


def test_elf_arch_ignores_architecture_name_in_path(tmp_path: Path) -> None:
    module = load_debug_env_module()
    elf = tmp_path / "libqemu-system-aarch64.so"
    shutil.copy2("/bin/true", elf)

    assert module.elf_arch(elf) == "x86_64"


def test_qbox_host_script_sets_libqemu_breakpoint(tmp_path: Path) -> None:
    module = load_debug_env_module()
    component = next(
        item for item in module.HOST_COMPONENTS if item.name == "qbox-host"
    )
    script = tmp_path / "qbox-host.gdb"

    module.write_gdb_script(
        script,
        ROOT,
        tmp_path,
        component,
        Path("/bin/true"),
        {},
        (tmp_path,),
    )

    contents = script.read_text()
    assert "set auto-solib-add on" in contents
    assert f"set debug-file-directory {tmp_path}" in contents
    assert f"set solib-search-path {tmp_path}" in contents
    assert f"set environment LD_LIBRARY_PATH {tmp_path}" in contents
    assert "tbreak libqemu_init" in contents


def test_component_script_reports_entry_source_line(tmp_path: Path) -> None:
    module = load_debug_env_module()
    component = next(
        item for item in module.HOST_COMPONENTS if item.name == "qbox-host"
    )
    script = tmp_path / "qbox-host.gdb"

    module.write_gdb_script(
        script,
        ROOT,
        tmp_path,
        component,
        Path("/bin/true"),
        {"main": 0x1000},
        (tmp_path,),
    )

    contents = script.read_text()
    assert "info line main" in contents
    assert "break main" in contents


def test_domain_scripts_load_each_staged_component(tmp_path: Path) -> None:
    module = load_debug_env_module()
    records = {
        "tfm-bl1_1": debug_record(tmp_path, "tfm-bl1_1", "0x1000"),
        "tfm-bl1_2": debug_record(tmp_path, "tfm-bl1_2", "0x2000"),
        "tfm-bl2": debug_record(tmp_path, "tfm-bl2", "0x3000"),
        "tfm-s": debug_record(tmp_path, "tfm-s", "0x4000"),
    }

    module.add_domain_records(tmp_path, records)

    domain = records["domain-rse"]
    contents = Path(str(domain["gdb_script"])).read_text()
    assert domain["members"] == ["tfm-bl1_1", "tfm-bl1_2", "tfm-bl2", "tfm-s"]
    assert domain["remote"] == "127.0.0.1:12340"
    assert contents.count("add-symbol-file") == 3
    assert "break *0x1000" in contents
    assert "break *0x4000" in contents
    assert "info line *0x1000" in contents
    assert contents.count("commands $bpnum") == 4
    assert f'symbol-file "{tmp_path}/tfm-bl2.elf"' in contents


def test_u_boot_uses_tf_a_bl33_runtime_address() -> None:
    module = load_debug_env_module()
    component = next(item for item in module.COMPONENTS if item.name == "u-boot")

    assert component.runtime_text_address == 0xE0000000


def test_domain_script_relocates_u_boot_symbols(tmp_path: Path) -> None:
    module = load_debug_env_module()
    record = debug_record(tmp_path, "u-boot", "0xe0000000")
    record["load_offset"] = "0x58000000"
    records = {"u-boot": record}

    module.add_domain_records(tmp_path, records)

    contents = Path(str(records["domain-ap"]["gdb_script"])).read_text()
    assert f'file "{tmp_path}/u-boot.elf"' in contents
    assert "break *0xe0000000" in contents
    assert f'symbol-file -o 0x58000000 "{tmp_path}/u-boot.elf"' in contents


def test_domain_scripts_use_default_resume_packets(tmp_path: Path) -> None:
    module = load_debug_env_module()
    records = {
        "tfm-bl1_1": debug_record(tmp_path, "tfm-bl1_1", "0x1000"),
        "tfa-bl2": debug_record(tmp_path, "tfa-bl2", "0x2000"),
    }

    module.add_domain_records(tmp_path, records)

    rse = Path(str(records["domain-rse"]["gdb_script"])).read_text()
    ap = Path(str(records["domain-ap"]["gdb_script"])).read_text()
    setting = "set remote verbose-resume-packet off"
    assert setting not in rse
    assert setting not in ap


def debug_record(tmp_path: Path, name: str, address: str) -> dict[str, object]:
    elf = tmp_path / f"{name}.elf"
    elf.touch()
    return {
        "label": name,
        "domain": "rse",
        "target": "rse",
        "elf": str(elf),
        "gdb_script": str(tmp_path / f"{name}.gdb"),
        "debugger": "gdb-multiarch",
        "arch": "arm",
        "has_symtab": True,
        "has_debug_info": True,
        "has_debug_line": True,
        "default_symbol": "entry",
        "symbols": {"entry": address},
        "text_address": address,
        "source_locations": {"entry": f"/src/{name}.c:1"},
        "source_roots": ["/src"],
    }
