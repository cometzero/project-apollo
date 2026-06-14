# Apollo QBox Placeholder Coverage Ledger

작성일: 2026-06-14

이 문서는 `tools/qbox/platforms/apollo/hw-block/`의 Apollo QVP
`gs_memory`와 `modeled = false` placeholder를 승격 계획 관점에서 분류한다.
분류 기준은 [Spec](spec-ko.md)의 `memory-backing`,
`accepted-placeholder`, `full-model-required`, `unsupported-gap` 정의를
따른다.

## 상태 요약

| 분류 | 의미 | 현재 처리 |
| --- | --- | --- |
| `memory-backing` | RAM, SRAM, TCM, vring, resource table, firmware/image/load area | `gs_memory` 유지 |
| `accepted-placeholder` | boot compatibility를 위한 임시 register window | ledger에 debt로 추적 |
| `full-model-required` | side effect, fault, access-control, interrupt, reset/power 상태가 필요한 IP | SystemC/TLM model로 승격 |
| `unsupported-gap` | FVP-visible이지만 first wave 범위 밖의 IP | 후속 epic에서 별도 구현 |

## First Wave Gate

첫 wave에서 `full-model-required`로 처리해야 하는 P0/P1 항목:

- `si_cl0_ssu`
- `si_cl0_fmu`
- `rse_nsacfg_regs`
- `rse_sacfg_regs`
- `rse_mpc_vm0_regs`
- `rse_mpc_vm1_regs`
- `rse_sic_regs`
- `rse_mpc_sic_regs`
- APU/ATU policy path: `host_si_atu`, `host_ap_atu`,
  `host_smdexp2smd_atu` 주변 접근 filter

`host_systop_pik`, `host_css_counters_timers`, `ap_secure_wdog`,
AP/SI cluster AE/control, RoS/I/O/debug placeholder는 first wave에서
분류만 고정하고, 구현은 decision record에 따라 후속 epic으로 분리한다.

## Primary Compute Standalone

Source: `tools/qbox/platforms/apollo/hw-block/primary_compute.lua`

| Entry | 현재 모델 | 분류 | 근거 / 후속 |
| --- | --- | --- | --- |
| `ram_0`, `ram_1` | `gs_memory` | `memory-backing` | AP DRAM backing |
| `sram_0` | `gs_memory` | `memory-backing` | AP boot/scratch SRAM |
| `si_cl1_rproc_rsctbl_0` | `gs_memory` | `memory-backing` | SI CL1 remoteproc resource table |
| `si_cl1_vdev0vring0_0`, `si_cl1_vdev0vring1_0` | `gs_memory` | `memory-backing` | virtio/rpmsg vring backing |
| `si_cl1_vdev0buffer_0` | `gs_memory` | `memory-backing` | virtio/rpmsg buffer backing |
| `ras_buffer_0` | `gs_memory` | `accepted-placeholder` | RAS/CPER buffer parity는 FR-007 follow-up |
| `fallback_0` | `gs_memory` | `accepted-placeholder` | standalone compatibility catch-all. coverage audit에서 fallback hit를 별도 추적해야 함 |

## Safety Island CL0

Source: `tools/qbox/platforms/apollo/hw-block/si_cl0.lua`

