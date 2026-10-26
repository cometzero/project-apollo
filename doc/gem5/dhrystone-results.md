# Dhrystone loop ROI 측정 결과

2026-10-26, Apollo AP gem5의 CPU0 O3 / 2 GHz에서 측정을 완료했다.
20,000회 기준 **5,394.51 DMIPS, 2.69726 DMIPS/MHz**이다.
이는 `UNCALIBRATED_AP_MODEL`의 instrumented loop ROI 결과이며,
실제 Cortex-A720AE hardware 성능이나 원본 guest timer 점수를 의미하지 않는다.

## 측정 조건 및 결과

- Binary: Yocto에서 빌드한 `dhry-gem5`, Dhrystone 2.1.
- Compiler baseline: `-O2 -fno-inline -fno-lto`, `-mcpu=cortex-a720+crypto`.
  Yocto의 branch protection, FORTIFY, stack protector 및 dynamic libc를 유지했다.
- CPU0 affinity, Atomic → O3 switch 후 warmup 1,000회.
  Benchmark state를 초기화한 후 원본 loop body만 ROI로 측정했다.
- 각 반복 조건을 한 번씩 실행했다. 입력, 결과 출력 및 shutdown은 ROI 밖이다.

| 항목 | 10,000회 | 20,000회 |
|---|---:|---:|
| DMIPS | 5,394.21735 | 5,394.51133 |
| DMIPS/MHz | 2.697109 | 2.697256 |
| Cycles/iteration | 211.0230 | 211.0115 |
| IPC | 1.416915 | 1.416988 |
| CPU cycles | 2,110,230 | 4,220,230 |
| Committed instructions | 2,990,017 | 5,980,017 |
| ROI simulated time | 1.055115 ms | 2.110115 ms |
| ROI host time | 22.46 s | 41.99 s |
| 전체 실행 host time | 191.49 s | 212.31 s |
| Guest 결과값 검사 / 정상 종료 | PASS | PASS |
| Collector ROI 검증 | PASS | PASS |

반복량을 두 배로 늘렸을 때 DMIPS 차이는 **+0.00545%**이다.
두 길이에서 반복당 비용은 거의 같지만, 동일 조건 반복 실험의 분산 검증은 아니다.
전체 실행 시간에는 snapshot restore, binary 전달, 결과 출력 및 shutdown이 포함된다.
최초 snapshot 생성에는 별도로 약 1,295초가 걸렸다.

```text
simulated_seconds = (roi_end_tick - roi_begin_tick) / simFreq
DMIPS = runs / simulated_seconds / 1757
DMIPS/MHz = DMIPS / 2000
```

`simFreq=10^12`, CPU clock period는 500 ticks이다. Collector는 실제 config의
clock domain과 CPU0 O3 설정을 확인하고, ROI begin/end와 정확히 일치하는
stats block 하나만 사용한다. Host 실행 시간은 점수 계산에 사용하지 않는다.
ROI marker 경계의 작은 비용과 ROI 내부 interrupt는 포함된다.

## Binary 및 snapshot provenance

Evidence directory:
`build/qbox-apollo-qvp/gem5/dhrystone-dmips-20261026/`.

기존 snapshot은 계측 binary 추가 전 initramfs로 생성됐다. 해당 snapshot에
맞는 `base-initrd.cpio.gz`를 그대로 지정하고, 새 Yocto package의 binary를
readfile command script로 `/tmp/dhry-gem5`에 전달했다. Guest에서 SHA256을
검증한 후 실행했으며 snapshot compatibility 검사를 우회하지 않았다.
전달에는 guest에서 지원되는 shell octal `printf`를 사용했다.
초기 base64 전달 시도는 해당 applet이 없어 측정 전에 실패했으며 결과에서 제외했다.

| Artifact | SHA256 |
|---|---|
| 측정한 `dhry-gem5` | `8982fa7569224f760479e231d091a0df9122f7f59b3ce5a7dc3efb525dc07b4c` |
| 새 initramfs | `dd35b5db6831fc2340e3e977bfccd61910d286687260489a6a0859018d7a1359` |

`binary-verification.json`에서 새 initramfs와 package의 계측 binary가 동일함을
확인했다. 원본 `dhry`의 `.text`/`.rodata`도 이전 build와 동일하다.
`measurement-10000.json`, `measurement-20000.json`, `summary.json`에
수치와 검증 결과를 보존했다. 각 `roi-N/m5out/`에는 UART, config, stats,
ROI event가 있고 `roi-N/result.json`에는 launcher 종료 결과가 있다.

## 재현

보존한 campaign의 snapshot으로 실행:

```sh
campaign=build/qbox-apollo-qvp/gem5/dhrystone-dmips-20261026
./run_gem5_linux.sh --headless \
  --initrd "$campaign/base-initrd.cpio.gz" --resume "$campaign/snapshot" \
  --out-dir /tmp/dhry-repeat-20000 --workload command \
  --command-file "$campaign/run-20000-octal.sh" --timeout 7200
python3 scripts/gem5/summarize_dhrystone.py /tmp/dhry-repeat-20000
```

새 initramfs는 `dhry-gem5`를 포함하므로 fresh boot에서는 직접 실행한다.
새 이미지에 맞게 생성한 snapshot에는 `--resume`을 추가할 수 있다.

```sh
./run_gem5_linux.sh --headless --out-dir /tmp/dhry-new-image \
  --workload command --command 'dhry-gem5 20000 1000'
python3 scripts/gem5/summarize_dhrystone.py /tmp/dhry-new-image
```

자체 switch/ROI marker가 있으므로 `gem5-control run`으로 감싸지 않는다.
Yocto image build 및 collector의 10개 focused tests가 통과했다.
원본 `dhry`의 장시간 timer 측정, hardware 비교 및 CPU model 보정은 수행하지 않았다.
Dhrystone 결과 하나로 cache/DRAM bandwidth 정합성을 판정하지 않는다.
