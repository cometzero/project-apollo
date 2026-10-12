# SI CL0 fast-channel polling / interrupt-safe WFI 분리 측정

2026-10-06. Apollo QVP Saturn-V의 BSP 부팅 후 idle 상태를 비교한다.
기존 [runtime idle 개선 기록](qbox-runtime-idle.md)은 여러 변경의 결합 효과다.
이번에는 SCP의 두 CMake 옵션만 바꾸어 각각의 영향을 측정했다.

## 측정 조건

- `MACHINE=apollo-qvp`, `TMPDIR=build/tmp_baremetal`,
  `nexios-bsp-initramfs`, SI CL0 TCG `MULTI`.
- Linux UART에서 `NEXIOS_BSP_INITRAMFS_READY`와 `nexios-bsp#`를 모두 확인하고
  **20초 안정화 후 30초씩 2구간** 측정한다. 부팅 시간은 집계에서 제외한다.
- 구성별 독립 cold boot 2회, 총 120초를 집계한다.
  순서는 A → B → C → D → D → C → B → A이다.
- guest 명령, workload, fault injection, GDB/perf를 실행하지 않는다.
  QMP CPU TID 조회는 측정 전에, simulation time 조회는 구간 경계에서만 한다.
  PFDI 및 정상 firmware timer/서비스는 유지한다.
- 모든 실행에 `--no-vmcu`를 사용한다. 외부 TC397/SIL Kit 연동 부하는 포함하지
  않으며, SCP에 컴파일된 safety-channel 처리는 동일하게 유지한다.
- AP disk는 실행별 복사본, RSE state는 비영속 상태를 사용한다.
  빌드를 먼저 완료하여 측정과 겹치지 않게 했다.
- 호스트는 Ryzen 7 PRO 4750G, Linux 6.8.0-142-generic, governor `powersave`다.
  CPU pinning이나 호스트 독점 격리는 하지 않았다.

부하는 QMP `query-cpus-fast`로 식별한 SI CL0 vCPU thread의
`/proc` user+system CPU 시간 차이를 wall time으로 나눈 값이다.
**100%는 호스트 논리 CPU 하나이며, 실제 SI 코어의 사용률이나 소비전력이 아니다.**
전체 QBox CPU는 다른 도메인 및 SystemC/helper thread도 포함한다.

## 결과

| 구성 | Fast-channel polling | Interrupt-safe WFI | SI CL0 평균 | 부팅별 평균 범위 | 전체 QBox | sim/host |
|---|---|---|---:|---:|---:|---:|
| A | ON | OFF (WFE) | 98.13% | 97.97–98.29% | 105.92% | 1.001137 |
| B | OFF | OFF (WFE) | 98.20% | 98.17–98.22% | 108.81% | 1.001102 |
| C | ON | ON | 3.53% | 3.47–3.60% | 13.36% | 1.001247 |
| D (현재 기본) | OFF | ON | 3.87% | 3.80–3.93% | 19.75% | 1.001234 |

평균은 CPU 시간 합 / 측정 wall time 합으로 계산했다. 범위는 두 부팅의
각 60초 평균이며 신뢰구간이 아니다. 전체 8회 부팅과 16개 측정 구간이 PASS였다.

| 비교 | SI CL0 변화 | 해석 |
|---|---:|---|
| WFI OFF에서 polling 제거 (A → B) | +0.07%p | 상대 0.07% 증가 |
| polling ON에서 WFI 적용 (A → C) | -94.60%p | 상대 96.40% 감소 |
| WFI ON에서 polling 제거 (C → D) | +0.33%p | 상대 9.43% 증가 |
| polling OFF에서 WFI 적용 (B → D) | -94.33%p | 상대 96.06% 감소 |
| 두 변경 결합 (A → D) | -94.26%p | 상대 96.06% 감소 |

**이번 idle 조건에서 부하 감소의 주된 요인은 interrupt-safe WFI 적용이다.**
polling만 끈 B는 A와 거의 같고, WFI 상태에서 끈 D는 C보다 0.33%p 높았다.
따라서 polling 제거가 추가 CPU 절감을 제공했다고 결론내릴 수 없다.
후자의 작은 증가 원인은 이 실험으로 분리하지 않았다. Fast-channel capability와
AP의 SCMI 경로도 함께 달라지므로 timer 제거 자체의 순수 비용으로 해석하지 않는다.

SI CL0 CPU seconds / simulation second는 A 0.98019, B 0.98089,
C 0.03528, D 0.03861이다. sim/host는 모두 약 1.001로 유지되어
시뮬레이션 진행 속도 감소가 큰 부하 차이를 설명하지 않는다.

전체 QBox 비용도 WFI 적용 시 낮아지지만 AP 등 다른 thread의 비용이 포함되므로
SI CL0 개선량은 위 SI CL0 열로 판단한다. 기존 문서의 97.73% → 1.39%는
다른 시점의 여러 변경을 합친 수치이며 이번 개별 효과와 혼용하지 않는다.

## WFI만 재측정 (2026-10-06)

사용자 요청에 따라 fast-channel polling을 **OFF로 고정**하고 WFI만 다시
비교했다. 앞선 결과와 합산하지 않은 독립 측정이다. SHA256을 확인한 동일
펌웨어를 사용했으며 실행 순서는 OFF → ON → ON → OFF였다. 각 부팅에서
BSP READY와 shell prompt 확인 후 20초 안정화, 30초 × 2구간을 측정했다.
PFDI 유지 및 외부 vMCU 미실행 등 나머지 조건은 앞선 실험과 같다.

| WFI | 1회 부팅 평균 | 2회 부팅 평균 | 최종 SI CL0 평균 | 전체 QBox 평균 | sim/host |
|---|---:|---:|---:|---:|---:|
| OFF (기존 WFE) | 98.41% | 98.29% | **98.35%** | 108.99% | 1.001170 |
| ON | 3.88% | 3.67% | **3.77%** | 19.44% | 1.001230 |

