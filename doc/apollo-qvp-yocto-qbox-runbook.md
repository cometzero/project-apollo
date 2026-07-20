# Apollo QVP Yocto/QBox Runbook

Updated: 2026-07-18

This runbook covers the Apollo QVP Yocto machine and the Yocto-built QBox host
provider. It documents the deploy contract and current blockers. It does not
claim QVP runtime success; that requires QBox runtime logs and `result.json`
evidence from the QVP path.

## Scope

Apollo QVP is a first-class Yocto `MACHINE` with QVP deploy-visible names. The
initial QBox platform still uses transition compatibility names where existing
QBox and RD-Aspen/FVP infrastructure has not been renamed.

Canonical names:

| Item | Name |
| --- | --- |
| Yocto machine | `apollo-qvp` |
| Recommended build directory | `build/` |
| Deploy image root | `build/tmp_baremetal/deploy/images/apollo-qvp` |
| QBox run config | `nexios-image-apollo-qvp.qboxconf` |
| QBox image class | `qboxboot` |
| libqemu native recipe | `qbox-libqemu-native` |
| Apollo QVP QBox provider recipe | `qbox-apollo-qvp-native` |

## Setup

Initialize the shared Apollo build directory:

```bash
export TEMPLATECONF=$PWD/hsoc-stack/yocto/meta-hsoc-auto-solutions/conf/templates/apollo-qvp
source layers/poky/oe-init-build-env build
```

The QVP template sets `MACHINE ??= "apollo-qvp"` and keeps the baremetal
`TMPDIR` layout. The shared `build/conf/local.conf` can also be overridden
with `MACHINE=apollo-qvp bitbake ...` or `./yocto_build.sh --machine
apollo-qvp`. The template keeps BitBake disk monitoring enabled with
`STOPTASKS` thresholds for `${TMPDIR}`, `${DL_DIR}`, `${SSTATE_DIR}`, and
`/tmp`.

Return to the repository root before using the wrapper commands:

```bash
cd "$OLDPWD"
```

## Build

Build the Apollo QVP image from the repository root:

```bash
./yocto_build.sh --machine apollo-qvp
```

Optional dm-verity variants use QVP multiconfig names:

```bash
./yocto_build.sh --machine apollo-qvp --dm-verity=on
./yocto_build.sh --machine apollo-qvp --dm-verity=off
```

The expected deploy image root is:

```text
build/tmp_baremetal/deploy/images/apollo-qvp/
```

Expected QVP deploy-visible image names include:

- `nexios-image-apollo-qvp.*`
- `apollo-qvp.dtb`
- `firmware-apollo-qvp`
- `uefi-capsule-apollo-qvp`
- `efi-capsule-update-disk-image-apollo-qvp.img`

## QBox Native Sysroot/qboxconf

Build the QBox host-side native provider and generate the image `.qboxconf`
from an initialized `build/` BitBake shell:

```bash
MACHINE=apollo-qvp bitbake qbox-libqemu-native -c populate_sysroot
MACHINE=apollo-qvp bitbake qbox-apollo-qvp-native -c populate_sysroot
MACHINE=apollo-qvp bitbake nexios-image -c do_write_qboxboot_conf
```

The canonical QBox run config is:

```text
build/tmp_baremetal/deploy/images/apollo-qvp/nexios-image-apollo-qvp.qboxconf
```

The deploy contract is the generated `.qboxconf` plus the native sysroot
provider. The deploy tree carries the run configuration; host executables,
libraries, modules, and data stay in native sysroot components.

| Field or path | Purpose |
| --- | --- |
| `provider.name` | Native provider recipe, currently `qbox-apollo-qvp-native`. |
| `provider.bindir` | Native sysroot component directory containing `platforms-vp`. |
| `provider.libdir` | Native sysroot component directory containing `libqbox.so` and libqemu libraries. |
| `provider.module_dir` | Native sysroot component directory containing QBox module `.so` files. |
| `provider.data_dir` | Native sysroot component directory containing QBox Lua platform data. |
| `sysroot.components_dir` | Yocto native sysroot components root. |
| `sysroot.recipe_sysroot_native` | Provider recipe native sysroot used by the runner. |
| `exe` | Relative executable path, currently `platforms-vp`. |
| `config` | Relative Lua entrypoint, currently `platforms/apollo/apollo-qvp.lua`. |
| `images` | Deploy image artifact names consumed by the runner. |

## Run

Run Apollo QVP through the Yocto deploy tree, generated `.qboxconf`, and
native sysroot provider:

```bash
./run_qbox_yocto.sh
```

For a file-backed dry run:

```bash
./run_qbox_yocto.sh --headless --dry-run
```

일반 실행은 QBox 시작 전에 deploy artifact 전체를 해시하지 않는다. 동일 초기
상태 FVP/QBox 비교처럼 실행 전 byte identity가 필요한 qualification에서만 다음
옵션을 추가한다.

```bash
./run_qbox_yocto.sh --headless --record-initial-state
```

이 옵션은 `OUT_DIR/initial-state.json`에 RSE/AP flash, OTP, provisioning
bundle, rootfs WIC와 EFI disk의 크기 및 SHA-256을 기록한다. 현재 rootfs WIC는
sparse 파일이어도 논리 크기 전체를 읽으므로 QBox 프로세스 시작 전에 수십 초가
걸릴 수 있다. 자동화에서는 `RUN_QBOX_RECORD_INITIAL_STATE=1`로 같은 동작을
요청할 수 있다.

