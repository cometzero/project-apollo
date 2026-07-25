################################################################################
#
# apollo-pfdi-bsp
#
################################################################################

APOLLO_PFDI_BSP_VERSION = 1.0
APOLLO_PFDI_BSP_SITE = $(APOLLO_PFDI_BSP_SOURCE_DIR)
APOLLO_PFDI_BSP_SITE_METHOD = local
APOLLO_PFDI_BSP_LICENSE = MIT
APOLLO_PFDI_BSP_LICENSE_FILES = license.rst
APOLLO_PFDI_BSP_CONF_OPTS = -DPFDI_TARGET=Linux

define APOLLO_PFDI_BSP_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 \
		$(@D)/pfdi-demo/pfdi-sample-app/pfdi-sample-app \
		$(TARGET_DIR)/usr/bin/pfdi-sample-app
	$(INSTALL) -D -m 0755 \
		$(@D)/libpfdi/libpfdi.so.1.0 \
		$(TARGET_DIR)/usr/lib/libpfdi.so.1.0
	ln -sf libpfdi.so.1.0 $(TARGET_DIR)/usr/lib/libpfdi.so.1
	ln -sf libpfdi.so.1 $(TARGET_DIR)/usr/lib/libpfdi.so
	$(INSTALL) -D -m 0644 $(APOLLO_PFDI_BSP_CONFIG_PACK) \
		$(TARGET_DIR)/etc/pfdi/pfdi_test_config_0.pack
endef

$(eval $(cmake-package))
