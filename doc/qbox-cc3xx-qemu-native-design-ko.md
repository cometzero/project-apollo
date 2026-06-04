# QBox CC3XX QEMU-Native Backend Design

작성일: 2026-06-04

상태: 구현 및 검증 완료

## 설계 요약

권장 구조는 `cc3xx_core` 하나를 두고 SystemC wrapper와 QEMU wrapper가 이를
공유하는 방식이다.

```text
RSE CPU MMIO
  -> QEMU MemoryRegionOps
  -> qemu_cc3xx wrapper
  -> cc3xx_core
      -> DMA memory_if
          -> QEMU AddressSpace first
          -> limited TLM fallback if required

KMU/SystemC cold path
  -> remote_crypto_router
  -> qemu_cc3xx target_socket
  -> QemuTargetSocket::init_with_mr()
  -> same QEMU MemoryRegionOps
  -> cc3xx_core

Legacy SystemC path
  -> cc3xx target_socket
  -> SystemC cc3xx wrapper
  -> same cc3xx_core
```

이 구조는 세 가지 목적을 동시에 만족한다.

- 기존 SystemC backend의 동작을 유지한다.
- QEMU CPU의 hot MMIO traffic은 QEMU process 안에서 처리한다.
- KMU 같은 SystemC peripheral이 수행하는 key export write는 계속 받을 수
  있다.

## 파일 구조

초기 구현은 header-only core를 권장한다. 현재 `cc3xx.h`도 대부분 class body
내 구현이므로 첫 split에서 CMake risk를 줄일 수 있다. 구현이 안정되면
`cc3xx_core.cc`로 이동할 수 있다.

| 파일 | 역할 |
| --- | --- |
| `tools/qbox/systemc-components/cc3xx/include/cc3xx_core.h` | register/crypto/DMA side effect 공통 core |
| `tools/qbox/systemc-components/cc3xx/include/cc3xx.h` | 기존 SystemC adapter, CCI/TLM/reset/stats-file ownership |
| `tools/qbox/systemc-components/cc3xx/src/cc3xx.cc` | 기존 `cc3xx` module registration |
| `tools/qbox/qemu-components/cc3xx_native/include/qemu_cc3xx.h` | QEMU-native wrapper |
| `tools/qbox/qemu-components/cc3xx_native/src/qemu_cc3xx.cc` | `qemu_cc3xx` module registration |
| `tools/qbox/qemu-components/cc3xx_native/CMakeLists.txt` | `gs_create_dymod(qemu_cc3xx)` target |
| `tools/qbox/tests/components/cc3xx/cc3xx_core-tests.cc` | core-only tests |
| `tools/qbox/tests/components/cc3xx/qemu_cc3xx-tests.cc` | QEMU wrapper unit/integration tests where practical |

## Core API

Core는 bus framework에 독립적인 byte access API를 제공한다.

```cpp
namespace qbox {
namespace cc3xx {

enum class access_status {
    ok,
    address_error,
    command_error,
};

struct access_result {
    access_status status = access_status::ok;
    uint32_t transferred = 0;
};

struct memory_if {
    virtual ~memory_if() = default;
    virtual bool read(uint64_t address, uint8_t* data, uint32_t len) = 0;
    virtual bool write(uint64_t address, const uint8_t* data, uint32_t len) = 0;
};

struct trace_config {
    bool enabled = false;
    uint32_t limit = 64;
    uint32_t skip = 0;
    std::string filter = "all";
    uint64_t address_min = 0;
};

class core {
public:
    explicit core(std::string name);

    void set_memory(memory_if* memory);
    void set_trace_config(const trace_config& config);

    void reset(bool count_stats);
    access_result read(uint64_t offset, uint8_t* data, uint32_t len,
                       bool debug);
    access_result write(uint64_t offset, const uint8_t* data, uint32_t len,
                        bool debug);

    const stats_state& stats() const;
    void write_stats_json(std::ostream& out) const;
};

} // namespace cc3xx
} // namespace qbox
```

`trace_config`는 CCI를 직접 참조하지 않는다. SystemC wrapper는 CCI parameter를
읽어 core config로 복사하고, QEMU wrapper는 Lua/CCI parameter를 같은 형태로
복사한다.

