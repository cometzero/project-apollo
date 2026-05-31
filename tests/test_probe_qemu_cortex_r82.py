import importlib.util
from pathlib import Path

import pytest

PROBE_PATH = Path(__file__).resolve().parents[1] / "scripts/probe_qemu_cortex_r82.py"
spec = importlib.util.spec_from_file_location("probe_qemu_cortex_r82", PROBE_PATH)
assert spec is not None
assert spec.loader is not None
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)
ProbeError = probe.ProbeError
probe_sources = probe.probe_sources


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_source_tree(root: Path) -> None:
    write(
        root / "tools/qemu/target/arm/tcg/cpu64.c",
        """
        static void aarch64_cortex_r82_initfn(Object *obj) {}
        static const ARMCPUInfo aarch64_cpus[] = {
            { .name = "cortex-r82", .initfn = aarch64_cortex_r82_initfn },
        };
        """,
    )
    write(
        root / "tools/qemu/target/arm/helper.c",
        """
        MPUIR_EL2 PRSELR_EL2 PRBAR_EL2 PRLAR_EL2
        """,
    )
    write(
        root / "tools/qemu/target/arm/cpu.h",
        """
        uint64_t *rbar[M_REG_NUM_BANKS];
        uint64_t *rlar[M_REG_NUM_BANKS];
        uint64_t *hprbar;
        uint64_t *hprlar;
        """,
    )
    write(
        root / "tools/qemu/target/arm/ptw.c",
        """
        static uint64_t *regime_rbar(CPUARMState *env, ARMMMUIdx mmu_idx,
                                     uint32_t secure);
        bool pmsav8_mpu_lookup(CPUARMState *env, vaddr address,
                               MMUAccessType access_type);
        hwaddr base = regime_rbar(env, mmu_idx, secure)[n] & ~bitmask;
        """,
    )
    write(
        root / "tools/qbox/qemu-components/cpu_arm/CMakeLists.txt",
        "add_subdirectory(cpu_arm_cortex_r82)\n",
    )
    write(
        root
        / "tools/qbox/qemu-components/cpu_arm/cpu_arm_cortex_r82/include/cortex-r82.h",
        """
        class cpu_arm_cortexR82 : public QemuCpuArm {
            cpu_arm_cortexR82(sc_core::sc_module_name name, QemuInstance& inst)
                : QemuCpuArm(name, inst, "cortex-r82-arm") {}
        };
        """,
    )
    write(
        root
        / "tools/qbox/qemu-components/cpu_arm/cpu_arm_cortex_r82/CMakeLists.txt",
        "gs_create_dymod(cpu_arm_cortexR82)\n",
    )


def test_probe_sources_accepts_complete_tree(tmp_path: Path) -> None:
    make_source_tree(tmp_path)

    result = probe_sources(tmp_path)

    assert result == [
        "qemu-cpu-model",
        "qemu-el2-mpu-sysregs",
        "qemu-pmsav8-64bit-storage",
        "qbox-cpu-wrapper",
    ]


def test_probe_sources_reports_missing_cpu(tmp_path: Path) -> None:
    make_source_tree(tmp_path)
    (tmp_path / "tools/qemu/target/arm/tcg/cpu64.c").write_text(
        "static const ARMCPUInfo aarch64_cpus[] = {};",
        encoding="utf-8",
    )

    with pytest.raises(ProbeError, match="QEMU CPU model"):
        probe_sources(tmp_path)
