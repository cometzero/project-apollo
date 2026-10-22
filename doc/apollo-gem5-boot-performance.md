# Apollo gem5 Linux 부팅 성능 조사

조사일: 2026-10-22. 이 문서는 소스와 기존 실행 증거를 조사한 결과다.
전용 initramfs와 런처 변경은 `apollo-gem5.md`에 별도로 기록한다.
이 조사 자체에서는 커널 가속 구현이나 A/B 성능 측정을 수행하지 않았다. 예상 효과에 배수를
부여하지 않는다. 경로는 workspace 기준이며 줄 번호는 조사 시점 기준이다.

## 결론과 우선순위

1. **작은 전용 initramfs**: benchmark 목적이면 product의 udev/systemd/rootfs
   전환을 거치지 않고 `/init`에서 proc/sys/dev mount, CPU 확인, workload를
   수행한다. 기존 product 부팅 검증은 별도 유지한다. 이는 실행 범위를
   줄이는 방법이며 product 이미지와 동등한 부팅 성능 결과가 아니다.
2. **별도 최소 커널**: initramfs 축소 후에도 유지되는 kernel 초기화 비용을
   줄인다. 현재 커널에서 실제 관찰된 trace metadata 초기화를 먼저 줄이고,
   사용하지 않는 드라이버/네트워크/파일시스템/crypto를 제외한다. 4 CPU,
   GICv3, PL011, PSCI, timer, initramfs, ELF, proc/sys/devtmpfs, 필요 시 virtio
   block/RNG와 현재 workload ABI/SVE를 유지한다. PREEMPT_RT 제거는 별도
   실험 항목으로 둔다. 제품 RT 동작과 동일하다는 주장을 하지 않는다.
3. **동일 이미지 경로의 호스트 profile**: boot 단계별 host 시간과 guest
   tick/명령 수를 수집하고 CPU/Ruby atomic 메모리 접근/초기 이미지 로드의
   CPU 시간을 측정한 뒤 최적화한다. 현재 소스만으로 Ruby functional 검색을
   전체 병목이라고 단정할 수 없다.
4. **정확히 일치하는 kernel symbols A/B**: 동일 빌드의 vmlinux를 사용하면
   기존 delay skip hook을 사용할 수 있다. raw Image와 동일한 text/config임을
   확인해야 한다. 이는 busy delay 구간에만 효과가 있으며 trace 문자열 처리,
   메모리 복사나 udev 명령 실행을 제거하지 않는다.
5. **boot checkpoint**: diskless 전용 initramfs의 Atomic 부팅 완료 지점을
   저장하고 복원하는 옵션을 추가했다. 최초 부팅 비용은 그대로이며 반복 실행에서
   커널 초기화를 생략한다. 사용법과 실제 검증은 `apollo-gem5.md`를 참고한다.
   block 장치나 O3 실행 중 snapshot은 지원하지 않는다.
6. **Arm host의 KVM**: 호스트 변경 및 AP 장치/메모리/CPU 전환 통합이 필요한
   장기 후보다. 현재 x86_64 호스트에서 Arm guest KVM은 사용할 수 없다.

## 현재 구현과 관찰된 비용

- `hsoc-stack/tools/gem5/configs/zena_cmn/run_fs.py:65,124`는 기본 Atomic
  부팅과 `atomic_noncaching` 메모리 모드를 사용한다. ROI만 O3로 전환한다.
  따라서 “Atomic으로 바꾸면 된다”는 제안은 이미 적용된 설정을 반복한다.
- CPU 접근은 `src/cpu/simple/atomic.cc:274`의 `sendAtomic`에서
  `src/mem/ruby/system/RubyPort.cc:344`로 들어간다. Ruby는 noncaching만
  허용하며 주소에 맞는 memory controller를 선택한다(:385-397).
  `src/mem/ruby/slicc_interface/AbstractController.cc:420`은 memory port로
  전달한다. 이는 timing CHI packet simulation과 다르다.
- 이미지 로딩과 VirtIORng의 `system.physProxy`는 functional system-port
  경로를 사용한다. `src/sim/system.cc:173`, `src/mem/port_proxy.cc:53`,
  `src/mem/ruby/system/RubyPort.cc:414`를 참조한다. 일반 Atomic CPU 접근과
  이 functional 경로의 비용을 구분해서 측정해야 한다.
- 조사 대상 product kernel Image는 약31MiB, uncompressed initrd는 약48MiB다.
  큰 initrd는 호스트→guest 메모리 로드뿐 아니라 guest CPIO 해제·파일 생성·
  page 해제 작업도 늘린다. 호스트에서 gzip을 해제하더라도 후자는 남는다.
- `build/qbox-apollo-qvp/gem5/native-cache/gdb-boot-snapshot-25min.txt`는
  `trace_event_update_all(map,len=1186)` → `update_event_fields` → `strstr`
  실행을 기록한다. “UART 출력 없음”이 해당 구간의 정지 증거는 아니다.
