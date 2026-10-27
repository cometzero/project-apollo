# SI CL1 Zephyr: QBox/gem5 통합 이미지와 benchmark

2026-10-27 기준, `run_qbox_zephyr.sh`는 Apollo QVP의 **통합
`zephyr-demos-cl1.bin/.elf`를 그대로 사용**하여 SI CL1만 실행한다.
`run_gem5_zephyr.sh`도 같은 통합 image를 기본으로 사용한다. 기존 standalone
benchmark는 `--mode benchmark`로 선택한다. 두 simulator는 별도 process이며
AP Linux의 `run_gem5_linux.sh`와 독립적이다.

gem5에는 `/srv/oss_contrib/gem5`의 PMSA64/private TCM, standalone CL1,
Minor speculative atomic 및 timer compare overflow 수정을 이식했다.

## Source 및 build

| 소유 repository / 경로 | 역할 |
|---|---|
| `hsoc-stack/tools/gem5/src/arch/arm/` | opt-in PMSA64, MPU 권한, TCM routing |
| `hsoc-stack/tools/gem5/configs/zena_si_cl1/run.py` | 4 PE, memory/cache, GIC, timer, PL011 |
| `hsoc-stack/tools/gem5/src/dev/arm/css/SiCl1Mhu.py`, `si_cl1_mhu.cc` | 통합 image용 MHUv3/PFDI functional device |
| `hsoc-stack/tools/gem5/tests/zena_si_cl1/` | protection 및 speculative atomic probe |
| `hsoc-stack/components/system_mgmt/zephyrproject/zephyr_hsoc_src/boards/hsoc/apollo_si_cl1_bench/` | standalone board |
| 같은 repository의 `apps/si_cl1_bench/` | memory, timer IRQ, realtime workload |
| `hsoc-stack/yocto/meta-hsoc-auto-solutions/recipes-kernel/zephyr-si-cl1/` | Zephyr externalsrc recipe |
| 같은 layer의 `recipes-devtools/gem5/gem5-si-cl1-probes.bb` | bare-metal/SE probe build |
| `scripts/gem5/run_zephyr.py`, `report_si_cl1.py` | 실행, provenance, strict result/ROI 검증 |
| `scripts/run/run_qbox_zephyr.py` | QBox provider, 통합 ELF/binary 검증 및 SI CL1 profile 실행 |
| `hsoc-stack/yocto/meta-hsoc-bsp/recipes-kernel/zephyr-kernel/zephyr-demos-cl1-apollo-qvp.inc` | 기존 통합 QVP Zephyr board/image 구성 |

QBox는 기존 `apollo-qvp` image build가 배포한 `zephyr-demos-cl1`과 QBox provider를
사용한다. Zephyr만 다시 빌드할 때는 다음을 실행한다. 별도
`zephyr-si-cl1-boot` recipe를 QBox launcher용으로 빌드할 필요가 없다.

```sh
./yocto_build.sh --keep-conf zephyr-demos-cl1
```

`nexios-bsp-initramfs-apollo-qvp.qboxconf` 또는 `nexios-image-apollo-qvp.qboxconf`와
그 provider executable은 기존 BSP/product build로 준비되어 있어야 한다.
`--qboxconf`로 다른 유효한 provider manifest를 선택할 수 있다.

gem5 통합 image 부팅에는 `gem5-native`와 기존 `zephyr-demos-cl1`만 필요하다.

```sh
./yocto_build.sh --keep-conf gem5-native zephyr-demos-cl1
```

gem5 benchmark/probe build는 기존 명령을 유지한다.

```sh
./yocto_build.sh --keep-conf --gem5-zephyr
```

실제 `build/conf`의 `MACHINE=apollo-qvp`를 확인한다. `--gem5-zephyr`는 `gem5-native`,
`zephyr-si-cl1-bench`, `zephyr-si-cl1-boot`, `gem5-si-cl1-probes`를 함께 빌드한다. 공유 BitBake build는
직렬화하며 build 중 externalsrc를 수정하지 않는다. Zephyr는 기존 patched
Zephyr와 `zephyr-sdk-native`를 사용한다. probe는 Yocto AArch64 target compiler로
빌드하며 launcher는 compiler를 호출하지 않는다.

Deploy root는 `build/tmp_baremetal/deploy/`다.

