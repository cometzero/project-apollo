# Apollo AP 전용 gem5

현재 구성의 상세 기술 문서는 [Apollo gem5 문서 모음](gem5/README.md)을 참고한다. 이 문서는 초기 통합과 검증 기록을 보존한다.

최신 이미지·snapshot 재생성과 도구별 O3 측정은
[벤치마크 실행 결과](apollo-gem5-benchmark-results.md)에 기록한다.
아래 검증 이력의 이미지 크기와 snapshot 경로는 각 실행 당시의 값이다.

## 범위와 모델

`run_gem5_linux.sh`는 Apollo Yocto `Image`와 전용
`nexios-gem5-initramfs`를 사용한다. 기본 부팅에는 WIC가 필요 없다. AP CPU, 캐시, interconnect, DRAM, GICv3,
PL011, RTC, architected timer, virtio block/RNG를 실행한다. RSE/SCP/Safety Island와
기존 TF-A boot chain은 실행하지 않는다. gem5의 작은 PSCI firmware와
구현된 장치만 기술하는 DTB를 사용한다. QBox DTB를 그대로 사용하지 않는다.

소스는 `hsoc-stack/tools/gem5`, 원격은 `cometzero/gem5`, 브랜치는
`apollo-qvp`이다. `/srv/oss_contrib/gem5`의 `zena-css-ap`
(`4a09b8d5b714`) 소스를 기준으로
가져왔으며 실행 시 그 외부 경로에 의존하지 않는다.

| 부분 | 현재 구성 | 해석 한계 |
| --- | --- | --- |
| CPU | atomic boot → workload 진입 시 2 GHz ArmO3CPU; A720AE documented profile | Cortex-A720AE RTL 또는 cycle-accurate 모델 아님 |
| L1/L2 | 코어별 L1I/L1D 64 KiB, L2 512 KiB | profile의 latency/queue/prefetch 가정 |
| DSU | 4코어 cluster당 4 MiB L3 | DSU-120AE 캐시/일관성 프록시 |
| CMN | Ruby CHI/Garnet, 6×4 mesh, 8 HNF/총 4 MiB SLC | CMN-S3AE protocol/timing의 근사 모델 |
| DRAM | LPDDR5X 8533, 기본 16×16-bit 채널, 총 2 GiB | LPDDR5 기반 geometry/timing 가정, 실물 보정 안 됨 |
| 실행 규모 | 4/16 CPU, 4/8/16 DRAM 채널 | 채널 수 변경 시 총 메모리 용량 유지 |

런처의 CPU 수는 내장 PSCI firmware가 지원하는 4/16으로 제한한다.
현재 Linux와 성능 runtime 검증은 4코어 구성이다.

실제 사용 값은 각 실행의 `m5out/resolved-profile.json`, `config.ini`로 확인한다.
일반 부팅은 atomic_noncaching이므로 그 통계로 CPU/cache 성능을 주장하지 않는다.
CPU MIDR은 gem5의 generic Arm identity를 유지한다. A720AE 이름으로
미구현 ISA 기능을 광고하지 않으며 CPU 성능 profile과 ISA identity를 구분한다.
현재 gem5에 없는 64-bit NEON PMULL은 AP release에서 제외한다.
AES/SHA1/SHA256/CRC32는 유지한다. Linux의 GPT CRC 경로가 지원되는
명령을 선택하도록 한 것으로, Cortex-A720AE의 전체 ISA 지원을 뜻하지 않는다.
Yocto의 `cortex-a720` userspace에 필요한 SVE/SVE2는 VL 128-bit로 활성화한다.
STLUR B/H/W/X release store와 LDAPUR W/X decode도 실제 loader 실행에 맞춰
수정했다. 짧은 EL0 명령 시험은 TimingSimpleCPU와 해당 O3 profile에서 실행했다.
virtio RNG는 `0x30030000`, INTID 290에 연결한다. 기존 gem5 PRNG 데이터를
Ruby functional 경로로 전달하며 timing DMA traffic을 모델링하지 않는다.
시뮬레이션의 entropy 공급용이며 보안용 난수 장치의 성질을 보장하지 않는다.

