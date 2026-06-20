# QBox Local Build Boot Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Boot the artifacts produced by `./local-build.sh build` on the QBox
Apollo FVP primary-compute platform and validate Linux login with file-backed
logs.

**Architecture:** Use the existing QBox Apollo primary-compute direct-boot path
as the first acceptance target. QBox loads the locally built Linux `Image`, a
QBox-compatible Apollo DTB, and the locally built Buildroot initramfs directly
into guest RAM, then starts the existing AArch64 boot stub. This deliberately
bypasses RSE, TF-A, OP-TEE, and U-Boot in phase 1; full firmware-chain boot can
be planned separately after the direct Linux path is stable.

**Tech Stack:** Bash, Python 3, QBox `platforms-vp`, Lua platform config,
Device Tree Compiler tools (`dtc`, `fdtput`), local Apollo build artifacts,
and file-backed QBox UART logs.

---

## Current Context

- Local build entrypoint: `./local-build.sh build`
- Local deploy root: `build/local-apollo-fvp/deploy/`
- Local Linux image: `build/local-apollo-fvp/deploy/boot/Image`
- Local initramfs: `build/local-apollo-fvp/deploy/boot/initramfs.cpio.gz`
- Local FVP DTB: `build/local-apollo-fvp/deploy/boot/apollo-fvp.dtb`
- QBox Apollo runner: `scripts/run/run_qbox_apollo_fvp_linux.py`
- QBox Apollo entrypoints:
  - `./local-build.sh qbox`
  - `python3 scripts/run/run_qbox_apollo_fvp_linux.py --skip-build --interactive`
- QBox Apollo platform:
  - `tools/qbox/platforms/apollo-fvp/conf.lua`
  - local-build base DTB plus generated direct-boot overlay

The local FVP DTB describes the full Apollo FVP hardware. The QBox
primary-compute direct-boot platform models only the blocks wired in
`tools/qbox/platforms/apollo-fvp/conf.lua`, so the runner prepares a direct-boot
DTB from the local-build `apollo-fvp.dtb` and a small `/chosen` overlay. The
local build artifacts that should be reused are the kernel `Image`, the base
DTB, and `initramfs.cpio.gz`.

The FVP U-Boot boot script currently uses:

```text
kernel_addr_r=0x80080000
fdt_addr_r=0x8fc00000
ramdisk_addr_r=0x94000000
bootargs=console=ttyAMA0,115200 earlycon=pl011,0x1A400000 root=/dev/ram0 rw rdinit=/init loglevel=7 cpuidle.governor=menu maxcpus=4 mem=4064M
```

QBox should use the same bootargs and load addresses unless map validation
shows an overlap.

## File Structure

- Modify `scripts/run/run_qbox_apollo_fvp_linux.py`
  - Add a local-build artifact resolver.
  - Add `--local-build-dir`, `--initramfs`, `--bootargs`,
    `--initramfs-addr`, and `--post-login-probe`.
  - Generate a per-run DTB that injects bootargs and initramfs metadata.
  - Record artifact paths and probe results in `result.json`.

- Modify `tools/qbox/platforms/apollo-fvp/conf.lua`
  - Load an optional initramfs binary into QBox guest RAM when
    `QBOX_APOLLO_INITRAMFS` is set.
  - Keep the existing disk devices available, but do not require a rootfs disk
    for initramfs boot.

- Modify `local-build.sh`
  - Build QBox targets and generate the Apollo QBox DTB from the local-build
    contract.

- Update the interactive `run_qbox_apollo_fvp_linux.py` command
  - Keep interactive mode, but allow the runner to regenerate the DTB by
    default because initramfs size changes between builds.

- Create `tools/qbox/platforms/apollo-fvp/README.md`
  - Document direct-boot scope, local artifact paths, commands, output logs,
    and the difference from full firmware-chain boot.

- Create `tests/test_run_qbox_apollo_fvp_linux.py`
  - Unit-test local artifact resolution, DTB patch command construction, and
    result metadata generation without launching QBox.

## Task 1: Add Runner Unit Tests

**Files:**
- Create: `tests/test_run_qbox_apollo_fvp_linux.py`
- Modify: `scripts/run/run_qbox_apollo_fvp_linux.py`

- [ ] **Step 1: Create tests for artifact defaults**

Create `tests/test_run_qbox_apollo_fvp_linux.py` with:

```python
from pathlib import Path
import importlib.util


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/run/run_qbox_apollo_fvp_linux.py"


def load_runner():
    spec = importlib.util.spec_from_file_location("apollo_runner", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_local_build_artifacts_are_resolved_from_deploy_root(tmp_path):
    runner = load_runner()
    local_build = tmp_path / "build/local-apollo-fvp"
    deploy_boot = local_build / "deploy/boot"
    deploy_boot.mkdir(parents=True)
    for name in ("Image", "initramfs.cpio.gz"):
        (deploy_boot / name).write_bytes(b"x")

    artifacts = runner.resolve_local_build_artifacts(local_build)

    assert artifacts.kernel == deploy_boot / "Image"
    assert artifacts.initramfs == deploy_boot / "initramfs.cpio.gz"
    assert artifacts.disk == deploy_boot / "apollo-fvp-local-disk.img"


def test_default_bootargs_match_local_fvp_boot_script():
    runner = load_runner()

    assert runner.DEFAULT_LOCAL_BOOTARGS == (
        "console=ttyAMA0,115200 earlycon=pl011,0x1A400000 "
        "root=/dev/ram0 rw rdinit=/init loglevel=7 "
        "cpuidle.governor=menu maxcpus=4 mem=4064M"
    )
```

- [ ] **Step 2: Run the new tests and confirm they fail**

Run:

```bash
pytest tests/test_run_qbox_apollo_fvp_linux.py -q
```

Expected: failure because `resolve_local_build_artifacts` and
`DEFAULT_LOCAL_BOOTARGS` do not exist yet.

- [ ] **Step 3: Add the minimal runner API**

In `scripts/run/run_qbox_apollo_fvp_linux.py`, add near the constants:

```python
from dataclasses import dataclass


DEFAULT_LOCAL_BOOTARGS = (
    "console=ttyAMA0,115200 earlycon=pl011,0x1A400000 "
    "root=/dev/ram0 rw rdinit=/init loglevel=7 "
    "cpuidle.governor=menu maxcpus=4 mem=4064M"
)


@dataclass(frozen=True)
class LocalBuildArtifacts:
    kernel: Path
    initramfs: Path
    disk: Path


def resolve_local_build_artifacts(local_build_dir: Path) -> LocalBuildArtifacts:
    boot_dir = local_build_dir / "deploy/boot"
    return LocalBuildArtifacts(
        kernel=boot_dir / "Image",
        initramfs=boot_dir / "initramfs.cpio.gz",
        disk=boot_dir / "apollo-fvp-local-disk.img",
    )
```

- [ ] **Step 4: Verify tests pass**

Run:

```bash
pytest tests/test_run_qbox_apollo_fvp_linux.py -q
```

Expected: `2 passed`.

- [ ] **Step 5: Commit**

```bash
git add scripts/run/run_qbox_apollo_fvp_linux.py tests/test_run_qbox_apollo_fvp_linux.py
git commit -s -m "test(apollo): cover QBox local artifacts"
```

## Task 2: Load Local Initramfs In QBox

**Files:**
- Modify: `tools/qbox/platforms/apollo-fvp/conf.lua`
- Modify: `tests/test_run_qbox_apollo_fvp_linux.py`

- [ ] **Step 1: Add a test for initramfs environment metadata**

Append to `tests/test_run_qbox_apollo_fvp_linux.py`:

```python
def test_qbox_env_exports_initramfs_path(tmp_path):
    runner = load_runner()
    root = tmp_path
    kernel = tmp_path / "Image"
    dtb = tmp_path / "apollo.dtb"
    initramfs = tmp_path / "initramfs.cpio.gz"
    disk = tmp_path / "disk.img"
    for path in (kernel, dtb, initramfs, disk):
        path.write_bytes(b"x")

    args = type(
        "Args",
        (),
        {
            "kernel": kernel,
            "dtb": dtb,
            "initramfs": initramfs,
            "accel": "tcg",
            "netdev": "type=user",
        },
    )()

    env = runner.qbox_env(root, args, disk, [])

    assert env["QBOX_APOLLO_KERNEL"] == str(kernel.resolve())
    assert env["QBOX_APOLLO_DTB"] == str(dtb.resolve())
    assert env["QBOX_APOLLO_INITRAMFS"] == str(initramfs.resolve())
```

