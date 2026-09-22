# AutoSD Apollo OTA 후속 검증

## 범위와 합격 조건

공식 `autosd/sig-docs/demos/system_upgrade_rollback`의 순서를 따른다.
base A 부팅 → httpd health check를 추가한 good B로 `bootc switch` →
`/usr/bin/false` health check를 추가한 bad A로 전환 → 실패 부팅 반복 후
good B로 **자동** 복귀해야 전체 PASS이다. 수동 슬롯 변경이나 재부팅만으로
OTA/rollback PASS를 선언하지 않는다.

공식 manifest와 두 patch를 먼저 적용하고 Apollo target/kernel/repository
설정만 덧붙인다. 모든 이미지의 실제 커널 release는
`6.18.5-rt3-yocto-preempt-rt`이며, RPM EVR `6.18.5-1`과 구별한다.
빌더는 ARM64 full-system VM(`127.0.0.1:2226`), OTA 대상은 별도 포트
`2228`을 사용한다. 원본 nightly, 공유 Yocto 빌드, 호스트 binfmt는 변경하지 않는다.

로컬 unsigned kernel RPM과 OCI 파일 전송을 사용하는 기능 검증이다.
Secure Boot, 배포용 서명·원격 registry 인증, 전원 차단 원자성 및 실제 하드웨어
watchdog 동작까지 검증한 것으로 확대 해석하지 않는다.

## 실행 상태

**PASS — 2026-09-23, QEMU Apollo native EFI에서 base→good 업데이트와
bad health 실패 7회 후 good 자동 rollback을 실제 검증했다.**

| 단계 | 실제 관찰 | 증거 (`build/autosd/demo-ota-followup/` 기준) |
| --- | --- | --- |
| base A | EFI/OSTree, health 성공, SELinux Enforcing | `base-state/`, `base-slot-a/` |
| good B | httpd active, 새 digest 부팅, 슬롯 성공 표시 | `stage-good/`, `good-state/`, `good-slot-b/` |
| bad A | 실패 health 7회, tries 7→6→5→4→3→2→1 | `stage-bad/`, `rollback-history/`, `target-native-session/linux-uart.log` |
| 자동 복귀 B | 이전 good digest·슬롯 바이트 그대로, health/httpd 정상 | `rollback-state/`, `rollback-slot-b/`, `verification-final.json` |

최종 boot ID는 `81149747-600b-42e1-9077-171629c2cb32`이며,
bootc의 `bootOrder=rollback`, `rollbackQueued=true` 상태에서 **booted** digest가
기존 good digest와 정확히 일치한다. bad 배포는 비부팅 배포로 남아 있으며
삭제했다고 주장하지 않는다. A는 priority=15/tries=0/successful=0으로 소진됐고,
B는 priority=14/tries=0/successful=1이므로 부팅 가능한 정상 슬롯으로 선택됐다.
gcc와 실패 health drop-in은 복귀한 `/usr`에서 없고 httpd는 active이다.
각 실패 boot ID의 journal에 `status=1/FAILURE`가 있으며 UART에는 각 실패 뒤
`systemd-shutdown[1]: Rebooting.`이 있다. bad 적용 직후의 최초 재부팅 1회 외에
수동 재부팅, 슬롯 변경, 성공 플래그 조작 또는 health 우회를 하지 않았다.

bad 빌드는 2574.92초 후 exit 0이며 OCI digest는
`3d28d65fb34c3d0b2dbf18d7424fc88a23cd46d3da6690bcabdb489b0cd8bdf5`,
419,181,568바이트 archive SHA256은
`56256b904c7c15ed691e3fd7b8b82caa25cb01c21aca0185ef971d1bf96d132d`이다.
소진된 슬롯 A의 실제 initramfs SHA가 bad OCI와 일치하며, 정상 슬롯 B의
전체 128 MiB SHA는 good 부팅 때와 rollback 후 동일하다.

