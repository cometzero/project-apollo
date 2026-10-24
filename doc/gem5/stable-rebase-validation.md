# gem5 v26 stable rebase 및 검증

기준일: 2026-10-24. Apollo AP domain의 기존 변경을 upstream stable
`fed0e07e930fecf1e73dce94dd44e69a5bf70c46` (v26.0.0.0) 위로 rebase했다.
실제 upstream fetch로 stable ref를 확인했다. `/srv/oss_contrib/gem5`는
호환성 수정의 reference로만 사용했으며 해당 checkout은 변경하지 않았다.

## Source 이력과 호환성

- 이전 Apollo HEAD: `b28c542efabb7ac608fad531e6eac5cc30d35cdc`.
- 보존 branch: `backup/apollo-qvp-before-v26-20261024`.
- 기존 Apollo commit 24개를 replay하고 v26 호환성 commit 4개를 추가했다.
- 현재 native HEAD: `ae2612dbc25f`. Profile의 `model.gem5_tag`도
  `v26.0.0.0`으로 변경했다.
- CHI DMA coherence 충돌은 reference의 v26 port와 대조했다.
  기존 custom stale-evict 처리는 upstream `Send_CompI`의 `is_stale` 및
  CBusy 처리로 대체되어 중복 삽입하지 않았다.
- SME feature-disable guard는 v26의 확장된 SME/SME2 register 처리 앞에 유지했다.
- CHI node의 `NoC_Params`, router/link latency, buffer 설정을 v26 API로 변경했다.
- NC completion의 CBusy callback, SCons optional-library probe의 `bool()`
  변환, verifier의 zero-padded CPU ID 처리를 반영했다.
- Root multicore collector는 `roi_cpu0`과 `roi_cpu00` 이름을 모두 처리한다.
  같은 CPU ID에 두 counter가 존재하거나 pinned worker의 instruction counter가
  없으면 실패한다. 기존 ROI tick·checksum·channel traffic 검증은 유지한다.

Reference의 Safety Island 및 power 관련 확장은 가져오지 않았다.
Rebase로 Git 이력이 변경되었으며 remote push는 수행하지 않았다.

## Yocto 변경

`hsoc-stack/yocto/meta-hsoc-auto-solutions/recipes-devtools/gem5/gem5-native.bb`:

- `PV = "26.0.0.0"`으로 native work/build 경로를 구분한다.
- upstream libfdt README의 source provenance URL 변경에 맞춰 checksum을
  `efc456d6a0e4e5a8345c8a0753c5d38f`로 갱신했다. License 조건 변경은 없다.
- `externalsrc`, ARM ISA + Ruby CHI, native Python 환경 manifest를 유지한다.
- KVM/SystemC/Capstone은 기존처럼 비활성화한다.

사용한 build configuration은 `MACHINE=apollo-qvp`,
`DISTRO=auto-ad-nexios`, `TMPDIR=build/tmp_baremetal`이다.
`--keep-conf`로 기존 configuration을 유지하며 BitBake를 직렬 실행한다.

```sh
APOLLO_BUILD_THREADS=2 APOLLO_PARALLEL_MAKE=-j4 \
  ./yocto_build.sh --keep-conf gem5-native
APOLLO_BUILD_THREADS=2 APOLLO_PARALLEL_MAKE=-j4 \
  ./yocto_build.sh --gem5 --keep-conf
```

## 검증 결과

아래 결과는 이번 checkout과 Yocto deploy artifact로 실행했다. 실제 로그는 evidence directory에 보존한다.

- Root host regression: 26 tests PASS.
- Native parameter host tests: 17 tests PASS.
- Verifier host tests: 3 PASS, 실제 run config/DTB를 요구하는 18개 SKIP.
- Native source의 추가 host suite: 123 tests 중 97 PASS, 19 SKIP,
  3 FAIL, 4 ERROR. 실패는 `run_smoke.py`가 checkout 밖의 `test_zena_css`를
  import하는 기존 의존성에서 발생했다. 해당 파일은 rebase 전과 동일하며
  Apollo의 `scripts/gem5/run_linux.py`와 다른 runner다. 전체 suite PASS로
  해석하지 않는다. 상세: `host-native-tests.log`.