- [ ] **Step 2: Run the test and confirm it fails**

Run:

```bash
pytest tests/test_run_qbox_apollo_fvp_linux.py::test_qbox_env_exports_initramfs_path -q
```

Expected: failure because `qbox_env()` does not export
`QBOX_APOLLO_INITRAMFS`.

- [ ] **Step 3: Export initramfs from the runner**

In `qbox_env()` in `scripts/run/run_qbox_apollo_fvp_linux.py`, add:

```python
    if getattr(args, "initramfs", None):
        env["QBOX_APOLLO_INITRAMFS"] = str(args.initramfs.resolve())
```

- [ ] **Step 4: Load initramfs in Lua**

In `tools/qbox/platforms/apollo-fvp/conf.lua`, add near the load-address
constants:

```lua
_INITRAMFS_LOAD_ADDR = INITIAL_DDR_SPACE + 0x14000000
```

Add near the existing image variables:

```lua
local initramfs_image = os.getenv("QBOX_APOLLO_INITRAMFS")
```

Replace the current `load` table with:

```lua
    load = {
        moduletype = "loader",
        initiator_socket = {bind = "&router.target_socket"};
        { bin_file = kernel_image, address = _KERNEL64_LOAD_ADDR };
        { bin_file = dtb_image, address = _DTB_LOAD_ADDR };
        { data = _bootloader_aarch64, address = INITIAL_DDR_SPACE };
    };
```

Then immediately after the closing `};` line that ends the `platform` table,
append:

```lua
if initramfs_image ~= nil and initramfs_image ~= "" then
    table.insert(platform.load, {
        bin_file = initramfs_image,
        address = _INITRAMFS_LOAD_ADDR
    })
end
```

Add print output:

```lua
if initramfs_image ~= nil and initramfs_image ~= "" then
    print("initramfs:    "..initramfs_image);
    print("initramfs is loaded at: 0x"..string.format("%x", _INITRAMFS_LOAD_ADDR));
end
```

- [ ] **Step 5: Verify Python and Lua syntax paths**

Run:

```bash
python3 -m py_compile scripts/run/run_qbox_apollo_fvp_linux.py
pytest tests/test_run_qbox_apollo_fvp_linux.py -q
```

Expected: Python compile succeeds and all tests pass.

- [ ] **Step 6: Commit**

```bash
git add scripts/run/run_qbox_apollo_fvp_linux.py \
  tools/qbox/platforms/apollo-fvp/conf.lua \
  tests/test_run_qbox_apollo_fvp_linux.py
git commit -s -m "feat(apollo): load local initramfs in QBox"
```

## Task 3: Generate A Local-Build QBox DTB

**Files:**
- Modify: `scripts/run/run_qbox_apollo_fvp_linux.py`
- Modify: `tests/test_run_qbox_apollo_fvp_linux.py`

- [ ] **Step 1: Add tests for DTB patch commands**

Append:

```python
def test_initramfs_end_is_computed_from_size(tmp_path):
    runner = load_runner()
    initramfs = tmp_path / "initramfs.cpio.gz"
    initramfs.write_bytes(b"12345678")

    assert runner.initramfs_range(initramfs, 0x94000000) == (
        0x94000000,
        0x94000008,
    )


def test_fdtput_commands_include_bootargs_and_initrd(tmp_path):
    runner = load_runner()
    dtb = tmp_path / "apollo.dtb"
    bootargs = "console=ttyAMA0 root=/dev/ram0"

    commands = runner.fdt_patch_commands(
        dtb=dtb,
        bootargs=bootargs,
        initrd_start=0x94000000,
        initrd_end=0x94001000,
    )

    assert commands == [
        ["fdtput", "-t", "s", str(dtb), "/chosen", "bootargs", bootargs],
        [
            "fdtput",
            "-t",
            "x",
            str(dtb),
            "/chosen",
            "linux,initrd-start",
            "0x94000000",
        ],
        [
            "fdtput",
            "-t",
            "x",
            str(dtb),
            "/chosen",
            "linux,initrd-end",
            "0x94001000",
        ],
    ]
```

- [ ] **Step 2: Run the DTB tests and confirm they fail**

Run:

```bash
pytest tests/test_run_qbox_apollo_fvp_linux.py::test_initramfs_end_is_computed_from_size \
  tests/test_run_qbox_apollo_fvp_linux.py::test_fdtput_commands_include_bootargs_and_initrd \
  -q
```

