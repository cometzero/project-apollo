# Automotive Yocto 커널 RPM 전환 검증

상태: **빌드·부팅·대표 시나리오 검증 완료**. 실행하지 않은 범위는 아래에 구분한다.
계획은 [전환 계획서](automotive-rpm-aib-migration-plan-ko.md)를 참조한다.

사용자 요청으로 장시간 진행하던 qemu-user 커널 컴파일을 중단하고 Yocto 바이너리
RPM 패키징으로 전환했다. 부분 컴파일 결과는 `build/autosd/rpm-source-run/`에
보존하며 최종 이미지의 커널로 사용하지 않는다. 작은 사용자 공간 ARM64 빌드는 유지한다.
중단 실험의 관측 구간은 00:56:59~06:34:33 KST, 약 5시간 37분이다.
종료 시각은 마지막 로그 수정 시각 기준이며 설정·smoke·작은 payload·재시작 시간이
포함돼 순수 커널 compiler 시간과 다르다. 이 시간 안에 최종 커널은 완성되지 않았다.

## 현재 확인된 결과

| 항목 | 상태 | 근거 |
|---|---|---|
| AArch64 binfmt | PASS | 호스트 qemu-aarch64 등록, POF flags |
| Podman | PASS | rootless Podman 및 허용된 `sudo -n podman` 확인 |
| 펌웨어 전용 빌드 | PASS | 3,362 tasks, 3,314 cached; 플랫폼 `.qboxconf` 별도 배포 |
| 펌웨어 입력 hash binding | PASS | 부팅/reset에 사용되는 9개 입력 검증; BL2 ELF/RSE provisioning 포함 |
| 펌웨어 의존성 분리 | PASS | graph 270 recipes, Linux/제품 OS/외부 모듈/PFDI 사용자 공간 recipe 없음 |
| Yocto 입력 CLI/AIB 회귀 검사 | PASS | UKI/cache 수정 후 관련 검사 46 tests; 실제 부팅 증거와 구분 |
| Dashboard UI 회귀 | PASS | node test 36개 및 브라우저 결과표/timerlat histogram/osnoise 시계열 SVG 확인 |
| ARM64 빌드 컨테이너 | PASS | glibc-static 누락을 CRB로 해결; image `312263352b22` |
| qemu-user 커널 컴파일 | STOPPED_USER_REQUEST | 실제 컴파일 도중 사용자 방향 변경; 최종 Image/RPM 미생성 |
| Yocto 커널·외부 모듈 준비 | PASS | 1,186 tasks, 1,182 cached; virtual/kernel 및 HIPC/PFDI 모듈 |
| Yocto 바이너리 RPM 패키징 | PASS | 278개 모듈(외부 3종 포함), ABI/서명/depmod/payload 및 반복 RPM SHA 검증 |
| PFDI 사용자 공간 | PASS/제한 있음 | ARM64 빌드·RPM 및 guest CPU0~3 OK 관측; stub·EBUSY 경고 보존 |
| workload/latency-probe | BUILD_PASS | ARM64 정적 바이너리 생성; OCI 조립 smoke PASS |
| Automotive manifest 해석 | PASS | 진단용 vendor kernel로 Root/QM/RT/BlueChi/OCI 및 native/ARM64 compose 확인; disk 생성 없음 |
| 선택 manifest 정책 보존 | PASS | 추가 파일·권한·디렉토리·OCI 병합, 충돌 거부 및 minimal SSH 계약 검사 11개 |
| RPM 메타데이터 복구 | PASS | 실제 ARM64 PFDI RPM으로 repodata 누락·손상 복구, RPM hash 불변; 단위 검사 4개 |
| Yocto RPM 캐시 | PASS | 최종 native helper로 repodata 손상 복구, RPM hash 불변, 컴파일 재실행 없음; 관련 검사 3개 |
| readiness 회귀 | PASS | QM degraded 거부·SSH retry·전체 probe 예산; 관련 66 tests 및 실제 자동 health 통과 |
| Automotive 디스크 조립 | PASS | AIB exit 0, qemu-img check 및 GPT/UKIBoot control 검사 통과; UKI 아키텍처 결함 별도 |
| Automotive UKI 아키텍처 | PASS | 수정 이미지의 EFI loader/UKI/내장 커널 ARM64 검사, 관련 8 tests 통과 |
| QBox 펌웨어·Linux 부팅 | PASS | 네 도메인 부팅·Linux login marker 및 HIPC endpoint 연결 관측 |
| Guest readiness | PASS | 수정 후 새 full startup 자동 판정 PASS, boot-1 receipt와 현재 boot ID 연결 확인 |
| Automotive health 직접 실행 | PASS | 58.44초, Enforcing·BlueChi online·ADAS/QM/nested heartbeat·CPU 분리·Safety HEALTHY |
| Automotive S01~S06 | PASS | 최종 OS 30d5bd08, platform 4ffbdb60; 실제 ADAS fault/latch/recovery 포함 |
| 대표 RT·mixed-criticality·watchdog | PASS(범위별) | R02/R06, timerlat/osnoise 수집, MC02, WD01/WD04 reset·복구 통과 |
| 정상 Power off | PASS(QBox 모델) | platform 7857c89c: AP0~3·cluster OFF, IRQ ack/readback, warm-resume/ASSERT 없음 |
| 일반 Reboot | PASS | 새 boot epoch 3 및 readiness 복구; job 4cd92aca15e741538fc6baae0956e038 |
| minimal QM 이미지 | PASS | 최종 DHCP/ESP 정책 및 ARM64 UKI/hashguard 검사 통과 |
| minimal QM 부팅 | PASS | image f4df06b5 + platform 7857c89c; full boot/preinstalled readiness/자동 minimal health, validator exit 0 |

