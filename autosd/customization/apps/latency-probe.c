/* Bounded Linux scheduling experiment, not a real-time qualification test. */
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <inttypes.h>
#include <sched.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/resource.h>
#include <time.h>
#include <unistd.h>

static volatile sig_atomic_t interrupted;
static void stop(int sig) { interrupted = sig; }
static void die(const char *what) { perror(what); exit(1); }
static uint64_t now_ns(void)
{
    struct timespec ts;
    if (clock_gettime(CLOCK_MONOTONIC, &ts)) die("clock_gettime");
    return (uint64_t)ts.tv_sec * 1000000000ULL + (uint64_t)ts.tv_nsec;
}
static void sleep_until(uint64_t ns)
{
    struct timespec ts = { (time_t)(ns / 1000000000ULL), (long)(ns % 1000000000ULL) };
    int rc;
    do { rc = clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, &ts, NULL); }
    while (rc == EINTR && !interrupted);
    if (rc && rc != EINTR) { errno = rc; die("clock_nanosleep"); }
}
static uint64_t number(const char *s, uint64_t min, uint64_t max)
{
    char *end;
    if (!*s || strspn(s, "0123456789") != strlen(s)) goto invalid;
    errno = 0;
    unsigned long long n = strtoull(s, &end, 10);
    if (errno || *end || n < min || n > max) goto invalid;
    return (uint64_t)n;
invalid:
    fprintf(stderr, "invalid numeric argument: %s (range %" PRIu64 "..%" PRIu64 ")\n", s, min, max);
    exit(2);
}
static int compare(const void *a, const void *b)
{
    uint64_t x = *(const uint64_t *)a, y = *(const uint64_t *)b;
    return (x > y) - (x < y);
}
static double percentile(const uint64_t *samples, size_t count, unsigned permille)
{
    if (!count) return 0;
    size_t rank = (count * permille + 999) / 1000;
    return samples[rank - 1] / 1000.0;
}
int main(int argc, char **argv)
{
    int cpu = -1, priority = 0, load = 0, lock = 0;
    uint64_t duration = 10, period_us = 1000, threshold_us = 1000, inject_us = 0;
    const char *output = NULL;
    for (int i = 1; i < argc; ++i) {
        const char *arg = argv[i];
        if (!strcmp(arg, "--load")) { load = 1; continue; }
        if (!strcmp(arg, "--mlock")) { lock = 1; continue; }
        if (!strcmp(arg, "--help")) {
            puts("latency-probe --cpu N --output NEW.json [--duration SEC(1..600)]\n"
                 "  [--period-us N(100..1000000)] [--priority N(0..80)]\n"
                 "  [--threshold-us N] [--inject-us N(0..1000000)] [--mlock]\n"
                 "  --load: bounded SCHED_OTHER CPU load; output optional.\n"
                 "Exit zero means valid measurement, not threshold PASS.");
            return 0;
        }
        if (i + 1 == argc) { fprintf(stderr, "missing value for %s\n", arg); return 2; }
        const char *value = argv[++i];
        if (!strcmp(arg, "--cpu")) cpu = (int)number(value, 0, CPU_SETSIZE - 1);
        else if (!strcmp(arg, "--duration")) duration = number(value, 1, 600);
        else if (!strcmp(arg, "--period-us")) period_us = number(value, 100, 1000000);
        else if (!strcmp(arg, "--priority")) priority = (int)number(value, 0, 80);
        else if (!strcmp(arg, "--threshold-us")) threshold_us = number(value, 0, 600000000);
        else if (!strcmp(arg, "--inject-us")) inject_us = number(value, 0, 1000000);
        else if (!strcmp(arg, "--output")) output = value;
        else { fprintf(stderr, "unknown option: %s\n", arg); return 2; }
    }
    if (cpu < 0 || (!load && !output) || (load && (priority || inject_us))) {
        fputs("--cpu and measurement --output required; --load forbids priority/injection\n", stderr);
        return 2;
    }
    /* Reserve evidence before changing scheduling; never overwrite a prior run. */
    FILE *out = stdout;
    if (output) {
        int fd = open(output, O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC, 0600);
        if (fd < 0) die("open exclusive output");
        out = fdopen(fd, "w");
        if (!out) die("fdopen");
    }
    struct sigaction action = { .sa_handler = stop };
    sigemptyset(&action.sa_mask);
    if (sigaction(SIGINT, &action, NULL) || sigaction(SIGTERM, &action, NULL)) die("sigaction");
    cpu_set_t affinity;
    CPU_ZERO(&affinity); CPU_SET(cpu, &affinity);
    if (sched_setaffinity(0, sizeof(affinity), &affinity)) die("sched_setaffinity");
    if (sched_getaffinity(0, sizeof(affinity), &affinity)) die("sched_getaffinity");
    if (CPU_COUNT(&affinity) != 1 || !CPU_ISSET(cpu, &affinity)) {
        fputs("requested CPU affinity was not applied\n", stderr); return 1;
    }
    uint64_t period = period_us * 1000;
    size_t capacity = (size_t)(duration * 1000000000ULL / period + 1);
    uint64_t *samples = load ? NULL : calloc(capacity, sizeof(*samples));
    if (!load && !samples) die("allocate samples");
    /* Touch every sample page plus stack before the timed window. */
    if (samples) {
        volatile uint64_t *touch = samples;
        for (size_t i = 0; i < capacity; i++) touch[i] = 0;
    }
    volatile unsigned char stack[65536];
    for (size_t i = 0; i < sizeof(stack); i++) stack[i] = 0;
    if (lock && mlockall(MCL_CURRENT | MCL_FUTURE)) die("mlockall requested");
    if (priority) {
        /* RLIMIT_RTTIME counts continuous CPU time between blocking syscalls. */
        struct rlimit limit = { 100000, 200000 };
        if (setrlimit(RLIMIT_RTTIME, &limit)) die("RLIMIT_RTTIME safeguard");
    }
    struct sched_param param = { .sched_priority = priority };
    int requested_policy = priority ? SCHED_FIFO : SCHED_OTHER;
    if (sched_setscheduler(0, requested_policy, &param)) die("sched_setscheduler requested policy");
    int policy = sched_getscheduler(0);
    if (policy < 0 || sched_getparam(0, &param)) die("read scheduler");
    if (policy != requested_policy || param.sched_priority != priority) {
        fputs("requested scheduling policy was not applied\n", stderr); return 1;
    }
    struct timespec resolution;
    struct rusage before, after;
    if (clock_getres(CLOCK_MONOTONIC, &resolution) || getrusage(RUSAGE_SELF, &before)) die("measurement preflight");
    uint64_t start = now_ns(), end = start + duration * 1000000000ULL;
    uint64_t next = start + period, missed = 0, exceed = 0;
    uint64_t first_threshold = 0, max_timestamp = 0, max_latency = 0;
    size_t count = 0;
    long double sum = 0;
    volatile uint64_t burn = 1;
    if (load) {
        while (!interrupted && now_ns() < end) {
            for (unsigned i = 0; i < 1024; i++) burn = burn * 6364136223846793005ULL + 1;
        }
    } else {
        while (!interrupted && next <= end) {
            sleep_until(next);
            if (interrupted) break;
            if (!count && inject_us) sleep_until(now_ns() + inject_us * 1000);
            if (interrupted) break;
            uint64_t wake = now_ns();
            uint64_t late = wake > next ? wake - next : 0;
            if (count >= capacity) { fputs("sample capacity exceeded\n", stderr); return 1; }
            samples[count++] = late;
            sum += late;
            if (!max_timestamp || late > max_latency) { max_latency = late; max_timestamp = wake; }
            if (late > threshold_us * 1000) {
                if (!exceed) first_threshold = wake;
                exceed++;
            }
            next += period;
            if (wake >= next) {
                /* Only count skipped deadlines in this experiment's window. */
                uint64_t bounded_wake = wake < end ? wake : end;
                if (bounded_wake >= next) {
                    uint64_t skip = (bounded_wake - next) / period + 1;
                    missed += skip; next += skip * period;
                }
            }
        }
    }
    uint64_t elapsed = now_ns() - start;
    if (getrusage(RUSAGE_SELF, &after)) die("getrusage after");
    /* Sorting/output are not part of the RT measurement. */
    param.sched_priority = 0;
    if (sched_setscheduler(0, SCHED_OTHER, &param)) die("restore SCHED_OTHER");
    if (lock && munlockall()) die("munlockall");
    if (count) qsort(samples, count, sizeof(*samples), compare);
    fprintf(out, "{\n  \"completed\": %s, \"mode\": \"%s\", \"synthetic\": %s,\n"
        "  \"cpu\": %d, \"affinity\": [%d], \"policy\": \"%s\", \"priority\": %d,\n"
        "  \"duration_sec\": %" PRIu64 ", \"elapsed_ns\": %" PRIu64 ", \"period_us\": %" PRIu64 ",\n"
        "  \"threshold_us\": %" PRIu64 ", \"injected_us\": %" PRIu64 ",\n"
        "  \"first_threshold_monotonic_ns\": %" PRIu64 ", \"max_latency_monotonic_ns\": %" PRIu64 ",\n"
        "  \"count\": %zu, \"threshold_exceedances\": %" PRIu64 ", \"missed_periods\": %" PRIu64 ",\n"
        "  \"clock_resolution_ns\": %" PRIu64 ", \"mlock_requested\": %s, \"mlock_success\": %s,\n"
        "  \"minor_faults_delta\": %ld, \"major_faults_delta\": %ld,\n"
        "  \"latency_us\": {\"min\": %.3f, \"mean\": %.3Lf, \"max\": %.3f,"
        " \"p50\": %.3f, \"p95\": %.3f, \"p99\": %.3f, \"p999\": %.3f}\n}\n",
        interrupted ? "false" : "true", load ? "load" : "measurement", inject_us ? "true" : "false",
        cpu, cpu, policy == SCHED_FIFO ? "SCHED_FIFO" : "SCHED_OTHER", priority,
        duration, elapsed, period_us, threshold_us, inject_us, first_threshold, max_timestamp, count, exceed, missed,
        (uint64_t)((uint64_t)resolution.tv_sec * 1000000000ULL + (uint64_t)resolution.tv_nsec),
        lock ? "true" : "false", lock ? "true" : "false",
        after.ru_minflt - before.ru_minflt, after.ru_majflt - before.ru_majflt,
        count ? samples[0] / 1000.0 : 0, count ? sum / count / 1000 : 0,
        count ? samples[count - 1] / 1000.0 : 0,
        percentile(samples, count, 500), percentile(samples, count, 950),
        percentile(samples, count, 990), percentile(samples, count, 999));
    if (fclose(out)) die("write output");
    free(samples);
    return interrupted ? 128 + interrupted : 0;
}