Expected: failure because the helper functions do not exist.

- [ ] **Step 3: Add DTB helper functions**

In `scripts/run/run_qbox_apollo_fvp_linux.py`, add:

```python
def initramfs_range(initramfs: Path, load_addr: int) -> tuple[int, int]:
    size = initramfs.stat().st_size
    return load_addr, load_addr + size


def fdt_patch_commands(
    *, dtb: Path, bootargs: str, initrd_start: int, initrd_end: int
) -> list[list[str]]:
    return [
        ["fdtput", "-t", "s", str(dtb), "/chosen", "bootargs", bootargs],
        [
            "fdtput",
            "-t",
            "x",
            str(dtb),
            "/chosen",
            "linux,initrd-start",
            f"0x{initrd_start:x}",
        ],
        [
            "fdtput",
            "-t",
            "x",
            str(dtb),
            "/chosen",
            "linux,initrd-end",
            f"0x{initrd_end:x}",
        ],
    ]
```

Replace `compile_dtb()` with a version that accepts optional boot metadata:

```python
def compile_dtb(
    root: Path,
    dts: Path,
    dtb: Path,
    *,
    bootargs: str | None = None,
    initramfs: Path | None = None,
    initramfs_addr: int | None = None,
) -> None:
    dtc = shutil.which("dtc")
    if not dtc:
        raise RuntimeError("dtc not found; install device-tree-compiler")
    dtb.parent.mkdir(parents=True, exist_ok=True)
    run([dtc, "-I", "dts", "-O", "dtb", "-o", str(dtb), str(dts)], cwd=root)

    if bootargs is None and initramfs is None:
        return

    if not shutil.which("fdtput"):
        raise RuntimeError("fdtput not found; install device-tree-compiler")
    if bootargs is None or initramfs is None or initramfs_addr is None:
        raise RuntimeError("bootargs, initramfs, and initramfs_addr must be set together")

    initrd_start, initrd_end = initramfs_range(initramfs, initramfs_addr)
    for cmd in fdt_patch_commands(
        dtb=dtb,
        bootargs=bootargs,
        initrd_start=initrd_start,
        initrd_end=initrd_end,
    ):
        run(cmd, cwd=root)
```

- [ ] **Step 4: Add CLI options**

In `parse_args()` add:

```python
    parser.add_argument(
        "--local-build-dir",
        type=Path,
        default=root / "build/local-apollo-fvp",
    )
    parser.add_argument("--initramfs", type=Path)
    parser.add_argument("--bootargs", default=DEFAULT_LOCAL_BOOTARGS)
    parser.add_argument(
        "--initramfs-addr",
        type=lambda value: int(value, 0),
        default=0x94000000,
    )
```

After `args = parse_args()` and path resolution, derive local defaults:

```python
    artifacts = resolve_local_build_artifacts(args.local_build_dir)
    if args.kernel is None:
        args.kernel = artifacts.kernel
    if args.initramfs is None:
        args.initramfs = artifacts.initramfs
    if args.disk is None:
        args.disk = artifacts.disk
```

Change the `--kernel` and `--disk` defaults to `None` so the local-build
resolver owns the default paths:

```python
    parser.add_argument("--kernel", type=Path)
    parser.add_argument("--disk", type=Path)
```

When compiling the DTB, call:

```python
        if not args.skip_dtb:
            compile_dtb(
                root,
                args.dts,
                args.dtb,
                bootargs=args.bootargs,
                initramfs=args.initramfs,
                initramfs_addr=args.initramfs_addr,
            )
```

- [ ] **Step 5: Update required path checks**

For non-build-only runs, require:

```python
                (args.kernel, "kernel image"),
                (args.initramfs, "initramfs image"),
```

Do not require `args.disk` for initramfs boot. Keep disk attachment optional:

```python
        disk = args.disk
        if disk and not args.no_copy_disk:
            disk = args.out_dir / args.disk.name
            copy_disk(args.disk, disk)
```

Update `qbox_env()` to only set `QBOX_APOLLO_ROOTFS` when `disk` is not
`None`. Keep extra disks so virtio block probing still works.

When the primary disk is unavailable and was not explicitly requested, patch
the generated DTB so QBox and Linux describe the same primary block-device
topology:

```python
["fdtput", "-t", "s", str(dtb), "/soc/virtio-block@30020000", "status", "disabled"]
```

- [ ] **Step 6: Verify DTB contains initramfs metadata**

Run:

```bash
python3 scripts/run/run_qbox_apollo_fvp_linux.py --build-only --skip-build
fdtdump build/qbox-apollo-fvp/apollo-fvp-direct.dtb | \
  rg -n "bootargs|linux,initrd-start|linux,initrd-end"
```

Expected:

```text
bootargs = "console=ttyAMA0,115200 earlycon=pl011,0x1A400000 root=/dev/ram0 rw rdinit=/init loglevel=7 cpuidle.governor=menu maxcpus=4 mem=4064M";
linux,initrd-start = <0x94000000>;
linux,initrd-end is present and is greater than 0x94000000.
```

- [ ] **Step 7: Commit**

```bash
git add scripts/run/run_qbox_apollo_fvp_linux.py tests/test_run_qbox_apollo_fvp_linux.py
git commit -s -m "feat(apollo): generate QBox local DTB"
```

## Task 4: Make Wrappers Use The Local-Build Contract

**Files:**
- Modify: `./local-build.sh qbox`
- Update: interactive `run_qbox_apollo_fvp_linux.py` command

- [ ] **Step 1: Update the local-build qbox command**

Change the `qbox` command in `local-build.sh` to pass the local build
directory explicitly to the QBox runner:

```bash
args=(--build-only --local-build-dir "${workspace_root}/build/local-apollo-fvp")
```

Use the repository-wide `JOBS` handling from `local-build.sh`.

- [ ] **Step 2: Use the interactive Python runner directly**

Use `scripts/run/run_qbox_apollo_fvp_linux.py` directly so it skips only the
QBox build, not DTB generation:

```bash
python3 scripts/run/run_qbox_apollo_fvp_linux.py \
    --skip-build \
    --interactive \
    --timeout "${QBOX_APOLLO_TIMEOUT:-0}" \
    --local-build-dir build/local-apollo-fvp
```

This keeps the interactive path safe when `initramfs.cpio.gz` changes size.

- [ ] **Step 3: Verify shell syntax**

Run:

```bash
bash -n ./local-build.sh
python3 -m py_compile scripts/run/run_qbox_apollo_fvp_linux.py
```

Expected: no output and exit code 0.

- [ ] **Step 4: Commit**

```bash
git add local-build.sh scripts/run/run_qbox_apollo_fvp_linux.py
git commit -s -m "build(apollo): use local QBox artifacts"
```

## Task 5: Add Login Probe Evidence

**Files:**
- Modify: `scripts/run/run_qbox_apollo_fvp_linux.py`
- Modify: `tests/test_run_qbox_apollo_fvp_linux.py`

- [ ] **Step 1: Add probe constants**

Add to `scripts/run/run_qbox_apollo_fvp_linux.py`:

```python
PROBE_DONE_MARKER = "__QBOX_APOLLO_PROBE_DONE__"
PROBE_DONE_OUTPUT_RE = re.compile(
    rf"(?:^|\n){re.escape(PROBE_DONE_MARKER)}:0(?:\r?\n|$)"
)
POST_LOGIN_PROBE_COMMANDS = [
    "uname -a",
    "cat /proc/cmdline",
    "cat /proc/meminfo | head -n 5",
    "ls -l /dev/vd* 2>/dev/null || true",
    "ip link show || true",
    "dmesg | grep -Ei 'GIC|pl011|ttyAMA|virtio|rng|rtc|watchdog|initrd|Freeing initrd|VFS|Run /init' || true",
    f"printf '\\n{PROBE_DONE_MARKER}:%s\\n' \"$?\"",
]
```

- [ ] **Step 2: Add CLI option**

Add:

```python
    parser.add_argument(
        "--post-login-probe",
        action="store_true",
        help="Log in on the serial console and run Apollo direct-boot probes.",
    )
    parser.add_argument("--login-user", default="root")
```

- [ ] **Step 3: Send login and probe commands**

Mirror the control flow from `scripts/run/run_qbox_fvp_rd_aspen_rse.py`, but use
Apollo login prompts:

```python
if (
    args.post_login_probe
    and not args.interactive
    and proc.stdin is not None
):
    clean_text = ANSI_RE.sub("", text).replace("\r", "")
    if not sent_login and "apollo-fvp login:" in clean_text:
        proc.stdin.write((args.login_user + "\n").encode())
        proc.stdin.flush()
        sent_login = True
    prompt_ready = bool(
        re.search(r"(?:^|\n)(?:root@apollo-fvp:[^\n]*[#>]|\S+ #)\s*$", clean_text)
    )
    if sent_login and not sent_probe and prompt_ready:
        proc.stdin.write(("\n".join(POST_LOGIN_PROBE_COMMANDS) + "\n").encode())
        proc.stdin.flush()
        sent_probe = True
    probe_complete = bool(PROBE_DONE_OUTPUT_RE.search(clean_text))
```

Only stop early when `passed` and either no probe was requested or
`probe_complete` is true.

- [ ] **Step 4: Record probe metadata**

Add these fields to `status`:

```python
    status["post_login_probe"] = args.post_login_probe
    status["probe_complete"] = probe_complete
```

- [ ] **Step 5: Verify Python tests**

Run:

```bash
python3 -m py_compile scripts/run/run_qbox_apollo_fvp_linux.py
pytest tests/test_run_qbox_apollo_fvp_linux.py -q
```

Expected: compile succeeds and tests pass.

- [ ] **Step 6: Commit**

```bash
git add scripts/run/run_qbox_apollo_fvp_linux.py tests/test_run_qbox_apollo_fvp_linux.py
git commit -s -m "feat(apollo): probe QBox local boot"
```

## Task 6: Document The Apollo QBox Local Boot Flow

**Files:**
- Create: `tools/qbox/platforms/apollo-fvp/README.md`
- Modify: `AGENTS.md`

- [ ] **Step 1: Create Apollo QBox README**

Create `tools/qbox/platforms/apollo-fvp/README.md`:

````markdown
# QBox Apollo FVP Primary Compute

This platform boots the Apollo FVP primary-compute Linux image directly on
QBox. It is intended for local-build validation of the Linux kernel,
initramfs, and primary-compute device model wiring.

This is not the full Apollo firmware chain. RSE, TF-A, OP-TEE, and U-Boot are
bypassed by the QBox AArch64 direct-boot stub. Use the RSE-oriented QBox
platform when firmware-chain fidelity is required.

## Build Local Artifacts

```bash
./local-build.sh build
```

The QBox runner consumes:

```text
build/local-apollo-fvp/deploy/boot/Image
build/local-apollo-fvp/deploy/boot/initramfs.cpio.gz
```

The runner generates a direct-boot overlayed DTB at:

```text
build/qbox-apollo-fvp/apollo-fvp-direct.dtb
```

## Build QBox Targets

```bash
./local-build.sh qbox
```

## Headless Boot

```bash
python3 scripts/run/run_qbox_apollo_fvp_linux.py \
  --timeout 600 \
  --post-login-probe
```

The result files are written under:

```text
build/qbox-apollo-fvp/<timestamp>/
```

Inspect:

```text
result.json
summary.txt
qbox-apollo-fvp.log
```

## Interactive Boot

```bash
python3 scripts/run/run_qbox_apollo_fvp_linux.py \
  --skip-build \
  --interactive \
  --timeout "${QBOX_APOLLO_TIMEOUT:-0}" \
  --local-build-dir build/local-apollo-fvp
```

Set `QBOX_APOLLO_TIMEOUT=0` for an unbounded interactive session.
````

- [ ] **Step 2: Add AGENTS pointer**

In `AGENTS.md`, under "QBox helper scripts", add:

```markdown
  `./local-build.sh qbox`,
  `scripts/run/run_qbox_apollo_fvp_linux.py`,
```

Under runtime checks, add:

```markdown
   - For Apollo local-build direct boot on QBox, use
     `python3 scripts/run/run_qbox_apollo_fvp_linux.py --timeout 600
     --post-login-probe` and inspect `build/qbox-apollo-fvp/<timestamp>/`.
```

- [ ] **Step 3: Verify markdown diff**

Run:

```bash
git diff --check -- AGENTS.md tools/qbox/platforms/apollo-fvp/README.md
```

Expected: no output and exit code 0.

- [ ] **Step 4: Commit**

```bash
git add AGENTS.md tools/qbox/platforms/apollo-fvp/README.md
git commit -s -m "docs(apollo): describe QBox local boot"
```