- `native-product-boot-stlur/gdb-boot-snapshot-25min.txt`는
  `jent_mod_init` → `jent_entropy_init` → `jent_measure_jitter` 실행을 기록한다.
- `native-product-boot-rng/gdb-udev-snapshot.txt`는 CRNG_READY와 initramfs
  udev worker들의 파일 경로 조회를 기록한다. `gdb-udev-snapshot-99min.txt`는
  PID1 systemd, dm-0/vda5 journal과 rootfs systemd-udevd를 기록하므로 이전
  initramfs udev에서 동일하게 정지한 상황이 아니다.
- VirtIORng 추가 후 UART `random: crng init done`이 확인되었다. entropy
  해결이 udev/systemd 전체 명령 실행 비용까지 제거하지는 않는다.

## 커널 설정의 구체적 후보

현재 빌드의 기준은
`build/tmp_baremetal/work/apollo_qvp-poky-linux/linux-yocto-rt/6.18.5+git/build/.config`다.
`CONFIG_PREEMPT_RT=y`, `CONFIG_NR_CPUS=512`, `CONFIG_EVENT_TRACING=y`,
`CONFIG_FTRACE=y`, `CONFIG_FUNCTION_TRACER=y`, `CONFIG_FUNCTION_GRAPH_TRACER=y`,
`CONFIG_CRYPTO_JITTERENTROPY=y`가 설정되어 있다.

- 별도 benchmark 커널에서 tracing 기능을 제외하면 실제 관찰된 trace eval
  metadata 작업을 줄일 후보가 된다. `ftrace=off` 같은 runtime 토글이 해당
  초기화 자체를 제거한다고 가정하지 말고 Kconfig 의존성/최종 `.config`를
  확인한다.
- `NR_CPUS=4`는 실제 AP CPU 수에 맞는 크기 축소 후보다. 실제 부팅 CPU 수는
  이미4이므로 512개 CPU를 부팅하고 있다는 의미는 아니다.
- jitterentropy 제거는 VirtIORng/CRNG_READY가 검증된 전용 커널에서 검토한다.
  entropy 공급 없이 RNG 검사를 단순 우회하는 설정은 권장하지 않는다.
- debug DWARF 제거는 vmlinux 크기/호스트 symbol 처리에는 영향을 주지만,
  부팅 raw Image의 실행 instruction을 동일 비율로 줄이는 방법은 아니다.
- `CONFIG_INIT_ON_ALLOC_DEFAULT_ON`과 `CONFIG_INIT_ON_FREE_DEFAULT_ON`은
  이미 꺼져 있다. 이를 끄자는 제안은 현재 설정에는 효과가 없다.
  arm64 `free_initmem()`은 별도로 poison을 수행한다
  (`arch/arm64/mm/init.c:387`, `mm/page_alloc.c:6167`). 전체 free 비용을
  init_on_free 옵션 하나로 제거할 수 없다.

## delay, symbols, clock의 정확성

`src/arch/arm/linux/fs_workload.cc:212`는 symtab이 없는 raw Image wrapper에서
symbol event hook을 건너뛴다. 같은 파일:258-273은 symbol이 있을 때
`__udelay`/`__const_udelay` skip hook을 등록한다. 이전 vmlinux 실행도
trace/jitterentropy 비용이 컸으므로 symbol 제공만으로 큰 개선을 보장하지 않는다.

기존 cmdline의 `lpj=1000000`은 정확성 문제가 있어 이번 런처 변경에서 제거했다. Linux
`arch/arm64/kernel/time.c:69`는 timer rate/HZ로 `lpj_fine`을 설정한다.
현재125MHz timer와 HZ100이면1250000이다. `init/calibrate.c:286`에서 명시한
lpj가 이 값을 덮어쓰고 `arch/arm64/lib/delay.c:23`의 delay 계산에 쓰인다.
따라서 1000000은 요구 delay를 약20% 짧게 만드는 값이다. 현재 기본값은
커널이 timer에서 얻은 값을 사용하며, 부팅 가속을 위해 이를 더 줄이지 않는다. CPU 주파수를
임의로 높이거나 timer를 낮추는 방법도 workload/timer 의미를 바꾸므로 먼저
선택할 방법이 아니다.

## checkpoint와 디버깅 한계

`run_fs.py`는 diskless Atomic boot의 checkpoint/restore를 제공한다.
WIC를 연결하는 경우 `src/dev/arm/timing_virtio_block.cc:588,594`의
serialize/unserialize는 명시적 fatal이므로 저장과 복원에서 block 장치를
거부한다. Atomic noncaching 상태에서 drain/writeback 후 저장하며, O3/ROI
진입 뒤 저장은 거부한다. 공식 checkpoint 문서의 Ruby flushing 설명 자체가
현재 CHI 구현에 대한 runtime 검증을 대신하지는 않는다.

