# Source, binary, runtime artifact 구조

Apollo gem5 구성은 root tooling, gem5 submodule, owned Yocto metadata의 세 경계에
걸쳐 있다. 이 문서는 파일을 수정하거나 실행 결과를 전달할 때 어떤 repository와
artifact를 함께 확인해야 하는지 설명한다. 경로는 workspace root 기준이다.

## 1. Repository와 source 소유권

| 경계 | 주요 경로 | 책임 |
|---|---|---|
| Root repository | `run_gem5_linux.sh`, `yocto_build.sh`, `scripts/gem5/`, `tests/`, `doc/gem5/` | build/run entrypoint, guest workload source, host 결과 수집, 문서 |
| gem5 submodule | `hsoc-stack/tools/gem5/` | ARM simulator, ZenaCSS platform, CPU/cache/Ruby/DRAM configuration, PSCI firmware |
| Product metadata | `hsoc-stack/yocto/meta-hsoc-auto-solutions/` | native/target build, 전용 image/init, benchmark package 확장 |
| BSP metadata | `hsoc-stack/yocto/meta-hsoc-bsp/` | source-root 정의, Linux와 Apollo machine integration |
| Linux source | `hsoc-stack/components/primary_compute/linux/` | 동일 Apollo kernel source, gem5에서 쓰는 `Image`의 소유 repository |
| External layers | `layers/`, `arm-zena-css/`, `sw-ref-stack/` | 기존 recipe/class/reference 제공; gem5 package 변경은 owned layer에서 확장 |

gem5는 [.gitmodules](../../.gitmodules)에서 `git@github.com:cometzero/gem5.git`을
가리키며 확인 시점 branch는 `apollo-qvp`, HEAD는 `68f6b04eb144`다. Upstream remote는
`https://github.com/gem5/gem5.git`이다. `/srv/oss_contrib/gem5`는 초기 참고 source이고
현재 recipe/launcher의 active source는 workspace submodule이다. Root gitlink와
submodule worktree revision이 일치하는지 별도로 확인한다.

```sh
git submodule status hsoc-stack/tools/gem5 \
  hsoc-stack/yocto/meta-hsoc-auto-solutions hsoc-stack/yocto/meta-hsoc-bsp
git -C hsoc-stack/tools/gem5 status --short --branch
git -C hsoc-stack/tools/gem5 remote -v
```

## 2. Root tooling

| 파일 | 역할 / consumer |
|---|---|
| [`run_gem5_linux.sh`](../../run_gem5_linux.sh) | `${PYTHON:-python3}`로 `scripts/gem5/run_linux.py`를 exec |
| [`scripts/gem5/run_linux.py`](../../scripts/gem5/run_linux.py) | input resolution, initrd preparation, checkpoint contract, tmux 연결, child process/UART, run 판정 |
| [`scripts/run/run_qbox_linux.py`](../../scripts/run/run_qbox_linux.py) | `start_tmux()`를 공유. gem5는 `console_command`를 전달하고 자체 runner에서 child를 관리 |
| [`scripts/gem5/benchmark.c`](../../scripts/gem5/benchmark.c) | `apollo-bench` source. cache pointer chase / DRAM streaming 및 checksum, m5 ROI marker |
| [`scripts/gem5/control.c`](../../scripts/gem5/control.c) | `gem5-control` source. checkpoint/readfile/m5 marker, CPU0 affinity를 가진 whole-command wrapper |
| [`scripts/gem5/benchmark.py`](../../scripts/gem5/benchmark.py) | 내장 `apollo-bench` 및 multicore 결과와 ROI/statistics 검증 |
| [`scripts/gem5/summarize_tools.py`](../../scripts/gem5/summarize_tools.py) | lmbench/tinymembench/STREAM guest 출력, O3/ROI, tool별 timing/수치 검증 |
| [`yocto_build.sh`](../../yocto_build.sh) | template/machine/build-dir 선택과 `--gem5` target dispatch |

Root regression은 `scripts/gem5/test_*.py`,
[`tests/test_gem5_initramfs_init.py`](../../tests/test_gem5_initramfs_init.py),
[`tests/test_yocto_build_gem5.py`](../../tests/test_yocto_build_gem5.py),
[`tests/test_lmbench_options.py`](../../tests/test_lmbench_options.py),
[`tests/test_tinymembench_options.py`](../../tests/test_tinymembench_options.py)에 있다.
Test 실행과 evidence 범위는 [validation](validation.md)에서 다룬다.

## 3. gem5 source에서 읽을 순서

