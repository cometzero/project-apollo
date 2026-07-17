# I3 - MMU-720AE와 SystemC SMMUv3 통합 계획

## 목적

Apollo의 MMU-720AE integration shell을 QBox의 reusable SMMUv3 translation
engine에 연결해 GPEX DMA의 정상 translation과 fault 경로를 실제화한다.

## 구현 범위

- QBox SMMUv3 모델의 linear STE/CD, 4 KiB stage-1 walk, CMDQ/TLBI, EVTQ를 먼저
  qualification한다.
- generic translation state owner는 하나만 두고 Apollo shell에는 integration
  ID, port/SID wiring, IRQ/RAS aggregation만 둔다.
- GPEX LTI00 요청과 page-table DMA를 AP canonical memory에 연결한다.
- `systemc-mmu720ae`와 대체 backend가 동시에 활성화되지 않도록 검증한다.
- translated DMI, stage-2, two-level STE와 queue overflow는 후속으로 남긴다.

## 구현 결정

조사 결과 QBox 공용 `smmuv3`가 계획한 translation, CMDQ/TLBI, EVTQ 기능을
이미 하나의 상태 저장소로 구현하고 있었다. 따라서 Apollo 전용 C++ walker를
추가하지 않는다. `systemc-mmu720ae` backend 이름은 유지하되, Apollo Lua
integration shell이 공용 `smmuv3`와 `smmuv3_tbu`를 생성하고 MMU-720AE IIDR,
PAMAX, SID, LTI00, AP memory/PTW, SPI 65 결선을 소유한다. 기존
`mmu720ae` register-only C++ 모델은 active machine에서 제외하고 회귀 비교용으로
남긴다.

공용 모델이 제공하는 stage-2, two-level STE, 추가 granule과 translated DMI는
이번 단계의 검증 통과를 의미하지 않는다. I3 판정은 아래 최소 stage-1 범위로
제한한다.

## 최소 검증

- 4 KiB mapping DMA read/write 하나
- unmapped IOVA의 EVTQ/IRQ 하나와 downstream side effect 없음
- TLBI 뒤 stale translation 미사용 하나
- 관련 QBox/QBox-platform unit target 후 `./local_build.sh qbox`

## 완료 조건과 보고서

DMA ingress, translation, fault record와 IRQ가 동일 SID/IOVA를 가리켜야 한다.
지원하지 않는 SMMUv3 feature는 capability와 ledger에 명시한다.

- 보고서: `i3-mmu720ae-smmuv3-completion-2026-07-16-ko.md`
