# Dhrystone O2/O3·Orin 비교와 gem5 stall 분석

2026-10-26 측정. 현재 model은 O2→O3 변경에 거의 반응하지 않지만,
Orin에서는 같은 toolchain/libc 조건에서 약 4.98% 향상됐다.
gem5의 branch-protection diagnostic은 약 27.10% 향상됐으며,
non-speculative 처리와 queue backpressure가 크게 줄었다.
CPU/cache/DRAM model parameter와 배포 binary의 보안 옵션은 변경하지 않았다.

## 1. 비교 조건과 결과

| 항목 | Apollo gem5 | Jetson AGX Orin |
|---|---|---|
| CPU | A720AE 대상 O3 model, CPU0 | Cortex-A78AE, CPU0 |
| Frequency | 2,000 MHz | 2,201.6 MHz |
| Compiler | Yocto GCC 14.3.0 | 같은 Yocto compiler |
| Target | `-mcpu=cortex-a720+crypto` | 같은 target, 이번 workload 실행 성공 |
| Common options | `-fno-inline -fno-lto`, branch protection/stack protector/FORTIFY 유지 | 동일 |
| libc/loader | 기존 snapshot의 glibc 2.41 | 해당 initramfs에서 추출한 동일 bytes |
| 측정 | loop ROI 20,000회, warmup 1,000회 | 원본 timer 100,000,000회 × 3 runs |
| Timebase | simulated elapsed ticks | `times()` user CPU time, 100 Hz |

| 플랫폼 / 조건 | DMIPS | DMIPS/MHz | Cycles/iteration |
|---|---:|---:|---:|
| gem5 O2 baseline | 5,394.5113 | 2.697256 | 211.01150 |
| gem5 O3 | 5,394.5228 | 2.697261 | 211.01105 |
| Orin O2 평균 | 18,846.5035 | 8.560367 | 미측정 |
| Orin O3 평균 | 19,785.1740 | 8.986725 | 미측정 |
| gem5 O2 diagnostic, branch protection off | 6,856.5463 | 3.428273 | 166.01710 |

O3 향상은 gem5 약 **0.00021%**, Orin 약 **4.9806%**다.
Orin O2 normalized score는 gem5 O2의 약 3.17배이나,
CPU 종류 및 timer/ROI 차이가 있으므로 이를 A720AE 보정 배율로 사용하지 않는다.
Diagnostic은 배포 baseline 또는 hardware 보정 결과가 아니다.

Orin 각 run은 약 2.87–3.04초의 user CPU time을 사용했다.
O2 범위는 18,722.10–18,908.70 DMIPS,
O3 범위는 19,762.22–19,831.08 DMIPS다.
CPU policy의 minimum을 일시적으로 maximum에 맞춘 뒤 원래 729,600 kHz로 복원했다.
각 실행 전후 scaling 및 hardware frequency는 2,201,600 kHz였다.
이는 continuous clock/PMU 관측을 의미하지 않는다.
허용받은 `dal-e_ros_can_bridge.service`, `dal-e_state_manager.service`는 중지 상태로 두었다.
Orin system libc는 변경하지 않고 private loader로 실행했다.

## 2. 정확한 ROI의 model 통계

O2와 O3는 각각 한 번의 20,000회 측정이며, 기존 O2의 10,000회 결과와도
반복당 비용이 거의 같았다. Statistics는 ROI begin/end와 일치하는 block만 사용했다.

| Counter | O2 | O3 | O2 protection-off diagnostic |
|---|---:|---:|---:|
| CPU cycles | 4,220,230 | 4,220,221 | 3,320,342 |
| `commitNonSpecStalls` | 280,002 | 280,002 | 20,002 |
| Issued `No_OpClass` | 280,000 | 280,000 | 20,000 |
| Rename ROB-full events | 539,941 | 459,961 | 0 |
| Rename LQ-full events | 419,956 | 419,961 | 0 |
| IEW LSQ-full events | 119,988 | 119,988 | 0 |
| Fetch I-cache wait cycles | 1,760,158 | 1,720,153 | 2,000,086 |

Baseline의 L1D demand miss는 0, L1I demand miss는 3, DRAM read는 총 128 bytes다.
Commit branch misprediction도 7회뿐이다. 따라서 이 결과는 DRAM bandwidth 부족이나
빈번한 cache miss가 주 병목이라는 해석을 지지하지 않는다.
`icacheStallCycles`는 hit 응답을 기다리는 시간도 포함하므로 I-cache miss stall로
표기하지 않는다. Queue-full event와 stall counter는 겹칠 수 있어 서로 더해
전체 CPI breakdown을 만들지 않는다.

현재 BTI decode는 `WarnUnimplemented`를 생성하고, 이 class는 `IsNonSpeculative`를
설정한다. Commit head에서 실행을 요청하는 경로가 생긴다:

- `hsoc-stack/tools/gem5/src/arch/arm/isa/formats/aarch64.isa`
- `hsoc-stack/tools/gem5/src/arch/arm/insts/pseudo.cc`
- `hsoc-stack/tools/gem5/src/cpu/o3/commit.cc`

