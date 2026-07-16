import importlib.util
from pathlib import Path

import pytest

PROBE_PATH = Path(__file__).resolve().parents[1] / "scripts/inspect/probe_qemu_cortex_r82.py"
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
        root / "hsoc-stack/tools/qemu/target/arm/tcg/cpu64.c",
        """
        static void aarch64_cortex_r82_initfn(Object *obj) {
            SET_IDREG(isar, ID_AA64PFR0, 0x0000001000000222ull);
            SET_IDREG(isar, ID_AA64ISAR0, 0x00211120);
            SET_IDREG(isar, ID_ISAR0, 0x02101110);
        }
        static const ARMCPUInfo aarch64_cpus[] = {
            { .name = "cortex-r82", .initfn = aarch64_cortex_r82_initfn },
        };
        """,
    )
    write(
        root / "hsoc-stack/tools/qemu/target/arm/helper.c",
        """
        if (cpu_isar_feature(aa64_sel2, cpu)) {}
        static bool arm_is_v8r_el2_sel2(CPUARMState *env) { return true; }
        static const ARMCPRegInfo vmsa_pmsa_cp_reginfo[] = {
            { .name = "ESR_EL1" },
        };
        static const ARMCPRegInfo vmsa_cp_reginfo[] = {};
        CNTHPS_CTL_EL2
        MPUIR_EL2 PRSELR_EL2 PRBAR_EL2 PRLAR_EL2
        """,
    )
    write(
        root / "hsoc-stack/tools/qemu/target/arm/cpu.h",
        """
        uint64_t *rbar[M_REG_NUM_BANKS];
        uint64_t *rlar[M_REG_NUM_BANKS];
        uint64_t *hprbar;
        uint64_t *hprlar;
        """,
    )
    write(
        root / "hsoc-stack/tools/qemu/target/arm/ptw.c",
        """
        static uint64_t *regime_rbar(CPUARMState *env, ARMMMUIdx mmu_idx,
                                     uint32_t secure);
        bool pmsav8_mpu_lookup(CPUARMState *env, vaddr address,
                               MMUAccessType access_type);
        hwaddr base = regime_rbar(env, mmu_idx, secure)[n] & ~bitmask;
        """,
    )
    write(
        root / "hsoc-stack/tools/qbox-platform/qemu-components/CMakeLists.txt",
        "add_subdirectory(cpu_arm/cpu_arm_cortex_r82)\n",
    )
    write(
        root
        / "hsoc-stack/tools/qbox-platform/qemu-components/cpu_arm/cpu_arm_cortex_r82/include/cortex-r82.h",
        """
        class cpu_arm_cortexR82 : public QemuCpuArm {
            cpu_arm_cortexR82(sc_core::sc_module_name name, QemuInstance& inst)
                : QemuCpuArm(name, inst, "cortex-r82-arm") {
                m_external_ev |= irq_in->default_event();
                m_external_ev |= fiq_in->default_event();
                m_external_ev |= virq_in->default_event();
                m_external_ev |= vfiq_in->default_event();
                cpu.set_aarch64_mode(true);
                if (!p_mp_affinity.is_default_value()) {}
            }
        };
        """,
    )
    write(
        root
        / "hsoc-stack/tools/qbox-platform/qemu-components/cpu_arm/cpu_arm_cortex_r82/CMakeLists.txt",
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
    (tmp_path / "hsoc-stack/tools/qemu/target/arm/tcg/cpu64.c").write_text(
        "static const ARMCPUInfo aarch64_cpus[] = {};",
        encoding="utf-8",
    )

    with pytest.raises(ProbeError, match="QEMU CPU model"):
        probe_sources(tmp_path)


def test_probe_sources_reports_missing_r82_irq_wakeup(tmp_path: Path) -> None:
    make_source_tree(tmp_path)
    header = (
        tmp_path
        / "hsoc-stack/tools/qbox-platform/qemu-components/cpu_arm/cpu_arm_cortex_r82/include/cortex-r82.h"
    )
    header.write_text(
        header.read_text(encoding="utf-8").replace(
            "m_external_ev |= irq_in->default_event();", ""
        ),
        encoding="utf-8",
    )

    with pytest.raises(ProbeError, match="QBox CPU IRQ wakeup"):
        probe_sources(tmp_path)