`run_qbox_yocto.sh`는 기본적으로 다음 위치의 RSE Protected Storage 상태를
재사용한다.

```text
build/qbox-apollo-fvp/state/yocto-apollo-qvp/rse-flash-image.img
```

source RSE flash의 SHA-256 또는 크기가 바뀌더라도 저장소 schema, PS/ITS layout,
RSE OTP identity가 호환되면 새 firmware 영역과 기존 PS/ITS를 자동 병합한다.
`result.json`의 `rse_flash_state.action`은 이 경우 `storage-preserved`다. schema,
layout 또는 OTP identity가 바뀌면 state를 새 이미지에서 다시 생성한다. 구형
sidecar metadata는 compatibility fingerprint가 없으므로 한 번 refresh된다.

명시적으로 초기화하거나 일회성 pristine 상태를 사용할 때는 다음 옵션을 사용한다.

```bash
./run_qbox_yocto.sh --reset-rse-state
./run_qbox_yocto.sh --no-persistent-rse-state
./run_qbox_yocto.sh --rse-state-dir /path/to/state
```

U-Boot의 FWU Regular State까지만 빠르게 검증하려면 Linux/Safety Island 완료
gate를 제외하는 전용 scope를 사용한다.

```bash
./run_qbox_yocto.sh --headless --uboot-only --timeout 90
```

RSE boot flash의 기본 backend는 같은 QEMU CFI01 MemoryRegion을 RSE CPU와 외부
TLM initiator가 공유하는 `qemu-cfi-local`이다. 비교나 rollback이 필요할 때만
runner 뒤에 다음 옵션을 전달한다.

```bash
./run_qbox_yocto.sh --headless --uboot-only -- \
  --rse-flash-backend systemc-strata
```

새 erased PS/ITS의 cold 경로를 검증할 때는 persistent state를 명시적으로
초기화한다.

```bash
./run_qbox_yocto.sh --headless --exit-after-pass --uboot-only \
  --reset-rse-state
```

`result.json`의 `rse_flash_state.action`이 초기화를 나타내는지 확인하고, 다음
reuse 실행에서 PS/ITS before/after hash가 같아야 한다.

local 이미지의 대응 state는
`build/qbox-apollo-fvp/state/local-apollo-qvp/`이며,
`run_qbox_local.sh`도 같은 세 가지 state 옵션과 `--uboot-only`를 제공한다.

The QVP runtime output root should use:

```text
build/qbox-apollo-qvp/
```

Runtime success requires generated QBox evidence, not only a successful build.
Do not report QVP runtime success until `result.json`, `summary.txt`, and the
per-UART logs exist under the QVP runtime output directory.

## Compatibility Aliases

These names are allowed only as transition details:

- `apollo_fvp_full_system`: current QBox aggregate CMake target used by
  `qbox-apollo-qvp-native` through `QBOX_APOLLO_BUILD_TARGET`.
- `apollo-qvp.lua`: canonical QVP Lua entrypoint. A `.qboxconf`-declared
  compatibility Lua path is acceptable only while the config records it.
- `fvp-rd-aspen`: inherited machine override, native machine name, firmware
  recipe include, and existing RD-Aspen QBox environment prefix. QVP runtime
  scripts do not automatically fall back to FVP-named deploy artifacts; use an
  explicit command-line override when a compatibility artifact is intentional.
- `apollo-fvp`: historical source/configuration reference only. QVP deploy
  names must remain `apollo-qvp` or `qbox-apollo-qvp`.

Compatibility aliases must not replace QVP deploy-visible names.

## Blocker Classification

Use these statuses in reports:

| Status | Meaning |
| --- | --- |
| `blocked_disk_space_stoptasks` | BitBake stopped scheduling tasks because the disk monitor action was `STOPTASKS`. Current `df -h /build` evidence shows `/build` at 100% with 713M available, below the configured 1G threshold, and QBox native deploy did not complete. |
| `runtime_blocked_missing_artifacts` | Required QVP image files, `.qboxconf`, native sysroot provider files, or runtime logs are missing. |
| `runtime_unverified` | Build or deploy evidence exists, but no QVP `result.json` and UART logs have been inspected. |
| `compatibility_alias_in_use` | A documented alias such as `apollo_fvp_full_system` or `fvp-rd-aspen` is still present as an implementation detail. |

Current verification notes:

- Build and deploy evidence belongs under the shared `build/` directory.
- Native QBox provider artifacts belong in Yocto sysroot components; deploy
  contains the `.qboxconf` run configuration and image artifacts.
- QVP runtime success still requires generated `result.json`, `summary.txt`,
  and per-UART logs under `build/qbox-apollo-qvp/`.

To refresh the QBox provider and run config directly:

```bash
source layers/poky/oe-init-build-env build
MACHINE=apollo-qvp bitbake qbox-libqemu-native -c populate_sysroot
MACHINE=apollo-qvp bitbake qbox-apollo-qvp-native -c populate_sysroot
MACHINE=apollo-qvp bitbake nexios-image -c do_write_qboxboot_conf
./run_qbox_yocto.sh --headless --dry-run
```

Only run a bounded boot after the image artifacts, `.qboxconf`, native provider
artifacts, and dry-run command are valid.
