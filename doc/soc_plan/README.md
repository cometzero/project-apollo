# Apollo QVP Lua: SoC · VP · Saturn-V Board 분리 설계

작성 기준: 2026-10-02, 현재 checkout의 Lua 및 QBox loader 분석.
상태: 구조 분리와 관련 소비자 변경, Yocto 빌드·설치·부팅 검증을 완료했다. Full-system 기본 boot/post-login과 Board I/O, AP-only audio DMA/PIO는 통과했다. Full-system SPI/UART DMA와 AP-only BSP PFDI selftest 실패는 남아 있다. 실제 구현 차이와 검사별 판정은 [구현·검증 기록](implementation.md)을 기준으로 확인한다. 아래 설계 예제와 초기 분석은 설계 당시의 기록이다.

권장 구조는 `apollo-qvp-saturn-v.lua`가 **SoC hardware, QVP 실행 환경, Saturn-V board 구성을 명시적으로 조합**하는 방식이다. Device Tree의 `.dtsi` include와 board `.dts` 조합 방식을 참고하되, 기존 Lua module의 `return table`과 `define/connect` 함수를 사용한다. 별도 DSL이나 범용 overlay engine은 도입하지 않는다.

가장 중요한 구분은 **파일의 계층과 실행 객체의 계층**이다. 파일은 도메인별로 분리하지만 `platform.ap_cpu_0`, `platform.si_cl0_gic`, `platform.rse_cpu_pass.cpu_0` 등 현재 객체 경로는 유지한다. CCI·socket·monitor·runner가 이 경로를 사용하기 때문이다.

- [구현과 검증 기록](implementation.md): 적용한 파일 구조, 소비자 변경, 실행 증거와 제한.
- [변경 전 구조와 소스 근거](current-structure.md): 17개 Lua의 역할, 호출 순서, 결합 관계.
- [전환 단계와 검증](migration.md): 파일별 이동, 소비자 변경, 단계별 완료 조건.
- [계획 리뷰와 반영 사항](review.md): backend 선택 순서, 중복 정의, 오류 처리, 검사기 호환성.
- [Lua 작성·가독성 지침](lua-style.md): 공식 문서 조사, module 예제, naming/formatting/lint 적용 방안.

## 1. 설계 범위와 경계

| 계층 | 소유하는 내용 | 다른 계층에 전달하는 내용 |
|---|---|---|
| `soc/` | CPU, GIC, timer, mailbox, ATU, interconnect, SRAM, controller, pinctrl, 내부 reset/IRQ/주소 view | board 연결용 controller/pin 참조, VP가 사용할 CPU·memory·reset 참조 |
| `vp/` | QemuInstance, quantum/sync, backend 선택, 파일·console·network, 이미지 loader, 가속, monitor/QMP, 가상 장치와 firmware 대체 모델 | 실행 옵션, 모델 backend 선택, 부팅 profile, QVP 전용 확장 |
| `board/` | 외부 EEPROM·GPIO expander·PMIC, 외부 bus, board 배선·pull-up·주소 strap, 외부 메모리 장착 정보 | board resource 설정 및 SoC port와의 연결 |
| entry | 위 세 계층과 profile 선택, 구성 순서 | 최종 global `platform` table |

판단 기준은 구현 언어가 아니라 **무엇을 모델링하는가**이다. `cpu_arm_cortexA720AE`나 QEMU 기반 I2S도 SoC IP를 표현하면 SoC 정의에 속한다. 그 IP를 어느 QemuInstance/backend로 실행할지와 trace/pacing 정책은 VP 입력이다. 반대로 MMIO 주소가 있는 VirtIO와 firmware stub은 VP 구성이다.

공식 SoC 구분은 로컬 [Zena CSS 기능 블록](../arm_zena_css_dev_guide/05-functional-blocks-in-zena-css.md), [부팅 흐름](../arm_zena_css_dev_guide/06-boot-flow-of-zena-css.md)을 참고한다. 다만 이 문서는 **현재 Apollo QVP의 구조 개선안**이며 모든 QVP 확장을 Zena CSS hardware로 인정하는 재분류가 아니다.

### Saturn-V 명칭의 적용 범위

