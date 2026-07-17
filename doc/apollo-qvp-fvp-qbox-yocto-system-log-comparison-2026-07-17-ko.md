# Apollo QVP Yocto 이미지 FVP/QBox 시스템 로그 비교 보고서

- 작성일: 2026-07-17
- 대상: `apollo-qvp`, RD-Aspen CFG2, Primary Compute 4 CPU
- 범위: RSE, Safety Island CL0, Safety Island CL1, TF-A/OP-TEE,
  Primary Compute
- 목적: 같은 Yocto 산출물로 FVP와 QBox를 부팅해 QBox 구현의 수정 후보를
  식별하고 1차 원인을 분석한다.
- 상태: 비교, fidelity 개선, local/Yocto 통합 검증 완료

## 1. 결론

두 플랫폼 모두 RSE, SI0, SI1, TF-A/OP-TEE, U-Boot, Linux 순으로 부팅했고
Primary Compute 4 CPU 및 `apollo-qvp login:`까지 도달했다. 이전에 관찰됐던 SI1
PFDI timeout은 이번 QBox Yocto 실행에서 재발하지 않았다.

다만 FVP와 동등한 시스템 기능으로 보기에는 다음 수정이 필요하다.

| 우선순위 | 도메인 | QBox 차이 | 1차 원인 | 확신도 |
| --- | --- | --- | --- | --- |
| P0 완료 | SI1 ↔ AP | SI1 `RPMSG Endpoint: ATTACHED` 미도달 | live MHU peer 연결 및 HIPC SRAM AP reset 보존으로 해결 | 확인 완료 |
| P1 완료 | AP ↔ RSE | RSE online measured boot 5개 항목 미수신 | 실제 MHU2 peer를 기본 경로로 전환하고 RSE ATU용 AP flash physical bridge를 추가해 해결 | 확인 완료 |
| P1 완료 | AP ↔ RSE | U-Boot `psa_fwu_query: -140`, FWU ABI 미검출 | 임시 AP FIP logical file alias가 동적 RSE ATU mailbox window를 shadow함; alias를 제거해 해결 | 확인 완료 |
| P1 완료 | SI0 ↔ AP | `40050000.mhu` RX IRQ에서 channel 미검출 | MBX clear에서 combined IRQ deassert를 동기 반영해 해결 | 확인 완료 |
| P2 완료 | SI0 | CMN-CYPRUS r0p0 및 축약 node graph | r3p0 6×4 XP와 CFG2 child node graph를 구현해 해결 | 확인 완료 |
| P2 완료 | Primary Compute | SMMU 48-bit/축약 IDR profile | MMU-720AE 52-bit PA walk와 CFG2 IDR capability profile을 구현해 해결 | 확인 완료 |
| P2 완료 | TF-A/Primary Compute | 16-frame GICR footprint 및 ITS collection 차이 | 16개 register footprint와 ITS collection entry size 2를 구현해 해결 | 확인 완료 |
| P2 완료(지원 범위) | Primary Compute | Cortex-A720AE feature register 차이 | QEMU TCG가 실제 지원하는 QARMA3/FGT/ECV/PAN/WFx와 AArch64-only EL0를 구현 | 확인 완료 |
| P3 완료 | Primary Compute | PL011 rev1, FVP는 rev3 | 재사용 PL011에 revision property를 추가하고 Apollo를 rev3로 설정 | 확인 완료 |
| P3 완료 | Primary Compute | QBox의 vdc/vdd가 각각 64 MiB | device enumeration은 유지하고 backing capacity를 0으로 맞춤 | 확인 완료 |

완료된 통신 및 capability 항목 외의 차이는 현재 4 CPU 부팅을 막지 않는다. 성능 수치와 절대
timestamp는 에뮬레이터 특성 차이이므로 판정 기준에 포함하지 않았다.

## 2. 원자적 커밋 결과

비교 실행 전에 기존 변경을 owning repository별로 Conventional Commit 및
`Signed-off-by`가 있는 원자적 커밋으로 정리했다.

### 2.1 QBox core

| commit | 내용 |
| --- | --- |
| `d6b5e13d76bb` | `feat(tlm): propagate request context` |
| `ed46e5a5298d` | `test(smmuv3): expand translation coverage` |
| `d0be52e078e8` | `feat(pci): support fixed device slots` |
| `949a3029fa3b` | `feat(cpu): add co-simulation hold` |

### 2.2 QBox platform

| commit | 내용 |
| --- | --- |
| `1d7b867badd1` | `feat(ni710ae): enforce access policy` |
| `8865ae0d17dc` | `feat(fmu): model fault event flow` |
| `ff5424772a0f` | `fix(cc3xx): protect identification registers` |
| `813b12613b8c` | `feat(mhu): harden shared-memory transport` |
| `4d5ed1442d6c` | `feat(apollo): integrate fidelity profiles` |

### 2.3 최상위 repository

| commit | 내용 |
| --- | --- |
| `f83938495612` | `build(apollo): update fidelity models` |
| `ee9e3b027d37` | `feat(apollo): add fidelity validation` |
| `fbf65d1f5f7c` | `docs(apollo): record fidelity completion` |

커밋 후 QBox core, QBox platform과 최상위 worktree가 모두 clean임을 확인했다.
이 보고서는 사용자가 요청한 커밋 이후 조사 산출물이므로 위 커밋에는 포함하지
않았다.

## 3. 비교 조건과 재현 명령

### 3.1 활성 Yocto 설정

- build directory: `build/`
- machine: `apollo-qvp`
- image: `nexios-image`
- TMPDIR: `build/tmp_baremetal`
- variant: `RD_ASPEN_VARIANT = "cfg2"`
- Primary Compute CPU: `PC_CPUS_COUNT_DEFAULT = "4"`

커밋된 QBox provider는 비교 전에 다음 명령으로 다시 빌드했다.

```bash
source layers/poky/oe-init-build-env build
bitbake qbox-apollo-qvp-native
```

결과는 1,056 task 전부 성공이다. 6개의 forced-task taint warning은 있었지만
configure, compile, check, install, sysroot 및 SPDX task 실패는 없었다.

### 3.2 동일 산출물 통제

비교 root는
[`build/apollo-qvp-system-comparison-20260717-r1`](../build/apollo-qvp-system-comparison-20260717-r1/)이다.
FVP와 QBox가 서로의 writable disk를 변경하지 않도록 실행 전 같은 deploy WIC를
각각 복제했다. 복제 직후 세 WIC의 SHA-256은 다음과 같이 같았다.

```text
1408fa24bfe49b2fa9e7bff685cb3455209531863140b4ea35143b6b263a8d99c7
```

두 실행은 같은 deploy directory의 RSE/SI/AP firmware를 사용했다.