| 경로 (`hsoc-stack/tools/gem5/` 아래) | 읽을 때 확인할 계약 |
|---|---|
| [`src/dev/arm/ZenaCSS.py`](../../hsoc-stack/tools/gem5/src/dev/arm/ZenaCSS.py) | platform의 GIC/UART/timer/RTC, MPIDR affinity, 기본 DT 생성 |
| [`src/arch/arm/zena_fs_workload.cc`](../../hsoc-stack/tools/gem5/src/arch/arm/zena_fs_workload.cc) | Zena ARM full-system workload 구현; source capability와 active run 구성 구분 |
| [`src/mem/ruby/protocol/chi/`](../../hsoc-stack/tools/gem5/src/mem/ruby/protocol/chi/), [`src/mem/ruby/network/garnet/`](../../hsoc-stack/tools/gem5/src/mem/ruby/network/garnet/) | compiled CHI protocol state machine과 packet/flit network 구현 |
| [`configs/zena_cmn/run_fs.py`](../../hsoc-stack/tools/gem5/configs/zena_cmn/run_fs.py) | full-system object 생성, Atomic/O3 CPU 쌍, terminal/disk/readfile, event loop |
| [`configs/zena_cmn/profiles/a720ae_documented.yaml`](../../hsoc-stack/tools/gem5/configs/zena_cmn/profiles/a720ae_documented.yaml) | launcher 기본 profile. CPU/cache/fabric/memory 정책 |
| [`configs/zena_cmn/parameters.py`](../../hsoc-stack/tools/gem5/configs/zena_cmn/parameters.py) | profile merge, default와 validation, CLI override |
| [`configs/zena_cmn/cpu_profile.py`](../../hsoc-stack/tools/gem5/configs/zena_cmn/cpu_profile.py), [`a720ae_fu.py`](../../hsoc-stack/tools/gem5/configs/zena_cmn/a720ae_fu.py) | CPU parameter와 functional unit proxy |
| [`configs/zena_cmn/ruby_system_builder.py`](../../hsoc-stack/tools/gem5/configs/zena_cmn/ruby_system_builder.py), [`chi_topology.py`](../../hsoc-stack/tools/gem5/configs/zena_cmn/chi_topology.py), [`cluster_rnf.py`](../../hsoc-stack/tools/gem5/configs/zena_cmn/cluster_rnf.py) | Ruby cache/controller/network 연결 |
| [`configs/zena_cmn/memory_backend.py`](../../hsoc-stack/tools/gem5/configs/zena_cmn/memory_backend.py), [`lpddr5x_documented.py`](../../hsoc-stack/tools/gem5/configs/zena_cmn/lpddr5x_documented.py) | memory backend 생성, channel mapping과 part provenance |
| [`configs/zena_cmn/address_map.py`](../../hsoc-stack/tools/gem5/configs/zena_cmn/address_map.py), [`device_tree.py`](../../hsoc-stack/tools/gem5/configs/zena_cmn/device_tree.py) | address/DT/cache topology 계약 |
| [`configs/zena_cmn/kernel_image.py`](../../hsoc-stack/tools/gem5/configs/zena_cmn/kernel_image.py) | raw arm64 Image 검증과 ELF wrapping |
| [`configs/zena_cmn/roi_control.py`](../../hsoc-stack/tools/gem5/configs/zena_cmn/roi_control.py) | switch/warm-up/ROI state machine, statistics reset/dump |
| [`configs/zena_cmn/checkpoint.py`](../../hsoc-stack/tools/gem5/configs/zena_cmn/checkpoint.py) | diskless Atomic checkpoint 정책과 COMPLETE metadata |
| [`system/arm/bootloader/zena_css/`](../../hsoc-stack/tools/gem5/system/arm/bootloader/zena_css/) | `boot.S`, `monitor.c`, `link.ld`, Makefile: 4/16 CPU PSCI firmware |
| [`workloads/zena_cmn/`](../../hsoc-stack/tools/gem5/workloads/zena_cmn/) | 공통 marker header, 별도 SE/directed workload source |
| [`tests/zena_cmn/`](../../hsoc-stack/tools/gem5/tests/zena_cmn/) | model policy, address/cache/ROI 검사 및 directed traffic 시험 |

Profile directory에 NPU/diagnostic/calibration 후보가 존재해도 기본 launcher에서
실제로 활성화되는지는 `resolved-profile.json`을 기준으로 판정한다. 별도 workload의
SE 결과를 Linux full-system 실행 결과로 취급하지 않는다.

## 4. Build output과 deploy layout

