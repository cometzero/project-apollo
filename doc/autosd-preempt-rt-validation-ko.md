# AutoSD PREEMPT_RT 구성 및 실험 검증

실행일: 2026-09-27. [RT Quick Guide](autosd-preempt-rt-guide-ko.md).

## 구성 및 빌드

새 QVP RT tracer 커널과 진단 profile을 구성하고 private regular AutoSD guest에서
측정했다. 측정 기능 PASS와 latency 임계값 초과를 구분한다.

- AutoSD 문서 조사: QM RT 제한, CPUWeight 의미, RT/PCP 역할 구분 반영.
- AutoSD nightly RPM 확인: realtime-tests 2.10-1.el10, rtla 6.12.0-270.el10,
  trace-cmd 3.3.1-3.el10, stress-ng 0.19.03-2.el10 (aarch64).
  원본 listing: `build/autosd/rt-repo-audit/packages.html`.
- 기본 이미지 정책과 분리된 `prepare.py --rt-tools` profile 구현.
- static probe native unit tests 17개 및 AArch64 static compile PASS.
- QVP diagnostic tracer defconfig 및 BSP **PASS**: 5,817 tasks 성공(5,741 재사용).
  로그 `build/autosd/rt-kernel-bsp-build.log`; 기존 taint warning 5개 보존.
- 새 Image SHA-256:
  `fc22e51a1a2a7d0b8153a90ca6080812f86ab65cfc275804e52258bf456c9fe0`.
- matching kernel RPM **PASS**: 반복 빌드 SHA 일치, module 275개.
  SHA `a054972cd5f862ab0a288615d5c7a896f56962be43e017de4d876e0748653858`.
  `build/autosd/automotive-rt-kernel-rpm/result.json`.
- 기존 regular customization disk의 private copy에 새 Image로 부팅한 뒤 실제
  `/proc/config.gz`에서 PREEMPT_RT/HWLAT/OSNOISE/TIMERLAT/HIST_TRIGGERS=y 확인.
  `build/autosd/rt-guest-preflight-ready/`, `rt-trace-preflight/`.
- private guest RPM 설치 **PASS**: realtime-tests/rtla/trace-cmd/stress-ng와 9개 dependency,
  모두 AutoSD repository에서 취득. `build/autosd/rt-tools-install/console.log`.
- matching kernel RPM 재설치 및 `rpm -V` **PASS**, guest vmlinuz SHA가 host Image와 일치.
  `build/autosd/rt-kernel-install/`. 이후 Power down 및 새 copy cold boot 수행.
- 신규 진단 도구 stage 후 Automotive healthy 검사 **PASS**, SELinux Enforcing 유지.
  `build/autosd/rt-probe-stage/`. RT 실험은 재부팅한 `automotive-rt-measure/`에서 수행.

## R01–R06 재실행 결과

원본: `build/autosd/rt-experiment-verified/results.json`.
QEMU TCG 4 CPU, CPU 1, period 1,000 µs, 각 5초, FIFO priority 50,
검출용 예시 threshold 1,000 µs. 전체 측정 유효성 PASS, 서비스 전후 검사 PASS,
latency 종합 **EXCEEDED**(exit 2), suite 경과 96.04초.

| 실험 | sample | 평균 µs | 최대 µs | p99 µs | 초과 / missed |
| --- | ---: | ---: | ---: | ---: | ---: |
| R01 SCHED_OTHER | 4,921 | 315.474 | 5,870.864 | 1,339.648 | 57 / 79 |
| R02 FIFO + mlock | 5,000 | 138.015 | 548.200 | 259.648 | 0 / 0 |
| R03 QM CPU 부하 | 5,000 | 208.450 | 551.896 | 390.176 | 0 / 0 |
| R04 동일 CPU 경합 | 5,000 | 173.258 | 447.408 | 339.600 | 0 / 0 |
| R05 3,000 µs synthetic 주입 | 4,997 | 138.342 | 3,411.504 | 237.032 | 1 / 3 |
| R06 cyclictest | 5,000 | 173.520 | 779.000 | 별도 histogram | 0 / 미집계 |

R02–R05에서 요청한 FIFO/priority/affinity/mlock이 확인됐다. R01–R05 측정 중
minor/major fault delta는 모두 0. QM/root 부하 unit의 active 및 CPUUsageNSec 증가를
확인하고 소유 unit을 정리했다. R05는 검출 PASS이며 성능 비교에서 제외한다.
기존 ADAS container 자체를 RT화한 결과가 아니라 CPU 1의 root native probe 결과다.

