/*
 * SPDX-FileCopyrightText: <text>Copyright 2026 Arm Limited and/or its
 * affiliates <open-source-office@arm.com></text>
 *
 * SPDX-License-Identifier: Apache-2.0
 */

#include <errno.h>
#include <inttypes.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#include <zephyr/shell/shell.h>
#include <zephyr/shell/shell_string_conv.h>

#include <zephyr/drivers/pfdi/pfdi.h>

#include "pfdi_mgmt_priv.h"

static int parse_u32(const struct shell *sh, const char *s, uint32_t *out)
{
	int err = 0;

	if (!sh || !s || !out) {
		if (sh) {
			shell_error(sh, "internal error: null argument");
		}
		return -EINVAL;
	}

	*out = (uint32_t)shell_strtoul(s, 0, &err);

	if (err != 0) {
		shell_error(sh, "invalid number: '%s' (err=%d)", s, err);
		return -EINVAL;
	}

	return 0;
}

static int parse_i32(const struct shell *sh, const char *s, int32_t *out)
{
	int err = 0;

	if (!sh || !s || !out) {
		shell_error(sh, "internal error: null argument");
		return -EINVAL;
	}

	*out = (int32_t)shell_strtol(s, 0, &err);
	if (err != 0) {
		shell_error(sh, "invalid number: '%s' (err=%d)", s, err);
		return -EINVAL;
	}

	return 0;
}

static int parse_cpu_checked(const struct shell *sh, const char *s, uint32_t *cpu_out)
{
	int r;
	int ncpus;

	r = parse_u32(sh, s, cpu_out);
	if (r) {
		return r;
	}

	ncpus = pfdi_num_cpus();
	if (ncpus <= 0) {
		shell_error(sh, "pfdi: invalid cpu count (%d)", ncpus);
		return -EIO;
	}

	if (*cpu_out >= (uint32_t)ncpus) {
		shell_error(sh, "cpu out of range: %u (valid range: 0..%d)", *cpu_out, ncpus - 1);
		return -ERANGE;
	}

	return 0;
}

#if defined(CONFIG_PFDI_MGMT_DEBUG)
static int parse_bool01(const struct shell *sh, const char *s, bool *out)
{
	uint32_t value;
	int ret = parse_u32(sh, s, &value);

	if (ret) {
		return ret;
	}

	if (value > 1U) {
		shell_error(sh, "value must be 0 or 1 (got: %u)", value);
		return -EINVAL;
	}

	*out = (value != 0U);

	return 0;
}
#endif

static int report_mgmt_err(const struct shell *sh, const char *op, uint32_t cpu, int err)
{
	if (err == 0) {
		return 0;
	}

	shell_error(sh, "pfdi: %s failed (cpu%u, err=%d)", op, cpu, err);

	return err;
}

static int cmd_pfdi_status(const struct shell *sh, size_t argc, char **argv)
{
	int ret;
	uint32_t cpu;
	bool running;
	uint32_t period_ms;

	if (argc != 2) {
		shell_error(sh, "usage: pfdi get-status <cpu>");
		return -EINVAL;
	}

	ret = parse_cpu_checked(sh, argv[1], &cpu);
	if (ret) {
		return ret;
	}

	ret = pfdi_mgmt_status_cpu(cpu, &running, &period_ms);
	if (ret) {
		return report_mgmt_err(sh, "get-status", cpu, ret);
	}

	if (running) {
		shell_print(sh, "pfdi: cpu%u running (period: %u ms)", cpu, period_ms);
	} else {
		shell_print(sh, "pfdi: cpu%u stopped", cpu);
	}

	return 0;
}

