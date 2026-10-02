# QBox AP / SI CL1 PFDI 주기와 부하 측정

측정일: 2026-10-02. 대상은 `MACHINE=apollo-qvp`의 전체 도메인
QBox + `nexios-bsp-initramfs`이며 AP 4 CPU, SI CL1 4 CPU를 사용했다.

현재 기본 주기는 AP/SI CL1 모두 **3000 ms**이며, SI CL1 보고 감시
timeout은 **25초**다. 추가 요청에 따라 600 ms에서 5배 더 늘렸다.

## 2차 측정: 600 ms → 3000 ms

추가 요청으로 AP/SI CL1 주기를 5배 늘리고 SI online 감시 timeout을
5초에서 25초로 늘렸다. AP의 60초 timeout과 OoR/boot timeout은 유지했다.
동일한 BSP 전체 도메인 구성에서 새로 30초씩 3회 측정하고, 앞서 보존한
600 ms 결과와 비교했다. 100%는 호스트 코어 하나이며 수치는 관측 평균이다.

| 대상 | 600 ms | 3000 ms | sim 시간당 CPU 비용 감소 |
|---|---:|---:|---:|
| AP vCPU 합계 | 28.97% | 27.42% | 5.35% |
| SI CL1 vCPU 합계 | 0.70% | 0.53% | 23.79% |
| QBox 프로세스 전체 | 305.54% | 302.31% | 1.04% |

AP `pfdi_worker/0..3`의 자발적 문맥 전환은 guest 1초당 6.68회에서
1.31회로 약 80% 줄었다. sample-app과 kernel worker CPU tick 합계는
2.05에서 0.49 ticks/guest-second로 줄었다. 이것은 진단 실행 횟수의
정확한 카운터가 아니라 해당 thread의 scheduler accounting이다.

전체 프로세스의 감소 폭은 작고, 일부 구간의 CPU 사용률 범위는 겹친다.
각 설정에서 한 번 부팅한 뒤 3개 구간을 비교한 결과로, 통계적인 성능
보장으로 해석하지 않는다. RSE/SI CL0의 CPU 비용은 여전히 남아 있다.
3초 정책에서 90초 측정 중 PFDI 감시 timeout은 없었다.

추가 증거는 `build/qbox-apollo-qvp/pfdi-load-3000ms/`에 보관했다.
`comparison.json`은 600 ms 원본의 경로도 기록하며, `after-load.json`은
3000 ms의 원시 측정값이다. `effective-config.json`에 AP pack, Zephyr
최종 Kconfig, SCP CMake 값과 두 이미지의 testdata를 기록했다.

## 1차 측정: 60 ms → 600 ms

AP와 SI CL1의 online 진단 주기를 **60 ms에서 600 ms로 변경**했다.
부팅과 기본 post-login 검증이 끝난 뒤 10초 대기하고, 변경 전후 각각
30초 구간을 3회 측정했다. 아래 CPU 사용률의 100%는 호스트 코어 하나다.
AP/SI CL1 값은 해당 도메인 vCPU 호스트 스레드의 합이다.

| 대상 | 변경 전 호스트 CPU | 변경 후 호스트 CPU | 시뮬레이션 시간으로 정규화한 CPU 비용 감소 |
|---|---:|---:|---:|
| AP | 45.55% | 28.97% | 36.38% |
| SI CL1 | 2.41% | 0.70% | 70.96% |
| 전체 QBox 프로세스 | 316.60% | 305.54% | 3.48% |
| SI CL0 | 96.42% | 97.60% | 감소 없음 |
| RSE | 99.92% | 99.91% | 사실상 동일 |

AP의 구간별 범위는 변경 전 44.56–46.06%, 변경 후 27.50–30.36%였다.
SI CL1은 각각 2.20–2.67%, 0.67–0.77%였다. 시뮬레이션 진행률은
각각 호스트 1초당 1.00153초와 1.00140초로 거의 같았다.

AP Linux `pfdi_worker/0..3`의 자발적 문맥 전환 합계는 guest 1초당
66.66회에서 6.68회로 약 90% 줄었다. 이는 요청 처리 빈도가 줄었다는
보조 증거이며, 정확한 진단 실행 횟수 카운터는 아니다. sample-app과
kernel worker의 CPU tick 합계도 guest 1초당 17.70에서 2.05로 줄었다.
이 guest 수치는 호스트 측정과 별도 시간 구간으로 정규화했다.

PFDI 주기를 늘리면 AP/SI CL1의 비용은 줄지만 전체 QBox CPU 비용은
같은 비율로 줄지 않는다. 이번 관측에서는 RSE와 SI CL0가 각각 호스트
코어 하나에 가까운 CPU 시간을 사용했다. 이 잔여 비용의 원인은 이번
측정만으로 특정하지 않았으며 해당 도메인 구현은 변경하지 않았다.

## 현재 설정의 소유권과 의미 (3000 ms)

정책은
`hsoc-stack/yocto/meta-hsoc-bsp/conf/machine/include/apollo-qvp-qbox-timing.inc`
한 곳에 둔다.