현재 `board/*.lua`는 PCA9539, TPS6594, EEPROM, 시험용 loopback을 구성한다. 분석한 파일에는 Saturn-V schematic/BOM에 대한 대응표가 없다. 따라서 새 이름은 우선 **현재 QVP board 구성을 담는 Saturn-V profile의 이름**으로 사용하고, 실물 부품·배선 일치 여부는 `UNVERIFIED`로 기록한다. 부품 추가나 배선 변경은 실제 board 근거를 확보한 후 별도 변경으로 진행한다.

특히 현재 SI CL0 PMIC용 I2C/GPIO 주소는 소스가 명시한 **QVP extension**이다. 이를 `soc/hw-block/si_cl0/io_peri.lua`로 옮겨 실제 SI peripheral인 것처럼 취급하지 않는다. 외부 TPS6594는 `board/`, 이 장치에 접근하기 위해 추가한 controller/GPIO는 `vp/extensions/`가 소유한다.

## 2. 권장 디렉터리

아래 경로는 모두 `hsoc-stack/tools/qbox-platform/platforms/apollo/` 기준의 **목표 구조**다. 현재 파일 목록은 별도 분석 문서에 있다. 파일은 해당 기능을 실제로 추출할 때 생성하며 빈 파일을 미리 만들지 않는다.