```text
build/
├── conf/                         local build inputs; generated resource conf 포함
├── tmp_baremetal/
│   ├── work/
│   │   ├── x86_64-linux/gem5-native/26.0.0.0/
│   │   │   ├── build/ARM/gem5.opt
│   │   │   ├── recipe-sysroot-native/
│   │   │   └── temp/log.do_*, run.do_*
│   │   └── <target>/<recipe>/<version>/
│   │       ├── build/             guest/package build output
│   │       └── temp/              BitBake task evidence
│   └── deploy/
│       ├── gem5-native/
│       │   ├── gem5.opt           host executable
│       │   └── gem5-native.json   native library/Python/source paths
│       └── images/apollo-qvp/
│           ├── Image             matching kernel symlink
│           ├── nexios-gem5-initramfs-apollo-qvp.cpio.gz
│           ├── nexios-gem5-initramfs-apollo-qvp.manifest
│           ├── ...testdata.json, ...spdx.json
│           └── gem5/
│               ├── zena_css4.elf, zena_css16.elf
│               ├── apollo-bench, apollo-memory-bench, gem5-control
│               └── stream-gem5-cache
└── qbox-apollo-qvp/gem5/         run directories와 checkpoints
```

Native manifest는 build-tree의 `recipe-sysroot-native/usr`를 `PYTHONHOME`으로,
그 아래 library directory를 `LD_LIBRARY_PATH`로 사용하도록 명시한다. `gem5.opt`만
다른 host로 복사하는 방식은 portable deployment가 아니다. 동일 binary라도 sysroot
삭제·이동 뒤에는 실행 실패할 수 있다.

Deploy guest binary와 initramfs에 package된 binary의 크기/hash는 동일하지 않을 수
있다. Yocto packaging의 strip/debug 분리가 적용되기 때문이다. 배포 binary hash를
이미지 내부 binary hash 대신 사용하지 않는다. Custom `--benchmark`를 전달하면
launcher가 해당 deploy/외부 binary를 새 CPIO overlay에 넣는다.

`Image`는 raw AArch64 image이며 launcher가 실행한 `run_fs.py`가 run directory의
`kernel-image.elf`로 wrapping한다. 이것은 재compile이나 kernel debug symbol 생성이
아니다. Source debug에는 일치하는 unstripped `vmlinux`가 별도로 필요하다.

## 5. Initramfs filesystem과 진입점

| Guest 경로 | Source / 생성 주체 | 사용 시점 |
|---|---|---|
| `/init` | [`nexios-gem5-init/init`](../../hsoc-stack/yocto/meta-hsoc-auto-solutions/recipes-core/initrdscripts/nexios-gem5-init/init) | PID 1, proc/sys/dev/devpts/run mount, READY, checkpoint/readfile, shell |
| `/usr/bin/gem5-workload` | [`nexios-gem5-init/gem5-workload`](../../hsoc-stack/yocto/meta-hsoc-auto-solutions/recipes-core/initrdscripts/nexios-gem5-init/gem5-workload) | `/run/gem5-workload.sh`, 없으면 `/etc/gem5-workload.sh` 실행 |
| `/usr/bin/gem5-control` | guest recipe | m5 pseudo-op와 command ROI wrapper |
| `/usr/bin/apollo-bench` | guest recipe | `--workload cache/dram`의 내장 workload |
| `/usr/bin/apollo-memory-bench` | guest recipe | `--workload dram-multicore`; gem5 `workloads/zena_cmn/memory_bench.c` |
| `/usr/bin/lat_mem_rd`, `/usr/bin/bw_mem` | lmbench package | external benchmark |
| `/usr/bin/tinymembench` | tinymembench package | external benchmark |
| `/usr/bin/stream` | update-alternatives, STREAM priority 100 | 공식 STREAM 기본조건 binary 선택 |
| `/usr/bin/stream.lmbench` | lmbench package | 이름이 같은 lmbench 구현 보존 |
| `/usr/bin/stream-gem5-cache` | reduced STREAM recipe | 1.5MiB 총 배열의 cache-oriented 측정 |
| `/run/gem5-workload.sh` | 매 실행 host readfile에서 복사 | snapshot을 바꾸지 않고 새 명령 전달 |

Dedicated initramfs는 RAM rootfs다. `--rootfs`를 지정해 virtio block을 연결해도
`/init`가 자동으로 그 disk에 `switch_root`하지 않는다.

## 6. Run directory의 artifact 계약

Launcher의 기본 output은 `build/qbox-apollo-qvp/gem5/YYYYmmdd-HHMMSS/`다.
`--out-dir`도 **존재하지 않는 새 경로**여야 하며 이전 결과를 덮어쓰지 않는다.

