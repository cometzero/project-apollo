# Apollo QVP AutoSD 데모 실행 리포트

검증일: 2026-09-22. 실행 순서: **QM·컨테이너·네트워크 → CPU/IPC/SELinux → BlueChi/iceoryx2 → OTA/rollback**.

이 문서는 최초 실행 단계의 기록이다. 이후 QM 경계 IPC·BlueChi·SELinux·iceoryx2,
QBox 교차 검사 및 OTA 후속 결과는 [잔여 범위 리포트](autosd-remaining-validation-ko.md)를
참고한다. 아래 초기 BLOCKED/NOT_TESTED는 해당 시점의 증거로 보존한다.
2026-09-23 사용자 정리 요청으로 삭제된 중간 디렉터리의 로그·설정·결과는
`build/autosd/cleanup-20260923-evidence.tar.gz`에 보관했다. 디스크 및 중간
바이너리는 해당 archive에 포함되지 않으며, 정확한 목록은 잔여 범위 리포트에 있다.

## 최신 결과 요약

- 해결: nft FIB 커널 지원 및 root 컨테이너 HTTP/DNS/포트 전달.
- 해결: ARM64 full-system AIB로 공식 minimal_qm 이미지 생성, QEMU·QBox QM 실행.
- PASS: 새 커널 regular/OSTree UKIBoot, 유효한 bootctl 및 슬롯 성공 기록,
  디스크 재사용 후 실제 재부팅, QBox root 네트워크·IPC·BlueChi.
- 준비 완료: Apollo 커널 RPM(실제 설치 검증), 로컬 이미지 intake,
  AIB custom kernel release/target 및 bootc manifest compose.
- 남음: QM 경계 IPC·nested container·정책 허용/거부, BlueChi root↔QM,
  iceoryx2 별도 RPM/이미지, Apollo 커널 내장 bootc 이미지의 실제 업데이트·자동 rollback.
- 런처/이미지 처리 115개, AIB 관련 146개 테스트 통과. 호스트 설정 변경·commit·push 없음.

최초 실패 표는 원인 추적을 위해 보존한다. 현재 판정은 이 요약과 후속 보완 절을 따른다.

## 후속 보완: 컨테이너 네트워크 차단 해소

아래 최초 검사 표의 네트워크 FAIL은 후속 수정으로 해소했다. QM·OTA의 최종
판정과 혼동하지 않도록 실패 기록은 그대로 보존한다.

- QVP defconfig에 `CONFIG_NFT_FIB_IPV4=m`, `CONFIG_NFT_FIB_IPV6=m`,
  `CONFIG_NFT_FIB_INET=m`을 추가했다. 생성된 `.config` 및 네 모듈(FIB 공통 포함)을 확인했다.
- `./yocto_build.sh --keep-conf --bsp`: 5,817 task 성공.
  로그: `build/autosd/demo-network-bsp-build.log`.
- 새 UKI로 regular AutoSD를 부팅하고 동일 빌드의 모듈을 안전한 helper로 설치했다.
  설치 증거: `demo-network-new-modules/`.
- SELinux Enforcing에서 **FIB rule, bridge 컨테이너, 호스트 포트 전달,
  컨테이너 DNS 조회, 외부 HTTP 다운로드 PASS**.
  증거: `demo-network-fixed-check-2/console.log`, `result.json`.
  이는 root Podman 네트워크 검사이며 QM nested network 검사는 아니다.
- 첫 수정 후 HTTP 시험은 Alpine에 `httpd`가 없어 실패했다. 커널 실패와 구분하여
  기록하고, 포함된 `nc`를 이용하는 재현 helper `network_guest_check.sh`로 수정했다.

새 산출물 SHA-256:

```text
Image: 9f953c06bbdee67187d4583566546b2272a687bf223196debed0b1855d10a8ab
nexios-bsp-initramfs-a.efi: e4d1c0913c9c541980fa174ed61b213e337b606cb8125c0d37517a984be7076b
modules-apollo-qvp.tgz: 6064199435d73e36440ed8dc0f190af6120174581d8d6b5ea8245a98955d48ad
```