| Entry | 현재 모델 | 분류 | 근거 / 후속 |
| --- | --- | --- | --- |
| `si_cl0_sram` | `gs_memory` | `memory-backing` | CL0 SRAM backing |
| `si_cl0_atu_check_*` | `gs_memory` | `accepted-placeholder` | ATU reachability check window. first wave APU/ATU filter evidence로 전환 예정 |
| `si_cl0_rse_shared_sram` | `gs_memory` | `memory-backing` | RSE/SI shared SRAM merged view |
| `si_cl0_ssu` | `gs_memory` | `full-model-required` | SSU `ERR_*`, `SYS_*`, FMU aggregation, external safety state 필요 |
| `si_cl0_fmu` | `gs_memory` | `full-model-required` | FMU error record, group status, critical/non-critical interrupt 필요 |
| `si_cl0_smd_expansion_window` | `gs_memory` | `accepted-placeholder` | SMD expansion decode coverage. APU/ATU filter가 deny/report를 담당해야 함 |
| `si_cl0_css_counters_timers_window` | `gs_memory` | `full-model-required` | counter/timer control side effect 필요. MODEL-070 follow-up |
| `si_cl0_ap_peripheral_secure_sram` | `gs_memory` | `memory-backing` | AP secure peripheral SRAM backing |
| `si_cl0_ap_peripheral_ns_sram` | `gs_memory` | `memory-backing` | AP non-secure peripheral SRAM tail backing |
| `si_cl0_smd_shared_sram` | `gs_memory` | `memory-backing` | SMD shared SRAM backing |
| `si_cl0_smd_exp_mgi_sram` | `gs_memory` | `memory-backing` | SMCF/SMD expansion MGI SRAM backing |
| `si_cl0_systop_pik_window` | `gs_memory` | `full-model-required` | PIK reset/power/status polling side effect 필요. MODEL-070 follow-up |
| `si_cl1_ppu_ae` | `gs_memory` | `accepted-placeholder` | CL1 AE register parity follow-up |
| `si_cl0_ap_cluster*_ae` | `gs_memory` | `accepted-placeholder` | AP cluster AE/RAS parity follow-up |
| `si_cl0_ap_cluster*_control` | `gs_memory` | `accepted-placeholder` | AP cluster control parity follow-up |

## Safety Island CL1

Sources:

- `tools/qbox/platforms/apollo/hw-block/si_cl1.lua`
- `tools/qbox/platforms/apollo/hw-block/si_cl1_isolated.lua`

| Entry | 현재 모델 | 분류 | 근거 / 후속 |
| --- | --- | --- | --- |
| `si_cl1_sram` | `gs_memory` | `memory-backing` | CL1 SRAM backing |
| `si_cl1_scmi_shmem` | `gs_memory` | `memory-backing` | SCMI shared memory |
| `si_cl1_shared_ram` isolated mode | `gs_memory` | `memory-backing` | isolated CL1 shared RAM backing |
| `fallback_0` isolated mode | `gs_memory` | `accepted-placeholder` | isolated compatibility catch-all |

## RSE And Host Integration

Source: `tools/qbox/platforms/apollo/hw-block/rse.lua`