## 빌드

```sh
./yocto_build.sh --gem5 --keep-conf
```

`--gem5`는 `nexios-gem5-initramfs`를 빌드하며 gem5 native, guest firmware와
benchmark, kernel deploy 의존성도 준비한다. 전용 이미지에는 BusyBox,
`/init`, `/usr/bin/gem5-workload`, `/usr/bin/gem5-control`,
`/usr/bin/apollo-bench`가 포함된다.
추가로 meta-oe의 `lmbench` 3.0-a9, `tinymembench` 0.4.9+git와
공식 STREAM 5.10을 포함한다. lmbench의 Perl/libtirpc 등 런타임 의존성은
Yocto 패키지 의존성으로 함께 설치한다. 외부 meta-oe 레시피는 수정하지 않는다.
STREAM은 제품 레이어의 `recipes-benchmark/stream/stream_5.10.bb`에서
공식 소스와 라이선스를 체크섬으로 고정해 빌드한다.

`/usr/bin/stream`은 alternatives 우선순위100으로 공식 STREAM을 선택하며,
lmbench에 포함된 별도 구현은 `/usr/bin/stream.lmbench`로 유지한다.
공식 STREAM의 기본값은 double 1천만 개 배열3개(약228.9MiB), 10회,
단일 스레드다. `STREAM_CPPFLAGS:pn-stream`으로 빌드 값을 변경하면
변경값을 결과와 함께 기록해야 한다.

이 세 도구는 자동 실행하지 않는다. 기존 `--workload cache/dram`은 계속
ROI marker가 포함된 `apollo-bench`를 사용한다. upstream 도구를 셸이나
`--workload command`로 실행하는 것만으로 O3 전환/ROI 통계가 적용되지는 않는다.
제품 systemd/udev나 dm-verity rootfs 전환은 수행하지 않는다.

ARM 명령어 생성 파일 컴파일은 프로세스 하나가 수 GiB를 사용할 수 있다.
메모리가 부족하면 `APOLLO_PARALLEL_MAKE=-j2`를 위 명령 앞에 지정한다.

`meta-hsoc-auto-solutions/recipes-devtools/gem5/gem5-native.bb`는
`HSOC_APOLLO_GEM5_SRC`를 externalsrc로 사용하며 별도 WORKDIR에서 ARM/CHI를
빌드한다. 기본 Apollo 구성의 산출물은
`build/tmp_baremetal/deploy/gem5-native/gem5.opt`와 `gem5-native.json`이다.
런처는 manifest의 native sysroot library/Python 경로를 적용한다.
바이너리만 다른 호스트로 복사하는 독립 배포는 지원하지 않는다.

`gem5-apollo-guest` target recipe가 Yocto 크로스 툴체인으로 PSCI firmware
`zena_css4.elf`, `zena_css16.elf`와 정적 guest benchmark `apollo-bench`를
빌드한다. 산출물은 `build/tmp_baremetal/deploy/images/apollo-qvp/gem5/`에
배포된다. `gem5-native`의 build task가 이 deploy task에 의존하므로 위 명령으로
host simulator와 guest 실행 파일을 함께 준비한다. guest 파일만 갱신하려면:

```sh
./yocto_build.sh --keep-conf gem5-apollo-guest
```

런처는 배포 파일만 사용하며 실행 시 컴파일하지 않는다. 호스트에 별도
`aarch64-linux-gnu-gcc`를 설치할 필요가 없다. `--bootloader`와 `--benchmark`로
사전 빌드한 파일을 지정할 수 있다. 기본 benchmark는 이미지에 포함돼 있으며 `--benchmark`는 이를 override한다.
파일이 없으면 실행 전에 빌드 명령과 함께 오류를 출력한다.
기존 host build는 `--gem5 /path/to/gem5.opt`로 지정할 수 있으나 raw Image 지원
변경이 포함된 바이너리를 사용해야 한다.

## 실행

