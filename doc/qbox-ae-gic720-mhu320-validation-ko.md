# Apollo QVP GIC-720AE / MHU-320AE AE 구현 및 검증

작성일: 2026-10-23. 대상은 `MACHINE=apollo-qvp`, `nexios-image`,
`build/tmp_baremetal`의 QBox provider와 실제 RSE/SI0/SI1/AP firmware다.
아래 기능은 소프트웨어가 관찰하는 기능 모델이다. ECC 회로, lockstep 비교기,
물리 오류율, ASIL 진단 커버리지 또는 FVP 타이밍 동등성을 검증한 결과가 아니다.

후속 FMU 감사에서 정상 byte-enable KEY 쓰기 거부와 MHU의 서로 다른 SMID
overflow 누락을 재현했다. 아래 PASS는 당시 실행한 시나리오에 한정되며
FMU 전체 구현 판정이 아니다. [TRM gap 조사](qbox-ae-trm-gap-analysis-ko.md)에
추가 구현과 소프트웨어 변경 목록, 원 실패 증거 및 GIC/MHU의 OF 규칙 차이를 정리했다.
두 결함의 수정과 FMU 명령 상태, GIC routing/GICT, MHU 실제 RAM 검출 및
firmware 복구 변경은 [후속 구현·검증 기록](qbox-ae-followup-validation-ko.md)에
분리했다. 아래 실행 수치와 수동 절차는 첫 구현 당시의 보존 기록이다.

## 근거와 구현 범위

주 근거는 저장소에 보존한 Arm 공식 TRM이다.

