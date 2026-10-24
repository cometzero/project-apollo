# Apollo AP power 및 thermal model

기준일: 2026-10-24. 이 문서는 `/srv/oss_contrib/gem5`의 reference
`078dc86553ac`에서 Apollo AP-only 실행 경로로 이식한 power 기능을 설명한다.
이식 범위는 offline activity 분석, native energy/RC 기반, SCMI/DVFS,
online power/thermal accounting이다. DRAMPower bridge와 AP hot checkpoint는
후속 단계이며 현재 지원으로 표시하지 않는다.

## 측정 의미

이 모델은 Cortex-A720AE, DSU, CMN-S3AE, LPDDR5X의 calibrated electrical model이
아니다. `SYNTHETIC`은 계산 경로를 검증하는 임의 계수이며, `ASSUMED_RC`는
sensitivity 분석용 lumped thermal network다. `COMPLETE_LEDGER`는 선언한
actor 모두의 계산이 가능하다는 뜻이며 실제 silicon 전체 회로의 coverage가 아니다.

CPU pipeline, L1I/L1D/L2, DSU/L3, SLC, CMN router/link, DMC/PHY,
external DRAM, I/O proxy의 energy 소유자를 분리한다. Dynamic energy는
실제 event count × J/event, leakage는 명시한 temperature/state law로 계산한다.
옵션 `reference_voltage_v`가 있는 actor만 이상적인 V² scaling을 적용한다.
Frequency는 event rate에 이미 반영되므로 별도의 frequency 배수를 곱하지 않는다.

계수가 없으면 `UNCONFIGURED`/null로 남기며 전체 energy를 발명하지 않는다.
기본 offline profile은 `unconfigured.json` 사용을 권장한다. Synthetic profile의
전력·온도를 제품 사양이나 Orin/Apollo 실측으로 해석하지 않는다.

## Source와 build

| 소유 경로 | 역할 |
|---|---|
| gem5 `src/sim/power/`, `src/sim/power_state.*` | latched energy, residency, RC thermal |
| gem5 `src/dev/arm/css/` | SCMI Performance/Sensor와 MHU completion |
| gem5 `configs/zena_cmn/power_control.py` | AP4/AP16 cluster clock/voltage, MHUv1 및 DTB |
| gem5 `configs/zena_cmn/power_runtime.py` | epoch accounting 및 online RC feedback |
| gem5 `scripts/zena_cmn/analyze_power.py`, `thermal_replay.py` | offline analysis/replay |
| Root `scripts/gem5/run_linux.py`, `benchmark.py` | launcher input 계약 및 ROI 결과 수집 |
| Linux `arch/arm64/configs/apollo_qvp_defconfig` | MHUv1, SCMI sensor, CPU cooling, userspace governor |
| `gem5-apollo-guest.bb` | `apollo-power-probe` target build/package/deploy |

기존 `gem5-native` externalsrc와 `nexios-gem5-initramfs` image를 사용한다.
Runtime에서 compiler나 downloader를 실행하지 않는다.

```sh
APOLLO_BUILD_THREADS=2 APOLLO_PARALLEL_MAKE=-j4 \
  ./yocto_build.sh --gem5 --keep-conf
```

## Offline 분석

기존 PASS run의 `launch.json`, `result.json`, 그리고
`m5out/{config.json,stats.txt,roi-events.json,exit.json}`을 사용한다.
Reference의 `run_manifest.json`도 읽지만 두 manifest가 동시에 있으면 모호한
provenance를 거부한다. 실제 입력 hash와 manifest를 결과에 보존한다.

```sh
python3 hsoc-stack/tools/gem5/scripts/zena_cmn/analyze_power.py \
  --run build/qbox-apollo-qvp/gem5/stable-rebase-20261024/resume-cache-ap4 \
  --profile hsoc-stack/tools/gem5/configs/zena_cmn/profiles/power/unconfigured.json \
  --output build/qbox-apollo-qvp/gem5/power-offline
```

`activity.jsonl`, `energy.jsonl`, `power-summary.json`을 생성한다.
이 offline 명령은 ROI 전체에 대응하는 exact stats block이 있는 기존 실행을
대상으로 한다. 주기적 reset이 있는 online 실행은 아래 online ledger와
Root `result.json`의 ROI-only summary를 사용한다.
Native residency가 ROI 전체를 덮지 않는 과거 binary 결과는 ON 시간으로
임의 보정하지 않는다. Missing counter도 문서화된 `nozero` 항목만 0으로 해석한다.