```sh
./run_gem5_linux.sh --dry-run
./run_gem5_linux.sh
./run_gem5_linux.sh --bsp --workload smoke --headless
./run_gem5_linux.sh --workload cache --passes 16 --headless
./run_gem5_linux.sh --workload dram --size-kib 16384 --passes 1 --headless
./run_gem5_linux.sh --workload command --command 'cat /proc/cpuinfo' --headless
```

`--build-dir`, `--deploy-dir`, `--kernel`, `--initrd`, `--rootfs`, `--bootloader`,
`--benchmark`, `--profile`, `--cpus`, `--channels`, `--bootargs`, `--max-ticks`, `--out-dir`로
입력과 실행 범위를 지정한다. `--timeout`은 host 시간 상한이며 기본값은
7,200초이다. 실제 제한은 host 속도와 workload 규모에 맞춰 지정한다.
기본 실행은 QBox 런처와 같은 tmux 3분할 화면을 연다. 상단은 입력 가능한
UART, 하단은 `gem5.log` platform 로그와 작업용 셸이다. UART 출력은
`uart.log`에도 저장한다. **F12**를 누르면 해당 tmux 세션과 gem5 프로세스를
종료한다. 다른 세션의 키 설정은 변경하지 않는다. 실행 종료 후에도 창을
유지해 로그를 확인할 수 있다.
`--session NAME`으로 세션 이름(기본 `apollo-gem5`)을 지정하며,
`--no-attach`는 세션만 만들고 바로 연결하지 않는다. 기존 동명 세션이 있으면
덮어쓰지 않고 오류를 출력한다. `--headless`와 `--dry-run`은 tmux를 사용하지 않는다.
`--headless --workload boot`는 `nexios-gem5#` 셸 또는 호환 이미지의
로그인 프롬프트를 관측하면 종료하고
`BOOT_OBSERVED`로 기록한다. 전체 서비스 검증을 뜻하지 않는다.
기존 결과를 덮어쓰지 않도록 출력 디렉터리는 새 경로여야 한다.

`boot`는 이미지에 포함된 전용 `/init`를 실행한다. proc/sys/dev를 준비한 뒤
`NEXIOS_GEM5_INITRAMFS_READY`와 `nexios-gem5#` 셸을 제공한다.
`smoke`, `cache`, `dram`, `command`는 host의 `guest-init.sh`를 gem5 readfile로
전달한다. `/init`가 `/run/gem5-workload.sh`로 읽고 이미지의 `gem5-workload`
스크립트가 이를 실행하며 benchmark는 이미지 내
`/usr/bin/apollo-bench`를 사용한다. `--benchmark`를 지정할 때만 바이너리도
덧붙인다. 원본 initramfs는 변경하지 않는다.
모든 자동 workload는 온라인 CPU 수를 확인한다. 명령 workload 종료 시 sync 후
`poweroff -f`를 사용하며, 최소 BusyBox 패키지에 해당 applet이 없으면
`/proc/sysrq-trigger`의 power-off를 사용한다. 현재 커널은 `CONFIG_MAGIC_SYSRQ=y`다. `--rootfs`를 명시하면
virtio block을 연결하고 WIC block read도 확인한다. WIC 원본은 read-only이며
쓰기는 gem5 메모리 내 COW에 보관한다. `--bsp`는 기존 BSP initramfs/WIC
경로를 사용하는 호환 옵션이다.

`boot-timings.json`에는 simulator 시작 기준 host 경과 초로 `first_uart`,
`linux_start`, `initramfs_ready`를 기록한다. 이 값은 UART에서 각 문자열을
관측한 시각이며, 특히 `linux_start`는 실제 kernel entry 실행 시각이 아니다. 커널 command line의 기존
`lpj=1000000` 강제값은 제거했다. arm64 timer가 제공하는 `lpj_fine`을 사용하며
부팅 가속을 위해 delay 시간을 임의로 줄이지 않는다.
부팅 가속 후보와 한계는 [부팅 성능 조사](apollo-gem5-boot-performance.md)를 참고한다.

## 부팅 snapshot 저장과 복원

