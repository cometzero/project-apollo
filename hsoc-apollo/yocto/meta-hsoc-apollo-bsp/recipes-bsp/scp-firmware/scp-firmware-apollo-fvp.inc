#
# SPDX-License-Identifier: MIT
#

inherit externalsrc

EXTERNALSRC:pn-scp-firmware:apollo-fvp = "${HSOC_APOLLO_SCP_FIRMWARE_SRC}"
EXTERNALSRC_BUILD:pn-scp-firmware:apollo-fvp = "${WORKDIR}/build"
EXTERNALSRC_SYMLINKS:pn-scp-firmware:apollo-fvp = ""
