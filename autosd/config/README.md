# AutoSD source configuration

`build_autosd.sh` reads `automotive.json` by default and builds
`autosd/customization/automotive.aib.yml`. `--minimal` selects the official
`autosd/sig-docs/demos/minimal_qm/minimal_qm.aib.yml`; the same file can be selected
with `--aib-manifest PATH`. Do not combine these two selection options.

Paths in configuration are relative to the repository root. Generated files
under `build/autosd/` are disposable outputs, not configuration sources.

- `aib_manifest`: source-controlled product policy.
- `builder_reference`: host-native AIB image tag or immutable registry digest.
  Record the resolved digest; use a digest for repeatable input selection.
- `minimal-qm.json`: retained legacy configuration. The new default is Automotive.
- `nightly_build_id`: legacy import input; the source-build path does not need a
  nightly disk image.

Kernel and modules are built by Yocto and repackaged as an ARM64 RPM using
host-native tools. `kernel_input` is `yocto-deploy`; `--deploy-dir` and
`--kernel-artifacts` select matching deployed inputs. Kernel configuration remains
the Linux submodule's `apollo_qvp_defconfig`. PFDI, workload and latency-probe
use AArch64 GCC in a rootless Podman container through qemu-user. The image assembler is the separate host-native
AIB/OSBuild container and still requires the documented rootful Podman access.

Use `--prepare-inputs-only` to prepare containers and downloads, `--build-only`
to build a disk without launching QBox, and the default command for image build
plus QBox readiness and poweroff checks. Full scenario qualification is separate
from readiness. `--rpm-build-dir PATH` selects a Yocto RPM packaging work/cache directory;
reuse requires matching inputs and artifact hashes.

Root and QM use AutoSD's unmodified crun RPM. The regular image contains the
selected kernel, modules, services, RT tools (Automotive profile), and workload
OCI before first boot. The prepared-image launcher validates and copies the
artifact; it does not install packages or replace its UKI/ESP.

See the [full build guide](../../doc/autosd-minimal-qm-build-ko.md),
[migration plan](../../doc/autosd/automotive-rpm-aib-migration-plan-ko.md), and
[current verification report](../../doc/autosd/automotive-source-build-validation-20261105-ko.md).
The report distinguishes implementation/tests from actual image and runtime results.