- Native build: **PASS**, 815 tasks 전체 성공 (`build-native.log`).
- Initramfs image build: **PASS**, 4,167 tasks 전체 성공 (`build-image.log`).
  기존 kernel의 forced configure/compile taint 경고 2개는 유지된다.
- 실제 native AddrRange/CPU 설정: **10 tests PASS** (`test_address_map.log`).
- v26 Garnet/Simple NoC 기본/변경 설정: **4 tests PASS** (`test_v26_topology.log`).
- CHI NC DMA parallel: **PASS**, 451 operations, 8 cases, negative control 및
  drain 완료 (`chi-dma/nc-dma-result.json`). 이는 모델 traffic 검증이다.
- Fresh boot의 실제 config/DTB 검증: **PASS**
  (`boot-ap4/m5out/config-verification.json`).
- Fresh Linux boot 및 checkpoint 저장: **PASS**, host 1,293.23초
  (약 21분 33초), tick `589499179500`. CPU 4개, DRAM 2GiB/16 channels,
  channel interleave 64 B, `AtomicSimpleCPU` boot이다.
  UART의 `Run /init as init process`, `NEXIOS_GEM5_INITRAMFS_READY` 및
  `CHECKPOINT_SAVED` 결과를 확인했다.
- Snapshot resume → O3 cache ROI: **PASS**, host 34.34초.
  32KiB/1 pass, 512 dependent loads, checksum=expected=1.
  ROI `[595479935000, 595481280500]`, 1,345,500 ticks를 정확히 선택했다.
  이 짧은 workload는 동작 확인용이며 성능 campaign의 대체가 아니다.
- Boot 중 진행 확인용 SIGUSR1 통계 dump 2개를 남겼다.
  Resume은 별도 output directory이며 해당 dump를 ROI로 사용하지 않는다.

Evidence root:
`build/qbox-apollo-qvp/gem5/stable-rebase-20261024/`.
`rebase-inputs.json`은 입력 SHA, `range-diff.txt`는 replay 및 호환성 변경,
`build-native.log`는 Yocto build 기록이다.

## 부팅 및 복원 재현

아래는 이번 실행 명령이다. Checkpoint와 output directory는 새 경로여야 한다.
기존 checkpoint를 이용하려면 두 번째 명령을 새 `--out-dir`로 실행한다.

```sh
./run_gem5_linux.sh --headless --cpus 4 --channels 16 \
  --checkpoint build/qbox-apollo-qvp/gem5/stable-rebase-20261024/checkpoint-ap4 \
  --out-dir build/qbox-apollo-qvp/gem5/stable-rebase-20261024/boot-ap4 \
  --timeout 86400
./run_gem5_linux.sh --headless --cpus 4 --channels 16 \
  --resume build/qbox-apollo-qvp/gem5/stable-rebase-20261024/checkpoint-ap4 \
  --workload cache --size-kib 32 --passes 1 \
  --out-dir build/qbox-apollo-qvp/gem5/stable-rebase-20261024/resume-cache-ap4 \
  --timeout 3600
```

- UART 원본: `boot-ap4/m5out/system.platform.terminal`.
- Platform log: `boot-ap4/gem5.log`.
- 입력 경로/hash 및 실행 command: 각 run의 `launch.json`.
- Fresh boot 판정: `boot-ap4/result.json`.
- Resume 판정 및 ROI: `resume-cache-ap4/result.json` 및 `m5out/roi-events.json`.
- Kernel: `Image--6.18.5+git0+d8bded2984-r0-apollo-qvp-20261023042028.bin`.
- Image: `nexios-gem5-initramfs-apollo-qvp-20261024053331.cpio.gz`.

## Snapshot 및 성능 해석

이전 v25 snapshot의 compatibility 검사를 우회하지 않는다. 새 native binary와
initramfs로 fresh boot한 snapshot을 사용해야 한다. 이전 Orin 비교와 interleave
보고서는 당시 binary의 고정 결과이며 v26의 동일 성능을 입증하지 않는다.
본 검증은 모델의 build/boot/ROI 실행 검증이며 silicon 성능 qualification이 아니다.
