# QEMU/QBox 멀티코어 GDB 동작 분석

> 상태(2026-07-26): Linux secondary CPU bring-up 문제의 추가 구현과
> 런타임 검증은 보류한다. 아래 분석, 실패 경계, 권장 구현안은 후속 작업의
> 기준선으로 유지한다.

## 1. 목적과 기준선

이 문서는 Apollo QVP에서 다음 명령을 실행한 뒤 Linux secondary CPU
bring-up이 멈추는 문제를 구현 전에 분석한 결과이다.

```bash
./run_qbox_local.sh --debug linux
```

분석 기준선은 다음과 같다.

- top-level: `d18e93b2b1822d602e4043f83caa612325e8772a`
- QBox: `a23c5bbe8dc7e3ed53f506c01d3df0a9c1dc5e3a`
- QEMU: `94223e94079ed89b035bc9a9ebc02e1c41fb6a48`
- AP QEMU instance: `MULTI` TCG, Cortex-A720AE 4개
- Linux GDB endpoint: `127.0.0.1:12343`

## 2. QEMU의 멀티코어 GDB 모델

QEMU는 GDB에 CPU cluster를 inferior로, cluster 안의 CPU를 thread로
노출한다. 여러 cluster가 있는 경우 `target extended-remote`, inferior
추가 연결, `set schedule-multiple on`이 필요하다.

Apollo QBox AP CPU는 하나의 QEMU instance에 독립 CPU 객체로 만들어지며
`TYPE_CPU_CLUSTER` 부모나 `cluster_index` 설정을 사용하지 않는다.
QEMU의 CPU 초기값은 `UNASSIGNED_CLUSTER_INDEX`이므로 네 AP CPU 모두 기본
inferior 1의 thread가 된다.

따라서 현재 AP 구성에서는 `schedule-multiple`이 secondary CPU 실패의
핵심 원인이 아니다. 실제 GDB 패킷도 다음과 같이 inferior 1의 전체
thread를 continue했다.

```text
$vCont;c:p1.-1
```

관련 소스:

- `hsoc-stack/tools/qemu/docs/system/gdb.rst`
- `hsoc-stack/tools/qemu/gdbstub/gdbstub.c`
  - `gdb_get_cpu_pid()`
  - `gdb_handle_vcont()`
- `hsoc-stack/tools/qemu/gdbstub/system.c`
  - `gdb_continue_partial()`

## 3. attach와 continue 상태 전이

GDB가 QEMU gdbstub에 연결되면 `gdb_chr_event()`가
`vm_stop(RUN_STATE_PAUSED)`를 호출한다. 이는 다음을 수행한다.

1. QEMU runstate를 `PAUSED`로 변경
2. virtual clock tick 정지
3. 모든 vCPU pause
4. 각 CPU의 `stop/stopped` 상태 반영

GDB `continue`의 `vCont` 처리에서는 선택된 CPU마다 `cpu_resume()`를
호출한다. `cpu_resume()`는 `stop`과 `stopped`를 지우지만 `halted`는
변경하지 않는다.

이는 서로 다른 상태를 의도적으로 구분하기 때문이다.

| 상태 | 소유자/의미 | GDB continue |
| --- | --- | --- |
| `stop` | vCPU 실행 루프 정지 요청 | 지움 |
| `stopped` | vCPU가 QEMU pause에 도달한 상태 | 지움 |
| `soft_stopped` | libqemu/QBox 스케줄러가 보류한 상태 | 유지 |
| `halted` | WFI 또는 전원 상태에 따른 CPU architectural halt | 유지 |
| reset/power state | QBox PPU와 Arm CPU 모델의 전원 계약 | 유지 |

관련 소스:

- `hsoc-stack/tools/qemu/gdbstub/system.c:gdb_chr_event()`
- `hsoc-stack/tools/qemu/system/cpus.c`
  - `do_vm_stop()`
  - `gdb_continue_partial()`
  - `cpu_resume()`
  - `cpu_can_run()`
- `hsoc-stack/tools/qemu/libqemu/wrappers/cpu.c`
  - `libqemu_cpu_can_run()`
  - `libqemu_cpu_halt()`
  - `libqemu_cpu_reset()`

