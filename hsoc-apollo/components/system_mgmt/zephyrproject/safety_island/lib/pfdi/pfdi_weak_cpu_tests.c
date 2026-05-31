/*
 * SPDX-FileCopyrightText: <text>Copyright 2026 Arm Limited and/or its
 * affiliates <open-source-office@arm.com></text>
 *
 * SPDX-License-Identifier: Apache-2.0
 */

/**
 * @file pfdi_weak_cpu_tests.c
 * @brief Stub implementation of the PFDI backend library
 *
 * This file provides weak default implementations of the PFDI backend
 * functions (pfdi_lib_run(), pfdi_lib_count(), etc.).
 *
 * These implementations are intended for:
 *  - Platform bring-up
 *  - Demonstration
 *  - Unit testing of higher layers (management layer / shell interface)
 *
 * They DO NOT perform any real fault detection.
 * Instead, they fabricate deterministic statistics based on the
 * provided run parameters.
 *
 * Production platforms MUST override these weak symbols by linking
 * against a real fault detection validation library.
 *
 * @warning
 * This stub implementation is for development and testing only and
 * must not be used in safety-critical production builds.
 *
 * Stub model:
 *   - 11 blocks (blk_id 1..11)
 *   - 100 total tests
 *   - distribution:
 *       blk1 = 10 tests
 *       blk2..11 = 9 tests each
 */

#include <stdbool.h>
#include <stdint.h>
#include <string.h>
#include <inttypes.h>

#include <zephyr/sys/util.h>
#include <zephyr/kernel.h>
#include <zephyr/logging/log.h>

#include <zephyr/drivers/pfdi/pfdi.h>

LOG_MODULE_REGISTER(pfdi_stub, CONFIG_PFDI_MGMT_LOG_LEVEL);

#define PFDI_STUB_BLOCK_COUNT 11U
#define PFDI_STUB_TOTAL_TESTS 100U

__weak pfdi_status_t pfdi_lib_run(const pfdi_run_configs_t *run_configs,
				  const pfdi_run_params_t *run_params, pfdi_run_stats_t *stats)
{
	ARG_UNUSED(run_configs);

	uint32_t tests_in_block = 0U;
	uint64_t scheduled_tests = 0U;

	if (!run_params || !stats) {
		LOG_ERR("Invalid parameters");
		return PFDI_INVALID_PARAMETERS;
	}

	memset(stats, 0, sizeof(*stats));

	const int64_t blk_id = run_params->blk_id;
	const int64_t start = run_params->start;
	const int64_t end = run_params->end;

	const bool all_tests = (blk_id == -1 && start == -1 && end == -1);
	const bool block_all_parts = (blk_id >= 1 && start == -1 && end == -1);
	const bool block_range = (blk_id >= 1 && start >= 1 && end >= 1);

	if (blk_id < -1) {
		LOG_ERR("Invalid block id=%" PRId64 " (must be -1 or >=1)", blk_id);
		return PFDI_INVALID_PARAMETERS;
	}

	if (blk_id >= 1 && (uint64_t)blk_id > PFDI_STUB_BLOCK_COUNT) {
		LOG_ERR("Invalid block id=%" PRId64 " (supported: 1..%u)", blk_id,
			PFDI_STUB_BLOCK_COUNT);
		return PFDI_INVALID_PARAMETERS;
	}

	if (!(all_tests || block_all_parts || block_range)) {
		LOG_ERR("Invalid argument combination: blk_id=%" PRId64 " start=%" PRId64
			" end=%" PRId64,
			blk_id, start, end);
		return PFDI_INVALID_PARAMETERS;
	}

	if (blk_id >= 1) {

		const uint32_t block_idx = (uint32_t)blk_id - 1U;

		const uint32_t tests_per_block_base = PFDI_STUB_TOTAL_TESTS / PFDI_STUB_BLOCK_COUNT;

		const uint32_t extra_tests_blocks = PFDI_STUB_TOTAL_TESTS % PFDI_STUB_BLOCK_COUNT;

		tests_in_block =
			tests_per_block_base + ((block_idx < extra_tests_blocks) ? 1U : 0U);
	}

	if (all_tests) {
		scheduled_tests = PFDI_STUB_TOTAL_TESTS;
	} else if (block_all_parts) {
		scheduled_tests = tests_in_block;
	} else {

		if (tests_in_block == 0U) {
			LOG_ERR("Internal: tests_in_block=0 for blk_id=%" PRId64, blk_id);
			return PFDI_INVALID_PARAMETERS;
		}

		if (start > end || start < 1 || end < 1 || (uint64_t)start > tests_in_block ||
		    (uint64_t)end > tests_in_block) {

			LOG_ERR("Invalid part range: start=%" PRId64 " end=%" PRId64
				" (valid for blk_id=%" PRId64 ": 1..%u)",
				start, end, blk_id, tests_in_block);

			return PFDI_INVALID_PARAMETERS;
		}

		scheduled_tests = (uint64_t)(end - start + 1);
	}

	stats->scheduled = scheduled_tests;
	stats->success = scheduled_tests;

	return PFDI_SUCCESS;
}

__weak pfdi_status_t pfdi_lib_count(int64_t blk_id, uint64_t *out_blk_cnt, uint64_t *out_part_cnt)
{
	/* Stub model: 11 blocks (blk_id 1..11), 100 tests distributed */
	if (blk_id == -1) {

		if (!out_blk_cnt) {
			return PFDI_INVALID_PARAMETERS;
		}

		*out_blk_cnt = PFDI_STUB_BLOCK_COUNT;
		return PFDI_SUCCESS;
	}

	if (blk_id < 1 || (uint64_t)blk_id > PFDI_STUB_BLOCK_COUNT) {
		return PFDI_INVALID_PARAMETERS;
	}

	if (!out_part_cnt) {
		return PFDI_INVALID_PARAMETERS;
	}

	const uint32_t block_idx = (uint32_t)blk_id - 1U;

	const uint32_t tests_per_block_base = PFDI_STUB_TOTAL_TESTS / PFDI_STUB_BLOCK_COUNT;

	const uint32_t extra_tests_blocks = PFDI_STUB_TOTAL_TESTS % PFDI_STUB_BLOCK_COUNT;

	const uint32_t tests_in_block =
		tests_per_block_base + ((block_idx < extra_tests_blocks) ? 1U : 0U);

	*out_part_cnt = tests_in_block;

	return PFDI_SUCCESS;
}
