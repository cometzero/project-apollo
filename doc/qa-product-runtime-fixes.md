# Apollo Product runtime 실패 수정

검증 대상은 `MACHINE=apollo-qvp`, `nexios-image`, QBox 전체 시스템의 AP 4 CPU
구성이다. 기존 qa-tests 재설계 실행의 `11 PASS / 4 FAIL / 9 SKIP / 1 ERROR`를
출발점으로 삼았다. 원본 실패 증거는
`build/qbox-apollo-qvp/qa-redesign/runtime-product/`에 보존했다.

수정 후 최종 Product runtime은 **16 PASS / 9 SKIP / 0 FAIL / 0 ERROR**다.
자동 report는 `build/qbox-apollo-qvp/product-runtime-fix/runtime-product-validated/`에
있다. 전체 host pytest와 실제 watchdog 복구도 아래와 같이 통과했다.

## 원인과 수정

| 실패 | 원인 | 수정 |
| --- | --- | --- |
| CPU topology | 모델과 Linux online CPU는 4개지만, Product UKI 내 DT는 CPU 16개와 DSU 4개를 기술했다. `maxcpus=4`는 DT topology를 줄이지 않는다. | Linux에 4-CPU DT를 추가하고 `PC_CPUS_COUNT`로 kernel DT, A/B UKI, `.qboxconf`가 동일한 파일을 선택하도록 했다. 직접 부팅 및 GIC/PCIe/audio 검사 도구도 manifest의 DT를 선택한다. |
| platform-devices | legacy `primary-ssh` assertion이 실제로 검사하는 CPU topology가 같은 이유로 실패했다. | 같은 DT 수정으로 해결한다. 별도 SSH testcase의 성공과 구분한다. HTTP fixture 보완은 이전 qa-tests 변경에 포함되어 있다. |
| CPU RAS | TF-A의 오류 주입과 IRQ 처리는 있었으나 DT에 CPER reserved memory와 Linux `arm,ras-ffh` consumer가 없었다. | `0xffa00000`의 1 MiB CPER 영역과 INTID 89 (`GIC_SPI 57`) consumer를 추가했다. 기존 RAS 판정 기준을 유지한다. |
| SI CL1 version 명령 | Zephyr는 부팅했지만 `CONFIG_KERNEL_SHELL`이 없어 `kernel version`을 실행할 수 없었다. | QVP SI CL1 defconfig에 `CONFIG_KERNEL_SHELL=y`를 추가했다. |
| 간헐적 AP 부팅 정지 | TF-A의 SCMI CPU_OFF 요청 뒤 SCP가 static PPU OFF를 실행해, TF-A의 `AFF_STATE_OFF` 기록 전에 CPU reset이 걸릴 수 있었다. primary CPU는 secondary의 OFF 상태를 계속 기다렸다. | QVP AP의 정상 OFF는 dynamic OFF와 OFF_LOCK으로 WFI를 기다린다. OFF 도중 ON은 보류하고 완료 이벤트에서 OFF→ON 순으로 보고한다. generation으로 오래된 이벤트를 무효화한다. core reset과 SI0 watchdog/software recovery는 별도 static force OFF를 사용한다. |

Zephyr CL1 binary는 kernel shell 활성화로 287,220 → 296,564바이트(+9,344바이트)가
되었다. 새 binary를 포함한 RSE firmware와 Product 이미지를 다시 생성했다.

SCP의 기존 power-domain framework는 driver가 ON 요청을 수락한 뒤 OFF를 보고해도
같은 core의 ON을 재요청하지 않는다. 따라서 보류된 ON은 PPU driver가 완료해야 한다.
ISR은 취소 가능한 완료 이벤트만 보내고, 실제 상태 보고는 framework event context에서
수행한다. FWK 일반 이벤트와 ISR 이벤트의 우선순위 때문에 이전 OFF 보고가 새 복구
상태를 덮는 경우를 막기 위한 순서다.

PPU arm 과정은 IRQ critical section에서 MIN interrupt mask/ack를 먼저 수행한 뒤
현재 PWSR을 확인한다. 이후 WFI로 발생한 새로운 완료 interrupt를 지우지 않는다.
강제 복구는 CPU의 WFI에 의존하지 않으며 기존 PD composite OFF 요청도 유지한다.

