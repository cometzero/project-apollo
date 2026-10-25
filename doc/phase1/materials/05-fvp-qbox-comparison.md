# 05. FVP 대비 QBox 구성 비교

> **발표 목표:** 두 platform이 공유하는 SW contract와 서로 다른 model 구성, 실제로 비교 가능한 evidence를 설명한다.
> Source 기준: 2026-10-25 checkout. 과거 기록을 인용하며 이번 문서 작업에서 FVP/QBox를 새로 실행하지 않았다.

[전체 목차](README.md) · [이전: QBox 실행 구조](04-qbox-runtime-and-lua.md) · [다음: Component SW](06-component-software-architecture.md)

비교의 시작점은 IP 이름이나 boot 속도가 아니라 **guest가 수행해야 할 동작**이다.
같은 protocol을 확인하려면 CPU·address·IRQ·firmware·DTB 조건이 맞아야 하고,
결과에는 실제 stimulus와 assertion이 남아야 한다.
이 장은 baseline을 정한 뒤 device mechanism을 비교하고 evidence의 의미를 판정하는 순서로 구성했다.

![공통 guest contract를 구현하는 FVP와 Apollo QVP](diagrams/05-fvp-qbox.drawio.svg)

[draw.io 편집 원본](diagrams/05-fvp-qbox.drawio) · [기존 HTML 보기](diagrams/05-fvp-qbox.html)

## 학습 순서

| 순서 | Subchapter | 답할 질문 | 중심 그림·사례 |
|---|---|---|---|
| 05.1 | [비교 baseline과 artifact 계약](05-comparison/01-comparison-baseline.md) | 무엇을 같게 맞추고 machine별 차이는 어떻게 기록하는가? | Arm Compute Complex, common contract, AP4→AP16 |
| 05.2 | [Topology와 device mechanism](05-comparison/02-topology-device-mechanisms.md) | CMN/NI·GIC·SMMU·power·HIPC를 QVP에서 어떻게 구현하는가? | SMB, multiple views, power, HIPC packet |
| 05.3 | [Evidence와 실패 진단](05-comparison/03-evidence-and-diagnosis.md) | standalone PASS와 FVP comparison은 무엇이 다른가? | provenance gate, assertion coverage, boot/service/case 경계 |

05.1은 model 개발자와 firmware/OS 담당자가 공통 baseline을 합의하는 데 사용한다.
05.2는 source를 따라 control/data/IRQ 경로를 검토할 때,
05.3은 실행 보고서의 PASS·FAIL·BLOCKED·UNSUPPORTED 의미를 판단할 때 사용한다.

## 먼저 기억할 비교 기준

| 질문 | 이 장에서 사용하는 기준 |
|---|---|
| FVP와 QBox의 내부 실행 엔진이 같아야 하는가? | Fast Models와 TCG/SystemC의 구현은 다르며 guest-visible 동작을 비교한다 |
| 같은 source이면 image도 같은가? | machine override, DTB, boot package, persistent state를 따로 확인한다 |
| SCP와 SMD는 같은 domain인가? | SCP는 SI CL0 firmware, SMD는 shared resource domain이다 |
| CPU 모델의 AE 이름이 모든 safety 회로를 뜻하는가? | functional detector/delivery 경로와 physical ECC/CRC/DCLS/PING coverage를 구분한다 |
| QVP named profile에 FVP가 항상 필요한가? | 현재 allowlist는 standalone을 허용하며 reference를 주면 엄격한 gate를 적용한다 |
| QVP PASS로 FVP 미지원 기능의 동등성을 주장하는가? | QVP 독립 증거와 FVP `UNSUPPORTED` / `NOT_COMPARABLE` 경계를 함께 남긴다 |

현재 local snapshot은 cfg2, AP4, SI CL0 1 functional PE, SI CL1 4 PE다.
기본 QVP는 RSE helper를 포함해 QemuInstance 다섯 개를 사용하지만 firmware domain은 네 개다.
FVP의 physical block diagram, QVP module 수, OS가 보는 CPU 수는 각각 다른 비교 단위다.

## 발표에서 연결할 세 사례

1. **GIC multiple views:** management view 설정, runtime view의 접근 권한, 실제 CPU INTID delivery를 분리해 읽는다.
2. **CPUFreq/CPUIdle:** SCMI performance 상태와 PSCI/PPU power 전이, host TCG 처리량을 구분한다.
3. **HIPC:** packet은 shared SRAM/vring에 있고 MHU는 notification을 전달한다. Attach와 buffer 반환까지 확인한다.

연결해서 읽기: [QBox object 생성](04-qbox/02-qemu-instance-construction.md),
[QBox 주소·시간](04-qbox/04-address-time-transport.md),
[Component SW Architecture](06-component-software-architecture.md),
[System SW Core](07-system-software-core.md).

주요 source: [Arm Components](../../../arm-zena-css/documentation/design/components.rst),
[QVP platform README](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/README.md),
[reference policy](../../../scripts/validation/apollo_validation/reference_policy.py),
[reference 검증 구현](../../../scripts/validation/apollo_validation/fvp_reference.py).