## 후속 보완: 디스크 재사용·재부팅 경로

`run_qemu_linux.sh --reuse-autosd-disk PREVIOUS_OUT_DIR`를 추가했다.
이 모드는 기존 private 디스크를 제자리에서 사용하며 UKI 변환·복사·슬롯 덮어쓰기를
수행하지 않는다. 기존 launch/GPT 증거를 확인하고 원본 이미지·symlink·hardlink를
거부하며 실행 중 exclusive lock을 유지한다. 이 모드의 `--uki`는 슬롯에 새로
설치되는 payload가 아니다. 슬롯의 실제 내용이 다음 부팅 커널을 결정한다.

새 U-Boot banner를 감지하면 이전 로그인/PASS 상태를 초기화하고 EFI loader 명령을
다시 전송한다. 실제 `systemctl reboot` 후 두 번째 U-Boot와 Linux 로그인을 확인했다.

- `demo-reuse-reboot-session/result.json`: firmware boot 2회, 로그인 2회.
- `demo-reuse-before/`: boot ID `2fc37b79-c93c-402b-a037-353b5b6295e5`.
- `demo-reuse-after-ready/`: boot ID `4b120755-ee12-4589-aebe-a6aee59e6813`,
  EFI 존재, ukiboot-set-success active, slot A 성공 확인.
- 재부팅 후 모듈을 수동으로 다시 로딩하지 않고 네트워크 helper도 PASS했다.
- 비-smoke launcher의 `efi_boot_observed=false`/`NOT_OBSERVED`는 자동 probe를
  실행하지 않았다는 뜻이다. 위 SSH 검사의 EFI/service/slot 증거를 별도로 사용한다.

이는 단일 이미지의 재부팅 검증이며 **업데이트·자동 rollback PASS가 아니다**.
재사용 디스크를 보존할 때는 guest에서 sync/poweroff로 종료한다. timeout/중단은
QEMU 강제 종료일 수 있으므로 정상 storage shutdown으로 간주하지 않는다.

```sh
./run_qemu_linux.sh --autosd build/autosd/regular.json \
  --uki build/tmp_baremetal/deploy/images/apollo-qvp/nexios-bsp-initramfs-a.efi \
  --reuse-autosd-disk build/autosd/demo-network-fixed-session \
  --out-dir build/autosd/demo-reuse-reboot-session --headless --timeout 900 \
  --netdev user,id=net0,hostfwd=tcp:127.0.0.1:2224-:22
```

로컬 AIB 산출물을 위한 `prepare_autosd.py --image PATH --mode regular|ostree`도
추가했다. 원본 SHA를 기록하고 별도 raw 사본에서 BLS/initrd를 추출한다.
출력 덮어쓰기와 backing/external-data 의존 이미지는 거부한다.

## 후속 보완: QBox 교차 실행

새 커널과 matching modules가 설치된 private disk를 다시 복사하여
`run_qbox_linux.sh` AP-only 직접 부팅 프로파일에서도 검사했다.
`QBOX_APOLLO_NETDEV=type=user,hostfwd=tcp:127.0.0.1:2227-:22`로 SSH를 분리했다.

- `demo-qbox-network-check/`: FIB/포트 전달/DNS/외부 HTTP, CPU 0 affinity,
  공식 UDS 및 공유 메모리 프로그램, BlueChi root start/stop **모두 PASS**.
- SELinux Enforcing 유지. QM agent는 offline이므로 QM 데모 성공은 아니다.
- 부팅 로그: `demo-qbox-network-session/linux-uart.log`.
- QBox는 여기서 U-Boot/UKIBoot를 사용하지 않는 direct Linux 경로다.
  따라서 이 결과는 QBox UKI/OTA, 전체 firmware, 타이밍·안전 격리 검증이 아니다.

관련 회귀 테스트는 후속 변경 포함 **115 passed (6.24s)**이다.

새 커널의 OSTree UKIBoot 회귀 검사도 **PASS (53.04초)**다.
`demo-newkernel-ostree-smoke/result.json`에서 EFI 부팅, slot A,
bootctl CRC/구조 유효, `successful_boot=1`, ukiboot success service를 확인했다.
이는 AP 부팅 검사이며 OTA·Secure Boot 검증은 아니다.

