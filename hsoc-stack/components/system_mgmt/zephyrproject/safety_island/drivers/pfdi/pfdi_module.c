/*
 * SPDX-FileCopyrightText: <text>Copyright 2026 Arm Limited and/or its
 * affiliates <open-source-office@arm.com></text>
 *
 * SPDX-License-Identifier: Apache-2.0
 */

#include <string.h>

#include <zephyr/device.h>
#include <zephyr/init.h>
#include <zephyr/irq.h>
#include <zephyr/kernel.h>
#include <zephyr/sys/__assert.h>
#include <zephyr/sys/atomic.h>
#include <zephyr/sys/util.h>

#include <zephyr/drivers/pfdi/pfdi.h>

#if IS_ENABLED(CONFIG_SMP)
#include <zephyr/arch/cpu.h>
#endif

#define MAX_PFDI_ITER 255U

static const struct device *prov;

#if CONFIG_PFDI_OOR_ENABLE
static pfdi_oor_result_t pfdi_oor_result[CONFIG_MP_MAX_NUM_CPUS];
static atomic_t pfdi_oor_valid[CONFIG_MP_MAX_NUM_CPUS];
#endif /* CONFIG_PFDI_OOR_ENABLE */

static const struct fault_detection_interface_api pfdi_api = {
	.run = pfdi_lib_run,
	.count = pfdi_lib_count,
};

static inline uint32_t current_cpu_index(void)
{
#if IS_ENABLED(CONFIG_SMP)
	return (uint32_t)arch_curr_cpu()->id;
#else
	return 0U;
#endif
}

static inline const struct fault_detection_interface_api *pfdi_api_get(void)
{
	return (prov != NULL) ? FAULT_DETECTION_INTERFACE_API(prov) : NULL;
}

static inline pfdi_status_t pfdi_cfg_valid(const pfdi_run_configs_t *cfg)
{
	if (!cfg) {
		return PFDI_INVALID_PARAMETERS;
	}

	if (cfg->exec_mode != PFDI_MODE_OLT && cfg->exec_mode != PFDI_MODE_OLE &&
	    cfg->exec_mode != PFDI_MODE_OOR) {
		return PFDI_INVALID_PARAMETERS;
	}

	if (cfg->failsafe_mode != PFDI_FAILSAFE_STOP &&
	    cfg->failsafe_mode != PFDI_FAILSAFE_RETURN) {
		return PFDI_INVALID_PARAMETERS;
	}

	if (cfg->num_iter > MAX_PFDI_ITER) {
		return PFDI_INVALID_PARAMETERS;
	}

	return PFDI_SUCCESS;
}

static inline void config_defaults(pfdi_run_configs_t *cfg)
{
	cfg->exec_mode =
		IS_ENABLED(CONFIG_PFDI_ONL_EVENT_TRIGGERED) ? PFDI_MODE_OLE : PFDI_MODE_OLT;

	cfg->num_iter = IS_ENABLED(CONFIG_PFDI_ONL_EVENT_TRIGGERED) ? CONFIG_PFDI_NUM_ITER : 0U;

	cfg->failsafe_mode =
		IS_ENABLED(CONFIG_PFDI_FAILSAFE_RETURN) ? PFDI_FAILSAFE_RETURN : PFDI_FAILSAFE_STOP;
}

pfdi_status_t pfdi_run(const pfdi_run_configs_t *run_configs, const pfdi_run_params_t *run_params,
		       pfdi_run_stats_t *stats)
{
	pfdi_run_configs_t cfg = {0};
	pfdi_status_t ret = PFDI_UNKNOWN;
	const struct fault_detection_interface_api *func = pfdi_api_get();

	config_defaults(&cfg);
	if (run_configs) {
		cfg = *run_configs;
	}

	if (!func || !func->run) {
		ret = PFDI_NOT_SUPPORTED;
		goto exit;
	}

	ret = pfdi_cfg_valid(&cfg);
	if (ret != PFDI_SUCCESS) {
		goto exit;
	}

	if (!run_params || !stats) {
		ret = PFDI_INVALID_PARAMETERS;
		goto exit;
	}

	if ((run_params->blk_id < -1 || run_params->start < -1 || run_params->end < -1) ||
	    (run_params->blk_id == -1 && !(run_params->start == -1 && run_params->end == -1)) ||
	    ((run_params->start == -1) != (run_params->end == -1)) ||
	    (run_params->start >= 0 && run_params->end >= 0 &&
	     run_params->start > run_params->end)) {
		ret = PFDI_INVALID_PARAMETERS;
		goto exit;
	}

	ret = func->run(&cfg, run_params, stats);

exit:
#if CONFIG_PLAT_PFDI_POST_RUN_HOOK
	pfdi_post_run_hook((uint32_t)current_cpu_index(), (uint64_t)cfg.exec_mode, (int32_t)ret);
#endif

	return ret;
}

