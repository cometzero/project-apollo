# I5 - Fault, Safety, Watchdog Event Plane 구현 계획

## 목적

fault source, record/aggregation, interrupt 또는 reset sink, clear/recovery를 한
사건 흐름으로 관찰하고 검증한다.

## 구현 범위

- 소유 저장소는 `hsoc-stack/tools/qbox-platform`이다.
- 기존 FMU/SSU 모델에 test-only fault source와 JSON observer를 연결한다.
- 우선 SMMU fault를 EVTQ/SMMU IRQ/FMU observer로 연결한다.
- 근거가 확보된 순서로 APU violation, SI DCLS와 AP secure watchdog 수직 slice를
  추가한다.
- watchdog은 WS0/WS1, RGM request/ack, AP CPU0~CPU3 reset과 backing-store
  preserve/clear 정책을 명시한다.
- `components/**` firmware 소스는 변경하지 않는다.

## 최소 검증

- 구현한 source 하나를 inject해 sink가 한 번 발생함
- clear/ack 뒤 IRQ와 상태가 정상으로 복구됨
- fault disabled 시 sink side effect가 없음
- 관련 unit target 후 `./local_build.sh qbox`

## 완료 조건과 보고서

event observer가 source, request/fault ID, sink, clear와 recovery 순서를 기록해야
한다. placeholder 또는 register 저장만으로는 완료하지 않는다.

- 보고서: `i5-fault-safety-completion-2026-07-16-ko.md`
