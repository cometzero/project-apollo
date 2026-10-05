# Apollo Saturn-V Board Dashboard

2026-10-05 Saturn-V Yocto 보드 dashboard를 구현했다. `--dashboard`는 웹 서버와
보드를 headless로 함께 실행한다. 실제 지원 범위와 시험 결과는
[구현·검증 보고서](implementation-report-ko.md)를 따른다. 아래 설계 문서는 최초 계획도 보존한다.

## 실행

```bash
./run_qbox_yocto.sh --bsp --dashboard --stats
# CAN 왕복 fixture와 차량 측 AP 제어까지 사용
./run_qbox_yocto.sh --bsp --dashboard --stats-interval 2 \
  --sil-kit --sil-kit-echo-fixture --sil-kit-allow-actuation
```

실행 터미널에 loopback/LAN 접속 URL이 출력된다. 기본 포트는 `8765`이며
**계정·암호 없이 바로 접속**한다. 서버는 foreground에서 유지되며 Ctrl-C/SIGTERM으로
자신이 시작한 QBox·TC397·SIL Kit participant를 정리한다. 브라우저를 닫아도
보드는 실행을 유지한다. 웹의 **보드 실행 정지**는 서버를 남기므로 다시 시작할 수 있다.

`--dashboard-port`, `--dashboard-listen IPv4`(반복 가능)로 접속을 지정한다.
`--dashboard-password-file`을 명시한 경우에만 `autosd` 계정 인증을 사용한다.
동시 실행은 서로 다른 output/HTTP/monitor/SSH 포트를 사용한다.
`--bsp`를 생략하면 기존 기본 `nexios-image`를 사용하며 TC397 기능은 제공하지 않는다.

보드/블록도, UART, 시나리오, 제어, 증거 탭을 제공한다. `--stats`가 없으면 부하 패널은
DISABLED로 표시한다. 통계의 100%는 host 논리 CPU 한 개이며, AP/RSE/SI 값은
QBox vCPU thread의 부분 합이다. TC397와 SIL Kit 프로세스의 부하는 포함하지 않는다.

## 새 설계 문서

| 문서 | 내용 |
|---|---|
| [현재 구성과 재사용 대상](current-state-ko.md) | 실제 launcher, Lua, firmware, 기존 웹 서버의 소유권·격차 |
| [실행 구조와 API](architecture-ko.md) | 외부 접속, 자동 headless, 프로세스 수명, 인증, 로그·명령 계약 |
| [보드 그림과 화면](board-ui-ko.md) | Lua 기반 Board/Block 두 보기, UART, 상태·주소·출처 표현 |
| [시나리오와 보드 제어](scenarios-ko.md) | vMCU/SIL Kit, QVP 검증 profile, 실행 조건·복구·한계 |
| [구현·검증 계획](implementation-plan-ko.md) | 단계별 파일, 통과 기준, 추가 기능 우선순위 |
| [서버 구조 설계도](assets/dashboard-architecture.drawio) | 편집 가능한 draw.io 원본 |
| [보드 화면 설계도](assets/dashboard-board-wireframe.drawio) | 논리적 PCB 형태의 화면 배치안; 실물 회로도 아님 |

## 핵심 결정

- 기존 Python dashboard의 인증·작업·monitor·topology 코드를 재사용한다. 먼저
  Yocto backend를 분리하고, 별도의 프런트엔드 프레임워크나 데이터베이스는 도입하지 않는다.
- `--dashboard`는 웹 서버와 보드를 함께 시작하고 **tmux 없는 지속 실행**을 선택한다.
  기본 이미지는 기존 `nexios-image` 선택을 유지한다. `--bsp --dashboard`가 vMCU 기능의
  첫 검증 대상이며, `--sil-kit`를 추가하면 차량 CAN 시험망까지 시작한다.
- 웹은 기본 loopback과 자동 선택한 LAN IPv4의 `8765` 포트에서 로그인 없이 접속을 받는다. Host/Origin/CSRF 검사를 유지하고 QBox monitor,
  QMP, UART 및 SIL Kit 내부 endpoint는 외부에 직접 노출하지 않는다.
- 실제 실행에 선택한 **provider Lua + 환경변수 + CCI override**를 기록한다. Board와
  Block view는 같은 그래프를 사용한다. 외부 TC397/SIL Kit은 launcher manifest로 합성한다.
- SI CL0의 기존 PFDI가 AP health의 기준이다. vMCU의 5초 보고·GPIO·CAN 상태를 표시하며
  dashboard에 별도 AP heartbeat 판정기를 만들지 않는다.
- `--dashboard --stats`로 **현재 부하와 추이**를 표시한다. 기본 5초 간격이며
  `--stats-interval`로 조절한다. QBox CPU/main/vCPU/AP·RSE·SI/other, RSS, thread 수를
  기존 collector에서 받아 표시하고 monitor/QMP 자동 활성화 계약을 유지한다.
- AP graceful off/wake, AP 복구, MCU reset, 전체 보드 프로세스 재실행과 정지를 구분한다.
  PMIC는 SI CL0 단일 소유이며 초기 UI는 rail 설정값과 live STAT 조회를 제공한다.

지원하는 실행 조합:

```bash
./run_qbox_yocto.sh --dashboard
./run_qbox_yocto.sh --bsp --dashboard
./run_qbox_yocto.sh --bsp --dashboard --sil-kit
./run_qbox_yocto.sh --bsp --dashboard --stats
./run_qbox_yocto.sh --bsp --dashboard --sil-kit --stats-interval 2
```

최초 계획 작성 시 문서의 상대 링크, 구성도 XML과 PNG 렌더링 2개를 확인했다.
[검토 증거](../../build/qbox-apollo-qvp/dashboard-plan-review/validation.json),
[서버 구조 미리보기](../../build/qbox-apollo-qvp/dashboard-plan-review/dashboard-architecture.png),
[보드 화면 미리보기](../../build/qbox-apollo-qvp/dashboard-plan-review/dashboard-board-wireframe.png)는
local build 디렉터리에 보관한다. 편집 원본은 위 `assets/`에 있다.

## 기존 AutoSD Dashboard 설계 및 구현 검증

- [QBox monitor 연동 구현계획](qbox-monitor-integration-plan-ko.md)
- [구현계획 검토 결과](qbox-monitor-integration-review-ko.md)
- [구현 및 검증 · Quick Guide](qbox-monitor-implementation-ko.md)
- [QBox Lua 연결도 · Quick Guide](qbox-topology-guide-ko.md)

아래 기존 문서들은 각 문서의 작성일 checkout 기준이다. 최초 계획과 실제 구현 범위·검증 결과는 구분한다.
완료 여부, 재현 명령, 실패 후 수정 사항 및 남은 제한은 구현·검증 보고서를 따른다.
