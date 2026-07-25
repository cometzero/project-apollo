include $(sort $(wildcard $(BR2_EXTERNAL_APOLLO_BSP_PATH)/package/*/*.mk))

UTIL_LINUX_CONF_OPTS += --without-tinfo

define APOLLO_BSP_FINALIZE
	rm -f $(TARGET_DIR)/etc/ld.so.conf
	rm -rf $(TARGET_DIR)/etc/ld.so.conf.d
	ln -sf busybox $(TARGET_DIR)/bin/mount
	mkdir -p $(TARGET_DIR)/usr/lib
	for library in \
		libblkid.so.1 \
		libfdisk.so.1 \
		libmount.so.1 \
		libsmartcols.so.1 \
		libuuid.so.1; do \
		if test -e $(TARGET_DIR)/lib/$$library; then \
			ln -sf ../../lib/$$library \
				$(TARGET_DIR)/usr/lib/$$library; \
		fi; \
	done
endef
TARGET_FINALIZE_HOOKS += APOLLO_BSP_FINALIZE