```sh
# 처음 한 번: 커널 부팅과 initramfs mount 완료 직후 저장하고 종료
./run_gem5_linux.sh --headless --checkpoint build/qbox-apollo-qvp/gem5/boot-snapshot

# 이후: 같은 snapshot에서 새 명령 실행
./run_gem5_linux.sh --resume build/qbox-apollo-qvp/gem5/boot-snapshot \
  --workload command --command 'cat /proc/uptime; cat /proc/sys/kernel/random/boot_id' --headless

# UART 셸로 복원: 기존 tmux 분할 화면과 F12 종료 사용
./run_gem5_linux.sh --resume build/qbox-apollo-qvp/gem5/boot-snapshot

# Atomic 상태로 복원 후 benchmark가 O3 전환과 warm-up/ROI 수행
./run_gem5_linux.sh --resume build/qbox-apollo-qvp/gem5/boot-snapshot \
  --workload cache --passes 16 --headless
```

`--checkpoint`와 `--resume`은 동시에 사용할 수 없다. 저장 대상은 새 경로여야
하며 실패한 부분 저장도 덮어쓰지 않는다. 저장 성공은 `result.json`의
`CHECKPOINT_SAVED`, `m5.cpt`, `apollo-checkpoint.json`, `launcher.json`으로
확인한다. checkpoint는 Atomic CPU/atomic_noncaching, ROI 이전, diskless
전용 initramfs만 지원한다. `--bsp`, `--rootfs`, `--benchmark` override와 함께
사용할 수 없다. O3 실행 중 저장이나 NPU/virtio block 상태 복원은 지원하지 않는다.

저장 후 `/init`의 checkpoint 명령 바로 다음에서 재개하며 host readfile을 새로
읽는다. 따라서 저장된 RAM/initramfs를 바꾸지 않고 복원마다 workload를 선택한다.
커널·firmware·initramfs·gem5 바이너리·Python 모델 설정·profile·CPU/채널 수·
bootargs가 저장 시점과 다르면 복원을 거부한다. 이 입력을 변경한 뒤에는 새
snapshot을 만든다. snapshot에는 guest RAM 내용이 포함된다.

`--timeout`은 복원 작업에도 host 시간 상한으로 적용한다. `--max-ticks`는
복원 tick을 포함한 절대 simulated tick 상한이다. RAM 복원과 gem5 모델 생성
시간은 여전히 필요하며, 복원 시 UART에 커널 부팅 로그가 다시 나오지 않는 것이
정상이다. 별도 결과 디렉터리의 `gem5.log`, `uart.log`, `result.json`을 확인한다.

### Linux snapshot 검증 (2026-10-22)

기본 4 CPU/16 DRAM 채널, 배포된 Yocto kernel과 전용 initramfs에서 실제 실행했다.
증거 루트는 `build/qbox-apollo-qvp/gem5/`이며 snapshot은
`linux-boot-snapshot/`에 보존했다.

| 실행 디렉터리 | 확인 결과 |
| --- | --- |
| `checkpoint-linux-save` | `CHECKPOINT_SAVED`, 1,659.55초; READY 1,641.45초, tick 614882853500 저장 |
| `checkpoint-linux-resume-first-fixed` | command PASS, 46.37초; `/run/checkpoint-probe` 생성 |
| `checkpoint-linux-resume-second` | command PASS, 43.02초; 이전 RAM 파일 부재 확인 |
| `checkpoint-linux-resume-cache` | PASS, 40.81초; Atomic→O3, warm-up/ROI, checksum=expected=2 |
| `checkpoint-linux-resume-shell` | BOOT_OBSERVED, 22.41초; `nexios-gem5#` 프롬프트 확인 |
| `checkpoint-linux-reject-mismatch` | channels=8 변경 시 simulator 실행 전 거부 |

두 command 복원의 `/proc/uptime`은 `0.56 1.59`, boot ID는 모두
`6c45d4b9-aecb-4f5e-911a-8700748ba3ee`였다. 커널 부팅 배너는 다시 출력되지
않았고 별도 readfile의 `first`/`second` 명령을 각각 실행했다. snapshot 크기는
약25MiB이며 입력 해시와 완료 marker를 포함한다. 최초 저장 중 Atomic GDB로
trace 초기화 상태를 짧게 확인했으므로 최초 시간은 엄밀한 무간섭 benchmark가 아니다.

