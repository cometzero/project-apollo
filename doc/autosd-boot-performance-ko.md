# AutoSD QBox full-system 부팅 지연 조사

## 범위와 측정 방법

`./run_qbox_autosd.sh`의 실제 RSE → SI CL0/CL1 → AP UKIBoot/AutoSD
경로를 대상으로 한다. AP-only 부팅이나 호스트 빌드 성공으로 full-system
동작을 대체 판정하지 않는다. 원본 다운로드 대신 launcher의 private disk를 사용한다.

`systemd-analyze time`은 guest 시간이다. 펌웨어 시작부터의 호스트 경과 시간이나
실제 하드웨어 성능을 뜻하지 않는다. `blame` 항목은 서로 겹치므로 합산하지 않는다.
호스트의 BitBake 부하를 제거한 뒤 변경 후 부팅을 측정한다.

## 원인과 수정

- 가장 큰 추가 지연은 AutoSD `98-trace-cmd.rules`였다. 비활성 상태인
  `trace-cmd.service`를 모듈 add 이벤트마다 `systemctl is-active`로 조회한다.
  135개 모듈이 있고 coldplug가 module 이벤트를 먼저 처리하므로 디스크·serial
  인식이 뒤로 밀린다. 현재 guest에서 조회 1회는 약 0.805초였다.
  vendor 조건과 active 상태의 reload 동작을 보존하면서, systemd가 서비스
  활성 기간에 관리하는 `RuntimeDirectory`를 먼저 검사하도록 한다.
  서비스가 꺼져 있으면 외부 프로세스와 D-Bus 호출을 생략한다.
  vendor rule이 달라지거나 사용자 override가 있으면 덮어쓰지 않고 SKIP한다.
- 기존 manifest의 `slub_debug=FPZ`는 모든 SLUB 객체의 검증·poison·redzone을
  활성화하고 빠른 할당 경로를 제한한다. 기본 full-system 실행에서 제거한다.
- `rcupdate.rcu_expedited=1 rcupdate.rcu_normal_after_boot=0`도 제거한다.
  PREEMPT_RT 커널의 기본 RCU 정책을 사용한다. 진단용 원래 설정은
  `./run_qbox_autosd.sh --diagnostic-boot`로 재현할 수 있다.
- SLUB debug에 따른 unhashed kernel pointer 경고도 같은 원인이다.
  보안 경고의 로그 레벨만 낮추는 방식은 사용하지 않는다.
- SI CL1용 `ethsi1`은 DHCP망이 아니다. 기준 계약은 VLAN 200,
  AP `192.168.1.2/24`, SI CL1 `192.168.1.1/24`다. SSH용 `eth0` 설정은
  유지하고 `ethsi1`의 자동 DHCP만 억제한다. 이는 HIPC 통신 검증과 별개다.
- private guest provisioning에서 `NetworkManager/conf.d`의 추가 정책과
  `boot-efi.mount`의 `0077` permission mask를 설치한다. 기존 사용자 연결은
  삭제하지 않으며 다음 부팅에 적용된다. 조사 이미지의 자동 DHCP 연결은
  `/run/NetworkManager/system-connections/`에 있어 재부팅으로 소멸한다.
  `/etc/fstab` 없는 이미지에는 임의 fstab 대신 전용 mount drop-in을 쓴다.
- AutoSD의 BPF LSM 요구에 맞춰 `CONFIG_BPF_LSM`, `CONFIG_DEBUG_INFO_BTF`를
  활성화한다. owned Yocto QVP metadata에서 `KERNEL_DEBUG=True`로
  `pahole-native`를 공급한다. out-of-tree 모듈의 불필요한 BTF 결합을 피하기 위해
  `CONFIG_DEBUG_INFO_BTF_MODULES`는 비활성화한다.
- `CONFIG_SECURITY_YAMA=y`로 AutoSD의 `kernel/yama/ptrace_scope` sysctl
  인터페이스를 제공한다. 실제 scope 값은 기존 AutoSD 정책이 설정한다.
- FF-A RxTx 등록 실패는 반환 오류 번호를 출력하도록 개선하여 펌웨어와
  Linux의 실제 실패 계약을 구분한다. 오류 출력 개선 자체를 FF-A 복구로 판정하지 않는다.
- 실제 반환값은 `-13`(FFA_DENIED)이었다. U-Boot ExitBootServices에서
  EFI disk handle 삭제 실패가 DM 제거 순회를 중단하여 기존 FF-A RX/TX
  정리가 실행되지 않는 경로를 확인했다. OS handoff 때만 EFI protocol
  삭제를 생략하고 DM 종료를 계속하도록 수정한다. 일반 hot-unplug 보호와
  잘못된 memory-map key의 ExitBootServices 재시도 동작은 유지한다.
