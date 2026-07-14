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
    assert "break libqemu_init" in contents