## 4. QBox의 AP secondary CPU release 경로

Apollo AP secondary CPU는 QBox `halt` 신호로 켜지는 것이 아니다.
SI0가 제어하는 `host_ppu.power_on_reset`이 각
`ap_cpu_N.reset`에 연결된다.

PSCI `CPU_ON` 경로는 다음과 같다.

```text
Linux PSCI CPU_ON
  -> TF-A BL31 SCMI power-domain request
  -> SI0 SCP
  -> host_ppu power-on reset pulse
  -> ap_cpu_N.reset
  -> QemuCpu::reset_cb(false)
  -> QemuCpu::release_start_in_reset()
  -> CpuArm power on + soft_stopped 해제 + reset 해제
```

`release_start_in_reset()`은 CPU의 async-safe work queue에서 전원과 reset
상태를 바꾸고 완료 이벤트를 SystemC 쪽에 알린다. 따라서 GDB가 모든 CPU의
`stop/stopped`를 변경한 이후에도 이 work item이 확실히 실행되어야 한다.

관련 소스:

- `hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/ap_compute.lua`
- `hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/si_cl0.lua`
- `hsoc-stack/tools/qbox/qemu-components/common/include/cpu.h`
  - `reset_cb()`
  - `release_start_in_reset()`
- `hsoc-stack/tools/qemu/libqemu/wrappers/cpu.c`
  - `libqemu_cpu_reset()`

## 5. 현재까지 확인된 실패 경계

호스트 QBox와 guest AP QEMU에 GDB를 동시에 연결해 실제 실패 경계를
측정했다.

- 호스트 QBox: gdbserver `127.0.0.1:12339`
- guest AP QEMU: gdbstub `127.0.0.1:12343`
- Linux `start_kernel` 정지 시:
  - CPU0: `start_kernel`, running
  - CPU1~3: `0x82000`, halted
- `rest_init` 이후 실패 시:
  - Linux 마지막 로그: `smp: Bringing up secondary CPUs ...`
  - CPU0 PC: `0x1101c`
  - CPU1~3 PC: `0x82000`, halted 유지

`bl31.elf`로 `0x1101c`를 역해석한 결과는
`scmi_send_sync_command()`의 SCMI mailbox-free polling loop이다.
SI0 로그에는 이 Linux 요청 이후의 CPU1 power-on 기록이 없었다. SI0에
있던 CPU1~3 on/off 기록은 Linux 부팅보다 앞선 BL31 PFDI OoR 검사이다.

호스트 GDB에서 `libqemu_cpu_reset()` 계열 5개 shared-library 위치에
breakpoint를 설치했지만 Linux 실패 동안 CPU1 reset에는 도달하지 않았다.
따라서 현재 실패는 CPU1 reset release나 secondary entry 이후 문제가
아니라, CPU0의 AP-to-SI0 SCMI 요청/응답 동기화 단계에서 먼저 발생한다.

실행 증거:

- `build/qbox-apollo-qvp/linux-gdb-dual-state3-20260726-1405/`
- `host-state-at-start-kernel.txt`
- `guest-state-at-start-kernel.txt`
- `guest-state-at-smp-stall.txt`
- `qbox-primary-console.log`
- `qbox-safety-island-cl0.log`

## 6. QBox time-sync 경계

Apollo AP Lua 구성에는 `time_sync_strategy` override가 없다. 따라서 현재
AP 인스턴스는 QBox `QemuInstance` 기본값인 `quantum_keeper`를 사용한다.
`sync_policy=multithread-quantum`은 quantum keeper의 정책 설정이며
`time_sync_strategy=mcips` 선택과는 다르다.

정상 `halt` 신호 경로는 다음과 같이 time-sync lifecycle을 대칭으로
처리한다.

```text
QemuCpu::halt_cb(true)
  -> CpuTimeSyncStrategy::on_halt_pre(true)
  -> BQL lock
  -> Cpu::halt(true)
  -> BQL unlock
  -> CpuTimeSyncStrategy::on_halt_post()
```

