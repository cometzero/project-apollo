# Standalone SI CL1 Zephyr

Apollo SI CL1의 Cortex-R82AE 기능을 별도 process에서 실행한다. AP Linux의
`run_gem5_linux.sh`와 독립된 configuration이다. `/srv/oss_contrib/gem5`의
PMSA64/private TCM, standalone CL1, Minor speculative atomic 및 timer compare
overflow 수정을 이식했다.

## Source 및 build

| 소유 repository / 경로 | 역할 |
|---|---|
| `hsoc-stack/tools/gem5/src/arch/arm/` | opt-in PMSA64, MPU 권한, TCM routing |
| `hsoc-stack/tools/gem5/configs/zena_si_cl1/run.py` | 4 PE, memory/cache, GIC, timer, PL011 |
| `hsoc-stack/tools/gem5/tests/zena_si_cl1/` | protection 및 speculative atomic probe |
| `hsoc-stack/components/system_mgmt/zephyrproject/zephyr_hsoc_src/boards/hsoc/apollo_si_cl1_bench/` | standalone board |
| 같은 repository의 `apps/si_cl1_bench/` | memory, timer IRQ, realtime workload |
| `hsoc-stack/yocto/meta-hsoc-auto-solutions/recipes-kernel/zephyr-si-cl1/` | Zephyr externalsrc recipe |
| 같은 layer의 `recipes-devtools/gem5/gem5-si-cl1-probes.bb` | bare-metal/SE probe build |
| `scripts/gem5/run_zephyr.py`, `report_si_cl1.py` | 실행, provenance, strict result/ROI 검증 |
| `scripts/run/run_qbox_zephyr.py` | QBox provider 및 standalone profile 실행 |

```sh
./yocto_build.sh --keep-conf --gem5-zephyr
```

`MACHINE=apollo-qvp`와 기존 `build/conf`를 사용한다. `gem5-native`,
`zephyr-si-cl1-bench`, `zephyr-si-cl1-boot`, `gem5-si-cl1-probes`를 함께 빌드한다. 공유 BitBake build는
직렬화하며 build 중 externalsrc를 수정하지 않는다. Zephyr는 기존 patched
Zephyr와 `zephyr-sdk-native`를 사용한다. probe는 Yocto AArch64 target compiler로
빌드하며 launcher는 compiler를 호출하지 않는다.

Deploy root는 `build/tmp_baremetal/deploy/`다.

- `gem5-native/gem5.opt`, `gem5-native/gem5-native.json`: host binary와 runtime 환경.
- `images/apollo-qvp/zephyr-si-cl1-bench.{elf,bin,map,dts,config}`: guest image/debug 자료.
- `images/apollo-qvp/zephyr-si-cl1-bench-manifest.json`: compiler, source 및 input hash.
- `images/apollo-qvp/zephyr-si-cl1-boot.{elf,bin,map,dts,config}`: QBox 전용 boot smoke.
- `images/apollo-qvp/gem5/gem5-si-cl1-{pmsa,minor-atomic,stage2}.elf`: directed regression probe.

기존 production `zephyr-demos-cl1` board/app의 HIPC/PFDI/SCMI 의존성과 분리한다.
이 benchmark image는 Apollo full-system firmware의 대체물이 아니다.

## 모델 구성

| 항목 | 설정 |
|---|---|
| CPU | 4 PE, MPIDR `0x10000`, `0x10100`, `0x10200`, `0x10300` |
| gem5 default | MinorCPU, 1 GHz; generic in-order timing proxy |
| 실행 EL | EL2 reset → Zephyr EL1, PMSAv8-64 MPU |
| Counter | 100 MHz, gem5 tick 1 THz |
| LLRAM | `0x140000000`, 8 MiB; ELF/text/data/stack |
| MM SRAM | `0x40000000`, 8 MiB, cacheable |
| NC SRAM | `0x48000000`, 8 MiB, non-cacheable |
| ITCM / DTCM | `0x100000000` / `0x100100000`, 각 PE별 128 KiB |
| Cache | PE별 L1I/L1D 64 KiB 4-way, shared L2 512 KiB 8-way |
| GIC | GICD `0x30200000`, GICR `0x30260000`, stride `0x20000` |
| PL011 | `0x2a410000`, INTID 39 |
| Timer | CNTP PPI29, CNTV PPI27 |
| 실험 latency | SRAM 20 ns, TCM 1 ns |

