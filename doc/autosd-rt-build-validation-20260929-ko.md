# AutoSD 빌드의 RT 준비 통합 및 검증

작업은 2026-09-29에 시작했으며 Dashboard 측정은 2026-09-30 KST에 완료했다.

## 변경 내용

기본 `./build_autosd_minimal_qm.sh`의 Automotive customization에 RT 준비를
포함했다. `--minimal`은 기존처럼 Automotive/RT customization을 생략한다.

- `scripts/autosd_demo/build_minimal_qm.py`: 기존 bundle 생성기에 `--rt-tools`
  전달, RT 패키지 설치, QEMU/QBox RT readiness 단계 추가.
- `autosd/customization/rt/prepare-guest.sh`: regular/private ARM64 guest만 허용.
  Root RT 패키지 설치, QM을 정지한 상태에서 installroot로 stress-ng 설치,
  QM 재기동 및 준비 확인. 패키지 오류는 즉시 실패로 전달한다.
- 기존 bundle installer로 Root/QM static `latency-probe` 및 Root의
  `rt-experiment.py`, `rt-trace.py`, `check-automotive.sh` 설치.
- QEMU/QBox 준비 검사: 패키지·명령 존재, PREEMPT_RT 활성화,
  timerlat/osnoise tracer, Root/QM probe hash 일치와 양쪽 실행 확인.
- `prepare.py` provenance에 생성한 probe SHA256 추가.
- benchmark 서비스 자동 기동, watchdog 정책 변경, latency 기준 완화 없음.

이번 작업에서는 Apollo 커널·firmware 및 외부 Yocto layer를 변경하지 않았다.

## 빌드 검증

기존 공식 AIB 생성 qcow2를 재사용해 이미지 준비부터 QEMU 설치·검증,
QBox full 부팅·검증·정상 종료까지 다시 실행했다. AIB 자체의 OS 생성은
이번에 재실행하지 않았다.

```sh
./build_autosd_minimal_qm.sh \
  --cache-dir build/autosd/cold-bootstrap-20260929 \
  --image build/autosd/minimal-qm-rebuild-20260929-fetch/minimal_qm.aarch64.qcow2 \
  --output build/autosd/demo-minimal-qm-rt-v2-prepared \
  --work-dir build/autosd/minimal-qm-rt-20260929-v2 \
  --qbox-out-dir build/qbox-apollo-qvp/autosd-minimal-qm-rt-20260929-v2
```

**결과: PASS — 18개 단계 모두 returncode 0.**

- 빌드 결과: `build/autosd/minimal-qm-rt-20260929-v2/result.json`
- RT 설치 로그: 같은 경로의 `customization-rt-packages/console.log`
- 준비 검사: `qemu-rt-readiness/console.log`, `qbox-rt-readiness/console.log`
- 최종 이미지: `build/qbox-apollo-qvp/autosd-minimal-qm-rt-20260929-v2/rootfs.wic`
- 최종 manifest: `build/autosd/demo-minimal-qm-rt-v2-prepared/regular.json`

최종 이미지 SHA256:
`70d0f3f1e8af2f7d6222ad5583ddee3094f2467f2e6b03f9bae106d8e730850a`

실제 설치 버전:

| 패키지 | 버전 |
| --- | --- |
| realtime-tests | 2.10-1.el10.aarch64 |
| rtla | 6.12.0-271.el10.aarch64 |
| trace-cmd | 3.3.1-3.el10.aarch64 |
| stress-ng (Root/QM) | 0.19.03-2.el10.aarch64 |
| util-linux | 2.40.2-23.el10.aarch64 |
| procps-ng | 4.0.4-13.el10.aarch64 |

Root/QM probe SHA256:
`2ad0b83aad7c8aa88b4f19d473c16d510ea50e8dc0dcdc40f0d60136c08c9c93`

첫 실행에서 QM 정지 시 Quadlet이 컨테이너 객체를 제거해 다음 bundle 설치기의
`podman inspect qm`이 실패했다. RT 패키지 설치 후 QM 재기동/준비 확인을
추가하고, 첫 VM은 정상 종료한 뒤 새 출력 디렉터리(v2)에서 전체 절차를 통과했다.
첫 실패 증거 `build/autosd/minimal-qm-rt-20260929/`는 삭제하거나 PASS로 바꾸지 않았다.

## 정적/회귀 검사