## SCMI 및 online 실행

기본 launcher는 power 기능을 끈다. `--power-control`로 AP-only synthetic
SCMI service를 활성화한다. AP4는 1개, AP16은 4개 cluster policy를 사용한다.
Atomic CPU와 측정용 `roi_cpu`가 같은 cluster clock/voltage를 공유한다.
Ruby/CMN 및 DRAM clock은 CPU DVFS에 무조건 종속시키지 않는다.

Reference 초기 OPP는 2GHz/0.85V이며 2.5GHz/0.95V, 1.8GHz/0.75V도 제공한다.
Transition latency 1200us와 이 OPP 표는 synthetic assumption이다.
1THz simulator tick 기준 native period는 각각 500/400/556 ticks다.
1.8GHz는 정수 tick 양자화로 약 1.79856GHz이며 SCMI readback은 nominal 1.8GHz다.
SCMI Performance cost는 abstract cost이며 mW 값이 아니다.
SCMI sustained frequency는 2GHz이므로 Linux는 2.5GHz를 turbo OPP로 분류한다.
기본 boost-off 상태에서 2.5GHz 요청은 제한된다. 일반 DVFS 시험은
2.0GHz와 1.8GHz를 사용한다. Thermal feedback fixture는 boost와 policy maximum을
명시적으로 2.5GHz로 설정한 뒤 hot-start sensor에 의한 cooling을 확인한다.

MHUv1 base `0x2a000000`, shared memory `0x2a020000`, INTID 92/93/94를
사용한다. 이는 gem5 내부 service이며 QBox의 MHUv3/SCP firmware나 실제
Apollo power sequencer를 재현한다고 해석하지 않는다. Kernel의 MHUv3는 유지한다.
Linux 부팅에 limits-change notifier 등록 경고가 남는다. 이번 검증은 동기
Performance/Sensor 요청과 cpufreq/thermal 경로이며 SCMI notification 전체 지원을
의미하지 않는다.

```sh
./run_gem5_linux.sh --headless --power-control \
  --workload command \
  --command 'gem5-control run apollo-power-probe 4 1800000'
```

Probe는 policy 개수, SCMI driver, requested/actual frequency, cluster sensor,
CPU0 memory checksum을 검사한다. Probe 자체에는 m5 marker가 없으므로
`gem5-control run`을 한 번 사용한다. AP16은 launcher `--cpus 16`과 probe의
첫 인자를 함께 16으로 바꾼다.

SCMI를 켠 cache/DRAM benchmark는 DVFS stats reset을 정확히 수집하도록
online profile을 함께 요구한다. Control-only command probe는 허용한다.

Online mode는 다음 옵션을 함께 사용한다.

```text
--power-control
--power-profile /absolute/path/to/coefficients.json
--thermal-profile /absolute/path/to/thermal-profile.json
--power-interval-us 100
```

Power profile과 thermal profile은 반드시 명시한다. Thermal profile은
`thermal_replay.py`가 생성한 `thermal-profile.json` 또는 같은 schema의
명시적 RC profile을 사용한다. Thermal nodes는 실행 topology의 actor mapping을
모두 포함해야 한다. AP4/16 전환 시 core/DSU nodes도 함께 확인한다.
`--temperature-mc`는 SCMI의 boot 초기 sensor 값이며 online 시작 후에는
RC model의 native temperature가 sensor를 갱신한다.

Atomic boot와 boot-checkpoint restore에서는 timing energy를 계산하지 않는다.
O3 전환 후 warmup부터 accounting을 시작하고, ROI marker에서 epoch를 닫는다.
Online accounting은 stats dump/reset과 DVFS 경계를 한 owner가 관리한다.
단순히 모든 stats dump의 energy를 더하지 않는다.

## 결과 및 검증

| 파일 | 의미 |
|---|---|
| `online-activity.jsonl` | 실제 counter와 reset-bounded epoch |
| `online-energy.jsonl` | 해당 epoch의 activity-derived J/W |
| `online-thermal.jsonl` | interval 시작/끝 temperature와 native clock |
| `online-power-summary.json` | 전체 timing history 및 host accounting 비용 |
| Root `result.json`의 `power` | warmup/exit를 제외한 정확한 ROI energy/temperature |

