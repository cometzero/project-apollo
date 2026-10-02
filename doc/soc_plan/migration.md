# Apollo QVP Lua 전환 순서와 검증

[설계안](README.md) · [현재 구조](current-structure.md) · [계획 리뷰](review.md) · [Lua 작성 지침](lua-style.md)

이 문서는 구현 전 전환 계획을 보존한다. 실제 완료 단계, 구현 차이와 검증 결과는 [구현·검증 기록](implementation.md)에 기록한다. 아래 baseline 분석을 새 구현의 runtime 증거로 사용하지 않는다.

## 1. 현재 파일에서 목표 파일로

경로는 Lua root `platforms/apollo/` 기준이다.

| 현재 | 이동/분리 대상 | 유지할 계약 |
|---|---|---|
| `apollo-qvp.lua` | 새 `apollo-qvp-saturn-v.lua` 및 `vp/debug.lua`, `vp/test-wiring/runtime-injection.lua` | 기존 entry는 forwarding; monitor/injection 조건과 경로 |
| `apollo-qvp-common.lua` | `soc/apollo.lua`, `vp/backends.lua`, board aggregator | AP/RoS 공용 재사용, 현재 audio 교체 결과 |
| `apollo-qvp-linux.lua` | entry 유지 + `vp/profiles/linux-direct.lua`, `vp/boot/linux.lua` | AP-only CPU, boot ABI, GIC/PSCI, stub 경계 |
| `apollo-qvp-qmp.lua` | `vp/debug.lua` 또는 그 하위 QMP module | domain별 instance/socket 경로, opt-in |
| `hw-block/config.lua` | `vp/options.lua`, 각 hardware owner의 상수/helper/reset 연결 | 환경변수 호환, 평가 시점, reset target 순서 |
| `hw-block/fabric.lua` | `soc/hw-block/fabric/fabric.lua` + `vp/qvp.lua` | router/addrtr map과 Container/quantum 분리 |
| `hw-block/ap_compute.lua` | `soc/hw-block/ap_compute/*` + `vp/boot`, `vp/qemu`, 시험 장치 | CPU/GIC/PCIe/SMMU 주소·IRQ·reset·instance |
| `hw-block/rse.lua` | `soc/hw-block/rse/*` + VP firmware/가속/backend | nested container, secure alias, crypto/flash backend |
| `hw-block/system_mgmt.lua` | `soc/hw-block/system_mgmt/*` | SMD map, counter, MHU pair, reset source |
| `hw-block/si_cl0.lua` | `soc/hw-block/si_cl0/*`, `si_common/interrupts.lua`, VP PMIC host | CL1/AP PPU 제어, GIC views, ATU 연결 |
| `hw-block/si_cl1.lua` | `soc/hw-block/si_cl1/*`, VP loader/console | shared window, HIPC/PFDI, reset ordering |
| `hw-block/ros.lua` | `soc/hw-block/ros/*`, `vp/virtio.lua`, Board EEPROM, VP loopback | 모든 MMIO target의 AP view 재연결 |
| `hw-block/pinctrl.lua` | `soc/hw-block/ros/pinctrl.lua` | bank/GPIO/peripheral gate; backend별 지원 한계 |
| `board/*.lua` | `board/saturn-v.lua`, `board/hw-block/*`, `vp/test-wiring/loopbacks.lua` | 부품 수·bus 주소·pullup/IRQ, 시험 배선의 선택 |
| `linux-boot/domains.lua` | `vp/mocks/domains.lua` | 지원하지 않는 protocol의 명시적 오류 응답 |

`linux-boot/`의 boot assembly, Python 도구, README는 Lua ownership 정리만을 이유로 이동하지 않는다. C++ 모델 소스/등록 라이브러리도 이번 구조 변경의 필수 수정 대상이 아니다.

## 2. 반드시 함께 확인할 소비자

