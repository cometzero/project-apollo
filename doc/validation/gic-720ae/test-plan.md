# Apollo GIC-720AE FVP 대비 QBox 검증 계획

작성일: 2026-07-29

대상: Apollo cfg2, `apollo-qvp`, Primary Compute 4 CPU

## 1. 목적

FVP에서 활성화된 GIC-720AE 기능을 기준으로 QBox의 구현 상태를
`구현·검증 완료`, `부분 구현`, `미구현`, `현재 환경에서 검증 불가`로
분류한다. Arm 제품 최대 사양과 Apollo cfg2에서 실제 활성화된 기능은
분리한다.

Primary Compute는 Linux, Safety Island Cluster 0은 SCP-firmware, Safety
Island Cluster 1은 Zephyr에서 관측한다. 부팅 성공이나 Linux의 feature
문자열만으로 전체 기능 구현을 판정하지 않는다.

## 2. 기준 구성

| 항목 | 값 |
| --- | --- |
| Yocto machine | `apollo-qvp` |
| RD-Aspen variant | `cfg2` |
| Primary Compute CPU | 4 |
| Yocto TMPDIR | `build/tmp_baremetal` |
| QBox source | `hsoc-stack/tools/qbox/` |
| QBox platform | `hsoc-stack/tools/qbox-platform/` |
| local QEMU | `hsoc-stack/tools/qemu/` |
| Linux | `hsoc-stack/components/primary_compute/linux/` |
| SCP-firmware | `hsoc-stack/components/system_mgmt/scp-firmware/` |
| Zephyr | `hsoc-stack/components/system_mgmt/zephyrproject/` |

## 3. 판정 원칙

| 판정 | 기준 |
| --- | --- |
| 구현·검증 완료 | 활성 FVP 계약이 QBox 소스에 있고 해당 도메인의 실행 결과가 동작을 관측 |
| 부분 구현 | register/probe/boot 호환성은 있으나 핵심 동작, 상태 공유 또는 negative path가 없음 |
| 미구현 | 소스 경로가 없거나 명시적으로 storage/stub/정적 route만 존재 |
| 검증 불가 | 필요한 FVP 라이선스 문서, 테스트 stimulus, guest 장치 또는 실행 경로가 없음 |

테스트 결과가 `PASS`여도 해당 테스트의 관측 범위만 통과한 것으로
해석한다. 예를 들어 GIC feature 로그 비교 PASS는 discovery parity이지
MSI/LPI delivery 증명이 아니다.

## 4. 테스트 케이스

### TP-01 활성 구성 및 소스 기준선

- 명령:

  ```bash
  sed -n '1,240p' build/conf/local.conf
  sed -n '1,240p' build/conf/bblayers.conf
  sed -n '1,120p' build/conf/templateconf.cfg
  git -C hsoc-stack/tools/qbox rev-parse HEAD
  git -C hsoc-stack/tools/qbox-platform rev-parse HEAD
  git -C hsoc-stack/tools/qemu rev-parse HEAD
  ```

- PASS: cfg2, apollo-qvp, 4 CPU와 정확한 source SHA가 기록된다.

### TP-02 FVP/QBox memory map 및 topology 정적 검증

- 명령:

  ```bash
  python3 scripts/test/validate_qbox_apollo_fvp_full_map.py
  python3 scripts/test/audit_qbox_core_boundary.py
  python3 scripts/test/validate_qbox_apollo_topology.py
  ```

- PASS: 모든 validator가 종료 코드 0을 반환한다.
- 한계: 주소와 wiring을 검증하며 interrupt delivery는 검증하지 않는다.

### TP-03 QBox GIC compatibility component build/test

- 명령:

  ```bash
  # generated build tree의 원래 값은 BUILD_TESTING=OFF이다.
  cmake -S hsoc-stack/tools/qbox-platform \
    -B build/local-apollo-qvp/work/qbox-platform \
    -DBUILD_TESTING=ON
  cmake --build build/local-apollo-qvp/work/qbox-platform \
    --target gicx00_multiview-tests gic720ae_messreg-tests --parallel 4
  ctest --test-dir build/local-apollo-qvp/work/qbox-platform \
    -R '^(gicx00_multiview-tests|gic720ae_messreg-tests)$' -V
  cmake -S hsoc-stack/tools/qbox-platform \
    -B build/local-apollo-qvp/work/qbox-platform \
    -DBUILD_TESTING=OFF
  ```

- PASS: 재구성, 두 test executable의 소스 재빌드, 두 ctest가 종료 코드
  0이고 cache가 원래 `BUILD_TESTING=OFF`로 복원된다.
- 관측: register reset/read/write, bounds, synthetic redistributor,
  backend forwarding.
- 비관측: cross-view IRQ ownership, GIC state 공유, FuSa/RAS, message
  전달 의미론.

### TP-04 AP Linux FVP/QBox discovery parity

- 입력: 동일 계열 이미지로 생성된 FVP와 QBox Primary Compute console.
- 명령:

  ```bash
  python3 scripts/test/compare_qbox_fvp_gic_logs.py \
    --fvp-log <fvp-u-boot-linux.log> \
    --qbox-log <qbox-primary-console.log> \
    --expect-fvp-parity \
    --output <evidence-dir>/ap-linux-gic-parity.json
  ```