TCM은 L1 전에 PE별 private backing으로 routing한다. MM SRAM은 L1/L2를 거치고
NC SRAM은 L2를 bypass한다. LLRAM instruction fetch에는 L1I를 사용할 수 있지만
**LLRAM data는 강제 NC**다. 실제 write-through cache/TCM bank arbitration을
구현했다고 해석하지 않는다. Cortex-R82AE MIDR과 일부 architectural 기능을
제공하지만 pipeline 및 latency는 silicon에 calibration되지 않았다.

`ArmISA.pmsa64`는 기본 off다. AP VMSA는 기존 경로를 사용한다. sysreg metadata가
process-global이므로 **한 gem5 process에서 PMSA와 VMSA CPU를 혼합할 수 없다**.
혼합 profile은 초기화 오류로 거부한다. nested stage2, secure-state isolation,
physical lockstep, ECC/RAS, 직접 번호 PRBARn encoding 등은 지원 범위 밖이다.

## 실행

```sh
# 실제 QBox provider에서 standalone Zephyr boot
./run_qbox_zephyr.sh
./run_qbox_zephyr.sh --headless --timeout 120 --exit-after-pass

# gem5: Zephyr boot 후 모든 benchmark 자동 실행
./run_gem5_zephyr.sh
./run_gem5_zephyr.sh --headless --out-dir /tmp/si-cl1-discovery

# 동일 ELF/configuration으로 정확한 memory ROI 통계 replay
./run_gem5_zephyr.sh --headless --out-dir /tmp/si-cl1-replay \
  --roi-schedule /tmp/si-cl1-discovery/report/roi-schedule.json
python3 scripts/gem5/report_si_cl1.py /tmp/si-cl1-discovery/system.platform.terminal \
  --backend gem5 --gem5-dir /tmp/si-cl1-discovery \
  --replay-dir /tmp/si-cl1-replay --output /tmp/si-cl1-report
```

기존 output directory를 덮어쓰지 않는다. interactive 실행은 tmux UART/platform
log pane을 사용하며 F12로 해당 session을 종료한다. headless는 제한시간과 exit
status로 자동화한다. UART 파일과 simulator log를 별도로 보존한다. gem5의 authoritative UART는
`system.platform.terminal`이며 socket 전달본은 `uart.log`다.

QBox는 `zephyr-si-cl1-boot.elf`를 사용한다. 기존 Cortex-R82 backend에는
AArch64 PMSA가 없어 `CONFIG_ARM_MPU=n`인 별도 boot app을 빌드한다. MPU와
private TCM을 사용하는 benchmark ELF로는 초기 MPU 확인에서 중단된다.

QBox는 dedicated Lua profile에서 CL1 CPU/GIC/UART/LLRAM만 조립하며 AP/RSE/SCP
handoff를 생략한다. ELF entry와 PT_LOAD를 읽어 loader 입력을 만들므로 hardcoded
entry나 runtime cross compiler가 필요 없다. QBox의 판정 범위는 UART의
`SI_CL1_BOOT_CPU` 4개 및 `SI_CL1_BOOT_RESULT`까지의 **4 PE Zephyr boot**다. gem5 private TCM/cache timing 검증으로
확대하지 않는다. standalone counter/PPI 변경은 production platform에 적용하지 않는다.

## 측정 조건과 판정

- Memory 12 cases: TCM/L1/L2/SRAM_NC × read/write/chase.
- TCM/L1 working set 16 KiB, L2/NC 256 KiB. read/write 8 passes,
  chase 4 passes, 64-byte stride와 8-byte useful access.
- 초기화/warmup/checksum/output은 ROI 밖. memory ROI에서만 local IRQ를 mask한다.
- Bandwidth는 useful bytes ÷ guest CNTPCT duration이다. host elapsed time을
  simulated bandwidth 계산에 사용하지 않는다.