- ESP는 private 복사본에서 `fsck.fat`로 검사한다. 임시 ESP의 repair 결과가
  dirty flag 1비트 변경뿐이고 재검사가 clean일 때만 반영한다. 다른 손상은
  자동 복구하지 않고 중단한다. `dosfstools`가 필요하다.

## 변경 전 관측

2026-09-28의 단일 baseline 부팅:

| 항목 | Guest 시간 |
|---|---:|
| Kernel | 5.959초 |
| Initrd | 8.949초 |
| Userspace | 139.304초 |
| 합계 | 154.213초 |
| dev-vda5.device blame | 81.008초 |
| graphical.target 도달(userspace 기준) | 115.504초 |

`systemd-udev-trigger` 완료 뒤에도 장치 인식이 지연되어 ESP 마운트가 늦었다.
`systemctl --failed`는 0개다. 서비스 실패와 느린 장치 인식은 구분해야 한다.
이후 host 빌드를 병행한 상태에서는 `user@0` 시작 timeout과 ADAS stop 후
exit 137도 관측됐다. 따라서 최초 부팅의 0 failed를 장시간 안정성 PASS로
확대하지 않는다. 개선 후에는 host 빌드 없이 다시 검증한다.

증거:

- `build/qbox-apollo-qvp/autosd-boot-diagnosis-20260928/`
- `build/autosd/boot-diagnostics-before-partial/time.txt`, `blame.txt`
- `build/autosd/boot-diagnostics-before-journal/console.log`
- `build/autosd/boot-diagnostics-before-detail/console.log`

## 진단 자료 수집

실행 중인 private guest를 대상으로 다음과 같이 수집한다. 포트와 출력 이름은
실제 세션에 맞춘다. 기존 출력 디렉터리를 재사용하지 않는다.

```sh
python3 scripts/autosd_demo/guest_exec.py --port 2244 \
  --out build/autosd/boot-check-NEW --timeout 240 \
  --upload scripts/autosd_demo/collect_boot_diagnostics.sh:/var/tmp/collect-boot.sh \
  --command 'bash /var/tmp/collect-boot.sh /var/tmp/boot-check-NEW' \
  --download /var/tmp/boot-check-NEW.tar.gz:boot-evidence.tar.gz
```

`journalctl -b`로 현재 부팅만 수집한다. 이전 부팅의 journal을 새 회귀로
오인하지 않는다. `critical-chain`/SVG 생성은 제한 시간 내에서 시도하며,
실패 시에도 time/blame/journal 자료를 남긴다.

## 판정상 주의

- `cpuidle.off=1`은 그대로 유지한다. 기존 QBox 전원관리 검증이 미완료인 상태에서
  경고 제거만을 위해 CPU idle을 활성화하지 않는다.
- `arm_si_rproc`의 out-of-tree module taint는 빌드 형태를 알리는 표시다.
- host 부하에 따른 hrtimer/PFDI 지연은 물리 RT 성능으로 해석할 수 없다.
- 최소 AutoSD initrd에는 journald가 없어 일부 초기 service stdout의 journal socket
  연결 경고가 있다. rootfs 전환 후 journald의 동작과 구분해야 한다.

변경 전후 수치는 각각 단일 부팅 관측값이며 통계적 벤치마크는 아니다.

### 1차 개선: 커널·RT 옵션·EFI 권한·NetworkManager

`build/autosd/boot-optimized-first-check/console.log`:

- 총 137.227초(kernel 5.402 + initrd 7.659 + userspace 124.165).
- `dev-vda5.device`: 73.984초. 따라서 진단 옵션 제거만으로 주요 지연이
  해결됐다고 판정하지 않았다. 이후 trace-cmd rule 원인을 추가 조사했다.
- `systemctl --failed`: 0개.
- LSM `capability,yama,selinux,bpf`, `/sys/kernel/btf/vmlinux` 존재,
  YAMA scope 0, BPF LSM program attach 확인.
- ESP `fmask=0077,dmask=0077`, world-accessible 경고 없음.
- NetworkManager의 ethsi1 자동 DHCP 연결 및 재시도 경고 없음.
- FF-A와 기존 FAT dirty-bit 경고는 남아 있어 2차 수정을 진행했다.

### 2차 개선: trace-cmd coldplug·EFI handoff·ESP 검사

증거: `build/autosd/boot-udev-final-check/console.log`,
`build/qbox-apollo-qvp/autosd-boot-udev-20260928/`.

