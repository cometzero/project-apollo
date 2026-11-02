# Process View 구현 검증 — 2026-11-01

## 구현/회귀 검사

- PASS: `node test-diagrams.cjs` — 기존 5개 graph/source excerpt/bounds/reference 및 mailbox path 종류.
- PASS: `node test-processes.cjs` — schema/identity/중복·상충 PID/TID/실행 문맥/process crossing 구분.
- PASS: `python3 test_snapshot.py` — 5개 unittest: 실제 자기 process 수집, /proc 미확인, PID 재사용, 잘못된 monitor 소유권, QMP mock 매핑/외부 TID 거절.
- PASS: Playwright `browser-check.js`: 5개 chapter × 3개 view, step 유지, keyboard process 이동, snapshot import, invalid snapshot 시 이전 상태 유지, IPC/endpoint 이동, thread 표시, static 복귀, player, responsive, reduced-motion.
- PASS: 기존 drawio 5개 page에 process 경계 존재. 현재 view export XML parsing 및 process boundary 확인.
- PASS: browser console error 0.

## 실제 관측과 제한

- OBSERVED: HTTP 서버 PID 10886의 /proc snapshot 수집과 browser import. JSON은 `build/qbox-apollo-qvp/qvp-interactive-preview/process-snapshot.json`에 저장.
- TEST_ONLY: IPC endpoint와 QMP CPU/TID mapping은 UI fixture 또는 mocked diagnostics로 검증. 실제 QBox 실행 증거가 아니다.
- NOT_RUN: QBox boot/guest traffic/runtime QMP, 실제 IRQ/DMI behavior, MacBook Safari 직접 접속.
- UNKNOWN: effective TCG mode/binary revision, component의 현재 실행 TID, guest PID. source Git revision과 구분한다.
- IPC 자동 discovery는 구현하지 않았다. schema의 links로 확인된 endpoint를 입력하면 boundary port/이동을 제공한다.
- Snapshot은 수집 시점의 기록이며 이후 process 생존 여부를 실시간 검증하지 않는다.

## 화면 검사

1440/1280/768px에서 page 가로 overflow 없음. SVG는 내부 scroll 및 zoom 지원.
Process Map과 process detail screenshot을 육안 확인했다. 긴 label은 ellipsis + tooltip/inspector로 보존한다.
캡처는 `build/qbox-apollo-qvp/qvp-interactive-preview/process-map-v3.png`, `process-detail-v3.png`.
검증은 문서 UI와 정적 구조에 관한 것이며 hardware/firmware qualification이 아니다.

---

이전 2차 시안 검증 기록:

# 2차 상세 시안 검증 — 2026-11-01

- PASS: JavaScript syntax check (`app.js`, `diagrams.js`, `diagram-view.js`).
- PASS: `node doc/qvp-interactive/test-diagrams.cjs` — 5개 graph, ID/reference, bounds, source excerpt snapshot, mailbox TLM/internal-call 구분.
- PASS: drawio XML parsing 및 5개 diagram page.
- PASS: LAN URL browser navigation, console error 0.
- PASS: browser assertion으로 70개 node 각각 선택/source excerpt 확인, 57개 edge, 20개 step별 active node 확인.
- PASS: reset, zoom 125%, fit 100%, 자동 재생 후 단계 이동, pause 후 단계 유지.
- PASS: node keyboard Enter 선택.
- PASS: 1440px 및 768px page 가로 overflow 없음. 작은 화면은 SVG 영역 내부에서 scroll.
- PASS: reduced-motion media emulation 시 animation-name=none.
- PASS: overview/mailbox/DMI screenshot 육안 확인. Mailbox edge label이 node에 가려지는 문제를 수정했다.
- 수정: 첫 browser load에서 renderer 초기화의 `el` 선언 순서 오류를 발견하여 수정, 재검증 시 console error 0.
- NOT_RUN: 실제 MacBook Safari, keyboard 전체 navigation/스크린리더, QVP boot/traffic/IRQ/DMI runtime qualification.

Screenshot evidence: `build/qbox-apollo-qvp/qvp-interactive-preview/`의 `overview-v2.png`, `mailbox-v2.png`, `dmi-v2.png`.
Overview screenshot은 global address view 하단 row 추가 이전이며 최종 전체도를 완전히 대표하지 않는다.
위 결과는 문서 UI와 정적 구조 검증이다. Physical interconnect, cache coherence, firmware protocol timing의 검증이 아니다.