good 공식 AIB 빌드는 2333.05초 후 exit 0이며 OCI digest는
`4c414b42e753fc4763c0cd2184975ae443267b440b4310b084759bd04e4317b4`이다.
아카이브 SHA256 `73a566df0fc2c038b66299ee0f671c0bc7e5a0f2f6eb9be1281a88a1c7a20129`를
builder/전송/target에서 대조했다. `stage-good/`은 실제 `bootc switch`
성공과 staged digest를 기록하고, 정상 재부팅 한 번 뒤 `good-state/`에서
새 boot ID `bb92b8e9-3ba5-4783-9493-9cbca8bfcec8`, 같은 booted digest,
slot B(1) priority=15/tries=0/successful=1, httpd active, gcc 미설치,
health/success 각각 active, SELinux Enforcing을 확인했다.
실제 `/proc/cmdline`과 UART에서 `loglevel=7 systemd.show_status=yes`가
적용됐고, 설치된 ESP baseline loader 해시는 업데이트 전후 동일하다.
bad도 동일한 공식 AIB 경로로 빌드했으며 수동 rollback/슬롯 전환은 수행하지 않았다.

Fresh AIB base의 실제 native EFI 부팅과 상태 검증은 PASS했다.
`convert-base/result.json`은 디스크 변환 exit 0(2015.62초),
`transfer-base.json`은 1,727,266,816바이트 QCOW2의 양단 SHA256
`443cf4925fedc672ded99e6f45c8a7be29530b892b930df7e21bcc305b8c5a79` 일치를 기록한다.
`target-native-session/`은 UKI A/B와 bootctl을 보존하고 ESP의 로더만
Apollo baseline으로 교체한 private disk다. 최초 공식 `X` 초기 bootctl은
UKIBoot가 정상 초기화했으며 invalid CRC 오류는 발생하지 않았다.
`base-state/`에서 EFI, OSTree, SELinux Enforcing, Apollo kernel,
각 health/success unit active, slot A(0) successful=1/tries=0과
기대 base OCI digest `6944a8a7…`를 확인했다.
설치된 ESP loader SHA256은 `8c1822d7ea68c75a51b397cc2a388a81c5d3b8fad9fcfea11a0e05ca242ede51`이다.
변환기는 기본 GRUB 설치를 보고했지만 native 슬롯의 실제 명령행에는
Apollo `console=ttyAMA0 earlycon=pl011,0x1a400000`이 그대로 유지된다.
good 이미지는 기존 build-tools `05a6b249…`를 실제 재사용하여 빌드했다.
`base-slot-a/inspect.json`은 게스트의 슬롯 전체 SHA를 전송 양단에서 대조하고,
내장 `.linux` SHA `9f953c06…`와 현재 배포 Image의 일치를 확인했다.
`base-runtime-contract/`에는 실제 `FailureAction=reboot-force`,
`boot-complete.target` 이후 `ukibootctl mark-successful` 실행 관계를 기록했다.
`good-slot-b/inspect.json`에서도 `.linux` SHA가 동일하며 실제 UKI `.cmdline`의
`loglevel=7 systemd.show_status=yes`를 확인했다. 슬롯 B 전체 SHA는
`9a39f8d1c96c4b1eaea5db6b1852e0a5c0b7ed8c36d6380142d6a550f505c5f4`이다.

- 기존 private ARM64 builder root/scratch를 복사 없이 재시작했다.
- native `aarch64`, SELinux Enforcing, scratch 18 GiB 가용을 확인했다.
- 공식 good/bad patch 적용과 원본 SHA 기록을 완료했다.
- Apollo kernel RPM 및 수정된 AIB를 builder 전용 `/srv/aib/ota`에 배치했다.
- base bootc OCI가 생성됐고 대상에 `kernel-apollo-6.18.5-1.aarch64` 및
  `sysboot-0.1.2-1.el10iv`가 포함됐다. QCOW2는 helper 준비 후 변환했다.
- 현대 `aib build`의 disk 변환에는 별도의 distro-matched `aib build-builder`
  이미지가 필요하다. 기존 regular QM 빌더에 이 이미지는 없으므로 OCI 생성과
  helper 생성, disk 변환을 분리해 순차 실행했다.
