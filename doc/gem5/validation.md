# 검증 수준, provenance 및 유지보수

[문서 목차](README.md) · [Benchmark guide](benchmark-guide.md)

## 1. 기준 checkout

2026-10-22 문서 작성 시작 시 확인한 revision이다. 이 문서 자체는 이후 추가되는 변경이므로
root SHA가 문서까지 포함한다는 의미는 아니다. Native manifest는 source/runtime 경로와
build target을 기록하며 build source revision을 저장하지 않는다. 실행별 `launch.json`의
`gem5_revision`도 실행 시 checkout HEAD다. Binary hash와 실행 입력을 함께 확인하고,
실제 build revision의 증명에는 별도 build provenance를 보존해야 한다.

| Repository | HEAD |
|---|---|
| workspace root | `7d8b891a2f0d0e14c3c80dde8a93ffc40e855548` |
| `hsoc-stack/tools/gem5` | `68f6b04eb14427a733b0cbf17ff03f8b7df67e03` |
| `hsoc-stack/yocto/meta-hsoc-auto-solutions` | `7a5ab6579a35efcea83c762eedf9304e356a9876` |
| `hsoc-stack/yocto/meta-hsoc-bsp` | `e22957deeb9431b6a8fe9bbfead98dd94b5263b7` |

Source commit만으로 현재 deploy binary가 그 revision에서 다시 build됐다고 단정하지 않는다.
v4 실행은 commit 이전 working tree에서 수행됐다. 이후 commit의 내용과 실제 snapshot
compatibility에 쓰이는 file hash를 구분해야 한다.

## 2. Evidence 수준

| 수준 | 확인할 수 있는 것 | 확인하지 못하는 것 |
|---|---|---|
| Source/static | binding, parameter, 주소·IRQ, task dependency, parser 조건 | 실제 boot와 traffic |
| Host regression | CLI 거부 조건, summary validation, fake simulator 기반 tmux/F12 | AArch64 instruction·cache timing |
| Yocto build | 선택한 metadata의 compile/package/rootfs 성공 | Linux boot 및 device 동작 |
| Directed gem5 | 특정 checkpoint/register/RAM/readfile/O3 경로 | 모든 Linux device의 snapshot |
| AP Linux runtime | 해당 image의 boot, checkpoint restore, workload 및 ROI | RSE/SCP/SI full-system, FVP parity |
| Silicon comparison | 현재 제공하지 않음 | physical latency, bandwidth, power qualification |

`PASS`, `FAIL`, `SKIP`, `UNVERIFIED`, `UNSUPPORTED`를 서로 바꾸어 사용하지 않는다.
예를 들어 O3 checkpoint는 느려서 시험하지 않은 항목이 아니라 현재 지원 범위에서
거부하는 항목이다. 16-CPU 설정 가능성과 4-CPU v4 benchmark PASS도 별개의 주장이다.

## 3. 보존된 v4 runtime 증거

기본 위치는 `build/qbox-apollo-qvp/gem5/`이며 Git에 snapshot이나 대형 log를 넣지 않는다.
다른 checkout에서는 generated evidence 파일이 없을 수 있다.

| Evidence | 내용 |
|---|---|
| `benchmarks-v4-verification.json` | image, snapshot file hash, save result, tool measurements |
| `benchmarks-v4-image-build.log` | 4167 tasks 완료, 4137 재사용; 기존 kernel forced-task 경고 2개 |
| `benchmarks-v4-image-inspection.json` | initramfs 내 AArch64 binary 및 hash |
| `benchmarks-v4-checkpoint-save/` | fresh boot, timing, checkpoint save 결과 |
| `linux-benchmarks-v4-snapshot/` | simulator state, RAM, cache archive, metadata/launcher contract |
| `benchmarks-v4-lmbench/` | modified lmbench 측정 |
| `benchmarks-v4-tinymembench/` | runtime option으로 축소한 측정 |
| `benchmarks-v4-stream/` | cache-sized STREAM 측정과 numerical validation |

최종 image는 `nexios-gem5-initramfs-apollo-qvp-20261022031446.cpio.gz`이며
compressed size는 **8,367,466 bytes**, SHA256은 다음과 같다.

```text
2e29bebd1186c7788917c211159e5b93899abc02e314d58be512e77d7f5872d8
```

저장 당시 host 시간의 예다. 속도 보장이나 timeout 계산 공식으로 사용하지 않는다.

| Event | 시작 후 host elapsed |
|---|---:|
| first UART byte | 26.18s |
| `Booting Linux on physical CPU` | 178.58s |
| `NEXIOS_GEM5_INITRAMFS_READY` | 1664.00s |
| checkpoint save 완료 | 1682.36s |

Benchmark의 host elapsed는 lmbench 844.50s, tinymembench 1567.75s, STREAM 484.55s였다.
동시에 실행된 세 simulation의 host 시간이며 guest의 ROI 시간은 각각 46.222ms,
48.972ms, 8.357ms다. 이 값들을 혼용하지 않는다.

## 4. 초기 문서 작성에서 확인한 것

초기 문서 작성에서는 새 build나 장시간 boot 대신 source와 보존 artifact를 read-only로 확인했다.
후속 build와 interleave / 16-core 실행은 [별도 시험 보고서](interleave-16core-results.md)를 따른다.

- `run_gem5_linux.sh --help`로 문서의 public option을 대조했다.
- 세 v4 directory를 현재 `summarize_tools.py`로 재분석해 모두 PASS를 확인했다.
- v4 snapshot의 `launcher.json`에 기록된 gem5/kernel/firmware/profile hash,
  압축 해제한 initramfs hash, configuration Python file hash가 현재 파일과 일치함을 확인했다.
  이것은 새 restore 실행의 대체 증거가 아니라 compatibility 입력의 정적 대조다.
