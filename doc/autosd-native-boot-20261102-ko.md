# Native 빌드 AutoSD의 QBox full-system 부팅 검증

## 판정

**AutoSD 부팅과 minimal QM 실행은 PASS, 종료를 포함한 전체 검증은 FAIL이다.**
Linux poweroff 이후 AP secure console에 TF-A assertion이 기록됐다. 판정 기준을
완화하거나 원본 FAIL receipt를 PASS로 바꾸지 않았다. 테스트 VM은 종료되어 있다.

| 항목 | 결과 | 근거 |
|---|---|---|
| RSE | PASS | TF-M BL1/BL2, SCP SCMI 연결, AP power-on 표식 |
| SI CL0 | PASS | SCP 시작, 모듈 초기화, GIC multiview 표식 |
| SI CL1 | PASS | Zephyr, PFDI ready, RPMsg ATTACHED 표식 |
| AP AutoSD 부팅 | PASS | TF-A/OP-TEE/U-Boot/UKIBoot → Linux → root 로그인/SSH |
| 커널 | PASS | `6.18.5-rt3-yocto-preempt-rt`, matching BSP 모듈 |
| QM | PASS | 컨테이너 running, Root/QM PID namespace 상이, QM 안의 systemd 실행 |
| SELinux | PASS | guest 검사에서 Enforcing 확인; 경고가 없다는 의미는 아님 |
| UKIBoot | PASS | active/booted 슬롯 일치, slot 0 successful_boot=1; invalid partition 메시지 없음 |
| 모듈·PFDI | PASS | 모듈 load, ethsi1 열거 및 PFDI startup 검사 |
| Linux poweroff | PASS | 파일시스템 해제, `reboot: Power down`, launcher 종료 |
| Secure firmware 종료 | FAIL | `ASSERT: lib/xlat_tables_v2/xlat_tables_core.c:801` |
| 전체 pipeline | FAIL | 마지막 all-domain/shutdown evidence 검사 실패 |

## 입력과 재현 명령

- source image: `build/autosd/native-builder-20261102/rootful-cross-v2/fetch/minimal_qm.aarch64.qcow2`
- SHA256: `b1e199073127e00c65a93f955147516222949290eec167f595e49606f6a0c6c3`
- effective MACHINE/DISTRO: `apollo-qvp` / `auto-ad-nexios`
- BSP deploy: `build/tmp_baremetal/deploy/images/apollo-qvp`
- 실제 부팅 커널은 이미지 내 upstream 6.12 커널 대신 Apollo BSP UKI의 6.18.5 RT 커널이다.
- 원본 qcow2는 보존하고 변환 이미지 및 private 실행 디스크에 모듈/PFDI와 검증용
  openssh-server/iproute 등을 추가했다. Automotive/RT customization 설치는 선택하지 않았다.

실행은 기존 host-tools 환경의 `LIBGUESTFS_BACKEND`, `SUPERMIN_KERNEL`,
`SUPERMIN_MODULES`를 적용한 뒤 다음 pipeline을 사용했다. 재실행 시 출력 경로를 바꾼다.

```bash
python3 scripts/autosd_demo/build_minimal_qm.py \
  --image build/autosd/native-builder-20261102/rootful-cross-v2/fetch/minimal_qm.aarch64.qcow2 \
  --guestfish build/autosd/cold-bootstrap-20260929/host-tools/root/usr/bin/guestfish \
  --output build/autosd/native-boot-20261102-v2-prepared \
  --work-dir build/autosd/native-boot-20261102-v2 \
  --qbox-out-dir build/qbox-apollo-qvp/autosd-native-boot-20261102-v2
```

## 검증 도구 보완과 수동 개입

첫 실행은 headless launcher에 UART 입력이 없고 pipeline이 자동 로그인을 가정해
SSH 준비에서 대기했다. 해당 검증 세션을 종료하고 두 번째 세션을 생성했다.

`build_minimal_qm.py`에 실행별 private UART FIFO를 생성하고
`QBOX_RDASPEN_PRIMARY_UART_READ_FILE`로 전달하도록 수정했다. Linux root/password
로그인, 비밀번호 프롬프트 뒤 kernel 로그가 섞이는 경우를 처리한다.

두 번째 세션에서는 초기 수정본의 터미널 상태 응답이 U-Boot autoboot를 중단시켜
수동으로 `boot`를 실행했다. 로그인 타이밍 보완 중에도 수동 콘솔 입력을 사용했다.
최종 코드는 터미널 상태 응답을 보내지 않으며, U-Boot에서 입력하지 않는 회귀 테스트와
로그인 프롬프트 처리 테스트를 통과했다. **최종 수정본으로 완전히 무인 재부팅을
반복 검증한 것은 아니다.**

관련 Python 회귀 테스트 5개 파일의 71개 테스트가 통과했다. 이 결과는
콘솔 처리 및 빌드 도구의 회귀 검사이며 무인 부팅의 runtime 증거를 대신하지 않는다.

## 종료 실패 및 남은 경고

guest 체크와 종료 명령은 모두 returncode 0이었다. 최종 QBox receipt는
`POWERED_OFF`, `passed=true`, `poweroff_observed=true`지만 그 안의
`domains.status=FAIL`, AP errors의 `ASSERT:=true`이므로 전체 pipeline은 FAIL이다.

secure console의 마지막 backtrace는 EL3 0x82a88, 0x917f4 등에서 시작한다.
현재 TF-A 소스의 해당 행은 translation table 초기화 후 static mapping 추가를
금지하는 `assert(!ctx->initialized)`이다. 현재 로컬 BL31 ELF로는 이 runtime 주소를
해석하지 못했으므로 **배포된 firmware와 일치하는 ELF/relocation 검증 없이 정확한
호출자를 확정하지 않는다.** 이번 작업에서 TF-A를 수정하거나 재빌드하지 않았다.

경고 로그에는 bridge netfilter 안내, SELinux cgroup2 mount 설정 충돌,
SMMU SID 범위, cpuidle 등록 실패, sysusers 중복, EFI random-seed 권한,
ethsi1 NetworkManager 활성화 실패 등이 남아 있다. QM은 경고 이후 실제 실행 검사를
통과했다. 경고가 모두 해결됐다는 판정은 하지 않는다.

## 증거 위치

- `build/autosd/native-boot-20261102-v2/result.json`: 전체 FAIL 및 단계별 반환 코드
- 같은 디렉터리 `qbox-guest-check/console.log`, `result.json`: QM/EFI/SELinux PASS
- 같은 디렉터리 `qbox-modules/`, `qbox-poweroff/`: 모듈 및 종료 명령 결과
- `build/qbox-apollo-qvp/autosd-native-boot-20261102-v2/`: 네 도메인 UART, private rootfs,
  `modules.json`, `domains.json`, `result.json`
- 위 디렉터리 `full-system/qbox-secure-console.log`: 종료 시 TF-A assertion

Automotive scenario, RT latency, IPC·OTA·watchdog fault injection 및 장시간 안정성은
이번 부팅 검증 범위에 포함하지 않는다.
