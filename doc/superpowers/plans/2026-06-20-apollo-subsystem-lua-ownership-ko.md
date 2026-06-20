# Apollo Subsystem Lua Ownership Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `hw-block/rse.lua`가 Apollo full-system device 대부분을 소유하는 구조를 해체하고, 각 subsystem Lua 파일이 자기 하드웨어 object를 직접 정의하도록 재배치한다.

**Architecture:** `apollo-qvp.lua`는 platform orchestration만 담당하고, `config.lua`가 공통 실행 옵션과 artifact path를 정규화하며, `fabric.lua`가 공통 Container/router를 만든 뒤 `rse.lua`, `ap_compute.lua`, `ros.lua`, `system_mgmt.lua`, `si_cl0.lua`, `si_cl1.lua`가 자기 domain object를 추가한다. 기존 QBox object name, socket name, environment variable, boot marker 문자열은 유지해서 migration 중에도 FVP/QBox 비교와 runtime validator가 같은 대상을 추적한다.

**Tech Stack:** Lua QBox platform config, SystemC/TLM QBox modules, QEMU-backed components, Python validation scripts, `luac`, project QBox boot runners.

---

## 현재 문제

현재 `tools/qbox-platform/platforms/apollo/hw-block/rse.lua`는 이름과 달리
RSE local hardware만 표현하지 않는다. 이 파일은 `platform = { ... }`를 직접
생성하면서 다음 subsystem object를 함께 정의한다.

| 현재 `rse.lua` 영역 | 실제 ownership |
| --- | --- |
| `rse_rom`, `rse_itcm`, `rse_dtcm`, `rse_vm*`, `rse_dma350`, `rse_cc3xx`, `rse_cpu_pass` | RSE |
| `ap_qemu_inst`, `ap_reset_gpio`, `ap_gpex_0`, `ap_gic`, `ap_smmu_0`, `ap_cpu_*`, `host_ap_dram*`, `host_ap_flash` | Primary Compute / AP compute |
| `ap_virtioblk_*`, `ap_virtionet_0`, `ap_virtiorng_0`, `ap_rtc_0` | RoS |
| `host_si_*`, `host_ap_si_*`, `host_rse_si_*`, `host_ap_rse_*`, `host_smdexp2smd_atu`, `host_smcf_sram` | System Management / Safety Island integration |
| `host_si_cl0_sram`, `host_si_cl1_sram`, `host_si_cl*_ppu`, live reset hooks | Safety Island CL0/CL1 service/live boundary |

이 구조는 기존 RD-Aspen RSE-first topology를 빠르게 이식하기에는 유리했지만,
지금은 hardware block별 파일이 실제 hardware ownership을 대표하지 못한다.
특히 `ap_compute.lua`는 AP device를 선언하지 않고 AP-view binding만 후처리하고,
`system_mgmt.lua`는 ownership ledger와 mutation만 가지며,
`si_cl0.lua`/`si_cl1.lua`는 live mode object만 추가한다.

## 목표 구조

`apollo-qvp.lua`가 다음 순서로 platform을 구성하도록 바꾼다.

```lua
local config = dofile(apollo_dir.."hw-block/config.lua")
local fabric = dofile(apollo_dir.."hw-block/fabric.lua")
local rse = dofile(apollo_dir.."hw-block/rse.lua")
local ap_compute = dofile(apollo_dir.."hw-block/ap_compute.lua")
local ros = dofile(apollo_dir.."hw-block/ros.lua")
local system_mgmt = dofile(apollo_dir.."hw-block/system_mgmt.lua")
local si_cl0 = dofile(apollo_dir.."hw-block/si_cl0.lua")
local si_cl1 = dofile(apollo_dir.."hw-block/si_cl1.lua")

local ctx = config.create(apollo_dir)
ctx.modules = {
    rse = rse;
    ap_compute = ap_compute;
    ros = ros;
    system_mgmt = system_mgmt;
    si_cl0 = si_cl0;
    si_cl1 = si_cl1;
}

platform = fabric.create()
rse.define(ctx, platform)
ap_compute.define(ctx, platform)
ros.define(ctx, platform)
system_mgmt.define(ctx, platform)
si_cl0.define(ctx, platform)
si_cl1.define(ctx, platform)

if ctx.apollo_live_cl0 then
    system_mgmt.prepare_live_cl0_integration(ctx, platform)
    si_cl0.enable(ctx, platform)
end

if ctx.apollo_live_cl1 then
    si_cl1.enable(ctx, platform)
end
```

### File Ownership