- [GIC-720AE r2p1, 102666/0201](https://developer.arm.com/documentation/102666/0201):
  [Functional safety](gic-720ae/0007-Functional-safety-in-GIC-720AE.md),
  `GICD_ICERR/ICGERR/ISERR/ICVERR`, `GICR_ICERR0/ISERR0`, FMU register summary.
- [MHU-320AE r0p1, 107612/0001](https://developer.arm.com/documentation/107612/0001):
  [Fast channels](mhu-320ae/0014-Fast-channels.md),
  [FST_ERRINS](mhu-320ae/0244-MBX_FST_ERRINS-Mailbox-fast-channel-RAM-ECC-Error-Insertion-Register.md),
  SRAS/RRAS 및 FMU register summary와 recovery 절차.

| TRM 기능 | 구현 | 검증 경계 |
| --- | --- | --- |
| GIC SPI / SGI / PPI error state | `gicx00_multiview`: ISERR, ICERR, ICGERR, ICVERR, view/group ownership 검사 | Backend enable 차단, 잘못된 view 및 Non-secure recovery 거부, 명시적 재설정 후 enable |
| GIC functional control | 지원 FCTLR bit mask와 synchronous scrub completion | RAM scrub 지연이나 실제 ECC 생성 없음 |
| GIC/MHU FMU | `zena_device_fmu`: GIC 12 / MHU 6 records, BLKTYPE/BLKID/SMID, criticality, enable, injection, page read/write | 보호 메커니즘의 제어·관찰 interface; 실제 보호 회로 없음 |
| FMU recovery | one-shot KEY, Secure access, queue/overflow, W1C V/UE/OF, ERRUPDATE의 record pair, reset | 주입 상태 clear와 독립 hardware-event 상태를 분리 |
| FMU hierarchy | leaf level → `zena_fmu` child record → root summary → SI0 IRQ/SSU | 상위 먼저 acknowledge해도 leaf가 남으면 다시 latch |
| MHU FCE | 32/64-bit payload, split 64-bit access, latest-value, group pending, read-clear, combined IRQ | active Apollo는 64 × 32-bit, 32 channels/group; FIFO extension은 미구현 |
| MHU local RAS | 선택적 SRAS/RRAS, CE count/overflow, CE/UC ERRINS, error summary 및 W1C | AP/SI0 NS endpoints에서 guest polling; local RAS IRQ 배선은 미구현 |
| MHU reset/pair | 동일 pair에만 전달, reset peer에 stale delivery/replay 방지, reset 후 재송신 | OP_REQ를 전송 enable로 잘못 해석하지 않음 |

FMU 소프트웨어 injection과 MHU RAM ERRINS는 서로 다른 동작이다. ERRINS는
payload를 유지하며 local RAS에 오류를 기록한다. 이를 물리 ECC 검출이나
독립 FMU protection event로 자동 변환하지 않는다.

## 소유 저장소와 실제 연결

| 소유 저장소 | 변경 영역 |
| --- | --- |
| `hsoc-stack/tools/qbox-platform` | GIC wrapper, MHU, leaf/System FMU, Lua 배선, component 및 실제 CPU tests |
| `hsoc-stack/tools/qbox` | module factory의 optional multi-target TLM socket binding |
| `hsoc-stack/components/system_mgmt/scp-firmware` | MHU3 FCE driver, active QVP FMU driver, SI0 진단 및 AP view 설정 |
| root | Lua descriptor/주소 계약 검사, 본 문서 및 기존 상태 문서 |

AP GIC의 관리 View0는 `0x20000000`, AP가 사용하는 View1은 `0x20800000`이다.
Redistributor는 각각 `0x20080000` / `0x20880000`부터 stride `0x40000`이다.
두 view 모두 `ap_gic_multiview`를 거쳐 private `ap_gic_backend_router`의
libqemu GIC로 전달한다. 원래 `platform.ap_gic` 객체, IRQ socket 번호 및
ITS `0x20840000` 경로는 유지한다. QEMU MemoryRegion hint가 wrapper를
우회하는 직접 alias를 만들지 못하도록 차단해야 error containment가 유지된다.
Managed payload도 hint를 즉시 제거한다. AP 전원 reset은 SCP가 설정한 view를
유지하고 전체 system reset만 wrapper를 초기화한다. SCP가 없는 Linux 직접
실행 profile은 기존 AP 부트 스텁에서 SPI/redistributor View1 및 view enable을
설정한다. Loader는 파일만 적재하고 GIC MMIO는 CPU 실행 후 수행한다.

SI의 기존 CL0/CL1은 독립 libqemu GIC 두 개를 사용한다. 현재 SI의 multiview
metadata overlay와 FMU 연결을 AP의 단일 backend containment 증거로
대체하지 않는다. SI 실제 IRQ source containment는 현재 backend 배선에서
미구현(`UNSUPPORTED`)이다.

Apollo의 실제 MHU 15개 pair / 30개 endpoint에는 FCE geometry를 명시한다.
`fast_channel_count=64`, `fast_channels_per_group=32`,
`fast_channel_word_bits=32`는 QVP 기능 구성값이며 실리콘 synthesis 값이라는
주장이 아니다. `ras_enable=true`는 AP↔SI0 non-secure 두 pair의 네 endpoint에
한정한다. Local RAS `fault_irq/error_irq`는 CPU에 연결하지 않는다.

SI0의 GIC FMU 하나와 MHU FMU 열 개는 기존 parent bank/record를 유지하며
level 방식으로 System FMU에 연결된다. System reset은 leaf를 먼저 reset하고
parent를 reset한다. 기존 NI-710AE와 CPU RAS 경로는 유지한다.

## 소프트웨어 변경

- MHU3의 N-1 channel count, 그룹별 register stride, partial last group,
  payload 크기 검사와 IN channel IRQ callback 처리를 수정했다.
- 하드웨어 FCE를 `SCMI_PERF_FAST_CHANNELS`와 분리해 켰다. SCMI 성능 제어는
  기존 doorbell 방식이며 주기적 SCMI fast-channel polling을 다시 켜지 않는다.
- `apollo-qvp/si0_ramfw`의 AP non-secure FCE 채널 32에 진단용 IN/OUT을
  예약했다. `test mhu_fce`는 실제 MHU3 ISR callback에서 payload를 읽고
  bitwise complement 응답을 실제 PBX로 보낸다.
- QVP FMU driver의 ERRUPDATE write 주소/값, `record_id / 2` 선택,
  V/UE/OF acknowledge와 timeout 전파, record별 IRQ enable을 수정했다.
- AP GIC을 View1으로 접근할 수 있도록 QVP SCP가 구현된 모든 AP SPI
  INTID 32–991을 View1에 배정한다. SI의 CL0/View1, CL1/View2 표와
  GIC security group 설정은 유지한다. 배포 ELF에서 AP map의 `.bss`는
  3,840 bytes이며 근거는 `scp-firmware-size.json`이다.
- Linux mailbox driver는 doorbell을 계속 사용한다. AP에서 FCE 응답 IRQ를
  마스킹하고 polling하며, SI0 방향은 실제 combined IRQ를 사용한다.

## 재현

공유 BitBake 작업은 반드시 순차 실행한다. 현재 설정과 실행 인자는
`build/qbox-apollo-qvp/ae-20261023/`에 보존했다.

```bash
./yocto_build.sh scp-firmware -c deploy
./yocto_build.sh qbox-apollo-qvp-native -c check
./yocto_build.sh qbox-apollo-qvp-native -c populate_sysroot
python3 -m pytest -q tests/test_apollo_lua_descriptor.py
python3 -m pytest -q tests/test_apollo_linux_lua.py
python3 scripts/test/validate_qbox_apollo_fvp_full_map.py
python3 scripts/run/run_qbox_linux.py --headless --copy-disk --exit-after-pass \
  --timeout 180 --out-dir build/qbox-apollo-qvp/ae-linux-recheck
```

실제 CPU test는 Yocto `do_check`에도 포함된다. 단독 재현:

```bash
ctest --test-dir build/tmp_baremetal/work/x86_64-linux/qbox-apollo-qvp-native/1.0/build \
  -R '^apollo-gic-ae-containment$' --output-on-failure --no-tests=error
```

실제 A720AE가 SPI INTID 105를 acknowledge한 후 ISERR로 격리한다.
격리 중 다시 enable/pend를 시도해도 IAR은 spurious 1023이어야 한다.
View/group/error 복구, 설정 재작성 및 명시적 enable 이후 다시 105여야 한다.
이 검사는 QEMU/libqemu CPU 및 IRQ 전달 경로를 사용한다.

Full-system 실행은 `run_qbox_yocto.sh`의 boot-only 경로 대신 canonical
`scripts/run/run_qbox_apollo_fvp_full.py --post-login-probe`를 사용한다.
자동 시나리오는 증거 디렉터리의 `guest-check.py`, 입력은
`baseline-command.json`, 각 실행의 최종 인자는 `invocation.json`에 있다.
원본 rootfs/EFI image는 reflink 복제하고 RSE flash state도 실행별로 분리한다.

FCE 수동 재현은 다음 순서다. 두 콘솔을 동시에 열고 SI0의 READY를 기다린다.
현재 `nexios-image`에는 `devmem`이 없으므로, 포함된 Python `mmap`/`ctypes`로
폭과 alignment를 명시하여 접근한다. AP root shell에 다음 함수를 정의한다.
AP의 PBX/MBX 주소는 DTS의 `0x40020000` / `0x40050000`이다. ATU 이후의
시스템 주소 `0x400003b000000` / `0x400003b040000`를 `/dev/mem`에 사용하지 않는다.

```sh
mmio() {
    python3 - "$@" <<'PY'
import ctypes, mmap, os, sys
address, width = (int(value, 0) for value in sys.argv[1:3])
assert width in (32, 64) and address % (width // 8) == 0
fd = os.open("/dev/mem", os.O_RDWR | os.O_SYNC)
with mmap.mmap(fd, mmap.PAGESIZE, offset=address & -mmap.PAGESIZE) as page:
    word = getattr(ctypes, f"c_uint{width}").from_buffer(page, address % mmap.PAGESIZE)
    if len(sys.argv) == 4:
        word.value = int(sys.argv[3], 0)
    else:
        print(f"0x{word.value:X}")
    del word
os.close(fd)
PY
}
```

| 단계 | 콘솔 | 명령 / 기대 |
| --- | --- | --- |
| 1 | AP | `mmio 0x40050140 32` 값을 저장하고 bit 2를 clear하여 AP FCE IRQ 마스크 |
| 2 | SI0 | `test mhu_fce` → `MHU_FCE_READY channel=32 payload=0x320ae001` |
| 3 | AP | `mmio 0x40023080 32 0x320ae001` |
| 4 | SI0 | `MHU_FCE_PASS channel=32 irq_count=1 reply=0xcdf51ffe` |
| 5 | AP | `mmio 0x40050484 32`의 bit 0이 1 |
| 6 | AP | `mmio 0x40053080 32` → `0xCDF51FFE` |
| 7 | AP | 다시 `0x40050484` 읽으면 bit 0이 0; 저장한 FCH_CTRL 복구 |

여기서 `irq_count`는 진단이 수락한 ISR callback 수다. 전체 GIC IRQ 진입
횟수를 뜻하지 않는다. 진단은 예약된 채널 32를 사용하며 다른 미등록 FCE
채널의 소프트웨어 서비스까지 검증하지 않는다.

## 실행 결과

변경한 provider 및 SI0 firmware를 함께 배포한 `guest-9`에서 AP4 Linux
부팅, 기본 post-login 검사, SSU/FMU와 FCE/RAS를 통과했다. Post-login 판정은
8개 driver marker와 `failed_units_count:0`에 한정하며, 선택적 secure-service,
FWU 및 DWC probe를 통과했다는 뜻이 아니다. 아래 상대 증거 경로는
`build/qbox-apollo-qvp/ae-20261023/` 기준이다.

| 검사 | 상태 | 증거 |
| --- | --- | --- |
| Lua AP4/AP16 descriptor, Linux profile 및 주소 계약 | PASS 29개 | `descriptor-tests-final.log`, `full-map-validation-final.json` |
| SCP MHU3 host unit tests 36개 | PASS | `../ae-software/mhu3-unit.log` |
| QVP FMU driver host tests 7개 | PASS | `../ae-software/fmu-unit.log` |
| QVP AP/SI GIC view 설정 host test | PASS | `../ae-software/gic-map-test.log` |
| provider 전체 CTest | PASS 70/70 | `provider-install-7.log`, `provider-ctest-7.log` |
| 실제 A720AE GIC containment/recovery | PASS | `irq-tests-6.log`: 105 → 1023 → 105, canonical View1 |
| AP4 full-system boot / 기본 post-login | PASS | `guest-9/ae-result.json`, `guest-9/qbox-primary-console.log` |
| 실제 SI0 SSU / FMU 진단 | PASS 1 / 20개 | `guest-9/qbox-safety-island-cl0.log` |
| AP → SI0 FCE 실제 IRQ → AP reply / read-clear | PASS | `guest-9/ae-result.json`: 채널 32, reply `0xcdf51ffe` |
| AP MBX FCE CE/UC local RAS | PASS | CE `0xc6000006`, UC `0xe4300006`; summary set/W1C clear, payload 보존 |
| SCP 없는 AP4 Linux 직접 부팅 / CPU·disk smoke | PASS | `linux-direct-2/result.json`, `linux-direct-2/linux-uart.log`; SI/RSE는 mock |
| source/설치 Lua 111개 및 boot/README 일치 | PASS 114/114 | `installed-source-match-final.json` |

`implementation-manifest-final.json`은 변경 소스와 설치 module/실행 파일/SI0
binary SHA-256을 기록한다. 마지막 설치 후에도 `guest-9`에서 사용한 runtime
artifact 7개가 모두 동일함을 `runtime-artifacts-match-guest9.json`으로 확인했다.
전체 검사 요약은 `verification-summary.json`에 있다.

Provider의 70개 CTest에는 GIC wrapper 24개 gtest, MHU/FMU component suite와
실제 A720AE containment test가 포함된다. QBox core 전체 CTest는 recipe 설정에서
비활성화되어 있다. 이번 core optional socket binding 변경은 실제 container를
사용하는 leaf FMU test 및 full-system elaboration으로 검증했다.

RAS 주입은 MBX의 `FST_ERRINS +0xf018`에 CE `0x8000002000008000`,
UC `0x8000002080018000`을 64비트 write한다. RRAS record 4/5의 `ERRSTATUS`
(`+0x10110` / `+0x10150`)와 `ERRGSR +0x10e00`을 확인하고 `ERRSTATUS`에
`0xff000000`을 써서 acknowledge한다. 정확한 실행 명령은
`guest-9/commands.json`에 있다. 이 검사는 local RAS IRQ handler를 검증하지 않는다.

실패 로그는 삭제하지 않는다. `guest-1`은 optional multi-target socket의
동적 binding 누락으로 elaboration에 실패했다. `guest-2`는 Lua View1
redistributor 소켓 이름 오류로 elaboration에 실패했고 실제 region socket과
AP stride에 맞게 수정했다. `guest-3`–`guest-5`의 secondary CPU GICR discovery
실패는 managed payload에 남은 QEMU MemoryRegion hint와 AP 전원 reset이
SCP view map을 지우는 문제를 추적하는 근거다. Hint를 즉시 제거하고 reset
소유권을 수정한 뒤 `guest-6`부터 AP4가 부팅했다. `guest-6`의 SI0 UART FIFO
누락, `guest-7`의 `devmem` 부재, `guest-8`의 시스템 주소/AP 주소 혼동은
검증 harness에서 수정했다. `irq-tests-1` 이후 CPU 검사에서 확인한 view enable
fixture 오류도 수정했다.
이전 FMU test의 elaboration/미연결 socket 실패도 원본 로그로 보존한다.
`linux-direct`는 elaboration 단계의 GIC MMIO로 실패했다. 해당 초기화를
파일 loader에서 기존 AP `linux-boot/boot.S`로 옮겨 실행 시점을 수정했다.

## 남은 경계

- GIC RAM ERRINS/GICT RAS 전체, 물리 ECC/lockstep/parity/CRC 및 PING
  timing은 미구현이다. FCTLR completion은 기능적이며 주기 정확하지 않다.
- MHU FIFO/security-control extension, local RAS IRQ의 guest handler,
  clock/power Q-channel 모델은 미구현이다.
- FMU page interface 중 timeout 저장/조회는 실제 보호 통신의 timeout 검출을
  의미하지 않는다. 실제 보호 회로의 coverage로 해석하지 않는다.
- AP16은 Lua 정적 구성 검사 범위다. 이번 full-system 실행은 AP4이며
  FVP/실리콘 비교와 ASIL qualification은 수행하지 않는다.
