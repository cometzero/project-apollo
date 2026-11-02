/* SPDX-License-Identifier: BSD-3-Clause */
#define _GNU_SOURCE
#include "common.h"
#include <stdatomic.h>

#define MAX_BACKGROUND 15
#define CHUNK_WORDS 512
#define MAX_ALLOCATION (UINT64_C(1024) * 1024 * 1024)
_Static_assert(sizeof(size_t) == 8, "64-bit benchmark required");
_Static_assert(sizeof(float) == 4, "32-bit float required");

struct frame_sample {
    uint64_t release, start, finish;
    unsigned slot;
};

struct background {
    unsigned cpu;
    uint64_t *source, *destination;
    uint64_t chunks, checksum, warmup_checksum;
    uint64_t start, finish;
};

static unsigned width = 640, height = 480, frames = 4, pool = 2, warmup = 1;
static unsigned foreground_cpu, background_count, background_kib = 16384;
static int copy_background;
static size_t pixels, background_words;
static uint8_t *input;
static float *output;
static struct background background[MAX_BACKGROUND];
static struct frame_sample *samples;
static pthread_barrier_t barrier;
static atomic_int stop_background;
static cpu_set_t allowed_cpus;

static void
complete_memory(void)
{
#if defined(__aarch64__)
    __asm__ volatile("dsb sy" : : : "memory");
#else
    atomic_thread_fence(memory_order_seq_cst);
#endif
}

static uint64_t
counter(void)
{
    if (host) {
        struct timespec now;
        if (clock_gettime(CLOCK_MONOTONIC_RAW, &now)) {
            die("clock_gettime");
        }
        return (uint64_t)now.tv_sec * UINT64_C(1000000000) + now.tv_nsec;
    }
#if defined(__aarch64__)
    uint64_t value;
    __asm__ volatile("isb; mrs %0, cntvct_el0" : "=r"(value) : : "memory");
    return value;
#else
    abort();
#endif
}

static uint64_t
counter_frequency(void)
{
    if (host) {
        return UINT64_C(1000000000);
    }
#if defined(__aarch64__)
    uint64_t value;
    __asm__ volatile("mrs %0, cntfrq_el0" : "=r"(value));
    if (!value || value > UINT32_MAX) {
        fprintf(stderr, "invalid architectural counter frequency\n");
        exit(1);
    }
    return value;
#else
    abort();
#endif
}

static uint64_t
nanoseconds(uint64_t ticks, uint64_t frequency)
{
    return ticks / frequency * UINT64_C(1000000000) +
           ticks % frequency * UINT64_C(1000000000) / frequency;
}

static unsigned
integer(const char *text, unsigned maximum, int allow_zero)
{
    char *end;
    errno = 0;
    unsigned long value = strtoul(text, &end, 10);
    if (!*text || *text < '0' || *text > '9' || errno || *end ||
        value > maximum || (!allow_zero && !value)) {
        fprintf(stderr, "invalid integer: %s\n", text);
        exit(2);
    }
    return (unsigned)value;
}

static void
pin_cpu(unsigned cpu)
{
    cpu_set_t set;
    CPU_ZERO(&set);
    CPU_SET(cpu, &set);
    if (sched_setaffinity(0, sizeof(set), &set)) {
        die("setaffinity");
    }
}

static void
parse_background(const char *text)
{
    char *list = strdup(text), *cursor = list;
    if (!list) {
        die("CPU list allocation");
    }
    while (cursor) {
        char *item = strsep(&cursor, ",");
        if (background_count == MAX_BACKGROUND) {
            fprintf(stderr, "at most 15 background CPUs are supported\n");
            exit(2);
        }
        background[background_count++].cpu =
            integer(item, CPU_SETSIZE - 1, 1);
    }
    free(list);
}

