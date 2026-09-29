# AutoSD source configuration

See the [Korean full build and execution guide](../../doc/autosd-minimal-qm-build-ko.md)
for prerequisites, clean builds, cache reuse, intermediate artifacts and logs.

`minimal-qm.json` is the root build entrypoint's source configuration. Paths in
this file are relative to the repository root, not `build/autosd`.

- `aib_manifest`: source-controlled AIB YAML.
- `nightly_build_id`: `null` selects latest on first use; set an official ID to pin.
- `builder_reference`: official AIB tag or SHA256 registry digest. Tags resolve
  once to ARM64 content digests before downloading layers.
- `customize`: enable Automotive private-guest services and RT tools by default.
  Root gets realtime-tests, rtla, trace-cmd and stress-ng; QM gets stress-ng.
  Both get the static latency probe. QEMU/QBox readiness checks do not imply
  that all RT experiments or latency thresholds have passed.

Generated cache receipts are not configuration sources. Removing `build/autosd`
requires downloading/building inputs again, but no settings are lost. Upstream
availability and documented host/BSP prerequisites remain necessary.
