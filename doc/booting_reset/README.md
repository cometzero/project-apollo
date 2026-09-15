# Apollo QVP 부팅 및 reset 구조 비교

작성 기준: 2026-09-13. 현재 `apollo-qvp.lua`의 도메인별 boot/reset 연결을
Arm Zena CSS hardware guide 및 `arm-zena-css` RD-Aspen 참조 소프트웨어와 비교한다.

- [부팅 구조와 순서](boot-sequence.md): RSE, SI CL0/CL1, AP의 준비·해제 순서,
  image/entrypoint, CMN-S3AE 및 NI-710AE 초기화 역할.
- [Reset 구조와 영향 범위](reset-structure.md): trigger, fanout 순서,
  warm/cold/domain reset 비교, 상태 보존과 미연결 경로.
- 관련 문서: [fabric 및 memory map](../fabric/README.md).
- 후속 실측(2026-09-14): [RSE SysTick/TIMER counter 및 CLKSOURCE Iris 검증](rse-counter-iris-validation.md).

## 핵심 결론

RSE가 먼저 실행되고, RSE가 CL0를, CL0가 AP 및 CFG2 CL1을 관리하는 구조를
QVP도 따른다. 다만 CPU release는 SystemC `host_ppu`의 signal과 QEMU CPU
reset callback으로 구현되며, SI image는 실행용 SRAM에 host loader로도
적재된다. Hardware의 image 인증·전달과 QVP의 CPU 실행 성공은 별개로 검증해야 한다.

QVP의 `ap_cold_reset_fanout`과 `apollo_system_reset_fanout`은 서로 다른
대상 목록이다. 후자도 POR처럼 모든 상태를 초기화하지 않는다. CMN GPV,
ATU, NI FMU 등의 일부 상태는 전체 fanout에 연결되지 않고, RSE warm/cold/AON
reset tree도 hardware와 완전히 같지 않다.

현재 hardware SI는 CL0 DCLS 구성이다. CL1 4-core SMP는 FVP CFG2 확장이므로
하드웨어 기본 구성과 CFG2를 분리해서 비교한다.

## 소스 snapshot과 분석 조건

| 저장소 | HEAD |
| --- | --- |
| Workspace root | `47af3224b7e64783cb75916f913a8c02b296234a` |
| `hsoc-stack/tools/qbox-platform` | `d7731408c25309a7461ab1cf6d98b4f820f6db45` |
| `hsoc-stack/tools/qbox` | `e84f25603cfeb3f9a073002b4339ba5bb67c444e` |
| `arm-zena-css` | `bf34d9e71f674e11beea3b8e84ea54486f555d2a` |

앞선 작업의 `doc/fabric/`은 보존했다. 구현 변경 없이 source Lua와 C++를
정적으로 분석했다. AP 포함 설명은 full-system runner의
`QBOX_RDASPEN_ENABLE_AP_CPUS=true`를 전제로 한다. Lua 단독 fallback은 AP
비활성이고, 활성화 시 CPU 수 fallback은 4개(설정 범위 1–16)이다.

현재 `build/conf/local.conf`의 MACHINE 기본값과 `templateconf.cfg`는
`apollo-fvp`이다. 이 작업에서 build 설정을 변경하거나 QVP/FVP를 실행하지
않았다. 배포 runtime을 비교할 때는 `.qboxconf`가 선택한 provider Lua,
binary, firmware image 및 환경변수를 별도로 고정해야 한다.

## 증거와 검증 범위

소스 근거는 각 문서의 상대 경로 링크와 함수·객체 이름으로 표시한다.
문서에 나오는 순서는 다음 세 종류를 구분한다.

| 종류 | 의미 |
| --- | --- |
| Hardware/reference 순서 | Guide와 RD-Aspen design 문서가 규정하는 계약 |
| QVP 정적 연결 순서 | Lua binding 및 C++ callback에서 확인한 의존 관계 |
| Runtime 실행 순서 | 이번 작업에서는 미수집; timestamp/PC/PPU/MHU trace 필요 |

기존 reset 정적 검사는 아래 명령으로 실행하여 **5/5 PASS**를 확인했다. 이 검사는 5개 source
assertion이며, 전체 reset propagation이나 문서 전체의 정확성을 증명하지 않는다.

```sh
python3 scripts/test/validate_qbox_apollo_fvp_full_map.py --check reset \
  --out build/qbox-apollo-qvp/booting-reset-doc/reset-static-validation.json
```

문서 링크와 표 형식도 확인한다. Build, component runtime, QBox/FVP 재부팅,
실제 watchdog/fault 주입은 수행하지 않았다. 이전 boot 또는 component PASS를
현재 reset parity 증거로 사용하지 않는다.