| 소유 repository / 소비자 | 현재 의존 | 후속 변경 |
|---|---|---|
| `qbox-platform` Lua | `hw-block/*.lua` 고정 include | 파일 상대 literal 경로로 변경 |
| Root `run_qbox_yocto.sh`, `scripts/run/run_qbox_apollo_fvp_full*.{py,sh}`, `qbox_apollo_runtime.py` | full entry 기본 경로 | wrapper 기간에는 유지, 전환 시 canonical 경로 갱신 |
| Root `scripts/run/run_qbox_autosd.py`, `scripts/autosd_demo/build_minimal_qm.py` | process command에서 `apollo-qvp.lua` 문자열 식별 | old/new entry를 모두 full-system으로 인식 |
| Root `scripts/run/run_qbox_linux.py` | Linux entry | 경로 유지; module 이동 후 동작 확인 |
| `meta-hsoc-bsp`의 `qbox-apollo-qvp-native.bb` | 설치 파일 검사 및 provider.env의 `apollo-qvp.lua` | 새 canonical entry 반영, old wrapper도 설치 |
| `meta-hsoc-auto-solutions`의 `nexios-apollo-qboxboot.inc` | `QBOX_CONFIG:apollo-qvp` | `.qboxconf`에 새 entry 기록하는 전환 시 갱신 |
| Root `scripts/test/apollo_ap_map_lua.py` | literal `dofile`, entry-dir 하위 graph | include 규칙 유지; 신규 entry graph fixture 추가 |
| Root `scripts/autosd_dashboard/topology.py` | entry 이름, source allowlist, folder 기반 group | 새 경로 분류·entry 평가·source attribution 갱신 |
| Root `audit_qbox_apollo_ap_memory_map.py` | AP/RoS/config 고정 파일 및 합쳐 읽는 module 목록 | 모든 leaf/선택 backend가 검사 범위에 들어가게 수정 |
| Root `audit_qbox_apollo_lua_ownership.py` | `hw-block/*.lua` 비재귀 glob, basename 분류 | relative path 기준 재귀 수집, SoC/VP/Board owner 구분 |
| Root `validate_qbox_apollo_fvp_full_map.py` | 현재 파일/함수에 대한 regex | 구조 검사 경로 갱신, 주소/IRQ 기대값은 유지 |
| Root tests / 관련 PCIe·timer·PMIC/audio scripts | 파일 경로, source hash, 고정 함수명 | 해당 단계의 consumer와 fixture 갱신 |
| 플랫폼 README 및 `doc/qbox-fvp-emulation-project.md` | 현재 entry/구조/기능 설명 | 실제 구현 전환 시 반영 |

