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