- Markdown의 로컬 파일 링크, native draw.io XML, SVG export 및 화면 배치를 확인했다.
  최종 검사 결과는 본 문서 끝의 문서 검증 기록에 남긴다.

## 5. 관련 regression 실행

아래 명령은 workspace root에서 실행한다. Python test가 일부 host compiler나 tmux를
필요로 할 수 있으며, skip 여부를 확인한다. lmbench/tinymembench option test는 현재
Yocto work source를 fixture로 사용할 수 있으므로 clean clone에서 해당 source가 준비되지
않으면 동일한 결과가 보장되지 않는다.

```sh
python3 -m unittest discover -s scripts/gem5 -p 'test_*.py'
python3 -m pytest -q tests/test_gem5_initramfs_init.py \
  tests/test_yocto_build_gem5.py tests/test_lmbench_options.py \
  tests/test_tinymembench_options.py
python3 hsoc-stack/tools/gem5/tests/zena_cmn/test_checkpoint.py
```

직전 commit 검증에서 각각 23개, 49개, 4개가 통과했다. 이 결과를 문서 변경 시 새로
simulation을 실행한 결과로 표시하지 않는다. `m5`에 의존하는 다른 gem5 test는 host
Python으로 무차별 discover하지 않고 해당 test의 gem5 runner를 사용한다.

## 6. 변경별 확인 범위

| 변경 | 먼저 확인 | 필요한 runtime 증거 |
|---|---|---|
| 설명·도면만 변경 | source link, 숫자, XML/render, 명령 구문 | 동작 주장을 바꾸지 않으면 재부팅 불필요 |
| launcher/parser | `test_run_linux`, tmux/cleanup, dry-run inputs | headless·tmux의 영향받는 경로 |
| guest control / init | host test, target build, initramfs binary/hash | fresh boot, checkpoint, restore, ROI |
| benchmark option | parser test, recipe patch, image package | 새 조건의 전체 출력과 marker/stats |
| CPU/cache/mesh/profile | parameter validation, effective config | 해당 traffic, ROI, 새 snapshot |
| address/IRQ/firmware | DTB와 firmware contract, directed test | Linux driver/UART/SMP evidence |
| native recipe/toolchain | build manifest와 dependency, binary ABI | matching runtime과 snapshot 재생성 여부 |

Source revision·guest artifact·snapshot을 묶어 보존한다. deployed alias가 다른 image를
가리키게 되면 기존 snapshot은 hash mismatch로 거부될 수 있다. hash 검사를 약화하는
방식으로 우회하지 말고 matching artifacts를 명시하거나 새 snapshot을 생성한다.

## 7. Source 근거 찾기

| 질문 | 기준 source |
|---|---|
| launcher의 input/CLI/compatibility | [run_linux.py](../../scripts/gem5/run_linux.py) |
| model 객체와 boot image 배치 | [run_fs.py](../../hsoc-stack/tools/gem5/configs/zena_cmn/run_fs.py) |
| parameter merge와 validation | [parameters.py](../../hsoc-stack/tools/gem5/configs/zena_cmn/parameters.py) |
| CPU switch / statistics | [roi_control.py](../../hsoc-stack/tools/gem5/configs/zena_cmn/roi_control.py) |
| checkpoint 완료 표시와 제한 | [checkpoint.py](../../hsoc-stack/tools/gem5/configs/zena_cmn/checkpoint.py) |
| guest marker와 command exit | [control.c](../../scripts/gem5/control.c) |
| tool 결과 허용 조건 | [summarize_tools.py](../../scripts/gem5/summarize_tools.py) |

draw.io export는 [공식 XML reference](https://raw.githubusercontent.com/jgraph/drawio-mcp/main/shared/xml-reference.md)의
native cell/connector 형식을 사용한다. Apollo 동작 근거는 외부 diagram 형식 문서가 아니라
위 프로젝트 source와 실제 runtime evidence다.

## 문서 검증 기록

2026-10-22 최초 문서 작업의 검사 결과다. 이후 interleave 구현과 runtime 검증은
[Interleave 시험 보고서](interleave-16core-results.md)에 별도로 기록한다.

| 검사 | 결과 |
|---|---|
| Markdown 8개, local file link 162개 | PASS, 모든 link target 존재 |
| Shell example 23개 | PASS, `bash -n` 구문 검사; build/run 예제를 실제 실행한 것은 아님 |
| Native draw.io 5개 | PASS, XML parse, unique cell ID, edge endpoint/geometry |
| SVG 5개 | PASS, CLI export, embedded diagram과 native source cell 내용 일치 |
| Render preview 5개 | PASS, 한글 표시·라벨·연결선 배치 육안 확인 |
| Source review | CLI/recipe/checkpoint/ROI/tmux 설명 대조; repeats 적용 범위와 build provenance 표현 수정 |
| 보존된 benchmark 재분석 | lmbench / tinymembench / STREAM 모두 PASS |

도면의 편집 기준은 `.drawio`다. 변경 후 SVG도 함께 갱신한다. Headless Linux에서
draw.io Desktop과 Xvfb가 설치되어 있으면 다음과 같이 export할 수 있다.

```sh
for source in doc/gem5/diagrams/*.drawio; do
  xvfb-run -a drawio -x -f svg -e -b 20 -o "$source.svg" "$source"
done
```

최초 문서 작업에서는 simulator/recipe code를 바꾸거나 image·snapshot을 재생성하지 않았다.
후속 interleave 작업에서 새 image와 세 snapshot을 생성하고 16-CPU Linux restore 및
multicore ROI를 검증했다. Physical calibration과 장시간 원본 benchmark 조건은
이번 interleave 시험의 검증 범위에 포함되지 않는다.
