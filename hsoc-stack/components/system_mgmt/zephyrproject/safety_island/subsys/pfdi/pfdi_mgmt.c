/*
 * SPDX-FileCopyrightText: <text>Copyright 2026 Arm Limited and/or its
 * affiliates <open-source-office@arm.com></text>
 *
 * SPDX-License-Identifier: Apache-2.0
 */

#include <zephyr/device.h>
#include <zephyr/init.h>
#include <zephyr/kernel.h>
#include <zephyr/sys/atomic.h>
#include <zephyr/sys/util.h>

#include <zephyr/logging/log.h>
LOG_MODULE_REGISTER(pfdi_mgmt, CONFIG_PFDI_MGMT_LOG_LEVEL);

#include <zephyr/drivers/pfdi/pfdi.h>

#ifdef CONFIG_SMP
#include <zephyr/arch/cpu.h>
#endif

#include <errno.h>
#include <inttypes.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>

#include "pfdi_mgmt_priv.h"

#define MAX_PFDI_CPUS CONFIG_MP_MAX_NUM_CPUS

#define PERIOD_MS CONFIG_PFDI_MGMT_PERIOD_MS

#ifdef K_LOWEST_APPLICATION_THREAD_PRIO
#define PFDI_THREAD_PRIO K_LOWEST_APPLICATION_THREAD_PRIO
#else
#define PFDI_THREAD_PRIO 10
#endif

#define PFDI_SUBMIT_TIMEOUT_MS 10
#define PFDI_QUEUE_TIMEOUT_MS  10
#define PFDI_WORK_TIMEOUT_MS   500

enum pfdi_operation {
	PFDI_OP_NONE = 0,
	PFDI_OP_RUN,
	PFDI_OP_COUNT,
#if CONFIG_PFDI_OOR_ENABLE
	PFDI_OP_RESULT,
#endif /* CONFIG_PFDI_OOR_ENABLE */
	PFDI_OP_INFO,
	PFDI_OP_STATUS_GET,
#if CONFIG_PFDI_MGMT_DEBUG
	PFDI_OP_STATUS_SET,
	PFDI_OP_FORCE_ERROR,
#endif /* CONFIG_PFDI_MGMT_DEBUG */
};

struct pfdi_cpu_state {
	atomic_t periodic_enabled;
};

struct pfdi_request {
	enum pfdi_operation op;
	union {
		pfdi_run_params_t run;
		struct {
			int32_t blk_id;
		} count;
#if CONFIG_PFDI_MGMT_DEBUG
		struct {
			bool enable;
		} state;
		struct {
			int32_t error_id;
		} ferr;
#endif /* CONFIG_PFDI_MGMT_DEBUG */
	} args;
};

struct pfdi_response {
	int rc;
	uint64_t count_blk;
	uint64_t count_part;
#if CONFIG_PFDI_OOR_ENABLE
	pfdi_oor_result_t oor;
#endif /* CONFIG_PFDI_OOR_ENABLE */
	pfdi_fw_metadata_fields_t info;
	bool running;
	pfdi_run_stats_t run_stats;
};

struct pfdi_work_item {
	struct pfdi_request req;
	struct pfdi_response *resp;
	struct k_sem *done;
};

static struct k_thread worker_threads[MAX_PFDI_CPUS];
K_THREAD_STACK_ARRAY_DEFINE(worker_stacks, MAX_PFDI_CPUS, CONFIG_PFDI_MGMT_THREAD_STACK_SIZE);

#ifdef CONFIG_THREAD_MAX_NAME_LEN
#define PFDI_THREAD_NAME_LEN CONFIG_THREAD_MAX_NAME_LEN
#else
#define PFDI_THREAD_NAME_LEN 16
#endif
static char worker_thread_names[MAX_PFDI_CPUS][PFDI_THREAD_NAME_LEN];
static struct k_mutex submit_lock[MAX_PFDI_CPUS];
static struct k_msgq worker_msgq[MAX_PFDI_CPUS];
static struct pfdi_work_item worker_msgq_buf[MAX_PFDI_CPUS][1];
static struct pfdi_cpu_state cpu_states[MAX_PFDI_CPUS];
#if CONFIG_PFDI_MGMT_DEBUG
static atomic_t forced_error_id[MAX_PFDI_CPUS];
#endif /* CONFIG_PFDI_MGMT_DEBUG */

