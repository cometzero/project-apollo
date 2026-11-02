# AutoSD source configuration

See the [Korean full build and execution guide](../../doc/autosd-minimal-qm-build-ko.md)
for prerequisites, clean builds, cache reuse, intermediate artifacts and logs.

`minimal-qm.json` is the root build entrypoint's source configuration. Paths in
this file are relative to the repository root, not `build/autosd`.

- `aib_manifest`: source-controlled AIB YAML.
- `nightly_build_id`: `null` selects latest on first use; set an official ID to pin.
- `builder_reference`: official AIB tag or SHA256 registry digest. Tags resolve
  once to host-native content digests before downloading layers. Target remains ARM64.
- `customize`: enable Automotive private-guest services and RT tools by default.
  Root gets realtime-tests, rtla, trace-cmd and stress-ng; QM gets stress-ng.
  Both get the static latency probe. QBox readiness checks do not imply
  that all RT experiments or latency thresholds have passed.

Generated cache receipts are not configuration sources. Removing `build/autosd`
requires downloading/building inputs again, but no settings are lost. Upstream
availability and documented host/BSP prerequisites remain necessary.

The build entrypoint uses host-native Podman/AIB/OSBuild with target qemu-user binfmt and
separate native build and ARM64 target pipelines. It requires noninteractive sudo for Podman and output
ownership restoration. Nightly is retained only for the read-only guestfish
appliance smoke test; no builder VM or builder-base image is created.
QBox full-system remains the final customization and boot validation target.
`--rootless` uses rootless Podman and OSBuild `--in-vm image` instead, without sudo.
Builder archives are cached in `builder-amd64/` or `builder-arm64/`; old ARM64
archives are not reused on an x86_64 build host. A target-specific ARM64 digest
must be replaced by a native image digest or a multiarch index reference.