Quantum keeper에서는 `on_halt_pre(true)`가 deadline timer를 삭제하고
QK를 멈춘다. 반대로 resume 경로는 QK를 시작하고 deadline timer를 다시
설정해야 한다.

현재 PC-entry debug hook은 다음과 같이 이 lifecycle을 우회한다.

```cpp
if (pc == p_gdb_breakpoint && first_hit) {
    m_cpu.halt(true);
}
```

GDB `continue`는 QEMU 내부에서 `cpu_resume()`를 호출한다. 따라서 QBox의
`halt_cb(false)`나 time-sync resume hook은 호출되지 않는다. 이 비대칭이
guest instruction 실행은 재개하지만 QBox/SystemC 동기화와 deadline
상태는 debug-stop 이전 계약으로 복구하지 못하는 핵심 후보이다.

MCIPS 전용 idle 처리 변경도 실험했지만 현재 AP가 MCIPS를 사용하지 않아
실행 경로에 영향을 주지 않았다. 해당 실험 변경은 모두 제거했다.

## 7. 권장 구현안

### 7.1 1순위: QBox PC-entry pause lifecycle 대칭화

QEMU를 변경하지 않고 `QemuCpu` 안에서만 다음 상태 전이를 추가한다.

1. PC-entry 첫 hit에서 debug-pause 상태를 설정한다.
2. 현재 time-sync strategy의 pause hook을 호출한다.
3. CPU를 정지하고 기존 marker를 출력한다.
4. GDB `continue`로 `m_cpu.can_run()`이 다시 참이 된 시점을
   `prepare_run_cpu()`에서 감지한다.
5. debug-pause 상태를 원자적으로 해제하고 time-sync resume hook과
   deadline rearm을 호출한다.
6. 기존 QEMU runstate와 CPU1~3 reset/power 상태는 변경하지 않는다.

이 방식은 변경 범위가 QBox `cpu.h` 한 파일로 제한되고, 현재
quantum-keeper 경로와 향후 MCIPS 경로가 같은 lifecycle interface를
사용할 수 있다. 단, `McipsSync`의 halt hook은 현재 no-op이므로 Apollo
AP에 `time_sync_strategy=mcips`를 실제로 적용할 때는 별도
debug-pause/resume 동작을 구현하고 검증해야 한다.

### 7.2 2순위: libqemu debug stop/resume callback 추가

QEMU gdbstub의 `vm_stop()`과 `gdb_continue_partial()`에서 libqemu 전용
callback을 제공하고 QBox가 이를 받아 time-sync를 정지/재개하는 방법이다.
QEMU native breakpoint, Ctrl-C, single-step까지 한 계약으로 처리할 수
있다는 장점이 있다.

반면 변경 범위가 QEMU gdbstub, libqemu export, QBox C++ wrapper,
`QemuCpu`까지 확장된다. Apollo처럼 QEMU shared library를 여러 namespace로
로드하는 구성에서 instance별 callback 소유권도 검증해야 한다. 1순위
구현으로 PC-entry 문제가 해결되지 않거나 Ctrl-C/step까지 완전한
동기화가 필요할 때 적용한다.

### 7.3 비권장안

- GDB `schedule-multiple on` 강제: 현재 AP는 단일 inferior이므로 원인과
  무관하다.
- Linux/TF-A/PPU timeout 증가: SCMI 응답이 오지 않는 동기화 오류를
  숨길 뿐이다.
- GDB continue에서 CPU1~3의 `stop/stopped`를 별도로 복원: CPU1 reset
  경로에 도달하기 전에 실패하므로 현재 증거와 맞지 않는다.
- debug stop마다 전체 SystemC `sc_pause()` 호출: 다른 도메인 디버깅과
  외부 이벤트 처리를 함께 막고 resume 소유권이 복잡해진다.

## 8. 구현 후 검증 기준

다음 조건을 한 세션에서 모두 만족해야 한다.

