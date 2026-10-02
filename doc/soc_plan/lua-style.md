# Apollo QVP Lua 작성·가독성 지침

[설계안](README.md) · [계획 리뷰](review.md) · [전환 계획](migration.md)

조사일: 2026-10-02. Lua 공식 문서, 저자의 Programming in Lua, Luacheck·StyLua 문서와 현재 QBox 소스를 비교했다. 아래 규칙은 그 결과를 Apollo 구성 코드에 맞게 선택한 **프로젝트 제안**이다. 들여쓰기·파일 크기·field 배치에 관한 선택을 Lua의 공식 표준이라고 주장하지 않는다.

이 문서는 설계 당시의 작성 지침과 도구 도입안을 보존한다. 이후 module 분리와 descriptor 기반 검사기를 구현했다. 실제 적용 범위와 실행 결과는 [구현·검증 기록](implementation.md)을 따른다. 아래 source parser 제약은 변경 전 검사기에 대한 분석이다.

목표는 파일을 열었을 때 **어떤 IP가 어느 주소에 있고, 누구와 연결되며, 어느 profile에서 생성되는지** 바로 읽을 수 있게 하는 것이다. 선언적인 device table을 중심으로 두고 반복되는 동일 IP만 작은 함수와 spec table로 묶는다.

## 1. 기본 작성 규칙과 적용 범위

아래는 **목표 스타일**이다. 기존 regex가 읽는 코드는 소비자를 수정하기 전까지 기존 서식을 유지한다. 자동 formatter뿐 아니라 `..` 공백 추가나 `if`로 감싸는 수동 정리에도 이 조건이 적용된다. 새 helper/loop/들여쓰기를 도입할 때 source 수집 집합을 비교한다. 현재 `dofile(dir .. "cpu.lua")`의 공백은 허용되지만, 같은 공백 규칙을 모든 parser가 지원하는 것은 아니다.

| 항목 | 권장 규칙 | 이유 |
|---|---|---|
| module | `local <block> = {}`와 마지막 `return <block>` | 공개 API와 local 구현 구분 |
| global | 최종 entry의 `platform`만 export | QBox `_G` → CCI 변환에서 불필요한 metadata 유출 방지 |
| load 시점 | include와 정적 정의만 수행 | profile 선택 전 env 읽기/객체 생성 방지 |
| 이름 | 함수/변수 `snake_case`, hardware 상수 `UPPER_SNAKE_CASE` | 현재 Apollo 관례에 맞춤 |
| 기존 식별자 | `moduletype`, CCI key, socket, runtime object name 그대로 유지 | naming 정리와 ABI 변경 분리 |
| 들여쓰기 | space 4개, tab 금지 | 기존 코드 및 현 parser와 호환 |
| 길이 | 보통 100 columns 이내를 목표; 긴 경로/참조는 의미 우선 | 좌우 이동 없이 table 비교 가능 |
| 문자열/include | 큰따옴표, `dofile(dir .. "cpu.lua")` | 현재 include scanner 호환 |
| 연산자 | `=`, `..`, 산술·비교 연산자 앞뒤 공백 | 식의 경계를 분명하게 표시 |
| table | 한 field 한 줄, 마지막 field에도 `;` | 현재 semicolon 기반 parser와 작은 diff 유지 |
| 함수 호출 | 항상 괄호 사용, module API는 `.` 호출 | `self` 암묵 전달과 DSL 모양의 호출 방지 |
| 조건문 | profile 선택은 명시적인 `if`; 한 줄에 여러 동작 금지 | 생성/생략 경로가 눈에 보이게 함 |
| 반복 | 동일 IP만 spec table로 반복 생성 | 예외가 많은 장치까지 일반화하지 않음 |
| 주석 | 주소 view·단위·IRQ 의미·순서 이유·모델 한계 설명 | 코드를 읽어 알 수 없는 근거를 제공 |