| 산출물 | 실행 전 SHA-256 |
| --- | --- |
| `rse-rom-image.img` | `ec460d392dc5f04872c373ce8094dcf14906296091b2f16bae8f65dbd00a99c7` |
| `rse-flash-image.img` | `ded2e42a019259f58f69245496c0129a015e9a17c9c822da21cb3b5e6f44213a` |
| `rse-otp-image.img` | `f5e6b0caab5c84e5fca4d9f79ef5b1cd84c6385c436ce2f07b20f818702b43f5` |
| `ap-flash-image.img` | `a9aeaa6a4584959050fcccf5d1c51af6bca74978d0687aa2666a5e99a1e43425` |
| `si0_ramfw.bin` | `99e04a35967cd43d25dd1b3727da620e57938e0f92c0a8bd657f9d15fd0394f6` |
| `zephyr-demos-cl1.bin` | `cdf22bd67ffad11373c499b2a71010cf0f3bc8a55be003643344e6fcd75a2bf5` |
| provisioning message | `b35cd92e3973f011713e01c20c552845d20ac1b6a7d4e639179b7fda6fae55d4` |

EFI capsule disk는 플랫폼별 기존 생성 방식을 보존했기 때문에 FVP와 QBox hash가
각각 `4549400a...`와 `473884e3...`로 다르다. 두 로그 모두 capsule update를
수행하지 않았으므로 아래 차이의 원인으로 보지 않았다.

### 3.3 FVP 실행

```bash
./run_fvp.sh --machine apollo-qvp \
  --fvpconf build/apollo-qvp-system-comparison-20260717-r1/inputs/fvp-comparison.fvpconf \
  --out-dir build/apollo-qvp-system-comparison-20260717-r1/fvp \
  --session apollo-fvp-system-compare-r1 --no-attach
```

약 4분 후 `apollo-qvp login:`을 확인하고, 추가 로그 flush 시간을 둔 뒤 session을
종료했다.

### 3.4 QBox 실행

```bash
./run_qbox_yocto.sh --machine apollo-qvp --headless --exit-after-pass \
  --timeout 600 \
  --out-dir build/apollo-qvp-system-comparison-20260717-r1/qbox \
  --rootfs build/apollo-qvp-system-comparison-20260717-r1/inputs/qbox-rootfs.wic \
  --efi-capsule-disk build/apollo-qvp-system-comparison-20260717-r1/inputs/qbox-efi.img \
  --no-copy-disks
```

[`qbox/result.json`](../build/apollo-qvp-system-comparison-20260717-r1/qbox/result.json)은
`passed: true`, blocker 없음, G0/G4 pass다. 실행 시간은 약 62초였으며
`apollo-qvp login:`까지 도달했다.

### 3.5 로그 대응

| 도메인 | FVP | QBox |
| --- | --- | --- |
| RSE | [`rse.log`](../build/apollo-qvp-system-comparison-20260717-r1/fvp/uarts/rse.log) | [`qbox-rse.log`](../build/apollo-qvp-system-comparison-20260717-r1/qbox/qbox-rse.log) |
| SI0 | [`safety_island_cl0.log`](../build/apollo-qvp-system-comparison-20260717-r1/fvp/uarts/safety_island_cl0.log) | [`qbox-safety-island-cl0.log`](../build/apollo-qvp-system-comparison-20260717-r1/qbox/qbox-safety-island-cl0.log) |
| SI1 | [`safety_island_cl1.log`](../build/apollo-qvp-system-comparison-20260717-r1/fvp/uarts/safety_island_cl1.log) | [`qbox-safety-island-cl1.log`](../build/apollo-qvp-system-comparison-20260717-r1/qbox/qbox-safety-island-cl1.log) |
| TF-A/OP-TEE | [`tf_a.log`](../build/apollo-qvp-system-comparison-20260717-r1/fvp/uarts/tf_a.log) | [`qbox-secure-console.log`](../build/apollo-qvp-system-comparison-20260717-r1/qbox/qbox-secure-console.log) |
| U-Boot/Linux | [`u_boot_linux.log`](../build/apollo-qvp-system-comparison-20260717-r1/fvp/uarts/u_boot_linux.log) | [`qbox-primary-console.log`](../build/apollo-qvp-system-comparison-20260717-r1/qbox/qbox-primary-console.log) |

## 4. 도메인별 분석

### 4.1 RSE: online measured boot가 실제 RSE로 전달되지 않음

offline measured boot 결과는 양쪽에서 모두 같다.

```text
BL1_2, BL2, SI_CL1, SI_CL0, AP_BL2, RT_0
```

그러나 `SCMI Comms subscribed to power state notifications` 이후 FVP RSE에는
다음 AP boot-stage 측정값이 추가되지만 QBox RSE에는 없다.

```text
FW_CONFIG
SECURE_RT_EL3
HW_CONFIG
SECURE_RT_EL1_SPMD
BL_33
```

