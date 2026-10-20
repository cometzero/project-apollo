/* SPDX-License-Identifier: BSD-3-Clause */
#define _GNU_SOURCE
#include "common.h"
#include <inttypes.h>

struct line {
    struct line *next;
    unsigned char pad[56];
};
_Static_assert(sizeof(struct line) == 64, "64-bit benchmark required");
static volatile uint64_t observed;

static inline void
roi_barrier(void)
{
#if defined(__aarch64__)
    __asm__ volatile("dsb sy" : : : "memory");
#endif
}

static __attribute__((noinline)) struct line *
chase(struct line *p, size_t count)
{
    for (size_t i = 0; i < count; ++i) {
        p = *(struct line *volatile *)p;
    }
    return p;
}

static __attribute__((noinline)) uint64_t
read_array(const uint64_t *data, size_t count)
{
    uint64_t a = 0, b = 0, c = 0, d = 0;
    const volatile uint64_t *p = data;
    for (size_t i = 0; i < count; i += 4) {
        a += p[i];
        b += p[i + 1];
        c += p[i + 2];
        d += p[i + 3];
    }
    return a + b + c + d;
}

int
main(int argc, char **argv)
{
    (void)spawn;
    (void)sync_workers;
    const char *mode = "cache";
    unsigned size_kib = 0, passes = 2;
    for (int i = 1; i < argc; ++i) {
        if (!strcmp(argv[i], "--host")) {
            host = 1;
        } else if (!strcmp(argv[i], "--mode") && i + 1 < argc) {
            mode = argv[++i];
        } else if (!strcmp(argv[i], "--size-kib") && i + 1 < argc) {
            size_kib = number(argv[++i]);
        } else if (!strcmp(argv[i], "--passes") && i + 1 < argc) {
            passes = number(argv[++i]);
        } else {
            fprintf(stderr, "usage: %s [--host] [--mode cache|dram] "
                    "[--size-kib N] [--passes N]\n", argv[0]);
            return 2;
        }
    }
    int cache = !strcmp(mode, "cache");
    if ((!cache && strcmp(mode, "dram")) || passes > 1024 ||
        size_kib > 262144) {
        return 2;
    }
#if !defined(__aarch64__)
    if (!host) {
        fprintf(stderr, "non-AArch64 execution requires --host\n");
        return 2;
    }
#endif
    if (!size_kib) {
        size_kib = cache ? 32 : 65536;
    }
    pin(0);
    size_t bytes = (size_t)size_kib * 1024;
    void *buffer = aligned_alloc(64, bytes);
    if (!buffer) {
        die("allocation");
    }
    size_t count = bytes / (cache ? sizeof(struct line) : sizeof(uint64_t));
    if (cache) {
        struct line *ring = buffer;
        size_t *order = malloc(count * sizeof(*order));
        if (!order) {
            die("shuffle allocation");
        }
        memset(buffer, 0, bytes);
        for (size_t i = 0; i < count; ++i) {
            order[i] = i;
        }
        uint32_t rng = UINT32_C(0x12345678);
        for (size_t i = count - 1; i; --i) {
            rng ^= rng << 13;
            rng ^= rng >> 17;
            rng ^= rng << 5;
            size_t j = rng % (i + 1), tmp = order[i];
            order[i] = order[j];
            order[j] = tmp;
        }
        for (size_t i = 0; i < count; ++i) {
            ring[order[i]].next = &ring[order[(i + 1) % count]];
        }
        free(order);
    } else {
        uint64_t *data = buffer;
        for (size_t i = 0; i < count; ++i) {
            data[i] = 1;
        }
    }
    puts("APOLLO_BENCH_READY initialization=atomic cpu=0");
    fflush(stdout);
    marker_begin(UINT64_C(0x5a535743));
    if (cache) {
        observed = (uintptr_t)chase(buffer, count);
    } else {
        observed = read_array(buffer, count);
    }
    uint64_t checksum = 0;
    /* Serialize O3 requests around markers; inner barriers count in ROI time. */
    roi_barrier();
    marker_begin(0);
    roi_barrier();
    for (unsigned p = 0; p < passes; ++p) {
        checksum += cache ? chase(buffer, count) == buffer
                          : read_array(buffer, count);
    }
    roi_barrier();
    marker_end();
    roi_barrier();
    uint64_t expected = (uint64_t)passes * (cache ? 1 : count);
    int ok = checksum == expected;
    printf("APOLLO_BENCH_RESULT {\"mode\":\"%s\",\"result\":\"%s\","
           "\"working_set_bytes\":%zu,\"passes\":%u,\"warmup_passes\":1,"
           "\"useful_bytes\":%" PRIu64 ",\"dependent_loads\":%" PRIu64 ","
           "\"checksum\":%" PRIu64 ",\"expected\":%" PRIu64 ","
           "\"host\":%s}\n",
           mode, ok ? "PASS" : "FAIL", bytes, passes,
           (uint64_t)count * passes * sizeof(uint64_t),
           cache ? (uint64_t)count * passes : 0, checksum, expected,
           host ? "true" : "false");
    fflush(stdout);
    free(buffer);
#if defined(__aarch64__)
    if (!host && ok) {
        register uint64_t x0 __asm__("x0") = 0;
        __asm__ volatile(".inst 0xff210110" : "+r"(x0) : : "memory");
    }
#endif
    return !ok;
}