| 설정 | 이전 | 변경 | 의미 |
|---|---:|---:|---|
| `PFDI_AP_INTERVAL_MS` | 600 | 3000 | AP CPU별 timerfd 주기 |
| `PFDI_SI_CL1_PERIOD_MS` | 600 | 3000 | SI CPU별 worker의 대기 시간 |
| `SCP_SICL1_PFDI_ONLINE_TIMEOUT_US` | 5000000 | 25000000 | SI CL0의 CL1 online 보고 감시 deadline |
| `SCP_PFDI_ONLINE_TIMEOUT_US` | 60000000 | 유지 | SI CL0의 AP online 보고 감시 deadline |

AP는 owned product layer의 `platform-fault-detection.bbappend`에서 기존
`pfdi-tool`로 4 CPU, 진단 범위 0–40의 pack을 다시 생성한다. QVP의
package architecture도 machine에 맞춰 서로 다른 정책의 sstate 혼입을
방지한다. 앱은 시작할 때 pack을 읽으므로 실행 중 파일만 바꾸어서는
주기가 바뀌지 않는다.

SI CL1은 owned BSP의 `zephyr-demos-cl1-apollo-qvp.inc`에서
`-DCONFIG_PFDI_MGMT_PERIOD_MS=3000`을 전달한다. 실제 주기는 3000 ms 대기와
진단/SCMI 왕복 처리 시간의 합이다. shell의 worker 요청도 이 대기를
다시 시작할 수 있으므로 측정 중 상태 명령을 반복하지 않는다.

SI CL0 online timeout은 정상 보고를 받을 때마다 갱신되는 감시 값이며
진단 실행 주기가 아니다. SI의 deadline/period 비율을 기존과 같은
약 8.33으로 유지했다. OoR/boot deadline, AP driver의 개별 ioctl 완료
timeout, SMCF 주기는 변경하지 않았다. FVP의 60 ms 진단 기본값도 유지한다.

진단 간격과 SI 보고 누락 감지 시간이 길어지는 변경이다. 실제 제품의
FTTI, 물리 시간 정확도 또는 진단 coverage를 보장하는 설정은 아니다.
특히 현재 SI CL1은 `CONFIG_PFDI_USE_ARM_FW_LIB`가 꺼진 weak backend를
사용하므로 측정 비용은 주로 scheduling과 SCMI/MHU 통신 비용이다.

## 측정 방법과 재현

`scripts/test/measure_qbox_pfdi_load.py`는 다음 정보를 기록한다.

1. domain별 QMP `query-cpus-fast`의 `thread-id`로 vCPU 호스트 TID를 찾는다.
   여러 QEMU 인스턴스에서 중복되는 `CPU 0/TCG` 같은 스레드 이름으로
   도메인을 추정하지 않는다.
2. 호스트 `/proc/PID/task/TID/stat`의 user/system CPU tick과
   `/proc/PID/task/TID/status`의 문맥 전환 값을 구간 양 끝에서 읽는다.
3. QBox monitor `/sc_time`으로 시뮬레이션 진행 시간을 함께 기록한다.
   `CPU seconds / host seconds × 100`과 `CPU seconds / sim seconds`를
   모두 계산하여 느려진 시뮬레이션을 부하 감소로 오해하지 않도록 한다.
4. 측정 구간 밖에서 AP `/proc/stat`, `/proc/interrupts`, sample-app의
   모든 thread와 `pfdi_worker/*`의 accounting을 저장한다. 진단 SMC는
   별도 kernel worker에서 실행하므로 sample-app만 측정하면 누락된다.

측정 구간 안에는 monitor polling, guest shell 명령, fault injection을
실행하지 않는다. trace/perf 설정을 바꾸지 않는다. 이 커널에는 guest
`schedstat`가 없으므로 guest 분석에는 `stat`과 context-switch 값을 사용했다.
PFDI `count` 명령은 지원 진단 항목 수를 반환하므로 부하 카운터로 쓰지 않는다.

이미 부팅하고 유휴 상태인 전체 도메인 run에 다음과 같이 실행한다.
run에는 primary UART FIFO와 loopback QBox monitor가 있어야 한다.
PID는 해당 run의 `platforms-vp` 프로세스다.

```sh
python3 scripts/test/measure_qbox_pfdi_load.py \
  --run-dir build/qbox-apollo-qvp/<run> \
  --pid <platforms-vp-pid> --monitor-port 18110 \
  --seconds 30 --windows 3 \
  --output build/qbox-apollo-qvp/<run>-load.json
```

이번 실행의 재현 harness와 입력 이미지 SHA256, 원본 console, 개별
window의 counter는 `build/qbox-apollo-qvp/pfdi-load/`에 보관했다.
`run.py before`와 `run.py after`가 사용한 명령은 각각 `*-command.json`에
있고, 쓰기 가능한 disk/flash는 run마다 별도 복사본을 사용했다.
각 label은 실행 당시 배포된 이미지를 복사하므로 새 비교에서는 별도의
label을 사용해야 한다. 보존된 `before-inputs/`를 현재 배포물로 덮어쓰지 않는다.

