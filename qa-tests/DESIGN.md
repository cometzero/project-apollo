# Apollo QVP runtime pytest 설계

상태: 구현 완료. 실행 결과와 미해결 runtime 실패는 run별 report 및 검증 기록에서 별도로 기록한다.

## 목적과 기준

`sw-ref-stack/documentation/test_automation/user_guide/fvp.rst`와 AutoAPI의 실제 Python 계약을 따른다.
pytest가 Apollo SoC의 runtime 기능을 실행·판정한다. 소스 문자열 검사와 mock 단위 검사는 runtime 결과에 섞지 않는다.
QBox는 simulator backend이고 `apollo-qvp`는 대상 machine이다. FVP와 물리/timing 동등성을 주장하지 않는다.

공통 소스는 sw-ref-stack의 Config, Device, DriverBundle/registry, AutoTestPlatformBase,
BaseNetworkManager만 선택적으로 복사한다. 저작권·MIT 문구와 원본 revision/hash는 upstream.json과 LICENSES에 보존한다.
FVP/FPGA 전용 controller, 불필요한 통신/빌드 코드는 복사하지 않는다.

## 디렉터리 소유

- `tests/{ap,rse,si_cl0,si_cl1}/{boot,security,power,safety,network,devices,...}/test_<기능>.py`: DUT runtime case.
- `test_automation/utils`, `configs/config.py`, `targets/registry.py`: upstream 공통 API.
- `test_automation/targets/qbox`: QBox Device 및 UART/guest SSH adapter.
- `test_automation/checks`: 순차 명령·공통 결과 판정 helper. 실제 case 수와 내부 assertion 수를 구분한다.
- `test_automation/pytest_plugin.py`: 설정, session fixture, lifecycle, evidence 연결.
- `test_automation/reporting.py`: pytest 결과의 domain/category별 HTML·Markdown·JSON 집계.
- `configs/qbox.yaml`: Apollo-QVP terminal/이미지/timeout 설정.
- `unittests`: framework·report·transport의 host 검증. 기존 qa-tests/tests도 이곳으로 이동한다.
- `scripts/validation`: 기존 OEQA/profile orchestrator, profiles/schema/matrix, injection 입력.
  기존 `run_test.sh`, canonical runner와 dashboard의 공개 인터페이스는 이 호환 도구를 계속 사용한다.
- `build/qbox-apollo-qvp/qa-runtime-<UTC>-<unique>`: run별 보고서와 DUT 원본 로그. 소스 트리에 생성물을 두지 않는다.

## Fixture와 실행

부팅 이미지(`--image=bsp|product`)와 테스트 적용 범위(`image("bsp-only"|"product-only"|"any")`)를 구분한다.
marker를 생략하면 `any`이며 잘못된 값은 collection 오류로 처리한다.
이미지 불일치는 collection에서 skip marker를 부여하여 session fixture도 시작하지 않는다.
`--test-scope`는 한 분류만 선택하며 나머지는 deselected로 보고한다.
공통 kernel/firmware 검사는 `any`가 기본이고 실제 image 의존 도구·서비스가 있는 경우만 전용으로 지정한다.
현재 `bsp-only`는 없으며 OVS/systemd 장치 profile, PSA 도구, RAS 서비스의 3개 case만 `product-only`다.

가이드의 fixture graph를 유지한다:
`cfg -> auto_platform_config_data -> platform_bundle -> platform_driver/session_manager -> platform_base_obj`.
`@register_platform("qbox")` factory는 `DriverBundle`을 반환한다.
초기화 이전부터 try/finally를 적용하여 start/ready/login 실패에서도 DUT를 정리한다.
단순 설정 오류·부팅 실패를 SKIP으로 바꾸지 않는다.

QBox driver는 기존 `run_qbox_yocto.sh`의 provider/.qboxconf 해석과
`qbox_board_session.py`의 FIFO·PID/start_ticks 소유 및 cleanup receipt를 재사용한다.
빌드를 수행하지 않으며 prebuilt 이미지가 필요하다. 고유 run directory, copy-disks,
no-persistent-rse-state, multi-session을 사용하여 원본 이미지와 기존 session을 보존한다.
pytest 외부 writer와 기존 --validation-profile 내부 writer는 동시에 활성화하지 않는다.
TC397 외부 companion은 기본 SoC suite에서 꺼 두고 지원 범위를 명시한다.
Product network 검사는 기존 `platform_network_server`를 session 동안 열고
canonical `--validation-http-port`의 guestfwd를 사용한다. guest HTTP 응답과 서버
request 기록을 보존하며 session 정리 시 host 서버도 종료한다.

