/*
 * SPDX-FileCopyrightText: <text>Copyright 2026 Arm Limited and/or its
 * affiliates <open-source-office@arm.com></text>
 *
 * SPDX-License-Identifier: Apache-2.0
 */

#ifndef PFDI_MGMT_PRIV_H_
#define PFDI_MGMT_PRIV_H_

#include <stdbool.h>
#include <stdint.h>
#include <zephyr/sys/__assert.h>

typedef uint64_t pfdi_fw_metadata_t;

/**
 * @brief Decoded firmware metadata fields
 *
 * Structure containing unpacked firmware identification fields.
 */
typedef struct {
	uint8_t vendor; /**< Vendor ID (8 bits) */
	uint8_t impl;   /**< Implementation ID (4 bits) */
	uint8_t major;  /**< Major version (8 bits) */
	uint8_t minor;  /**< Minor version (8 bits) */
} pfdi_fw_metadata_fields_t;

#ifdef CONFIG_PFDI_MGMT
#ifndef CONFIG_PFDI_FW_METADATA
#error "CONFIG_PFDI_FW_METADATA must be explicitly set (packed metadata) when CONFIG_PFDI_MGMT is enabled."
#endif
#endif

/*
 * Bit layout of CONFIG_PFDI_FW_METADATA (low 32 bits):
 *
 *   [31:24]  Vendor ID      (8 bits)
 *   [23:20]  Reserved       (must be 0)
 *   [19:16]  Implementation (4 bits)
 *   [15:8]   Major version  (8 bits)
 *   [7:0]    Minor version  (8 bits)
 */

#define PFDI_FW_VENDOR_SHIFT 24u
#define PFDI_FW_IMPL_SHIFT   16u
#define PFDI_FW_MAJOR_SHIFT  8u
#define PFDI_FW_MINOR_SHIFT  0u

#define PFDI_FW_VENDOR_MASK   UINT64_C(0x00000000FF000000)
#define PFDI_FW_RESERVED_MASK UINT64_C(0x0000000000F00000)
#define PFDI_FW_IMPL_MASK     UINT64_C(0x00000000000F0000)
#define PFDI_FW_MAJOR_MASK    UINT64_C(0x000000000000FF00)
#define PFDI_FW_MINOR_MASK    UINT64_C(0x00000000000000FF)

/*
|------------------------------------------------------------
|             Vendor ID         |        Vendor Name        |
|-----------------------------------------------------------|
|  1                            | Arm Limited               |
|-----------------------------------------------------------|
|  Others                       | Reserved.                 |
|-----------------------------------------------------------|
 *
 * Vendor ID 0x01 is reserved for Arm. Vendor-specific implementations
 * must use a different non-zero value to avoid conflicts with Arm's
 * firmware.
 */

/**
 * @brief Mask of all allowed bits in firmware metadata
 *
 * Bits outside this mask must be zero.
 */
#define PFDI_FW_ALLOWED_MASK                                                                       \
	((PFDI_FW_VENDOR_MASK) | (PFDI_FW_IMPL_MASK) | (PFDI_FW_MAJOR_MASK) | (PFDI_FW_MINOR_MASK))

BUILD_ASSERT((((uint64_t)CONFIG_PFDI_FW_METADATA) & ~PFDI_FW_ALLOWED_MASK) == 0u,
	     "CONFIG_PFDI_FW_METADATA has invalid bits set (reserved/upper bits must be 0)");
BUILD_ASSERT((((uint64_t)CONFIG_PFDI_FW_METADATA) & PFDI_FW_RESERVED_MASK) == 0u,
	     "CONFIG_PFDI_FW_METADATA reserved bits [23:20] must be 0");

#ifndef CONFIG_PFDI_USE_ARM_FW_LIB
BUILD_ASSERT(((((uint64_t)CONFIG_PFDI_FW_METADATA & PFDI_FW_VENDOR_MASK) >> PFDI_FW_VENDOR_SHIFT) !=
	      0x01u),
	     "Vendor ID 0x01 is reserved for Arm");
#endif

/**
 * @brief Retrieve packed firmware metadata
 *
 * @return Packed firmware metadata word defined by CONFIG_PFDI_FW_METADATA
 */
static inline pfdi_fw_metadata_t pfdi_fw_metadata_get(void)
{
	return (pfdi_fw_metadata_t)CONFIG_PFDI_FW_METADATA;
}

/**
 * @brief Validate firmware metadata word
 *
 * Checks:
 * - Only allowed bits are set
 * - Reserved bits are zero
 * - Vendor ID restrictions are respected
 *
 * @param md Packed firmware metadata word
 *
 * @retval true  Metadata is valid
 * @retval false Metadata is invalid
 */