| 파일 | 책임 |
| --- | --- |
| `tools/qbox-platform/platforms/apollo/hw-block/config.lua` | `QBOX_*` environment parsing, artifact path, live/service-mode flags, cross-file constants exported through `ctx.config` |
| `tools/qbox-platform/platforms/apollo/hw-block/fabric.lua` | `platform = { moduletype = "Container" }`, `host_router`, `keep_alive_0`, 공통 root fabric만 생성 |
| `tools/qbox-platform/platforms/apollo/hw-block/rse.lua` | RSE ROM/flash/OTP, RSE TCM/VM, RSE DMA/KMU/LCM/SAM/ATU/CC3XX, RSE MHU local frames, RSE UART, RSE CPU pass |
| `tools/qbox-platform/platforms/apollo/hw-block/ap_compute.lua` | AP QEMU instance, AP reset GPIO, AP CPU loop, AP BL2 loader, AP flash/DRAM/SRAM, AP GIC/ITS/SMMU/GPEX, AP UART/watchdog/timer/SID/FMU, AP logical view router |
| `tools/qbox-platform/platforms/apollo/hw-block/ros.lua` | RoS peripheral ledger plus AP-visible virtio block/net/rng and PL031 RTC construction |
| `tools/qbox-platform/platforms/apollo/hw-block/system_mgmt.lua` | AP/SI/RSE MHU, AP/RSE logical aliases, host ATU windows, SMCF SRAM, SYSTOP/CSS counter windows, cross-domain reset/power ownership |
| `tools/qbox-platform/platforms/apollo/hw-block/si_cl0.lua` | CL0 host-visible SRAM/control windows plus optional live CL0 CPU/GIC/UART/loader/SCP path |
| `tools/qbox-platform/platforms/apollo/hw-block/si_cl1.lua` | CL1 host-visible SRAM/control windows plus optional live CL1 CPU/GIC/UART/loader/Zephyr path |

## Non-Negotiable Migration Rules

- 기존 QBox object name은 유지한다. 예: `ap_gic`, `host_ap_dram1`,
  `host_rse_si_mhu_pbx`, `si_cl0_cpu_0`, `rse_cpu_pass`.
- 기존 socket names와 bind string은 유지한다. 예:
  `&host_router.initiator_socket`, `&ap_gic.spi_in_65`,
  `&rse_cpu_pass.target_signal_socket_139`.
- boot marker 문자열은 유지한다. `validate_qbox_apollo_fvp_boot_sequence.py`가
  RSE/SI/AP handoff marker를 확인한다.
- `apollo-qvp.lua`는 `ctx`를 먼저 생성한 뒤 `platform = fabric.create()`를
  호출한다. `fabric.create()`는 domain config에 의존하지 않는다.
- subsystem 파일은 `define(ctx, platform)`으로 기본 object를 항상 추가하고,
  live CPU/GIC/loader처럼 mode-dependent object만 `enable(ctx, platform)`에 둔다.
- Safety Island host-visible SRAM/control windows는 service-model boot에서도
  필요하므로 `si_cl0.define()`과 `si_cl1.define()`에서 항상 선언한다. live
  CL0/CL1 CPU, GIC, UART, loader만 `enable()` 조건부 path에 둔다.
- `QBOX_*` env parsing과 artifact path 조합은 `config.lua`에 모으고,
  subsystem 파일은 `ctx.config.<domain>` 값을 읽는다. 단, Lua 5.1 local limit을
  피하기 위한 domain-local large table은 해당 subsystem 파일에 둘 수 있다.
- `rse.lua`가 언급한 Lua 5.1 local variable limit 회피 전략은 유지한다.
  대량 constant는 module table 또는 chunk global로 유지하고, 한 파일 안에서
  새 local을 과도하게 늘리지 않는다.
- 한 task가 끝날 때마다 `luac`, static validator, AP map audit를 실행한다.
  AP/SI/RSE handoff 관련 task 후에는 QBox full-system boot도 실행한다.

## 4관점 리뷰 결과 및 반영 사항

| 관점 | 리뷰 결과 | 계획 반영 |
| --- | --- | --- |
| Architect | 기존 계획의 예시에서는 `ctx` 생성 전에 `fabric.create(ctx)`가 호출될 수 있어 초기화 순서가 불명확했다. 또한 env/config를 각 subsystem으로 동시에 옮기면 중복과 drift가 생긴다. | `config.lua`를 추가하고 `ctx -> platform -> subsystem define -> live enable` 순서를 명시했다. `fabric.create()`는 ctx-free root fabric 생성만 담당한다. |
| HW | MHU, ATU, reset/power, shared SRAM처럼 한 domain만의 IP가 아닌 cross-domain window가 있다. 이를 AP/RSE/SI 파일에 임의로 나누면 Zena CSS HW ownership과 다르게 보일 수 있다. | local domain IP는 subsystem 파일이 소유하고, cross-domain transport/control window는 `system_mgmt.lua`가 소유한다. SI host-visible SRAM/control window는 cluster ownership으로 분리하되 service-model에서도 항상 선언한다. |
| SW | `si_cl0.lua`/`si_cl1.lua`의 현재 public function은 `enable()`이며, validators는 `rse.lua` 파일 위치를 직접 참조한다. 이름 변경이나 validator 후행 수정은 boot regression을 숨길 수 있다. | 기존 `enable()` 이름을 유지하고, validator 업데이트를 각 migration task의 필수 산출물로 둔다. 새 ownership audit를 먼저 report-only로 만들고 최종 task에서 fail gate로 전환한다. |
| Test | 현재 AP map audit는 `rse.lua` 중심으로 coverage를 계산한다. object 이동 후 parser가 새 owner 파일을 보지 못하면 실제 map regression과 parser regression을 구분하기 어렵다. | Task 0을 추가해 object ownership inventory를 남기고, Task 2에서 AP map parser를 multi-owner로 확장한다. 최종 gate는 Lua syntax, full map, AP map, boot sequence, runtime boot, coverage audit를 모두 포함한다. |