1. `./run_qbox_local.sh --debug linux`가 `start_kernel` 소스에서 정지
2. `info threads`에서 AP CPU0~3이 한 inferior의 thread로 표시
3. `start_kernel`과 `rest_init`에서 각각 30초 이상 정지 후 continue
4. SI0가 Linux 요청에 따른 CPU1~3 power-on을 처리
5. Linux가 CPU1, CPU2, CPU3의 secondary processor boot를 출력
6. Linux가 4개 CPU를 online으로 보고
   `NEXIOS_BSP_INITRAMFS_READY`와 `nexios-bsp#`에 도달
7. 같은 build로 non-debug local boot도 BSP shell에 도달
8. PFDI timeout이나 SCMI mailbox busy 고착이 없음

추가로 QEMU multi-namespace 호스트 GDB에서는 같은 이름의
`libqemu-system-aarch64.so`가 여러 번 로드된다. 단순
`cpus_queue` 조회는 한 namespace만 가리킬 수 있으므로 CPU1 분석에는
instance별 symbol 위치 또는 `libqemu_cpu_reset()`의 multi-location
breakpoint를 사용해야 한다.

## 9. 참고

- QEMU 공식 문서:
  <https://www.qemu.org/docs/master/system/gdb.html#debugging-multicore-machines>
- Apollo QBox platform 설명:
  `hsoc-stack/tools/qbox-platform/platforms/apollo/README.md`

## 10. Yocto 산출물 GDB 구성

`run_qbox_yocto.sh`도 local-build launcher와 같은 target 이름과 GDB pane
계약을 사용한다.

```bash
./run_qbox_yocto.sh --debug
./run_qbox_yocto.sh --debug rse
./run_qbox_yocto.sh --bsp --debug tf-a
./run_qbox_yocto.sh --debug qbox
```

`--debug`는 대화형 tmux pane을 사용하므로 `--headless`와 함께 사용할 수
없다. 실제 실행에서는 선택한 Yocto workdir ELF로
`OUT_DIR/debug/symbols.json`과 GDB command file을 생성하고 다음 조건을
모두 검사한다.

- `.debug_info`와 `.debug_line` 존재
- target entry symbol과 source line 존재
- QBox host는 실행 파일과 debug ELF의 Build ID 일치
- 선택한 GDB port가 사용 중이지 않음

Yocto artifact 위치는 deploy image가 아니라 다음 workdir ELF가 기준이다.

| target | Yocto ELF |
| --- | --- |
| `qbox` | `qbox-apollo-qvp-native/*/build/platforms-vp` |
| `rse` | `trusted-firmware-m/*/build/bin/bl1_1.elf` |
| `si_cl0` | `scp-firmware/*/build/ramfw/si0/bin/*-si0-bl2.elf` |
| `si_cl1` | `*_safety_island_c1-zephyr/zephyr-demos-cl1/*/build/zephyr/zephyr.elf` |
| `tf-a` | `trusted-firmware-a/*/build/apollo_qvp/debug/bl2/bl2.elf` |
| `u-boot` | `u-boot/*/build/u-boot` |
| `linux` | `linux-*/*/build/vmlinux` |

TF-M, SCP-firmware, U-Boot의 DWARF에는 `/usr/src/debug/...` 경로가 기록될
수 있다. manifest 생성기는 실제 workspace source suffix를 찾아 GDB
`set substitute-path`를 자동 생성한다.

QBox native recipe는 source-level host debug를 위해
`RelWithDebInfo`로 빌드한다. sysroots-components의 runtime
`platforms-vp`는 strip될 수 있으므로 GDB는 동일 Build ID를 가진 workdir
ELF를 symbol file로 사용한다.

Apollo QVP defconfig는 `CONFIG_DEBUG_INFO_DWARF_TOOLCHAIN_DEFAULT`,
`CONFIG_GDB_SCRIPTS`, `CONFIG_KALLSYMS_ALL`을 활성화한다. 변경 전에
생성된 `vmlinux`에는 DWARF가 없으므로 커널을 다시 빌드해야
`--debug linux`의 엄격한 검사를 통과한다. Linux SMP debug 런타임
검증은 계속 보류하며, 재개할 때는 image 크기와 빌드 시간 영향 및 앞
절의 SCMI/time-sync 문제를 함께 검증해야 한다.