**WFI 적용으로 94.57%p, 상대 96.16% 감소**했다. 이전 동일 조건의
98.20% → 3.87%와 같은 수준이다. SI CL0 CPU seconds / simulation second도
0.98233 → 0.03770으로 감소했다. 모든 4회 부팅과 8개 측정 구간이 PASS이며,
runner의 PFDI 오류 marker는 검출되지 않았다. 부팅별 범위는 신뢰구간이 아니다.

[재측정 원본](../build/qbox-apollo-qvp/si0-idle-ablation/wfi-repeat/)의
`run.py`, `matrix.log`, `summary.json` 및 `off1/on1/on2/off2/idle-load.json`에
실행 순서, 이미지 hash, 원본 counter와 집계 결과를 보관한다.

## 변경의 의미와 해석 범위

[Firmware.cmake](../hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/si0_ramfw/Firmware.cmake)의
`SCP_ENABLE_SCMI_PERF_FAST_CHANNELS` 및 `SCP_ENABLE_WFI_IDLE`을 ON/OFF로 바꿨다.
현재 기본값은 각각 OFF/ON(D)이다.

Fast-channel polling은
[si0_cfgd_scmi.h](../hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/si0_ramfw/include/si0_cfgd_scmi.h)의
40,000 µs, 즉 초당 25회 주기다. OFF는 해당 polling 모듈뿐 아니라 SCMI
fast-channel capability도 제거한다. 따라서 Linux의 일반 SCMI mailbox
`LEVEL_SET`/`LEVEL_GET` 경로 사용까지 포함한 **기능 옵션 전체의 효과**다.
활성 전송 동안의 MHU ACK polling과 다른 firmware 주기 작업은 남아 있다.

WFI ON은 [fwk_core.c](../hsoc-stack/components/system_mgmt/scp-firmware/framework/src/fwk_core.c)의
event queue drain → IRQ mask → normal/ISR queue 재확인 → `DSB; WFI` → IRQ 복원을
사용한다. OFF의 기존 대기 명령은 `WFE`다. 네 ELF의 disassembly로 확인했다.
따라서 이 비교는 **interrupt-safe WFI 구현 전체 대 기존 WFE**이며,
IRQ masking만의 비용이나 safe WFI 대 unsafe WFI를 분리한 실험은 아니다.

각 구성의 2회 부팅은 작은 표본이다. 작은 차이의 통계적 유의성이나 다른
workload에서의 비용을 보장하지 않는다. 정상 idle 동안의 CPU 비용과 boot PASS가
모든 IRQ race, 실시간 지연 상한 또는 물리 저전력 동작의 검증을 대신하지 않는다.

## 빌드 및 재현 증거

Root 기준 SHA: `f29c761ffe488bb7f48f122d780b16f37401b7f2`.
SCP 기준 SHA: `7949efe176bdac22d09173cebc4c32b2b084a33e`.
현재 Yocto SCP configure 환경과 toolchain을 재사용하고 빌드 디렉터리만 분리했다.
각 raw CL0 image를 기존 signing 환경으로 서명하여 별도 RSE flash의
`0x67000` 위치 1 MiB CL0 slot에 반영했다. raw image만 바꾸면 RSE가 원래 서명
이미지로 SRAM을 다시 채울 수 있으므로 **raw CL0와 대응 RSE flash를 함께** 전달한다.

측정기는 기존 host CPU/QMP helper를 재사용하는
[measure_scp_idle.py](../scripts/test/measure_scp_idle.py)다.

```sh
python3 scripts/test/measure_scp_idle.py \
  --name fc-off-wfi-on-repeat \
  --si-cl0-image build/qbox-apollo-qvp/si0-idle-ablation/fc_off_wfi_on/si0_ramfw.bin \
  --rse-flash build/qbox-apollo-qvp/si0-idle-ablation/fc_off_wfi_on/rse-flash-image.img \
  --out-dir build/qbox-apollo-qvp/si0-idle-ablation/repeat-new \
  --settle 20 --seconds 30 --windows 2 --boot-timeout 240
python3 -m unittest discover -s tests -p test_measure_scp_idle.py
```

출력 디렉터리는 새 이름을 사용한다. 원본은
[si0-idle-ablation](../build/qbox-apollo-qvp/si0-idle-ablation/)에 보관한다.

| 파일 | 내용 |
|---|---|
| `baseline-inputs.json` | 호스트, 기준 Git SHA, 기본 배포 이미지 SHA256 |
| `build-variants.py`, `artifacts.json` | 분리 빌드/서명 절차, 옵션, 이미지 SHA256, ELF 검증 |
| `run-matrix.py`, `matrix.log` | 실행 순서 및 종료 코드 |
| `A1b`, `B1`, `C1`, `D1`, `D2`, `C2`, `B2`, `A2` | 실행별 UART, boot 결과, thread counter 및 측정값 |
| `summarize.py`, `summary.json` | 시간 가중 집계 및 부팅별 평균 |
| `final-checks.json` | 8회 boot/측정 PASS, PFDI 오류 marker 없음, 실행 프로세스 종료 확인 |

초기 `A1`은 boot에는 성공했으나 launcher의 기본 runtime detach를 측정기가
종료로 판단하여 측정 전에 실패했다. `--foreground-runtime`을 추가하고
프로세스 정리 후 `A1b`로 다시 실행했다. `A1`은 집계에 포함하지 않는다.
측정기 검사는 3/3 PASS다. SCP 작업 트리는 clean이며 기본 CL0, RSE flash,
BSP 이미지 SHA256이 측정 전과 동일함을 확인했다.