| Entry | 현재 모델 | 분류 | 근거 / 후속 |
| --- | --- | --- | --- |
| `rse_rom` | `gs_memory` | `memory-backing` | RSE ROM image backing |
| `rse_itcm`, `rse_itcm_cpu0` | `gs_memory` | `memory-backing` | RSE ITCM backing and aliases |
| `rse_dtcm`, `rse_dtcm_cpu0` | `gs_memory` | `memory-backing` | RSE DTCM backing and aliases |
| `rse_vm0`, `rse_vm1` | `gs_memory` | `memory-backing` | RSE VM SRAM backing |
| `rse_otp_wrapper` | `gs_memory` | `accepted-placeholder` | OTP wrapper load window. lifecycle semantics are handled by `rse_lcm`/KMU paths today |
| `rse_cpu0_secctrl_regs`, `rse_cpu0_pwrctrl_regs`, `rse_cpu0_identity_regs` | `gs_memory` | `accepted-placeholder` | CPU local control/identity parity follow-up |
| `rse_nsacfg_regs` | `gs_memory` | `full-model-required` | non-secure access configuration behavior 필요 |
| `rse_sacfg_regs` | `gs_memory` | `full-model-required` | secure access configuration behavior 필요 |
| `rse_mpc_vm0_regs`, `rse_mpc_vm1_regs` | `gs_memory` | `full-model-required` | SIE-300 MPC-style block config/status/lock behavior 필요 |
| `rse_sic_regs`, `rse_mpc_sic_regs` | `gs_memory` | `full-model-required` | SIC/MPC access-control state 필요 |
| `rse_syscntr_cntrl_regs`, `rse_syscntr_read_regs` | `gs_memory` | `full-model-required` | system counter/timer control side effect 필요. MODEL-070 follow-up |
| `rse_tram` | `gs_memory` | `memory-backing` | TRAM backing |
| `host_ap_shared_sram` | `gs_memory` | `memory-backing` | AP/RSE shared SRAM and SDS data backing |
| `host_ap_mhu_ns_shared_sram` | `gs_memory` | `memory-backing` | AP MHU non-secure shared SRAM |
| `host_ap_bl2_header_sram` | `gs_memory` | `memory-backing` | AP BL2 header SRAM backing |
| `host_ap_trusted_nvctr` | `gs_memory` | `accepted-placeholder` | trusted nvCounter register parity follow-up |
| `host_ap_dram1`, `host_ap_dram2` | `gs_memory` | `memory-backing` | AP DRAM backing |
| `host_ap_ffa_mm_comm_buffer` | `gs_memory` | `memory-backing` | FF-A MM communication buffer |
| `host_ap_spmc_sdram` | `gs_memory` | `memory-backing` | SPMC SDRAM backing |
| `ap_secure_wdog` | `gs_memory` | `full-model-required` | secure watchdog control/refresh side effect 필요. MODEL-080 follow-up |
| `host_si_cl0_sram`, `host_si_cl1_sram` | `gs_memory` | `memory-backing` | host-visible SI SRAM backing |
| `host_si_cl0_cub`, `host_si_cl1_cub` | `gs_memory` | `accepted-placeholder` | SI cluster utility bus coverage window |
| `host_rse_si_ssram` | `gs_memory` | `memory-backing` | RSE/SI shared SRAM backing |
| `host_systop_pik` | `gs_memory` | `full-model-required` | system top PIK polling/reset/power status 필요. MODEL-070 follow-up |
| `host_css_counters_timers` | `gs_memory` | `full-model-required` | REFCLK/generic timer sync control 필요. MODEL-070 follow-up |
| `host_smcf_sram` | `gs_memory` | `memory-backing` | SMCF SRAM backing |
| `host_ap_rse_mailbox` | `gs_memory` | `memory-backing` | TF-M SFCP pointer-access mailbox backing |
| `rse_integ_layer_regs` | `gs_memory` | `accepted-placeholder` | integration-layer register parity follow-up |
| `ap_gicr_reserved_*` | `gs_memory` | `accepted-placeholder` | inactive AP GIC redistributor frames for AP16/GIC parity follow-up |

## RoS / I/O / Debug Gap

Source: `tools/qbox/platforms/apollo/hw-block/ros.lua`

| Entry | 현재 모델 | 분류 | 근거 / 후속 |
| --- | --- | --- | --- |
| `system_registers` | `modeled = false` | `unsupported-gap` | RoS system register model 필요. FR-008 follow-up |
| `virtio_p9` | `modeled = false` | `unsupported-gap` | P9 virtio parity follow-up |
| `vsi[0..1]` | `modeled = false` | `unsupported-gap` | VSI parity follow-up |
| `uart[0..1]` | `modeled = false` | `unsupported-gap` | RoS UART parity follow-up |
| `virtio_blk[0..3]`, `virtio_net`, `virtio_rng`, `rtc` | QEMU-backed | modeled | 현재 QBox 모델 유지 |

## Coverage Audit Rule

향후 `scripts/audit_qbox_apollo_fvp_full_coverage.py`는 다음 규칙을 적용해야
한다.

- P0/P1 `full-model-required` 항목이 `gs_memory`로 남아 있으면 fail.
- `memory-backing` 항목은 `gs_memory`로 남아도 pass.
- `accepted-placeholder` 항목은 warning/debt로 기록하되 first wave gate는
  통과할 수 있다.
- `unsupported-gap` 항목은 full FVP parity gate에서는 fail이지만, first wave
  runtime gate에서는 follow-up epic 링크가 있으면 pass 가능하다.
