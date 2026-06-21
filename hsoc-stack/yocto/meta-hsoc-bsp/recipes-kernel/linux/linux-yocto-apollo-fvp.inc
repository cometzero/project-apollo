#
# SPDX-License-Identifier: MIT
#

inherit externalsrc

FILESEXTRAPATHS:prepend := "${THISDIR}:"

EXTERNALSRC:pn-linux-yocto:apollo-fvp = "${HSOC_APOLLO_LINUX_SRC}"
EXTERNALSRC_BUILD:pn-linux-yocto:apollo-fvp = "${WORKDIR}/build"
EXTERNALSRC:pn-linux-yocto-rt:apollo-fvp = "${HSOC_APOLLO_LINUX_SRC}"
EXTERNALSRC_BUILD:pn-linux-yocto-rt:apollo-fvp = "${WORKDIR}/build"

SRC_URI:remove:apollo-fvp = "${SRC_URI_EXTRAS_KMETA}"
SRC_URI:remove:apollo-fvp = "file://arm-auto-solutions-kmeta-extra;type=kmeta;name=arm-auto-solutions-kmeta-extra;destsuffix=arm-auto-solutions-kmeta-extra"
SRC_URI:remove:apollo-fvp = "file://apollo-kmeta;type=kmeta;name=apollo-kmeta;destsuffix=apollo-kmeta"
SRC_URI:remove:apollo-fvp = "file://modsign.scc file://modsign.cfg"
SRC_URI:remove:apollo-fvp = "file://extra-configs.cfg"
SRC_URI:remove:apollo-fvp = "file://arm-ffa-transport.cfg"

APOLLO_FVP_KERNEL_FEATURES_REMOVE = "\
    cfg/efi.scc \
    features/arm-mhuv3/arm-mhuv3.scc \
    features/bpf/bpf.scc \
    features/mailbox/mailbox.scc \
    features/remoteproc/remoteproc.scc \
    features/rpmsg-virtio/rpmsg-virtio.scc \
    features/vswitch/vswitch.scc \
    features/xen/xen.scc \
    features/arm-pci-ahci/arm-pci-ahci.scc \
    features/ras/arm-ras-dt.scc \
    features/podman/podman.scc \
    ${KERNEL_CACHE_FEATURES} \
"
KERNEL_FEATURES:remove:apollo-fvp = "${APOLLO_FVP_KERNEL_FEATURES_REMOVE}"

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