초기 `checkpoint-linux-resume-first`는 guest 명령까지 성공했지만 BusyBox의
`poweroff` applet 부재로 정상 종료하지 못해 FAIL로 남겼다. 위 `first-fixed`와
`second`는 커널 power-off fallback 수정 후 PSCI SYSTEM_OFF와 gem5 exit=0까지
검증한 결과다. 모델 성능은 보정되지 않았으며 이 시험은 실물 성능 보증이 아니다.
통합 판정은 `checkpoint-linux-verification.json`에 기록했다. root 검사21개와
checkpoint 정책 검사4개도 통과했다.
16 CPU는 미검증이며 WIC/NPU 및 O3 실행 중 checkpoint는 지원하지 않는다.

### lmbench/tinymembench/STREAM 포함 이미지 검증 (2026-10-22)

세 패키지를 처음 추가했을 당시의 이미지용 snapshot은
`build/qbox-apollo-qvp/gem5/linux-benchmarks-snapshot/`이다.
이전 `linux-boot-snapshot`은 이전 이미지의 기록이며 현재 이미지와 호환되지 않는다.

```sh
./yocto_build.sh --gem5 --keep-conf
# 이미 생성한 새 이미지 snapshot으로 UART 셸 복원
./run_gem5_linux.sh --resume build/qbox-apollo-qvp/gem5/linux-benchmarks-snapshot
```

- Yocto build: 4,148 task 성공, 4,043 재사용. 기존 kernel forced-task 경고2개.
- initramfs: gzip8,338,090bytes, raw21,866,496bytes. 최종 CPIO의 AArch64 ELF와
  공식 STREAM alternatives 링크를 검사했다.
- `benchmarks-checkpoint-save`: READY1,662.13초, 저장 완료1,680.99초.
- `benchmarks-resume-packages`:57.76초에 PASS. 복원 guest에서 `lat_mem_rd`,
  `bw_mem`, `tinymembench`, `stream`, `stream.lmbench`의 동적 라이브러리 해석,
  공식 STREAM 링크, `lat_mem_rd` usage 실행 및 정상 power-off를 확인했다.
- `benchmarks-resume-shell`:22.44초에 `nexios-gem5#` 프롬프트 확인.

통합 증거는 `build/qbox-apollo-qvp/gem5/benchmarks-snapshot-verification.json`,
각 실행의 UART/platform 로그는 위 이름의 하위 디렉터리에 있다.
당시에는 전체 upstream benchmark 성능 실행과 이들 도구의 O3/ROI 연동을 수행하지 않았다.
기존 `apollo-bench`의 ROI 측정과 구분한다.

### 벤치마크 실행량 조정

lmbench의 `lat_mem_rd -N 1 8 64`는 최대 8MiB, stride64bytes, 반복1회다.
`-E` 생략 시 원본의 크기별 100ms 측정 목표와 보정 동작을 유지한다.
제품 레이어의 `lmbench_%.bbappend`는 `-E <microseconds>`(200~INT_MAX)를
추가한다. 명시하면 해당 값으로 `ENOUGH`를 설정해 긴 시간 탐색을 생략하고,
타이머·루프 오버헤드는 원본 방식으로 측정한다. 예를 들어
`lat_mem_rd -N 1 -E 200 1 64`는 최대1MiB, 표본 목표200µs다.
이 결과는 수정된 lmbench 축소 시험이며 원본 기본 조건 점수와 구분한다.

제품 레이어의 `tinymembench_%.bbappend`는 다음 실행 옵션을 추가한다.
옵션 생략 시 원본 기본값과 측정 커널을 유지한다.

| 옵션 | 기본값 | 의미 |
|---|---:|---|
| `--bandwidth-size-kib` | 32768 | 대역폭 시험의 버퍼 하나 크기(KiB), 2KiB 배수 |
| `--latency-size-kib` | 65536 | 지연 시험 최대 크기(KiB), 2의 거듭제곱 |
| `--duration-ms` | 500 | 대역폭 표본당 최소 guest 측정 시간(ms) |
| `--repeats` | 10 | 최대 반복 횟수, 기존 조기 종료 조건 유지 |
| `--latency-count` | 10000000 | 지연 시험 접근 반복 수, 16의 배수 |
| `--help` | — | 사용법 출력 |