Readiness는 SSH channel 개설도 startup 예산 안에서 재연결하도록 수정했다.
정상 Automotive health가 58.44초 걸려 기존 probe별 30초 제한에 잘리는 문제도
수정했다. remote 전체 180초·host 전체 360초 제한은 유지하며 관련 테스트 66개가 통과했다.
현재 실제 실행 결과는
`build/qbox-apollo-qvp/autosd-yocto-rpm-validation-checks/interim-runtime-summary.json`에 모은다.

펌웨어 빌드의 warning 2건은 기존 QBox do_check/do_populate_sysroot의 강제 실행 taint이다.
컴파일/QA 오류는 아니며 taint를 지우거나 경고를 숨기지 않았다.

펌웨어 증거는 `build/autosd/firmware-only-validation/`의 `build.log`,
`platform-build.log`, `graph-result.json`, `pn-buildlist`, `task-depends.dot`에 있다.
ARM64 컨테이너 준비 로그는 `build/autosd/rpm-source-run/builder.log`에 있다.
메타데이터 복구 증거는 같은 디렉토리의 `metadata-repair.log`와
`metadata-repair-test/`에 있다. 기본 AIB builder 참조는 검증한
`sha256:37ce37564e1c76b6db707aa53800a77e112dfdc6167a2da77f93d4ce679f548f`
로 고정했다(현재 Ubuntu x86_64 호스트용).

## 입력과 구현 범위

- 새 진입점: `build_autosd.sh`; 기본 Automotive, 옵션 `--minimal`.
- 커널과 모듈은 Yocto에서 빌드한 바이너리를 native RPM 도구로 패키징한다.
- PFDI 소스는 `autosd/pfdi` submodule의
  `ff9b4e4e73bf2349be76161c795ef3efb02725c1` revision을 사용한다.
- 패키징은 기존 Yocto 모듈 서명을 보존한다. 제품 서명 체계 qualification을 의미하지 않는다.
- Native AIB는 x86_64에서 실행하고 완성 이미지의 UKI·ESP를 생성한다.
- 새 manifest의 런처는 UKI/ESP 교체나 모듈 설치를 하지 않고 부팅 readiness를 확인한다.

커널 release는 `6.18.5-rt3-yocto-preempt-rt`, RPM version-release는
`6.18.5-1.2bc46aa3b5a8`이다. kernel RPM SHA256은
`ea72e9edf711b11baa8705b399dd3e421e350b8432150b434eb00b9572d006ee`이다.
최종 receipt와 입력 hash는 `build/autosd/rpm-yocto-v2/result.json`에 기록됐다.
이미지는 `build/autosd/automotive/rootfs.img`(8 GiB raw)이며 SHA256은
`30d5bd08a3008ccf56bec8b2a818fa46409ac47f4497e507b9cfdfa5ac92be08`이다.
선택 manifest는 같은 디렉토리의 `regular.json`이다. 첫 x86_64 UKI 산출물은
`build/autosd/automotive-failed-x64-uki/`에 보존했다. 기본 경로에는 ARM64 UKI와
HIPC 자동 DHCP 방지·ESP umask0077 정책을 적용한 최종 이미지를 게시했다.
최종 30d5bd08 이미지와 수정 펌웨어 조합에서 부팅·자동 health·CPU1 offline/online이 통과했다.
첫 TF-A 수정만 적용한 종료는 runner PASS와 달리 PPU 상태가 실패했다.
최종 7857c89c 펌웨어에서는 4 CPU 부팅·hotplug·모든 AP 코어와 cluster OFF가 통과했다.
실제 Dashboard의 Feature 01/02 PASS 표시도 확인했다.
위 정적 검사나 펌웨어 빌드 결과를 AutoSD 런타임 PASS로 해석하지 않는다.