- base osbuild 전체 pipeline 및 OCI archive 생성은 성공했다. 실제 dracut 및
  UKI/aboot 생성에서 Apollo의 정확한 kernel release를 확인했다.
  전체 `build ... OCI QCOW2` 명령은 예상한 helper 부재로 4008초 후 FAIL이며,
  이를 OCI 성공과 구별한다. 완성된 `base.oci.tar`는 334 MiB이며 재빌드하지 않는다.
  SHA256: `7436c8b3786bfbc268df8fc645340bf4c8d6b321f84aca1247ab80ea70168df4`.
  OCI image digest: `6944a8a7ab01eca371e9e9105494d23ac0395ca552036bffe5f2b21c87cf2714`.
  OSTree commit: `5b1dc90a2dd83d290eb3188949c030829c5c014b93e2ddbdfe7bec536357383b`.
- temporary container cleanup의 cross-device rename 경고도 보존했다.
  이후 AIB temporary storage를 persistent nested store 하위로 옮겼지만,
  디스크 변환 cleanup에서 overlay link의 cross-device rename 경고가
  재발했다. 이 경고의 해결을 주장하지 않으며 실제 명령 종료 상태와
  산출물 해시를 별도로 확인한다.
  별도 distro helper 생성과 container store 등록은 5476.41초 후 PASS했다
  (`build-helper/result.json`, exit 0). `localhost/aib-build:autosd10-sig`를
  이용한 base 디스크 변환을 완료했으며, base build-tools checkpoint
  `05a6b249…`가 여전히 cache에 남아 있음을 확인했다. helper OCI digest는
  `2e723d4ad613b304711b2ad658be7e33d2aeddc6be7948116529db86a4700505`,
  OSTree commit은 `853d004a96d395488d3d77508b76a4d6ef7536c35ab4d8e6c4187556744fe928`이다.
- host에서 OCI의 모든 blob checksum을 검증했다. `arm64`, `containers.bootc=1`,
  `ostree.linux=6.18.5-rt3-yocto-preempt-rt` 및 실제 vmlinuz SHA가 현재 배포
  Image와 일치한다. `base-archive/inspect.json`에 initramfs, bootc install
  설정, health check, packaged EFI loader 해시를 함께 기록했다.

## 부팅 로그 정책

AIB가 manifest의 `systemd.show_status=yes` 뒤에 고정된
`systemd.show_status=auto`를 붙이는 것을 생성된 base osbuild manifest에서
확인했다. 기본 변수 `systemd_show_status=auto`를 추가하고 Apollo target만
`yes`, `kernel_loglevel=7`로 설정했다. 다른 target 기본값은 유지한다.
관련 kernel release/simple/reproducible/logging 집중 테스트 148개가 통과했다.
실행 중인 base의 입력 사본은 변경하지
않았으며, 이 설정은 good/bad 빌드에 적용했다. good의 실제 UKI와 런타임에서
`loglevel=7`/`systemd.show_status=yes` 및 상세 UART 로그를 확인했다. OTA 검증의 base는
AIB native UKI/boot-control 상태를 보존하므로 초기 payload에는 기존
`loglevel=4`/`systemd.show_status=auto`가 남는다. 기존 Yocto UKI 적응형
launcher의 두 슬롯 덮어쓰기는 이번 native OTA 검증에 사용하지 않는다.
good/bad 최종 OCI와 실제 슬롯 및 UART에서 logging 설정을 확인했다.

공식 문서의 Containerfile layering도 검토했으나 이번 base는 dnf가 없고,
AIB의 `ostree.preptree` 단계는 `/var` 디렉터리·계정·tmpfiles를 변환한다.
단순 RPM installroot/commit은 업데이트 시 httpd의 상태 디렉터리를 보존하지
못할 수 있으므로 실행하지 않았다. 세 이미지 모두 원래 AIB 경로를 유지한다.

## 재현 도구와 증거

