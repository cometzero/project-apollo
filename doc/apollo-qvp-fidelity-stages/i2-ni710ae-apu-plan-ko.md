# I2 - NI-710AE APU Data-path 구현 계획

## 목적

RD-Aspen의 boot-time protection 정책을 실제 transaction verdict로 적용하는 APU
수직 경로를 만든다.

## 선행 Gate

NI-710AE APU의 공식 register offset, reset value, region encoding, lock 및 fault
side effect를 local Arm 문서 또는 공개 공식 문서에서 확인한다. 근거를 확보하지
못하면 register programming model은 구현하지 않고 해당 범위를 `blocked`로
보고한다. 유사 IP의 register를 추측해 대체하지 않는다.

## 구현 범위

- 소유 저장소는 `hsoc-stack/tools/qbox-platform`이며 generic 결함만 QBox에 둔다.
- reset 시 RSE 관리 경로만 허용하는 default-deny data path를 시험부터 고정한다.
- 근거가 확보된 범위에서 region, permission, lock과 violation record를 구현한다.
- `host_ni710ae_nci` discovery window와 실제 APU register owner를 연결한다.
- deny는 downstream side effect 없이 유한 TLM 오류를 반환하고 fault observer에
  동일 request ID를 남긴다.
- 초기 구현에서는 protected aperture의 DMI를 허용하지 않는다.

## 통합 검증에서 승인한 계획 조정

I7 실부팅에서 Cortex-R82가 보호 aperture의 코드 영역에 DMI를 사용하지 못하면
firmware 진행이 실용적으로 불가능함을 확인했다. 따라서 correctness를 약화하지
않는 범위에서 다음 항목을 I2 최종 구현에 포함한다.

- reset 상태는 owner/trusted context에만 downstream DMI를 허용한다.
- APU enable 뒤에는 downstream DMI 전체 범위가 하나의 허용 region 안에 있고
  read/write permission이 모두 충족될 때만 grant한다.
- APU enable 또는 실행 중 policy 변경은 protected aperture의 DMI를 다음 SystemC
  delta에 한 번만 무효화한다.
- 고정 security context가 명시된 CPU는 QEMU `MemTxAttrs`의 기본값보다 해당
  context를 우선한다.

## 최소 검증

- reset 상태 RSE allow 하나와 AP deny 하나
- programming 뒤 AP allow 하나
- lock 뒤 policy write deny 하나
- reset/programmed DMI allow와 non-secure DMI deny
- 관련 unit target과 `./local_build.sh qbox`
- I7 full-system 보호 경로 부팅 한 번

## 완료 조건과 보고서

공식 표로 증명된 reset/program/lock/deny 동작만 완료로 판정한다. 문서 미확보 시
부분 구현도 전체 I2 완료로 표시하지 않는다.

- 보고서: `i2-ni710ae-apu-completion-2026-07-16-ko.md`