## Task 0: Ownership inventory와 audit baseline

**Files:**
- Create: `scripts/test/audit_qbox_apollo_lua_ownership.py`
- Generate: `build/qbox-apollo-fvp/subsystem-lua-ownership-before.json`

- [ ] **Step 1: 현재 object ownership inventory 생성**

Create a lightweight parser that scans all Apollo `hw-block/*.lua` files and
records:

```text
object name
owner file
moduletype
explicit address/size/bind fields if statically visible
domain classification: rse, ap_compute, ros, system_mgmt, si_cl0, si_cl1, unknown
```

The first version must support `--report-only` so the current monolithic
`rse.lua` state can be recorded without failing the build.

- [ ] **Step 2: Baseline 실행**

Run:

```bash
python3 scripts/test/audit_qbox_apollo_lua_ownership.py \
  --report-only \
  --output build/qbox-apollo-fvp/subsystem-lua-ownership-before.json
```

Expected:

```text
command exits 0
report lists AP/RoS/SI/system_mgmt objects currently owned by rse.lua
```

- [ ] **Step 3: Baseline을 migration checklist로 사용**

Use the generated JSON as the move checklist for Tasks 1-5. Do not remove an
object from `rse.lua` unless the same object name appears in the intended owner
file and existing map validators still cover it.

## Task 1: 공통 config/fabric 분리

**Files:**
- Create: `tools/qbox-platform/platforms/apollo/hw-block/config.lua`
- Create: `tools/qbox-platform/platforms/apollo/hw-block/fabric.lua`
- Modify: `tools/qbox-platform/platforms/apollo/apollo-qvp.lua`
- Modify: `tools/qbox-platform/platforms/apollo/hw-block/rse.lua`
- Modify: `scripts/test/validate_qbox_apollo_fvp_full_map.py`
- Modify: `doc/apollo-qbox-hardware-ko.md`

- [ ] **Step 1: Create `config.lua`**

Move shared `QBOX_*` env helpers and cross-file execution settings out of
`apollo-qvp.lua` and `rse.lua`. The first pass should expose stable fields but
avoid moving every address constant immediately:

```lua
local config = {}

local function getenv_or(name, default)
    local value = os.getenv(name)
    if value == nil or value == "" then
        return default
    end
    return value
end

local function getenv_number_or(name, default)
    local value = tonumber(getenv_or(name, default))
    assert(value ~= nil, name.." must be numeric")
    return value
end

local function getenv_bool_or(name, default)
    local value = getenv_or(name, default and "true" or "false")
    return value == "true" or value == "1" or value == "yes"
end

function config.create(apollo_dir)
    local root = apollo_dir.."../../../../"
    local si_mode = getenv_or("QBOX_APOLLO_FULL_SI_MODE", "service-model")

    return {
        apollo_dir = apollo_dir;
        apollo_root = root;
        getenv_or = getenv_or;
        getenv_number_or = getenv_number_or;
        getenv_bool_or = getenv_bool_or;
        apollo_si_mode = si_mode;
        apollo_live_cl1 =
            getenv_bool_or("QBOX_APOLLO_FULL_LIVE_CL1", false) or
            si_mode == "live-cl1" or si_mode == "live-cl0-cl1";
        apollo_live_cl0 =
            getenv_bool_or("QBOX_APOLLO_FULL_LIVE_CL0", false) or
            si_mode == "live-cl0-cl1";
        config = {
            rse = {};
            ap = {};
            ros = {};
            system_mgmt = {};
            si_cl0 = {};
            si_cl1 = {};
        };
    }
end

return config
```

`config.lua` is allowed to grow in later tasks, but the first commit should
only move values that are already shared or needed by multiple owner files.

- [ ] **Step 2: Create `fabric.lua`**

Create only root platform objects that are not owned by a specific subsystem:

```lua
local fabric = {}

function fabric.create()
    return {
        moduletype = "Container";
        quantum_ns = 10000000;

        host_router = {
            moduletype = "router";
            log_level = 0;
        };

        keep_alive_0 = {
            moduletype = "keep_alive";
        };
    }
end

return fabric
```

- [ ] **Step 3: Make `rse.lua` additive**

Change `platform = { ... }` in `rse.lua` to:

```lua
local rse = {}

function rse.define(ctx, platform)
    local rse_cfg = ctx.config.rse

    platform.rse_router = {
        moduletype = "router";
        log_level = 0;
    }

    platform.qemu_inst_mgr = {
        moduletype = "QemuInstanceManager";
    }

    platform.qemu_inst = {
        moduletype = "QemuInstance";
        args = {"&platform.qemu_inst_mgr", "AARCH64"};
        sync_policy = "multithread-freerunning";
        qemu_args = rse_cfg.qemu_args;
    }

    -- Move only existing RSE-owned object literals here in this task.
end

return rse
```