- `gem5-native/gem5.opt`, `gem5-native/gem5-native.json`: host binary와 runtime 환경.
- `images/apollo-qvp/zephyr-si-cl1-bench.{elf,bin,map,dts,config}`: guest image/debug 자료.
- `images/apollo-qvp/zephyr-si-cl1-bench-manifest.json`: compiler, source 및 input hash.
- `images/apollo-qvp/zephyr-demos-cl1.{elf,bin}`: 두 launcher가 기본으로 사용하는 통합 이미지.
- `images/apollo-qvp/zephyr-si-cl1-boot.{elf,bin,map,dts,config}`: 이전 QBox boot smoke artifact; 현재 launcher의 기본 입력이 아니다.
- `images/apollo-qvp/gem5/gem5-si-cl1-{pmsa,minor-atomic,stage2}.elf`: directed regression probe.

gem5 benchmark image는 통합 `zephyr-demos-cl1` board/app의 HIPC/PFDI/SCMI
의존성과 분리되어 있으며 Apollo full-system firmware의 대체물이 아니다.

## gem5 모델 구성

| 항목 | 설정 |
|---|---|
| CPU | 4 PE, MPIDR `0x10000`, `0x10100`, `0x10200`, `0x10300` |
| gem5 CPU | 통합 boot: AtomicSimpleCPU; benchmark: MinorCPU, 1 GHz |
| 실행 EL | EL2 reset → Zephyr EL1, PMSAv8-64 MPU |
| Counter | 통합 boot: 125 MHz; benchmark: 100 MHz; gem5 tick 1 THz |
| LLRAM | `0x140000000`, 8 MiB; ELF/text/data/stack |
| MM SRAM | `0x40000000`, 8 MiB, cacheable |
| NC SRAM | `0x48000000`, 8 MiB, non-cacheable |
| ITCM / DTCM | `0x100000000` / `0x100100000`, 각 PE별 128 KiB |
| Cache | PE별 L1I/L1D 64 KiB 4-way, shared L2 512 KiB 8-way |
| GIC | GICD `0x30200000`, GICR `0x30260000`, stride `0x20000` |
| PL011 | `0x2a410000`, INTID 39 |
| Timer | CNTP PPI29, CNTV PPI27 |
| 실험 latency | SRAM 20 ns, TCM 1 ns |
| HIPC (통합 mode) | PBX `0x39000000`, MBX `0x39040000`, INTID 72/73; shared RAM `0xe0130000`, 512 KiB |
| PFDI (통합 mode) | PBX `0x39200000`, MBX `0x39240000`, INTID 82; SCMI `0x48000000`에 40-byte slot × 4 |

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
# 실제 QBox provider에서 통합 SI CL1 Zephyr image boot
./run_qbox_zephyr.sh --dry-run
./run_qbox_zephyr.sh
./run_qbox_zephyr.sh --headless --timeout 120 --exit-after-pass

# gem5: 동일 통합 image를 부팅하고 UART shell 사용
./run_gem5_zephyr.sh --dry-run
./run_gem5_zephyr.sh
./run_gem5_zephyr.sh --headless --exit-after-pass --timeout 1200

# 명시적으로 기존 memory/realtime benchmark image 선택
./run_gem5_zephyr.sh --mode benchmark --headless --out-dir /tmp/si-cl1-discovery

# 동일 ELF/configuration으로 정확한 memory ROI 통계 replay
./run_gem5_zephyr.sh --mode benchmark --headless --out-dir /tmp/si-cl1-replay \
  --roi-schedule /tmp/si-cl1-discovery/report/roi-schedule.json
python3 scripts/gem5/report_si_cl1.py /tmp/si-cl1-discovery/system.platform.terminal \
  --backend gem5 --gem5-dir /tmp/si-cl1-discovery \
  --replay-dir /tmp/si-cl1-replay --output /tmp/si-cl1-report
```

기존 output directory를 덮어쓰지 않는다. interactive 실행은 tmux UART/platform
log pane을 사용하며 F12로 해당 session을 종료한다. headless는 제한시간과 exit
status로 자동화한다. UART 파일과 simulator log를 별도로 보존한다. gem5의 authoritative UART는
`system.platform.terminal`이며 socket 전달본은 `uart.log`다.

### QBox 통합 이미지 부팅 경로

기본 입력은 deploy directory의 `zephyr-demos-cl1.elf`와 동일 basename의 `.bin`이다.
명시적으로 선택할 때도 같은 build의 두 파일을 전달한다.

```sh
./run_qbox_zephyr.sh --elf /path/to/zephyr-demos-cl1.elf \
  --image /path/to/zephyr-demos-cl1.bin --dry-run