static const char *pfdi_op_name(enum pfdi_operation op)
{
	switch (op) {
	case PFDI_OP_NONE:
		return "NONE";
	case PFDI_OP_RUN:
		return "RUN";
	case PFDI_OP_COUNT:
		return "COUNT";
#if CONFIG_PFDI_OOR_ENABLE
	case PFDI_OP_RESULT:
		return "RESULT";
#endif /* CONFIG_PFDI_OOR_ENABLE */
	case PFDI_OP_INFO:
		return "INFO";
	case PFDI_OP_STATUS_GET:
		return "STATUS_GET";
#if CONFIG_PFDI_MGMT_DEBUG
	case PFDI_OP_STATUS_SET:
		return "STATUS_SET";
	case PFDI_OP_FORCE_ERROR:
		return "FORCE_ERROR";
#endif /* CONFIG_PFDI_MGMT_DEBUG */
	default:
		return "UNKNOWN";
	}
}

static inline int pfdi_effective_cpus(void)
{
#if defined(CONFIG_SMP) && defined(CONFIG_SCHED_CPU_MASK)
	int num = arch_num_cpus();

	if (num <= 0) {
		num = 1;
	}
	if (num > (int)MAX_PFDI_CPUS) {
		num = (int)MAX_PFDI_CPUS;
	}
	return num;
#else
	/*
	 * No SMP or no CPU pinning support:
	 * Use a single worker so "cpu index" unambiguously maps to one
	 * execution context.
	 */
	return 1;
#endif
}

static inline unsigned int current_cpu_id(void)
{
#ifdef CONFIG_SMP
	return (unsigned int)arch_curr_cpu()->id;
#else
	return 0U;
#endif
}

static inline bool cpu_index_valid(int cpu_index)
{
	const int cpu_count = pfdi_effective_cpus();

	return (cpu_index >= 0) && (cpu_index < cpu_count);
}

static void fill_fw_info(pfdi_fw_metadata_fields_t *info)
{
	pfdi_fw_metadata_fields_t md;

	if (!info) {
		return;
	}

	memset(info, 0, sizeof(*info));

	if (!pfdi_fw_metadata_unpack(&md)) {
		LOG_WRN("Invalid firmware metadata");
		return;
	}

	info->vendor = md.vendor;
	info->impl = md.impl;
	info->major = md.major;
	info->minor = md.minor;
}

