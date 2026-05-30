#
# SPDX-License-Identifier: MIT
#

inherit externalsrc

EXTERNALSRC:pn-linux-yocto:apollo-fvp = "${HSOC_APOLLO_LINUX_SRC}"
EXTERNALSRC_BUILD:pn-linux-yocto:apollo-fvp = "${WORKDIR}/build"
EXTERNALSRC:pn-linux-yocto-rt:apollo-fvp = "${HSOC_APOLLO_LINUX_SRC}"
EXTERNALSRC_BUILD:pn-linux-yocto-rt:apollo-fvp = "${WORKDIR}/build"

# Apollo FVP reuses RD-Aspen kernel metadata until Apollo-specific
# kernel fragments are added.
KMACHINE:pn-linux-yocto:apollo-fvp = "fvp-rd-aspen"
KMACHINE:pn-linux-yocto-rt:apollo-fvp = "fvp-rd-aspen"

do_shared_workdir:append:apollo-fvp() {
    if [ "${MODSIGN_ENABLED}" = "1" ]; then
        if [ ! -f "${B}/modsign_key.pem" ]; then
            bbfatal "modsign is enabled, but ${B}/modsign_key.pem is missing"
        fi
        install -m 0600 "${B}/modsign_key.pem" \
            "${STAGING_KERNEL_BUILDDIR}/modsign_key.pem"
    fi
}
