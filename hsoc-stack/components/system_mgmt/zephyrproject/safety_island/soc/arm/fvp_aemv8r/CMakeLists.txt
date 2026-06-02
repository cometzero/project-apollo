#
# SPDX-FileCopyrightText: <text>Copyright 2026 Arm Limited and/or its
# affiliates <open-source-office@arm.com></text>
#
# SPDX-License-Identifier: Apache-2.0

zephyr_linker_sources(DATA_SECTIONS aarch64/resource_table.ld)
zephyr_library_sources(aarch64/soc.c)