pfdi_status_t pfdi_count(int64_t blk_id, uint64_t *out_blk_cnt, uint64_t *out_part_cnt)
{
	const struct fault_detection_interface_api *func = pfdi_api_get();

	if (!func || !func->count) {
		return PFDI_NOT_SUPPORTED;
	}

	if (blk_id < -1 || blk_id == 0) {
		return PFDI_INVALID_PARAMETERS;
	}

	if (blk_id == -1) {
		if (out_blk_cnt == NULL) {
			return PFDI_INVALID_PARAMETERS;
		}
	} else {
		if (out_part_cnt == NULL) {
			return PFDI_INVALID_PARAMETERS;
		}
	}

	return func->count(blk_id, out_blk_cnt, out_part_cnt);
}

#if CONFIG_PFDI_OOR_ENABLE
pfdi_status_t pfdi_result(pfdi_oor_result_t *oor_result)
{
	const uint32_t cpu = current_cpu_index();

	if (!oor_result) {
		return PFDI_INVALID_PARAMETERS;
	}

	if (cpu >= ARRAY_SIZE(pfdi_oor_result)) {
		return PFDI_INVALID_PARAMETERS;
	}

	if (atomic_get(&pfdi_oor_valid[cpu]) == 0) {
		return PFDI_NOT_RUN;
	}

	*oor_result = pfdi_oor_result[cpu];

	return PFDI_SUCCESS;
}

void pfdi_oor(void)
{
	const uint32_t cpu = current_cpu_index();
	pfdi_run_stats_t stats = {0};
	pfdi_status_t st = PFDI_ERROR;

	pfdi_run_configs_t cfg = {
		.exec_mode = PFDI_MODE_OOR,
		.failsafe_mode = IS_ENABLED(CONFIG_PFDI_FAILSAFE_RETURN) ? PFDI_FAILSAFE_RETURN
									 : PFDI_FAILSAFE_STOP,
		.num_iter = 0,
	};

	pfdi_run_params_t params = {
		.blk_id = -1,
		.start = -1,
		.end = -1,
	};

	if (cpu >= ARRAY_SIZE(pfdi_oor_result)) {
		printk("OoR invalid CPU index %u", cpu);
		return;
	}

	atomic_set(&pfdi_oor_valid[cpu], 0);

	st = pfdi_run(&cfg, &params, &stats);

	pfdi_oor_result[cpu].status = st;
	pfdi_oor_result[cpu].stat = stats;

	atomic_set(&pfdi_oor_valid[cpu], 1);

	if (st != PFDI_SUCCESS) {
		printk("OoR failed on CPU %u (status %d)", cpu, (int)st);
		return;
	}

	printk("Out of Reset (OoR) completed on CPU: %u\n", cpu);
}
#endif /* CONFIG_PFDI_OOR_ENABLE */

static int pfdi_dev_init(const struct device *dev)
{
	prov = dev;

	__ASSERT(FAULT_DETECTION_INTERFACE_API(dev) != NULL, "PFDI API missing");

#if CONFIG_PFDI_OOR_ENABLE
	for (size_t i = 0; i < ARRAY_SIZE(pfdi_oor_result); i++) {
		atomic_set(&pfdi_oor_valid[i], 0);
		pfdi_oor_result[i].status = PFDI_NOT_RUN;
		memset(&pfdi_oor_result[i].stat, 0, sizeof(pfdi_oor_result[i].stat));
	}

	/* Running PFDI OOR on the primary core */
	pfdi_oor();
#endif /* CONFIG_PFDI_OOR_ENABLE */

	return 0;
}

DEVICE_DEFINE(pfdi_provider, "PFDI_PROVIDER", pfdi_dev_init, NULL, NULL, NULL, POST_KERNEL,
	      CONFIG_PFDI_INIT_PRIORITY, &pfdi_api);
