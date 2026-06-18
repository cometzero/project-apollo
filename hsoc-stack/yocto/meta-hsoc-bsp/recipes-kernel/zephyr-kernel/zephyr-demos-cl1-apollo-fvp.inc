#
# SPDX-License-Identifier: MIT
#

# Apollo FVP reuses the RD-Aspen Safety Island Zephyr board until
# Apollo-specific Safety Island board metadata is introduced.
ZEPHYR_BOARD:apollo-fvp = "fvp_rd_aspen_safety_island_c1"

python () {
    src_uri = []
    for uri in (d.getVar("SRC_URI") or "").split():
        is_git_dependency = (
            uri.startswith(("git://", "gitsm://")) and
            "destsuffix=git/" in uri and
            "type=" not in uri
        )
        if is_git_dependency:
            uri = f"{uri};type=git-dependency"
        src_uri.append(uri)
    d.setVar("SRC_URI", " ".join(src_uri))
}

inherit externalsrc

EXTERNALSRC:pn-zephyr-demos-cl1:apollo-fvp = "${HSOC_APOLLO_ZEPHYRPROJECT_SRC}"
EXTERNALSRC_BUILD:pn-zephyr-demos-cl1:apollo-fvp = "${WORKDIR}/build"
EXTERNALSRC_SYMLINKS:pn-zephyr-demos-cl1:apollo-fvp = ""

ZEPHYR_SAFETY_ISLAND_MODULE:apollo-fvp = "${HSOC_APOLLO_SAFETY_ISLAND_ZEPHYR_SRC}"
ZEPHYR_SRC_DIR:apollo-fvp = "${ZEPHYR_SAFETY_ISLAND_MODULE}/apps/sample"

python () {
    import os

    source_root = d.getVar("S")
    unpack_root = os.path.join(d.getVar("WORKDIR"), "git")
    safety_island = d.getVar("ZEPHYR_SAFETY_ISLAND_MODULE")
    modules = d.getVar("ZEPHYR_MODULES") or ""
    modules = modules.replace(f"{source_root}/", f"{unpack_root}/")
    modules = modules.replace(os.path.join(unpack_root, "safety_island"), safety_island)
    d.setVar("ZEPHYR_MODULES", modules)
}

do_configure[file-checksums] += "${HSOC_APOLLO_ZEPHYR_SRC}:True"
do_compile[file-checksums] += "${HSOC_APOLLO_ZEPHYR_SRC}:True ${HSOC_APOLLO_SAFETY_ISLAND_ZEPHYR_SRC}:True"
