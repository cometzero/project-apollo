/*
 * SPDX-FileCopyrightText: <text>Copyright 2026 Arm Limited and/or its
 * affiliates <open-source-office@arm.com></text>
 *
 * SPDX-License-Identifier: Apache-2.0
 */

#ifndef PFDI_H_
#define PFDI_H_

#include <stdbool.h>
#include <zephyr/device.h>
#include <zephyr/types.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief PFDI return codes
 */
typedef enum {
	PFDI_TEST_COUNT_ZERO = -7,
	PFDI_UNKNOWN = -6,
	PFDI_NOT_RUN = -5,
	PFDI_ERROR = -4,
	PFDI_FAULT_FOUND = -3,
	PFDI_INVALID_PARAMETERS = -2,
	PFDI_NOT_SUPPORTED = -1,
	PFDI_SUCCESS = 0,
} pfdi_status_t;

/**
 * @brief Execution mode selection
 */
typedef enum {
	PFDI_MODE_OLT = 0, /**< Online test mode */
	PFDI_MODE_OLE = 1, /**< Online event-triggered mode */
	PFDI_MODE_OOR = 2, /**< Out-of-reset mode */
} pfdi_mode_t;

/**
 * @brief Failsafe behavior
 */
typedef enum {
	PFDI_FAILSAFE_STOP = 0,   /**< Stop execution on failure */
	PFDI_FAILSAFE_RETURN = 1, /**< Return failure status */
} pfdi_failsafe_mode_t;

/**
 * @brief PFDI run configuration parameters
 *
 * These parameters control how the PFDI is executed.
 */
typedef struct pfdi_run_configs {
	/* Execution mode */
	pfdi_mode_t exec_mode;
	/* Failsafe behavior */
	pfdi_failsafe_mode_t failsafe_mode;
	/*The number of iterations that must be completed
	 *to test the part
	 */
	uint32_t num_iter;
} pfdi_run_configs_t;

/**
 * @brief PFDI run selection parameters
 *
 * Used to select a subset of tests to execute.
 */
typedef struct pfdi_run_params {
	/* Block ID */
	int64_t blk_id;
	/* Part start ID */
	int64_t start;
	/* Part end ID */
	int64_t end;
} pfdi_run_params_t;

/**
 * @brief Statistics returned by a PFDI run
 */
typedef struct {
	uint64_t scheduled;
	uint64_t success;
	bool failed;
	uint64_t skipped;
	uint64_t f_blk_id;
	uint64_t f_part_id;
} pfdi_run_stats_t;

/**
 * @brief Result of an Out-of-Reset (OoR) execution
 */
#if CONFIG_PFDI_OOR_ENABLE
typedef struct {
	pfdi_status_t status;
	pfdi_run_stats_t stat;
} pfdi_oor_result_t;
#endif /* CONFIG_PFDI_OOR_ENABLE */

/**
 * @brief The API implemented by a fault detection provider
 */
__subsystem struct fault_detection_interface_api {
	/**
	 * @brief Execute PFDI test(s)
	 *
	 * @param run_configs Execution configuration
	 * @param run_params  Test selection parameters
	 * @param stats       Output statistics
	 *
	 * @return PFDI status code
	 */
	pfdi_status_t (*run)(const pfdi_run_configs_t *run_configs,
			     const pfdi_run_params_t *run_params, pfdi_run_stats_t *stats);

	/**
	 * @brief Query block or part counts
	 *
	 * @param blk_id
	 *        -1 to query the number of supported blocks.
	 *        >0 to query the number of supported parts in a specific block.
	 *
	 * @param out_blk_cnt
	 *        Output pointer for block count when @p blk_id == -1.
	 *        Must be non-NULL in that case.
	 *
	 * @param out_part_cnt
	 *        Output pointer for part count when @p blk_id > 0.
	 *        Must be non-NULL in that case.
	 *
	 * @return PFDI_SUCCESS on success, otherwise an error code.
	 */
	pfdi_status_t (*count)(const int64_t blk_id, uint64_t *out_blk_cnt, uint64_t *out_part_cnt);
};

#define FAULT_DETECTION_INTERFACE_API(dev)                                                         \
	((const struct fault_detection_interface_api *const)(dev)->api)

/* Public wrappers exposed by the driver */

/**
 * @brief Execute PFDI test(s)
 *
 * @param run_configs Execution configuration (may be NULL for defaults)
 * @param run_params  Test selection parameters
 * @param stats       Output statistics
 *
 * @return PFDI status code
 */
pfdi_status_t pfdi_run(const pfdi_run_configs_t *run_configs, const pfdi_run_params_t *run_params,
		       pfdi_run_stats_t *stats);

/**
 * @brief Query block or part counts
 *
 * @param blk_id
 *        -1 to query the number of supported blocks.
 *        >0 to query the number of supported parts in a specific block.
 *
 * @param out_blk_cnt
 *        Output pointer for block count when @p blk_id == -1.
 *        Must be non-NULL in that case.
 *
 * @param out_part_cnt
 *        Output pointer for part count when @p blk_id > 0.
 *        Must be non-NULL in that case.
 *
 * @return PFDI_SUCCESS on success, otherwise an error code.
 */
pfdi_status_t pfdi_count(const int64_t blk_id, uint64_t *out_blk_cnt, uint64_t *out_part_cnt);

#if CONFIG_PFDI_OOR_ENABLE
/**
 * @brief Execute Out-of-Reset (OoR) tests on the current CPU
 *
 * Runs the OoR mode and stores the result internally.
 */
void pfdi_oor(void);

/**
 * @brief Retrieve the stored Out-of-Reset (OoR) result for the current CPU
 *
 * Returns the OoR execution result previously produced by @ref pfdi_oor().
 * The result is stored per CPU and must be retrieved from the same CPU
 * that executed the OoR test.
 *
 * @param oor_result Pointer to structure that receives the OoR result
 *
 * @retval PFDI_SUCCESS           OoR result successfully retrieved
 * @retval PFDI_NOT_RUN           OoR has not been executed on this CPU
 * @retval PFDI_INVALID_PARAMETERS If @p oor_result is NULL
 */
pfdi_status_t pfdi_result(pfdi_oor_result_t *oor_result);
#endif /* CONFIG_PFDI_OOR_ENABLE */

/*
 * Backend adapter API used by the driver.
 * Vendor can override these with strong definitions.
 */

/**
 * @brief Vendor-specific run implementation
 */
pfdi_status_t pfdi_lib_run(const pfdi_run_configs_t *run_configs,
			   const pfdi_run_params_t *run_params, pfdi_run_stats_t *stats);

/**
 * @brief Vendor-specific count implementation
 */
pfdi_status_t pfdi_lib_count(const int64_t blk_id, uint64_t *out_blk_cnt, uint64_t *out_part_cnt);

/**
 * @brief Platform hook for PFDI integration
 *
 * This hook is implemented by the platform and can be used to perform
 * any platform-specific handling after a PFDI execution.
 *
 * @param cpu    CPU index
 * @param mode   Execution mode (see @ref pfdi_mode_t)
 * @param result Result status code
 *
 */
#ifdef CONFIG_PLAT_PFDI_POST_RUN_HOOK
void pfdi_post_run_hook(uint32_t cpu, uint64_t mode, int32_t result);
#endif

#ifdef __cplusplus
}
#endif

#endif /* PFDI_H_ */