```sh
tinymembench --bandwidth-size-kib 16 --latency-size-kib 256 \
  --duration-ms 1 --repeats 1 --latency-count 1024
```

위 명령은 기능 검증용 축소 예시이며 표준 성능 결과가 아니다. 대역폭
copy 시험은 source/destination 두 버퍼를 사용하므로 전체 working set은
버퍼 하나 크기보다 크다. 짧은 표본은 타이머 해상도와 잡음의 영향을 받는다.
기존 snapshot 내부 바이너리는 변경되지 않으므로 새 옵션을 사용하려면
새 이미지로 snapshot을 생성하거나 새 바이너리를 readfile로 전달해야 한다.

옵션 추가 검증(2026-10-22): Yocto target 빌드 926 tasks 및 package QA,
호스트 회귀 25개, launcher 회귀 11개 통과. 기존 snapshot에 새 ELF를
readfile로 전달한 Atomic guest 기능 시험은 200.18초에 PASS했다.
SHA256, 도움말, 잘못된 입력 거부, AArch64 bandwidth와 1~256KiB latency
완료를 확인했다. 성능 비교/O3 측정 증거는 아니다.
증거: `build/qbox-apollo-qvp/gem5/tinymembench-options-verification.json`.
이 옵션 기능 검증 단계에서는 initramfs와 snapshot 자체를 재생성하지 않았다.

## 측정과 증거

- `cache`: CPU0 고정, 기본 32 KiB 무작위 dependent pointer chase.
- `dram`: CPU0 고정, 기본 64 MiB scalar sequential read. 현재 캐시 총량보다
  큰 working set이지만 단일 코어 read가 DRAM 최대 대역폭을 뜻하지 않는다.
- 초기화는 atomic CPU에서 수행하고 O3 전환 후 한 번 warm-up한다.
  guest의 workbegin/workend 구간만 측정한다.
  두 marker 전후의 DSB SY로 O3 메모리 접근 경계를 직렬화한다.
  ROI 안쪽 barrier와 loop/OS overhead도 측정 시간에 포함된다.
- 결과는 simulated ticks/simFreq 기반 latency와 useful-byte throughput이다.
  host 실행시간과 구분하며 silicon 성능 또는 최대 DRAM bandwidth로 사용하지 않는다.
- 다른 profile이나 작은 `--size-kib`를 사용하면 DRAM 대신 캐시에 적중할 수 있다.
  stats의 cache/memory traffic으로 실제 접근 계층을 함께 확인해야 한다.

증거는 `build/qbox-apollo-qvp/gem5/<timestamp>/` 아래에 남는다:
`launch.json`, `result.json`, `gem5.log`, `uart.log`, `guest-init.sh`,
`m5out/manifest.json`, `resolved-profile.json`, `roi-events.json`, `stats.txt`.
`result.json`은 해당 ROI의 cache hit/miss와 DRAM read byte도 기록한다.
바이너리와 guest initramfs SHA-256은 `launch.json`에서 확인한다.
raw Image는 바이트를 보존한 ELF wrapper로 로딩하며 원본 SHA를 기록한다.
raw Image에는 kernel symbols가 없으므로 panic/oops hook 및 delay acceleration은
사용하지 않는다. 실패 판단에는 console과 exit/ROI 증거가 필요하다.
현재 gem5의 CPU 교체 후 remote GDB context 갱신 결함으로, O3 전환 뒤
GDB attach 시 switched-out CPU의 MMU port 오류가 발생할 수 있다.
이 경로는 지원하지 않으며 workload 실행 중 디버거를 연결하지 않는다.

## 검증 상태

2026-10-21 기존 제품/BSP initramfs 검증 (아래 성능 수치는 새 전용 이미지의 결과가 아님):

- native recipe: 515 tasks 성공. `--build-info`, native PyYAML import,
  `ldd`, 최종 `bitbake -e` 확인. 근거: `recipe/`.