#if CONFIG_PFDI_OOR_ENABLE
static int cmd_pfdi_result(const struct shell *sh, size_t argc, char **argv)
{
	uint32_t cpu = 0;
	pfdi_oor_result_t oor;
	const char *status_str;
	int ret;

	if (argc != 2) {
		shell_error(sh, "usage: pfdi result <cpu>");
		return -EINVAL;
	}

	ret = parse_cpu_checked(sh, argv[1], &cpu);
	if (ret) {
		return ret;
	}

	memset(&oor, 0, sizeof(oor));

	ret = pfdi_mgmt_result_cpu(cpu, &oor);
	if (ret < 0) {
		return report_mgmt_err(sh, "result", cpu, ret);
	}

	if ((int)oor.status < 0) {
		shell_print(sh, "pfdi: cpu%u OoR status error(%d)", cpu, (int)oor.status);
		return 0;
	}

	status_str = (oor.stat.failed == true) ? "FAILED" : "SUCCESS";

	shell_print(sh,
		    "pfdi: cpu%u OoR status: %s, success: %" PRIu64 ", skipped: %" PRIu64
		    ", scheduled: %" PRIu64,
		    cpu, status_str, (uint64_t)oor.stat.success, (uint64_t)oor.stat.skipped,
		    (uint64_t)oor.stat.scheduled);

	if (oor.stat.failed == true) {
		shell_print(sh, "pfdi: cpu%u OoR failed block id %" PRIu64 ", part id: %" PRIu64,
			    cpu, (uint64_t)oor.stat.f_blk_id, (uint64_t)oor.stat.f_part_id);
	}

	return 0;
}
#endif /* CONFIG_PFDI_OOR_ENABLE */

static int validate_pfdi_run_args(const struct shell *sh, int32_t blk_id, int32_t start,
				  int32_t end)
{
	/* blk_id must be -1 or >=1 */
	if (blk_id < -1 || blk_id == 0) {
		shell_error(sh, "invalid block id: %d (must be -1 or >= 1)", blk_id);
		return -EINVAL;
	}

	/* Case 1: all tests */
	if (blk_id == -1 && start == -1 && end == -1) {
		return 0;
	}

	/* Case 2: blk_id with all part ids */
	if (blk_id >= 1 && start == -1 && end == -1) {
		return 0;
	}

	/* Case 3: explicit range: require all >=1 and end >= start */
	if (blk_id >= 1 && start >= 1 && end >= 1) {
		if (end >= start) {
			return 0;
		} else {
			shell_error(sh, "invalid range: end (%d) must be >= start (%d)", end,
				    start);
			return -EINVAL;
		}
	}

	shell_error(sh, "invalid argument combination: block id %d, part range %d-%d", blk_id,
		    start, end);
	return -EINVAL;
}

static int cmd_pfdi_run(const struct shell *sh, size_t argc, char **argv)
{
	uint32_t cpu = 0;
	int32_t blk_id = -1, start = -1, end = -1;
	pfdi_run_stats_t stats = {0};
	int ret;

	/* Supported forms:
	 *   pfdi run <cpu>                   -> all tests
	 *   pfdi run <cpu> <blk_id>          -> all parts under Block ID
	 *   pfdi run <cpu> <blk_id> <s> <e>  -> Parts range under Block ID
	 */
	if (argc != 2 && argc != 3 && argc != 5) {
		shell_error(sh, "usage:\n"
				"  pfdi run <cpu>\n"
				"  pfdi run <cpu> <block id>\n"
				"  pfdi run <cpu> <block id> <start_part> <end_part>");
		return -EINVAL;
	}

	ret = parse_cpu_checked(sh, argv[1], &cpu);
	if (ret) {
		return ret;
	}

	if (argc >= 3) {
		ret = parse_i32(sh, argv[2], &blk_id);
		if (ret) {
			return ret;
		}
	}

	if (argc == 5) {
		ret = parse_i32(sh, argv[3], &start);
		if (ret) {
			return ret;
		}
		ret = parse_i32(sh, argv[4], &end);
		if (ret) {
			return ret;
		}
	}

	ret = validate_pfdi_run_args(sh, blk_id, start, end);
	if (ret) {
		return ret;
	}

	ret = pfdi_mgmt_run_cpu(cpu, blk_id, start, end, &stats);
	if (ret < 0) {
		return report_mgmt_err(sh, "run", cpu, ret);
	}

	if (blk_id == -1 && start == -1 && end == -1) {
		shell_print(sh, "pfdi: run completed: cpu%u all blocks (rc=%d)", cpu, ret);
	} else if (blk_id >= 0 && start == -1 && end == -1) {
		shell_print(sh, "pfdi: run completed: cpu%u block id %d all parts (rc=%d)", cpu,
			    blk_id, ret);
	} else {
		shell_print(sh, "pfdi: run completed: cpu%u block id %d  part range: %d->%d rc=%d",
			    cpu, blk_id, start, end, ret);
	}

	shell_print(sh,
		    "pfdi: stats: scheduled: %" PRIu64 ", success: %" PRIu64 ", skipped: %" PRIu64,
		    (uint64_t)stats.scheduled, (uint64_t)stats.success, (uint64_t)stats.skipped);

	if (stats.failed) {
		shell_print(sh, "pfdi: failed block id: %" PRIu64 " part id: %" PRIu64,
			    (uint64_t)stats.f_blk_id, (uint64_t)stats.f_part_id);
	}

	return 0;
}