static inline bool pfdi_fw_metadata_is_valid(pfdi_fw_metadata_t md)
{
	if ((md & ~PFDI_FW_ALLOWED_MASK) != 0u) {
		return false;
	}
	if ((md & PFDI_FW_RESERVED_MASK) != 0u) {
		return false;
	}

#ifndef CONFIG_PFDI_USE_ARM_FW_LIB
	if (((md & PFDI_FW_VENDOR_MASK) >> PFDI_FW_VENDOR_SHIFT) == 0x01u) {
		return false;
	}
#endif
	return true;
}

/**
 * @brief Unpack firmware metadata fields
 *
 * Decodes the packed metadata word into individual fields.
 *
 * @param[out] out Pointer to structure that receives decoded metadata
 *
 * @retval true  Metadata was valid and successfully unpacked
 * @retval false Metadata was invalid or @p out was NULL
 */
static inline bool pfdi_fw_metadata_unpack(pfdi_fw_metadata_fields_t *out)
{
	if (!out) {
		return false;
	}

	const pfdi_fw_metadata_t md = pfdi_fw_metadata_get();
	if (!pfdi_fw_metadata_is_valid(md)) {
		return false;
	}

	out->vendor = (uint8_t)((md & PFDI_FW_VENDOR_MASK) >> PFDI_FW_VENDOR_SHIFT);
	out->impl = (uint8_t)((md & PFDI_FW_IMPL_MASK) >> PFDI_FW_IMPL_SHIFT);
	out->major = (uint8_t)((md & PFDI_FW_MAJOR_MASK) >> PFDI_FW_MAJOR_SHIFT);
	out->minor = (uint8_t)((md & PFDI_FW_MINOR_MASK) >> PFDI_FW_MINOR_SHIFT);

	return true;
}

/*
 * Internal mgmt API prototypes.
 */

/**
 * @brief Number of effective CPUs used by the PFDI subsystem
 *
 * This accounts for SMP and any configured upper bound.
 */
int pfdi_num_cpus(void);

/**
 * @brief Query per-CPU scheduled state
 *
 * @param cpu CPU index
 * @param[out] running true if periodic job is enabled on the CPU, false otherwise
 * @param[out] period_ms pointer to receive the periodic interval in milliseconds (may be NULL)
 *
 * @return 0 on success or negative POSIX err on failure (e.g. -ERANGE)
 */
int pfdi_mgmt_status_cpu(int cpu, bool *running, uint32_t *period_ms);

/**
 * @brief Get the Out-of-Reset result for a CPU
 *
 * @param cpu CPU index
 * @param[out] out pointer to result structure to populate
 *
 * @return 0 on success or negative on failure
 */
#ifdef CONFIG_PFDI_OOR_ENABLE
int pfdi_mgmt_result_cpu(int cpu, pfdi_oor_result_t *out);
#endif /* CONFIG_PFDI_OOR_ENABLE */
/**
 * @brief Request a single/partial run on the specified CPU
 *
 * @param cpu CPU index
 * @param blk_id block id (or -1 for whole-suite)
 * @param start part start id
 * @param end part end id
 * @param out_stats pointer to result structure to populate
 *
 * @return 0 on success or negative error code / provider error
 */
int pfdi_mgmt_run_cpu(int cpu, int32_t blk_id, int32_t start, int32_t end,
		      pfdi_run_stats_t *out_stats);

/**
 * @brief Get count information for a CPU provider
 *
 * @param cpu CPU index
 * @param blk_id same semantics as pfdi_count(): -1 => blocks, >=1 => parts in block
 * @param out_blk_cnt pointer to receive block count (may be NULL unless blk_id == -1)
 * @param out_part_cnt pointer to receive part count (may be NULL unless blk_id >= 1)
 *
 * @return 0 on success or negative error code / provider error
 */
int pfdi_mgmt_count_cpu(int cpu, int32_t blk_id, uint64_t *out_blk_cnt, uint64_t *out_part_cnt);

/**
 * @brief Retrieve decoded firmware metadata for a CPU/provider
 *
 * @param cpu CPU index
 * @param[out] out pointer to decoded metadata fields
 *
 * @return 0 on success or negative on failure
 */
int pfdi_mgmt_info_cpu(int cpu, pfdi_fw_metadata_fields_t *out);

#if defined(CONFIG_PFDI_MGMT_DEBUG)
/**
 * @brief Inject a forced error for the next request on @p cpu
 *
 * @param cpu CPU index
 * @param error_id signed error id to inject (negative values allowed)
 *
 * @return 0 on success or negative on failure
 */

int pfdi_mgmt_force_error_cpu(int cpu, int32_t error_id);

/**
 * @brief Enable/disable periodic scheduled runs on @p cpu
 *
 * @param cpu CPU index
 * @param enable true to enable periodic runs, false to stop them
 *
 * @return 0 on success or negative on failure
 */
int pfdi_mgmt_state_cpu(int cpu, bool enable);
#endif /* CONFIG_PFDI_MGMT_DEBUG */

#endif /* PFDI_MGMT_PRIV_H_ */
