from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[1]
OEQA_CASE = (
    ROOT
    / "hsoc-stack/yocto/meta-hsoc-auto-solutions/lib/oeqa/runtime/cases/"
    / "test_01_auto_ad_nexios_uki_boot.py"
)


def load_module():
    sys.path.insert(0, str(ROOT / "layers/poky/meta/lib"))
    spec = importlib.util.spec_from_file_location(
        "test_01_auto_ad_nexios_uki_boot", OEQA_CASE
    )
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_uki_boot_marker_check_uses_existing_console_log(tmp_path: Path) -> None:
    module = load_module()
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    default_log = log_dir / "default_log.20260628120000"
    default_log.write_text(
        "\n".join(marker for _, marker in module.expected_boot_markers()) + "\n",
        encoding="utf-8",
    )
    (log_dir / "default_log").symlink_to(default_log.name)

    case = module.AutoAdNexiosUkiBootTest(
        methodName="test_01_uboot_uki_boot_markers"
    )
    case.console = "default"
    case.td = {"TEST_LOG_DIR": str(log_dir)}
    case.target = SimpleNamespace(
        DEFAULT_CONSOLE="default",
        bootlog=str(log_dir / "missing-bootlog"),
        expect=lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("live expect should not be used")
        ),
    )

    case.test_01_uboot_uki_boot_markers()


def test_writable_mount_check_queries_each_target() -> None:
    module = load_module()
    commands: list[str] = []

    class FakeTarget:
        def run(self, command: str, timeout: int = 120) -> tuple[int, str]:
            commands.append(command)
            mount_outputs = {
                "findmnt -nro TARGET,FSTYPE --target /rootrw": "/rootrw ext4\n",
                "findmnt -nro TARGET,FSTYPE --target /data": "/data ext4\n",
                "findmnt -nro TARGET,FSTYPE --target /run": "/run tmpfs\n",
            }
            if command in mount_outputs:
                return 0, mount_outputs[command]
            if command.startswith("printf oeqa > "):
                return 0, ""
            return 1, f"unexpected command: {command}"

    case = module.AutoAdNexiosUkiBootTest(
        methodName="test_03_writable_mounts"
    )
    case.target = FakeTarget()

    case.test_03_writable_mounts()

    assert "findmnt -nro TARGET,FSTYPE /rootrw /data /run" not in commands
    assert commands[:3] == [
        "findmnt -nro TARGET,FSTYPE --target /rootrw",
        "findmnt -nro TARGET,FSTYPE --target /data",
        "findmnt -nro TARGET,FSTYPE --target /run",
    ]
