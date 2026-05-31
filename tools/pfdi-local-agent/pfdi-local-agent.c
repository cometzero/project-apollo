// SPDX-License-Identifier: MIT
/*
 * Minimal local-build PFDI Online monitor agent.
 *
 * The Yocto demo image runs pfdi-sample-app from systemd.  The local
 * Buildroot initramfs intentionally stays small, so this agent only performs
 * the periodic OnL ioctl calls needed to feed the firmware-side PFDI monitor.
 */

#define _GNU_SOURCE

#include <errno.h>
#include <fcntl.h>
#include <getopt.h>
#include <inttypes.h>
#include <pthread.h>
#include <signal.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <sched.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/types.h>
#include <time.h>
#include <unistd.h>

#define DEFAULT_TEST_START 0U
#define DEFAULT_TEST_END 40U
#define DEFAULT_PERIOD_MS 60U
#define MAX_CPUS 256U

struct pfdi_test_range {
    uint64_t start;
    uint64_t end;
};

struct pfd_test_payload {
    struct pfdi_test_range range;
    uint64_t ft_id;
};

#define IOCTL_PFDI_PE_TEST_RUN _IOWR('P', 2, struct pfd_test_payload)

struct worker_config {
    unsigned int cpu;
    uint64_t start;
    uint64_t end;
    unsigned int period_ms;
    bool verbose;
};

static volatile sig_atomic_t stop_requested;

static void handle_signal(int sig)
{
    (void)sig;
    stop_requested = 1;
}

static void sleep_ms(unsigned int milliseconds)
{
    struct timespec req = {
        .tv_sec = milliseconds / 1000U,
        .tv_nsec = (long)(milliseconds % 1000U) * 1000000L,
    };

    while (!stop_requested && nanosleep(&req, &req) == -1 && errno == EINTR) {
    }
}

static unsigned int parse_online_cpu_count(void)
{
    FILE *fp;
    char buf[256];
    unsigned int max_cpu = 0;
    char *cursor;

    fp = fopen("/sys/devices/system/cpu/online", "r");
    if (!fp) {
        long count = sysconf(_SC_NPROCESSORS_ONLN);

        return count > 0 ? (unsigned int)count : 1U;
    }

    if (!fgets(buf, sizeof(buf), fp)) {
        fclose(fp);
        return 1U;
    }
    fclose(fp);

    cursor = buf;
    while (*cursor != '\0') {
        unsigned int first;
        unsigned int last;
        int consumed = 0;

        if (sscanf(cursor, "%u-%u%n", &first, &last, &consumed) == 2) {
            if (last > max_cpu) {
                max_cpu = last;
            }
        } else if (sscanf(cursor, "%u%n", &first, &consumed) == 1) {
            if (first > max_cpu) {
                max_cpu = first;
            }
        } else {
            break;
        }

        cursor += consumed;
        if (*cursor == ',') {
            cursor++;
        }
    }

    return max_cpu + 1U;
}

static int open_pfdi_device(unsigned int cpu)
{
    char path[64];
    bool logged_wait = false;

    snprintf(path, sizeof(path), "/dev/cpu/%u/pfdi", cpu);

    while (!stop_requested) {
        int fd = open(path, O_RDWR | O_CLOEXEC);

        if (fd >= 0) {
            return fd;
        }

        if (!logged_wait) {
            fprintf(stderr, "pfdi-local-agent: waiting for %s: %s\n",
                    path, strerror(errno));
            logged_wait = true;
        }
        sleep_ms(200);
    }

    return -1;
}

static int pin_current_thread(unsigned int cpu)
{
    cpu_set_t set;

    CPU_ZERO(&set);
    CPU_SET(cpu, &set);

    return pthread_setaffinity_np(pthread_self(), sizeof(set), &set);
}

static void *pfdi_worker(void *arg)
{
    const struct worker_config *config = arg;
    int fd;
    unsigned int failure_count = 0;
    int ret;

    ret = pin_current_thread(config->cpu);
    if (ret != 0) {
        fprintf(stderr, "pfdi-local-agent: failed to pin thread to CPU%u: %s\n",
                config->cpu, strerror(ret));
        return NULL;
    }

    fd = open_pfdi_device(config->cpu);
    if (fd < 0) {
        return NULL;
    }

    fprintf(stderr, "pfdi-local-agent: CPU%u range %" PRIu64 "-%" PRIu64
            " every %u ms\n",
            config->cpu, config->start, config->end, config->period_ms);

    while (!stop_requested) {
        struct pfd_test_payload payload = {
            .range = {
                .start = config->start,
                .end = config->end,
            },
            .ft_id = UINT64_MAX,
        };
        int ret = ioctl(fd, IOCTL_PFDI_PE_TEST_RUN, &payload);

        if (ret == 0) {
            failure_count = 0;
            if (config->verbose) {
                fprintf(stderr, "pfdi-local-agent: CPU%u OnL OK\n",
                        config->cpu);
            }
        } else {
            failure_count++;
            if (failure_count <= 5 || (failure_count % 100U) == 0U) {
                if (errno == EFAULT && payload.ft_id != UINT64_MAX) {
                    fprintf(stderr,
                            "pfdi-local-agent: CPU%u OnL failed at test %"
                            PRIu64 "\n",
                            config->cpu, payload.ft_id);
                } else {
                    fprintf(stderr,
                            "pfdi-local-agent: CPU%u OnL ioctl failed: %s\n",
                            config->cpu, strerror(errno));
                }
            }
        }

        sleep_ms(config->period_ms);
    }

    close(fd);
    return NULL;
}