static int cmd_pfdi_count(const struct shell *sh, size_t argc, char **argv)
{
	uint32_t cpu = 0;
	int32_t blk_id = -1;
	uint64_t blk_cnt = 0;
	uint64_t part_cnt = 0;
	int ret;

	if (argc != 2 && argc != 3) {
		shell_error(sh, "usage: pfdi count <cpu> [block id]");
		return -EINVAL;
	}

	ret = parse_cpu_checked(sh, argv[1], &cpu);
	if (ret) {
		return ret;
	}

	if (argc == 3) {
		ret = parse_i32(sh, argv[2], &blk_id);
		if (ret) {
			return ret;
		}
		if (blk_id < 1) {
			shell_error(sh, "block id must be >= 1");
			return -EINVAL;
		}
	}

	ret = pfdi_mgmt_count_cpu(cpu, blk_id, (blk_id == -1) ? &blk_cnt : NULL,
				  (blk_id >= 1) ? &part_cnt : NULL);
	if (ret) {
		return report_mgmt_err(sh, "count", cpu, ret);
	}

	if (blk_id == -1) {
		shell_print(sh, "pfdi: cpu%u supports %" PRIu64 " blocks", cpu, blk_cnt);
	} else {
		shell_print(sh, "pfdi: cpu%u, block id %d supports %" PRIu64 " parts", cpu, blk_id,
			    part_cnt);
	}

	return 0;
}

static int cmd_pfdi_info(const struct shell *sh, size_t argc, char **argv)
{
	uint32_t cpu = 0;
	pfdi_fw_metadata_fields_t info;
	int ret;

	if (argc != 2) {
		shell_error(sh, "usage: pfdi info <cpu>");
		return -EINVAL;
	}

	ret = parse_cpu_checked(sh, argv[1], &cpu);
	if (ret) {
		return ret;
	}

	memset(&info, 0, sizeof(info));

	ret = pfdi_mgmt_info_cpu(cpu, &info);
	if (ret) {
		return report_mgmt_err(sh, "info", cpu, ret);
	}

	if (info.vendor == 0U && info.impl == 0U && info.major == 0U && info.minor == 0U) {
		shell_print(
			sh,
			"pfdi: cpu%u firmware: stub implementation detected (no vendor library)",
			cpu);
	} else {
		shell_print(sh, "pfdi: cpu%u firmware: vendor=0x%02x impl=0x%02x version=%u.%u",
			    cpu, info.vendor, info.impl, info.major, info.minor);
	}

	return 0;
}

#if defined(CONFIG_PFDI_MGMT_DEBUG)
static int cmd_pfdi_force_error(const struct shell *sh, size_t argc, char **argv)
{
	uint32_t cpu = 0;
	int32_t error_id = 0;
	int ret;

	if (argc != 3) {
		shell_error(sh, "usage: pfdi force-error <cpu> <error_id>");
		return -EINVAL;
	}

	ret = parse_cpu_checked(sh, argv[1], &cpu);
	if (ret) {
		return ret;
	}

	ret = parse_i32(sh, argv[2], &error_id);
	if (ret) {
		return ret;
	}

	ret = pfdi_mgmt_force_error_cpu(cpu, error_id);
	if (ret) {
		return report_mgmt_err(sh, "force-error", cpu, ret);
	}

	shell_print(sh, "pfdi: forced error-id: %d on cpu%u", error_id, cpu);

	return 0;
}

