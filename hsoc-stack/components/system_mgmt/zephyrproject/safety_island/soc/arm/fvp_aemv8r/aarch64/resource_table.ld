/*
 * SPDX-FileCopyrightText: <text>Copyright 2026 Arm Limited and/or its
 * affiliates <open-source-office@arm.com></text>
 *
 * SPDX-License-Identifier: Apache-2.0
 */

SECTION_PROLOGUE(.resource_table,, SUBALIGN(4))
{
	KEEP(*(.resource_table*))
} > RAM
