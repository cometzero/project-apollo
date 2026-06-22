# SPDX-License-Identifier: MIT

SUMMARY = "Auto AD Nexios writable storage mount units"
DESCRIPTION = "Installs rootrw and data mount metadata for the Auto AD Nexios read-only root filesystem profile."
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

SRC_URI = " \
    file://data.mount \
    file://rootrw.mount \
"

S = "${UNPACKDIR}"

inherit features_check systemd

REQUIRED_DISTRO_FEATURES = "systemd"

SYSTEMD_SERVICE:${PN} = "rootrw.mount data.mount"
SYSTEMD_AUTO_ENABLE:${PN} = "enable"

do_install() {
    install -d ${D}/rootrw
    install -d ${D}/data
    install -d ${D}${systemd_system_unitdir}

    install -m 0644 ${UNPACKDIR}/rootrw.mount ${D}${systemd_system_unitdir}/rootrw.mount
    install -m 0644 ${UNPACKDIR}/data.mount ${D}${systemd_system_unitdir}/data.mount
}

FILES:${PN} = " \
    /rootrw \
    /data \
    ${systemd_system_unitdir}/rootrw.mount \
    ${systemd_system_unitdir}/data.mount \
"