| 항목 | 원래 설정 | 1차 개선 | 최종 관측 |
|---|---:|---:|---:|
| systemd 총 부팅 시간 | 154.213초 | 137.227초 | 92.423초 |
| Userspace | 139.304초 | 124.165초 | 79.222초 |
| graphical.target(userspace 기준) | 115.504초 | 105.829초 | 61.391초 |
| ESP mount 완료(journal monotonic) | 97.444초 | 약 89초 | 43.372초 |

총 부팅 시간 약 40% 감소. 마지막 행은 systemd 단계 시간과 기준이 다르므로
서로 합산하지 않는다. 최종 부팅 시 별도 host 빌드 없음.

- RSE/SI CL0/SI CL1/AP boot와 HIPC/PFDI provision PASS.
- `systemctl --failed`: 0개. ADAS, Safety Monitor, QM 모두 active.
  Safety 상태 `HEALTHY`, failures 0.
- `udevadm verify`: 새 rule 1개 PASS.
- `/sys/bus/arm_ffa/devices/arm-ffa-{1..7}` 등록, OP-TEE driver 초기화.
  EFI handle 삭제 오류와 RX/TX 등록 실패 해소.
- EFI 권한·FAT dirty·YAMA·unhashed pointer·ethsi1 DHCP 재시도 경고 없음.
- ESP 검사는 실제로 1바이트의 dirty bit만 수정했으며 receipt를
  `launch.json`의 `esp_check`에 보존한다.
- 관련 Python 테스트 74개 PASS, 셸 스크립트 syntax PASS.
- 실제 trace-cmd 활성/비활성 회귀 검사 PASS:
  `build/autosd/trace-policy-runtime-20260928/`. 활성 시 marker 생성과
  module add에 따른 reload(exit 0)를 확인했다. 비활성 시 reload 없음.
  임시 설정과 격리 trace instance는 정리했고 global tracing 상태는 복원했다.
  재현 스크립트: `scripts/autosd_demo/check_trace_cmd_boot_policy.sh`.

남은 표시의 의미:

| 표시 | 판정 |
|---|---|
| SMMU 2-level SID 25/32 bits | Linux stream table 커버리지 제한. 광고 기능을 임의로 축소하지 않음 |
| cpuidle 등록 오류 | 의도적인 `cpuidle.off=1`; 미검증 전원관리 활성화로 숨기지 않음 |
| initrd journal socket 없음 | 최소 AutoSD initrd에 journald 부재. rootfs journald와 별개 |
| arm_si_rproc out-of-tree taint | 외부 모듈 빌드 형태 표시 |
| BlueChi heartbeat interval 0 | 기존 비활성 정책. 설정 변경 없이 명시적으로 남김 |
| FF-A notification -95 | firmware가 제공하지 않는 선택 기능. FF-A 장치 등록/OP-TEE 초기화와 구분 |

이 결과는 기능 부팅/서비스 확인이며 ASIL 인증, 물리 RT 성능 또는 전체 firmware
reset qualification이 아니다. 전원 제어/watchdog 검증은 별도 단계로 수행한다.

## 빌드 및 재부팅 준비 증거

- `./yocto_build.sh --keep-conf virtual/kernel -c configure`: 837 tasks 성공.
- `./yocto_build.sh --keep-conf --bsp`: BPF/BTF 변경 후 및 YAMA 추가 후 각각
  5846 tasks 성공. 경고 5개는 기존 forced-task taint이며 컴파일 오류가 아니다.
- 최종 `.config`: BPF_LSM/BTF/YAMA 활성, pahole 1.29, BTF_MODULES 비활성.
- `CONFIG_MODVERSIONS=n`이므로 module CRC 검증을 했다고 주장하지 않는다.
  동일 빌드의 kernel modules archive와 HIPC/PFDI 모듈을 모두 설치하고 재부팅한다.
- 실행 중인 이전 커널에 새 모듈을 강제 로드하지 않도록
  `install_guest_modules.sh ARCHIVE --install-only`를 사용한다.
- `build/autosd/boot-next-kernel-modules/`: 설치 PASS.
- `build/autosd/boot-before-poweroff/`: 정상 종료 요청 PASS;
  baseline UART에서 모든 파일시스템 unmount 및 `reboot: Power down` 확인.
- 최종 Yocto UKI SHA256:
  `632c30263850def2c41b4577b35c94eeb662e989027b0b8759d9cdf746bb3e85`
- 최종 modules archive SHA256:
  `c375089f42abfd0bb33eaee4e37682942c1c928c3a66f92e49ac0e09d55b4fd9`
- 로그: `build/autosd/kernel-bpf-configure-20260928.log`,
  `kernel-bpf-bsp-20260928.log`, `kernel-bpf-yama-bsp-20260928.log`.