## 후속 준비: Apollo 커널을 포함한 bootc 이미지

최초 디스크에만 UKI를 주입하는 방식으로는 OTA 후 Apollo 커널 유지가 보장되지
않는다. 이를 위해 별도 `kernel-apollo` RPM과 AIB 연결을 준비했다.

- `scripts/autosd_demo/kernel_rpm_build.sh`: 배포된 Image와 matching modules를
  검증해 ARM64 RPM 및 로컬 repository를 만든다. host 패키지는 설치하지 않는다.
  최종 결과는 `build/autosd/demo-kernel-rpm-v5/`이며 RPM SHA-256은
  `429d8f902ce55d9cde79676f9118b293f840acdeae7bf77ac6d0431323d10884`다.
  모듈 275개의 ELF/vermagic, payload digest, depmod 결과 및 반복 빌드 해시 일치를 확인했다.
- RPM EVR은 `6.18.5-1`이고 실제 uname은 `6.18.5-rt3-yocto-preempt-rt`다.
  이를 혼동하지 않도록 AIB에 선택적 `kernel.uname_r` 필드를 추가했다.
  생략하면 기존 EVRA 기반 경로를 그대로 사용한다. **이 필드는 workspace의
  로컬 AIB 확장이며 배포된 upstream AIB에 이미 있는 기능이 아니다.**
- `targets/apollo-qvp.ipp.yml`은 virtio-MMIO storage를 선택한다. 일반 qemu
  target의 `nvme_common`은 현재 Apollo 6.18 modules.builtin에 없으므로 요구하지 않는다.
- `apollo_kernel_image.aib.yml`은 SSH·정상 health check를 포함한 bootc 후보 manifest다.
- 실제 AIB compose 성공: `demo-kernel-compose/apollo-kernel.osbuild.json`의
  `org.osbuild-auto.aboot.update.kernel`이 정확한 Apollo release를 가리킨다.
  dracut driver는 virtio_blk/virtio_mmio, 추가 driver는 erofs/overlay/loop다.
- 실제 regular 게스트 RPM 설치·`rpm -V`·vmlinuz SHA 일치·네트워크 재검사 PASS:
  `demo-rpm-install-check/` (59.34초). 기존 UKI 커널과 동일한 payload를 설치한
  검사이며, AIB가 생성한 새 bootc 이미지로 부팅한 검사는 아니다.
- AIB 변경 관련 테스트: **146 passed (1.87s)**.
- 재현: `bash scripts/autosd_demo/aib_compose_kernel.sh RPM_REPO NEW_OUTPUT_DIR`.

`demo-ota-runtime-contract/console.log`에서 aboot hook은 전달받은 kernel release를
사용하는 것을 확인했다. versioned `kernel-uname-r` RPM Provides가 필수라는 증거는
없었으나, 이것만으로 실제 bootc 업데이트 호환이 검증된 것은 아니다.
이 RPM은 개발용 unsigned 패키지이며, compose는 이미지 빌드·부팅·OTA PASS가 아니다.
향후 다른 커널 payload를 배포할 때에는 동일 NEVRA를 재사용하지 말고 Release를 올려야 한다.

로컬 raw 이미지 입력의 실제 검사도 완료했다:
`demo-local-intake/regular.json`에서 원본/출력 SHA가 동일하고 BLS/initrd 추출이 정상이다.

## 후속 보완: ARM64 full-system AIB builder

x86 호스트의 qemu-user/cross-RPM 경로 대신 Apollo QEMU에서 실제 ARM64 커널로
실행되는 전용 builder VM을 구성했다. `builder_launch.py`, `builder_guest.sh`,
`builder_fetch.py`를 사용하며, root 디스크 사본과 24 GiB scratch 디스크를 분리했다.
호스트 패키지·binfmt 설정은 변경하지 않았다. privileged AIB 컨테이너는 이 전용
게스트 내부에서만 실행하며 호스트 Docker socket이나 호스트 파일시스템은 노출하지 않는다.