guest gate는 `sysboot-health.target`과 `ukiboot-set-success.service`의
활성 상태를 각각 검사한다. 다중 인자를 받는 `systemctl is-active`의
"하나라도 active이면 성공" 동작 때문에 발생할 수 있는 잘못된 통과를
리뷰에서 제거했고, 두 종류의 부분 실패 및 전체 성공을 검사하는 테스트
3개가 통과했다(`ota-helper-tests.xml`). 이후 잘못된 staging 입력 거부 및
불완전한 실패/tries/복귀 시퀀스 거부를 추가해 최종 **10개 PASS**를 기록했다
(`ota-helper-tests-complete.xml`). 이 gate만으로 자동 rollback을
입증하지 않으며 최종 판정 도구가 UART, journal, bootc digest와 슬롯 SHA를
교차 확인한다.

- `scripts/autosd_demo/ota_builder_resume.py`: 기존 중지된 private builder 재시작.
- `scripts/autosd_demo/ota_make_manifests.py`: 공식 patch 적용 후 Apollo profile 추가.
- `scripts/autosd_demo/ota_build_guest.sh base|good|bad|builder|convert`: native ARM64 AIB 실행.
- `scripts/autosd_demo/ota_transfer.py`: base 회수 또는 builder→target OCI 직접 전송 및 SHA 확인.
- `scripts/autosd_demo/ota_check_guest.sh`: kernel/EFI/OSTree/SELinux/health/slot 확인.
- `scripts/autosd_demo/ota_stage_guest.sh`: 정상 슬롯·health·SHA를 확인하고
  `bootc switch` 전후 digest/bootctl/ESP 해시를 기록한다. 재부팅은 하지 않는다.
- `scripts/autosd_demo/ota_inspect_oci.py`: 실행·파일 추출 없는 OCI blob 및 kernel/boot 설정 검사.
- `scripts/autosd_demo/ota_capture_slot.py`: 업데이트/부팅 완료 후 guest 슬롯을 SSH로
  읽기 전용 회수하여 실제 native UKI kernel SHA와 `.cmdline`을 확인한다.
- `scripts/autosd_demo/ota_verify_evidence.py`: 10개 boot ID, 7개 실패 부팅,
  순차 tries 감소, good digest 복귀와 슬롯/ESP 보존을 교차 검증한다.
- `build/autosd/demo-ota-followup/preflight-2/`: builder 재시작 확인.
- `build/autosd/demo-ota-followup/manifests/`: 최종 manifest와 공식 입력 SHA.
- `build/autosd/demo-ota-followup/build-base/`: 실제 base 빌드 로그.

처음 SSH 연결은 서비스 준비 전 실패했고 `preflight/`에 보존했다. 재시도
`preflight-2/`에서 정상 연결과 파일시스템 상태를 확인했다. 모든 출력은
private 복사본 또는 전용 작업 경로이며 외부 registry push는 하지 않는다.

### 재검증 명령

```sh
python3 scripts/autosd_demo/ota_verify_evidence.py \
  build/autosd/demo-ota-followup /tmp/apollo-ota-verification-new.json
python3 -m pytest -q tests/test_autosd_ota.py
```

결과 파일은 기존 파일을 덮어쓰지 않는다. 테스트 이미지는 localhost 전용
root/password 시험 계정을 포함하므로 배포용 이미지로 사용하지 않는다.
본 OTA 시퀀스는 QEMU에서 검증했다. QBox의 별도 EFI 부팅 PASS를 이 OTA
시퀀스의 QBox 실행 PASS로 확대하지 않는다. overlay cleanup 경고는 보존된
제약이며, 원격 인증·서명·전원 차단 및 실제 하드웨어 검증은 별도 범위다.

검증 종료 후 target(2228)과 builder(2226)를 정상 poweroff했으며 두 QEMU
프로세스 종료를 확인했다. private disk/cache/OCI/로그는 모두 보존했다.
종료 후 UART SHA256은
`891022a763c629ccd75bd184be2e5a0fc814031148d2325523e71c8d43f37045`이며,
`verification-final.json`은 이 최종 로그를 대상으로 PASS했다.
회수한 base QCOW2의 `qemu-img check`도 오류 없이 통과했다.