하나의 session에서 테스트를 실행한다. 파괴적 fault injection은 destructive marker로 표시하며,
이후 테스트 전에 새 generation으로 재부팅한다. 설정을 바꾸는 정상 power test는 원상 복원한다.
종료 실패는 pytest ERROR이며 이전 PASS에 숨겨지지 않는다.
재부팅 실패 시 현재 DUT를 정리하고 이후 의존 testcase를 setup ERROR로 기록한다.
실패한 generation을 재사용하거나 testcase마다 같은 boot를 무한히 재시도하지 않는다.
모든 도메인의 boot case를 먼저 실행하여 일반 runtime 명령이 초기 부팅 로그에 영향을 주지 않게 한다.
RSE, RSE measured boot, SI CL0, SI CL1, TF-A, U-Boot, Linux, OP-TEE를 각각 로그로 판정한다.
Linux/Zephyr shell 명령은 devices category의 별도 case이며 boot 성공과 구분한다.
공통 fixture는 AP readiness/login을 요구하므로 Linux 부팅 실패 시 선행 firmware case도 setup ERROR다.

## 명령과 로그 API

테스트는 `platform_base_obj.mgr.execute_command_with_prompt_capture(port, command, timeout)`의
`(returncode, output)` 및 `wait_for_prompt_in_log(port, prompt, timeout, ...)`를 사용한다.
terminal 역할은 ap, secure, rse, si_cl0, si_cl1, ssh이다.

AP UART는 command별 새 로그 cursor와 nonce completion marker로 echo/이전 출력을 배제하고 실제 shell exit code를 반환한다.
SI CL0는 Ctrl-E/command/newline/Ctrl-D framing, SI CL1은 Zephyr shell과 새 응답을 사용한다.
펌웨어 CLI에 Unix exit status가 없을 때 returncode 0은 완료 여부이며, case가 기능별 내용까지 검증해야 한다.
RSE boot와 measured boot는 로그 증거이며 쓰기 가능한 RSE shell 지원과 동일하지 않다.
SSH test는 hostfwd로 전달되는 guest SSH에 실제 인증·명령 실행한다. UART 검사를 SSH 성공으로 표기하지 않는다.

기존 11개 profile의 79개 기능 assertion과 신규 SSH 검사를 coverage mapping으로 추적한다.
순차 profile 명령은 한 pytest case로 실행할 수 있으나 내부 280개 command를 독립 testcase로 세지 않는다.
미구현·이미지 미지원 기능은 명확한 SKIP 사유를 갖는다. 부팅/transport 오류를 지원 부족으로 덮지 않는다.

## 자동 보고서

plain pytest 실행에도 run directory와 report.html/report.md/results.json/junit.xml을 자동 생성한다.
상단 summary에 PASS/FAIL/SKIP/ERROR, 선택·미실행 수, 총 시간과 실행 설정을 둔다.
각 domain chapter 아래 category 결과와 testcase별 setup/call/teardown/총 시간을 표시한다.
각 case의 image_scope를 HTML/Markdown/JSON/JUnit에 기록하고 summary에 분류별 선택 수를 표시한다.
실패에는 traceback, captured log, 실제 명령/응답 및 UART 로그 경로를 제공한다.
setup/teardown 오류, collection 오류, 중단, 실행 0건은 정상 PASS로 표시하지 않는다.
HTML의 모든 로그 문자열은 escape한다. 첫 case setup 시간에 session boot 비용이 포함되는 점을 명시한다.

## 검증 계획

1. host unit: API 계약, 설정, 새 로그/nonce, FIFO 오류, SSH timeout/exit, partial startup cleanup, report 결과·시간·escaping.
2. collection: domain/category tree, duplicate basename, image/unsupported SKIP, 기존 host suite와 runtime 수집 분리.
3. 실제 QBox: boot 도메인별 로그, AP UART/SSH, SI CL0/CL1 명령을 실행하고 원본 로그와 cleanup receipt 보존.
4. 전체 runtime suite를 실행하여 FAIL/SKIP을 숨기지 않고 모델/이미지 한계와 adapter 결함을 구분한다.
5. 기존 host suite와 CLI/dashboard adapter regression; shared BitBake 입력을 변경하거나 재빌드하지 않는다.