- 입력: 공식 `demos/minimal_qm/minimal_qm.aib.yml` 원문.
- ARM64 builder digest: `179a58db45306498791d2011b7cbd4d5e20ace29d7e9d51e95bb987c98027c36`.
- 실제 mount/PID namespace 생성 및 ARM64 RPM 설치 성공.
- build, qm_rootfs_base, qm_rootfs, extra-tree-content pipeline 완료.
- 전체 AIB 빌드 **PASS (3,679.73초)**. 최종 qcow2 1,135,214,592 bytes, virtual 8 GiB.
  `minimal_qm.aarch64.qcow2` SHA-256:
  `045bafc9b9fd61c92767675d88f5a1a5bd390287f218953968dc3c4a5a2a9902`.
  게스트/호스트 해시 일치 및 `qemu-img check` 오류 없음 확인.
- 로그: `demo-builder-fullsystem/build-attempt-6/console.log`.

앞선 두 builder 경로의 실패는 이 경로에서 재현되지 않았다. 빌더는 회수 후 정상
poweroff했고 scratch/cache는 보존했다. 상세: `demo-builder-fullsystem/report.ko.md`.
런타임 검사용
`qm_guest_check.sh`는 서비스·컨테이너 실행, 별도 PID namespace, 내부 명령 실행,
SELinux Enforcing을 확인하며 IPC·보안 격리의 완전성·OTA를 대신 검증하지 않는다.

### 공식 minimal_qm 이미지의 Apollo QEMU 실행

`demo-minimal-qm-prepared/`에서 원본 qcow2의 별도 raw/BLS/initrd를 준비했다.
추가 시험용 사본에 kernel-apollo RPM과 검사 helper만 업로드하고 Yocto UKI로 부팅했다.
UART에서 RPM 설치·검증 및 depmod 후 QM을 재시작했다.

- **QM 런타임 PASS**: qm.service active, 컨테이너 running, 별도 PID namespace,
  내부 `/sbin/init`(systemd) 및 명령 실행, SELinux Enforcing.
- 내부 `systemctl --failed`: 0 units.
- EFI 존재, ukiboot success service active, slot A successful_boot=1,
  booted=active 확인. `APOLLO_QM_RECHECK_0` 마커로 전체 명령 성공 확인.
- 증거: `demo-minimal-qm-runtime/linux-uart.log`.
- 최초 검사 마지막에 잘못된 `aboot-bootctl` 명령을 사용해 exit 127이 났다.
  이는 시험 명령 오류이며 올바른 `ukibootctl`로 재검사했다. 최초 로그도 보존했다.
- 시작 시 `SELinux: mount invalid ... cgroup2` 경고가 관측됐으나 위 동작은 성공했다.
  경고 원인 및 보안 정책 허용/거부 전체 검증은 별도 과제로 남긴다.

공식 manifest로 이미지 생성 후 Apollo UKI와 matching modules를 적용한 결과다.
처음부터 Apollo 커널을 포함한 AIB 이미지 빌드나 bootc OTA 검증을 뜻하지 않는다.

### 동일 QM 이미지의 QBox 교차 실행

정상 종료한 QEMU 시험 디스크를 다시 복사하여 QBox AP-only direct Linux로 부팅했다.
별도 모듈 설치·수동 QM 재시작 없이 QM이 자동 기동했다.
`demo-minimal-qm-qbox/linux-uart.log`의 `QBOX_QM_CHECK_0`에서 동일 runtime helper,
별도 PID namespace, 컨테이너 내부 실행, Enforcing 및 내부 failed units=0을 확인했다.
**QBox QM 런타임 PASS**이며 EFI/UKIBoot·전체 firmware·타이밍 검증은 아니다.
두 시험 VM 모두 검사 후 sync/poweroff로 종료했다.

## 최초 검사 결과 (후속 보완 전 기록)