## SystemC Wrapper

기존 `cc3xx` public surface는 유지한다.

- `p_trace`, `p_trace_limit`, `p_trace_skip`, `p_trace_filter`,
  `p_trace_address_min`, `p_stats_file`, `p_stats_interval`
- `initiator_socket`
- `target_socket`
- `reset`
- `doreset()`, `b_transport()`, `transport_dbg()`

변경점은 private 구현이 `cc3xx_core` 호출로 바뀌는 것이다.

```text
b_transport(trans, delay)
  -> sync CCI config to core
  -> core.read/write(...)
     -> if DMA: systemc_memory_if uses initiator_socket->b_transport()
  -> translate access_result to TLM response status
  -> interval stats file write
```

Debug access는 현재처럼 PKA SRAM read cursor와 stats를 변경하면 안 된다.

## QEMU-Native Wrapper

`qemu_cc3xx`는 QEMU object model device가 아니라 QBox qemu-component
`sc_module`로 시작한다. 이 모듈은 `QemuInstance&`를 constructor argument로
받고, 자체 `qemu::MemoryRegion`과 `qemu::MemoryRegionOps`를 만든다.

```cpp
class qemu_cc3xx : public sc_core::sc_module {
public:
    qemu_cc3xx(sc_core::sc_module_name name, sc_core::sc_object* o);

    QemuTargetSocket<> target_socket;
    tlm_utils::simple_initiator_socket<qemu_cc3xx, DEFAULT_TLM_BUSWIDTH>
        initiator_socket;
    TargetSignalSocket<bool> reset;

private:
    QemuInstance& m_inst;
    qemu_container m_container;
    qemu::MemoryRegion m_region;
    qemu::MemoryRegionOpsPtr m_ops;
    std::shared_ptr<qemu::AddressSpace> m_system_as;
    qbox::cc3xx::core m_core;
};
```

초기화 흐름:

```text
constructor
  -> m_region = inst.get().object_new_unparented<qemu::MemoryRegion>()
  -> m_ops = inst.get().memory_region_ops_new()
  -> m_ops->set_read_callback(qemu_read)
  -> m_ops->set_write_callback(qemu_write)
  -> m_ops->set_max_access_size(8)
  -> m_region.init_io(m_container, name, window_size, m_ops)
  -> target_socket.init_with_mr(m_region)
  -> m_system_as = inst.get().address_space_get_system_memory()
```

`m_container`는 QEMU object lifetime owner로 쓰는 작은 `qemu::Object` wrapper다.
`MemoryRegion` 자신을 owner로 넘기면 shutdown 시 QEMU `object_unref()`
assertion이 발생하므로, region과 분리된 container owner를 둔다.

`QemuTargetSocket::init_with_mr()`는 같은 `MemoryRegion`을 SystemC/TLM
target으로 노출한다. 첫 cold-path TLM access 후
`QemuMrHintTlmExtension`이 붙으면 CPU-side `QemuInitiatorSocket`은 CPU root에
alias를 설치할 수 있다. 이후 CPU MMIO hot path는 QEMU memory region callback
으로 직접 들어가는 것이 기대 경로다.

완전한 zero-cold-path가 필요하면 후속 단계에서 CPU root에 subregion을 직접
설치하는 QBox API를 추가한다. 첫 구현은 hint 기반 alias 설치를 우선한다.

## Lua Wiring

RSE local crypto path는 기존 router를 유지한다. Lua 5.1의 main function local
variable limit 때문에 새 backend selection 값과 helper function은 global로
정의한다.

```lua
cc3xx_backend = getenv_or("QBOX_RDASPEN_CC3XX_BACKEND", "systemc")
assert(cc3xx_backend == "systemc" or cc3xx_backend == "qemu-native",
       "QBOX_RDASPEN_CC3XX_BACKEND must be systemc or qemu-native")
```

SystemC default와 QEMU-native opt-in은 같은 helper가 만든다.

