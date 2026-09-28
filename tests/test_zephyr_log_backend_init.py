"""Native regression using Zephyr's actual runtime-filter implementation.

No firmware build or simulator is started. Scheduler order is deterministic:
the negative control delays backend IDs until after shell enable, as the old
code did; both orders use IDs from early log_core_init in the fixed case.
"""
from pathlib import Path
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]
ZEPHYR = ROOT / "hsoc-stack/components/system_mgmt/zephyrproject/zephyr"


def function(source, signature):
    start = source.index(signature)
    opening = source.index("{", start)
    depth = 1
    end = opening + 1
    while depth:
        depth += (source[end] == "{") - (source[end] == "}")
        end += 1
    return source[start:end]


def harness():
    core = (ZEPHYR / "subsys/logging/log_core.c").read_text()
    management = (ZEPHYR / "subsys/logging/log_mgmt.c").read_text()
    boot = function(core, "void log_core_init(void)")
    early = boot[boot.index("{") + 1:boot.index("\tpanic_mode = false;")]
    late = function(core, "static uint32_t z_log_init(")
    assert "log_backend_id_set" in early
    assert "log_backend_id_set" not in late
    assert "log_backend_count_get() < LOG_FILTERS_MAX_BACKENDS" in early
    assert "CONFIG_LOG_FRONTEND_ONLY" in early
    source = r'''
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>
#define IS_ENABLED(x) (x)
#define CONFIG_LOG_RUNTIME_FILTERING 1
#define CONFIG_LOG_MULTIDOMAIN 0
#ifndef CONFIG_LOG_FRONTEND_ONLY
#define CONFIG_LOG_FRONTEND_ONLY 0
#endif
#define LOG_LEVEL_NONE 0
#define LOG_FILTER_AGGR_SLOT_IDX 0
#define LOG_FILTER_FIRST_BACKEND_SLOT_IDX 1
#define LOG_FILTERS_NUM_OF_SLOTS 10
#define LOG_FILTERS_MAX_BACKENDS 9
#define __ASSERT_NO_MSG(x) assert(x)
#define LOG_FILTER_SLOT_GET(p, id) ((*(p) >> (3 * (id))) & 7)
#define LOG_FILTER_SLOT_SET(p, id, value) (*(p) = (*(p) & ~(7u << (3 * (id)))) | ((value) << (3 * (id))))
struct log_backend_control_block { unsigned id, level; bool active; };
struct log_backend { struct log_backend_control_block *cb; };
struct log_link { int unused; };
static struct log_backend_control_block controls[2];
static struct log_backend log_backend_items[2] = {{&controls[0]}, {&controls[1]}};
static struct log_link log_link_items[1];
static unsigned log_backend_count = 2, log_link_count;
static uint32_t filters[4];
#define STRUCT_SECTION_FOREACH(type, item) for (struct type *item = type##_items; item < type##_items + type##_count; ++item)
static struct log_backend *log_backend_get(unsigned n) { return &log_backend_items[n]; }
static unsigned log_backend_count_get(void) { return log_backend_count; }
static void log_backend_id_set(struct log_backend *b, unsigned id) { b->cb->id=id; }
static uint32_t *get_dynamic_filter(unsigned domain, unsigned source) { return &filters[source]; }
static bool z_log_is_local_domain(unsigned domain) { return domain == 0; }
static void z_log_link_set_runtime_level(unsigned domain, unsigned source, unsigned level) {}
static unsigned log_src_cnt_get(unsigned domain) { return 4; }
static void link_filter_set(struct log_link *link, const struct log_backend *b, unsigned level) {}
static void log_backend_activate(const struct log_backend *b, void *ctx) { b->cb->active=true; }
static void z_log_notify_backend_enabled(void) {}
'''
    source += "\nstatic void early_ids(void) {\n" + early + "}\n"
    source += function(management, "static uint32_t max_filter_get(") + "\n"
    source += function(management, "static void set_runtime_filter(") + "\n"
    source += r'''
/* The real filter_set clamps the requested level to compiled level 3. */
static void log_filter_set(const struct log_backend *b, unsigned domain, unsigned source, unsigned level) {
    set_runtime_filter(b->cb->id, domain, source, level < 3 ? level : 3);
}
'''
    source += function(management, "static void backend_filter_set(") + "\n"
    source += function(management, "void log_backend_enable(") + "\n"
    source += r'''
int main(int argc, char **argv) {
    bool old_order = argc > 1;
    if (CONFIG_LOG_FRONTEND_ONLY) {
        early_ids(); assert(controls[0].id == 0 && controls[1].id == 0);
        puts("frontend-only: backend IDs untouched"); return 0;
    }
    for (unsigned logger_first=0; logger_first<2; logger_first++) {
        memset(controls, 0, sizeof(controls));
        for(unsigned i=0;i<4;i++) filters[i]=3; /* aggregate init */
        if (!old_order || logger_first) early_ids();
        log_backend_enable(&log_backend_items[0], NULL, 4);
        if (old_order && !logger_first) early_ids();
        for(unsigned i=0;i<4;i++) {
            if (old_order && !logger_first) {
                assert(filters[i] == 0); /* exact observed failure */
                assert(controls[0].active && controls[0].id == 1);
            } else {
                assert(filters[i] == 0x1b);
                assert(LOG_FILTER_SLOT_GET(&filters[i], 1) >= 3);
            }
        }
        if (!old_order) {
            log_backend_enable(&log_backend_items[1], NULL, 2);
            assert(controls[1].id == 2);
            for(unsigned i=0;i<4;i++) assert(filters[i] == 0x9b);
        }
    }
    puts(old_order ? "negative control: late-ID shell-first filters=0 reproduced" :
                    "early IDs: shell-first and logger-first filters=0x1b PASS");
    return 0;
}
'''
    return source


@pytest.mark.parametrize("frontend_only", [False, True])
def test_source_filter_ordering(tmp_path, frontend_only):
    source = tmp_path / "log-order.c"
    source.write_text(harness())
    binary = tmp_path / "log-order"
    command = ["cc", "-std=c11", "-Wall", "-Werror", "-Wno-unused-function",
               str(source), "-o", str(binary)]
    if frontend_only:
        command.append("-DCONFIG_LOG_FRONTEND_ONLY=1")
    subprocess.run(command, check=True, capture_output=True, text=True)
    fixed = subprocess.run([str(binary)], check=True, capture_output=True, text=True, timeout=5)
    assert ("backend IDs untouched" if frontend_only else "filters=0x1b PASS") in fixed.stdout
    if not frontend_only:
        negative = subprocess.run([str(binary), "late-id"], check=True,
                                  capture_output=True, text=True, timeout=5)
        assert "filters=0 reproduced" in negative.stdout
