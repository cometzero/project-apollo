#
# SPDX-License-Identifier: MIT
#

inherit externalsrc

EXTERNALSRC:pn-u-boot:apollo-fvp = "${HSOC_APOLLO_UBOOT_SRC}"
EXTERNALSRC_BUILD:pn-u-boot:apollo-fvp = "${WORKDIR}/build"

do_configure:append() {
    capsule_crt_path="${@__import__('os').path.relpath('${B}/CRT.crt', '${S}')}"

    bbnote "Setting CONFIG_EFI_CAPSULE_CRT_FILE to ${capsule_crt_path}"
    "${S}/scripts/config" --file "${B}/.config" \
        --set-str EFI_CAPSULE_CRT_FILE "${capsule_crt_path}"
}