Arm Zena CSS boot 문서는 AP의 각 boot stage가 online measured boot API로 MHU를
통해 RSE runtime에 측정값을 전달해야 한다고 정의한다
([`boot_process.rst:150`](../arm-zena-css/documentation/design/boot_process.rst#L150)).

QBox의 기본 AP-RSE 경로는
[`system_mgmt.lua:442`](../hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/system_mgmt.lua#L442)에서
`QBOX_RDASPEN_RSE_PS_PROXY` 기본값을 `true`로 두고, 실제 RSE pair인
`ap_s_to_rse`/`rse_to_ap_s` 대신 두 frame 모두 `ap_rse_ps_proxy`에 연결한다.
`rse-ps-proxy` protocol은
[`mhu320ae.h:2013`](../hsoc-stack/tools/qbox-platform/systemc-components/mhu320ae/include/mhu320ae.h#L2013)에서
request를 host에서 읽고 reply를 합성한 뒤 return한다. 반면 live RSE의 MHU2는
[`rse.lua:482`](../hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/rse.lua#L482)에서
실제 pair와 `doorbell-bridge`로 대기한다.

따라서 현재 구조는 OP-TEE Protected Storage 사용을 host proxy로 가능하게 하지만,
같은 architectural AP-RSE MHU를 사용하는 online measured boot request가 RSE
firmware에 도달하지 않는 것으로 판단한다.

수정 방향은 live RSE 실행에서 AP PBX/MBX를 RSE MHU2와 실제 pair로 연결하고
shared memory, IRQ, response를 firmware가 소유하게 하는 것이다. 임시 PS proxy가
필요하다면 measured-boot channel까지 종단하지 않도록 transport/service를
분리해야 한다. 단순히 환경 변수를 끄는 것만으로 PS 회귀가 없는지는 별도 확인이
필요하다.

RSE의 다음 warning은 양 플랫폼에 동일하므로 QBox 수정 대상이 아니다.

```text
tfm_builtin_key_loader_init: Skipping key_id 7fff816f ...
due to 40000015 platform error
```

#### 4.1.1 구현 결과: 완료

AP-RSE 기본 경로를 host `rse-ps-proxy` 대신 실제 `ap_s_to_rse`/`rse_to_ap_s`
MHU2 pair와 `doorbell-bridge`로 전환했다. 실제 경로의 첫 시험에서는 AP가 보낸
128-channel measured-boot packet이 RSE MHU2 MBX까지 도달했지만, RSE runtime이
`0x703ab000`에서 BusFault를 일으켰다.

QEMU exception trace와 `tfm_s.elf` 심볼/구조체를 대조한 결과 이 주소는 PS가 아니라
RSE의 AP flash 논리 주소 `0x703a6000`에 FWU metadata replica offset `0x5000`을
더한 값이었다. RSE ATU는 이를 architected physical address `0x38005000`으로
정상 변환했지만, `host_ap_flash`가 AP 논리 router에만 연결돼 system router에서
접근할 수 없어 downstream address error가 발생했다.

다음과 같이 수정했다.

- `system_to_ap_flash_bridge`를 추가해 RSE ATU의 system-physical AP flash 접근을
  기존 `host_ap_flash` 인스턴스와 같은 상태로 연결했다.
- address map에 `system_ap_flash`를 `ap_flash`의 physical alias로 기록했다.
- `QBOX_RDASPEN_RSE_PS_PROXY` 기본값을 `false`로 바꿔 실제 RSE firmware가
  AP-RSE service request와 response를 소유하도록 했다.
- MHU doorbell packet은 마지막 notify channel에서만 combined IRQ를 commit하도록
  실제 AP-RSE/RSE MHU2 path에 한정해 적용했다. 중간 data channel write마다
  불완전 packet을 소비하는 race를 방지한다.

변경 파일은 다음과 같다.

- `hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/ap_compute.lua`
- `hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/address_map.lua`
- `hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/system_mgmt.lua`
- `hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/rse.lua`
- `hsoc-stack/tools/qbox-platform/systemc-components/mhu320ae/include/mhu320ae.h`
- `hsoc-stack/tools/qbox-platform/tests/components/mhu320ae/mhu320ae-tests.cc`
- `scripts/test/validate_qbox_apollo_fvp_full_map.py`

정적/빌드 검증은 다음과 같이 통과했다.

```text
luac -p platforms/apollo/hw-block/{ap_compute,address_map,system_mgmt}.lua
PASS

python3 scripts/test/validate_qbox_apollo_fvp_full_map.py --check memory
PASS

cmake --build build/local-apollo-qvp/work/qbox-platform \
  --target apollo_fvp_full_system mhu320ae-tests --parallel 8
PASS

ctest --test-dir build/local-apollo-qvp/work/qbox-platform \
  -R '^mhu320ae-tests$' --output-on-failure
PASS
```

환경 변수 override 없이 새 기본 경로로 다음 full-system 시험을 수행했다.

```text
python3 scripts/run/run_qbox_apollo_fvp_full.py \
  --si-mode live-cl0-cl1 --skip-build --timeout 180 \
  --out-dir build/qbox-apollo-qvp/fidelity-p1-rse-default-live-path-20260717

passed: True
blocker: none
G0: pass
G4: pass
```

RSE 로그에서 offline 측정값 6개와 FVP에 있던 online 측정값 5개를 모두 확인했다.

```text
offline: BL1_2, BL2, SI_CL1, SI_CL0, AP_BL2, RT_0
online : FW_CONFIG, SECURE_RT_EL3, HW_CONFIG, SECURE_RT_EL1_SPMD, BL_33
```

같은 실행에서 `[PS] Encryption alg: 0x5500200`, 4 CPU Linux,
`apollo-qvp login:`, SI1 `RPMSG Endpoint: ATTACHED`도 유지됐다. OP-TEE의
`psa_call: -140/-134`는 비교 FVP에도 있던 기존 service 초기화 오류와 같은
범주이며 새 경로로 악화되지 않았다. 검증 근거는
[`summary.txt`](../build/qbox-apollo-qvp/fidelity-p1-rse-default-live-path-20260717/summary.txt),
[`qbox-rse.log`](../build/qbox-apollo-qvp/fidelity-p1-rse-default-live-path-20260717/qbox-rse.log),
[`qbox-primary-console.log`](../build/qbox-apollo-qvp/fidelity-p1-rse-default-live-path-20260717/qbox-primary-console.log)에 있다.

#### 4.1.2 FWU ABI/ATU routing 구현 결과: 완료

실제 RSE MHU 경로를 사용한 뒤 U-Boot에서 `FWU: ABI version 1.0 detected`가
사라지고 secure console에 `psa_fwu_query: ... -140`이 남는 문제를 추가로
추적했다. QEMU initiator와 SystemC router에 일시적인 read trace를 넣어 최초
오류 access를 확인한 결과, RSE firmware가 ATU region 10에 다음 동적 변환을
설정한 직후 `0x703ea000`을 읽고 있었다.

```text
logical : 0x703ea000..0x70409fff
physical: 0xfffe0000..
```

그러나 router는 이 access를 priority 0의 `rse_ap_fip_logical` direct file alias로
보내고 있었다. 해당 alias는 `0x703ad000`부터 `0x240000` 범위를 넓게 점유하므로,
priority 10의 실제 RSE ATU target과 겹쳐 동적으로 설정된 FWU mailbox window를
가렸다. alias priority를 일시적으로 낮춘 진단 실행에서 실제 ATU가
`0x703ea000 -> 0xfffe0000`으로 변환하고 FWU ABI가 즉시 복구돼 원인을 확정했다.

수정은 임시 `rse_ap_fip_logical` file alias를 Apollo Lua에서 제거하고 모든 RSE
logical AP FIP/mailbox access가 실제 `rse_atu`와 system router를 통과하게 한
것이다. runner의 fidelity 상태도 `atu-systemc-route`로 바꾸고, 기본 실행에서
direct alias가 다시 생기지 않는 회귀 시험을 추가했다. 진단용 trace는 원인 확정
후 QBox core에서 제거했다.

변경 및 정적 검증 범위는 다음과 같다.

- `hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/ap_compute.lua`
- `scripts/run/run_qbox_fvp_rd_aspen_rse.py`
- `tests/test_run_qbox_fvp_rd_aspen_rse.py`

```text
luac -p hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/ap_compute.lua
PASS

python3 -m py_compile scripts/run/run_qbox_fvp_rd_aspen_rse.py
PASS

pytest -q tests/test_run_qbox_fvp_rd_aspen_rse.py \
  -k 'fast_boot_sram_dmi_uses_real_atu_ap_fip_path or ap_fip_logical'
2 passed, 12 deselected

python3 scripts/test/validate_qbox_apollo_fvp_full_map.py \
  --check memory \
  --out build/qbox-apollo-fvp/fwu-atu-map-validation.json
PASS

cmake --build build/local-apollo-qvp/work/qbox-platform \
  --target router ApolloRseCPU platforms-vp --parallel 8
PASS
```

priority override나 진단 환경 변수 없이 수행한 기본 full-system 실행도 통과했다.

```text
python3 scripts/run/run_qbox_apollo_fvp_full.py \
  --si-mode live-cl0-cl1 --timeout 600 --skip-build \
  --out-dir \
  build/qbox-apollo-fvp/fidelity-p1-rse-fwu-atu-route-fixed-20260717

passed: true
blocker: null
G0/G4: pass/pass
ap_fip_logical_aperture.enabled: false
rse_ap_fip_visibility: atu-systemc-route
```

동일 실행에서 다음 핵심 표식을 함께 확인했다.

```text
FWU: ABI version 1.0 detected
FWU: System booting in Regular State
smp: Brought up 1 node, 4 CPUs
apollo-qvp login:
PFDI service ready (4 CPUs)
RPMSG Endpoint: ATTACHED
```

근거는
[`result.json`](../build/qbox-apollo-fvp/fidelity-p1-rse-fwu-atu-route-fixed-20260717/result.json),
[`qbox-primary-console.log`](../build/qbox-apollo-fvp/fidelity-p1-rse-fwu-atu-route-fixed-20260717/qbox-primary-console.log),
[`qbox-safety-island-cl1.log`](../build/qbox-apollo-fvp/fidelity-p1-rse-fwu-atu-route-fixed-20260717/qbox-safety-island-cl1.log)에 있다.

### 4.2 Safety Island CL0: CMN-CYPRUS discovery topology 축약

SI0는 양쪽에서 초기화되고 AP power-on, SCMI 및 PFDI monitoring을 수행한다. 오류
로그는 없지만 CMN discovery 결과는 크게 다르다.

| 항목 | FVP | QBox |
| --- | ---: | ---: |
| revision | r3p0 | r0p0 |
| RN-SAM | 21 | 1 |
| HN-S | 8 | 8 |
| RN-D | 3 | 0 |
| RN-F | 8 | 1 |
| RN-I | 8 | 0 |
| CCG Request/Home/Link Agent | 2/2/2 | 0/0/0 |

Apollo Lua는
[`si_cl0.lua:512`](../hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/si_cl0.lua#L512)에서
revision이나 topology parameter 없이 `host_cmn_cyprus`를 생성한다. 모델은
[`host_cmn_cyprus.h:134`](../hsoc-stack/tools/qbox-platform/systemc-components/host_cmn_cyprus/include/host_cmn_cyprus.h#L134)에서
하나의 XP, 8 HN-S, 1 RN-SAM만 seed하며 revision 기본값도 0이다
([`host_cmn_cyprus.h:235`](../hsoc-stack/tools/qbox-platform/systemc-components/host_cmn_cyprus/include/host_cmn_cyprus.h#L235)).

현재 firmware boot에는 충분하지만 CMN configuration, RAS/MPAM, RN/CCG discovery
시험에는 FVP 동등하지 않았다.

#### 4.2.1 구현 결과: 완료

FVP SI0 discovery 로그의 6×4 XP, XP port 수, child node type, physical ID,
logical ID를 CFGM→XP→node register graph로 구현했다. 단순 로그 합성이
아니라 SI0 firmware가 기존 CMN discovery code로 실제 TLM register tree를
순회한다. 21개 RN-SAM은 기존 range-comparison capability와 writable
SAM register를 공유하고, 8개 HN-S와 MPAM view, RN-D/RN-I, RN-F port
type, CCG Request/Home/Link agent를 FVP CFG2 배치와 맞춰다.

변경 범위는 다음과 같다.

- `hsoc-stack/tools/qbox-platform/systemc-components/host_cmn_cyprus/include/host_cmn_cyprus.h`
- `hsoc-stack/tools/qbox-platform/tests/components/host_cmn_cyprus/host_cmn_cyprus-tests.cc`
- `hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/si_cl0.lua`

단위시험은 root XP 24개와 discovery count
`21/8/3/8/8/2/2/2`, r3p0 revision, RNSAM feature register 및 firmware
programming write 보존을 검사한다.

```text
cmake --build build/local-apollo-qvp/work/qbox-platform \
  --target host_cmn_cyprus-tests apollo_fvp_full_system --parallel 8
PASS

ctest --test-dir build/local-apollo-qvp/work/qbox-platform \
  --output-on-failure -R '^host_cmn_cyprus-tests$'
1/1 PASS
```

실제 full-system 검증
[`fidelity-p2-cmn-r3p0-topology-20260717`](../build/qbox-apollo-qvp/fidelity-p2-cmn-r3p0-topology-20260717/summary.txt)은
`passed: true`, blocker 없음이다. SI0 로그에서 FVP와 동일한 다음
signature를 확인했다.

```text
CMN-CYPRUS revision: r3p0
Total RN-SAM nodes: 21
Total HN-S nodes: 8
Total RN-D nodes: 3
Total RN-F nodes: 8
Total RN-I nodes: 8
Total CCG Request/Home/Link Agent nodes: 2/2/2
```

같은 실행에서 SCMI notification, RSE online measured boot, 4 CPU Linux,
login, SI1 RPMSG를 모두 유지했고 MHU RX warning은 0건이었다.

### 4.3 Safety Island CL1: PFDI는 정상, HIPC/RPMSG는 미연결

FVP와 QBox 모두 다음 marker를 출력한다.

```text
PFDI Agent setup complete
PFDI service ready (4 CPUs)
Network interface configured
```

이전 QBox의 `PFDI status timed out`와 `ret=-116`은 이번 실행에서 없었다. 그러나
FVP는 6.99초에 다음 marker를 추가로 출력하고 QBox는 출력하지 않는다.

```text
veth_rpmsg: RPMSG Endpoint: ATTACHED
```

일반 QBox runner가 login 직후 종료해 marker를 놓친 가능성을 배제하기 위해 같은
이미지로 180초 focused diagnostic을 추가 실행했다. 다음 marker를 필수 pass
조건으로 지정했지만 timeout으로 종료됐다.

```text
qbox_required_pass_marker_timeout:...qbox-safety-island-cl1.log:
RPMSG Endpoint: ATTACHED
```

진단 결과는
[`qbox-rpmsg-diagnostic/result.json`](../build/apollo-qvp-system-comparison-20260717-r1/qbox-rpmsg-diagnostic/result.json),
trace는
[`ap-si-mhuv3-trace.log`](../build/apollo-qvp-system-comparison-20260717-r1/qbox-rpmsg-diagnostic/ap-si-mhuv3-trace.log)와
[`si-cl1-mhuv3-trace.log`](../build/apollo-qvp-system-comparison-20260717-r1/qbox-rpmsg-diagnostic/si-cl1-mhuv3-trace.log)에 있다.

원인은 Lua pair가 서로 다르기 때문이다.

| 방향 | AP frame | SI1 frame |
| --- | --- | --- |
| AP → SI1 | `pair=ap_si_cl1`, `protocol=doorbell` | `pair=apollo_ap_to_si_cl1`, `protocol=doorbell-bridge` |
| SI1 → AP | `pair=ap_si_cl1`, `protocol=doorbell` | `pair=apollo_si_cl1_to_ap`, `protocol=doorbell-bridge` |

AP 설정은
[`system_mgmt.lua:261`](../hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/system_mgmt.lua#L261),
SI1 설정은
[`si_cl1.lua:190`](../hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/si_cl1.lua#L190)에 있다.
trace에서도 AP PBX의 channel 0 write는 반복되지만 SI1 MBX에는 부팅 초기 clear만
있고 대응하는 `doorbell-signal`이 없다.

Arm HIPC 문서는 AP와 SI1이 512 KiB shared memory의 resource table, 두 vring과
RPMsg buffer를 공유하고 MHUv3로 signaling해야 한다고 정의한다
([`hipc.rst:87`](../arm-zena-css/documentation/design/hipc.rst#L87)).

수정 시 `ctx.apollo_live_cl1`에서 다음과 같이 실제 peer를 교차 연결해야 한다.

```text
AP PBX pair=apollo_ap_to_si_cl1  -> SI1 MBX
SI1 PBX pair=apollo_si_cl1_to_ap -> AP MBX
protocol=doorbell-bridge
```

live mode에서는 AP frame의 synthetic resource-table seed와 RPMSG name-service
injection을 끄고, 실제 shared SRAM 및 guest firmware가 소유하는 resource table과
vring을 사용해야 한다. service-model mode의 기존 `ap_si_cl1` 합성 경로는 별도
profile로 유지할 수 있다.

#### 4.3.1 구현 결과: 완료

AP frame의 live pair를 실제 SI1 pair와 교차 연결하고, live mode에서는 host의
resource-table seed와 RPMsg name-service 합성을 비활성화했다. MHU trace에서 AP의
attach doorbell `0x8`이 SI1 MBX에 도달하고, SI1의 acknowledge `0x4`가 AP MBX에
돌아오는 것을 확인했다.

첫 peer 연결 시험에서는 AP remoteproc attach까지만 진행됐다. 추가 추적 결과
SI1이 AP reset release 전에 `0x00100000` backing에 생성한 resource table을
`host_ap_bl2_header_sram`의 AP system reset 및 `init_mem` 동작이 다시 0으로
지우고 있었다. 이 backing은 실제로 `E0130000` HIPC window의 512 KiB 공유
메모리이므로 다음과 같이 수정했다.

- `ap_system_reset_bind_targets()`에서 HIPC backing reset을 분리했다.
- HIPC backing의 `init_mem`을 `false`로 두어 AP reset에서 보존했다.
- address map과 software contract에 `preserve_on_ap_reset`을 명시했다.
- service-model mode의 기존 합성 경로는 그대로 유지했다.

변경 파일은 다음과 같다.

- `hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/system_mgmt.lua`
- `hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/config.lua`
- `hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/ap_compute.lua`
- `hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/address_map.lua`
- `hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/software_contract.lua`
- `scripts/run/run_qbox_apollo_fvp_full.py`
- `scripts/test/validate_qbox_apollo_fvp_full_map.py`

검증 결과는 다음과 같다.

```text
python3 scripts/test/validate_qbox_apollo_fvp_full_map.py --check irq,reset
PASS

./local_build.sh qbox
PASS (apollo_fvp_full_system 100%)

python3 scripts/run/run_qbox_apollo_fvp_full.py \
  --si-mode live-cl0-cl1 --skip-build --timeout 180 \
  --out-dir build/qbox-apollo-qvp/fidelity-p0-live-hipc-rpmsg-marker-20260717
passed: True, blocker: none
```

최종 로그에서 다음 실제 guest-owned 경로를 확인했다.

```text
[00:00:18.480,000] <inf> veth_rpmsg: RPMSG Endpoint: ATTACHED
rproc-virtio rproc-virtio.2.auto: assigned reserved memory node vdev0buffer@160000
virtio_rpmsg_bus virtio6: rpmsg host is online
virtio_rpmsg_bus virtio6: creating channel ethsi1 addr 0x400
brsi1: port 1(ethsi1) entered forwarding state
apollo-network-setup: configured brsi1/ethsi1
```

검증 근거는
[`summary.txt`](../build/qbox-apollo-qvp/fidelity-p0-live-hipc-rpmsg-marker-20260717/summary.txt),
[`qbox-safety-island-cl1.log`](../build/qbox-apollo-qvp/fidelity-p0-live-hipc-rpmsg-marker-20260717/qbox-safety-island-cl1.log),
[`qbox-primary-console.log`](../build/qbox-apollo-qvp/fidelity-p0-live-hipc-rpmsg-marker-20260717/qbox-primary-console.log)에 있다.
SI1 PFDI service와 4 CPU Linux login도 유지됐고 PFDI timeout/error는 없었다.
이 marker를 live CL1 runner의 필수 pass 조건에도 추가해 이후 회귀가 login 성공에
가려지지 않도록 했다.

### 4.4 TF-A/OP-TEE: 직접 부팅 오류는 동일, GICR footprint가 다름

BL2, BL31, OP-TEE secure partition 초기화와 Normal World handoff는 두 플랫폼에서
완료된다. 다음 로그는 양쪽에 공통이므로 QBox 고유 회귀가 아니다.

- ASLR seed 없음
- insecure OP-TEE configuration warning
- SMM Gateway service discovery `error -4` 및 console fallback
- secure storage remove `psa_call: -140`

마지막 secure storage remove 오류는 FVP에서 두 번, QBox에서 한 번 발생하지만
같은 service initialization 실패 경로이며 부팅 결과에는 차이가 없다.

반면 OP-TEE의 redistributor 탐색은 FVP가 16 CPU hardware footprint를 노출하는
반면 QBox는 활성 frame 하나만 로그에 나타낸다. Linux에서도 QBox만 다음 메시지를
출력한다.

```text
GICv3: No redistributor present @(____ptrval____)
```

QBox는
[`config.lua:508`](../hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/config.lua#L508)에서
전체 footprint를 16으로 선언하지만 active count는 현재 CPU 수 4에 결합한다.
[`ap_compute.lua:308`](../hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/ap_compute.lua#L308)은
QEMU GIC에 active 4개만 생성하고 나머지 aperture는 inactive memory로 보낸다.
따라서 firmware/OS가 전체 range를 probe할 때 redistributor register가 없는 frame을
만난다.

ITS collection table도 FVP는 32,768 entry/entry-size 2, QBox는 8,192
entry/entry-size 8이다. 현재 CPU0~3의 redistributor와 LPI pending table은 모두
정상 생성되므로 4 CPU 기능 blocker는 아니다. 우선 4 CPU를 유지하되 16-frame
hardware footprint와 GICR_TYPER/ITS capability register를 FVP와 맞추는 것이
수정 방향이다.

#### 4.4.1 구현 결과: 완료

4 CPU 실행 조건은 유지하면서 Apollo가 노출하는 16개 redistributor aperture를
모두 GICR register footprint로 구현했다. 비활성 CPU4~15 frame은 architected
`GICR_TYPER` affinity 값을 반환하고 canonical DT region 단위로 `Last=1`을
보고한다. 반면 OP-TEE가 사용하는 연속 multiview aperture에서는 마지막 CPU15
frame에서만 `Last=1`이 되도록 두 탐색 규칙을 분리했다. 초기 구현에서 모든
canonical region을 하나의 연속 range로 취급하자 Linux가 다음 region까지 계속
탐색하여 `gic_iterate_rdists()`에서 translation fault가 발생했으며, 이를 재현하는
실패 단위시험을 추가한 뒤 region별 종료 의미로 수정했다.

ITS collection table entry size도 Apollo FVP가 보고하는 2 byte로 설정하고 QEMU ITS가
고정 8 byte 대신 machine property의 entry size로 collection entry를 접근하도록
변경했다. 이 값은 GIC architecture에서 구현 정의인 collection table format을
Apollo integration에 맞춘 것이다.

```text
ctest --test-dir build/local-apollo-qvp/work/qbox-platform \
  --output-on-failure -R '^gicx00-multiview-tests$'
1/1 PASS (11 tests)

GICv3: 16 PPIs implemented
GICv3: DirectLPI feature enabled
ITS ... allocated 32768 Interrupt Collections ... (flat, esz 2, ...)
```

전체 QBox 실행은
[`debug-ap-gicr-last-fixed-20260717`](../build/qbox-apollo-qvp/debug-ap-gicr-last-fixed-20260717/summary.txt)에서
`passed: true`이며 4 CPU online, Linux login, SI1 PFDI service와 live RPMSG
attachment를 모두 유지했다. 실패 구현의 kernel panic 근거는
[`debug-ap-verbose-current-20260717`](../build/qbox-apollo-qvp/debug-ap-verbose-current-20260717/qbox-primary-console.log)에
남겨 원인과 수정의 인과관계를 보존했다.

### 4.5 Primary Compute

#### 4.5.1 간헐적 MHU combined IRQ warning

초기 QBox 비교에서 다음 warning이 발생했다.

```text
arm-mhuv3-mailbox 40050000.mhu:
Failed to find channel for the RX interrupt
```

`0x40050000`은 ATU를 거쳐 live SI0의 `host_ap_si_ns_scmi_mhu_mbx`에 연결된다
([`system_mgmt.lua:182`](../hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/system_mgmt.lua#L182)).
Linux warning은 combined IRQ handler가 실행됐지만 enabled channel status를 하나도
찾지 못할 때 발생한다
([`arm_mhuv3.c:966`](../hsoc-stack/components/primary_compute/linux/drivers/mailbox/arm_mhuv3.c#L966)).

QBox MHU model은 status를 바꾼 후 combined IRQ update를 zero-time event로 예약한다
([`mhu320ae.h:934`](../hsoc-stack/tools/qbox-platform/systemc-components/mhu320ae/include/mhu320ae.h#L934)).
diagnostic trace에는 같은 SystemC timestamp에서 다음 순서가 반복된다.

```text
doorbell-signal status=0x1
doorbell-clear  status=0x0
```

따라서 QEMU/Linux가 IRQ를 관찰할 때는 status가 이미 clear된 순서 경쟁이 1차
원인이었다. 기능 손실은 관찰되지 않았고 SCMI protocol은 초기화됐다.

##### 4.5.1.1 구현 결과: 완료

MHU MBX의 최종 pending status를 guest가 clear하는 MMIO transaction에서 combined
IRQ deassert를 동기적으로 반영했다. IRQ assert는 기존처럼 SystemC zero-time
event를 통해 QEMU boundary 밖에서 반영하되, 이미 assert된 level을 clear할 때는
guest IRQ handler가 EOI하기 전에 line이 low가 되도록 했다. 이로써 GIC가
이미 빈 MHU channel의 level IRQ를 다시 pending으로 잡는 경로를 제거했다.

변경 범위는 다음 QBox platform model과 단위시험으로 한정했다.

- `hsoc-stack/tools/qbox-platform/systemc-components/mhu320ae/include/mhu320ae.h`
- `hsoc-stack/tools/qbox-platform/tests/components/mhu320ae/mhu320ae-tests.cc`

단위시험은 notify channel을 포함한 모든 MBX status를 clear한 즉시, 추가
`sc_start()` 없이 IRQ line이 low인지 검사하도록 강화했다.

```text
cmake --build build/local-apollo-qvp/work/qbox-platform \
  --target mhu320ae-tests apollo_fvp_full_system --parallel 8
PASS

ctest --test-dir build/local-apollo-qvp/work/qbox-platform \
  --output-on-failure -R '^mhu320ae-tests$'
1/1 PASS
```

동일 조건으로 3회 cold boot한 결과는 모두 `passed: true`, blocker 없음이며
warning은 0건이다.

- [`run1`](../build/qbox-apollo-qvp/fidelity-p1-mhu-sync-deassert-run1-20260717/summary.txt)
- [`run2`](../build/qbox-apollo-qvp/fidelity-p1-mhu-sync-deassert-run2-20260717/summary.txt)
- [`run3`](../build/qbox-apollo-qvp/fidelity-p1-mhu-sync-deassert-run3-20260717/summary.txt)

세 실행 모두 SCMI notification 초기화, RSE online measured boot 5개,
Primary Compute 4 CPU, `apollo-qvp login:`, SI1 `RPMSG Endpoint: ATTACHED`를
유지했다.

#### 4.5.2 SMMU capability profile

```text
FVP : ias 52-bit, oas 52-bit (features 0x01fcdfcf)
QBox: ias 48-bit, oas 48-bit (features 0x00080f8c)
```

FVP는 32-bit SID 중 25-bit만 stream table이 덮는다는 메시지를 출력하지만 QBox는
SID size 자체가 작아 해당 메시지도 없다. QBox MMU-720AE core는 IDR0을 S1P,
AArch64 translation 및 coherency의 최소 subset으로, IDR1 queue/SID 값을 고정하고
IDR5를 48-bit OAS로 고정한다
([`mmu720ae_core.h:94`](../hsoc-stack/tools/qbox-platform/systemc-components/mmu720ae/include/mmu720ae_core.h#L94)).

현재 PCIe DMA translation/fault 경로는 동작하지만 52-bit address, PRI/MSI/ATS 및
larger SID capability는 FVP와 다르다. register 값을 먼저 과장해서 광고하면 guest가
미구현 경로를 사용하므로, feature별 동작과 test를 추가한 뒤 IDR bit를 단계적으로
활성화해야 한다.

##### 4.5.2.1 구현 결과: 완료

재사용 QBox `smmuv3` 모델을 Apollo MMU-720AE CFG2 profile에 맞췄다. Apollo
instance는 `pamax=52`, `sidsize=32`를 사용하며, 2-level stream table, HTTU access
및 dirty update, CD2L, SEV, HYP, attribute override, FWB, RIL, BBM level 2를
advertise한다. IDR5의 OAS/VAX만 52-bit로 표시하는 데 그치지 않고 page-table walk
내부 `PA_BITS`와 IPS decode도 52-bit로 확장했다. 따라서 기존 48-bit truncation을
남긴 채 capability만 과장하지 않는다.

변경 파일과 단위검증은 다음과 같다.

- `hsoc-stack/tools/qbox/systemc-components/smmuv3/include/smmuv3.h`
- `hsoc-stack/tools/qbox/tests/components/smmuv3/smmuv3-bench.h`
- `hsoc-stack/tools/qbox/tests/components/smmuv3/smmuv3-tests.cc`
- `hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/config.lua`

```text
cmake --build hsoc-stack/tools/qbox/build \
  --target smmuv3-tests --parallel 8
PASS

ctest --test-dir hsoc-stack/tools/qbox/build \
  -R '^smmuv3-tests$' --output-on-failure
1/1 PASS

cmake --build build/local-apollo-qvp/work/qbox-platform \
  --target smmuv3 --parallel 8
PASS
```

단위시험은 52-bit OAS/VAX, 2-level stream table과 추가 IDR capability뿐 아니라
내부 PA/IPS 상한이 52-bit인지 검사한다. local-build DTB에는 SMMU node가 없어
Linux probe 문자열이 나오지 않지만, 동일 Yocto 이미지의 최종 QBox 부팅에서는
FVP와 정확히 같은 다음 결과를 확인했다.

```text
arm-smmu-v3 1c0000000.iommu: ias 52-bit, oas 52-bit \
  (features 0x01fcdfcf)
arm-smmu-v3 1c0000000.iommu: 2-level strtab only covers 25/32 bits of SID
```

근거는
[`qbox-primary-console.log`](../build/qbox-apollo-fvp/final-yocto-validation-r3-20260717/qbox-primary-console.log)에
있다.

#### 4.5.3 Cortex-A720AE feature profile

FVP에만 보이는 대표 기능은 architected QARMA3 authentication, MTE, asymmetric
tag fault, enhanced counter virtualization/CNTPOFF, EPAN, FGT, WFx timeout,
MPAM/MPAM virtualization과 AMU다. QBox에는 IMP DEF authentication과 32-bit EL0
support가 추가로 보인다.

QBox-local QEMU의 `cortex-a720ae`는
[`cpu64.c:1114`](../hsoc-stack/tools/qemu/target/arm/tcg/cpu64.c#L1114)에서 A710
model을 상속하고 PARANGE를 48-bit, MIDR를 A720AE r0p0로 덮어쓰는 수준이다.
따라서 이름과 MIDR는 맞지만 A720AE architectural feature ID register profile은
완전하지 않다. 4 CPU 기능을 우선하되 FVP ID register dump를 기준으로 지원 가능한
TCG feature를 명시적으로 설정하고, 미지원 기능은 문서화해야 한다.

##### 4.5.3.1 구현 결과: 지원 가능한 범위 완료

QEMU `cortex-a720ae` profile에서 AArch64-only EL0, FGT, ECV/CNTPOFF, PAN3,
WFxT를 명시하고 QBox CPU wrapper의 pointer authentication을 architected QARMA3로
설정했다. 변경 후 기존 QBox에만 있던 `32-bit EL0 Support`와 `IMP DEF algorithm`은
사라졌고, FVP와 같은 다음 discovery 결과를 얻었다.

```text
Address authentication (architected QARMA3 algorithm)
Enhanced Counter Virtualization (CNTPOFF)
Enhanced Privileged Access Never
Fine Grained Traps
Generic authentication (architected QARMA3 algorithm)
WFx with timeout
```

MTE는 QEMU가 tag memory 없는 외부 SystemC RAM에서 realize 시 안전하게 제거하며,
AMU/MPAM은 현재 QEMU TCG가 구현하지 않아 ID register 값만 광고하지 않았다. 이 세
항목은 기능 모델이 추가될 때까지 명시적 fidelity 부채다.

검증 실행
[`fidelity-p2-capability-profile-20260717`](../build/qbox-apollo-fvp/fidelity-p2-capability-profile-20260717/qbox-primary-console.log)은
4 CPU와 login을 유지했고, FVP/QBox CPU feature 집합 차이는 MTE, asymmetric MTE,
AMU, MPAM/MPAM virtualization 5개로 축소됐다.

#### 4.5.4 PL011 revision

Linux는 FVP에서 `PL011 rev3`, QBox에서 `PL011 rev1`을 검출한다. Apollo는 generic
QEMU `pl011`을 사용하며 QEMU model의 PrimeCell ID 배열은 고정돼 있고 revision
property가 없다
([`pl011.c:99`](../hsoc-stack/tools/qemu/hw/char/pl011.c#L99)).
현재 console 기능에는 영향이 없지만 register fidelity를 위해 upstream-friendly한
ID/revision property 또는 Apollo용 compatible type이 필요하다.

##### 4.5.4.1 구현 결과: 완료

재사용 `uart-pl011` SystemC component에 기본값 1인 CCI `revision` parameter를
추가하고 PID2 revision nibble을 instance별로 생성하도록 했다. Apollo secure,
primary 및 direct-primary UART만 revision 3으로 설정해 다른 platform의 기존
동작은 유지했다.

```text
cmake --build build/local-apollo-qvp/work/qbox-platform \
  --target pl011-aperture-tests --parallel 8
PASS

ctest --test-dir build/local-apollo-qvp/work/qbox-platform \
  -R '^pl011-aperture-tests$' --output-on-failure
1/1 PASS

1a400000.serial: ... is a PL011 rev3
```

단위시험은 기본/alias PrimeCell aperture의 PID2가 모두 `0x34`인지 검사했고,
full-system 결과는 위 capability 실행 로그에서 확인했다.

#### 4.5.5 추가 virtio block device

FVP U-Boot은 `virtio-blk#3/#4 not ready`를 출력하고 Linux의 vdc/vdd 용량은 0이다.
QBox runner는
[`run_qbox_fvp_rd_aspen_rse.py:5596`](../scripts/run/run_qbox_fvp_rd_aspen_rse.py#L5596)에서
64 MiB sparse file 두 개를 항상 만들어 vdc/vdd를 실제 block device로 노출한다.
이는 enumeration 안정화를 위한 runner 정책 차이이며 부팅 blocker는 아니다.
FVP와 정확히 맞추려면 zero-capacity device semantics를 모델링하거나 disk numbering
의존을 제거한 뒤 두 device 생성을 생략해야 한다.

##### 4.5.5.1 구현 결과: 완료

FVP와 device enumeration 순서를 유지하기 위해 virtio-blk#2/#3 device 자체는
남기되 runner가 생성하는 backing file을 0 byte로 바꿨다. U-Boot과 Linux의 관찰
결과가 다음과 같이 FVP와 같아졌다.

```text
Disk virtio-blk#2 not ready
Disk virtio-blk#3 not ready
virtio_blk virtio2: [vdc] 0 512-byte logical blocks (0 B/0 B)
virtio_blk virtio3: [vdd] 0 512-byte logical blocks (0 B/0 B)
```

근거는
[`qbox-primary-console.log`](../build/qbox-apollo-fvp/fidelity-p2-capability-profile-20260717/qbox-primary-console.log)이며,
동일 실행은 `passed: true`, G0/G4 pass, 4 CPU 및 Linux login을 유지했다.

## 5. 수정 우선순위와 최소 검증 기준

### 단계 1: live SI1 HIPC 연결

상태: **완료**. 상세 구현 및 검증 근거는 4.3.1에 기록했다.

- AP/SI1 PBX-MBX pair와 protocol을 live peer 기준으로 교차 연결한다.
- live mode의 synthetic RPMSG seed/injection을 비활성화한다.
- 최소 검증:
  - `PFDI service ready (4 CPUs)` 유지
  - SI1 `RPMSG Endpoint: ATTACHED` 확인
  - AP 측 remoteproc/RPMsg endpoint 확인
  - PFDI timeout 4종 미검출

### 단계 2: AP-RSE 실제 MHU 및 online measured boot

상태: **완료**. 상세 원인, 구현 및 검증 근거는 4.1.1에 기록했다.

- AP-RSE request를 RSE MHU2와 shared memory로 전달한다.
- PS proxy를 제거하거나 service별 임시 경로로 격리한다.
- 최소 검증:
  - RSE offline 측정값 6개 유지
  - RSE online 측정값 5개 모두 확인
  - OP-TEE secure storage boot path가 기존보다 악화되지 않음

### 단계 3: MHU IRQ ordering

상태: **완료**. 구현과 3회 cold boot 검증 근거는 4.5.1.1에 기록했다.

- MBX status와 combined IRQ level의 관찰 순서를 보장한다.
- 최소 검증:
  - 3회 QBox cold boot
  - `Failed to find channel for the RX interrupt` 0회
  - SCMI 초기화와 Linux login 유지

### 단계 4: capability/topology fidelity

상태: **완료**. CMN r3p0 graph, SMMU 52-bit profile, GICR/ITS footprint,
지원 가능한 A720AE TCG feature, PL011 rev3와 zero-capacity block placeholder를
구현했다.

우선 CMN r3p0 graph, SMMU IDR/profile, GICR/ITS footprint를 구현한다. CPU feature,
PL011 revision, block placeholder는 그 다음에 처리한다. 각 항목은 boot 성능이
아니라 register/discovery signature와 기존 기능 회귀만 검사한다.

### 단계 5: local 및 Yocto 통합 검증

상태: **완료**.

정식 local QBox build와 full-system 검증 결과는 다음과 같다.

```text
./local_build.sh qbox
PASS (qbox-configure/qbox-build)

python3 scripts/run/run_qbox_apollo_fvp_full.py \
  --si-mode live-cl0-cl1 --timeout 600 --skip-build \
  --out-dir build/qbox-apollo-fvp/final-local-validation-20260717

passed: true
blocker: null
G0/G4: pass/pass
```

Yocto provider와 image도 같은 source tree에서 다시 빌드했다.

```text
source layers/poky/oe-init-build-env build
bitbake qbox-libqemu-native qbox-apollo-qvp-native
PASS (1059 tasks, all succeeded)

./yocto_build.sh
PASS (7293 tasks, all succeeded)
```

Yocto sysroot에 설치된 `platforms-vp`와 `apollo-qvp.lua`, 새 `nexios-image`를
사용한 최종 실행도 통과했다.

```text
./run_qbox_yocto.sh --machine apollo-qvp --headless \
  --timeout 600 --exit-after-pass --copy-disks \
  --out-dir build/qbox-apollo-fvp/final-yocto-validation-r3-20260717

passed: true
blocker: null
G0/G4: pass/pass
```

최종 Yocto 로그에서 FWU ABI 1.0/Regular State, 4 CPU, SMMU 52-bit exact
signature, ITS 32,768 collection/entry-size 2, QARMA3/ECV/FGT/WFxT, PL011 rev3,
zero-capacity vdc/vdd, Linux login과 SI1 PFDI/RPMsg를 모두 확인했다. 다음 회귀
패턴은 0건이다.

- `Failed to find channel for the RX interrupt`
- `No redistributor present`
- `psa_fwu_query`
- `Kernel panic`, `BusFault`
- PFDI timeout 4종

통합 runner의 정상 로그 fixture에도 새 live SI1 RPMsg 필수 조건을 반영했다.
실제 판정 조건을 완화하지 않고 `RPMSG Endpoint: ATTACHED`가 누락되면 실패하는
음성 회귀 테스트를 추가했다. 관련 runner 테스트와 정적 audit 결과는 다음과 같다.

```text
pytest -q tests/test_run_qbox_fvp_rd_aspen_rse.py \
  tests/test_run_qbox_apollo_fvp_full.py
48 passed

ctest --test-dir hsoc-stack/tools/qbox/build --output-on-failure \
  -R '^(router-coverage-tests|smmuv3-tests)$'
2/2 passed

ctest --test-dir build/local-apollo-qvp/work/qbox-platform \
  --output-on-failure \
  -R '^(gicx00_multiview-tests|host_cmn_cyprus-tests|mhu320ae-tests|rse_atu-tests|pl011-aperture-tests)$'
5/5 passed

python3 scripts/test/validate_qbox_apollo_fvp_full_map.py
PASS

python3 scripts/test/audit_qbox_core_boundary.py
PASS

python3 scripts/test/audit_qbox_apollo_fvp_full_coverage.py \
  --result-json \
    build/qbox-apollo-fvp/final-yocto-validation-r3-20260717/result.json \
  --output \
    build/qbox-apollo-fvp/final-yocto-validation-r3-20260717/full-coverage-audit.json
PASS
```

구현 완료 상태는
[`apollo-qvp-machine-architecture-ko.md`](apollo-qvp-machine-architecture-ko.md),
[`qbox-fvp-emulation-project.md`](qbox-fvp-emulation-project.md)와 QBox-platform
Apollo README에도 동기화했다. 따라서 기존의 “whole-system comparison backlog”,
축약 CMN graph와 service-modeled SI1 표기는 더 이상 현재 상태로 남아 있지 않다.

근거는
[`result.json`](../build/qbox-apollo-fvp/final-yocto-validation-r3-20260717/result.json),
[`qbox-primary-console.log`](../build/qbox-apollo-fvp/final-yocto-validation-r3-20260717/qbox-primary-console.log),
[`qbox-rse.log`](../build/qbox-apollo-fvp/final-yocto-validation-r3-20260717/qbox-rse.log),
[`qbox-safety-island-cl0.log`](../build/qbox-apollo-fvp/final-yocto-validation-r3-20260717/qbox-safety-island-cl0.log),
[`qbox-safety-island-cl1.log`](../build/qbox-apollo-fvp/final-yocto-validation-r3-20260717/qbox-safety-island-cl1.log),
[`full-coverage-audit.json`](../build/qbox-apollo-fvp/final-yocto-validation-r3-20260717/full-coverage-audit.json)에
있다.

## 6. 판정에서 제외한 차이

다음은 QBox 수정 필요성의 직접 근거로 사용하지 않았다.

- ASLR 주소, EFI allocation 주소, RTC timestamp
- systemd unit 시작 순서와 wall-clock 부팅 시간
- xor throughput 등 에뮬레이터 성능 수치
- 양쪽에 공통인 OP-TEE/SMMGW/FF-A warning
- FVP model 자체 stdout의 topology 및 ManagerID warning
- writable WIC의 부팅 후 hash 변화

## 7. 최종 판정

현재 Apollo QBox는 동일 Yocto 이미지로 4 CPU full-system boot와 PFDI service를
완료하며, live SI1 HIPC와 AP-RSE measured boot도 실제 peer firmware까지 이어진다.
두 경로는 각각 guest-owned RPMsg endpoint와 RSE의 5개 online 측정값으로 검증했다.

MHU RX IRQ warning은 status/IRQ ordering을 보정한 후 3회 cold boot에서 제거했다.
CMN r3p0 graph, SMMU 52-bit profile, 16-frame GICR/ITS, 지원 가능한 A720AE
feature, PL011 rev3와 zero-capacity virtio placeholder도 구현했다. CPU의 MTE,
AMU와 MPAM은 외부 SystemC RAM tag storage 또는 QEMU TCG 기능 구현 없이 register
값만 광고하지 않았으며 명시적 잔여 fidelity 부채로 남긴다.

이 분석은 기존 PFDI 수정 보고서
[`apollo-qvp-fvp-qbox-non-ap-pfdi-analysis-2026-07-17-ko.md`](apollo-qvp-fvp-qbox-non-ap-pfdi-analysis-2026-07-17-ko.md)를
후속 확장하며, `hsoc-stack/components/**` 소스는 변경하지 않았다.