Move these existing object blocks into `rse.define()` without changing their
contents: `rse_router`, `qemu_inst_mgr`, `qemu_inst`, `rse_rom`,
`rse_itcm`, `rse_itcm_cpu0`, `rse_dtcm`, `rse_dtcm_cpu0`, `rse_vm0`,
`rse_vm1`, `rse_boot_flash`, `rse_otp_wrapper`, `rse_cpu0_secctrl_regs`,
`rse_cpu0_pwrctrl_regs`, `rse_cpu0_identity_regs`, `rse_nsacfg_regs`,
`rse_dma350`, `rse_sacfg_regs`, `rse_kmu_regs`, `rse_lcm_regs`,
`rse_sam_regs`, `rse_mpc_vm0_regs`, `rse_mpc_vm1_regs`, `rse_atu_regs`,
`rse_sic_regs`, `rse_mpc_sic_regs`, `rse_cc3xx`,
`rse_syscntr_cntrl_regs`, `rse_syscntr_read_regs`,
`rse_integrity_checker_regs`, `rse_tram`, `rse_mhu0_sender_s`,
`rse_mhu0_receiver_s`, `rse_mhu2_sender_s`, `rse_mhu2_receiver_s`,
`rse_sysctrl`, `rse_integ_layer_regs`, `rse_uart_file`,
`rse_host_uart0_s`, `rse_cpu_pass`.

- [ ] **Step 4: Update `apollo-qvp.lua` orchestration**

Replace the current `local rse = dofile(...)` side-effect dependency with:

```lua
local config = dofile(apollo_dir.."hw-block/config.lua")
local fabric = dofile(apollo_dir.."hw-block/fabric.lua")
local rse = dofile(apollo_dir.."hw-block/rse.lua")

local ctx = config.create(apollo_dir)
ctx.modules = {
    rse = rse;
}

platform = fabric.create()
rse.define(ctx, platform)
```

Keep any existing `ctx` fields that are still needed by downstream modules,
but move env parsing into `config.lua` instead of duplicating helpers in
`apollo-qvp.lua`.

- [ ] **Step 5: Run syntax and static validation**

Run:

```bash
luac -p tools/qbox-platform/platforms/apollo/hw-block/*.lua \
  tools/qbox-platform/platforms/apollo/apollo-qvp.lua
python3 scripts/test/validate_qbox_apollo_fvp_full_map.py
python3 scripts/test/validate_qbox_apollo_fvp_boot_sequence.py --static-only
python3 scripts/test/audit_qbox_apollo_lua_ownership.py \
  --report-only \
  --output build/qbox-apollo-fvp/subsystem-lua-ownership-task1.json
```

Expected:

```text
luac exits 0
full-map-validation.json has "passed": true
boot-sequence static output has "passed": true
```

- [ ] **Step 6: Commit**

```bash
git -C tools/qbox-platform add \
  platforms/apollo/apollo-qvp.lua \
  platforms/apollo/hw-block/config.lua \
  platforms/apollo/hw-block/fabric.lua \
  platforms/apollo/hw-block/rse.lua
git -C tools/qbox-platform commit -s \
  -m "refactor(apollo): split root fabric"
```

## Task 2: AP compute object ownership 이동

**Files:**
- Modify: `tools/qbox-platform/platforms/apollo/hw-block/rse.lua`
- Modify: `tools/qbox-platform/platforms/apollo/hw-block/config.lua`
- Modify: `tools/qbox-platform/platforms/apollo/hw-block/ap_compute.lua`
- Modify: `scripts/test/audit_qbox_apollo_ap_memory_map.py`
- Modify: `scripts/test/validate_qbox_apollo_fvp_full_map.py`
- Modify: `doc/apollo-qbox-hardware-ko.md`

- [ ] **Step 1: Add `ap_compute.define()`**

Keep `ap_compute.enable_ap_view_router(ctx, platform)` and add a new
construction function above it:

```lua
function ap_compute.define(ctx, platform)
    local ap = ctx.config.ap

    platform.ap_qemu_inst_mgr = ap.enable_cpus and {
        moduletype = "QemuInstanceManager";
    } or nil

    platform.ap_qemu_inst = ap.enable_cpus and {
        moduletype = "QemuInstance";
        args = {"&platform.ap_qemu_inst_mgr", "AARCH64"};
        accel = "tcg";
        tcg_mode = "MULTI";
        sync_policy = "multithread-freerunning";
        qemu_args = ap.qemu_args;
    } or nil

    -- Move AP-owned object literals here without renaming them.
end
```

Move these existing object blocks from `rse.lua` into `ap_compute.define()`:
`ap_qemu_inst_mgr`, `ap_qemu_inst`, `ap_reset_gpio`,
`ap_global_peripheral_initiator`, `ap_gpex_0`, `host_ap_shared_sram`,
`ap_bl2_reset_loader`, `host_ap_mhu_ns_shared_sram`,
`host_ap_bl2_header_sram`, `host_ap_flash`, `rse_ap_fip_logical`,
`host_ap_trusted_nvctr`, `host_ap_dram1`, `host_ap_ffa_mm_comm_buffer`,
`host_ap_spmc_sdram`, `host_ap_dram2`, `ap_gic`, `ap_gic_its`,
`ap_smmu_0`, `ap_watchdog_0`, `ap_secure_console_file`,
`ap_primary_console_file`, `ap_secure_uart`, `ap_primary_uart`,
`ap_timer_mem`, `ap_secure_timer_frame`, `ap_secure_wdog`,
`ap_secure_wdog_refresh`, `ap_sid`, `ap_rgic2lgic_messreg`,
`ap_cl0_ni710ae_fmu`, `ap_cl1_ni710ae_fmu`, `ap_cl2_ni710ae_fmu`,
`ap_cl3_ni710ae_fmu`, and the `ap_cpu_*` loop.