Guest에서 PFDI CPU 0~3의 OK 출력은 확인했지만 firmware stub 경고가 있어 실제
하드웨어 고장 검출 qualification으로 해석하지 않는다. Vanilla crun의 cgroup2
mount 경고는 앱 정상 상태와 함께 관측됐으며 SELinux는 Enforcing을 유지했다.

진단용 compose는 `build/autosd/automotive-compose-diagnostic/`에 보존한다.
최종 이미지에 진단용 vendor kernel을 대체 입력으로 사용하지 않는다.

Yocto 커널 갱신 로그: `build/autosd/yocto-kernel-repack-validation/yocto-build.log`.
기존 `do_configure`/`do_compile` 강제 실행 taint warning 2건이 있었으며 전체 task는 성공했다.

## 이미지 조립 중 발견한 결함

첫 AIB 실행은 QM의 `/usr/share/qm/contexts` 복사 단계에서 실패했다.
ARM64 target build에는 `qm` RPM이 있었지만 중립 native build에는 빠져 있었다.
Native 도구 manifest에도 QM 정책을 포함하도록 수정하고, 커널/target 정책은
그대로 분리했다. 재시도에서 QM 설정 복사와 QM checkpoint 생성이 통과했다.
실패 로그는 `build/autosd/automotive-yocto-build.log`, 재시도 로그는
`build/autosd/automotive-yocto-build-retry.log`에 보존한다.

이후 rootfs RPM transaction에서 `apollo-pfdi`와 배포판 `filesystem` 패키지의
`/usr/bin`, `/usr/lib`, `/usr/lib64` 충돌을 발견했다.
배포판은 공용 디렉토리를 0555로 소유하는데 PFDI가 0755로 다시 소유한 것이 원인이었다.
패키지 전용 경로만 소유하도록 수정했다. 실제 ARM64 filesystem RPM과의
transaction test에서 구 RPM의 충돌(exit 2)을 재현했고 새 RPM은 통과(exit 0)했다.
증거는 `build/autosd/rpm-yocto-v2/transaction-test{,-old-regression}.log`에 있다.
수정 RPM으로 `automotive-yocto-build-v2`에서 이미지 조립이 성공했다.
런타임 증거는 `build/qbox-apollo-qvp/autosd-yocto-rpm-validation/`에 기록한다.

실제 첫 QBox full 부팅은 RSE/SI 및 AP의 TF-A/U-Boot/UKIBoot까지 도달했다.
UKIBoot가 boot-control을 초기화했지만 UKI의 PE machine이 ARM64가 아닌
`0x8664`(x86_64)여서 LoadImage가 거부됐다. Native AIB가 host EFI stub를 선택한
문제로 확인했다. Target rootfs의 ARM64 stub를 명시하는 UKI 생성 단계와
오프라인 PE 아키텍처 검사를 추가했다. 검사 테스트 8개가 통과했고 실패 이미지에서
UKI 0x8664 거부를 재현했다. 같은 이미지의 BOOTAA64.EFI는 ARM64여서 원인을
UKI로 구분했다. 수정 이미지 재빌드는 `automotive-yocto-build-arm64-uki`에서 성공했다.
`image-architecture.json`에서 loader/UKI가 모두 0xaa64이고 B 슬롯은 정상 빈 상태임을 확인했다.
UKI 크기는 43,514,368 bytes로 슬롯 128 MiB 이내다.
디스크/GPT 검사 통과를 Linux 부팅 PASS로 해석하지 않는다.

## 정상 종료 결함

PPU trace에서 core 0/1이 terminal WFI 이후 `dynamic-power-off → warm-resume`로
전이하며 cold loader 없이 BL2를 재진입하는 것을 확인했다. TF-A의 Apollo QVP
hook이 SYSTEM_OFF/RESET/RESET2 및 secondary 종료 경로에서 기존 SCP core OFF
요청을 보내도록 수정했다. SCP의 OFF_LOCK 계약을 사용하고 상위 cluster는 마지막
SCMI 요청이 끝날 때까지 RUN으로 유지한다. 다른 플랫폼의 기본 hook은 no-op이다.

