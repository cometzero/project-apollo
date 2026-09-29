# QBox Lua 연결도 — 구현 및 Quick Guide

## 지원 범위

대시보드의 **QBox 연결도**는 `apollo-qvp.lua`에서 시작하는 Lua include graph를
평가해 Subsystem별 QEMU CPU → router → SystemC/QEMU wrapper 연결을 표시한다.
컴포넌트 이름과 연결을 별도 정적 목록으로 복제하지 않는다. CPU 루프, 조건부 정의,
테이블 조립 및 최종 bind 변경을 적용한 결과를 사용한다.

대표 입력은 `hsoc-stack/tools/qbox-platform/platforms/apollo/apollo-qvp.lua`와
그 파일에서 도달하는 `apollo-qvp-common.lua`, `hw-block/*.lua`, `board/*.lua`다.
추출 코드·웹 UI는 Root 저장소에 있고 QBox 모델이나 Lua 배선을 변경하지 않는다.

## Quick Guide

1. 기존 대시보드 서버를 실행한다. 실행 명령과 LAN 설정은
   [대시보드 가이드](../autosd-dashboard-guide-ko.md)를 따른다.
   호스트에 `lua5.4`, `lua5.3`, `lua`, `luajit` 중 하나가 필요하다.
2. `http://192.168.0.13:8765/#topology` 또는
   `http://127.0.0.1:8765/#topology`를 연다. 왼쪽 **MAP**으로도 이동한다.
3. **전체 연결도**에서 Subsystem별 CPU/Instance, Router, Component 블록과
   그룹 간 TLM 연결을 확인한다. 블록은 실제 연결을 집계한 요약이며 개별 장치가 아니다.
4. 그룹 블록을 누르거나 **Subsystem**을 선택해 개별 컴포넌트 연결도로 펼친다.
   AP Compute, RSE, Safety Island CL0/CL1, System Fabric, System Management,
   Rest of SoC, Pin Control, Board, Platform Services를 구분한다.
5. 개별 노드 또는 **COMPONENT INDEX** 항목을 누르면 연결을 강조하고 우측에
   CCI 경로, `moduletype`, QEMU instance, Lua 소스 위치, 설정값, 연결 포트를 표시한다.
   설정값은 `CCI / Lua 설정값`을 펼쳐 확인한다. 외부 Subsystem 연결도 상세 목록에
   포함하며, 해당 항목을 누르면 상대 컴포넌트로 이동한다.
   **MEMORY ADDRESS**에는 포트별 시작/끝 주소(포함), 크기(16진수/bytes), 연결된
   router 주소 공간, `relative_addresses`, `priority`, `mapped_base_addr`를 표시한다.
   개별 노드에도 첫 주소와 추가 창 개수를 표시하며 16진수 주소 검색을 지원한다.
   주소가 없으면 미정의로 표시하고, 크기가 없거나 0이면 끝 주소를 계산하지 않는다.
   JavaScript 정수 정밀도 범위를 넘는 숫자는 부정확한 주소 대신 경고로 표시한다.
   이 주소는 해당 포트의 decode 설정이며 상위 router/ATU 변환 후 guest PA와 같다고
   가정하지 않는다. `relative_addresses` 미지정 시 모델 기본값을 추정하지 않는다.
6. 검색은 선택 Subsystem 안에서 이름·CCI 경로·모델·설정값을 찾는다.
   전체 검색하려면 **전체 연결도**로 돌아간다. 첫 80개 결과를 표시하므로 검색어로 좁힌다.
7. 기본은 TLM 연결이다. **Signal · 참조 포함**으로 IRQ/reset/biflow와
   인스턴스 참조도 표시한다. `− / 맞춤 / +`와 캔버스 스크롤로 이동한다.
   노드는 Tab 및 Enter/Space로도 선택할 수 있다.
8. Lua 수정 후 **Lua 새로 분석**을 누른다. 소스 SHA-256이 바뀌면 캐시를 재생성한다.
   오류 시 이전 그래프를 현재 구성처럼 유지하지 않고 `UNAVAILABLE`로 표시한다.
9. **draw.io ↓**는 모든 컴포넌트와 연결을 담은 편집 가능한
   `apollo-qvp.drawio`를 다운로드한다. 현재 화면의 필터와 무관한 전체 구성이다.
   Subsystem 컨테이너, 모델·설정·소스 메타데이터와 분석 profile을 보존한다.