- [ ] **Step 2: Move AP helper functions and constants**

Move these AP-only definitions from `rse.lua` to `ap_compute.lua`:
`ap_cpu_reset_bind_targets()`, `ap_system_reset_bind_targets()`,
`mp_affinity()`, `repeat_value()` if only AP GIC uses it,
`ap_smmu_component()`, `AP_BL2_RESET`, `HOST_AP_*`, `AP_*`, and
`ARCH_TIMER_*` constants.

Move AP env/config values such as `QBOX_RDASPEN_AP_QEMU_ARGS`,
`QBOX_RDASPEN_ENABLE_AP_CPUS`, AP trace flags, AP log paths, AP flash path,
and AP map-file paths into `ctx.config.ap`. Keep cross-domain constants used
by `system_mgmt.lua` in `ctx.config.system_mgmt` or move them in Task 4, not
in this task.

- [ ] **Step 3: Call AP construction before live CL0 integration**

In `apollo-qvp.lua`, after `rse.define(ctx, platform)`:

```lua
ap_compute.define(ctx, platform)
```

This call must happen before `system_mgmt.prepare_live_cl0_integration()`
because that function lowers AP decode priority and enables AP view routing.

- [ ] **Step 4: Update AP map validator to parse all owner files**

In `scripts/test/audit_qbox_apollo_ap_memory_map.py`, change
`current_coverage()` so it scans these files:

```python
for lua_file in [
    "rse.lua",
    "ap_compute.lua",
    "ros.lua",
    "system_mgmt.lua",
    "si_cl0.lua",
    "si_cl1.lua",
]:
    text = read_text(root / "tools/qbox-platform/platforms/apollo/hw-block" / lua_file)
    sockets.extend(parse_object_sockets(text, lua_file, constants, tables))
```

Update expected source names in the output from only `rse.lua` to the new
owner file names.

- [ ] **Step 5: Validate**

Run:

```bash
luac -p tools/qbox-platform/platforms/apollo/hw-block/*.lua \
  tools/qbox-platform/platforms/apollo/apollo-qvp.lua
python3 scripts/test/validate_qbox_apollo_fvp_full_map.py
python3 scripts/test/audit_qbox_apollo_ap_memory_map.py \
  --output build/qbox-apollo-fvp/subsystem-lua-ap-map.json
python3 scripts/test/validate_qbox_apollo_fvp_boot_sequence.py --static-only
python3 scripts/test/audit_qbox_apollo_lua_ownership.py \
  --report-only \
  --output build/qbox-apollo-fvp/subsystem-lua-ownership-ap-compute.json
```

Expected:

```text
subsystem-lua-ap-map.json has "passed": true
no AP required row moves from covered/partial_model to missing
```

- [ ] **Step 6: Runtime smoke**

Run:

```bash
python3 scripts/run/run_qbox_apollo_fvp_full.py \
  --si-mode live-cl0-cl1 \
  --timeout 600 \
  --post-login-probe \
  --skip-build \
  --out-dir build/qbox-apollo-fvp/full-subsystem-lua-ap-compute
```

Expected:

```text
summary.txt contains "passed: True"
result.json has "passed": true
```

## Task 3: RoS object construction 이동

**Files:**
- Modify: `tools/qbox-platform/platforms/apollo/hw-block/rse.lua`
- Modify: `tools/qbox-platform/platforms/apollo/hw-block/config.lua`
- Modify: `tools/qbox-platform/platforms/apollo/hw-block/ros.lua`
- Modify: `tools/qbox-platform/platforms/apollo/hw-block/ap_compute.lua`
- Modify: `scripts/test/validate_qbox_apollo_fvp_full_map.py`
- Modify: `doc/apollo-qbox-hardware-ko.md`

- [ ] **Step 1: Add `ros.define()`**

Add:

```lua
function ros.define(ctx, platform)
    local ap = ctx.config.ap
    local ros_cfg = ctx.config.ros

    platform.ap_virtioblk_0 = ap.enable_cpus and {
        moduletype = "virtio_mmio_blk";
        args = {"&platform.ap_qemu_inst"};
        mem = {
            address = ros_cfg.virtio.block_base[1];
            size = ros_cfg.virtio.mmio_size;
            bind = "&host_router.initiator_socket";
            mirror_4k_aperture = true;
        };
        irq_out = {bind = "&ap_gic.spi_in_"..ros_cfg.virtio.block_irq[1]};
        blkdev_str = "file="..ros_cfg.virtio.disk_image..",format=raw,if=none,cache=writeback";
        trace = ros_cfg.virtio.trace;
        trace_file = ros_cfg.virtio.trace_file;
        trace_limit = ros_cfg.virtio.trace_limit;
        trace_filter = ros_cfg.virtio.trace_filter;
    } or nil

    -- Move ap_virtioblk_1..3, ap_virtionet_0,
    -- ap_virtiorng_0, and ap_rtc_0 here.
end
```

- [ ] **Step 2: Move RoS config data**

Move `ap_virtio` from `rse.lua` to `ctx.config.ros.virtio` in `config.lua`,
then consume it from `ros.lua`. Keep environment variable names unchanged:

```lua
QBOX_RDASPEN_ROOTFS
QBOX_RDASPEN_EXTRA_BLK1
QBOX_RDASPEN_EXTRA_BLK2
QBOX_RDASPEN_EXTRA_BLK3
QBOX_APOLLO_NETDEV
QBOX_RDASPEN_VIRTIO_TRACE
```

- [ ] **Step 3: Call RoS construction before AP view routing**

In `apollo-qvp.lua`, call:

```lua
ros.define(ctx, platform)
```

Place it after `ap_compute.define(ctx, platform)` because RoS virtio devices
need `platform.ap_qemu_inst` and `platform.ap_gic`, but before
`system_mgmt.prepare_live_cl0_integration()` because AP view routing must see
the RoS targets.

- [ ] **Step 4: Keep AP view routing in AP compute**

Keep object construction ownership in `ros.lua`. AP logical view wiring remains
AP compute ownership. Therefore either:

```text
ros.lua constructs ap_virtioblk_*/ap_virtionet_0/ap_virtiorng_0/ap_rtc_0
ap_compute.lua calls ros.bind_ap_view_targets() to bind AP logical view
```

or, if AP view routing is expanded directly in `ap_compute.lua`, remove only
the helper function and update validators to detect direct AP-view binding
assignments. Do not move RoS object construction into `ap_compute.lua`.

- [ ] **Step 5: Validate**

Run:

```bash
luac -p tools/qbox-platform/platforms/apollo/hw-block/*.lua \
  tools/qbox-platform/platforms/apollo/apollo-qvp.lua
python3 scripts/test/validate_qbox_apollo_fvp_full_map.py
python3 scripts/test/audit_qbox_apollo_ap_memory_map.py \
  --output build/qbox-apollo-fvp/subsystem-lua-ros-map.json
python3 scripts/test/audit_qbox_apollo_lua_ownership.py \
  --report-only \
  --output build/qbox-apollo-fvp/subsystem-lua-ownership-ros.json
```

Expected:

```text
RoS check names pass
AP Memory Expansion row remains covered by virtio and RTC objects
```

## Task 4: System Management ownership 이동

**Files:**
- Modify: `tools/qbox-platform/platforms/apollo/hw-block/rse.lua`
- Modify: `tools/qbox-platform/platforms/apollo/hw-block/config.lua`
- Modify: `tools/qbox-platform/platforms/apollo/hw-block/system_mgmt.lua`
- Modify: `tools/qbox-platform/platforms/apollo/hw-block/si_cl0.lua`
- Modify: `tools/qbox-platform/platforms/apollo/hw-block/si_cl1.lua`
- Modify: `scripts/test/validate_qbox_apollo_fvp_full_map.py`
- Modify: `scripts/test/audit_qbox_apollo_ap_memory_map.py`
- Modify: `scripts/test/validate_qbox_apollo_fvp_boot_sequence.py`
- Modify: `doc/apollo-qbox-hardware-ko.md`

- [ ] **Step 1: Add `system_mgmt.define()`**

Add:

```lua
function system_mgmt.define(ctx, platform)
    -- Cross-domain MHU, ATU, shared SRAM, and control windows.
end
```

Move these existing object blocks from `rse.lua`:
`host_rse_si_mhu_pbx`, `host_rse_si_mhu_mbx`, `host_rse_si_ssram`,
`host_ap_atu`, `host_ap_si_ns_scmi_mhu_pbx`,
`host_ap_si_ns_scmi_mhu_mbx`, `host_ap_si_scmi_mhu_pbx`,
`host_ap_si_scmi_mhu_mbx`, `host_ap_si_cl1_mhu_pbx`,
`host_ap_si_cl1_mhu_mbx`, `host_ap_si_pfdi_monitor_mhu_pbx`,
`host_smdexp2smd_atu`, `host_systop_pik`, `host_css_counters_timers`,
`host_smcf_sram`, `host_ap_rse_mhu_pbx`, `host_ap_rse_mhu_mbx`,
`host_ap_rse_mailbox`.

These objects are not "owned by RSE" just because RSE firmware touches them.
They model messaging, translation, shared memory, reset, or power/control
fabric between domains, so the source file should represent the HW block
boundary rather than the first booting CPU.

- [ ] **Step 2: Move system-management constants**

Move these constants from `rse.lua` to `system_mgmt.lua`:
`HOST_AP_SI_SCMI_MHU_PBX_PHYS_BASE`,
`HOST_AP_SI_SCMI_MHU_MBX_PHYS_BASE`, `HOST_AP_SI_MHU_FRAME_SIZE`,
`HOST_AP_SI_PFDI_MONITOR_MHU_PBX_PHYS_BASE`,
`HOST_AP_SCMI_PFDI_MONITOR_BASE`, `HOST_AP_SCMI_PFDI_MONITOR_STRIDE`,
`HOST_AP_SCMI_PFDI_MONITOR_CHANNELS`, `HOST_AP_ATU_PHYS_BASE`,
`HOST_SMDEXP2SMD_ATU_PHYS_BASE`, `HOST_CSS_COUNTERS_TIMERS_PHYS_BASE`,
`HOST_CSS_COUNTERS_TIMERS_SIZE`, `HOST_SYSTOP_PIK_PHYS_BASE`,
`HOST_SMCF_SRAM_PHYS_BASE`, `HOST_SMCF_SRAM_SIZE`,
`HOST_AP_RSE_MHU_PHYS_BASE`, `HOST_AP_RSE_MHU_SIZE`,
`MHU_V3_FRAME_SIZE`, `HOST_AP_MHU_POINTER_ACCESS_PHYS_BASE`,
`HOST_AP_MHU_POINTER_ACCESS_SIZE`, `HOST_AP_RSE_MAILBOX_PHYS_BASE`,
`HOST_AP_RSE_MAILBOX_SIZE`.