static __attribute__((noinline)) void
normalize(const uint8_t *source, float *destination)
{
    float *r = destination, *g = destination + pixels;
    float *b = destination + pixels * 2;
    for (size_t i = 0; i < pixels; ++i) {
        r[i] = ((float)source[i * 3] - 128.0f) * 0x1p-7f;
        g[i] = ((float)source[i * 3 + 1] - 128.0f) * 0x1p-7f;
        b[i] = ((float)source[i * 3 + 2] - 128.0f) * 0x1p-7f;
    }
}

static void
image(unsigned slot)
{
    normalize(input + pixels * 3 * slot, output + pixels * 3 * slot);
    /* Keep every call observable across repeated frames and counter reads. */
    __asm__ volatile("" : : : "memory");
}

static uint64_t
background_chunk(struct background *worker, size_t begin)
{
    uint64_t sum = 0;
    const volatile uint64_t *source = worker->source;
    volatile uint64_t *destination = worker->destination;
    for (size_t i = begin; i < begin + CHUNK_WORDS; ++i) {
        if (copy_background) {
            destination[i] = source[i];
        } else {
            sum += source[i];
        }
    }
    return sum;
}

static void *
run_background(void *arg)
{
    struct background *worker = arg;
    pin_cpu(worker->cpu);
    sync_workers(&barrier); /* All workers pinned before the global switch. */
    sync_workers(&barrier);
    for (unsigned pass = 0; pass < warmup; ++pass) {
        for (size_t i = 0; i < background_words; i += CHUNK_WORDS) {
            worker->warmup_checksum += background_chunk(worker, i);
        }
    }
    complete_memory();
    sync_workers(&barrier);
    sync_workers(&barrier); /* ROI start. */
    worker->start = counter();
    size_t begin = 0;
    do {
        worker->checksum += background_chunk(worker, begin);
        ++worker->chunks;
        begin += CHUNK_WORDS;
        if (begin == background_words) {
            begin = 0;
        }
    } while (!atomic_load_explicit(&stop_background, memory_order_acquire));
    complete_memory();
    worker->finish = counter();
    sync_workers(&barrier);
    sync_workers(&barrier); /* Thread teardown stays outside the ROI. */
    return NULL;
}

static uint64_t
hash_byte(uint64_t hash, unsigned byte)
{
    return (hash ^ byte) * UINT64_C(1099511628211);
}

static int
validate_output(uint64_t *hash, uint64_t *mismatches)
{
    *hash = UINT64_C(14695981039346656037);
    *mismatches = 0;
    for (unsigned slot = 0; slot < pool; ++slot) {
        for (unsigned channel = 0; channel < 3; ++channel) {
            for (size_t i = 0; i < pixels; ++i) {
                float actual = output[(slot * 3 + channel) * pixels + i];
                float expected = (float)input[(slot * pixels + i) * 3 + channel]
                                 / 128.0f - 1.0f;
                if (actual != expected) {
                    ++*mismatches;
                }
                uint32_t bits;
                memcpy(&bits, &actual, sizeof(bits));
                for (unsigned b = 0; b < 4; ++b) {
                    *hash = hash_byte(*hash, (bits >> (8 * b)) & 255);
                }
            }
        }
    }
    return *mismatches == 0;
}

static void
usage(const char *program)
{
    fprintf(stderr,
            "usage: %s [--host] [--width N] [--height N] [--frames N] "
            "[--frame-pool N] [--warmup N] [--cpu ID] "
            "[--background-cpus ID,ID...] [--background-mode read|copy] "
            "[--background-kib N]\n", program);
}