| Artifact | 생산자 / 의미 |
|---|---|
| `launch.json` | root launcher의 실제 input paths, child command, hash, gem5 revision/dirty 상태 |
| `initrd.cpio` | 원본 gzip을 해제한 실행용 newc CPIO; 필요한 경우 overlay 연결 |
| `guest-init.sh` | host readfile 원본; boot-only이면 빈 파일 |
| `gem5.log` | gem5 child stdout/stderr, warning/event/platform log |
| `uart.log` | launcher가 TCP로 수신한 guest UART stream |
| `boot-timings.json` | simulator 시작 이후 host 경과시간으로 관측한 UART milestone |
| `result.json` | launcher 판정, return code, timeout, host seconds; cache/dram은 measurement 포함 |
| `m5out/manifest.json` | model의 boot CPU/memory mode, source hash, memory provenance, asset hash |
| `m5out/resolved-profile.json` | default/override가 합쳐진 실제 model parameter |
| `m5out/config.ini`, `config.json` | instantiate한 SimObject와 port/parameter 구성 |
| `m5out/system.dtb` | ZenaCSS platform에서 생성하고 cache topology를 추가한 실행용 DTB |
| `m5out/stats.txt` | gem5 statistics dump; ROI dump와 종료 dump를 구분해야 함 |
| `m5out/roi-events.json` | switch/warmup, ROI begin/end tick; boot-only이면 없을 수 있음 |
| `m5out/exit.json` | model event loop의 종료 상태/cause/phase/tick |
| `m5out/system.platform.terminal` | gem5 terminal file; TCP 접속 전 출력도 보존하므로 UART의 원본 보완 자료 |
| `m5out/kernel-image.elf` | raw Image 입력을 쓸 때 생성하는 ELF wrapper |

`result.json`의 `PASS`는 workload별 검사 통과이며 `BOOT_OBSERVED`는 shell/login
문자열 관측이다. F12/외부 signal로 launcher를 중단하면 정상 후처리 전에 끝나
`result.json`이 없을 수 있다. 로그 존재만으로 완료를 추정하지 않는다.

Machine deploy directory의 `.fvpconf` 또는 QBox용 DTB는 gem5 launcher의 실행
입력이 아니다. gem5는 자신의 platform/profile과 CPU 수에 맞춰 `system.dtb`를
생성한다. 같은 kernel `Image`를 사용한다는 사실이 FVP/QBox와 동일한 device
tree 또는 전체 boot chain을 사용한다는 뜻은 아니다.

## 7. Checkpoint directory와 입력 호환성

| Snapshot 파일 | 의미 |
|---|---|
| `m5.cpt` | CPU/device/simulation state |
| `system.physmem.store0.pmem` | guest RAM backing store |
| `system.ruby.cache.gz` | Ruby checkpoint serialization output |
| `apollo-checkpoint.json` | model policy, saved tick, boot contract, `COMPLETE` marker |
| `launcher.json` | launcher-side hash/CPU/channel/bootargs contract |

일반 run의 `launch.json`과 snapshot의 `launcher.json`은 이름과 역할이 다르다.
Snapshot은 guest RAM을 포함하므로 image와 독립적인 package 저장소가 아니다.
원본 image, simulator, profile, Python config 또는 CPU/channel/bootargs가 바뀌면
동일 snapshot을 계속 사용하는 대신 새로 저장한다. 자세한 절차는
[run guide의 checkpoint 항목](run-guide.md#5-checkpoint-저장과-resume)을 참고한다.

## 8. 현재 보존된 artifact

아래는 2026-10-22에 실제 파일을 확인한 기록이다. 생성물은 Git source tree의
배포 문서와 달리 해당 build workspace가 있어야 접근할 수 있다.

| Artifact | 확인값 |
|---|---|
| native `gem5.opt` | 1,075,604,112 bytes, 2026-10-22 10:28 KST |
| 최종 initramfs | `nexios-gem5-initramfs-apollo-qvp-20261022031446.cpio.gz`, 8,367,466 bytes, 12:15 KST |
| image SHA256 | `2e29bebd1186c7788917c211159e5b93899abc02e314d58be512e77d7f5872d8` |
| kernel symlink target | `Image--6.18.5+git0+d8bded2984-r0-apollo-qvp-20261012033515.bin` |
| 최종 benchmark snapshot | `build/qbox-apollo-qvp/gem5/linux-benchmarks-v4-snapshot/` |
| 통합 검증 기록 | `build/qbox-apollo-qvp/gem5/benchmarks-v4-verification.json` |
| 세 run directory | 같은 evidence root의 `benchmarks-v4-lmbench`, `benchmarks-v4-tinymembench`, `benchmarks-v4-stream` |

수치 해석과 알려진 한계는 [benchmark guide](benchmark-guide.md), runtime evidence
등급은 [validation](validation.md)에서 다룬다. Build artifact는 commit하지 않고,
재현에 필요한 recipe/source와 실행 조건 및 검증 문서를 version control한다.