이 트리는 분리 가능한 책임의 목록이지 모든 파일을 즉시 만들어야 하는 목록은 아니다. 첫 단계는 domain aggregator와 응집된 leaf 몇 개로 시작한다. 하나의 변경을 위해 항상 함께 열어야 하는 작은 파일은 합치고, 서로 다른 owner·주소 view·변경 이유를 가진 코드를 분리한다. 구체적인 기준은 [파일 크기와 추상화 지침](lua-style.md#2-파일과-함수의-크기)을 따른다.

```text
apollo/
  apollo-qvp-saturn-v.lua       # 신규 full-system entry
  apollo-qvp.lua               # 기존 사용자용 forwarding entry
  apollo-qvp-linux.lua         # AP-only entry 유지, 같은 SoC module 재사용

  soc/
    apollo.lua                # SoC aggregator, domain 간 연결
    hw-block/
      fabric/
        fabric.lua            # system/SMD interconnect, 주소 domain 경계
      ap_compute/
        ap_compute.lua        # AP domain aggregator
        cpu.lua               # A720AE, affinity, CPU timer PPI
        syscore.lua           # GIC/ITS, timer, watchdog, SID 등
        memory.lua            # AP SRAM, DRAM aperture/alias
        io_peri.lua           # AP UART 등 domain 소유 peripheral
        pcie.lua              # RC/EPC, SMMU 연결 및 PCIe aperture
        safety.lua            # FMU, SBIST, RAS 경로
        address_view.lua      # AP logical/global address view 연결
      rse/
        rse.lua
        cpu.lua               # 기존 rse_cpu_pass 실행 계층 보존
        syscore.lua
        memory.lua
        security.lua          # OTP/KMU/LCM/SAM/CC3xx/MPC/PPC
        mailbox.lua
        io_peri.lua
      system_mgmt/
        system_mgmt.lua
        syscore.lua           # counter/PIK/SCR/RGM 등
        mailbox.lua           # AP/RSE/SI host-side MHU
        memory.lua
        interconnect.lua      # SMD ATU 및 주소 경로
        reset.lua             # system reset source 및 내부 fanout
      si_common/
        interrupts.lua        # CL0/CL1 공용 SI GIC view/IRQ 계약
      si_cl0/
        si_cl0.lua
        cpu.lua
        syscore.lua
        memory.lua
        mailbox.lua
        power.lua             # AP/SI PPU와 reset 연결
        safety.lua            # SSU/FMU/RAS
        interconnect.lua
      si_cl1/
        si_cl1.lua
        cpu.lua
        syscore.lua
        memory.lua
        mailbox.lua
        io_peri.lua
      ros/
        ros.lua               # 현재 RoS hardware 소유권을 우선 유지
        io_peri.lua           # DW I2C/SSI/UART/I2S, DMA350
        pinctrl.lua           # PERI0/PERI1 controller 및 SoC 내부 gate
        syscore.lua           # 기존 RoS의 RTC 등 실제 장치 정의

  vp/
    qvp.lua                   # Container, attach/finalize 실행 조합
    options.lua               # 환경변수/경로 파싱, validation
    profiles/
      full-system.lua         # 실제 RSE/SCP/Zephyr/AP firmware 구성
      linux-direct.lua        # AP-only 구성과 명시적 firmware substitutes
    qemu.lua                  # instance manager/instance, sync/debug 설정
    backends.lua              # SMMU/crypto/flash/audio backend 선택
    boot/
      full-system.lua         # firmware 파일 loader, 이미지 layout
      linux.lua               # boot stub/kernel/DTB/initrd loader
    io.lua                    # UART host backend, disk/net host resource
    virtio.lua                # VirtIO MMIO, disk/net/rng
    debug.lua                 # monitor, QMP, timer snapshot
    extensions/
      si-cl0-pmic-host.lua     # QVP 전용 I2C/GPIO MMIO 및 reset 연결
    mocks/
      domains.lua             # 현 linux-boot/domains.lua 기능
    test-wiring/
      loopbacks.lua           # GPIO/UART/I2S 시험 peer 연결
      runtime-injection.lua   # opt-in signal fault/injection service

  board/
    saturn-v.lua               # board aggregator와 SoC port 연결
    hw-block/
      i2c.lua                 # AP I2C0 및 SI PMIC bus 구성
      eeprom.lua              # 외부 EEPROM, address/page/write-cycle
      pca9539.lua             # GPIO expander 및 board pin 연결
      tps6594.lua             # 외부 PMIC, I2C alias/IRQ
      memory.lua             # 외부 DRAM/flash 장착 정보가 필요한 경우
```

`ros/`는 현재 하드웨어를 빠짐없이 옮기기 위해 유지한다. 이름에 `ap_`가 붙었다는 이유만으로 모든 장치를 AP domain으로 재분류하지 않는다. AP `io_peri.lua`는 AP가 소유한 peripheral을 담당하며, 현재 RoS의 DW controller를 AP 아래로 통합하는 결정은 주소 domain/clock/reset 소유권을 확인한 후 할 수 있다. 실제 소유권이 바뀌지 않는 파일 정리가 첫 목표다.

향후 board가 두 개 이상이 되면 `board/saturn-v/`와 `board/<other>/`로 aggregator와 배선을 나눌 수 있다. 현재는 요청한 `board/hw-block/`을 사용하며 다중 SoC registry나 board discovery는 만들지 않는다.

## 3. Device Tree 방식의 include 규칙

| Device Tree의 개념 | Lua에서의 대응 |
|---|---|
| SoC `.dtsi` | `soc/apollo.lua`가 domain aggregator를 include |
| IP/domain `.dtsi` | `cpu.lua`, `syscore.lua`, `io_peri.lua` 등의 module |
| board `.dts` | entry가 SoC + VP profile + `board/saturn-v.lua` 조합 |
| label/phandle | local `ctx.ports`와 기존 QBox socket/object reference |
| board의 `&i2c0 { ... }` | `board.connect()`가 공개된 I2C port에 외부 bus/device 연결 |
| `status = "disabled"` | profile의 명시적 presence 설정; 생성하지 않을 장치 결정 |
| overlay | 이름이 정해진 `connect()`/`attach()` 수정 단계와 검증 |

Lua `dofile()`은 textual include가 아니라 **chunk 실행**이다. 여러 번 호출하면 여러 번 실행되며 Device Tree처럼 자동 merge, phandle 해결, `status` 처리 기능을 제공하지 않는다. 이를 숨긴 일반적인 deep merge를 만들지 않는다. 배열인 `args`, reset target list, loader image list와 socket table은 각기 다른 의미가 있기 때문이다.

### 3.1 파일 상대 include

각 aggregator는 자신의 위치에서 상대 경로로 include한다. leaf module은 가능하면 다른 domain을 직접 include하지 않고 aggregator가 `ctx`로 전달한다.

```lua
-- soc/hw-block/ap_compute/ap_compute.lua: 제안 API 예제
local dir = debug.getinfo(1, "S").source:sub(2):match("(.*/)") or "./"
local cpu = dofile(dir .. "cpu.lua")
local syscore = dofile(dir .. "syscore.lua")
local io_peri = dofile(dir .. "io_peri.lua")
local ap_compute = {}

function ap_compute.define(ctx, platform)
    cpu.define(ctx, platform)
    syscore.define(ctx, platform)
    io_peri.define(ctx, platform)
end

return ap_compute
```

이는 현재 include 분석기의 `dofile(..."literal.lua")` 탐색과 맞는다. 다음 규칙을 적용한다.

1. entry만 최종 global `platform`을 설정한다. module table, `ctx`, hardware metadata는 `local`이다.
2. module load 시에는 함수와 정적인 상수만 만든다. 환경변수 파싱과 객체 생성은 각각 `options.resolve()`와 `define()`에서 수행한다.
3. 경로는 including file 기준의 큰따옴표 literal이다. `dofile(` 사이에는 공백을 두지 않는다. 중첩 파일에서 `dofile(ctx.apollo_dir.."soc/...")`를 쓰면 실제 Lua 실행과 현재 정적 분석기의 경로 해석이 달라진다. `..` 앞뒤 공백은 허용한다.
4. `require()`와 `package.path` 변경, 자동 directory scan, 새 `ctx.include()` wrapper는 사용하지 않는다. 도입하려면 현재 graph scanner와 sandbox evaluator를 먼저 수정해야 한다.
5. include graph는 DAG로 유지한다. CL1이 CL0 module을 통째로 다시 로드하는 대신 SoC aggregator가 공용 SI interrupt module을 한 번 로드해 전달한다.

`debug.getinfo()`로 얻는 `dir`은 소스 include에만 사용한다. 이미지·로그 경로를 `../../../../../../`와 결합해 추론하지 않는다. 이들은 runner가 전달하는 옵션을 사용하고 기존 local fallback이 필요하면 VP에서 한 번만 해석한다.

### 3.2 공개 API와 context

권장 API는 `define(ctx, platform)`과 `connect(ctx, platform)` 두 단계다. `define()`은 자신이 소유한 객체를 생성하고 `connect()`는 이미 정의된 객체 사이를 연결한다. 별도 단계가 필요하지 않은 leaf는 `define()`만 제공한다.

`ctx`는 플랫폼 descriptor 밖의 local table이다. 권장 필드는 다음 정도로 제한한다.

| 필드 | 내용 |
|---|---|
| `ctx.options` | 환경변수에서 정규화된 실행 값, 이미지·로그 경로 |
| `ctx.profile` | domain presence, full-system/AP-only 주소 view, test wiring 선택 |
| `ctx.backends` | `vp.prepare()`에서 확정한 backend 선택·capability·instance 참조; hardware 정의 전에 준비 |
| `ctx.board` | 외부 장치 장착·bus address·메모리 용량 등의 board 입력 |
| `ctx.modules` | 필요한 domain/shared helper; 현 API의 점진적 이행에 사용 |
| `ctx.ports` | SoC/VP가 board에 공개하는 객체명과 socket/pin 참조 |

`ctx.options/profile/board/backends`는 준비 이후 읽기 전용이라는 작성 규칙을 적용하고, `ctx.ports`는 해당 port owner만 등록한다. metatable 기반 동결이나 범용 registry는 도입하지 않는다. leaf의 private helper에는 필요한 작은 입력만 전달하고, `ctx.modules`를 통해 다른 domain 내부를 임의 수정하지 않는다.

공개 port 예: `ctx.ports.ap_i2c0 = { object = "ap_dw_i2c_0", socket = "i2c_socket" }`. Board는 이 port를 통해 bus를 연결하고 GIC, ATU, CPU의 내부 테이블을 찾아 수정하지 않는다. PMIC host port가 QVP extension에서 제공되면 그 소유권도 명시한다.

board가 PMIC를 요구하는데 port가 없으면 `assert`로 Lua 구성을 중단한다. 이것만으로 native process의 실패 종료를 보장하지는 않는다. 실제 loader/runner가 nonzero 종료 또는 명시적 FAIL로 처리하는 negative test가 완료 조건이다. AP-only profile에서 PMIC를 생략할 때는 profile/board options에서 명시적으로 제외한다. 지금의 `if not platform.<controller> then return end`처럼 요구 장치의 누락을 조용히 넘기지 않는다. 선택 장치에 대한 생략 동작은 계속 허용한다.

모든 객체 생성은 한 owner가 담당한다. **생성 직전** `assert(platform[name] == nil, ...)`로 중복을 확인한다. table literal 안의 중복 field는 lint/code review로 검사한다. 최종 `platform`에서는 이미 덮어쓴 값의 이력을 알 수 없으므로 `vp.validate()`에 중복 생성 검출을 맡기지 않는다. 다른 owner의 값을 수정할 때는 `connect()`의 공개 port 또는 정해진 VP 정책만 사용하고, 기존 기대값을 확인한 뒤 변경한다.

## 4. 구성 순서

목표 entry의 형태는 아래와 같다. 함수명과 파일은 **설계 예제이며 현재 구현된 API가 아니다**.

```lua
-- apollo-qvp-saturn-v.lua
local dir = debug.getinfo(1, "S").source:sub(2):match("(.*/)") or "./"
local options = dofile(dir .. "vp/options.lua")
local profile = dofile(dir .. "vp/profiles/full-system.lua")
local vp = dofile(dir .. "vp/qvp.lua")
local soc = dofile(dir .. "soc/apollo.lua")
local board = dofile(dir .. "board/saturn-v.lua")

local ctx = options.resolve(dir, profile, board.defaults())
vp.prepare(ctx)
local p = vp.create(ctx)
soc.define(ctx, p)
vp.attach(ctx, p)
board.define(ctx, p)
soc.connect(ctx, p)
board.connect(ctx, p)
vp.finalize(ctx, p)
vp.validate(ctx, p)
platform = p
```

| 단계 | 수행 내용과 조건 |
|---|---|
| 입력 확정 | domain presence, CPU 수, backend, board 장착 정보, 파일·로그 경로 해석. 결정되지 않은 firmware path는 필요한 profile에서 오류 |
| `vp.prepare` | backend 조합과 capability, instance 이름을 확정해 `ctx.backends`에 설정. 아직 platform 객체를 생성하지 않음 |
| `vp.create` | root `Container`, quantum, keep-alive 등 host 실행 틀 생성 |
| `soc.define` | 확정된 backend에 맞는 hardware descriptor/socket을 생성. QemuInstance 참조 문자열은 아직 target이 없어도 선언 가능 |
| `vp.attach` | SoC가 만든 container에 instance, loader, VirtIO, QVP 확장 또는 mock 추가. backend를 재선택하거나 기존 RSE nested container를 덮어쓰지 않음 |
| `board.define` | 외부 device와 bus 생성; SoC 주소 view와 별도로 bus-local 주소 설정 |
| `soc.connect` | 내부 CPU/GIC/ATU/MHU/reset 연결. profile에 맞는 주소 view를 선택해 VP MMIO 장치에도 동일 규칙 적용 |
| `board.connect` | 공개 port와 외부 bus/pin/pull-up 연결 |
| `vp.finalize` | console/debug/QMP, 시험 wiring, injection interpose, loader/reset 추가 연결을 최종 descriptor에 적용 |
| `vp.validate` | presence, 주소 view별 허용되지 않은 충돌, 필수 port, 참조, 선택 profile 조합 검증. 생성 중복은 assignment 직전 검사하며 C++ elaboration도 별도 수행 |

Lua descriptor를 만드는 순서와 SystemC 객체 생성 순서는 다르다. Lua가 반환한 후 QBox가 `construction_priority`, `args`, socket binding을 처리한다. 따라서 기존 `construction_priority`, `dont_construct`, QemuInstance 소유권과 생성자를 통한 dependency를 그대로 보존해야 한다.

마지막 `platform = p`는 검증 전 partial platform 공개를 줄이는 작성 규칙이다. legacy globals나 C++ loader의 오류 처리를 transaction으로 바꾸는 기능은 아니다. 검증 실패 후 native 실행이 정상으로 보고되지 않는지 별도로 확인한다.

첫 파일 이동부터 이 최종 순서를 강제하지 않는다. 현재 full-system의 `define → enable_ap_router → audio replacement → SI enable → PMIC` 순서를 그대로 보존한 compatibility composition으로 시작한 뒤, 후처리를 제거할 준비가 된 domain부터 두 단계 API로 바꾼다.

## 5. 분리 시 특별히 처리할 항목

### 5.1 `config.lua`: global을 context로 옮기기

현재 `config.lua`는 528행이며 module load 시 환경변수와 helper 함수를 global에 설정한다. 단순히 파일을 `vp/options.lua`로 옮기는 것으로 끝나지 않는다.

- 이미지/로그/console/QEMU/trace/DMI/monitor 값은 `vp/options.lua`로 이동한다. 기존 환경변수 이름과 기본값은 초기 단계에서 유지한다.
- CPU 최대 구성·affinity와 IRQ/MMIO 값은 실제 hardware owner에 둔다. 공통 `config.lua`에 모든 주소를 다시 모으지 않는다.
- AP/SoC reset target 목록은 hardware `connect()`로, VP loader·test object reset 대상은 VP 연결 단계로 나눈다. 순서와 target 집합을 비교한다.
- `AP_GIC_NUM_CPUS`, `rse_vmaddrwidth`처럼 다른 module이 load 시 읽는 값은 `define(ctx, ...)` 내부 계산으로 옮긴다. 이 전환 전에 global을 제거하면 include 단계에서 실패한다.
- 옵션 우선순위는 기존 profile 기본값 → 명시적 환경/launcher 입력 → profile 제약 검증으로 한다. hardware 상수까지 임의 override하는 merge는 제공하지 않는다. 기존 CCI `-p` override 동작은 별도로 보존·검증한다.

### 5.2 hardware identity와 backend

CPU·DMA·I2S·SMMU의 MMIO/IRQ/clock/reset 계약은 SoC module이 소유한다. VP는 `soc.define()` **전에** backend와 실행 파라미터를 선택해 전달한다. backend별로 socket과 constructor 인자도 다르므로 이름만 나중에 교체하면 안 된다. SoC가 `vp/`를 역방향 include하지 않도록 선택 결과나 작은 factory 함수를 `ctx`로 전달할 수 있다. 새 plugin registry는 필요하지 않다.

현재 `common.use_qemu_audio()`는 이미 만든 DMA/I2S table을 교체하고 pinctrl gate를 삭제한다. 초기 이행에서는 이 변환을 순서까지 유지해 VP에 옮긴다. 이후에는 hardware 정의 단계에서 최종 backend를 한 번만 생성하도록 개선한다. backend에 없는 pin gate/reset/trigger 연결을 최종 table에 남겨서는 안 된다. 서로 다른 backend를 물리적으로 동등하다고 선언하지 않는다.

### 5.3 주소 view와 shared memory

AP logical address, system physical address, SMD 및 SI local view는 파일 경로와 무관하다. `address_view.lua`와 `interconnect.lua`는 기존 ATU/addrtr aperture, `mapped_base_addr`, `relative_addresses`, decode priority를 유지한다. 단순히 bind 문자열을 새 domain 이름으로 바꾸는 작업이 아니다.

동일 SRAM의 AP/SI view는 기존 storage backing과 alias 관계를 유지한다. 파일을 나누며 별도의 RAM을 각각 생성하면 HIPC/SCMI가 분리된다. MHU 양쪽 frame은 각각의 owner가 만들고 SoC aggregator가 pair/shared-memory/IRQ 연결을 확정한다.

DRAM/flash도 세 부분으로 구분한다. SoC aperture/controller/alias는 SoC, 실제 장착 용량·구성은 board, host backing 파일과 image loader는 VP다. 현재 모델이 하나의 `gs_memory` 객체로 이를 표현하면 객체를 복제하지 않고 세 입력을 한 owner의 descriptor에 결합한다. 실물 장착 정보가 없는 경우 현재 QVP map 값을 유지한다.

### 5.4 SI CL0/CL1 공용 interrupt 계약

현재 CL1은 CL0의 PPI/SPI helper를 사용한다. 이를 `si_common/interrupts.lua`로 분리해 SoC aggregator가 양쪽에 전달한다. CL0/CL1의 실제 GIC, multiview wiring은 hardware 정의에 남긴다.

SI normal SPI의 `architectural INTID - 32` 변환, View1/View2 owner, PPI의 per-CPU 의미를 그대로 유지한다. 모든 IP의 IRQ 숫자에 일괄 `-32`를 적용하는 generic helper는 만들지 않는다. AP와 각 component socket의 숫자 의미는 현재 코드에 따라 검증한다.

CPU Generic Timer PPI는 `cpu.lua`에서 유지한다. AP MMIO REFCLK timer와 SMD/RSE counter는 각 hardware owner에 둔다. 파일 정리 과정에서 timer를 다른 종류의 timer/RAM으로 대체하지 않는다.

### 5.5 board device와 시험 연결

현재 AP I2C0 bus는 EEPROM `0x50`–`0x52`, PCA9539 `0x74`를 연결한다. TPS6594 하나는 SI CL0 management I2C의 `0x48`에 있고 page alias `0x48`–`0x4c`를 사용한다. 이 숫자는 현재 QVP 구성값이며 Saturn-V 실물 확인값은 아니다.

PCA9539 RESET_N/INT_N과 PMIC INT_N, pull-up은 board 배선으로 분리한다. 현재 PMIC INT_N은 SI CL0 GPIO의 polling 입력이며 GIC에 연결되지 않는다. 파일 분리가 SCP 비동기 fault IRQ 지원을 추가하는 것은 아니다. GPIO 0→1/8→9, PERI bank loopback, UART peer, I2S peer는 `vp/test-wiring/`로 분리한다. 초기 full-system/AP-only profile은 **현재 활성화된 시험 연결을 그대로 선택**해 BSP 검증 동작을 보존한다. 이를 기본 OFF로 바꾸는 것은 후속 동작 변경이다.

reset 의미도 장치별로 보존한다. 현재 TPS6594 모델에는 외부 reset input이 없고 warm reset에서 rail/register 상태를 유지한다. 모든 board 장치에 일괄 SoC reset을 연결하지 않는다. PMIC register/rail readback은 전기적 power sequencing·brownout·실물 reset 효과를 보장하지 않는다.

### 5.6 AP-only profile

`apollo-qvp-linux.lua`는 유지하고 동일 SoC 정의에 `linux-direct` profile을 적용한다. 이 profile은 AP CPU만 생성하며 RSE/SI CPU를 생성하지 않는다. SRAM/IRQ metadata가 필요하다는 이유로 RSE/SI firmware domain을 함께 켜지 않는다.

현재 동작 중 firmware reset 객체 삭제, GIC security 설정, CPU reset entry/PSCI, AP-local rebinding, kernel/DTB/initrd loader, SCMI/SI/RSE substitute는 VP profile에 모은다. 점진적으로 생성 후 삭제를 presence 입력으로 바꾸되 baseline descriptor와 동작을 비교한다. 실제 RSE/SCP/Zephyr 실행, secure service, 전역 EFI reset과 동일하다는 의미를 부여하지 않는다.

## 6. 채택할 결정

1. 새 full-system entry는 요청한 `apollo-qvp-saturn-v.lua`로 하고, `apollo-qvp.lua`는 같은 디렉터리의 forwarding entry로 유지한다.
2. `soc/hw-block/<domain>/<domain>.lua` 아래로 기존 domain을 나누되 runtime 객체명과 기존 nested RSE container를 보존한다.
3. include는 파일 상대 literal `dofile()`을 사용한다. 최종 `platform` 외의 metadata는 global table에 내보내지 않는다.
4. SoC 내부 연결은 SoC, 외부 부품/배선은 Board, 실행·mock·시험 정책은 VP가 소유한다. QVP 전용 MMIO 확장은 명시적으로 표시한다.
5. 새 폴더에 옮기는 단계와 생성/연결 API를 개선하는 단계를 분리한다. 전환 완료 조건은 [migration.md](migration.md)의 descriptor 비교와 실제 profile별 검증이다.
6. 가독성은 작은 hardware module, 명시적인 연결, 일관된 table 배치로 개선한다. 자동 formatter는 source parser의 서식 의존을 해소한 후 적용한다. [Lua 작성 지침](lua-style.md)을 구현 시 기준으로 사용한다.
