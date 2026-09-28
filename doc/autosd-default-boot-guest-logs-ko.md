# 기본 부팅 구성 및 분리 Guest 로그

## 기본 부팅 포함 여부

현재 customization 이미지의 unit/Quadlet 설정과 guest의 실제 부팅 journal을
대조했다. 단순 현재 active 상태가 아니라 시나리오 실행 이전의 최초 시작 기록을
확인했다. Quadlet의 `generated` 상태는 비활성화가 아니라 생성된 unit이며 실제
target의 Wants에 포함된다.

| 구성 | 기본 부팅 | 근거 |
| --- | --- | --- |
| Root OS | 포함 | `/dev/vda5` ext4 root filesystem |
| Root BlueChi controller/agent | 포함 | enabled, 부팅 journal 시작 기록 |
| Root safety monitor | 포함 | multi-user.target, ADAS 이후 시작 |
| ASIL-B ADAS 앱 | 포함 | apollo-adas Quadlet, multi-user.target |
| QM system container | 포함 | qm Quadlet, default target 의존성 |
| QM BlueChi agent | 포함 | QM 내부 enabled |
| QM native 앱 | 포함 | apollo-qm-app enabled, multi-user.target |
| QM nested 앱 컨테이너 | 포함 | apollo-qm-container Quadlet, multi-user.target |
| S01–S06 테스트 | 수동 | 기본 앱의 검사·제어·장애 주입·복구 시나리오 |
| R01–R06 / timerlat / osnoise | 수동 | RT 측정·부하 실험, 자동 서비스 아님 |

ASIL-B/QM은 별도 디스크 파티션이 아니라 cgroup/container 논리 구획이다.
Podman은 컨테이너 실행 도구이므로 별도 상주 daemon의 active 여부로 판단하지 않는다.
OTA/UKI, iceoryx2 등의 수동 workflow가 이 기본 regular VM에서 자동 시작됨을
의미하지 않는다.

기존 부팅 감사 증거:
`build/autosd/boot-autostart-audit-20260927-{live,journal,init}/`.
해당 부팅 최초 시작은 BlueChi 40초대, ADAS 46초대, safety 47초대, QM 50초대,
QM 내부 앱 58초대, nested container 64초대였다. 이는 관측값이지 부팅 시간 보장이 아니다.

## Guest 로그 창

기존 Host/Guest 탭 전환 대신 **서로 독립된 두 패널**로 표시한다.

- Host log: 기존처럼 작업별 명령 출력과 이전 세션 드롭다운.
- Guest log: 별도 패널에서 UART, Root services, Safety monitor, BlueChi, ADAS,
  QM system, QM app, QM container를 선택한다.
- `새 창에서 보기`는 `/?view=guest`를 별도 창/탭에 열어 Guest 로그만 표시한다.
- UART는 부팅 즉시 파일에서 읽는다. 서비스별 journal/stdout은 SSH 준비 후
  읽기 전용으로 수집하며 조용한 앱은 heartbeat snapshot과 빈 출력 표시를 구분한다.
- 서비스 로그는 최대 15초 캐시, 요청당 최대 128 KiB/명령 15초 제한이다.
  작업 명령을 입력받지 않고 고정 allowlist만 사용한다.
- Pause/종료/Reboot/RT 측정 중 서비스 로그 수집은 중단·보류한다.
  마지막 표본을 실시간 값으로 해석하지 않도록 상태와 수집 시각을 표시한다.
- Power on/Reboot의 로그 세션 경계와 이전 Host 실행 이력은 유지한다.

UI는 기존 콘솔 디자인을 유지하는 frontend-design 기준으로 분리했다.

## 신규 Power on 실제 검증

사용자 승인 후 guest 정상 종료(exit 0, UART Power down), 서버 재시작, 보존된
디스크 복사본으로 새 Power on을 수행했다. 이후 시나리오나 수동 서비스 시작을
실행하지 않은 상태에서 검증했다.

- boot job: `f37076a4b1524f9bb658257cb95720a1`
- boot ID: `8ebad7a1-11dd-44c0-b2c2-e4e81a2c936c`
- Root BlueChi 42초대, ADAS/Safety 48초대, QM 51초대, QM 내부 앱/BlueChi 58초대,
  nested QM container 65초대에 자동 시작. 8개 서비스 active, 3개 workload health
  exit 0, Safety HEALTHY. 시작 기록이 각각 최초 1건임을 확인했다.
- 증거: `build/autosd/boot-autostart-poweron-20260927/{console.log,result.json}`.

서비스 로그 API 7종(root/safety/bluechi/adas/qm/qm-app/qm-container) 모두 OK.
Enforcing 상태에서 ADAS와 nested QM의 heartbeat snapshot 읽기도 성공했다.
증거: `build/autosd/guest-service-log-validation-20260927/*.json`.

전용 창은 Host 영역을 숨기고 Guest 패널/8개 대상을 표시한다. 390px 화면에서
가로 넘침 없음, JavaScript 오류 없음. 스크린샷:
`build/autosd/dashboard/guest-window-{boot,mobile,adas}.png`.
Python 전체 AutoSD 테스트 257 PASS, UI 테스트 13 PASS.
최종 VM은 ONLINE·HEALTHY 상태로 유지했다.
