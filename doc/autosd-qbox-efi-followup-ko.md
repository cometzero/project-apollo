# Apollo QBox AutoSD EFI 최초 부팅

## 범위

기존 AP-only direct Linux 경로를 유지하면서 `--autosd MANIFEST --uki UKI`를
추가했다. SystemC/libqemu core reset 구현은 변경하지 않았다. 이 경로는
최초 U-Boot→UKIBoot→EFI Linux 부팅 검증용이며 전체 플랫폼 guest reboot,
bootc 업데이트/자동 rollback, Secure Boot는 검증 범위 밖이다.

현재 상태: **regular 및 OSTree 모두 실제 EFI 최초 부팅 PASS**.
private copy에서 U-Boot→UKIBoot→EFI Linux→root login까지 실행했다.

| 이미지 | 실행시간 | 결과 | 증거 디렉터리 |
|---|---:|---|---|
| AIB minimal_qm regular | 102.05초 | PASS, slot A successful | `build/autosd/qbox-efi-first/` |
| AutoSD nightly OSTree | 112.56초 | PASS, slot A successful | `build/autosd/qbox-efi-ostree-first/` |

## 실제 증거

`build/autosd/qbox-efi-first/`의 `launch.json`, `linux-uart.log`, `qbox.log`,
`result.json`에 입력/부팅로그/판정을 보존했다.

- U-Boot 2026.01-rc4가 DT의 RAM과 virtio block을 발견하고 ESP의
  `BOOTAA64.EFI`를 실행했다.
- UKIBoot 0.2.1이 미초기화 bootctl을 실제 초기화하고 slot A를 선택했다.
- Linux: `efi: EFI v2.11 by Das U-Boot`, kernel cmdline의
  `efi=runtime androidboot.slot_suffix=_a` 확인.
- `/boot/efi` mount와 `ukiboot-set-success.service` 성공.
- 실제 probe: EFI 디렉터리 존재, booted slot=active slot=0, AutoSD ID,
  CPU 4개, `/dev/vda` 읽기 성공.
- QBox 종료 후 raw disk 검사: bootctl magic `1420550408`, CRC valid,
  slot A `successful_boot=1`, `tries_remaining=0`, priority=15.
  slot B는 `successful_boot=0`, `tries_remaining=7`, priority=14.
- 결과 파일은 `boot_method=ukiboot-efi`, `efi_boot_observed=true`,
  `ukiboot_slot=0`, `efi_reboot_support=NOT_IMPLEMENTED`를 기록한다.

private disk 디렉터리의 실제 할당량은 약 1.1 GiB이며 원본 이미지는
수정하지 않았다. UKIBoot 시작 시 U-Boot의 `Handle ... has protocols installed.
Unable to delete` 메시지는 남아 있지만 위 최초 부팅은 완료됐다.

OSTree 실행도 동일 EFI/bootctl 성공 조건을 만족했다. 추가로
`/run/ostree-booted` 존재, `/`의 overlay mount, `ostree admin status`의
`default c6da042842823bb2eec1f9dfc61306d13946440fb3110f78e16f72f0d2c708c2.0`
배포를 확인했다. OSTree private 디렉터리는 약 2.6 GiB를 사용했다. 두 실행
후 QBox 프로세스는 종료했으며 원본 regular/OSTree 이미지를 보존했다.

## 구현

- `scripts/run/run_qbox_linux.py`: 기존 AutoSD UKI/disk helper 공유, private disk
  생성, U-Boot 명령 전송, EFI 존재·booted/active slot·success service 검사,
  QBox 종료 후 bootctl CRC/successful_boot/tries_remaining 검증.
- `platforms/apollo/apollo-qvp-linux.lua`: firmware 모드에 한해 U-Boot를
  `0x80080000`에 적재. direct Image는 기존 `0x80200000` 유지.
- `platforms/apollo/linux-boot/prepare.py`, `boot.S`: firmware text offset
  `0x80000` 검증 및 해당 entry로 EL2 진입. EFI 모드의 외부 initrd는 거부하고
  DT의 기존 initrd 정보를 제거한다. initrd는 on-disk UKI에서 공급한다.

Lua/boot 파일의 repository는 `hsoc-stack/tools/qbox-platform/`이다.

QBox QemuInstance는 `-M none -m 0`으로 실행하므로 standalone QEMU의
`-kernel` 옵션이 아닌 SystemC loader로 firmware를 적재한다. 기존
`u-boot-apollo-qemu.bin`은 x0 DTB에서 DRAM과 장치를 발견하는 보드 코드다.

## 재현 명령

```sh
QBOX_APOLLO_NETDEV='type=user,hostfwd=tcp:127.0.0.1:2229-:22' \
./run_qbox_linux.sh \
  --autosd build/autosd/demo-minimal-qm-prepared/regular.json \
  --uki build/tmp_baremetal/deploy/images/apollo-qvp/nexios-bsp-initramfs-a.efi \
  --headless --exit-after-pass --timeout 180 \
  --out-dir build/autosd/qbox-efi-first
```

OSTree는 위 명령의 manifest를 `build/autosd/ostree.json`, timeout을 `240`,
out-dir를 `build/autosd/qbox-efi-ostree-first`로 바꾸어 실행했다.

`--uboot`과 `--ukiboot-dir`로 firmware 및 loader/addon 경로를 명시할 수 있다.
UKI 모드에서 `--kernel`, `--initrd`, bootargs의 고정 slot suffix는 거부한다.
원본 disk/UKI는 수정하지 않는다.

## 현재 검사

- 기존 QBox+QEMU launcher 회귀: 51 passed
- 신규 firmware/EFI/재부팅 거부 사례 포함 QBox launcher 시험: 27 passed
- 최종 QBox/QEMU launcher 및 공용 UKI/disk helper 시험: 93 passed
- 실제 U-Boot 입력으로 prepare 수행: 성공, object의 entry literal
  `0x80080000` 확인 (`build/autosd/qbox-efi-prepare-probe/`)
- 변경 후 direct Linux reset payload를 실제 assemble하여 기존 실행의
  `demo-qm-followup-qbox/linux-boot/boot.bin`과 byte-for-byte 일치 확인
  (`build/autosd/qbox-direct-prepare-regression/`)
- 변경 파일 whitespace 검사: 통과

### 별도 direct Linux coldboot 결과

이 EFI 시험과 별개인 `build/autosd/demo-qm-followup-qbox-coldboot/result.json`은
`status=FAIL`, `login_observed=false`, 230.95초를 기록한다. 이를 EFI PASS나
독립 SSH 검사로 덮어쓰지 않는다. 같은 실행의 독립 SSH 검사
`demo-qm-followup-qbox-coldboot-check-ready/`에서는 Enforcing, QM active,
BlueChi 양쪽 node online, 공유 디렉터리 재생성을 확인하여 PASS했다.
이는 해당 SSH 검사 범위의 성공이며 serial 자동 login 판정 성공과 다르다.

## 재부팅 경계

PSCI SYSTEM_RESET 요청 자체는 libqemu에 존재하지만 AP-only Lua의 loader 및
SystemC 장치 전체로 reset이 전달되는 경로는 구현하지 않았다. firmware/DTB
메모리가 guest 실행 후 그대로 보존된다고 가정하지 않는다. 재부팅된
U-Boot banner를 관측하면 supervisor는 `UNSUPPORTED_REBOOT`로 중단한다.
result의 `efi_reboot_support`는 `NOT_IMPLEMENTED`이다. 프로세스 재생성을
native 전체 플랫폼 reset 성공으로 취급하지 않는다.
