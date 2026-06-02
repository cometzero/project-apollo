/*
 * SPDX-FileCopyrightText: <text>Copyright 2026 Arm Limited and/or its
 * affiliates <open-source-office@arm.com></text>
 *
 * SPDX-License-Identifier: Apache-2.0
 */

#include <stdint.h>
#include <zephyr/kernel.h>
#include <zephyr/arch/cpu.h>

#include <zephyr/drivers/pfdi/pfdi.h>

void soc_per_core_init_hook(void)
{
#if CONFIG_PFDI_OOR_ENABLE
	/* Running PFDI OOR on the primary core is too early */
	if (arch_curr_cpu()->id != 0) {
		pfdi_oor();
	}
#endif
}