- `before-load.json`, `after-load.json`: 원시 counter와 구간별 계산.
- `summarize.py`, `comparison.json`: 합산 및 guest accounting 비교.
- `effective-config.json`: 최종 pack, Zephyr Kconfig, SCP CMake 값.
- `build-components.log`, `build-bsp-retry.log`, `build-product.log`: 구성 요소,
  BSP와 제품 이미지 빌드.
- `native-check-first.log`, `native-check-pass.log`: 첫 종료 timeout과 재실행 결과.
- `product/result.json`, `product-retry/result.json`: 제품 첫 부팅 실패와
  동일 입력으로 재부팅한 결과. `product-retry-run.json`은 service 검사 결과.

SystemC 시간과 host counter는 원자적 snapshot이 아니며 endpoint 요청
시간이 포함되는 약 0.2% 이내의 구간 차이가 있었다. 각각 한 번의 부팅에서
3개 구간을 측정한 결과이고, 도메인 CPU 시간에는 PFDI 외의 guest 작업도
포함된다. 호스트 contention에 따른 변동과 물리 하드웨어 사용률을 구분해야 한다.

## 2차 변경 검증 (3000 ms)

정책 검사 10개가 통과했고, 구성 요소 빌드 1642 tasks와 BSP/제품 이미지
통합 빌드 7713 tasks가 통과했다. QBox platform 64개와 core 61개 검사도
통과했다. AP PFDI profile의 7개 assertion 및 SI CL1의 119개 명령/17개
assertion이 3초 정책에서 통과했다. 90초 유휴 측정 중 AP/SI의 report
watchdog timeout은 없었다.

제품 첫 부팅은 SI CL0가 TPS6594 `begin ... before=power` 이후 진행하지
못하고, RSE가 `SCP is not ready`를 보고하여 실패했다. 이 단계에서는
Linux가 아직 시작되지 않았고 입력 firmware SHA256은 성공한 BSP run과
동일했다. 실패 기록은 `pfdi-load-3000ms/product/`에 보존한다.
동일 설정 재부팅에서는 전체 post-login 검사와 `pfdi-app` active 상태,
설치 pack 및 service journal의 3000 ms를 확인했다. systemd 실패 unit은
0개이고 PFDI 감시 timeout은 없었다. 결과는 `product-retry/result.json`,
`product-retry-run.json`, `summary.json`에 있다. 첫 부팅 재현성 문제는
해결된 것으로 주장하지 않는다.

## 1차 변경 검증 (600 ms)

구성 요소 빌드 1642 tasks, BSP 이미지 재빌드 5847 tasks, 기본 제품
`nexios-image` 빌드 7358 tasks가 통과했다.
QBox native 검사는 platform 64개, core 61개가 통과했다. 첫 image 빌드의
`aarch64-single-tcg-five-cpu-shutdown-test` timeout은 로그로 보존했고,
같은 설정으로 재실행하여 통과했다. timeout이나 제외 목록은 수정하지 않았다.

변경 전후 전체 도메인 boot/post-login 및 90초 유휴 측정은 통과했다.
AP `pfdi` profile은 4개 CPU의 정상 진단, 오류 주입, SBIST/FMU와 SI0
감시 결과를 포함하여 7개 assertion을 통과했다. 설치 pack과 실제 앱
로그 모두 600 ms임을 확인했다. SI CL1 `pfdi-si-cl1` profile은 119개
명령을 실행하여 상태, 정상/잘못된 입력, 오류 주입, 반복 실행, SI0
감시를 포함한 17개 assertion을 통과했다. 결과는 각각
`ap-probe/result.json`, `si-probe/result.json`과 `qualification.json`에 있다.
이 결과의 `coverage_kind=identical`은 검증 profile 분류이며 이번에
FVP를 실행하여 성능 또는 물리 동등성을 비교했다는 뜻이 아니다.

관련 Python 검사 37개와 FVP/QVP의 실제 BitBake 설정 분리 검사 3개가
통과했다. QBox AP probe는 설치 pack의 interval과 실행 로그를 비교하고,
OEQA는 image testdata의 `PFDI_AP_INTERVAL_MS`를 사용한다. 따라서 이후
정책값을 바꾸어도 probe에 별도 주기 상수를 중복 관리할 필요가 없다.

제품 이미지 첫 부팅은 SI CL0의 TPS6594 `register-init status=-7` 및
`fwk_module_start_module` assertion으로 중단됐다. 이어서 RSE가 SCP 미준비를
보고했다. 실패 당시 펌웨어 SHA256은 성공한 BSP run과 동일했다. 입력이나
timeout을 바꾸지 않은 재부팅에서는 전체 boot/post-login, 4 CPU PFDI,
`pfdi-app`의 `active` 상태, 설치 pack 및 service journal의 600 ms를 확인했다.
실패한 systemd unit은 0개이고 PFDI error/timeout은 없었다. 첫 초기화 실패의
재현성 문제는 해결한 것으로 주장하지 않으며 원본 로그를 보존한다.