- launcher/측정기 검사 10개, raw Image wrapper 검사 2개 통과.
  gem5 변경 파일의 pre-commit 검사 통과.
- 실제 ID register와 AES/SHA1/SHA256/CRC32 명령 검사 통과:
  `ap-features-regression/ap-features-result.json`.
- STLUR/LDAPUR, SVE/SVE2의 실제 명령 실행 통과. 같은 initramfs에서 추출한
  loader/libc/coreutils의 true/echo/printf 실행 통과. SE 모드의 BusyBox는
  미구현 syscall 제한이 있으므로 이 결과를 Linux 전체 부팅으로 해석하지 않는다.
  근거: `yocto-loader-probe/`.
- raw Image 1-tick 구성 생성 완료. `native-raw-instantiate/`의 종료는
  의도한 tick 제한이며, workload 결과는 FAIL/INCOMPLETE로 남긴다.
- 최종 cache workload PASS: `native-cache-serialized/result.json`.
  4 CPU online/WIC block read/O3 전환/checksum/ROI 확인. 32 KiB, 16 passes,
  8,192 dependent loads, ROI 19.574 µs, **2.38940 ns/load**.
  L1 hit 8,193 / miss 0, DRAM read 64 bytes. Counter는 CHI demand event로,
  retired load 수와 일대일 대응하지 않는다. Barrier/loop/OS overhead 포함.
- 최초 cache workload는 checksum/ROI parser 검사를 통과했지만, 이후
  m5 marker의 O3 serialization 부족을 확인했다. `native-cache-stlur/`의
  수치는 최종 측정으로 사용하지 않는다. 위 최종 결과는 DSB 경계 보강 후 재측정한 값이다.
- 최초 64 MiB DRAM 실행은 O3 warm-up 중 GDB attach 오류로 중단됐다.
  `native-dram-stlur/`는 FAIL이며 성능 결과로 사용하지 않는다.
- 최종 DRAM workload PASS: `native-dram-serialized/result.json`.
  16 MiB, 1 pass, checksum 2,097,152 일치, ROI 8.262851 ms,
  **2.03044 GB/s** useful read. DRAM read 16,810,752 bytes를 확인했다.
  16/16 채널에서 각각 1,050,624–1,050,816 bytes를 읽었다.
  채널별 근거: `native-dram-serialized/dram-channel-traffic.json`.
  단일 코어 scalar read이며 전체 채널의 최대 대역폭이 아니다.
- 제품 로그인 검증 **FAIL(timeout), 로그인 미확인**:
  `native-product-boot-rng/result.json`, host 7,200.35초 제한으로 종료했다.
  CRNG 초기화, dm-verity rootfs mount, switch_root, 제품 systemd 실행,
  `/var/volatile` mount와 data partition 발견/마운트 시작까지 확인했다.
  종료 전에도 서비스 초기화는 진행했으나 로그인 성공으로 판정하지 않는다.
  `systemd-modules-load.service` 실패가 관측됐다. 제품의 자동 로드 대상인
  `pfdi_misc`는 PFDI_VERSION SMC `0xC40002D0`가 unsupported이면 초기화에
  실패하며, AP PSCI firmware는 이 요청에 -1을 반환한다. PFDI는 이 경로의
  지원 범위 밖이다. 제품 서비스 전체 PASS로 해석하지 않는다.

위 경로는 `build/qbox-apollo-qvp/gem5/` 기준이다. Linux 6.18.5 PREEMPT_RT
이미지는 atomic 부팅에서도 host 수십 분이 걸릴 수 있다. 이번 host에서
cache 실행은 총 32.8분, 16 MiB DRAM 실행은 총 43.2분이었다. 기본 64 MiB/
2-pass DRAM은 더 오래 걸리므로 host timeout과 simulated ROI 시간을 구분한다.

제품 부팅 검증에 사용한 명령은 다음과 같다. `verbose`는 진단 출력용이다.

```sh
./run_gem5_linux.sh --headless --timeout 7200 \
  --bootargs 'console=ttyAMA0,115200 earlycon=pl011,0x1a400000 lpj=1000000 rootwait root=PARTLABEL=rootro_a ro verbose'
```