핵심 근거: [provider 설치](../../hsoc-stack/yocto/meta-hsoc-bsp/recipes-devtools/qbox/qbox-apollo-qvp-native.bb#L256), [image config](../../hsoc-stack/yocto/meta-hsoc-auto-solutions/recipes-core/images/include/nexios-apollo-qboxboot.inc#L7), [ownership auditor](../../scripts/test/audit_qbox_apollo_lua_ownership.py#L162), [AP map reader](../../scripts/test/audit_qbox_apollo_ap_memory_map.py#L655).

provider는 Apollo data tree를 복사하므로 하위 directory 자체는 설치할 수 있다. 그러나 entry의 존재 확인, provider manifest, deployed `.qboxconf`와 process 식별은 별개다. 소스 entry만 실행한 결과를 설치본 검증으로 대신하지 않는다.

## 3. 권장 단계

### 단계 0 — 기존 결과 고정

현재 source SHA, 선택 환경변수, final platform descriptor와 include graph를 저장한다. 새 wrapper가 새 entry를 호출한 뒤에 old/new를 비교하면 양쪽이 같은 코드가 되어 회귀를 검출할 수 없다. **리팩터링 전 descriptor snapshot** 또는 별도 읽기 전용 checkout을 비교 기준으로 사용한다.

descriptor baseline은 AP CPU 1/4/16, full-system/AP-only, monitor/QMP/injection 선택, 실제 지원하는 backend 조합별로 만든다. 동일 profile의 옵션과 파일 경로를 동일하게 맞춘다. 사용하지 않은 조합을 검증 완료로 표시하지 않는다.

source parser의 서식 의존도 먼저 재현한다. 현재 큰따옴표 `dofile(`, 세미콜론 table field, 4-space 객체 선언을 검사기가 가정하며 일부 문자열 결합도 공백에 민감하다. 연산자 공백 변경과 중첩 `if`, helper 추출/동적 생성으로 객체를 수집하지 못하면 해당 consumer를 evaluated descriptor 기반으로 전환하거나 지원 문법을 보강한다. 빈 수집 결과도 오류로 판단하고 실제 기존 object/address 집합을 비교한다. 모든 Lua 문법을 regex로 해석하는 새 parser는 만들지 않는다.

### 단계 1 — 새 entry와 경로 호환성

`apollo-qvp-saturn-v.lua`를 만들고 기존 full-system composition을 옮긴다. `apollo-qvp.lua`는 다음 형태로 forwarding한다.

```lua
local dir = debug.getinfo(1, "S").source:sub(2):match("(.*/)") or "./"
dofile(dir .. "apollo-qvp-saturn-v.lua")
```

이 단계에서는 기존 default profile, globals, 호출 순서, 객체명과 모든 기본값을 유지한다. entry를 직접 검사하는 validator는 wrapper graph를 따르도록 함께 수정한다. 초기에는 런처와 provider의 기존 entry 선택을 유지할 수 있다.

완료 조건: old wrapper/new entry가 기존 baseline과 동일한 최종 descriptor를 만들고, 기존 런처 테스트 및 include graph 검사가 통과한다.

### 단계 2 — domain별 파일 분리

AP → RoS/pinctrl → RSE → SMD → SI 순으로 작은 변경을 권장한다. 각 domain aggregator는 현재 `define/enable` 순서를 그대로 실행한다. `cpu/syscore/io_peri`부터 나누고 파일 크기와 기능 응집도에 따라 memory/PCIe/safety를 추출한다. SI 공용 interrupt helper는 중복 생성 없이 SoC aggregator에서 전달한다.

고정 파일을 읽는 검사기와 해당 tests를 각 이동에 함께 갱신한다. 테스트를 지우거나 수집 결과가 0개인 상태를 PASS로 만들지 않는다. 새 helper와 경로가 검사 범위에 포함되는지 확인한다.

완료 조건: descriptor 차이가 없고 native elaboration에서 CCI/socket/instance 오류가 없다. 모듈을 나누면서 runtime Container를 추가하지 않는다.

### 단계 3 — VP와 board 소유권 추출

환경·loader·console·QMP·monitor·VirtIO·backend·mock을 VP로, EEPROM/PMIC/expander/bus를 Board로 옮긴다. SI PMIC host는 VP extension으로 분리한다. 현재 runtime name은 유지한다. test loopback은 VP에서 기존 profile에 명시적으로 선택한다.

이후 globals를 `ctx`로 바꾸고 module load 시 옵션 의존 계산을 제거한다. `vp.prepare()`에서 backend와 instance 참조를 먼저 확정한 후 `soc.define()`이 최종 hardware descriptor를 생성한다. 마지막으로 생성 후 교체/삭제를 줄이는 `define/connect` API를 도입한다. 주소 view의 대상 목록에는 이동한 VirtIO/extension도 포함한다.

완료 조건: baseline descriptor 및 선택 profile의 guest traffic/IRQ/reset 동작을 비교한다. 바뀐 hardware 의미가 있으면 구조 변경과 별도 변경으로 기록한다.

### 단계 4 — 설치본과 canonical entry 전환

provider manifest와 image `.qboxconf`를 새 entry로 전환하고 old wrapper는 호환 경로로 남긴다. `.qboxconf`를 재생성하는 배포 작업까지 수행한다. AutoSD의 process 식별·topology source grouping과 fixture도 함께 갱신한다.

shared BitBake 실행 여부, `MACHINE=apollo-qvp`, 실제 `build/conf/{local.conf,bblayers.conf,templateconf.cfg}`를 확인한 뒤 직렬로 빌드한다. 구조 정리에 필요하지 않은 toolchain, firmware ABI, external layer 변경은 포함하지 않는다.

완료 조건: 설치본의 include graph가 sysroot/data tree 내부에서 해결되며 source checkout과 다른 cwd에서도 실행된다. 설치 경로로 실제 profile boot 및 요구되는 post-login 검증을 통과한다.

### 단계 5 — lint/format 정착

새 module에는 [Lua 작성 지침](lua-style.md)을 적용하고 기존 파일은 수정 범위에서 정리한다. Luacheck는 새/이전 완료 module부터 적용하며 legacy global 경고를 전체 허용으로 숨기지 않는다. source parser 보강과 수집 집합 동등성 검사가 통과한 뒤, 고정한 StyLua 버전으로 임시 복사본의 diff를 검토한다. formatter 적용은 파일 이동이나 동작 변경과 별도 변경으로 남긴다.

완료 조건: formatter 전후 include graph, 검사기가 수집한 object/address 집합, final descriptor가 같다. formatter의 AST 비교만으로 QBox source 소비자 호환성을 판정하지 않는다.

## 4. 검증 계약

### descriptor 비교

키를 정렬한 최종 `platform` scalar tree를 baseline과 비교한다. 숫자 key, 문자열 key, scalar type, 배열 순서를 보존하고 주소를 lossy number로 변환하지 않는다. root 외 globals 제거는 별도로 허용·검토하고, platform 객체의 차이는 숨기지 않는다. 비교에 반드시 포함할 항목:

- object path, `moduletype`, `dylib_path`, `dont_construct`, `construction_priority`.
- constructor `args`의 값과 순서, QemuInstance 참조, CPU 수/affinity/entry/reset.
- MMIO address/size/alias/backing, `relative_addresses`, translation base, decode priority.
- IRQ/PPI/SPI/GIC view, reset fanout의 target와 순서, MHU pair/shared window.
- I2C address/page alias, pinctrl gate, bus/peer/socket 방향, 선택 backend.
- loader image/address/order, trace/debug/monitor/QMP와 host IO 옵션.

파일별 source location만 비교에서 제외한다. 예상된 artifact 경로 차이를 정규화할 경우 필드 목록을 기록한다. socket 이름을 단순 정규식으로 찾는 Lua 평가 검사는 실제 C++ socket 존재·type·binding cardinality를 증명하지 못하므로 native elaboration을 별도로 확인한다.

### 정적/구성 검사

기존 검사기를 갱신한 뒤 workspace root에서 수행한다. 아래 예제는 QBox dependency와 맞는 Lua 5.4 도구를 명시적으로 요구한다. 이 문서 리뷰 환경의 기본 `lua`/`luac`는 5.1.5이며 5.4 검증을 대신하지 않는다.

```bash
python3 - <<'PY'
from pathlib import Path
import subprocess
subprocess.run(['luac5.4', '-v'], check=True)
for path in sorted(Path('hsoc-stack/tools/qbox-platform/platforms/apollo').rglob('*.lua')):
    subprocess.run(['luac5.4', '-p', str(path)], check=True)
PY

python3 -m pytest -q \
  tests/test_apollo_linux_lua.py \
  tests/test_qbox_pca9539_board.py \
  tests/test_apollo_ap_map_modular_lua.py \
  tests/test_autosd_topology.py

python3 scripts/test/validate_qbox_apollo_fvp_full_map.py \
  --out build/qbox-apollo-qvp/soc-refactor/full-map-validation.json
python3 scripts/test/audit_qbox_apollo_lua_ownership.py \
  --output build/qbox-apollo-qvp/soc-refactor/lua-ownership.json
```

기존 pytest 중 `lua`를 직접 선택하는 검사도 있으므로 실행 interpreter/version을 결과에 남긴다. 필요하면 후속 구현에서 명시적 interpreter 입력을 추가한다. 위 `luac5.4`가 없는 환경은 검사 생략을 PASS로 보고하지 않는다.

추가할 의미 있는 검사는 include cycle/missing/outside-root, **생성 직전 guard**의 중복 객체명 검출, 필수 board port 누락, I2C alias 충돌, profile 간 동일 이름의 다른 instance 참조, pre-refactor descriptor 비교다. table literal 중복 field는 lint로 검사하고 최종 descriptor에서 overwrite 이력을 복원하려 하지 않는다. layout을 그대로 복사한 문자열 snapshot test만 늘리지 않는다.

### native 및 guest 검증

구현 후 해당 machine의 유효 configuration과 build 동시 실행 여부를 확인한 뒤 다음을 순차 수행한다.

```bash
./yocto_build.sh --keep-conf qbox-apollo-qvp-native
./yocto_build.sh --keep-conf qbox-apollo-qvp-native -c check
```

| 범위 | 요구 evidence |
|---|---|
| native elaboration | 설치본 entry/include 로딩, module/CCI/socket/instance 오류 없음 |
| native 오류 전달 | 필수 port/backend 설정 오류를 주입했을 때 native nonzero 또는 runner FAIL; partial 구성 실행이나 timeout만 발생하면 통과 불가 |
| full-system | 실제 RSE → SCP/SI CL0 → AP firmware/Linux, SI CL1 firmware 실행 및 기존 결과 |
| AP-only | kernel/DTB/initrd boot, 1/4/16 CPU composition, mock 경계, 선택 disk |
| Board/IO | EEPROM read/write, PCA9539 GPIO/IRQ/reset, SI PMIC HAL readback, GPIO/UART/SPI/I2S traffic |
| cross-domain | HIPC/SCMI/PFDI, shared memory, IRQ view 및 관련 reset probe |
| debug | opt-in monitor/QMP, CPU/object 경로, runtime injection 켠 profile의 기존 sink 유지 |

full-system의 post-login qualification은 canonical [Python runner](../../scripts/run/run_qbox_apollo_fvp_full.py#L2546)의 `--post-login-probe`와 관련 probe를 사용한다. 실행 binary, installed Lua, 동일 machine의 firmware/image 경로는 검증 시 확인해 명시적으로 전달한다. `--conf`, `--qbox-build-dir`, image 인자와 환경을 result와 함께 보관한다. root `run_qbox_yocto.sh`의 headless login PASS는 post-login 검증 결과가 아니다.

결과는 `build/qbox-apollo-qvp/soc-refactor/<run>/`에 실행 명령, source/installed hash, descriptor diff, `result.json`, domain별 로그와 함께 저장한다. 각 항목은 `PASS/FAIL/SKIP/UNSUPPORTED`를 유지한다. 구조 분리와 boot PASS만으로 coherence, timing, power/reset 전체, Saturn-V 실물 또는 FVP parity를 선언하지 않는다.

## 5. 남는 결정과 기본 처리

| 미확정 항목 | 현재 설계의 기본 처리 |
|---|---|
| Saturn-V schematic/BOM, 실제 external memory population | 현 QVP 구성을 유지하고 실물 일치 `UNVERIFIED` |
| RoS DW peripheral을 AP로 통합할지 | `ros/` owner 유지; 하드웨어 소유권 확인 후 별도 결정 |
| 시험 loopback 기본 OFF 전환 | 기존 boot/probe 호환을 위해 현 profile에서는 유지 |
| CPU 16개 또는 대체 backend의 실제 runtime 자격 | 수행한 조합만 PASS, 미실행 조합은 SKIP |
| old entry 제거 시점 | 기존 소비자가 없어졌음을 확인하기 전까지 forwarding 유지 |

문서 작성 단계에서 위 사항의 결정을 기다릴 필요는 없다. 기존 동작을 유지하는 경계와 단계가 이미 정해져 있으며, 실물 board 사양을 변경하는 시점에만 추가 근거가 필요하다.