수정은 TF-A 4파일 27줄이며 firmware-only 재빌드가 통과했다. 새 platform manifest
SHA256은 `4ffbdb60765ed9045ea9ff82fcdf58b06b029fe52cd2e32fe1bc155e15c681da`이다.
최종 정책 이미지에서 BL2 assertion은 해소됐으나 SCP의 비동기 요청 큐가 OFF_LOCK을
적용하기 전에 SCMI 응답을 반환하는 경쟁이 남았다. core2/3의 warm resume 후 최종
ON 상태를 확인해 arming-before-ack 보완을 추가했다. AP 코어 OFF와 실제 PMIC
rail-off를 구분하며 물리 전원 차단을 검증했다고 주장하지 않는다.

SCP 보완은 PD enqueue 성공 뒤 Apollo QVP의 secure PSCI/AP core/core-only OFF
요청만 동기 arm하고 그 뒤 SCMI ACK를 반환한다. PPU 단위 테스트 34개와 정책
테스트 11개가 통과했고 firmware-only 빌드도 성공했다. 최신 platform manifest는
`14261dcb62cf4ffeb0e1af68a83521e1c80ebc39af50cc78e9ad3e9ed4009d58`이다.
CPU_ON·다른 agent·상위 domain OFF는 새 hook 대상이 아니다. 현재 빌드의
HW_ASSISTED_COHERENCY=1에서는 core suspend가 SCMI POWER_STATE_SET을 보내지
않는다. 깊은 idle의 guest-runtime 검사는 `cpuidle.off=1` 이미지에서 NOT_RUN이다.

최종 minimal QM 이미지: `build/autosd/minimal-qm/regular.json`, raw SHA256 `f4df06b59f26c4ab435f3d49e73d8c17683e3c869bc476d1f0ce9e8b50d8fff4`.
Automotive guest에서 ESP 0700, ethsi1 자동 DHCP 없음, QM vanilla crun 1.30.1,
RT 도구 포함 및 failed units 0개를 확인했다. PFDI의 간헐적 EBUSY/coalescing은 원본 로그에 보존한다.

최신 SCP `14261dcb` 부팅에서는 CPU1~3이 online되지 않아 SMP 1 CPU로 진행하는
회귀가 발견됐다. 이 조합은 **FAIL**이며 채택하지 않는다. 초기 secondary OFF의
OFF_LOCK 및 완료 IRQ 처리와 뒤이은 CPU_ON 순서를 조사해 아래의 IRQ 매핑 결함을 수정했다. 기존 `4ffbdb60`과
최종 OS의 4 CPU 부팅·hotplug·S01~S06 증거와 분리한다.

회귀 원인은 SI View1 GIC multiview 소유권 목록에서 AP PPU INTID 260~279가
누락된 것이다. core1 PPU에서 ISR=0x20(DYNAMIC_MIN), IMR=0x1f,
PWSR=0x1100(OFF+LOCK)을 관측했지만 완료 ISR로 진입하지 않았다. Lua 연결과
PPU IRQ 설정은 존재하나 View1의 GIC enable/routing 쓰기가 허용되지 않았다.
이 누락을 수정하고 후속 실행에서 실제 IRQ completion을 검증했다. 회귀 VM도 추가 SSH의 정상
poweroff 명령으로 정리됐으며 boot domain 실패 때문에 실행 결과는 FAIL로 유지한다.

AP PPU IRQ 매핑 수정 후 firmware-only 빌드 3,361 tasks가 통과했다.
새 platform manifest는 `7857c89c81361bcac7996430fd6e3f1bca3f3a9a8550abcf75fa07aea510c1a0`,
SI0 RAMFW는 `8d9e0b53815022e490ede02d7ade84265d4f4b5ff40cd40ec52798d49bff42e0`이다.
매핑 단위 검사에서 AP/CL1 소유권 유지와 PPU 20개 중복 없음을 확인했다.
실제 4 CPU 부팅·종료 검증은 새 실행에 별도로 기록한다.

`7857c89c` 실제 trace에서 core1 OFF_LOCK → dynamic OFF → PPU ISR 0x20
read/ack → OFF 상태 확인 → CPU_ON reset 해제 순서를 확인했다. Linux SMP
4 CPU 부팅이 통과해 `14261dcb`의 초기 secondary CPU 회귀 해소를 확인했다.

최종 `7857c89c` 정상 poweroff는 **PASS(QBox 모델)**이다. AP0~3 모두
OFF_LOCK → WFI OFF → reset assert → IRQ ack → static OFF → PWSR OFF
readback → unlock 순서를 거쳤으며 이후 warm-resume/reset release가 없었다.
cluster도 OFF, secure assertion 없음, RSE shutdown complete 및 runner
POWERED_OFF를 확인했다. 근거는 검증 디렉토리의
`poweroff-final-ppu-review.json`이며 trace line 575~717과 입력 hash를 기록한다.
물리 PMIC rail-off 검증과 구분한다.