초기 실행 `rt-experiment-first/`는 잘못된 cyclictest `--jsonfile` 옵션을 사용했다.
cyclictest 2.10이 usage 오류에도 exit 0을 반환하여 초기 report의 measurement PASS는
전체 suite 판정으로 **무효**다(R01–R05 raw 관찰은 보존). `--json=` 수정과 JSON의
실제 cycles 검증을 추가했다. 별도 `rt-cyclictest-corrected/` 및 위 전체 재실행에서
5,000 cycles를 확인했다. 초기 evidence는 덮어쓰지 않았다.

## R07 trace 검출

`build/autosd/rt-timerlat-verified/trace-result.json`, `rtla.log`:
수집 PASS / latency EXCEEDED. IRQ/thread/user 각각 14 samples,
최대 97/836/1,096 µs. 임계 초과 trace가 저장됐고 모든 관찰 대상 tracefs 설정이
원복됐으며 잔여 instance가 없다. 요청 5초 전에 threshold-stop으로 종료된 측정이다.
사용한 rtla 6.12와 커널 6.18의 조합에서 실제 fallback 수집을 검증했다.

최초 `rt-timerlat-first/`의 rc2는 도구 실패가 아니라 threshold-stop이었다.
wrapper를 stop marker·유효 histogram·trace 존재·설정 원복까지 검사하도록 보완하고
새 디렉터리에서 재실행했다. `ALL:` 집계 행의 sample 중복 계산도 수정했다.
BTF 미구성 libbpf 경고는 원본 로그에 보존했다. 이 경고를 숨기기 위한 미검증
옵션이나 커널 debug 설정 변경은 하지 않았다.

## R08 OS 간섭 검출

R08 `build/autosd/rt-osnoise-verified/`: 수집 PASS / latency EXCEEDED,
1,545 samples, 평균 5.71 µs, 최대 1,377 µs. threshold-stop 및 trace 저장 확인.
sampling runtime/period는 10,000/100,000 µs이며 baseline wakeup 실험과 직접
성능 비교하지 않는다. 모든 trace 설정 복원 및 잔여 instance 없음 확인.

## 최종 확인 및 재현 산출물

- 관련 regression **185 PASS** (10.57초), root/Linux `git diff --check` PASS.
- 가이드의 shell block `bash -n` PASS.
- 최종 profile: `build/autosd/automotive-rt-bundle-final/automotive.aib.yml`.
  schema 검증 및 static AArch64 compile PASS; `provenance.json`에 source hash 보존.
- probe SHA: `2ad0b83aad7c8aa88b4f19d473c16d510ea50e8dc0dcdc40f0d60136c08c9c93`.
- 전체 guest raw 증거: `build/autosd/rt-final-evidence/apollo-rt-evidence.tar.gz`.
  최초 실패/수정 후 실행 모두 포함한다.
- 마지막 Automotive 검사 HEALTHY, SELinux Enforcing, failed service 0,
  root/QM의 실험용 잔여 unit 0, tracer nop / root events 0 / instance 없음.
  `build/autosd/rt-final-evidence/console.log`.
- host 정보: `rt-host-uname.log`, `rt-host-lscpu.log`; guest launch/UART:
  `build/autosd/automotive-rt-measure/`.
- 정상 종료 PASS: 파일시스템/loop detach, UART `reboot: Power down`, launcher exit 0,
  localhost 2234 listener 소멸 확인. `build/autosd/rt-final-poweroff/`.

## 미검증 및 해석 한계

전체 immutable RT 이미지 재빌드, 물리 보드 latency qualification, QBox 성능은
현재 PASS로 판정하지 않는다. 기본 native 이미지의 과거 부팅 PASS를 새 RT profile의
전체 이미지 검증으로 대신하지 않는다.
PCP/fio/memory/I/O/oslat/hwlat의 추가 부하 실험은 방법만 안내했으며 이번 실행
PASS에 포함하지 않는다. non-RT 대조군·장시간 반복·실제 ECU IRQ→ADAS 출력 측정도
미수행이다. PREEMPT_RT 적용에 따른 개선율, ASIL-B/FFI/FTTI/WCET 보장을 주장하지 않는다.