static unsigned long parse_ulong_arg(const char *text, const char *name)
{
    char *end = NULL;
    unsigned long value;

    errno = 0;
    value = strtoul(text, &end, 0);
    if (errno != 0 || end == text || *end != '\0') {
        fprintf(stderr, "pfdi-local-agent: invalid %s: %s\n", name, text);
        exit(2);
    }

    return value;
}

static void usage(FILE *stream, const char *argv0)
{
    fprintf(stream,
            "Usage: %s [options]\n"
            "\n"
            "Options:\n"
            "  -c, --cpus COUNT       CPU count, 0 for auto (default: auto)\n"
            "  -s, --start TEST       First PFDI test id (default: %u)\n"
            "  -e, --end TEST         Last PFDI test id (default: %u)\n"
            "  -p, --period-ms MS     Period per CPU (default: %u)\n"
            "  -v, --verbose          Log successful OnL runs too\n"
            "  -h, --help             Show this help\n",
            argv0, DEFAULT_TEST_START, DEFAULT_TEST_END, DEFAULT_PERIOD_MS);
}

int main(int argc, char **argv)
{
    unsigned int cpu_count = 0;
    uint64_t start = DEFAULT_TEST_START;
    uint64_t end = DEFAULT_TEST_END;
    unsigned int period_ms = DEFAULT_PERIOD_MS;
    bool verbose = false;
    pthread_t *threads;
    struct worker_config *configs;
    struct sigaction sa = {
        .sa_handler = handle_signal,
    };

    static const struct option long_options[] = {
        {"cpus", required_argument, NULL, 'c'},
        {"start", required_argument, NULL, 's'},
        {"end", required_argument, NULL, 'e'},
        {"period-ms", required_argument, NULL, 'p'},
        {"verbose", no_argument, NULL, 'v'},
        {"help", no_argument, NULL, 'h'},
        {NULL, 0, NULL, 0},
    };

    for (;;) {
        int opt = getopt_long(argc, argv, "c:s:e:p:vh", long_options, NULL);

        if (opt == -1) {
            break;
        }

        switch (opt) {
        case 'c':
            cpu_count = (unsigned int)parse_ulong_arg(optarg, "CPU count");
            break;
        case 's':
            start = parse_ulong_arg(optarg, "start test id");
            break;
        case 'e':
            end = parse_ulong_arg(optarg, "end test id");
            break;
        case 'p':
            period_ms = (unsigned int)parse_ulong_arg(optarg, "period");
            break;
        case 'v':
            verbose = true;
            break;
        case 'h':
            usage(stdout, argv[0]);
            return 0;
        default:
            usage(stderr, argv[0]);
            return 2;
        }
    }

    if (start > end) {
        fprintf(stderr, "pfdi-local-agent: start must be <= end\n");
        return 2;
    }
    if (period_ms == 0) {
        fprintf(stderr, "pfdi-local-agent: period must be non-zero\n");
        return 2;
    }
    if (cpu_count == 0) {
        cpu_count = parse_online_cpu_count();
    }
    if (cpu_count == 0 || cpu_count > MAX_CPUS) {
        fprintf(stderr, "pfdi-local-agent: unsupported CPU count: %u\n",
                cpu_count);
        return 2;
    }

    sigemptyset(&sa.sa_mask);
    sigaction(SIGINT, &sa, NULL);
    sigaction(SIGTERM, &sa, NULL);

    threads = calloc(cpu_count, sizeof(*threads));
    configs = calloc(cpu_count, sizeof(*configs));
    if (!threads || !configs) {
        perror("calloc");
        free(threads);
        free(configs);
        return 1;
    }

    fprintf(stderr,
            "pfdi-local-agent: monitoring %u CPUs, range %" PRIu64 "-%"
            PRIu64 ", period %u ms\n",
            cpu_count, start, end, period_ms);

    for (unsigned int cpu = 0; cpu < cpu_count; cpu++) {
        configs[cpu] = (struct worker_config){
            .cpu = cpu,
            .start = start,
            .end = end,
            .period_ms = period_ms,
            .verbose = verbose,
        };
        if (pthread_create(&threads[cpu], NULL, pfdi_worker, &configs[cpu]) !=
            0) {
            fprintf(stderr, "pfdi-local-agent: failed to start CPU%u thread\n",
                    cpu);
            stop_requested = 1;
            cpu_count = cpu;
            break;
        }
    }

    while (!stop_requested) {
        sleep(1);
    }

    for (unsigned int cpu = 0; cpu < cpu_count; cpu++) {
        pthread_join(threads[cpu], NULL);
    }

    free(threads);
    free(configs);
    return 0;
}
