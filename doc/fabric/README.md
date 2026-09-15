# Apollo QVP fabric와 Arm Zena CSS 비교

작성 기준: 2026-09-13. 현재 checkout의 `apollo-qvp.lua`와 그 파일이 최종
구성하는 QBox/SystemC 연결을 Arm Zena CSS hardware programmer's model 및
`arm-zena-css`의 RD-Aspen FVP/firmware 구성과 비교한다.

## 문서 구성

- [Fabric 및 bus routing](fabric-routing.md): 도메인별 연결, ATU/bridge,
  CMN-S3AE·NI-710AE 역할, 공유 메모리 및 구현 한계.
- [Global 및 domain-local memory map](global-memory-map.md): 52비트 namespace,
  주요 aperture와 실제 구현 범위, 로컬 주소 변환, 하드웨어/FVP 차이.

## 핵심 결론

QVP는 `rse_router`, `ap_router`, `si_cl0_router`, `si_cl1_router`,
`system_router`, `smd_router`와 선택적인 ATU/bridge 연결로 기능적 주소
접근을 구현한다. 이 router들을 각각 물리적인 NI-710AE 또는 CMN-S3AE
인스턴스와 일대일 대응시키면 안 된다.

CMN의 `host_cmn_cyprus`는 discovery 및 SAM 프로그래밍용 레지스터 모델이다.
AP의 DRAM 접근은 이 객체를 통과하지 않는다. NI-710AE는 CL0 CPU 경로의
APU 검사와 일부 NCI/FMU 동작을 구현하지만, 시스템 전체 NoC의 모든
initiator/target 경로를 하드웨어와 동일하게 모델링하지 않는다.

Global 주소와 각 CPU의 로컬 주소는 별개의 view이다. Global target이
존재한다고 AP/CL1에서 그 주소로 바로 접근할 수 있는 것은 아니다.
또한 SI의 global SRAM 객체와 CPU 실행용 SRAM 객체는 별도로 생성된다.
주소가 대응한다는 사실만으로 두 객체의 backing memory 동일성을 보장하지 않는다.

현재 hardware guide의 SI는 CL0 한 cluster이며, CL1 4-core SMP는 RD-Aspen
FVP CFG2 구성이다. 따라서 CL1은 CFG2와 비교하며 현재 하드웨어의 구현
누락이나 동등성으로 판정하지 않는다.

## 분석 범위와 재현 기준

| 저장소 | 분석한 HEAD |
| --- | --- |
| Workspace root | `47af3224b7e64783cb75916f913a8c02b296234a` |
| `hsoc-stack/tools/qbox-platform` | `d7731408c25309a7461ab1cf6d98b4f820f6db45` |
| `hsoc-stack/tools/qbox` | `e84f25603cfeb3f9a073002b4339ba5bb67c444e` |
| `arm-zena-css` | `bf34d9e71f674e11beea3b8e84ea54486f555d2a` |

분석 시작 시 위 저장소들의 tracked/untracked 변경은 없었다. 구현 기준은
source Lua이며 배포된 provider 복사본이나 실행 중 monitor의 topology를
수집한 결과가 아니다. `config.lua` 단독 기본값은 AP CPU 비활성이다.
이 문서의 AP 포함 구성은 full-system runner가 설정하는
`QBOX_RDASPEN_ENABLE_AP_CPUS=true`를 전제로 한다. AP CPU 수는 1–16개로
설정 가능하고 Lua fallback은 4개이다. CL0는 1개, CL1은 4개 R82 모델이다.

현재 로컬 `build/conf/local.conf`의 MACHINE 기본값과 `templateconf.cfg`는
`apollo-fvp`를 가리킨다. 이 문서 작업은 이를 변경하거나 apollo-qvp 이미지를
빌드하지 않았다. `bblayers.conf`에는 owned BSP/product layer가 포함되어
있다. 실제 Yocto 실행은 `.qboxconf`가 선택한 provider Lua와 image를 별도로
확인해야 한다.

## 검증과 판정 범위

| 항목 | 결과 / 의미 |
| --- | --- |
| Lua 최종 rebind, router/addrtr/ATU/APU C++ 확인 | 정적 구현 경로 확인 |
| 기존 full-map validator | PASS, 95/95; map/IRQ/ATU 관련 정적 assertion만 검증 |
| 신규 문서의 상대 경로 링크 | 파일 존재 여부 확인 |
| Build / QBox boot / FVP boot / active traffic | 미실행 |
| Coherence, QoS, 대역폭, latency, RTL/FVP parity | 이 문서에서 검증하지 않음 |

재현 명령과 결과 파일:

```sh
python3 scripts/test/validate_qbox_apollo_fvp_full_map.py \
  --out build/qbox-apollo-qvp/fabric-doc/full-map-validation.json
```

이 validator는 기존 문서와 소스의 정적 패턴을 검사한다. 신규 문서 전체의
정확성이나 실제 접근 성공을 자동으로 증명하지 않는다. 범위별 결론은 아래
문서의 소스 근거와 함께 읽어야 한다.

## 기준 자료

- [Hardware functional blocks](../arm_zena_css_dev_guide/05-functional-blocks-in-zena-css.md)
- [Hardware programmer's model](../arm_zena_css_dev_guide/09-programmers-model-for-zena-css.md), §9.1 및 Tables 9-3–9-9
- [FVP와 hardware의 차이](../arm_zena_css_dev_guide/08-fixed-virtual-platform.md), CFG2 및 RoS 설명
- [arm-zena-css 구성 설명](../../arm-zena-css/documentation/design/components.rst)
- [CMN RTL map 정렬 패치](../../arm-zena-css/yocto/meta-zena-css-bsp/recipes-bsp/scp-firmware/files/fvp-rd-aspen/0089-prod-rdaspen-Use-Arm-RTL-memory-map.patch)
- [실제 Lua entrypoint](../../hsoc-stack/tools/qbox-platform/platforms/apollo/apollo-qvp.lua)
- [Full-system runner](../../scripts/run/run_qbox_apollo_fvp_full.py)

이전 [map 분석](../qbox-apollo-fvp-map-analysis.md)은 역사적 계획과 placeholder
설명이 섞여 있다. 현재 모델의 존재 여부와 연결은 이 문서의 소스 snapshot을
기준으로 한다. 참조 자료 자체의 주소/크기 불일치는 memory-map 문서에서
별도로 표시한다.