남은 검증은 제품 로그인과 16코어/다른 채널 수 조합이다. 제품 로그인에는
더 긴 host 실행 예산 또는 부팅 지연 원인 분석이 필요하다. 현재 제공하는
cache/dram workload는 Linux initramfs에서 실행 완료했지만, 제품 서비스 전체
qualification은 완료하지 않았다.

## Guest 빌드의 Yocto 이관 검증

- `./yocto_build.sh --keep-conf gem5-native`: guest deploy 의존성을 포함한
  815 tasks 성공. guest recipe 자체의 build/deploy도 성공했다.
- `bitbake -e`와 compile signature에서 gem5 externalsrc 및 workspace의
  `scripts/gem5/benchmark.c` checksum 추적을 확인했다.
- 최종 deploy의 `apollo-bench`를 gem5 SE에서 실행해 cache/dram checksum을
  확인했다: `yocto-guest-se/result.json`. SE는 affinity syscall을 생략하므로
  Linux 실행이나 성능 검증으로 해석하지 않는다. `--host` 모드의 첫 시험은
  SE의 `sched_getaffinity` 미지원 때문에 실패했으며 해당 로그도 보존한다.
- 런처/tmux/측정기 검사 11개 통과: `yocto-guest-launcher-tests.log`.
  배포 파일이 없으면 빌드 안내로 실패하고, runtime compiler 호출 없이
  initramfs에 사전 빌드한 benchmark를 넣는 동작을 검사했다.
- 최종 Yocto 4코어 firmware의 PSCI self-test 15개 PASS:
  `yocto-guest-firmware-final/uart.log`. 100,000,000 tick 제한으로 종료한
  짧은 firmware 실행 검사이며 `result.json`의 boot 판정은 FAIL로 유지한다.
  Linux 로그인 성공을 의미하지 않는다.
- 기존 Linux ROI 성능 수치는 이관 전 바이너리의 결과다. 새 Yocto 바이너리로
  Linux 전체 부팅과 성능 측정을 다시 수행하지 않았다.

## 초기 전용 gem5 initramfs 검증 이력 (2026-10-22)

- `./yocto_build.sh --gem5 --keep-conf`: 4,076 tasks 성공, 4,047 재사용.
  경고 2개는 기존 kernel configure/compile 강제 실행 taint다.
- `nexios-gem5-initramfs-apollo-qvp.cpio.gz`: 5,574,711 bytes 압축,
  12,851,712 bytes 해제 후 크기. 실행 가능한 `/init`, `gem5-workload`,
  `apollo-bench`와 기본 overlay 부재를 archive 검사로 확인했다.
- 13개 package이며 systemd/udev/kernel module은 포함하지 않는다. OpenSSL과
  CA package는 기존 BusyBox의 필수 의존성이다. build graph에 QBox 또는
  product/BSP image 의존성이 없음을 확인했다.
- build CLI/init 동작 검사 9개, launcher/tmux/benchmark 검사 11개 통과.
  init의 5개 mount 단계 각각의 실패와 workload dispatch도 검사했다.
- 실제 실행 `dedicated-initramfs-boot/`: **FAIL(timeout), 셸 진입 미확인**.
  600.16 host 초 제한까지 커널 실행과 initramfs 해제 시작을 확인했다.
  첫 UART 23.28초, 첫 Linux UART 문자열 172.80초였다. READY는 미관측이다.
  두 번의 짧은 Atomic GDB 관측을 포함한 진단 실행이며 A/B 속도 비교가 아니다.
  CPU0의 BPF/BTF 파싱과 CPU2의 trace metadata 처리 스택을 확인했다.
- 이 초기 검증 단계에서는 새 이미지의 Linux benchmark ROI를 측정하지 않았다.

증거: `recipe-gem5-image-final.log`, `recipe-gem5-image-archive.json`,
`recipe-gem5-image-graph.log`, `dedicated-initramfs-host-tests.log`,
`initramfs-launcher-tests.log`, `dedicated-initramfs-boot/`.