## API와 안전 경계

| API | 응답 |
| --- | --- |
| `GET /api/topology` | nodes, edges, groups, sources/SHA-256, environment, warnings, limitations |
| `GET /api/topology/drawio` | native `mxGraphModel` XML 다운로드 |

기존 Host/Origin/인증 검사를 공유하며, 사용자 입력으로 Lua 경로나 환경 변수를
선택하지 않는다. 고정된 checkout의 include allowlist만 메모리에 읽고 별도 Lua
프로세스에서 최대 12초 평가한다. 평가 환경에 `io`, `require`, `os.execute`를
노출하지 않으며 호스트 환경 변수도 전달하지 않는다. VM 실행, MMIO 접근,
SystemC 객체 변경은 하지 않는다. 소스는 신뢰하는 로컬 checkout이어야 한다.

## 해석 시 주의사항

- **현재 VM 토폴로지가 아니다.** `QBOX_RDASPEN_ENABLE_AP_CPUS=true`만 설정한
  full-system Lua 기본 profile이다. QEMU/AP-only 실행 중이거나 VM이 꺼져 있어도
  full-system 정적 지도를 제공한다. 런처의 CPU 개수·장치 옵션·runtime injection 등
  실행 환경 차이는 반영하지 않는다. 특히 이번 기본 profile은 AP CPU 4개다.
- Group은 소스 모듈을 기본으로 하되 공용 생성 함수의 AP/SI CPU·instance·router는
  도메인 식별자로 소속을 보정한다. AP 관련 ROS 주변장치는 Rest of SoC에 유지한다.
- 소스 줄 번호는 최초 관찰 함수/호출 지점 범위이며 정확한 대입문의 줄 번호가 아니다.
- TLM/Signal 분류 및 화살표 방향은 포트 이름에서 추론한다. `direction`에 추론 기준,
  `binding`에 원래 선언을 보존한다. 상세 연결 tooltip에서도 원래 bind를 확인한다.
  도식만으로 모든 모델의 C++ 포트 방향을 검증했다고 해석하지 않는다.
- Subsystem 상세 도식에는 해당 그룹 내부 연결만 그린다. 외부 연결 개수와
  상대 장치는 요약 및 Inspector에서 확인한다. 전체 도식은 그룹 간 연결을 포함한다.
- Lua에서 정의한 컴포넌트/참조 해석 결과이며 내부 QEMU 디바이스 전체, 실제
  트래픽·대역폭·latency·IRQ 성공·물리/ASIL 보증을 의미하지 않는다.

## 검증 (2026-09-30)

실제 full-system Lua 평가: **333개 컴포넌트, 1,184개 연결, 10개 그룹**,
CPU 10개(AP 4, RSE 1, CL0 1, CL1 4), router 8개, 미해결 참조 0개.
이 숫자는 checkout/profile이 변경되면 바뀔 수 있다.

검증 항목은 실제 Lua 평가, 중첩 RSE QEMU instance, CL1 공용 함수 그룹 분류,
router→target 방향 정규화, 소스 변경 캐시 무효화, 오류 응답, 실행/파일 API 차단,
draw.io XML ID/edge geometry, UI 그룹·검색·레이아웃을 포함한다.

```bash
pytest -q tests/test_autosd*.py
node --test tests/test_autosd_topology_ui.cjs tests/test_autosd_dashboard_ui.cjs
```

AutoSD Python 회귀 테스트 **643개 PASS** (기존 Paramiko 경고 2개),
대시보드/토폴로지 Node 테스트 **45개 PASS** (주소·다중 창·정밀도 검사 포함).
브라우저에서 전체 지도, AP CPU 클릭/설정, Subsystem 선택, Signal 표시,
검색·상대 컴포넌트 이동, 390px 작은 화면, 키보드 선택, draw.io 다운로드를 확인했다.
LAN `192.168.0.13:8765`와 loopback `127.0.0.1:8765`에서 새 API를 확인했고,
VM이 정지된 상태에서 웹 서버만 기존 실행 옵션으로 재시작했다.
증거는 `build/qbox-apollo-qvp/topology-dashboard-validation/` 아래에 보존한다.
이번 변경을 위해 VM 부팅이나 장애 주입은 필요하지 않다.