O3 전환 뒤 GDB attach에는 현재 stale thread-context 문제로 simulator가
종료된 증거가 있다(`native-dram-stlur/gem5.log`). 속도 조사에는 호스트
profiling/명시적 통계 지점을 우선 사용하고, 기존 바이너리의 O3 guest GDB
접속을 반복하지 않는다. Atomic 실행의 bounded snapshot과 구별해야 한다.

## 검증 순서

같은 native 바이너리/호스트 자원 조건에서 최소 initramfs만 교체한 실행을
먼저 비교한다. 이후 최소 커널을 한 단계씩 적용한다. 각 실행에서 Image,
initrd, DTB, cmdline, config hash와 kernel initcall/guest init/ROI 진입의 host
시간 및 sim tick을 보존한다. `initcall_debug`는 원인 구간 진단용으로만
사용하고 출력 증가 때문에 최종 성능 측정에서는 제거한다. 최종 ROI는
동일 CPU 수/캐시/메모리/주파수와 warmup 정책으로 검증한다.

## 공식 자료

- [gem5 memory system](https://www.gem5.org/documentation/general_docs/memory_system/):
  atomic 접근은 fast forwarding에 사용하며 timing contention과 구분된다.
- [gem5 KVM](https://www.gem5.org/documentation/general_docs/using_kvm/):
  Arm/x86 guest는 각각 대응하는 host architecture가 필요하다.
- [gem5 checkpoints](https://www.gem5.org/documentation/general_docs/checkpoints/):
  긴 실행의 상태 재사용과 CPU 복원, Ruby memory state 제약을 설명한다.
- [Linux kernel parameters](https://docs.kernel.org/admin-guide/kernel-parameters.html):
  `initcall_debug`, `lpj`, `init_on_alloc`, `init_on_free`의 정의와 적용 조건.

## 전용 initramfs 초기 실행 관측 (2026-10-22)

부모 작업의 `dedicated-initramfs-boot` Atomic 실행을 host 약3분 시점에
1회 관찰했다. `gdb-early-boot-snapshot.txt`에서 CPU0는 `pci_driver_init`
→ `bus_register` → `/bus/pci_express` uevent 생성 → `rt_mutex_unlock`을
실행했고 나머지3 CPU는 secondary 초기화를 마친 idle 상태였다. 따라서
이 시점 UART에 Linux 출력이 없더라도 커널 진입 실패로 판정할 수 없다.
관측 sim tick은67,798,088,000이며1THz 기준 약0.0678초다. 정상 detach를
확인했으며 실행 설정·기한은 바꾸지 않았다. 이는 초기 진행 증거이며
전체 부팅 성공이나 이전 initramfs 대비 가속률 측정은 아니다.

같은 실행의 host 약7분 snapshot(`gdb-kernel-cost-snapshot.txt`)에서 CPU0는
`ip_init` → `ip_rt_init` → `xfrm_init` → `register_xfrm_state_bpf` →
`btf_parse_vmlinux` → `btf_check_type_tags`를 실행했다. CPU2는
`trace_event_update_all(len=1186)`의 `event_btrfs_trigger_flush` 필드에서
`COMPACT_SUCCESS` 문자열 치환을 처리했다. 나머지2 CPU는 idle이었다.
이는 작은 initramfs에도 원래 커널의 BPF/BTF 검증 및 tracing metadata
초기화가 남음을 보여 준다. 최소 커널 후보에 `CONFIG_DEBUG_INFO_BTF`와
BPF/XFRM의 필요성 검토를 추가한다. DWARF와 달리 BTF는 이 실행에서 실제
커널 runtime 처리 비용을 관찰했다. 단일 snapshot은 각 구간의 누적 시간이나
교착 여부를 측정하지 않으며, 해당 기능을 끈 A/B 검증이 필요하다.

## 실제 checkpoint 반복 실행 검증

후속 구현에서 동일한 배포 kernel로 최초 READY까지1,641.45초, snapshot 저장
완료까지1,659.55초가 걸렸다. Atomic GDB 상태 확인1회가 포함된 관측값이다.
`checkpoint-linux-save/atomic-kernel-progress.txt`에서 trace 초기화 실행을 확인했고,
완료된 `linux-boot-snapshot`을 재사용한 command 두 번은 각각46.37초/43.02초에
명령 실행과 정상 종료를 완료했다. 두 실행의 RAM rollback/동일 boot ID도 확인했다.
복원 후 O3 cache benchmark는40.81초에 ROI/checksum PASS였다.
이 시간은 gem5 생성·복원·workload·종료를 포함하며 host 속도에 의존한다.
실행 방법과 증거 목록은 [snapshot 검증](apollo-gem5.md#linux-snapshot-검증-2026-10-22)을 참고한다.