- PASS: 960 SPI, DirectLPI/RVPEID/Valid+Dirty discovery, GICv4.1 ITS,
  32768 collection, VPE invalidation marker가 비교 기준을 만족한다.
- 한계: 문자열 기반 discovery/init 비교이다.

### TP-05 AP Linux 실행 검증

- 기준 실행:

  ```bash
  python3 scripts/run/run_qbox_apollo_fvp_full.py --timeout 600
  ```

- 필수 관측:
  - 네 CPU redistributor와 CPU 0-3 online.
  - GIC/ITS 초기화 실패 없음.
  - `/proc/interrupts`의 알려진 source 전후 delta.
  - MSI/MSI-X 장치가 있으면 ITS/LPI vector delta.
  - MSI 장치가 없으면 해당 항목을 `검증 불가`로 기록.
- 선택 명령:

  ```bash
  python3 scripts/test/validate_qbox_apollo_pcie_irq_runtime.py \
    --msix-log <msix-runtime-log> \
    --intx-log <intx-runtime-log> \
    --output <evidence-dir>/ap-linux-pcie-irq.json
  ```

- PASS: 실제 source를 구동했을 때 대상 IRQ counter가 증가하고
  예상하지 않은 경로의 counter는 증가하지 않는다.
- 실행 경계: canonical full-system runner가 임의 post-login command를
  받지 않으므로, IRQ counter/affinity/hotplug 자극은 opt-in PCI profile
  또는 별도 공식 probe hook이 준비된 실행에서 수행한다.

### TP-06 Safety Island CL0 SCP-firmware

- 기준 실행: canonical full-system runner의 SI0 UART log.
- 필수 관측:
  - `GIC-multiview configured successfully`.
  - SCP framework/module 초기화 완료.
  - 가능하면 debugger CLI `test fmu`의 `test_inject_gic_fmu:PASS`.
  - 대표 CL0-owned interrupt 또는 MHU/timer handler 실행 증거.
- PASS:
  - 최소 boot-time multiview 초기화와 실제 handler/stimulus 하나가
    확인된다.
  - GIC FMU injection을 실행할 수 없으면 해당 기능은 완료 판정하지
    않는다.

### TP-07 Safety Island CL1 Zephyr

- 기준 실행: canonical full-system runner의 SI1 UART log.
- 필수 관측:
  - CPU 0-3 online.
  - Zephyr GICv3 redistributor/CPU interface 초기화에 성공.
  - scheduler SGI/IPI 또는 timer IRQ를 사용하는 SMP 동작.
  - 가능하면 Zephyr `smp` 및 `ipi_work` 테스트.
- 후보 build:

  ```bash
  ./local_build.sh zephyr
  ```

- PASS: 네 CPU와 최소 하나의 directed IPI 또는 timer-interrupt-to-IPI
  경로가 실행 로그로 확인된다.
- ITS/LPI는 SI View2 기준에 없으므로 baseline 요구사항이 아니다.

### TP-08 SI multiview negative/cross-view 검증

- 관측:
  - View0의 `GICR_VIEWR`, `GICD_IVIEWR`, `GICD_CTLR` 쓰기.
  - CL0-owned SPI는 CL0에만, CL1-owned SPI는 CL1에만 전달.
  - 반대 view에서는 delivery가 0.
- PASS: 하나의 공유 GIC state와 view policy가 실제 IRQ routing을
  제어한다.
- 현재 소스가 독립 SI0/SI1 GIC state이면 `미구현`으로 판정한다.

### TP-09 FuSa/RAS/real-time/power 기능

- 대상: FMU fault injection/record/ERI/CRI, GSPV, parity/CRC,
  Wake Request, Q/P channel, GICR power/wake, real-time SPI semantics.
- PASS: FVP 활성 구성 증거, QBox 동작 모델, targeted test가 모두 있다.
- 소스상 model이 없으면 `미구현`; confidential integration/safety
  정보가 필요한 세부 항목은 `검증 불가`로 분리한다.
- FVP는 cycle accurate가 아니므로 deterministic latency 수치 비교는
  범위 밖이다.

### TP-10 전체 결과 및 회귀

- 명령:

  ```bash
  python3 scripts/test/audit_qbox_apollo_fvp_full_coverage.py \
    --result-json <runtime-result.json> \
    --output <evidence-dir>/full-coverage-audit.json
  git diff --check
  ```

- PASS: coverage audit와 문서 diff check가 성공하고, 각 feature 판정이
  증거 파일 또는 명시적 blocker를 갖는다.

## 5. 실행 증거 위치

이번 실행의 생성 증거는
`build/qbox-apollo-qvp/gic-720ae-validation-20260729-195140/` 아래에
모은다. 기존 로그를 사용할 때는 원본 경로와 생성 시각을 함께 기록한다.

최종 판정은 `analysis.md`, 실행 결과는 `test-completion.md`에 기록한다.