세미콜론은 Lua statement마다 붙이라는 뜻이 아니다. **table field 구분자**에 현재 관례를 유지한다. Lua 자체는 comma/semicolon 모두 허용하지만, 현재 source parser는 그 둘을 동등하게 처리하지 않는다. [Lua table constructor 문법](https://www.lua.org/manual/5.4/manual.html#3.4.9), [로컬 재현 결과](review.md#4-p1--서식-변경으로-source-검사-범위가-사라질-수-있음).

## 2. 파일과 함수의 크기

아래 숫자는 분리 검토를 시작하는 참고값이며 CI가 강제할 제한이 아니다.

- entry/aggregator는 대략 20–80행: 선택과 호출 순서를 보여주고 MMIO map을 직접 쌓지 않는다.
- leaf는 보통 100–300행: 같은 IP군의 상수·정의·연결을 함께 둔다. 400행을 넘으면 owner나 변경 이유가 섞였는지 검토한다.
- helper는 한 가지 변환·검사·생성만 담당한다. 제어 흐름이 긴 함수는 나누되 긴 선언 table을 함수 여러 개로 잘라 숨기지 않는다.
- `syscore.lua`가 GIC·timer·watchdog의 집합으로 커지면 그때 `interrupts.lua`, `timers.lua`로 추출한다. 한두 객체만 있는 작은 domain에 동일 파일 수를 강요하지 않는다.
- `utils.lua`, `common.lua`에 모든 helper를 모으지 않는다. SI IRQ 변환처럼 공유 이유가 명확한 기능만 이름이 구체적인 module로 분리한다.

파일 배치는 **목적/제약 주석 → local module/include → local 상수/spec → private helper → 공개 `define/connect` → return** 순서를 권장한다. 기존 라이선스/저작권 표기는 이동 시 그대로 보존한다.

독자를 우선하고, 주석에는 동작을 반복하기보다 이유를 남긴다는 원칙은 [Roblox Lua Style Guide](https://roblox.github.io/lua-style-guide/#comments)도 제안한다. 여기서는 그 원칙만 참고하며 Roblox API, Luau type 문법, naming 체계까지 가져오지 않는다.

## 3. device table은 hardware 구조가 보이게 배치

field 순서는 아래를 기본으로 한다. constructor 배열과 reset list의 **값 순서**는 절대 서식 정렬 대상으로 삼지 않는다.

1. `moduletype`, 필요한 `dylib_path`.
2. `args`, `construction_priority`, reset/presence 관련 생성 값.
3. IP 파라미터: CPU/clock/channel count/주소 strap 등.
4. `target_socket`/`mem`/`dist_iface` 등 address view.
5. IRQ/reset, initiator/bus/backend 연결.
6. trace/log 설정.

주소는 hex, 크기는 기존 hardware 단위에 맞는 hex 또는 명명된 상수로 쓴다. `timer_frequency_hz`, `reset_delay_ns`, `flash_size_bytes`, `irq_intid`, `spi_index`처럼 단위와 의미를 이름에 드러낸다. `irq = 193`만 남기는 것보다 그 값이 INTID인지 QEMU SPI index인지 함께 밝히는 편이 중요하다.

실제 객체 경로와 socket 이름은 descriptor 가까이에서 읽을 수 있게 한다. `make_device(type, base, irq, flags, ...)`처럼 서로 다른 IP를 긴 positional 인자로 감싸지 않는다. 여러 값이 필요하면 이름 있는 record를 전달하되 실제 CCI `args` 배열은 원래 constructor 순서를 보존한다.

하드웨어 주소를 decimal 문자열이나 scientific notation으로 바꿔 가독성을 떨어뜨리지 않는다. QBox [Lua 숫자 변환](../../hsoc-stack/tools/qbox/systemc-components/common/src/luautils.cc#L241)은 `lua_tonumber()`/double을 경유하므로 Lua 5.4 integer라고 해서 모든 64-bit 주소가 손실 없이 전달된다고 가정하지 않는다. 새 고위 주소를 추가하는 작업은 별도 숫자 정밀도 검증 대상이다.

## 4. 반복 IP는 spec과 fresh descriptor를 분리

다음은 AP I2C0의 EEPROM 세 개를 Board가 소유하도록 옮길 때의 **작성 형태 예제**다. 실제 구현은 기존 descriptor를 보존하며 `board/hw-block/eeprom.lua`와 `pca9539.lua`에 population을 배치했다. 예제의 API와 field를 실제 runtime 결과로 간주하지 않는다. 반복 생성을 읽을 수 있도록 [검사기 전환](migration.md#단계-0--기존-결과-고정)도 함께 적용했다.

```lua
-- AP I2C0 EEPROM population. Bus creation belongs to board/i2c.lua.
local eeprom = {}

local EEPROM_SPECS = {
    { name = "ap_dw_i2c_0_eeprom"; address = 0x50; };
    { name = "ap_dw_i2c_0_eeprom_1"; address = 0x51; };
    { name = "ap_dw_i2c_0_eeprom_2"; address = 0x52; };
}

local function make_eeprom(spec)
    return {
        moduletype = "dw_i2c_eeprom";
        dylib_path = "dw-apb-i2c";
        address = spec.address;
        size = 256;
        address_width = 8;
        page_size = 8;
        write_cycle = "5 ms";
    }
end

function eeprom.define(_ctx, platform)
    for _, spec in ipairs(EEPROM_SPECS) do
        assert(platform[spec.name] == nil, "duplicate EEPROM: " .. spec.name)
        platform[spec.name] = make_eeprom(spec)
    end
end

function eeprom.connect(_ctx, platform)
    assert(platform.board_i2c0 ~= nil, "AP I2C0 EEPROM bus is missing")

    for _, spec in ipairs(EEPROM_SPECS) do
        local device = assert(platform[spec.name], "missing EEPROM: " .. spec.name)
        assert(device.i2c_socket == nil, "EEPROM already connected: " .. spec.name)
        device.i2c_socket = { bind = "&board_i2c0.initiator_socket"; }
    end
end

return eeprom
```

이 예제의 의도는 다음과 같다.

- name/address를 한 줄에서 비교할 수 있다. 작은 spec record는 한 field 한 줄 규칙의 예외로 둔다.
- 긴 공통 descriptor를 복사하지 않고 `make_eeprom()`이 매번 새로운 table을 만든다.
- AP runtime 이름, I2C address, page/write-cycle 값을 유지한다.
- 사용하지 않는 API 인자는 `_ctx`로 표시한다. 경고를 피하기 위한 불필요한 읽기 코드를 넣지 않는다.
- 생성, 외부 연결, 중복 정의의 실패 위치가 구분된다.

Lua의 table 대입은 참조를 공유한다. `device = template`를 반복한 뒤 field를 변경하면 별개의 장치 descriptor가 되지 않는다. 매번 새 table을 만들거나 필요한 field를 명시해 조립한다. hardware descriptor에 범용 deep-copy/deep-merge는 도입하지 않는다. [Programming in Lua: Tables](https://www.lua.org/pil/2.5.html)

## 5. 순서·boolean·중복을 숨기지 않기

### 순서가 중요한 배열

reset, loader image, constructor args, domain 호출 순서는 빈 index가 없는 배열 또는 명시적인 호출로 표현한다. `pairs()`에 실행 순서를 맡기지 않는다. `ipairs()`는 첫 누락 index에서 멈추므로 optional 항목을 `nil`로 끼워 넣지 말고 조건이 맞을 때 추가한다. [Programming in Lua: Generic for](https://www.lua.org/pil/4.3.5.html), [Lua ipairs](https://www.lua.org/manual/5.4/manual.html#pdf-ipairs)

```lua
local reset_targets = { "&ap_watchdog_0.reset"; }
if runtime_injection_enabled then
    reset_targets[#reset_targets + 1] = "&ap_i2c5_irq_fault.reset"
end
```

이것은 목록 작성 형태를 보여주는 예제이며 Apollo의 전체 reset 순서가 아니다. 실제 적용에서는 기존 fanout 순서를 보존한다. 배열 index는 1부터, hardware CPU 번호는 0부터라는 경계도 명시한다.

### false를 기본값으로 바꾸지 않기

`value or default`는 `false`도 대체한다. `enabled`처럼 false가 유효한 설정은 `nil`인지 명시적으로 판단한다. [Lua values and types](https://www.lua.org/manual/5.4/manual.html#2.1)

```lua
local enabled = options.enabled
if enabled == nil then
    enabled = true
end
```

목표 구조에서는 `enable and descriptor or nil` 표현보다 명시적인 `if`로 생성 범위를 감싼다. 생성하지 않은 device를 바로 뒤에서 참조하지 않도록, 종속된 설정도 같은 조건 내부에서 수행한다. 이 변경으로 객체 선언이 8칸 들여쓰기가 되면 현재 4칸 전용 parser가 놓칠 수 있으므로 해당 consumer를 먼저 수정한다.

### 중복은 생성 시점에, 의도적인 교체는 정해진 곳에서

`platform[name]`에 대입하기 전에 존재 여부를 확인한다. literal의 같은 이름 field도 금지한다. Lua는 한 constructor 안의 중복 key에 대한 대입 순서를 보장하지 않는다. [Lua table constructors](https://www.lua.org/manual/5.4/manual.html#3.4.9)

이행 중 audio backend를 교체할 때는 함수명에 그 의도를 드러내고, 교체 전 model과 보존할 MMIO/IRQ/trigger를 확인한다. 모든 table에 적용하는 `merge()`로 조용히 덮어쓰지 않는다.

## 6. context와 주석

`ctx`는 module 사이의 입력 전달 수단이다. 자유롭게 수정하는 global의 대용으로 사용하지 않는다. 공개 함수는 `define(ctx, platform)` 형태를 맞추고, private helper는 `make_cpu(cpu_spec, execution)`처럼 필요한 입력만 받는다. 상수 table을 함수 밖에 두더라도 `local`로 선언하고 호출마다 달라지는 상태는 저장하지 않는다. local scope에 관한 근거는 [Programming in Lua: Local Variables](https://www.lua.org/pil/4.2.html)를 참조한다.

주석은 현재 source 관례에 맞춰 간결한 영어를 기본으로 한다. 다음과 같은 정보를 남긴다.

```lua
-- AP logical view; keep the physical-domain translation in the ATU owner.
-- QVP extension: this window is not a physical RD-Aspen peripheral assignment.
-- Hold the CPUs before resetting the interrupt controller.
```

“값 설정”, “table 반환”처럼 코드를 그대로 반복하는 설명, 장식용 구분선, 오래된 안을 남긴 긴 주석 처리는 피한다. 근거는 TRM 절·기존 문서·대상 hardware 이름으로 추적할 수 있게 한다. software image의 symbol 값은 SoC 상수와 섞지 않고 VP boot policy에 둔다.

## 7. formatter / lint 도입안

### 현재 적용 범위

Module 분리와 의미 기반 검사기는 적용했지만 StyLua/Luacheck 설정과 도구 실행은 이번 구현에 포함하지 않았다. 아래 설정은 도입 후보이며 검증된 프로젝트 설정이 아니다. 기존 `.vscode` 설정은 이 작업의 변경 대상이 아니다. 자동 format을 추가할 때도 [리뷰의 parser 호환 문제](review.md#4-p1--서식-변경으로-source-검사-범위가-사라질-수-있음)와 descriptor 비교를 확인한다.

### StyLua: 서식 통일

parser를 보강한 뒤 `qbox-platform` repository 안에 둘 `.stylua.toml` 후보:

```toml
syntax = "Lua54"
column_width = 100
line_endings = "Unix"
indent_type = "Spaces"
indent_width = 4
quote_style = "ForceDouble"
call_parentheses = "Always"
space_after_function_names = "Never"
collapse_simple_statement = "Never"

[sort_requires]
enabled = false
```

이 설정이 현재 semicolon 표기를 보존한다는 뜻은 아니다. 이행 후 comma 표기를 채택한다면 formatter와 문서 예제를 함께 맞춘다. 먼저 기존 source를 기계적으로 바꾸지 않는다.

공식 자료는 파일을 쓰지 않는 `--check` diff와 `--verify` AST 재분석을 제공하지만, 후자도 검출 한계가 있어 tests가 필요하다고 설명한다. runtime syntax는 Luau 등과 혼합하지 않고 지정한다. 버전은 도입 시 고정하고 업데이트 시 diff를 확인한다. [StyLua README](https://raw.githubusercontent.com/JohnnyMorganz/StyLua/main/README.md)

### Luacheck: 오류 검출

미정의 global, unused value, shadowing, table literal field의 덮어쓰기 후보를 확인한다. 특히 111/112/113, 2xx, 314, 4xx를 전체 ignore하지 않는다. Luacheck는 runtime 문자열로 작성한 QBox socket 이름의 존재까지 검증하지 않는다. [Luacheck warnings](https://luacheck.readthedocs.io/en/stable/warnings.html)

`.luacheckrc` 후보는 entry에만 global을 허용한다. 새 구조로 이행한 module부터 단계적으로 적용한다.

```lua
-- Luacheck configuration, not a QBox runtime module.
std = "lua53"
max_line_length = 100
codes = true

files["platforms/apollo/apollo-qvp-saturn-v.lua"] = {
    globals = { "platform" };
}
files["platforms/apollo/apollo-qvp-linux.lua"] = {
    globals = { "platform" };
}
```

조회한 [Luacheck 표준 global 정의](https://raw.githubusercontent.com/lunarmodules/luacheck/master/src/luacheck/standards.lua)에는 `lua54`가 없어 `lua53`을 기본 API 집합으로 쓰는 제안이다. QBox runtime을 5.3으로 바꾸는 설정이 아니다. 5.4 전용 API/문법이 필요하면 채택한 도구의 지원 여부를 확인한다. API 목록 부족은 필요한 file의 추가 정의로 보완할 수 있지만 parser가 지원하지 않는 문법은 global 설정으로 해결되지 않는다. 파일별 설정은 [공식 configuration](https://luacheck.readthedocs.io/en/stable/config.html#per-file-and-per-path-overrides)에서 지원한다.

### 후속 check 명령

아래 명령은 신규 directory, 설정 파일, 고정 버전 도구를 도입한 후 `qbox-platform` repository root에서 실행한다. 이번에 실행한 명령은 아니다.

```bash
stylua --version
luacheck --version
stylua --check --verify --config-path .stylua.toml platforms/apollo/soc platforms/apollo/vp platforms/apollo/board
luacheck --config .luacheckrc platforms/apollo/soc platforms/apollo/vp platforms/apollo/board platforms/apollo/apollo-qvp-saturn-v.lua platforms/apollo/apollo-qvp-linux.lua
```

## 8. 리뷰 시 확인할 항목

1. 파일명에서 hardware 책임을 알 수 있고 entry를 위에서부터 읽으면 생성 순서를 이해할 수 있는가.
2. MMIO/IRQ/reset/instance 참조가 descriptor 가까이에 있어 helper를 여러 단계 추적하지 않고 읽을 수 있는가.
3. spec/template을 공유하다가 서로 다른 device의 가변 table까지 공유하지 않는가.
4. 생성 조건, 단위, INTID와 socket index, QVP 확장이 명확히 구분되는가.
5. global, 중복 정의, optional 배열의 누락 index, 순서 없는 reset 조립을 피했는가.
6. formatter/문법 PASS와 별개로 source 수집 범위와 최종 descriptor를 확인했는가.

문법, lint, format, descriptor/native elaboration, guest traffic은 서로 다른 검사다. Lua 가독성 개선을 runtime 동작이나 hardware fidelity의 증거로 사용하지 않는다.
