/* SPDX-License-Identifier: MIT
 * Development heartbeat workload; no vehicle control or safety claim.
 */
#define _POSIX_C_SOURCE 200809L
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

static volatile sig_atomic_t running = 1;

static void stop(int signal_number)
{
    (void)signal_number;
    running = 0;
}

static double monotonic(void)
{
    struct timespec now;
    if (clock_gettime(CLOCK_MONOTONIC, &now))
        exit(2);
    return now.tv_sec + now.tv_nsec / 1000000000.0;
}

int main(int argc, char **argv)
{
    if (argc != 3 || (strcmp(argv[1], "run") && strcmp(argv[1], "health"))) {
        fprintf(stderr, "usage: %s run|health HEARTBEAT_FILE\n", argv[0]);
        return 2;
    }
    if (!strcmp(argv[1], "health")) {
        double stamp = 0, age;
        FILE *input = fopen(argv[2], "r");
        if (!input)
            return 1;
        int valid = fscanf(input, "%lf", &stamp) == 1;
        fclose(input);
        age = monotonic() - stamp;
        return valid && age >= 0 && age < 1.0 ? 0 : 1;
    }
    char *temporary = malloc(strlen(argv[2]) + 5);
    if (!temporary)
        return 2;
    sprintf(temporary, "%s.new", argv[2]);
    /* Container PID 1 ignores default-fatal signals without a handler. */
    struct sigaction action = { .sa_handler = stop, .sa_flags = SA_RESTART };
    sigemptyset(&action.sa_mask);
    if (sigaction(SIGTERM, &action, NULL) || sigaction(SIGINT, &action, NULL)) {
        free(temporary);
        return 2;
    }
    while (running) {
        FILE *output = fopen(temporary, "w");
        if (!output)
            return 2;
        fprintf(output, "%.9f\n", monotonic());
        if (fclose(output) || rename(temporary, argv[2]))
            return 2;
        struct timespec interval = { .tv_nsec = 100000000 };
        nanosleep(&interval, NULL);
    }
    free(temporary);
    return 0;
}