int
main(int argc, char **argv)
{
    (void)number;
    (void)pin;
    (void)spawn;
    int explicit_cpu = 0, explicit_background = 0, explicit_mode = 0;
    for (int i = 1; i < argc; ++i) {
        const char *option = argv[i];
        if (!strcmp(option, "--host")) {
            host = 1;
        } else if (!strcmp(option, "--help")) {
            usage(argv[0]);
            return 0;
        } else if (i + 1 == argc) {
            usage(argv[0]);
            return 2;
        } else if (!strcmp(option, "--width")) {
            width = integer(argv[++i], 16384, 0);
        } else if (!strcmp(option, "--height")) {
            height = integer(argv[++i], 16384, 0);
        } else if (!strcmp(option, "--frames")) {
            frames = integer(argv[++i], 4096, 0);
        } else if (!strcmp(option, "--frame-pool")) {
            pool = integer(argv[++i], 64, 0);
        } else if (!strcmp(option, "--warmup")) {
            warmup = integer(argv[++i], 1024, 0);
        } else if (!strcmp(option, "--cpu")) {
            foreground_cpu = integer(argv[++i], CPU_SETSIZE - 1, 1);
            explicit_cpu = 1;
        } else if (!strcmp(option, "--background-cpus")) {
            if (explicit_background) {
                fprintf(stderr, "background CPU list must occur once\n");
                return 2;
            }
            explicit_background = 1;
            parse_background(argv[++i]);
        } else if (!strcmp(option, "--background-mode")) {
            const char *mode = argv[++i];
            if (strcmp(mode, "read") && strcmp(mode, "copy")) {
                usage(argv[0]);
                return 2;
            }
            copy_background = !strcmp(mode, "copy");
            explicit_mode = 1;
        } else if (!strcmp(option, "--background-kib")) {
            background_kib = integer(argv[++i], 262144, 0);
            explicit_mode = 1;
        } else {
            usage(argv[0]);
            return 2;
        }
    }
#if !defined(__aarch64__)
    if (!host) {
        fprintf(stderr, "non-AArch64 execution requires --host\n");
        return 2;
    }
#endif
    if (frames < pool || background_kib % 4 ||
        (explicit_mode && !background_count)) {
        fprintf(stderr, "frames must cover the pool; background size must be "
                "a multiple of 4 KiB and requires background CPUs\n");
        return 2;
    }
    if (sched_getaffinity(0, sizeof(allowed_cpus), &allowed_cpus)) {
        die("getaffinity");
    }
    if (host && !explicit_cpu) {
        for (foreground_cpu = 0; foreground_cpu < CPU_SETSIZE; ++foreground_cpu) {
            if (CPU_ISSET(foreground_cpu, &allowed_cpus)) {
                break;
            }
        }
    }
    cpu_set_t selected;
    CPU_ZERO(&selected);
    if (foreground_cpu >= CPU_SETSIZE ||
        !CPU_ISSET(foreground_cpu, &allowed_cpus)) {
        fprintf(stderr, "foreground CPU is unavailable\n");
        return 2;
    }
    CPU_SET(foreground_cpu, &selected);
    for (unsigned i = 0; i < background_count; ++i) {
        unsigned cpu = background[i].cpu;
        if (!CPU_ISSET(cpu, &allowed_cpus) || CPU_ISSET(cpu, &selected)) {
            fprintf(stderr, "background CPU is unavailable or duplicated\n");
            return 2;
        }
        CPU_SET(cpu, &selected);
    }
    pixels = (size_t)width * height;
    size_t image_bytes = pixels * 3 * pool;
    size_t bg_bytes = (size_t)background_kib * 1024;
    uint64_t allocation = (uint64_t)image_bytes * 5 +
        (uint64_t)bg_bytes * background_count * (copy_background ? 2 : 1) +
        (uint64_t)frames * sizeof(*samples);
    if (allocation > MAX_ALLOCATION) {
        fprintf(stderr, "requested buffers exceed 1 GiB workload allocation limit\n");
        return 2;
    }
    input = malloc(image_bytes);
    output = calloc(image_bytes, sizeof(*output));
    samples = calloc(frames, sizeof(*samples));
    if (!input || !output || !samples) {
        die("image allocation");
    }
    for (unsigned slot = 0; slot < pool; ++slot) {
        for (size_t i = 0; i < pixels; ++i) {
            for (unsigned channel = 0; channel < 3; ++channel) {
                input[(slot * pixels + i) * 3 + channel] =
                    (uint8_t)(i * 13 + channel * 37 + slot * 17 + i / width * 3);
            }
        }
    }
    /* First-touch output pages before switching from the Atomic boot CPUs. */
    volatile float *prefault_output = output;
    for (size_t i = 0; i < image_bytes; ++i) {
        prefault_output[i] = -2.0f;
    }
    volatile struct frame_sample *prefault_samples = samples;
    for (unsigned i = 0; i < frames; ++i) {
        prefault_samples[i].slot = 0;
    }
    background_words = bg_bytes / sizeof(uint64_t);
    for (unsigned i = 0; i < background_count; ++i) {
        struct background *worker = &background[i];
        worker->source = aligned_alloc(64, bg_bytes);
        if (copy_background) {
            worker->destination = aligned_alloc(64, bg_bytes);
        }
        if (!worker->source || (copy_background && !worker->destination)) {
            die("background allocation");
        }
        for (size_t j = 0; j < background_words; ++j) {
            worker->source[j] = 1;
            if (copy_background) {
                worker->destination[j] = 0;
            }
        }
    }
    int error = pthread_barrier_init(&barrier, NULL, background_count + 1);
    if (error) {
        errno = error;
        die("barrier_init");
    }
    pthread_t threads[MAX_BACKGROUND];
    for (unsigned i = 0; i < background_count; ++i) {
        error = pthread_create(&threads[i], NULL, run_background, &background[i]);
        if (error) {
            errno = error;
            die("pthread_create");
        }
    }
    pin_cpu(foreground_cpu);
    uint64_t frequency = counter_frequency();
    puts("APOLLO_IMAGE_READY initialization=atomic scope=synthetic_exploratory");
    fflush(stdout);
    sync_workers(&barrier);
    complete_memory();
    marker_begin(UINT64_C(0x5a535743));
    sync_workers(&barrier);
    for (unsigned pass = 0; pass < warmup; ++pass) {
        for (unsigned slot = 0; slot < pool; ++slot) {
            image(slot);
        }
    }
    complete_memory();
    sync_workers(&barrier);
    marker_begin(0);
    complete_memory();
    uint64_t roi_start = counter();
    sync_workers(&barrier);
    for (unsigned i = 0; i < frames; ++i) {
        samples[i].slot = i % pool;
        samples[i].release = i ? samples[i - 1].finish : counter();
        samples[i].start = counter();
        image(samples[i].slot);
        complete_memory();
        samples[i].finish = counter();
    }
    atomic_store_explicit(&stop_background, 1, memory_order_release);
    sync_workers(&barrier);
    complete_memory();
    uint64_t roi_end = counter();
    marker_end();
    complete_memory();
    sync_workers(&barrier);
    for (unsigned i = 0; i < background_count; ++i) {
        error = pthread_join(threads[i], NULL);
        if (error) {
            errno = error;
            die("pthread_join");
        }
    }
    uint64_t output_hash, mismatches;
    int ok = validate_output(&output_hash, &mismatches) && roi_end > roi_start;
    uint64_t background_total = 0;
    for (unsigned i = 0; i < background_count; ++i) {
        struct background *worker = &background[i];
        if (!worker->chunks || worker->start < roi_start ||
            worker->finish < worker->start || worker->finish > roi_end) {
            ok = 0;
        }
        if (copy_background) {
            for (size_t j = 0; j < background_words; ++j) {
                if (worker->destination[j] != 1) {
                    ok = 0;
                }
            }
        } else if (worker->checksum != worker->chunks * CHUNK_WORDS ||
                   worker->warmup_checksum != (uint64_t)background_words * warmup) {
            ok = 0;
        }
        uint64_t bytes = worker->chunks * CHUNK_WORDS * sizeof(uint64_t) *
                         (copy_background ? 2 : 1);
        background_total += bytes;
        uint64_t overlap_start = worker->start > samples[0].start
                                     ? worker->start : samples[0].start;
        uint64_t overlap_end = worker->finish < samples[frames - 1].finish
                                   ? worker->finish : samples[frames - 1].finish;
        uint64_t overlap = overlap_end > overlap_start ? overlap_end - overlap_start : 0;
        if (!overlap) {
            ok = 0;
        }
        printf("APOLLO_IMAGE_BACKGROUND {\"cpu\":%u,\"mode\":\"%s\","
               "\"completed_chunks\":%" PRIu64 ",\"useful_bytes\":%" PRIu64 ","
               "\"start_tick\":%" PRIu64 ",\"finish_tick\":%" PRIu64 ","
               "\"foreground_overlap_ticks\":%" PRIu64 "}\n",
               worker->cpu, copy_background ? "copy" : "read", worker->chunks,
               bytes, worker->start, worker->finish, overlap);
    }
    for (unsigned i = 0; i < frames; ++i) {
        struct frame_sample *sample = &samples[i];
        if (sample->release < roi_start || sample->start < sample->release ||
            sample->finish < sample->start || sample->finish > roi_end) {
            ok = 0;
        }
        printf("APOLLO_IMAGE_FRAME {\"frame\":%u,\"slot\":%u,"
               "\"release_tick\":%" PRIu64 ",\"start_tick\":%" PRIu64 ","
               "\"finish_tick\":%" PRIu64 ",\"duration_ns\":%" PRIu64 "}\n",
               i, sample->slot, sample->release, sample->start, sample->finish,
               nanoseconds(sample->finish - sample->start, frequency));
    }
    printf("APOLLO_IMAGE_RESULT {\"schema\":1,\"result\":\"%s\","
           "\"kernel\":\"rgb_u8_hwc_to_f32_chw\",\"fixture\":\"rgb_formula_v1\","
           "\"normalization\":\"(value-128)/128\",\"scope\":\"synthetic_exploratory\","
           "\"state\":\"steady_state_warmup_requested\",\"arrival\":\"closed_loop\","
           "\"queue_policy\":\"one_in_flight_no_drop\",\"host\":%s,"
           "\"width\":%u,\"height\":%u,\"frames\":%u,\"frame_pool\":%u,"
           "\"warmup_passes\":%u,\"cpu\":%u,\"background_workers\":%u,"
           "\"background_mode\":\"%s\",\"background_kib_per_worker\":%u,"
           "\"working_set_bytes\":%zu,\"useful_bytes\":%" PRIu64 ","
           "\"background_useful_bytes\":%" PRIu64 ",\"allocated_bytes\":%" PRIu64 ","
           "\"counter\":\"%s\",\"counter_hz\":%" PRIu64 ","
           "\"roi_start_tick\":%" PRIu64 ",\"roi_end_tick\":%" PRIu64 ","
           "\"roi_elapsed_ns\":%" PRIu64 ","
           "\"output_validation_scope\":\"every_element_of_each_final_pool_buffer\","
           "\"validated_elements\":%zu,\"output_mismatches\":%" PRIu64 ","
           "\"output_hash_fnv1a64\":\"%016" PRIx64 "\","
           "\"timing_scope\":\"kernel_calls_with_counter_and_completion_barrier\","
           "\"roi_includes\":\"start_barrier_frames_background_completion_barrier\","
           "\"background_cpus\":[",
           ok ? "PASS" : "FAIL", host ? "true" : "false", width, height, frames,
           pool, warmup, foreground_cpu, background_count,
           background_count ? (copy_background ? "copy" : "read") : "none",
           background_count ? background_kib : 0, image_bytes * 5,
           (uint64_t)pixels * 15 * frames, background_total, allocation,
           host ? "CLOCK_MONOTONIC_RAW" : "CNTVCT_EL0", frequency,
           roi_start, roi_end, nanoseconds(roi_end - roi_start, frequency),
           image_bytes, mismatches, output_hash);
    for (unsigned i = 0; i < background_count; ++i) {
        printf("%s%u", i ? "," : "", background[i].cpu);
    }
    puts("]}");
    fflush(stdout);
    for (unsigned i = 0; i < background_count; ++i) {
        free(background[i].source);
        free(background[i].destination);
    }
    pthread_barrier_destroy(&barrier);
    free(samples);
    free(output);
    free(input);
    return !ok;
}
