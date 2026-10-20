# Apollo AP 전용 gem5

## 범위와 모델

`run_gem5_linux.sh`는 `run_qbox_linux.sh`와 동일한 Apollo Yocto `Image`,
initramfs, WIC를 사용한다. AP CPU, 캐시, interconnect, DRAM, GICv3,
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
./yocto_build.sh --keep-conf gem5-native
```

ARM 명령어 생성 파일 컴파일은 프로세스 하나가 수 GiB를 사용할 수 있다.
메모리가 부족하면 `APOLLO_PARALLEL_MAKE=-j2`를 위 명령 앞에 지정한다.

`meta-hsoc-auto-solutions/recipes-devtools/gem5/gem5-native.bb`는
`HSOC_APOLLO_GEM5_SRC`를 externalsrc로 사용하며 별도 WORKDIR에서 ARM/CHI를
빌드한다. 기본 Apollo 구성의 산출물은
`build/tmp_baremetal/deploy/gem5-native/gem5.opt`와 `gem5-native.json`이다.
런처는 manifest의 native sysroot library/Python 경로를 적용한다.
바이너리만 다른 호스트로 복사하는 독립 배포는 지원하지 않는다.

PSCI firmware와 guest benchmark는 호스트 `make`, `aarch64-linux-gnu-gcc`,
`aarch64-linux-gnu-ld`로 실행 디렉터리에 빌드한다. 정적 AArch64 libc가 필요하다.
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
`--profile`, `--cpus`, `--channels`, `--bootargs`, `--max-ticks`, `--out-dir`로
입력과 실행 범위를 지정한다. `--timeout`은 host 시간 상한이며 기본값은
7,200초이다. 실제 제한은 host 속도와 workload 규모에 맞춰 지정한다.
`--headless`가 없으면 UART에 표준입력을 전달한다.
`--headless --workload boot`는 로그인 프롬프트를 관측하면 종료하고
`BOOT_OBSERVED`로 기록한다. 전체 서비스 검증을 뜻하지 않는다.
기존 결과를 덮어쓰지 않도록 출력 디렉터리는 새 경로여야 한다.

`boot`는 원래 initramfs `/init`를 실행한다. `smoke`, `cache`, `dram`,
`command`는 원본 initramfs에 별도 init과 workload만 덧붙여 실행한다.
따라서 workload 성공이 제품 rootfs/systemd 전체 부팅 성공을 의미하지 않는다.
모든 자동 workload는 온라인 CPU 수와 WIC block read를 먼저 확인한다.
`smoke`는 이 검사 후 종료한다.
`command`는 initramfs 안에서 실행하며 원래 제품 서비스는 시작하지 않는다.
WIC 원본은 read-only로 열고 쓰기는 gem5 메모리 내 COW에 보관한다.

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

2026-10-21 검증:

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