Apollo QEMU에서 AutoSD의 컨테이너 실행, CPU affinity, 공식 IPC 프로그램의
root 영역 통신, BlueChi root 노드 제어를 실제 실행했다. 전체 공식 데모를
완료한 것은 아니다. QM 이미지 생성과 컨테이너 네트워크에서 차단 요인을
재현했으며, QM 경계 통신·iceoryx2·자동 OTA 롤백은 미검증으로 남긴다.
최초 검사에서는 QBox 데모를 실행하지 않았다. 이후 결과는 위의
"후속 보완: QBox 교차 실행"을 따른다. 아래 FAIL/BLOCKED 표는 최초 상태이며
네트워크와 빌더의 최신 상태는 후속 보완 기록과 구분해야 한다.

| 단계 | 실제 검사 | 판정과 범위 | 증거 (`build/autosd/` 기준) |
|---|---|---|---|
| 1 | arm64 Alpine 컨테이너, network=none | PASS: aarch64 실행 및 출력 | `demo-container-root/` |
| 1 | 컨테이너 bridge·포트 18080→8080 | FAIL: bridge 모듈 보완 후에도 nftables rule 적용 실패 | `demo-container-network/`, `demo-network-modules/` |
| 1 | nftables FIB 최소 rule | FAIL: `fib daddr type local` 생성 불가 | `demo-nft-feature/` |
| 1 | QM RPM 설치 및 서비스 시작 | 설치 성공, 실행 FAIL: `/var/qm/tmp` 없음; QM rootfs도 없음 | `demo-install-qm/`, `demo-qm-runtime/` |
| 1 | 공식 minimal_qm manifest 이미지 생성 | BLOCKED: 두 builder 경로에서 실제 실패 | `demo-aib/bootstrap-report.ko.md` |
| 2 | 컨테이너 CPU affinity | PASS: guest CPU 0–3 중 컨테이너 CPU 0만 허용 | `demo-ipc-cpuset/` |
| 2 | 공식 UDS 예제 프로그램 | PASS: root↔root 응답 4회 | `demo-ipc-substrate-retry/`, `demo-ipc-traffic/` |
| 2 | 공식 mmap 공유 메모리 예제 | PASS: 30회 데이터 전달 및 정상 종료 | `demo-ipc-traffic/` |
| 2 | SELinux | Enforcing 유지 확인. custom policy 허용/거부 매트릭스는 NOT_TESTED | `demo-ipc-traffic/`, `demo-bluechi-control/` |
| 3 | BlueChi root 제어 | PASS: `test.service` start→active→stop→inactive | `demo-bluechi-control/` |
| 3 | BlueChi root↔QM | BLOCKED: `host=online`, `qm.host=offline` | 동일 |
| 3 | iceoryx2 root↔QM | BLOCKED: QM 부재 및 demo RPM 미설치. 현재 enabled repo cache에도 없음 | `demo-iceoryx-preflight/` |
| 4 | OSTree/bootc 및 UKIBoot 선행조건 | PASS: bootcHost, booted=active=0, successful_boot=1 | `demo-ota-preflight-retry/` |
| 4 | good update→bad update→자동 rollback | BLOCKED: sysboot/health target와 업데이트 이미지 없음. 실제 switch/reboot 반복은 NOT_TESTED | 동일 |

`guest_exec.py`의 `result.json.status`는 **명령의 종료 코드**만 나타낸다.
진단 명령 묶음의 마지막 명령이 성공해도 전체 데모 PASS는 아니다. 위 표는
콘솔 출력과 서비스/트래픽 결과를 검토한 시나리오별 판정이다.

## 입력과 환경

- AutoSD 10 developer aarch64 nightly: `2869696176.466d2e78`, regular 및 ostree.
- 문서 submodule: `autosd/sig-docs`, `75cb479c89c8ee01350d03ca031a9b780158a99d`.
- 새 builder submodule: `autosd/automotive-image-builder`, `0db5df5f8567f9ea1fbc0772f671e4f87ccfa7cd`.
- Apollo 커널: `6.18.5-rt3-yocto-preempt-rt`, 4 CPU, SELinux Enforcing.
- Yocto `nexios-bsp-initramfs-a.efi`를 AutoSD용으로 변환한 UKI와 실제 UKIBoot loader 사용.
- root Podman `6.1.0-2.el10`, BlueChi `1.3.0-1.el10iv`, QM `1.3-1.el10iv`.
- 호스트 x86_64, Docker 사용. host 패키지·binfmt·Docker daemon 설정은 변경하지 않았다.
- 모든 게스트 변경은 `demo-regular-session/rootfs.wic` 사본에 적용했다.
  원본 `regular.raw`, `ostree.raw`는 변경하지 않았다.