실제 watchdog 재검증에서는 추가로 PD 알림 응답 대기 중 중복 OFF 보고가
`previous_state=ON`을 `OFF`로 덮어 클러스터 OFF 진행을 누락시키는 결함이 나타났다.
알림을 시작할 때의 이전 상태를 응답 완료까지 보존하고, 강제 OFF 완료 보고보다
PD 정책 요청을 먼저 큐에 넣도록 수정했다. 정책 요청은 비동기이므로 실제 강제 OFF는
같은 event callback 안에서 계속 즉시 실행된다.

## 검증 증거

실행별 결과는 `build/qbox-apollo-qvp/product-runtime-fix/`에 보존한다.

- `runtime-product/`: DT/RAS/Zephyr 수정 후 16 PASS / 9 SKIP. 이 실행에는 검토 중인
  PPU 모델 변경이 포함되어 있어 최종 firmware 수정의 증거와 구분한다.
- `power-before/`: 초기 PPU 모델 수정에서 hotplug 8회 PASS, watchdog WS0/WS1 발생 뒤
  새 Linux boot 미관측으로 FAIL. 이 모델 변경은 원복했으며
  `rejected-static-off-delay.patch`에 비교용으로만 보존했다.
- `power-final/`: SCP graceful/force OFF 분리 후 hotplug 8회 PASS. watchdog에서 core
  OFF 이후 cluster OFF가 완료되지 않는 PD 중복 알림 문제를 발견한 중간 실패 실행이다.
- `uki-audit/`: 배포 WIC와 위 runtime의 4개 실제 WIC에서 A/B UKI 10개가 모두 배포
  EFI와 동일함을 확인했다. embedded DT는 선택된 4-CPU DT와 byte 단위로 동일하다.
  전체 WIC 해시 차이와 UKI/DT 일치는 별도로 기록했다.
- `build-product-pd-notify.log`: 최종 Product build PASS. 7,421 task 중 29개를 다시
  실행했다. 기존 forced-task 관련 warning 4건을 보존했다.
- `scp-pd-order-20261023T050116Z/`: 실제 PD FIFO/notification 경로에서 수정 전에는
  cluster OFF 미완료를 포함한 2개 회귀가 FAIL, 수정 후 3개 모두 PASS다.
  PD/PPU 7개 CTest, SI0 3개 CTest, vMCU 4개 실행파일도 PASS다.
- `watchdog-recovery/result.json`: hotplug 8회, watchdog WS0→WS1→reset-clear,
  새 Linux boot ID, online CPU `0-3`, SI0 IRQ rearm, 동일 QBox 프로세스 유지 PASS.
  SI CL1 재부팅도 관측되지 않았다. 전체 실행은 242.54초이며 cleanup PASS다.
- `host-pytest-validated.log`: 전체 host pytest 2,635 PASS / 9 SKIP / 2 warning,
  184.71초. report는 `build/qbox-apollo-qvp/pytest-20261023T050212Z-xp1cd1q3/report.md`다.
- `validated-artifacts.json`: 위 최종 이미지, firmware, QBox PPU module 및 수정한
  firmware source의 SHA-256과 각 owning repository 상태를 기록했다.
- `runtime-product-validated/`: 최종 Product runtime **16 PASS / 9 SKIP**, FAIL/ERROR 0,
  704.87초. profile 내부 assertion 21개도 모두 PASS다. 4개 새 QBox 세션의 cleanup은
  모두 PASS이며 잔여 PID가 없다. 테스트별 결과·수행 시간·명령·UART 로그는 자동
  HTML/Markdown/JSON/JUnit report에서 확인한다.
- `verification.json`: runtime/host 결과와 cleanup receipt를 대조했다. 최종
  source/firmware/module에 drift가 없으며 `build/conf` 입력도 최초와 동일하다.

## 재현

```sh
./yocto_build.sh --keep-conf nexios-image
python3 -m pytest -c qa-tests/pyproject.toml qa-tests/tests --image=product -v
python3 scripts/test/run_pytest.py -q
```

Runtime 명령은 실행마다 새 증거 디렉터리를 만들고 HTML/Markdown/JSON/JUnit report,
명령별 결과, 도메인 UART 로그와 cleanup receipt를 저장한다. 고정 위치가 필요하면
아직 존재하지 않는 디렉터리를 `--run-dir`로 지정한다. 예전 실행을 덮어쓰지 않는다.

Product의 9 SKIP은 BSP 전용 6개와 QBox probe 미구현 3개(MBPP, crypto extension,
HIPC)이다. 이번 수정은 해당 기능의 성공을 주장하지 않는다. BSP의 별도 RSE-SCP
readiness 실패, FVP 및 실물 하드웨어 검증도 이 Product 결과의 범위 밖이다.
