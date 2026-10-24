/* SPDX-License-Identifier: BSD-3-Clause */
#define _GNU_SOURCE
#include <errno.h>
#include <glob.h>
#include <inttypes.h>
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#ifndef POWER_SYSFS_ROOT
#define POWER_SYSFS_ROOT "/sys"
#endif

static void fail(const char *message)
{
    fprintf(stderr, "APOLLO_POWER_PROBE FAIL: %s\n", message);
    exit(1);
}

static long read_number(const char *path)
{
    FILE *file = fopen(path, "r");
    long value;
    char extra;
    if (!file || fscanf(file, "%ld %c", &value, &extra) != 1)
        fail(path);
    if (fclose(file))
        fail(path);
    return value;
}

static void write_text(const char *path, const char *text)
{
    FILE *file = fopen(path, "w");
    if (!file || fputs(text, file) == EOF || fclose(file))
        fail(path);
}

static void child_path(char *path, size_t size, const char *parent,
                       const char *child)
{
    int length = snprintf(path, size, "%s/%s", parent, child);
    if (length < 0 || (size_t)length >= size)
        fail("sysfs path too long");
}

static uint64_t memory_checksum(void)
{
    volatile uint64_t data[4096];
    uint64_t sum = 0;
    for (unsigned i = 0; i < 4096; ++i)
        data[i] = i + 1;
    for (unsigned pass = 0; pass < 2; ++pass)
        for (unsigned i = 0; i < 4096; ++i)
            sum += data[i];
    return sum;
}

int main(int argc, char **argv)
{
    if (argc != 3 || (strcmp(argv[1], "4") && strcmp(argv[1], "16")) ||
        (strcmp(argv[2], "1800000") && strcmp(argv[2], "2000000") &&
         strcmp(argv[2], "2500000"))) {
        fprintf(stderr, "usage: %s CPUS(4|16) FREQUENCY_KHZ(1800000|2000000|2500000)\n", argv[0]);
        return 2;
    }
    unsigned clusters = (unsigned)atoi(argv[1]) / 4;
    long requested = strtol(argv[2], NULL, 10);
    cpu_set_t cpus;
    CPU_ZERO(&cpus);
    CPU_SET(0, &cpus);
    if (sched_setaffinity(0, sizeof(cpus), &cpus))
        fail("CPU0 affinity");

    glob_t policies = {0}, zones = {0};
    if (glob(POWER_SYSFS_ROOT "/devices/system/cpu/cpufreq/policy*", 0,
             NULL, &policies) || policies.gl_pathc != clusters)
        fail("SCMI policy count does not match AP clusters");
    char path[512];
    for (size_t i = 0; i < policies.gl_pathc; ++i) {
        child_path(path, sizeof(path), policies.gl_pathv[i], "scaling_driver");
        FILE *driver = fopen(path, "r");
        char name[64];
        if (!driver || fscanf(driver, "%63s", name) != 1 ||
            strcmp(name, "scmi"))
            fail("expected SCMI cpufreq driver");
        if (fclose(driver))
            fail(path);
        child_path(path, sizeof(path), policies.gl_pathv[i], "scaling_governor");
        write_text(path, "userspace\n");
        child_path(path, sizeof(path), policies.gl_pathv[i], "scaling_setspeed");
        write_text(path, argv[2]);
        child_path(path, sizeof(path), policies.gl_pathv[i], "scaling_cur_freq");
        long actual = 0;
        for (unsigned attempt = 0; attempt < 100; ++attempt) {
            actual = read_number(path);
            if (actual == requested)
                break;
            if (usleep(1000))
                fail("frequency wait");
        }
        if (actual != requested)
            fail("SCMI frequency readback timeout");
        printf("APOLLO_POWER_POLICY path=%s requested_khz=%ld actual_khz=%ld\n",
               policies.gl_pathv[i], requested, actual);
    }
    if (glob(POWER_SYSFS_ROOT "/class/thermal/thermal_zone*", 0, NULL, &zones))
        fail("no thermal zones");
    unsigned sensors = 0;
    for (size_t i = 0; i < zones.gl_pathc; ++i) {
        child_path(path, sizeof(path), zones.gl_pathv[i], "type");
        FILE *type = fopen(path, "r");
        char name[64];
        if (!type || fscanf(type, "%63s", name) != 1)
            fail(path);
        if (fclose(type))
            fail(path);
        unsigned cluster;
        int end = 0;
        if (sscanf(name, "cluster%u-thermal%n", &cluster, &end) != 1 ||
            !end || name[end])
            continue;
        if (cluster >= clusters || (sensors & (1U << cluster)))
            fail("unexpected or duplicate cluster sensor");
        child_path(path, sizeof(path), zones.gl_pathv[i], "temp");
        long temperature = read_number(path);
        if (temperature < -273150 || temperature > 300000)
            fail("invalid SCMI temperature");
        sensors |= 1U << cluster;
        printf("APOLLO_POWER_SENSOR cluster=%u temperature_mc=%ld\n", cluster, temperature);
    }
    if (sensors != (1U << clusters) - 1)
        fail("missing cluster sensor");
    uint64_t sum = memory_checksum(), expected = UINT64_C(4096) * 4097;
    if (sum != expected)
        fail("memory checksum");
    printf("APOLLO_POWER_PROBE PASS cpus=%s policies=%u frequency_khz=%ld "
           "cpu=0 checksum=%" PRIu64 " expected=%" PRIu64 "\n",
           argv[1], clusters, requested, sum, expected);
    globfree(&policies);
    globfree(&zones);
    return fflush(stdout) == 0 ? 0 : 1;
}