## 1. QM·컨테이너·네트워크

nightly 기본 이미지에는 QM rootfs와 BlueChi가 없다. 게스트에서 서명 검증을
유지한 DNF로 QM·BlueChi 패키지를 설치했지만, QM RPM 설치만으로 AIB가 구성하는
`/usr/lib/qm/rootfs`, `/etc/qm`, `/var/qm`이 만들어지지는 않았다.
QM 서비스 시작은 `/var/qm/tmp` 부재로 실패했고 반복 재시도는 중지했다.

공식 `minimal_qm.aib.yml`을 변경하지 않고 regular 이미지 생성을 시도했다.
이는 공식 run-test의 bootc 이미지·AIR·expect 전체 실행과 구분된다.

1. arm64 AIB 컨테이너 + 기존 qemu-user binfmt: RPM 다운로드 후
   `bwrap: Creating new namespace failed: Invalid argument`.
2. native amd64 AIB + `--arch aarch64`: namespace를 통과했으나 RPM이
   `intended for a different architecture`로 거부했다.

AIB README의 native architecture 제약과 일치한다. 다음 빌드는 native aarch64
호스트 또는 실제 aarch64 커널을 사용하는 full-system builder VM이 필요하다.
다운로드·resolved manifest·로그는 `demo-aib/`에 보존했다.

네트워크에서는 다음 두 층의 문제가 확인됐다.

- Apollo의 `CONFIG_BRIDGE=m` 등 모듈을 AutoSD 파일시스템에 배포하지 않아 최초
  bridge 생성이 `Operation not supported`로 실패했다. 동일 빌드의 모듈을 설치하고
  bridge, nft_ct, nft_nat, nft_masq, nft_reject_inet, nft_limit 로딩까지 확인했다.
- 그 후에도 nftables rule 적용이 실패했다. 별도 `inet` table/chain을 만들고
  `fib daddr type local counter`를 추가하는 최소 검사도 ENOENT로 실패했다.
  최초 검사 시 defconfig에는 `CONFIG_NFT_FIB_IPV4`, `CONFIG_NFT_FIB_IPV6`,
  `CONFIG_NFT_FIB_INET`이 없었다. 후속 보완에서 세 설정을 추가하고 실제
  netavark 트래픽까지 검증했다. `ip_tables`도 당시 모듈에 없었지만
  실제 netavark는 nftables driver를 선택하므로 legacy iptables 활성화로 우회하지 않았다.

모듈 최초 수동 추출 중 Yocto archive의 `lib/` 디렉터리가 AutoSD `/lib` symlink를
대체해 ELF 실행/SSH가 일시 중단됐다. 살아 있는 UART shell에서 dynamic loader를
직접 호출하여 symlink를 복구했다. 재현용 `install_guest_modules.sh`는 archive의
release 경로를 확인하고 `/usr/lib/modules`에만 추출하여 이 문제를 피한다.
커널 release 이름뿐 아니라 같은 빌드 산출물인지 확인해야 한다. 원래 AutoSD의
6.12 모듈을 Apollo 6.18 커널에 섞어 쓰면 안 된다.

## 2. CPU·IPC·SELinux

공식 `ipc_between_qm_root_2`와 `shared_memory_qm_root` C 소스를 수정 없이
static aarch64로 빌드했다. source 및 binary hash는
`demo-ipc-payload/build-provenance.txt`에 기록했다.
UDS 응답 4회, 공유 메모리 payload 30회와 종료 메시지를 확인했다.
UDS client는 의도된 timeout으로 끝내며 server는 작업 PID만 종료한다.

이 검사는 root `unconfined_t` 영역이다. SELinux Enforcing 상태라도
QM 컨테이너 경계와 `ipc_t` 등의 사용자 정책을 검증한 것은 아니다.
CPU affinity는 `/proc/self/status`의 `Cpus_allowed_list: 0`로 확인했으나
실시간 지연, 간섭 격리, CPUWeight 공정성이나 안전성 검증은 아니다.

