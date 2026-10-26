# BTI decode 수정과 Dhrystone 재측정

2026-10-26 작업. 이전 [O2/O3·Orin 비교](dhrystone-comparison.md)에서 발견한
BTI serialization을 분리 검증하고, architectural 동작에 맞게 decoder를 수정했다.
CPU width, queue, cache/DRAM timing 및 compiler 보안 옵션은 변경하지 않았다.

## 1. 수정 범위

변경한 model source는
`hsoc-stack/tools/gem5/src/arch/arm/isa/formats/aarch64.isa`의 BTI decode 한 곳이다.
현재 gem5는 `ID_AA64PFR1_EL1.BT=0`이고 `FEAT_BTI`/HWCAP2.BTI를 제공하지 않는다.
[Arm ISA](https://documentation-service.arm.com/static/685eb35c3cb5b729562ba389)의
feature-absent 동작에 따라 네 BTI encoding을 `NopInst`로 decode한다.
기존 `WarnUnimplemented`는 `IsNonSpeculative`여서 O3 commit에서 불필요한 정체를
발생시켰다. Generic `WarnUnimplemented`, 다른 HINT 및 PAC 구현은 변경하지 않았다.

이 수정은 BTI guarded-page/BTYPE enforcement 구현이 아니다. 추후 FEAT_BTI를
노출하려면 branch target 검사와 fault/state 동작을 구현하고 새로 검증해야 한다.
현재 AP full-system release에는 FEAT_PAuth도 없다. 아래 compiler option 이름은
생성한 명령을 뜻하며 AP Linux에서 해당 보안 기능이 활성화됐다는 뜻이 아니다.

## 2. 기존 native에서 BTI/PAC 분리

같은 Yocto GCC/source/libc로 20,000회 ROI, warmup 1,000회, CPU0 2 GHz를 사용했다.
Original native를 별도 파일로 보존하고 원래 snapshot과 hash 검사를 유지했다.

| Compiler branch protection | DMIPS/MHz | Cycles/iteration | Non-spec stalls |
|---|---:|---:|---:|
| `standard`, 기존 baseline | 2.697256 | 211.01150 | 280,002 |
| `pac-ret`, PAC 명령 유지·application BTI 제거 | 3.270669 | 174.01700 | 20,002 |
| `bti`, BTI 유지·application PAC 제거 | 2.503485 | 227.34385 | 320,002 |
| `none`, 이전 진단 | 3.428273 | 166.01710 | 20,002 |

`pac-ret`에서는 ROB/LQ/LSQ full event가 모두 0이었다. `bti`에서는 implicit PAC
landing instruction 대신 explicit BTI가 추가되어 non-spec 명령이 반복당 16개로
늘었다. BTI 처리에 따른 backpressure를 지지하지만 code layout도 바뀌므로
compiler variant 간 모든 cycle 차이를 BTI 단일 명령 latency로 환산하지 않는다.
CRT/libc의 잔여 보호 명령도 남아 있다. 두 분리 실행 모두 checksum/ROI/종료 PASS다.

## 3. 기능 회귀 시험

| 시험 | 기존 native | 수정 native |
|---|---|---|
| 네 BTI encoding × 1,024, register/SP/NZCV 보존 | Atomic/Timing/O3 PASS | Atomic/Timing/O3 PASS |
| BTI 시험 O3 non-spec stalls | 4,098: regression FAIL | 2: PASS |
| PAuth 비활성 상태의 13 HINT case | 이번 작업에서 미실행 | Atomic/Timing/O3 PASS |
| 별도 PAuth-enabled EL3 fixture | Atomic/O3 PASS | Atomic/O3 PASS |

BTI loop 4,096개가 serialization을 만들던 현상을 재현한 뒤 수정했다.
수정 후 남은 2회는 test의 Linux syscall에 해당한다.

Enabled PAC fixture는 별도 Armv8.3 system에서 APIA key와 `SCTLR_EL3.EnIA`를
설정한다. Signature가 실제 pointer를 변경하는지, 정상 authentication/branch,
wrong modifier 거부, branch recovery, 잘못 인증된 target의 same-EL instruction
abort (`ESR_EL3.EC=0x21`)를 검사한다. 기존 O3 pipeline trace에는 AUTIA가
issue/complete됐으나 retire하지 않은 사례도 보존했다. 이 fixture는 AP profile을
변경하지 않으며 EL0/Linux 전체 보안 qualification으로 해석하지 않는다.

Tests와 재현 명령은
`hsoc-stack/tools/gem5/tests/gem5/arm_zena_css/README.md`에 있다.
초기 enabled-PAC fixture는 ELF 배치가 memory range와 맞지 않아 실패했다.
`-Ttext=0x80010000`으로 수정한 `old-v2` 이후 실행만 위 검증 결과에 사용한다.

## 4. Build 및 artifact 계약

```sh
APOLLO_BUILD_THREADS=2 APOLLO_PARALLEL_MAKE=-j2 \
  ./yocto_build.sh --keep-conf gem5-native
```

Native build/deploy는 815 tasks 성공, 806 reused였다. Guest package/compiler
조건은 기존 O2/O3 결과와 동일하게 유지했다. Native SHA256:

```text
old: 68a4cbd6579644fe32f59086b67dad406dfaae3d47d2cff6ac26d7a5c0f797dc
new: 037aee4e6f8e2ae63cd4d9f381c88e47c92338f08f5fc5a30b43e05d7e79a3ef
```

Native가 바뀌었으므로 기존 snapshot compatibility를 우회하지 않고, 기존
`dhrystone-dmips-20261026/base-initrd.cpio.gz` 및 kernel로 새 snapshot을 생성했다.
Boot는 1,300.12초에 `NEXIOS_GEM5_INITRAMFS_READY` 및 `CHECKPOINT_SAVED`로 완료됐다.
새 snapshot의 launcher contract는 기존 contract와 native SHA256만 다름을 검사했다.
측정 binary는 이전 O2/O3와 같은 bytes를 readfile로 전달하고 guest SHA256을 검사한다.

Campaign: `build/qbox-apollo-qvp/gem5/dhrystone-bti-20261026/`

- `isolation/`: 이전 native의 BTI/PAC 분리 측정 및 source/build/disassembly.
- `native-build.log`, `input-hashes.json`: build 및 simulator/image/workload provenance.
- `bti-regression-{old,new}/`, `pac-disabled-new/`: focused regression.
- `pac-enabled-{old-v2,new}-{atomic,o3}/`: 별도 enabled PAC 실행.
- `pac-enabled-old-trace/`: wrong-path AUTIA pipeline trace 및 추출 근거.
- `boot/`, `snapshot/`: 새 Linux boot/checkpoint.
- `contract-comparison.json`: 이전 snapshot과 native SHA256 이외의 입력이 동일함을 확인.
- `gem5-fixed.opt`, `gem5-fixed-native.json`: 수정 native와 runtime 경로 보존.

## 5. 수정 native의 Linux snapshot 재측정

동일 O2/O3 binary, CPU0 O3 2 GHz, warmup 1,000회, measured loop 20,000회 조건이다.
두 실행 모두 guest final-value 검사, exact ROI collector, 정상 shutdown PASS다.

| 항목 | 이전 O2 | 수정 O2 | 수정 O3 |
|---|---:|---:|---:|
| DMIPS | 5,394.5113 | **7,587.7798** | **7,742.6424** |
| DMIPS/MHz | 2.697256 | **3.793890** | **3.871321** |
| Cycles/iteration | 211.01150 | 150.01805 | 147.01750 |
| CPU cycles | 4,220,230 | 3,000,361 | 2,940,350 |
| Non-speculative commit stalls | 280,002 | **2** | **2** |
| ROI simulated time | 2.110115 ms | 1.5001805 ms | 1.470175 ms |
| ROI host time | 41.99 s | 41.35 s | 41.80 s |
| Restore부터 shutdown까지 host time | 212.31 s | 226.75 s | 230.37 s |

동일 O2의 score는 **40.6574% 상승**했다. 수정 후 O3는 O2보다 **2.0409%** 높다.
새 실행은 다른 probe와 병렬로 진행했으므로 host time을 CPU 성능 개선율로
사용하지 않는다. Score는 simulated ticks로 계산한다.
앞선 Orin O2/O3의 8.5604/8.9867 DMIPS/MHz와는 여전히 차이가 있으나,
A78AE와 A720AE proxy, 원본 user CPU timer와 짧은 loop ROI 차이를 유지해 해석한다.
이 차이에 맞춰 CPU parameter를 임의로 조절하지 않았다.

기본 AP의 Linux PAC probe는 `HWCAP_PACA`가 없어 exit 77 및
`PAUTH_LINUX status=SKIP reason=no_HWCAP_PACA`를 출력했다.
`pac-default-verification.json`은 기본 비활성 계약을 PASS로, enabled Linux PAC
검증을 **SKIP**로 분리한다. 별도 EL3 enabled fixture PASS와 혼동하지 않는다.

결과는 `measurement-o2.json`, `measurement-o3.json`, `summary.json`에 있으며,
각 `o2-20000/`, `o3-20000/`에 UART/config/stats/ROI events를 보존했다.

```sh
base=build/qbox-apollo-qvp/gem5/dhrystone-dmips-20261026
campaign=build/qbox-apollo-qvp/gem5/dhrystone-bti-20261026
./run_gem5_linux.sh --headless --initrd "$base/base-initrd.cpio.gz" \
  --resume "$campaign/snapshot" --out-dir /tmp/dhry-bti-fixed-o2 \
  --workload command --command-file "$campaign/run-o2-20000.sh" --timeout 7200
python3 scripts/gem5/summarize_dhrystone.py /tmp/dhry-bti-fixed-o2
```

이 명령은 현재 deploy native SHA256이 위 new 값인 경우에 해당한다.
O3는 `run-o3-20000.sh`와 별도 output directory를 사용한다.
Deploy가 바뀌면 보존한 `gem5-fixed.opt`를 `--gem5`로 지정하고,
`gem5-fixed-native.json`의 `PYTHONHOME`, `LD_LIBRARY_PATH`와 해당 Yocto Python을
`PYTHON` 환경변수로 지정한다. Custom binary에는 launcher가 manifest를 자동 적용하지 않는다.

이 결과는 native model의 잘못된 serialization 수정 검증이다. A720AE hardware
성능 보정이나 BTI/PAC를 포함한 전체 Arm security 기능 인증을 뜻하지 않는다.