## 최종 펌웨어 대표 시나리오

최종 OS `30d5bd08`와 platform `7857c89c` 조합에서 실행한다. RT 기준은
기존 5,000 µs를 유지하며 호스트 빌드를 종료한 상태에서 측정했다.

| 사례 | 결과 | 관측값 |
|---|---|---|
| R02 FIFO | PASS | CPU1, FIFO50, 5초, 4,917 samples; max 1,819.752 µs, p99 1,520.88 µs, 기준 초과 0 |
| R06 cyclictest | PASS | min/avg/max 135/281/1,994 µs; overflow 0; 5,000 µs 이내 |
| timerlat | PASS(수집) | CPU1 IRQ/Thr/Usr max 1,340/3,599/4,005 µs; count 4,336/4,337/4,336; overflow 0 |
| osnoise | PASS(수집) | histogram 14,796개, min/avg/max 2/33.47/1,561 µs, overflow 47; 시계열 553개, max 1,561.4 µs |
| MC02 QM 부하 | PASS | QM CPU 23.49초; ADAS 224 samples/heartbeat 223 advances, 최대 age 0.113초; monitor 12 advances |
| WD01 | PASS | watchdog 기본 상태/동작 사례 |
| WD04 | PASS | 실제 WS0/WS1 만료·reset, 새 boot epoch, health/HIPC 복구 |

위 PASS는 관측 구간의 시뮬레이션 기능·측정 결과이며 물리 하드웨어 RT 보증이 아니다.

실제 브라우저에서 timerlat IRQ/Thr/Usr histogram SVG의 21/48/51개 bar와
osnoise CPU별 시간-latency SVG를 확인했다. WD04 결과표의 PASS도 확인했으며
DOM evidence와 snapshot을 실행 증거에 보존한다.

osnoise의 overflow 47은 histogram 범위를 벗어난 표본 수이며
5,000 µs 기준 초과 건수로 해석하지 않는다. timerlat/osnoise는 수집 검증이며
별도 latency budget qualification PASS를 부여하지 않았다. 사례별 전체 경로와
결과는 `build/qbox-apollo-qvp/autosd-yocto-rpm-validation-checks/scenario-summary.json`에 있다.

Minimal QM 최종 이미지도 platform `7857c89c`에서 full boot와 preinstalled
readiness, 자동 minimal health를 통과했다(validator exit 0). 증거는
`autosd-yocto-rpm-validation-checks/boot-minimal-final/boot.json`과 해당 VM의
`modules.json`이다. Automotive 전용 앱·RT 시나리오는 minimal PASS 범위에 포함하지 않는다.

## 이번 실행에서 제외한 범위

- RT R01/R03~R05, mixed-criticality MC01/MC03, watchdog WD02/WD03의 개별 재검증은 `NOT_RUN`.
- 독립 monitor-mhu 사례, Pause/Resume qualification, 깊은 idle(`cpuidle.off=1`), 실물 하드웨어 timing/PMIC rail-off는 `NOT_RUN`.
- PFDI firmware stub, 간헐적 EBUSY/coalescing 및 vanilla crun cgroup2 경고는 숨기지 않았다.
- 로컬 RPM은 unsigned이며 기존 Yocto 개발용 모듈 서명 보존을 제품 신뢰 체계 검증으로 해석하지 않는다.

최종 서비스 복귀 중 watchdog reset에 사용한 private 디스크의 ESP dirty 상태가
검출돼 오프라인 재사용이 거부됐다(`c823d533` FAIL). WD04 reset·guest 복구 PASS와
별개인 디스크 재사용 경계다. 원본 private 디스크는 보존하고 정상 base 이미지에서
새 실행 복사본을 사용한다. ESP 검사 완화나 자동 수리는 적용하지 않았다.

## 최종 서비스 상태

최종 Automotive 원본의 새 실행 `cdad4d5d0e3345bbb5eb9ca1b2e9a373`에서
boot와 자동 health가 PASS했다. `qbox-full` backend와 서버/VM을 실행 상태로 유지했다.
이미지 `30d5bd08` / platform `7857c89c` binding을 확인했다.
`http://127.0.0.1:8765/`와 `http://192.168.0.13:8765/` 모두 HTTP 200이다.
최종 receipt는 `build/qbox-apollo-qvp/autosd-yocto-rpm-validation-checks/final-service.json`,
전체 사례·metric·제외 범위는 같은 디렉토리의 `scenario-summary.json`에 있다.