- [ ] **Step 3: Split Safety Island host-visible windows**

Move `host_si_cl0_sram`, `host_si_cl0_cub`, `host_si_cl0_clus_ppu`,
`host_si_cl0_core0_ppu` to `si_cl0.define(ctx, platform)`.

Move `host_si_cl1_sram`, `host_si_cl1_cub`, `host_si_cl1_clus_ppu` to
`si_cl1.define(ctx, platform)`.

Keep `host_si_pik`, `host_si_scr`, and `host_si_atu` in
`system_mgmt.define()` because they represent system-wide management/control
windows rather than a single cluster's live CPU path.

`si_cl0.define()` and `si_cl1.define()` must run for both service-model and
live modes. `si_cl0.enable()` and `si_cl1.enable()` should contain only live
CPU/GIC/UART/loader additions and live reset fanout.

- [ ] **Step 4: Update boot-sequence static validator**

In `scripts/test/validate_qbox_apollo_fvp_boot_sequence.py`, change the static
source lookup so it checks the owner file after migration:

```python
system_mgmt = apollo / "hw-block" / "system_mgmt.lua"
si_cl0 = apollo / "hw-block" / "si_cl0.lua"
si_cl1 = apollo / "hw-block" / "si_cl1.lua"
```

Keep the same required bind strings, but expect CL0/CL1 PPU reset wiring in
`si_cl0.lua` or `si_cl1.lua` after the move.

Also update marker-order checks so SI pre-load/image-loaded/release marker
strings are searched in the file that owns the loader/release path after the
move, not hardcoded to `rse.lua`.

- [ ] **Step 5: Validate and boot**

Run:

```bash
luac -p tools/qbox-platform/platforms/apollo/hw-block/*.lua \
  tools/qbox-platform/platforms/apollo/apollo-qvp.lua
python3 scripts/test/validate_qbox_apollo_fvp_full_map.py
python3 scripts/test/audit_qbox_apollo_ap_memory_map.py \
  --output build/qbox-apollo-fvp/subsystem-lua-system-mgmt-ap-map.json
python3 scripts/test/validate_qbox_apollo_fvp_boot_sequence.py --static-only
python3 scripts/test/audit_qbox_apollo_lua_ownership.py \
  --report-only \
  --output build/qbox-apollo-fvp/subsystem-lua-ownership-system-mgmt.json
python3 scripts/run/run_qbox_apollo_fvp_full.py \
  --si-mode live-cl0-cl1 \
  --timeout 600 \
  --post-login-probe \
  --skip-build \
  --out-dir build/qbox-apollo-fvp/full-subsystem-lua-system-mgmt
```

Expected:

```text
full-map validation passes
system-mgmt AP map output has "passed": true
boot-sequence static validation passes
full-system boot result.json has "passed": true
```

## Task 5: `rse.lua`를 RSE 전용 파일로 수렴

**Files:**
- Modify: `tools/qbox-platform/platforms/apollo/hw-block/rse.lua`
- Modify: `tools/qbox-platform/platforms/apollo/hw-block/config.lua`
- Modify: `tools/qbox-platform/platforms/apollo/hw-block/ap_compute.lua`
- Modify: `tools/qbox-platform/platforms/apollo/hw-block/ros.lua`
- Modify: `tools/qbox-platform/platforms/apollo/hw-block/system_mgmt.lua`
- Modify: `scripts/test/audit_qbox_apollo_lua_ownership.py`
- Modify: `doc/apollo-qbox-hardware-ko.md`
- Modify: `tools/qbox-platform/platforms/apollo/README.md`

- [ ] **Step 1: Remove non-RSE sections from `rse.lua`**

After Tasks 1-4, `rse.lua` must contain only:

```text
RSE artifact path/env parsing that has not moved to config.lua
RSE trace/performance options
RSE address constants
RSE helper functions
rse.define(ctx, platform)
RSE NVIC signal loop
return rse
```

No object names beginning with these prefixes should remain in `rse.lua`:

```text
ap_
host_ap_
host_si_
host_rse_si_
host_smd
si_cl0_
si_cl1_
```

Allowed exceptions:

```text
RSE-to-AP/SI IRQ constants used by RSE local MHU bindings
RSE host access alias constants used by rse_atu_regs
```

- [ ] **Step 2: Add a structural audit**

Turn the Task 0 checker into a fail gate:

```python
FORBIDDEN_IN_RSE = [
    r"platform\.ap_",
    r"platform\.host_ap_",
    r"platform\.host_si_",
    r"platform\.host_rse_si_",
]
```

The checker must fail if `rse.lua` regresses into owning AP/RoS/SI/system
objects again.

Required command:

```bash
python3 scripts/test/audit_qbox_apollo_lua_ownership.py \
  --output build/qbox-apollo-fvp/subsystem-lua-ownership-final.json
```

Expected:

```text
subsystem-lua-ownership-final.json has "passed": true
rse.lua forbidden ownership count is 0
```

- [ ] **Step 3: Update docs**

Update `doc/apollo-qbox-hardware-ko.md` so the Lua 구성 분석 table states:

```text
rse.lua: RSE-local secure boot and RSE-local peripherals only
ap_compute.lua: AP firmware chain, CPU, memory, GIC/SMMU, AP I/O
ros.lua: RoS virtio/RTC and RoS peripheral ledger
system_mgmt.lua: cross-domain MHU/ATU/reset/shared-memory windows
si_cl0.lua: SI CL0 service/live hardware
si_cl1.lua: SI CL1 service/live hardware
```

Update `tools/qbox-platform/platforms/apollo/README.md` with the same owner map.

- [ ] **Step 4: Final validation ladder**

Run:

```bash
luac -p tools/qbox-platform/platforms/apollo/hw-block/*.lua \
  tools/qbox-platform/platforms/apollo/apollo-qvp.lua
python3 scripts/test/validate_qbox_apollo_fvp_full_map.py
python3 scripts/test/audit_qbox_apollo_ap_memory_map.py \
  --output build/qbox-apollo-fvp/subsystem-lua-final-ap-map.json
python3 scripts/test/validate_qbox_apollo_fvp_boot_sequence.py --static-only
python3 scripts/test/audit_qbox_apollo_lua_ownership.py \
  --output build/qbox-apollo-fvp/subsystem-lua-ownership-final.json
```

Expected:

```text
all commands exit 0
subsystem-lua-final-ap-map.json has "passed": true
```

- [ ] **Step 5: Full-system runtime gate**

Run:

```bash
python3 scripts/run/run_qbox_apollo_fvp_full.py \
  --si-mode live-cl0-cl1 \
  --timeout 600 \
  --post-login-probe \
  --skip-build \
  --out-dir build/qbox-apollo-fvp/full-subsystem-lua-final
```

Expected:

```text
build/qbox-apollo-fvp/full-subsystem-lua-final/summary.txt contains:
passed: True
blocker: none
```

- [ ] **Step 6: Final coverage audit**

Run coverage against the final runtime result, not an earlier migration task:

```bash
python3 scripts/test/audit_qbox_apollo_fvp_full_coverage.py \
  --result-json build/qbox-apollo-fvp/full-subsystem-lua-final/result.json \
  --output build/qbox-apollo-fvp/subsystem-lua-final-coverage.json
```

Expected:

```text
subsystem-lua-final-coverage.json has "passed": true
```

## Task 6: Atomic commits

**Files:**
- Stage only files touched by each task.

- [ ] **Step 1: Commit qbox-platform Lua migration**

```bash
git -C tools/qbox-platform status --short
git -C tools/qbox-platform diff --stat
git -C tools/qbox-platform add \
  platforms/apollo/apollo-qvp.lua \
  platforms/apollo/hw-block/config.lua \
  platforms/apollo/hw-block/fabric.lua \
  platforms/apollo/hw-block/rse.lua \
  platforms/apollo/hw-block/ap_compute.lua \
  platforms/apollo/hw-block/ros.lua \
  platforms/apollo/hw-block/system_mgmt.lua \
  platforms/apollo/hw-block/si_cl0.lua \
  platforms/apollo/hw-block/si_cl1.lua \
  platforms/apollo/README.md
git -C tools/qbox-platform commit -s \
  -m "refactor(apollo): split subsystem lua"
```

- [ ] **Step 2: Commit top-level tests/docs/submodule pointer**

```bash
git status --short
git diff --stat
git add \
  scripts/test/audit_qbox_apollo_ap_memory_map.py \
  scripts/test/validate_qbox_apollo_fvp_full_map.py \
  scripts/test/validate_qbox_apollo_fvp_boot_sequence.py \
  scripts/test/audit_qbox_apollo_lua_ownership.py \
  doc/apollo-qbox-hardware-ko.md \
  doc/superpowers/plans/2026-06-20-apollo-subsystem-lua-ownership-ko.md \
  tools/qbox-platform
git commit -s \
  -m "test(qbox): validate subsystem lua ownership"
```

## Self-Review

- Spec coverage: 이 계획은 `rse.lua` 대신 각 subsystem Lua 파일이 해당
  hardware 정의를 소유하게 만드는 작업을 `config`, `fabric`, RSE, AP, RoS,
  System Management, SI CL0, SI CL1로 분리한다.
- Architect/HW/SW/Test review: 초기화 순서, cross-domain ownership, 기존
  Lua public API, validator drift 위험을 계획에 반영했다.
- Placeholder scan: 실행 단계와 검증 명령은 모두 구체적인 파일과 명령을
  포함한다.
- Type/name consistency: migration 중 QBox object name과 socket name은
  유지한다. `si_cl0.enable()`/`si_cl1.enable()` public function 이름도
  유지하고, validator는 파일 위치 변경만 따라간다.
- Risk: `rse.lua`의 local variable limit이 재발할 수 있으므로 대량 constant
  이동은 module table 또는 chunk global을 사용하고, 각 task마다 `luac -p`를
  gate로 둔다.