static void pfdi_worker(void *cpu_arg, void *unused2, void *unused3)
{
	ARG_UNUSED(unused2);
	ARG_UNUSED(unused3);

	const int cpu_index = (int)(intptr_t)cpu_arg;
	const int cpu_count = pfdi_effective_cpus();

	if (cpu_index < 0 || cpu_index >= cpu_count) {
		LOG_ERR("Invalid cpu_index=%d (cpu_count=%d)", cpu_index, cpu_count);
		return;
	}

#ifdef CONFIG_SMP
	const unsigned int observed_cpu = current_cpu_id();
#endif

#if defined(CONFIG_SMP) && defined(CONFIG_SCHED_CPU_MASK)
	if ((int)observed_cpu != cpu_index) {
		LOG_ERR("worker%d started on CPU%u (expected CPU%d) - pinning failed; aborting "
			"worker",
			cpu_index, observed_cpu, cpu_index);
		__ASSERT((int)observed_cpu == cpu_index,
			 "pfdi worker started on wrong CPU (pinning failed)");
		return;
	}
#endif

#if defined(CONFIG_SMP)
	LOG_DBG("worker%d started on CPU%u period=%dms\n", cpu_index, observed_cpu, (int)PERIOD_MS);
#else
	LOG_DBG("worker%d started period=%dms\n", cpu_index, (int)PERIOD_MS);
#endif

	for (;;) {
		const bool periodic = (atomic_get(&cpu_states[cpu_index].periodic_enabled) != 0);
		const k_timeout_t to = periodic ? K_MSEC(PERIOD_MS) : K_FOREVER;

		struct pfdi_work_item item;
		const int rc = k_msgq_get(&worker_msgq[cpu_index], &item, to);

		if (rc != 0) {
			if (periodic) {
				pfdi_run_stats_t stats = {0};
				pfdi_run_params_t params = {.blk_id = -1, .start = -1, .end = -1};
				(void)pfdi_run(NULL, &params, &stats);
			}
			continue;
		}

		if (item.resp == NULL || item.done == NULL) {
			LOG_ERR("worker%d: invalid msg (resp=%p done=%p op=%d)", cpu_index,
				item.resp, item.done, (int)item.req.op);
			continue;
		}

#if defined(CONFIG_SMP) && defined(CONFIG_SCHED_CPU_MASK)
		/*
		 * Hard requirement: execute requests on the selected CPU.
		 * Check any unexpected migration or scheduler/arch issues
		 */
		const unsigned int now_cpu = current_cpu_id();

		if ((int)now_cpu != cpu_index) {
			LOG_ERR("worker%d migrated to CPU%u (expected CPU%d) - aborting worker",
				cpu_index, now_cpu, cpu_index);
			item.resp->rc = -EIO;
			k_sem_give(item.done);
			return;
		}
#endif

#if CONFIG_PFDI_MGMT_DEBUG
		if (item.req.op != PFDI_OP_FORCE_ERROR) {
			const int injected = (int)atomic_set(&forced_error_id[cpu_index], 0);

			if (injected != 0) {
				item.resp->rc = injected;
				k_sem_give(item.done);
				continue;
			}
		}
#endif /* CONFIG_PFDI_MGMT_DEBUG */

		LOG_DBG("worker%d request %s", cpu_index, pfdi_op_name(item.req.op));

		memset(item.resp, 0, sizeof(*item.resp));

		switch (item.req.op) {
		case PFDI_OP_RUN: {
			pfdi_run_stats_t stats = {0};
			pfdi_run_params_t params = {
				.blk_id = item.req.args.run.blk_id,
				.start = item.req.args.run.start,
				.end = item.req.args.run.end,
			};
			const pfdi_status_t st = pfdi_run(NULL, &params, &stats);

			item.resp->rc = (int)st;
			item.resp->run_stats = stats;
			break;
		}
		case PFDI_OP_COUNT: {
			int32_t blk = item.req.args.count.blk_id;
			uint64_t out_blk = 0;
			uint64_t out_part = 0;

			const pfdi_status_t st =
				pfdi_count((int64_t)blk, &out_blk, (blk >= 0) ? &out_part : NULL);

			item.resp->count_blk = out_blk;
			item.resp->count_part = out_part;
			item.resp->rc = (int)st;
			break;
		}
#if CONFIG_PFDI_OOR_ENABLE
		case PFDI_OP_RESULT: {
			pfdi_oor_result_t oor = {0};
			const pfdi_status_t st = pfdi_result(&oor);

			item.resp->oor = oor;
			item.resp->rc = (int)st;
			break;
		}
#endif /* CONFIG_PFDI_OOR_ENABLE */
		case PFDI_OP_INFO: {
			fill_fw_info(&item.resp->info);
			item.resp->rc = 0;
			break;
		}
		case PFDI_OP_STATUS_GET: {

			item.resp->running =
				(atomic_get(&cpu_states[cpu_index].periodic_enabled) != 0);
			item.resp->rc = 0;
			break;
		}
#if CONFIG_PFDI_MGMT_DEBUG
		case PFDI_OP_STATUS_SET: {
			atomic_set(&cpu_states[cpu_index].periodic_enabled,
				   item.req.args.state.enable ? 1 : 0);
			item.resp->rc = 0;
			break;
		}
		case PFDI_OP_FORCE_ERROR: {
			atomic_set(&forced_error_id[cpu_index],
				   (atomic_val_t)item.req.args.ferr.error_id);
			item.resp->rc = 0;
			break;
		}
#endif /* CONFIG_PFDI_MGMT_DEBUG */
		case PFDI_OP_NONE:
		default:
			item.resp->rc = -EINVAL;
			break;
		}

		k_sem_give(item.done);
	}
}