```

`si_cl1_boot_config()`는 통합 full-system runner와 공유하는 검증 함수다.
ELF entry, PT_LOAD 범위, allocated section과 binary의 일치, post-build image CRC를
검사한다. `--dry-run`도 이 검사를 수행한다. CRC가 후처리된 **배포 binary를 그대로**
LLRAM `0x140000000`에 load하고, 네 CPU의 RVBAR를 ELF entry로 설정한다.
별도 assembly `boot.bin`, guest binary patch, runtime compiler가 필요 없다.
Zephyr의 원래 reset code가 startup voting과 secondary core rendezvous를 수행한다.
ELF를 임의로 objcopy한 binary는 CRC placeholder가 남아 `soc_prep_hook()`에서
정지할 수 있으므로 배포 `.bin`을 대체하지 않는다.

전용 Lua profile은 통합 board가 요구하는 125 MHz counter, CNTP PPI29,
GIC/PL011/LLRAM, MHU 및 SCMI shared memory를 제공한다. AP 쪽 HIPC window는
local shared RAM으로 제공하며 **AP peer는 offline**이다. PFDI는 기존 SystemC
`scmi` / `pfdi-monitor` responder가 protocol version 및 status 요청에 응답한다.
이는 SCP firmware가 실행되거나 AP RPMsg 통신이 검증되었다는 뜻이 아니다.
AP/RSE/SCP CPU와 full-system reset release는 이 경로에서 실행하지 않는다.

기본 headless timeout은 host 120초, interactive timeout은 0(제한 없음)이다.
`--exit-after-pass`는 Zephyr boot banner, CPU 0–3의 OoR 완료와 shell prompt를
모두 관찰하면 종료한다. Interactive tmux/UART/platform log와 F12 종료를 유지한다.
`kernel version`, `kernel uptime` 등의 명령으로 실제 shell 응답을 확인할 수 있다.

QBox Cortex-R82 backend는 EL1 PMSA를 완전히 구현하지 않는다. 현재 통합 image는
`CONFIG_ARM_MPU=y`지만 `CONFIG_ASSERT=n`이고, `z_arm64_mm_init()`는 backend가
보고한 memory-model feature를 지원하지 않아 MPU 설정을 건너뛴다. 따라서 통합
image의 boot/shell 성공은 MPU protection 또는 private TCM 검증이 아니다.
이 launcher 변경은 gem5의 100 MHz standalone benchmark profile이나 full-system
QBox platform의 timer 설정을 변경하지 않는다.

### gem5 통합 이미지 부팅 경로

Launcher는 QBox와 동일한 `si_cl1_boot_config()`로 ELF/배포 binary/CRC를 검증한다.
`ArmFsWorkload`가 ELF를 먼저 적재하고 원본 `.bin`을 LLRAM에 겹쳐 적재하므로
ELF entry/symbol/BSS와 binary-only CRC를 함께 유지한다. Guest image 수정이나
별도 boot stub, runtime compiler는 필요 없다. 네 CPU의 원래 reset voting을 사용한다.

통합 mode는 125 MHz counter와 `SiCl1Mhu`를 추가한다. MHUv3 register는 실제
SET/status/ACK/mask/combined IRQ 상태를 유지한다. PFDI channels 2–5는 protocol
`0x90`의 version (`0x20000`) 및 OoR/Online 요청에 제한된 SCMI 응답을 제공한다.
미지원 protocol/message와 잘못된 length/type은 error 응답을 낸다. HIPC는 AP peer가
없어 pending doorbell을 임의로 ACK하지 않는다. 실제 SCP firmware, PFDI fault
monitoring/recovery, AP RPMsg 통신은 구현·검증 범위가 아니다.

기본 AtomicSimpleCPU는 기능 부팅용이다. 이 mode의 시간·bandwidth를 Cortex-R82AE
성능으로 해석하지 않는다. `--cpu minor`/`timing`은 명시적으로 선택할 수 있다.
통합 image는 benchmark marker를 출력하지 않으며 기존 reporter를 실행하지 않는다.

Interactive는 host timeout/tick 제한 없이 shell을 유지한다. Headless 기본 timeout은
1200초이며 `--exit-after-pass`를 사용해야 네 CPU OoR, Zephyr banner, shell prompt를
확인한 뒤 종료한다. Timeout, simulation limit, fatal/crash는 성공으로 처리하지 않는다.
`result.json`의 `MODEL_BOOT_ONLY`는 이 제한된 functional boot 판정이다.
`manifest.json`에 ELF/binary/native/configuration hash와 실제 명령을 보존한다.

### QBox 통합 이미지 실행 증거 (2026-10-27)

Evidence: `build/qbox-apollo-qvp/zephyr-integrated-shell-20261027/`.
`result.json`은 `PASS`이며, `zephyr-uart.log`에서 다음을 확인했다.

- 원본 통합 Zephyr 4.1.0 boot와 CPU 0–3 OoR 완료.
- `APOLLO_SI1_TIMER cntfrq=125000000 configured=125000000 status=PASS`.
- `PFDI Agent setup complete`, `PFDI service ready (4 CPUs)`.
- 실제 UART 입력 `kernel version` / `kernel uptime`에 대한 shell 응답.

이는 해당 QBox profile의 통합 image 부팅·shell 및 synthetic PFDI 초기화 증거다.
AP peer 통신, 실제 SCP의 PFDI 처리, PMSA 또는 full-system qualification으로 확대하지 않는다.

### gem5 통합 이미지 실행 증거 (2026-10-27)

Evidence root: `build/qbox-apollo-qvp/gem5/si-cl1-integrated-20261027/`.

| 검사 | 결과 | Evidence |
|---|---|---|
| Yocto `gem5-native` build | PASS, 815 tasks | `build-final.log` |
| 통합 image Atomic boot | PASS, 4 OoR / 125 MHz / shell, host 24.50초 | `boot-v2/result.json`, `system.platform.terminal` |
| 실제 tmux/UART/F12 | PASS, 3 panes / `kernel version`, `kernel uptime` 응답 / native process 회수 | `tmux/tmux-check.json`, `uart-clean.txt` |
| MHU/PFDI native MMIO | Atomic/Minor 각각 96 checks PASS | `mhu-{atomic,minor}-v2/result.json`, `system.platform.terminal` |
| 통합 image PFDI shell | CPU0 running / OoR success 100, 4 worker thread 확인 | `pfdi-review/system.platform.terminal` |
| 기존 Minor benchmark | PASS, memory 12 / IRQ 48 / realtime 32, host 152.99초 | `benchmark/result.json`, `report/metrics.json` |
| Host launcher/CRC/tmux regression | PASS, 50 tests | `host-tests-final.log` |

Native SHA256: `5d364f8b8798f0b715a24bee7957e9dda3aeed5b22c8591d266bf61cd6b10e58`.
원본 ELF/binary hash는 QBox 실행 시점과 동일하다. 통합 `.bin` SHA256은
`ed47f0d6c8888f94f9997d780e9b6e9b04bfe2251470f2ffe9bb3014d1ddab76`이다.

첫 compile의 checkpoint array API 오류와 첫 native 초기화의 SimObject parent
순환은 수정했다. 실패 evidence는 `compile-initial-failure.log`, `boot/`에 유지한다.
최종 MMIO probe는 잘못된 길이/type/protocol/message, slot guard, TX ACK,
RX mask/clear, GIC pending/deassert 및 HIPC offline 상태를 실제 guest access로 검사한다.
GIC pending 검사는 CPU exception 진입 또는 실제 SCP fault 처리 검증이 아니다.
추가 shell의 `pfdi info 0`는 vendor library 없는 stub임을 보고한다. OoR SUCCESS를
실제 CPU diagnostic qualification으로 해석하지 않는다. `kernel uptime`은 명령 입력
시점의 simulated uptime이며, Atomic idle의 시간 진행 때문에 host boot 시간과 다르다.
일부 deferred service log는 QBox처럼 UART에 나타나지 않았다. Worker와 PFDI shell
응답은 확인했으나, deferred log delivery 차이의 원인은 아직 확정하지 않았다.

AP Linux full boot, integrated Minor mode, SI checkpoint restore와 hardware timing
calibration은 이번 변경에서 재검증하지 않았다. 기존 benchmark ROI replay도 이번에는
반복하지 않았으며 discovery/report의 functional 및 schedulability 판정만 확인했다.

## gem5 측정 조건과 판정

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

## 초기 standalone 이식 검증 기록 (2026-10-24)

Evidence root: `build/qbox-apollo-qvp/gem5/si-cl1-integration-20261024/`.
아래 QBox 행은 당시 별도 `zephyr-si-cl1-boot` smoke image의 기록이다. 현재 통합
image 경로의 검증으로 바꿔 해석하지 않는다. gem5 benchmark 경로는 그대로 유지한다.

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
