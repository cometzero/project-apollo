#
# SPDX-License-Identifier: MIT
#

inherit externalsrc

EXTERNALSRC:pn-trusted-firmware-a:apollo-fvp = "${HSOC_APOLLO_TFA_SRC}"
EXTERNALSRC_BUILD:pn-trusted-firmware-a:apollo-fvp = "${WORKDIR}/build"

# devtool modify keeps mbedTLS as a fetch dependency while the prepared
# source tree provides the checked-out submodule content.
SRC_URI:remove:pn-trusted-firmware-a:apollo-fvp = "${SRC_URI_MBEDTLS}"
SRC_URI:append:pn-trusted-firmware-a:apollo-fvp = " ${SRC_URI_MBEDTLS};type=git-dependency"