## Task 7: End-To-End Validation

**Files:**
- No source edits expected after this task.
- Generated evidence under `build/qbox-apollo-fvp/<timestamp>/`.

- [ ] **Step 1: Confirm local build artifacts exist**

Run:

```bash
test -f build/local-apollo-fvp/deploy/boot/Image
test -f build/local-apollo-fvp/deploy/boot/initramfs.cpio.gz
```

Expected: both commands exit 0. If either file is missing, run:

```bash
./local-build.sh build
```

- [ ] **Step 2: Build QBox Apollo targets and DTB**

Run:

```bash
./local-build.sh qbox
```

Expected: command exits 0 and prints:

```text
build/qbox-apollo-fvp/apollo-fvp-direct.dtb
```

- [ ] **Step 3: Run headless QBox boot**

Run:

```bash
python3 scripts/run/run_qbox_apollo_fvp_linux.py \
  --skip-build \
  --timeout 600 \
  --post-login-probe
```

Expected: command exits 0 and prints the output directory plus `summary.txt`
and `result.json` paths.

- [ ] **Step 4: Inspect result JSON**

Run:

```bash
export latest="$(find build/qbox-apollo-fvp -mindepth 1 -maxdepth 1 -type d | sort | tail -n 1)"
python3 - <<'PY'
import json
from pathlib import Path
latest = Path(__import__("os").environ["latest"])
result = json.loads((latest / "result.json").read_text())
assert result["passed"] is True
assert result["probe_complete"] is True
print(result["log_path"])
PY
```

Expected: prints the `qbox-apollo-fvp.log` path and exits 0.

- [ ] **Step 5: Check log evidence**

Run:

```bash
rg -n "Booting Linux on physical CPU|apollo-fvp login:|__QBOX_APOLLO_PROBE_DONE__|Kernel panic|Unable to mount root fs|No working init found" \
  "${latest}/qbox-apollo-fvp.log"
```

Expected:

- `Booting Linux on physical CPU` appears.
- `apollo-fvp login:` appears.
- `__QBOX_APOLLO_PROBE_DONE__` appears.
- The three failure strings do not appear.

- [ ] **Step 6: Run static checks**

Run:

```bash
python3 -m py_compile scripts/run/run_qbox_apollo_fvp_linux.py
pytest tests/test_run_qbox_apollo_fvp_linux.py -q
bash -n ./local-build.sh
git diff --check
```

Expected: all commands exit 0.

- [ ] **Step 7: Commit validation-only docs if needed**

If validation reveals a stable known limitation, add it to
`tools/qbox/platforms/apollo-fvp/README.md` and commit:

```bash
git add tools/qbox/platforms/apollo-fvp/README.md
git commit -s -m "docs(apollo): record QBox boot evidence"
```

If validation passes with no documentation changes, do not create a commit.

## Task 8: Optional Full Firmware-Chain Follow-Up

**Files:**
- No changes in the direct-boot implementation branch unless the user approves
  a separate full-chain scope.

- [ ] **Step 1: Confirm direct boot scope is accepted**

Use the direct-boot evidence from Task 7 as the baseline. Do not mix full
firmware-chain work into the direct-boot commits.

- [ ] **Step 2: Draft a separate plan if full chain is required**

The separate plan should target:

- RSE ROM/OTP/flash images from `build/local-apollo-fvp/deploy/firmware/`
- AP flash image from `build/local-apollo-fvp/deploy/firmware/ap-flash-image.img`
- TF-A BL2/FIP, OP-TEE, U-Boot, and Linux handoff through modeled reset
- Existing RSE-oriented QBox helpers and per-domain UART logs

Acceptance for that separate plan must include RSE, Safety Island, TF-A,
U-Boot, and Linux domain markers, not just primary-compute Linux login.

## Self-Review

- Spec coverage: The plan covers local-build artifacts, QBox runner changes,
  Lua initramfs loading, DTB boot metadata, wrapper scripts, documentation, and
  end-to-end validation.
- Placeholder scan: no incomplete placeholder markers remain.
- Type consistency: The plan consistently uses `LocalBuildArtifacts`,
  `initramfs_range()`, `fdt_patch_commands()`, and existing
  `qbox_env()`/`compile_dtb()` names.
- Scope: Full firmware-chain boot is explicitly separated from the direct
  primary-compute Linux boot acceptance target.