- Timer IRQ: idle 100 µs × 16회와 loaded 32회, 총 48 raw samples.
- Realtime: CPU별 pinned task, priority 1–4, period/deadline
  250 µs/500 µs/1 ms/2 ms, 각 8 jobs. CPU별 128 KiB priority-10 memory loader와 경쟁.
- `deadline_miss`, `skipped` 및 interference checksum/pass를 각각 검사한다.
  functional PASS는 schedulability PASS 또는 WCET 보장을 의미하지 않는다.

Reporter는 4 CPU/EL1/private TCM, MPU mapping, 12 memory checksum, 48 IRQ samples,
32 jobs 및 summary/raw record 일치를 검사한다. PASS 문자열 하나만 검사하지 않는다.
`L1`, `L2` 등의 label은 workload 목표이며 ROI traffic을 검증하기 전에는 실제 hit
경로를 보장하지 않는다. Replay는 discovery/replay guest begin/end와 native ROI event
및 해당 stats dump의 exact tick을 비교한다. `counter × 10000` 변환은 위 counter/tick
frequency와 epoch 0에만 유효하다. 종료 시 dump를 ROI로 대신 사용하지 않는다.

## 이식 검증 결과

Evidence root: `build/qbox-apollo-qvp/gem5/si-cl1-integration-20261024/`.

| 검사 | 결과 | Evidence |
|---|---|---|
| 실제 QBox Zephyr SMP4 boot | PASS, 4개 MPIDR / 100 MHz / `cpu_mask=f` | `qbox-boot-only/zephyr-uart.log`, `result.json` |
| gem5 UART/platform/F12 | PASS, 3 panes 및 native process 회수 | `gem5-tmux-cleanup-fixed/result.json` |
| Host launcher/parser tests | PASS, 29 tests | `host-tests-final.log` |
| QBox 정상 boot 후 F12 | PASS, session 종료 및 process 회수 | `qbox-boot-f12/cleanup.json` |
| Yocto build | PASS, 1,156 tasks | `yocto-build-final.log` |
| PMSA Atomic / Minor | PASS, 각각 17 checks | `native-probes.json`, `pmsa-{atomic,minor}/` |
| stage2 / 혼합 profile 거부 | PASS, stage2 및 두 초기화 순서 모두 expected exit 1 | `native-probes.json` |
| Minor wrong-path atomic | PASS, VMSA SE wrong-path squash 및 committed SWPAL | `minor-atomic/result.json` |
| Minor Zephyr benchmark | PASS, 12 memory / 48 IRQ / 32 jobs, misses=0 / skipped=0 | `minor-discovery-fixed/report/` |
| exact ROI replay | PASS, 12개 경로와 guest timing 일치 | `final-report/metrics.json` |
| gem5 초기 실행 | FAIL, MAX CVAL tick overflow 확인 | `minor-discovery/gem5.log` |

초기 실패는 reference의 `7c9713a1a604` timer overflow 보정이 추가로 필요함을
확인한 결과다. 해당 수정 적용 후의 native/benchmark 결과를 아래에 기록한다.
QBox boot에서 logical CPU 0의 physical PE는 startup voting에 따라 달라질 수
있으므로 affinity set 전체와 중복 여부로 검사한다.

검증 native binary SHA256:
`68a4cbd6579644fe32f59086b67dad406dfaae3d47d2cff6ac26d7a5c0f797dc`.

이번 검증은 standalone SI CL1 fresh boot 범위다. AP Linux full boot 및 SI checkpoint
restore는 재검증하지 않았다. Native Minor atomic probe는 VMSA SE 경로의 제한된 회귀
증거이며 AP Linux 전체 검증을 대신하지 않는다.

전체 수치와 latency distribution은 [측정 결과](si-cl1-benchmark-results.md)에 기록했다.
Discovery/replay host 시간은 각각 151.43 / 148.62초이며 simulated 성능 계산에는 사용하지 않았다.