Native power stats는 직전 latch를 나타낼 수 있으므로 현재 epoch의 J/W는
`online-energy.jsonl`을 사용한다. Retrospective accounting에서는 native
held-energy와 activity energy를 중복 합산하지 않는다.

Collector는 native stats를 block별로 streaming하여 파일 전체를 메모리에
보관하지 않는다. 523MB AP4 stats 재분석에서 이전 결과와 동일한 JSON
값을 확인했고 process peak RSS는 약 150MiB였다.
Collector는 ROI 전체를 덮는 연속 epoch와 각 epoch의 유일한 stats block을
요구한다. Instruction/byte/hit/miss count만 합산하고 비율은 다시 계산한다.
Occupancy, histogram, voltage, 이미 계산된 bandwidth를 단순 합산하지 않는다.
Online 옵션을 켠 command가 O3 ROI marker 없이 종료하면 power PASS가 아니다.

AP16의 full native stats는 epoch당 약 3.7MB이며 이번 host에서 dump 자체에
약 0.8초가 들었다. 100us sampling은 짧은 guest 시간에도 큰 host 비용과
파일 크기를 만든다. `online-power-summary.json`의 비용을 확인하고, 반복 분석은
예를 들어 `--power-interval-us 1000`과 half-interval 수렴 시험으로 적절한 값을
선정한다. Interval 변경 시 checkpoint도 다시 만들어야 한다. 이 host 비용을
guest 성능이나 전력으로 해석하지 않는다.

Sampling interval/half-interval 수렴, fixed OPP에서 power off/on의 결과,
AP4/AP16 policy/clock/sensor 검증을 별도로 기록한다. 상세 실행 증거는
`build/qbox-apollo-qvp/gem5/power-integration-20261024/`에 보존한다.
아래는 scoped integration 검증 결과다. 전체 요약은 evidence root의
`validation-summary.json`에 기록했다.

| 검증 | 상태 |
|---|---|
| Offline 실제 Apollo ROI 분석 | PASS, synthetic ledger; 미지정 계수는 PARTIAL/UNCALIBRATED |
| Root host regression | 34 PASS, streaming 및 init quiescence 포함 |
| Native build | PASS, Yocto compile 426 tasks |
| Native energy/residency/thermal boundary | 20 PASS |
| Native stats/step/SCMI AP4/AP16 | 5 PASS |
| Native RC 100us/50us convergence | energy 차이 0.0019%, 최종 temperature 최대 차이 0.000294°C |
| Image build | PASS, 4167 tasks; packaged probe 및 kernel config 확인 |
| Instantiated config 및 mutation tests | AP4 online 21 PASS/3 SKIP, AP16 online 22 PASS/2 SKIP, AP4 power-off 20 PASS/4 SKIP |
| SCMI DTB directed fixture | AP4/AP16 PASS |
| AP4 SCMI/O3 probe, 1차 image | PASS, 1.8GHz readback 및 native 556 ticks/0.75V |
| AP4 power-off/on cache, 1차 image | PASS, ROI ticks/checksum/cache counters/DRAM bytes 일치; online 3 epochs |
| Snapshot quiescence host tests | init fixture 3 PASS, native idle guard policy 6 PASS |
| 수정 image의 Atomic snapshot | AP4 power-off/on, AP16 power-on 모두 COMPLETE |
| 수정 image의 AP4 resume/O3 probe | PASS, policy/sensor/checksum 및 ROI energy |
| 수정 image의 AP4 thermal feedback | PASS, 80.006°C hot-start → cooling state 1 → 2.5GHz/0.95V에서 2.0GHz/0.85V |
| 수정 image의 AP16 resume/O3 probe | PASS, Atomic 준비 후 O3에서 4 policy/4 sensor/checksum; 모든16 CPU actor 500/.85 → 556/.75, ROI 79 epochs |

### Runtime evidence 읽기

최종 image는 `nexios-gem5-initramfs-apollo-qvp-20261024074854.cpio.gz`이며
native SHA256은 `a850488c5f2223d51119787048bd168898f1bb084c0e6b27aeb434854be24030`다.
증거 root는 `build/qbox-apollo-qvp/gem5/power-integration-20261024/`다.