```lua
function rse_cc3xx_component(target_bind, initiator_bind)
    local component = {
        moduletype = cc3xx_backend == "qemu-native" and "qemu_cc3xx" or "cc3xx";
        target_socket = {
            address = RSE_CC3XX_BASE_S;
            size = 0x00002000;
            bind = target_bind;
        };
        initiator_socket = {bind = initiator_bind};
    }
    if cc3xx_backend == "qemu-native" then
        component.args = {"&qemu_inst"}
        component.size = 0x00002000
    end
    return component
end
```

`remote_crypto_router`를 없애지 않는다. KMU가 `0x50154400`으로 export write를
보내는 경로와 QemuMrHint alias 설치 경로 모두에 필요하다.

`qemu_cc3xx`는 기존 `cc3xx`와 같은 trace/stats CCI parameter surface를
제공한다. runner가 `--cc3xx-stats`, `--cc3xx-trace`, histogram option을 켰을
때 SystemC backend와 QEMU-native backend 모두 동일한 `rse-cc3xx-stats.json`
구조를 남겨야 성능 비교가 가능하다.

runner의 `--cc3xx-qemu-native-backend`는
`QBOX_RDASPEN_CC3XX_BACKEND=qemu-native`와 함께
`QBOX_MMIO_DIRECT_FASTPATH_RANGES=0x50154000:0x2000`을 자동으로 추가한다.
이 fast path는 QEMU CPU MMIO가 `run_on_sysc()` hot path를 거치지 않고 같은
backend로 직접 들어가게 하기 위한 것이다. 사용자가 별도로
`--cc3xx-local-mmio-fastpath`를 지정한 경우에도 같은 range 목록에 병합한다.

## DMA 설계

`qemu_cc3xx` memory callback은 두 단계로 DMA memory를 처리한다.

1. QEMU `AddressSpace::read/write()`를 먼저 시도한다.
2. 실패하면 제한된 TLM fallback을 사용한다.

RSE BL1_2 validation에서 DMA chunk 수는 register access 수보다 훨씬 작다.
따라서 register hot path를 QEMU-local로 옮기는 것이 우선이며, DMA fallback이
일부 남더라도 성능 개선 여지는 크다.

TLM fallback 구현은 다음 원칙을 따른다.

- QEMU iothread lock을 잡은 채 SystemC target을 직접 호출하지 않는다.
- 기존 `QemuInitiatorSocket`의 `run_on_sysc()` 패턴과 동등한 ownership 전환을
  사용한다.
- fallback 횟수와 byte 수를 stats에 남긴다.

## Window Size

CC3XX model 내부 register file은 현재 `0x10000` byte지만, RSE platform mapping
은 `0x50154000:0x2000`이다. QEMU memory region도 `0x2000`으로 제한한다.

`0x10000` 전체를 설치하면 `0x5015A000` 이후 system counter, integrity
checker, TRAM region과 겹칠 수 있으므로 fail 조건이다.

## Backend Label

Runner와 `result.json`에는 다음 label을 기록한다.

| Backend | Label |
| --- | --- |
| 기존 SystemC | `hash-aes-cmac-modular-pka-model` |
| local MMIO fastpath | `hash-aes-cmac-modular-pka-model-local-mmio-fastpath` |
| QEMU-native | `hash-aes-cmac-modular-pka-qemu-native-model` |

`--cc3xx-status-read-fastpath`는 fixed read diagnostic이므로 QEMU-native fidelity
label과 섞지 않는다.

## 위험 및 대응

| 위험 | 대응 |
| --- | --- |
| SystemC/QEMU behavior drift | register side effect는 `cc3xx_core` 한 곳에만 둔다. |
| QEMU callback에서 SystemC fallback deadlock | QEMU AddressSpace first, fallback은 explicit ownership handoff helper 사용. |
| `QemuMrHint` alias가 설치되지 않음 | RSE trace와 QEMU trace로 first/cached access path를 확인하고 필요하면 direct root subregion API task로 승격. |
| window overlap | backend size를 `0x2000`으로 고정하고 Lua/map validation에 추가. |
| secure boot shortcut으로 오해 | runner option과 fidelity label에 secure boot skip이 아님을 기록. |