static int submit_request_to_cpu(int cpu_index, const struct pfdi_request *request,
				 struct pfdi_response *out_response)
{
	struct k_sem done;
	int rc;

	if (!cpu_index_valid(cpu_index) || !request || !out_response) {
		return -EINVAL;
	}

	rc = k_mutex_lock(&submit_lock[cpu_index], K_MSEC(PFDI_SUBMIT_TIMEOUT_MS));
	if (rc != 0) {
		LOG_WRN("Submit: cpu%d lock timeout (busy)", cpu_index);
		return -EBUSY;
	}

	k_sem_init(&done, 0, 1);

	struct pfdi_work_item item = {
		.req = *request,
		.resp = out_response,
		.done = &done,
	};

	rc = k_msgq_put(&worker_msgq[cpu_index], &item, K_MSEC(PFDI_QUEUE_TIMEOUT_MS));
	if (rc != 0) {
		LOG_WRN("submit: cpu%d queue full or timeout", cpu_index);
		k_mutex_unlock(&submit_lock[cpu_index]);
		return -ETIMEDOUT;
	}

	rc = k_sem_take(&done, K_MSEC(PFDI_WORK_TIMEOUT_MS));
	k_mutex_unlock(&submit_lock[cpu_index]);

	if (rc != 0) {
		LOG_ERR("submit: cpu%d operation timeout (worker did not respond)", cpu_index);
		return -ETIMEDOUT;
	}

	return 0;
}

int pfdi_num_cpus(void)
{
#if !defined(CONFIG_SMP)
	return 1;
#else
	return pfdi_effective_cpus();
#endif
}

int pfdi_mgmt_run_cpu(int cpu, int32_t blk_id, int32_t start, int32_t end,
		      pfdi_run_stats_t *out_stats)
{
	struct pfdi_response resp;
	int submit_rc;

	if (!cpu_index_valid(cpu)) {
		return -ERANGE;
	}

	struct pfdi_request req = {
		.op = PFDI_OP_RUN,
		.args.run =
			{
				.blk_id = blk_id,
				.start = start,
				.end = end,
			},
	};

	submit_rc = submit_request_to_cpu(cpu, &req, &resp);
	if (submit_rc != 0) {
		return submit_rc;
	}

	if (out_stats) {
		*out_stats = resp.run_stats;
	}

	return resp.rc;
}

int pfdi_mgmt_count_cpu(int cpu, int32_t blk_id, uint64_t *out_blk_cnt, uint64_t *out_part_cnt)
{
	struct pfdi_request req = {.op = PFDI_OP_COUNT};
	struct pfdi_response resp;
	int submit_rc;

	if (!cpu_index_valid(cpu)) {
		return -ERANGE;
	}

	req.args.count.blk_id = blk_id;

	submit_rc = submit_request_to_cpu(cpu, &req, &resp);
	if (submit_rc != 0) {
		return submit_rc;
	}

	if (out_blk_cnt) {
		*out_blk_cnt = resp.count_blk;
	}

	if (out_part_cnt) {
		*out_part_cnt = resp.count_part;
	}

	return resp.rc;
}

#if CONFIG_PFDI_OOR_ENABLE
int pfdi_mgmt_result_cpu(int cpu, pfdi_oor_result_t *out)
{
	struct pfdi_request req = {.op = PFDI_OP_RESULT};
	struct pfdi_response resp;
	int submit_rc;

	if (!cpu_index_valid(cpu) || !out) {
		return -EINVAL;
	}

	submit_rc = submit_request_to_cpu(cpu, &req, &resp);
	if (submit_rc != 0) {
		return submit_rc;
	}

	*out = resp.oor;
	return resp.rc;
}
#endif /* CONFIG_PFDI_OOR_ENABLE */

