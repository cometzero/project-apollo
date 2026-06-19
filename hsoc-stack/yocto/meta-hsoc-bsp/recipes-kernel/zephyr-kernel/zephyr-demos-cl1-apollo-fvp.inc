#
# SPDX-License-Identifier: MIT
#

# Apollo FVP reuses the RD-Aspen Safety Island Zephyr board until
# Apollo-specific Safety Island board metadata is introduced.
ZEPHYR_BOARD:apollo-fvp = "fvp_rd_aspen_safety_island_c1"

ZEPHYR_DEMOS_CL1_APOLLO_GIT_DEPS = "cmsis libmetal open-amp"
ZEPHYR_DEMOS_CL1_APOLLO_MODULE_SUFFIXES = "\
    modules/hal/cmsis \
    modules/hal/libmetal \
    modules/lib/open-amp \
"

python () {
    required_git_deps = set((d.getVar("ZEPHYR_DEMOS_CL1_APOLLO_GIT_DEPS") or "").split())
    src_uri = []
    for uri in (d.getVar("SRC_URI") or "").split():
        is_git_dependency = (
            uri.startswith(("git://", "gitsm://")) and
            "destsuffix=git/" in uri and
            "type=" not in uri
        )
        if uri.startswith(("git://", "gitsm://")) and "destsuffix=git/" in uri:
            name = "default"
            for parm in uri.split(";"):
                if parm.startswith("name="):
                    name = parm.split("=", 1)[1]
                    break
            if name not in required_git_deps:
                continue
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
    unpack_root = os.path.join(d.getVar("UNPACKDIR"), "git")
    safety_island = d.getVar("ZEPHYR_SAFETY_ISLAND_MODULE")
    required_suffixes = tuple(
        os.path.join(unpack_root, suffix)
        for suffix in (d.getVar("ZEPHYR_DEMOS_CL1_APOLLO_MODULE_SUFFIXES") or "").split()
    )
    modules = d.getVar("ZEPHYR_MODULES") or ""
    modules = modules.replace(f"{source_root}/", f"{unpack_root}/")
    modules = modules.replace(os.path.join(unpack_root, "safety_island"), safety_island)

    filtered_modules = []
    for module in modules.split("\\;"):
        module = module.strip()
        if not module:
            continue
        if module == safety_island or module in required_suffixes:
            filtered_modules.append(module)

    d.setVar("ZEPHYR_MODULES", "\\;".join(filtered_modules) + "\\;")
}

do_configure[file-checksums] += "${HSOC_APOLLO_ZEPHYR_SRC}:True"
do_compile[file-checksums] += "${HSOC_APOLLO_ZEPHYR_SRC}:True ${HSOC_APOLLO_SAFETY_ISLAND_ZEPHYR_SRC}:True"
