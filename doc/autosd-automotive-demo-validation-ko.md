# AutoSD Automotive 데모 검증 결과

검증일: 2026-09-26. [전체 실행 가이드](autosd-automotive-demo-guide-ko.md).

## 결과 요약

Apollo QEMU TCG, 4 vCPU, 4080 MiB, AutoSD 10 regular private image에서 실행했다.
커널은 `6.18.5-rt3-yocto-preempt-rt`다. 이전 customization 설치 디스크를
복사하여 사용했고, 원본 디스크와 OS 구성 소스는 변경하지 않았다.

| 시나리오 | 결과 | 증거 및 관찰 |
| --- | --- | --- |
| S01 자동 시작 | PASS | root/ADAS/QM 및 BlueChi 두 노드, heartbeat, Enforcing 정상 |
| S02 BlueChi 제어 | PASS | QM native 앱 inactive 확인, ADAS/nested heartbeat 유지, start 후 전체 정상 |
| S03 QM nested 장애 | PASS | SIGKILL 후 새 container ID로 자동 재생성, 전체 정상 |
| S04 ADAS 정지 감지 | PASS | SIGSTOP → 연속 3회 실패 → FAULT_LATCHED → container 종료, QM active |
| S05 latch 유지 | PASS | monitor 재시작 실패, ADAS 부재, QM 두 heartbeat 정상 |
| S06 운영자 복구 | PASS | fault JSON 보존, 명시적 latch 해제, ADAS/monitor 순서대로 시작 후 HEALTHY |
| S07 cold boot | PASS (준비 후) | 정상 종료된 디스크의 새 copy에서 수동 start 없이 전체 정상 |

S01–S06 소요 시간은 각각 18.364, 28.137, 36.748, 34.117, 11.689,
27.204초다. 각각 검사 전체 소요 시간이며 감지 latency나 FTTI 수치가 아니다.
host 집중 테스트는 **6 PASS**: manifest/heartbeat/monitor 및 demo runner의
실패 보존·시간 제한·첫 실패 중단을 검사했다.

CPU 실행 허용 목록은 ADAS `1`, QM `2-3`이었다. slice MemoryMax는 ADAS
536870912 byte, QM 1073741824 byte였으며 CPUWeight는 200/50이다.
이는 설정/readback 검증이다. 메모리 압박, OOM containment, CPU stress 또는
interference 성능 시험으로 해석하지 않는다.

## 증거 위치

모든 경로는 workspace root 기준이다.

- `build/autosd/automotive-demo-validation/`: 첫 VM launch/UART/private disk.
- `build/autosd/automotive-demo-suite/`: S01–S06 출력, helper 결과, `scenarios.json`.
- `build/autosd/automotive-demo-final-archive/evidence.tar.gz`: 여섯 case별 로그,
  결과 JSON, fault 해제 전 JSON, journal 및 source SHA-256.
- `build/autosd/automotive-demo-reboot/`: S07 launch/UART/private disk.
- `build/autosd/automotive-demo-reboot-ready/`: 준비 후 전체 healthy gate PASS.
- `build/autosd/automotive-demo-readiness-script/`: 재사용 readiness script 실행 증거.
- `build/autosd/automotive-demo-poweroff/`, `automotive-demo-reboot-poweroff/`:
  정상 poweroff 요청. 실제 종료는 각 launcher와 UART로 판단한다.

guest monitor Python, monitor unit, ADAS Quadlet의 SHA-256은 현재 source와
각각 일치했다. `source-sha256.txt`를 archive에 보존했다.

두 VM 모두 guest poweroff 후 filesystem unmount와 UART `Power down`,
launcher exit 0을 확인했다. 시험 VM은 실행 상태로 남겨두지 않았다.

## 실패·관찰 사항

S07 첫 검사는 SSH 가능 직후 QM BlueChi node가 `offline`이어서 FAIL이었다.
`build/autosd/automotive-demo-reboot-check/`에 그대로 보존했다. 서비스나 설정을
변경하지 않고 node online/nested unit active를 기다린 뒤 전체 검사가 통과했다.
재현 절차에 180초 제한의 read-only `wait-ready-guest.sh`를 추가했다.
부팅 준비 시간의 상한을 이번 1회 관찰로 보장하지 않는다.

초기 archive(`automotive-demo-archive/`)는 suite 완료 전에 수집되어 다섯 case만
포함한다. 최종 판정에는 **final-archive** 및 **suite/scenarios.json**을 사용한다.
초기 자료는 삭제하거나 성공 결과로 덮어쓰지 않았다.

UART의 기존 SELinux cgroup2 mount security settings 경고는 남아 있다.
Enforcing 및 실제 workload 실행은 확인했지만 정책 전체의 정확성을 보장하지 않는다.
SIGSTOP된 ADAS는 SIGKILL로 종료되어 exit 137/failed가 예상되는 시험 결과다.
latch를 가진 monitor 재시작의 failed도 의도된 동작이다.

## 미검증 및 적용 한계

- 신규 customization manifest의 전체 AIB OS image build와 해당 이미지 부팅.
- customization 이미지의 native UKI/OSTree OTA/rollback 및 QBox 실행.
- 실제 ADAS 알고리즘, actuator safe-state, 센서 입력과 차량 통신.
- ASIL-B 인증, 독립 safety partition, FFI, WCET, FTTI, 성능 및 장기 안정성.
- 네트워크/read-only/capability 정책에 대한 공격성 보안 시험.

실행 가이드는 이 범위를 명시하고, 구성된 이미지 경로와 기존 minimal_qm에서의
재설치 경로를 제공한다. 제품 AIB 빌드 경로는 layer README에 별도로 설명한다.
