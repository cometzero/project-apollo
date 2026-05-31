#
# SPDX-License-Identifier: MIT
#

# Apollo FVP reuses the RD-Aspen Safety Island Zephyr board until
# Apollo-specific Safety Island board metadata is introduced.
ZEPHYR_BOARD:apollo-fvp = "fvp_rd_aspen_safety_island_c1"

inherit externalsrc

EXTERNALSRC:pn-zephyr-demos-cl1:apollo-fvp = "${HSOC_APOLLO_ZEPHYRPROJECT_SRC}"
EXTERNALSRC_BUILD:pn-zephyr-demos-cl1:apollo-fvp = "${WORKDIR}/build"
EXTERNALSRC_SYMLINKS:pn-zephyr-demos-cl1:apollo-fvp = ""

# Keep Apollo Safety Island Zephyr sources in the product tree so board,
# driver, and application changes are decoupled from the reference BSP layer.
ZEPHYR_SAFETY_ISLAND_MODULE:apollo-fvp = "${HSOC_APOLLO_SAFETY_ISLAND_ZEPHYR_SRC}"
