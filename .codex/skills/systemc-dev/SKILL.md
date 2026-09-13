---
name: systemc-dev
description: Implement or debug Apollo SystemC/TLM component timing, reset, transport and payload lifetime.
---

# SystemC models

Reusable models belong in `hsoc-stack/tools/qbox`; Apollo-specific models in
`hsoc-stack/tools/qbox-platform`. Follow nearby C++14, CCI and socket patterns.

Inspect the affected process, binding and caller before changing behavior.
Preserve simulation-time/delta-cycle ordering; SC_METHOD cannot block.
Keep payloads/extensions alive through transport, set response status, and account
for annotated delay. Check DMI ranges and invalidation when applicable.
Reset must cancel or reconcile outstanding activity.

Use an existing focused component test to demonstrate the changed behavior.
For platform wiring or Linux-visible changes, add the relevant guest validation.
Provider compile: `./yocto_build.sh qbox-apollo-qvp-native -c compile`.
Select tests through recipe `do_check` and its QBOX_CORE_TEST_REGEX/
QBOX_CORE_TEST_DIRS controls; do not automatically rebuild the full image.