## 3. BlueChi·iceoryx2

공식 `bluechi_root_qm/conf/`의 controller/root agent 설정과 `test.service`를
사용했다. `bluechictl start host test.service`, `stop`이 실제 서비스 상태를
변경했다. 프로세스는 각각 `bluechi_t`, `bluechi_agent_t`로 실행됐다.
QM agent는 offline이므로 공식 2-node 데모 완료로 표시하지 않았다.

iceoryx2 공식 manifest는 `iceoryx2-demo` RPM, QM 및 `/tmp/iceoryx2` 공유가
필요하고 **SELinux permissive를 명시**한다. 이번에는 Enforcing을 낮추지 않았다.
현재 enabled repository cache에서 RPM이 없다는 관찰은 모든 devel/EPEL 저장소에
패키지가 없다는 뜻은 아니다. 별도 demo RPM 빌드·추가 repo 준비가 필요하다.
공식 `container-build.sh`와 `BUILD.bazel`을 재확인한 결과, 해당 RPM은 예제에서
직접 생성하는 패키지다. 실행 계약은 `publisher`와 `subscriber` 및
`/etc/iceoryx2/iceoryx2.toml`이며, 최초 probe의 `/usr/bin/iox2` 부재는 유효한
실패 기준이 아니다. RPM 미설치 및 QM 부재가 실제 차단 근거다.
ARM64 RPM을 빌드하고 repository를 root/QM 양쪽에 공급한 뒤 공유 경로와
tmpfiles를 구성해야 한다. 공식 PASS 기준은 `Send sample`과
`received: TransmissionData`의 실제 송수신 로그다. Enforcing 유지 검증에는
공식 permissive 예제 실행과 별도로 정책 작업이 필요하다.

## 4. 업데이트·롤백

OSTree 게스트의 `bootc status`는 실제 `bootcHost`를 반환했다.
현재 image digest는 `sha256:d1ee614deaf0f9857468760559c37a051016f2dda7fb7b7b6ecbc2bb77654a76`,
deployment는 `c6da042842823bb2eec1f9dfc61306d13946440fb3110f78e16f72f0d2c708c2.0`이다.
UKIBoot slot A는 priority 15, tries 0, successful 1이며
`ukiboot-set-success.service`가 정상 종료했다.

하지만 `sysboot`와 `sysboot-health.target`은 없고 rollback deployment도 없다.
공식 데모의 base→good update→bad health check→7회 실패→이전 이미지 복귀는
수행하지 않았다. 이전 A/B 수동 슬롯 부팅 검증도 이 OTA 검증을 대신하지 않는다.

최초 launcher는 새 실행 시 양 슬롯 UKI를 준비하고, 자동 재부팅 뒤
U-Boot 입력 상태를 다시 초기화하지 않았다. 후속 보완으로 아래 1번은 완료했다.
OTA 검증에는 나머지 항목이 필요하다.

1. 업데이트 슬롯을 덮어쓰지 않는 prepared-disk 재사용 모드와 reboot 대응.
2. base/good/bad 세 이미지 모두에 Apollo kernel·modules·UKI 계약 반영.
3. sysboot health 판정 및 매 부팅 boot_id/slot/tries/success/deployment 수집.
4. TCG에서 7회 재부팅할 충분한 제한 시간과 실패 로그 보존.

## 재현

프로젝트 루트에서 regular VM을 시작한다. 기존 출력 디렉터리가 있다면 새 이름을 쓴다.

```sh
./run_qemu_linux.sh --autosd build/autosd/regular.json \
  --uki build/tmp_baremetal/deploy/images/apollo-qvp/nexios-bsp-initramfs-a.efi \
  --headless --timeout 10800 \
  --netdev user,id=net0,hostfwd=tcp:127.0.0.1:2224-:22 \
  --out-dir build/autosd/demo-regular-session
```