Diagnostic은 두 C translation unit에만 `-mbranch-protection=none`을 추가했다.
Non-speculative counter는 반복당 14개에서 1개로 줄었고 queue-full event가 사라졌다.
이는 보호 명령의 model 처리와 backpressure 사이의 강한 연관 증거다.
다만 BTI, PAC/return instruction 및 address/alignment가 함께 바뀌었으므로
27.10% 향상의 전부를 BTI 하나의 비용으로 해석하지 않는다.
CRT/libc의 보호 명령은 여전히 남으며, CPU model의 기능을 수정한 실험도 아니다.

Model의 fetch/decode/rename/dispatch/issue/commit width는 8,
ROB192, IQ128, LQ32, SQ64다. Integer divide latency는 20 cycles이며 ROI에서
반복당 한 번 실행된다. `configs/zena_cmn/a720ae_fu.py`가 명시하듯 integer/LSU는
native mapping이며 전체 A720AE pipeline의 정확한 재현을 보증하지 않는다.
Counter만 보고 width나 queue를 확대하거나 divide latency를 축소하지 않았다.

Collector IPC는 `thread_0.numInsts` 기준으로 NOP를 제외한다.
O2→O3에서 이 count는 5,980,017→5,960,017이지만 전체 commit instruction count는
둘 다 6,020,017이다. 따라서 collector IPC 감소를 O3 실행시간 악화로 해석하지 않는다.

## 3. Build 및 검증

Owned `dhrystone_%.bbappend`에 `dhry-gem5-o3`를 추가했다.
`dhry-gem5`는 기존 O2와 byte 단위로 동일하고, 원본 `dhry`도 O2로 유지한다.
O3의 두 translation unit 모두 `-O3`로 컴파일하며 source merging/LTO는 사용하지 않는다.

- Yocto `image_complete`: 3,678 tasks 성공, 3,661 reused.
- 기존 forced kernel task taint warning 2개. 새 build failure 없음.
- `dhry`, `dhry-gem5`, `dhry-gem5-o3`: package와 initramfs bytes 일치.
- 새 compressed initramfs: 12,240,843 bytes.
- Orin: 6 runs의 22개 final values 및 pointer consistency PASS.
- Original-output parser의 corrupted-result 거부 self-check PASS.
- gem5 ROI collector: 10 focused tests PASS.
- O3 및 protection-off diagnostic: guest final-value 검사, 정상 종료 및 exact ROI 검증 PASS.

기존 snapshot의 입력 계약은 그대로 유지했다. 저장된 `base-initrd.cpio.gz`를 지정하고
새 binary를 readfile script의 octal `printf`로 전달하여 guest SHA256 검증 후 실행했다.
새 initramfs와 구 snapshot의 compatibility 검사를 우회하지 않았다.

## 4. Evidence와 재현

Campaign: `build/qbox-apollo-qvp/gem5/dhrystone-compare-20261026/`

- `build.log`, `yocto-run.do_compile`, `yocto-compile.log`: image build 및 실제 compiler 명령.
- `binary-verification.json`: package/image 비교 및 SHA256.
- `o3-20000/`, `o2-no-branch-protection/`: UART, config, ROI events, stats, launcher result.
- `measurement-o3.json`, `measurement-diagnostic.json`, `summary.json`: 검증된 측정 결과.
- `analysis/`: exact ROI counters와 binary disassembly 비교.
- `orin/`: build/실행/검증 script, 개별 출력, clock 관측, libc hashes 및 summary.

```sh
base=build/qbox-apollo-qvp/gem5/dhrystone-dmips-20261026
campaign=build/qbox-apollo-qvp/gem5/dhrystone-compare-20261026
./run_gem5_linux.sh --headless --initrd "$base/base-initrd.cpio.gz" \
  --resume "$base/snapshot" --out-dir /tmp/dhry-o3-repeat \
  --workload command --command-file "$campaign/run-o3-20000.sh" --timeout 7200
python3 scripts/gem5/summarize_dhrystone.py /tmp/dhry-o3-repeat
```

Diagnostic은 command file을 `run-o2-no-branch-protection.sh`로 바꾸고 별도
output directory를 사용한다. 새 initramfs fresh boot에서는
`--command 'dhry-gem5-o3 20000 1000'`으로 직접 실행할 수 있다.
Orin 재현은 `orin/README.md`와 저장한 `build.sh`, `run-remote.sh`를 따른다.

## 5. 다음 model 검증 대상과 한계

우선순위는 BTI/hint 및 PAC/return 처리의 기능·timing 검증이다. 보호 기능을
비활성화하여 score를 맞추는 방법은 사용하지 않는다. BTI-only/PAC-only controlled
variant나 짧은 instruction trace로 비용을 더 분리한 뒤, 실제 architectural behavior와
O3 speculative execution 규칙에 맞는 수정 및 regression 검증이 필요하다.
그 이후 남는 차이에 대해 frontend hit response, dependency, integer divide timing을
검토하고 여러 benchmark로 교차 검증한다.

이번에는 model 수정, A720AE hardware 비교, continuous PMU cycle 관측,
Arm 권장 20초 × 10회 실험을 수행하지 않았다. gem5는 약 1.66–2.11 ms loop ROI,
Orin은 약 3초 user CPU timer이며 동일 measurement scope가 아니다.
정확한 ticks로 계산하더라도 짧은 ROI의 정합성이 hardware qualification을 뜻하지 않는다.

후속 BTI/PAC 분리 시험과 decoder 수정은
[BTI 수정 및 재측정](dhrystone-bti-fix.md)에 별도로 기록한다.