- `boot-{baseline-ap4,online-ap4,online-ap16}-v2/result.json`: 실제 부팅·snapshot 저장.
- `cache-{baseline,online}-ap4-v2/result.json`: 정식 cache launcher와 online collector.
- `probe-online-ap4-v2/result.json`, `probe-prepared-ap16-v2/result.json`: Linux SCMI probe 및 ROI power.
- `thermal-feedback-validation.json`: Linux cooling과 native clock/voltage 변화.
- `cache-invariance-v2.json`: 32KiB, 128 passes, 2GHz/0.85V 고정 비교.
- `image-v2-verification.json`: packaged init와 수정 소스의 byte 동일성.

Resume은 저장된 native OPP와 guest governor를 복원한다. 초기 config의 2GHz는
resume 이후 주파수를 강제하지 않는다. 실제 새 image의 일반 cache 실행에서는
governor가 1.8GHz를 선택했으며, 이를 power accounting의 timing overhead로
해석하면 안 된다. 고정 2GHz 비교는 native 500 ticks/0.85V를 확인했고,
power-off 대비 ROI 시간 차이는 약 0.00064%였다. 허용치는 engineering regression
기준 5%이며 silicon 정확도 기준이 아니다.

AP16 최종 probe는 thermal polling 비활성화, userspace governor 및 2GHz 준비를
Atomic 구간에서 수행하고, 4개 cluster의 2.0→1.8GHz 변경/readback, sensor와
checksum 검증을 O3 ROI에 포함한다. `probe-ap16-prepared.sh`가 실제 fixture다.
Governor 정리까지 O3에 포함한 `probe-online-ap16-v2`는 policy0만 완료한
장시간 진단 실행으로 중단했으며 PASS가 아니다. 그 경로에는 RCU/worker
동기화가 포함되지만 정확한 wait site나 deadlock은 확인하지 않았다.

고정 OPP fixture는 설정 후 자체 종료하는 `apollo-bench`를 custom command로
실행했다. 이 경우 shell 완료 marker까지 돌아오지 않아 launcher의 command 결과는
FAIL로 보존했다. 별도 collector가 benchmark checksum, exact ROI, epoch ledger를
검증한 결과를 `cache-invariance-v2.json`에 기록했다. 일반 benchmark 실행은
`--workload cache`를 사용하며 위 두 정식 launcher 결과는 PASS다.

1차 AP16 저장은 outstanding SCMI channel 때문에 거부됐다. 이 실패를 보존하고
init quiescence 및 drain 전후 idle 검사를 추가한 뒤 새 image로 재검증했다.
첫 thermal fixture의 2.5GHz 설정 실패는 boost-off 조건 때문이며, 최종 fixture는
boost와 maximum을 명시적으로 설정한다. Thermal 검증은 RC node를 80°C에서
시작하는 기능 시험으로, workload에 의한 실제 온도 상승을 검증한 것은 아니다.

## Snapshot과 제외 범위

Commit의 pre-commit formatter가 Python config/analysis 파일의 표현 형식을
정규화했다. AST 동등성은 확인했지만 raw source hash는 달라졌으므로 위 runtime
snapshot은 현재 checkout에서 그대로 resume할 수 없다. 새 snapshot을 생성해야
한다. 검증 당시 config는 evidence root의 `commits/validated-configs/`에 보존했다.
기존 launcher/snapshot contract의 hash 검사를 우회하지 않는다.

기존 diskless Atomic boot snapshot만 지원한다. Native binary, kernel/image,
config source, coefficient/RC profile, control 설정, sampling interval이 바뀌면
새 snapshot이 필요하다. SCMI를 켠 initramfs는 저장 전에 cluster thermal mode와
SCMI governor를 `/run/gem5-checkpoint-power/`에 보존하고, thermal polling과
governor 요청을 일시 정지한 뒤 50ms를 기다린다. Resume 직후 원래 설정을
복원하고 새로운 workload의 `readfile`을 읽는다. 50ms는 engineering margin이며
저장 전후 native SCMI idle 검사가 최종 조건이다. Busy이면 저장을 거부하며,
host가 guest를 임의 재실행해 `readfile` 경계를 지나가지 않는다.
입력 검사를 우회하지 않는다. 서로 다른 profile의
snapshot을 같은 이름으로 덮어쓰지 않는다.

DRAM command backend, DRAM I/O/WCK energy, calibrated electrical coefficients,
full-SoC SCP power sequencing, AP hot timing checkpoint는 이번 적용 범위 밖이다.
Orin의 board/rail 전력을 A720AE per-event coefficient로 직접 옮기지 않는다.