int pfdi_mgmt_info_cpu(int cpu, pfdi_fw_metadata_fields_t *out)
{
	struct pfdi_request req = {.op = PFDI_OP_INFO};
	struct pfdi_response resp;
	int submit_rc;

	if (!cpu_index_valid(cpu) || !out) {
		return -EINVAL;
	}

	submit_rc = submit_request_to_cpu(cpu, &req, &resp);
	if (submit_rc != 0) {
		return submit_rc;
	}

	*out = resp.info;
	return resp.rc;
}

int pfdi_mgmt_status_cpu(int cpu, bool *running, uint32_t *period_ms)
{
	struct pfdi_request req = {.op = PFDI_OP_STATUS_GET};
	struct pfdi_response resp;
	int submit_rc;

	if (!cpu_index_valid(cpu)) {
		return -ERANGE;
	}

	submit_rc = submit_request_to_cpu(cpu, &req, &resp);
	if (submit_rc != 0) {
		return submit_rc;
	}

	if (running) {
		*running = resp.running;
	}

	if (period_ms) {
		*period_ms = PERIOD_MS;
	}

	return resp.rc;
}

#if CONFIG_PFDI_MGMT_DEBUG
int pfdi_mgmt_state_cpu(int cpu, bool enable)
{
	struct pfdi_request req = {.op = PFDI_OP_STATUS_SET};
	struct pfdi_response resp;
	int submit_rc;

	if (!cpu_index_valid(cpu)) {
		return -ERANGE;
	}

	req.args.state.enable = enable;

	submit_rc = submit_request_to_cpu(cpu, &req, &resp);
	return (submit_rc != 0) ? submit_rc : resp.rc;
}

int pfdi_mgmt_force_error_cpu(int cpu, int32_t error_id)
{
	struct pfdi_request req = {.op = PFDI_OP_FORCE_ERROR};
	struct pfdi_response resp;
	int submit_rc;

	if (!cpu_index_valid(cpu)) {
		return -ERANGE;
	}

	req.args.ferr.error_id = error_id;

	submit_rc = submit_request_to_cpu(cpu, &req, &resp);
	return (submit_rc != 0) ? submit_rc : resp.rc;
}
#endif

static int pfdi_service_init(void)
{
	const int cpu_count = pfdi_effective_cpus();

#if !defined(CONFIG_SMP)
	LOG_INF("PFDI mgmt: CONFIG_SMP=n; running single worker (CPU0)");
#endif

	for (int i = 0; i < cpu_count; i++) {
		k_msgq_init(&worker_msgq[i], (char *)worker_msgq_buf[i],
			    sizeof(worker_msgq_buf[i][0]), ARRAY_SIZE(worker_msgq_buf[i]));
		atomic_set(&cpu_states[i].periodic_enabled, 1);
#if CONFIG_PFDI_MGMT_DEBUG
		atomic_set(&forced_error_id[i], 0);
#endif /* CONFIG_PFDI_MGMT_DEBUG */
		k_mutex_init(&submit_lock[i]);

		k_tid_t tid = k_thread_create(&worker_threads[i], worker_stacks[i],
					      K_THREAD_STACK_SIZEOF(worker_stacks[i]), pfdi_worker,
					      (void *)(intptr_t)i, NULL, NULL, PFDI_THREAD_PRIO, 0,
					      K_FOREVER);

		snprintk(worker_thread_names[i], sizeof(worker_thread_names[i]), "pfdi_m%d", i);
		k_thread_name_set(tid, worker_thread_names[i]);

#if defined(CONFIG_SMP) && defined(CONFIG_SCHED_CPU_MASK)
		k_thread_cpu_mask_clear(tid);
		k_thread_cpu_mask_enable(tid, i);
#endif
		k_thread_start(tid);
	}

	LOG_INF("PFDI service ready (%d CPU%s)", cpu_count, (cpu_count == 1 ? "" : "s"));
	return 0;
}

SYS_INIT(pfdi_service_init, APPLICATION, CONFIG_PFDI_MGMT_INIT_PRIORITY);
