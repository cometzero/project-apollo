#
# SPDX-License-Identifier: MIT
#

inherit externalsrc

FILESEXTRAPATHS:prepend := "${THISDIR}:"

EXTERNALSRC:pn-linux-yocto:apollo-fvp = "${HSOC_APOLLO_LINUX_SRC}"
EXTERNALSRC_BUILD:pn-linux-yocto:apollo-fvp = "${WORKDIR}/build"
EXTERNALSRC:pn-linux-yocto-rt:apollo-fvp = "${HSOC_APOLLO_LINUX_SRC}"
EXTERNALSRC_BUILD:pn-linux-yocto-rt:apollo-fvp = "${WORKDIR}/build"

SRC_URI:append:apollo-fvp = " file://apollo-kmeta;type=kmeta;name=apollo-kmeta;destsuffix=apollo-kmeta"

KMACHINE:pn-linux-yocto:apollo-fvp = "apollo-fvp"
KMACHINE:pn-linux-yocto-rt:apollo-fvp = "apollo-fvp"
KBUILD_DEFCONFIG:pn-linux-yocto:apollo-fvp = "apollo_fvp_defconfig"
KBUILD_DEFCONFIG:pn-linux-yocto-rt:apollo-fvp = "apollo_fvp_defconfig"
KERNEL_DEVICETREE:apollo-fvp = "arm/apollo-fvp.dtb"

do_shared_workdir:append:apollo-fvp() {
    if [ "${MODSIGN_ENABLED}" = "1" ]; then
        if [ ! -f "${B}/modsign_key.pem" ]; then
            bbfatal "modsign is enabled, but ${B}/modsign_key.pem is missing"
        fi
        install -m 0600 "${B}/modsign_key.pem" \
            "${STAGING_KERNEL_BUILDDIR}/modsign_key.pem"
    fi
}