- `pytest -q tests/test_autosd*.py`: **625 PASS**, 기존 Paramiko deprecation 경고 2개.
- `bash -n autosd/customization/rt/prepare-guest.sh`: PASS.
- `git diff --check`: PASS.
- 새 테스트는 최소 이미지 경로 유지, RT 단계 연결·실패 전파, QM 정지/재기동
  순서, 패키지 실패, 비 ARM guest 거부 및 probe provenance를 검사한다.

빌드 준비 검사 성공은 실제 latency 기준 통과나 물리적 실시간 보장을 의미하지 않는다.

## Dashboard 실제 측정

새 이미지로 서버를 재시작하고 QBox full-system Power on, 자동 Automotive health
PASS 이후 웹 버튼으로 실행했다. 기존 5,000µs 기준은 변경하지 않았다.

| 측정 | 최대 지연 µs | 판정 |
| --- | ---: | --- |
| R01 SCHED_OTHER | 7509.960 | 측정 PASS / baseline EXCEEDED |
| R02 FIFO | 3680.416 | WITHIN_OBSERVED_THRESHOLD |
| R03 QM 부하 | 3316.496 | WITHIN_OBSERVED_THRESHOLD |
| R04 동일 CPU 경합 | 3357.632 | WITHIN_OBSERVED_THRESHOLD |
| R05 합성 지연 | 11837.664 | DETECTION_PASS (성능 판정 제외) |
| R06 Cyclictest | 3365 | WITHIN_OBSERVED_THRESHOLD |
| Timerlat IRQ | 1522 | 수집 PASS / 관측 최대값 기준 이내 |
| Timerlat thread | 3358 | 수집 PASS / 관측 최대값 기준 이내 |
| Timerlat user | 4083 | 수집 PASS / 관측 최대값 기준 이내 |
| OS noise | 1760 | 수집 PASS / 관측 최대값 기준 이내 |

RT 묶음의 `measurement_status=PASS`, `latency_status=WITHIN_OBSERVED_THRESHOLD`.
Timerlat은 각 histogram 4,169 samples를 수집했다. 전체 trace 판정은
`NO_THRESHOLD_STOP_OBSERVED`이며, 이것을 보장된 latency budget PASS로 해석하지 않는다.
대시보드의 RT 결과 표·최대 지연 그래프와 Timerlat histogram 렌더링을 확인했다.
OS noise는 histogram 12,001 samples와 실제 이벤트 기반 시간별 그래프를 확인했다.
시간별 그래프는 수집 이벤트 554개를 사용했다.
histogram 범위 밖 123개는 5,000µs 기준 초과 횟수가 아니다. 임계 초과 중지 시의
추가 trace snapshot은 발생하지 않았으며(`trace_collected=false`), 시간별 이벤트
데이터와 이 snapshot 필드를 혼동하지 않는다. 측정 후 safety 상태는 HEALTHY였다.

증거 세션: `build/autosd/dashboard/20260929-235334-05ec49ee/`

- RT: `45e6d15dd7244e87a45ef79137162f4a/guest/results.json`
- Timerlat: `aa7fe36c5a364933ac21cac1936b6085/guest/trace-result.json`
- OS noise: `6316fe1257e74a7e858fc454b26b2da7/guest/trace-result.json`
- 화면/부팅 증거: `build/autosd/rt-build-dashboard-20260929/`
- 정상 Power off: `8b41505852db4a92b55aa54a83d9ee66/job.json` PASS,
  UART `reboot: Power down`, Dashboard VM running=false 확인.

검증 VM은 정상 종료했고 Dashboard 서버는 새 RT 이미지 설정으로 유지했다.

QBox 관측은 실제 하드웨어의 WCET/FTTI나 ASIL 인증을 입증하지 않는다.

Dashboard 서버의 manifest/rootfs는 위 새 RT 이미지로 변경했다. 시작 예시는 다음과 같다.

```sh
python3 scripts/autosd_dashboard/server.py \
  --listen 127.0.0.1 --listen 192.168.0.13 \
  --allow-unauthenticated-lan --allow-private-guest --backend qbox-full \
  --runtime-injection --qbox-diagnostics \
  --manifest build/autosd/demo-minimal-qm-rt-v2-prepared/regular.json \
  --rootfs build/qbox-apollo-qvp/autosd-minimal-qm-rt-20260929-v2/rootfs.wic
```

서버를 중복 시작하지 않는다. 이 실행 예시는 신뢰하는 내부망 전용이다.
