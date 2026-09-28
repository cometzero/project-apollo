# AutoSD 전원 제어와 Feature 상태 연동

## 변경 내용

- 허용된 Power on / Reboot / Power off 요청마다 별도 `feature_session`을 발급한다.
- 현재 Feature 카드에는 해당 주기의 결과만 표시한다. 과거 실행 파일과 Host log 이력은 삭제하지 않는다.
- Power on / Reboot에서 1번은 RUNNING, 2번은 QUEUED로 시작한다.
- 1번은 실제 guest SSH와 boot ID를 확인한 후 PASS로 전환한다. Reboot는 이전 boot ID와 달라야 한다.
- 이후 2번 read-only Automotive health 검사를 한 번 자동 예약한다. 서비스 초기화 중에는 제한 시간 안에서 재시도한다.
- 부팅 실패 시 1번 FAIL/TIMEOUT, 2번 BLOCKED로 표시한다. 자동 장애 복구는 하지 않는다.
- Power off 요청 수락 시 기존 Feature 상태를 즉시 초기화한다. 종료 작업 자체의 결과와 로그는 계속 표시한다.
- 이전 주기의 늦은 완료 이벤트가 새 주기의 상태를 덮어쓰지 않도록 주기를 검증한다.

## 검증 범위

UI 자동 테스트에서 현재 주기 필터링, 과거/legacy 작업 제외, 부팅 PASS와
장기 실행 launcher 상태 분리, 대기 중 health와 실제 health 결과 우선순위를 확인한다.
브라우저에서 합성 상태를 주입해 1번 RUNNING / 2번 QUEUED 및 전체 카드 초기화를
확인했다. 이는 실제 VM 재부팅 검증과 구분한다.

검증 명령:

```sh
python3 -m pytest -q tests/test_autosd*.py
node --test tests/test_autosd_dashboard_ui.cjs
python3 -m py_compile scripts/autosd_dashboard/server.py
node --check scripts/autosd_dashboard/web/app.js
```

Python 테스트 240개, UI 테스트 15개 PASS 및 Python/JavaScript 구문 검사를 통과했다.
기존 Paramiko TripleDES deprecation 경고는 전원 연동 실패와 구분한다.

## 실제 적용 및 전원 검증

2026-09-27 사용자 승인 후 기존 VM을 정상 종료(`5deb1ae9931141eebaf074fb23d29110`,
exit 0 및 UART Power down 확인)하고 최신 디스크를 보존해 서버를 재시작했다.
증상 원인은 새 정적 UI와 재시작 전 구형 서버 API의 버전 불일치였다.

증거 디렉토리: `build/autosd/dashboard/20260927-161222-530e591a/`.

| 확인 | 결과 | 증거 |
| --- | --- | --- |
| 화면 Power on 직후 | 1 RUNNING / 2 QUEUED | boot `10e53714acf34799b09e9b7ef4ad8033` |
| guest boot ID/SSH 확인 | 1 PASS (69초) | `poweron-pass.json`, `.png` |
| 자동 Automotive health | 2 PASS | `c4b24015309645039e5fbfc3b3b6a0e0`, health marker/rc=0 |
| Reboot 수락 | 이전 상태 초기화, 1 RUNNING / 2 QUEUED | `90209ad50ef94023957a4bde9ff5b8e5` |
| Reboot 확인 | 1 PASS (101초), 새 boot ID | `38d027fe-d446-4dc4-9a02-6f4912c63494` → `c3155d19-b60f-42c7-856c-d9650d8dcbfb` |
| 재부팅 후 자동 health | 2 PASS | `0304120b2b374ea2af9c0a035f17ff6b`, `reboot-pass.json`, `.png` |
| localhost/LAN API | PASS | 두 주소 모두 새 Feature 필드와 PASS 상태 반환 |

현재 VM은 실행 상태로 유지했다. 브라우저 오류는 관찰되지 않았다.
이는 QEMU 기능 검증이며 하드웨어 타이밍/안전 인증 검증은 아니다.
사용 방법은 [대시보드 Quick Guide](autosd-dashboard-guide-ko.md)를 참고한다.