static int cmd_pfdi_state(const struct shell *sh, size_t argc, char **argv)
{
	uint32_t cpu = 0;
	bool enable = false;
	bool current_st = false;
	int ret;

	if (argc != 3) {
		shell_error(sh, "usage: pfdi set-status <cpu> <state(0|1)>");
		return -EINVAL;
	}

	ret = parse_cpu_checked(sh, argv[1], &cpu);
	if (ret) {
		return ret;
	}

	ret = parse_bool01(sh, argv[2], &enable);
	if (ret) {
		return ret;
	}

	ret = pfdi_mgmt_status_cpu(cpu, &current_st, NULL);
	if (ret) {
		return report_mgmt_err(sh, "set-status", cpu, ret);
	}

	if (current_st == enable) {
		shell_print(sh, "pfdi: cpu%u already %s", cpu, enable ? "enabled" : "disabled");
		return 0;
	}

	ret = pfdi_mgmt_state_cpu(cpu, enable);
	if (ret) {
		return report_mgmt_err(sh, "set-status", cpu, ret);
	}

	shell_print(sh, "pfdi: cpu%u periodic %s", cpu, enable ? "enabled" : "disabled");

	return 0;
}
#endif

SHELL_STATIC_SUBCMD_SET_CREATE(
	sub_pfdi,

	SHELL_CMD_ARG(run, NULL,
		      "Execute PFDI tests once.\n"
		      "Optional arguments:\n"
		      "  <blk_id> : Test block ID (1-based)\n"
		      "  <start>  : Start test index (1-based, inclusive)\n"
		      "  <end>    : End test index (inclusive, >= <start>)\n"
		      "Usage:\n"
		      "  pfdi run <cpu>\n"
		      "  pfdi run <cpu> <blk_id>\n"
		      "  pfdi run <cpu> <blk_id> <start> <end>\n",
		      cmd_pfdi_run, 2, 3),

	SHELL_CMD_ARG(info, NULL,
		      "Show firmware meta-data.\n"
		      "Usage:\n"
		      "		 pfdi info <cpu>\n",
		      cmd_pfdi_info, 2, 0),

	SHELL_CMD_ARG(count, NULL,
		      "Query supported blocks or parts.\n"
		      "Optional arguments:\n"
		      "  <blk_id> : Test block ID (1-based)\n"
		      "Usage:\n"
		      "  pfdi count <cpu>\n"
		      "  pfdi count <cpu> <blk_id>\n"
		      "Behavior:\n"
		      "  Without <blk_id> : prints number of supported blocks.\n"
		      "  With <blk_id>    : prints number of parts in the block.\n",
		      cmd_pfdi_count, 2, 1),

#if CONFIG_PFDI_OOR_ENABLE
	SHELL_CMD_ARG(result, NULL,
		      "Show Out-of-Reset (OoR) result.\n"
		      "Usage:\n"
		      "		pfdi result <cpu>\n",
		      cmd_pfdi_result, 2, 0),
#endif

#if CONFIG_PFDI_MGMT_DEBUG
	SHELL_CMD_ARG(force-error, NULL,
		      "Inject a simulated fault.\n"
		      "Usage:\n"
		      "pfdi force-error <cpu> <error_id>\n",
		      cmd_pfdi_force_error, 3, 0),

	SHELL_CMD_ARG(set-status, NULL,
		      "Enable or disable periodic execution.\n"
		      "Usage:\n"
		      " pfdi set-status <cpu> <0|1>\n"
		      "Values:0 = disable, 1 = enable\n",
		      cmd_pfdi_state, 3, 0),
#endif

	SHELL_CMD_ARG(get-status, NULL,
		      "Show periodic execution status.\n"
		      "Usage:\n"
		      "	pfdi get-status <cpu>\n",
		      cmd_pfdi_status, 2, 0),

	SHELL_SUBCMD_SET_END);

SHELL_CMD_REGISTER(pfdi, &sub_pfdi,
		   "Platform Fault Detection Subsystem commands.\n"
		   "Common argument:\n"
		   "  <cpu> : Logical CPU index (0-based)\n"
		   "Block model:\n"
		   "  A block is a logical group of related PFDI test cases.\n"
		   "  Each block contains multiple indexed tests.\n"
		   "  <blk_id> selects the block (1-based).\n"
		   "  <start> and <end> select an inclusive test index range\n"
		   "  within the selected block.\n",
		   NULL);