다른 터미널에서 로컬 테스트 VM에만 사용하는 helper로 실행한다.
기본 sample 계정 root/password를 사용하며 SSH 포트는 localhost에만 노출한다.

```sh
python3 scripts/autosd_demo/guest_exec.py \
  --out build/autosd/my-container-check \
  --command 'set -eu; podman run --rm --network=none alpine:3.22 uname -m'

python3 scripts/autosd_demo/guest_exec.py \
  --out build/autosd/my-module-install \
  --upload build/tmp_baremetal/deploy/images/apollo-qvp/modules-apollo-qvp.tgz:/var/tmp/apollo-modules.tgz \
  --upload scripts/autosd_demo/install_guest_modules.sh:/var/tmp/install_guest_modules.sh \
  --command 'bash /var/tmp/install_guest_modules.sh /var/tmp/apollo-modules.tgz'

bash scripts/autosd_demo/ipc_build.sh
```

IPC payload 네 바이너리와 `ipc_guest_baseline.sh`를 게스트의 같은 디렉터리에
복사하고 실행한다. 세부 업로드·실행 명령은 각 증거 디렉터리의 `result.json`에 있다.
`ipc_guest_cpuset.sh`는 별도로 실행할 수 있다. helper의 timeout은 SSH 채널 종료이며
원격 자식 프로세스 종료를 보장하지 않으므로 장시간 작업에는 원격 `timeout`도 사용한다.

## 다음 권장 순서

1. 완료: nft FIB 지원 추가·빌드 및 matching modules 배포 후 HTTP/DNS/외부 통신 검증.
2. 완료: full-system builder의 공식 minimal_qm 이미지 생성 및 Apollo QEMU QM 부팅 검증.
3. 동일 QM 기반에서 nested container, affinity, IPC, SELinux 허용/거부 정책 검증.
4. BlueChi QM 노드 및 iceoryx2 전용 이미지 검증.
5. OTA 전용 세 이미지를 준비해 자동 rollback 검증. 디스크 재사용·재부팅 대응은 완료.
6. 확장 QM/OTA 시나리오를 QBox에서 재실행. minimal QM 및 root 네트워크·IPC·BlueChi 교차 검증은 완료.

## 검사 및 종료 상태

- `test_autosd_disk`, `test_autosd_uki`, `test_prepare_autosd`,
  `test_run_qemu_linux`, `test_run_qbox_linux`: 후속 변경 포함 **115 passed (6.19s)**.
- AIB kernel release/simple/reproducible 테스트: **146 passed (1.80s)**.
- 새 shell helper 각각 `bash -n`, SSH helper `py_compile`, `git diff --check` 통과.
- 모듈 설치 helper 실제 게스트 실행: `demo-module-helper/`의
  `MODULE_DEPLOYMENT_PASS` 및 `/lib` symlink 유지 확인.
- 최초 두 작업용 VM은 sync 후 poweroff했고 UART의 `reboot: Power down`을 확인했다.
  OSTree 종료에는 남은 loop device finalize 경고가 있었다. 정상 부팅/bootc 선행조건
  판정과 별도로 보존하며, 완전한 storage shutdown qualification을 뜻하지 않는다.
- 재실행 가능한 스크립트·디스크 사본·실패 로그·builder cache는 삭제하지 않았다.

## 근거 문서

- [공식 데모 소스](../autosd/sig-docs/demos/)
- [QM 최소 이미지](../autosd/sig-docs/demos/minimal_qm/minimal_qm.aib.yml)
- [BlueChi root/QM](../autosd/sig-docs/demos/bluechi_root_qm/bluechi_root_qm.aib.yml)
- [iceoryx2 manifest](../autosd/sig-docs/demos/iceoryx2_ipc/image.aib.yml)
- [업데이트/롤백 실제 검사](../autosd/sig-docs/demos/system_upgrade_rollback/run-test.sh)
- [Apollo AutoSD 부팅 지원](autosd-apollo-linux.md)

워크스페이스/Yocto/kernel 스킬의 소유권·실행 증거 기준에 따라 원본 이미지와
외부 문서를 보존하고, 부팅·명령 성공·데모 통과를 분리했다. 커밋·push는 수행하지 않았다.
