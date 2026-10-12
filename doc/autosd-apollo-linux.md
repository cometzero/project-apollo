# AutoSD on Apollo QBox

AutoSD boots only through `run_qbox_autosd.sh`. The runner uses the complete
RSE/SI/AP firmware chain through `run_qbox_yocto.sh`, the platform U-Boot,
UKIBoot and an A/B UKI. `run_qbox_linux.sh` and `run_qemu_linux.sh` support
product/BSP direct Linux boot only; their former AutoSD/EFI options are removed.

## Prepare and boot

```sh
./yocto_build.sh --keep-conf --bsp
LIBGUESTFS_BACKEND=direct python3 scripts/prepare_autosd.py
./run_qbox_autosd.sh --autosd build/autosd/regular.json \
  --modules-archive build/tmp_baremetal/deploy/images/apollo-qvp/modules-apollo-qvp.tgz
```

Preparation requires `qemu-img` and `guestfish` with a usable libguestfs
appliance. It checks publisher hashes, converts the source disk to raw and
extracts the original AutoSD initramfs and boot arguments into a manifest.
The offline module installation option supports regular ext4 images only.
OSTree images require an already provisioned compatible deployment; do not
apply the regular-image offline installer to them.

The runner adapts the deployed `nexios-bsp-initramfs-a.efi` with the AutoSD
initramfs and arguments, and installs it with UKIBoot into a private disk
copy. `--uki` selects another Yocto UKI. It preserves the source disk.
`--modules-archive` installs matching modules and the PFDI service into the
private regular disk before the first firmware boot. This replaces the old
AP-only staging boot. The deployed kernel and modules must match; AutoSD's original kernel modules
cannot be loaded across kernel ABIs.

The BSP build deploys `ukibootaa64.efi`, `slot_a.addon.efi` and
`slot_b.addon.efi` through the `ukiboot` recipe. The separate
`u-boot-apollo-qemu` recipe has been removed: the full-system platform U-Boot
provides EFI services. `ukiboot` remains a BSP build dependency so the
existing AutoSD preparation command continues to work.

Use `--headless` for foreground operation or `--no-attach` to create the tmux
session without attaching. Outputs live under `build/qbox-apollo-qvp/`.
The [dashboard guide](autosd-dashboard-guide-ko.md) describes the UI.

## Evidence boundary

This launcher runs the full firmware chain, but a successful boot alone does
not qualify Secure Boot, OTA, safety functions or hardware timing. Use the
specific validation results for each feature.

[Historical AP-only evidence](autosd-apollo-linux-history.md) records the
removed direct-QEMU/direct-QBox modes; those commands are no longer supported.
