################################################################################
#
# apollo-perf
#
################################################################################

APOLLO_PERF_VERSION = 1.0
APOLLO_PERF_SITE = file://$(APOLLO_LINUX_SOURCE_DIR)
APOLLO_PERF_SITE_METHOD = file
APOLLO_PERF_SOURCE = COPYING
APOLLO_PERF_LICENSE = GPL-2.0
APOLLO_PERF_LICENSE_FILES = COPYING
APOLLO_PERF_DEPENDENCIES = \
	elfutils \
	host-bison \
	host-flex \
	host-python3 \
	libcap \
	zlib \
	zstd
APOLLO_PERF_OUTPUT = $(@D)/perf-output

APOLLO_PERF_MAKE_FLAGS = \
	ARCH=$(NORMALIZED_ARCH) \
	CROSS_COMPILE="$(TARGET_CROSS)" \
	DESTDIR=$(TARGET_DIR) \
	HOSTCC="$(HOSTCC) $(HOST_CFLAGS) $(HOST_LDFLAGS)" \
	JOBS=$(PARALLEL_JOBS) \
	NO_GTK2=1 \
	NO_LIBAUDIT=1 \
	NO_LIBBIONIC=1 \
	NO_LIBCRYPTO=1 \
	NO_LIBDEBUGINFOD=1 \
	NO_LIBNUMA=1 \
	NO_LIBPERL=1 \
	NO_LIBPYTHON=1 \
	NO_LIBTRACEEVENT=1 \
	NO_LIBUNWIND=1 \
	NO_LZMA=1 \
	NO_NEWT=1 \
	NO_SHELLCHECK=1 \
	NO_SLANG=1 \
	O=$(APOLLO_PERF_OUTPUT)/ \
	PKG_CONFIG_LIBDIR="$(STAGING_DIR)/usr/lib/pkgconfig" \
	WERROR=0 \
	prefix=/usr

define APOLLO_PERF_EXTRACT_CMDS
	$(INSTALL) -D -m 0644 $(APOLLO_LINUX_SOURCE_DIR)/COPYING \
		$(@D)/COPYING
endef

define APOLLO_PERF_BUILD_CMDS
	mkdir -p $(APOLLO_PERF_OUTPUT)
	PYTHONDONTWRITEBYTECODE=1 \
		$(TARGET_MAKE_ENV) $(MAKE1) $(APOLLO_PERF_MAKE_FLAGS) \
		-C $(APOLLO_LINUX_SOURCE_DIR)/tools/perf
endef

define APOLLO_PERF_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(APOLLO_PERF_OUTPUT)/perf \
		$(TARGET_DIR)/usr/bin/perf
endef

$(eval $(generic-package))
