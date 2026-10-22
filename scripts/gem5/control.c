/* SPDX-License-Identifier: BSD-3-Clause */
#define _GNU_SOURCE
#include <errno.h>
#include <gem5/m5ops.h>
#include <sched.h>
#include <stdio.h>
#include <string.h>
#include <sys/wait.h>
#include <unistd.h>

static void
barrier(void)
{
#if defined(__aarch64__)
    __asm__ volatile("dsb sy" : : : "memory");
#endif
}

static int
run_command(char **command)
{
    cpu_set_t cpus;
    CPU_ZERO(&cpus);
    CPU_SET(0, &cpus);
    if (sched_setaffinity(0, sizeof(cpus), &cpus) < 0) {
        perror("gem5-control: CPU0 affinity");
        return 1;
    }
    puts("GEM5_CONTROL_RUN cpu=0 scope=whole-command includes=fork,exec,kernel");
    if (fflush(stdout) != 0)
        return 1;
    barrier();
    m5_work_begin(0x5a535743, 0);
    barrier();
    m5_work_begin(0, 0);
    barrier();

    int result = 1, status;
    pid_t child = fork();
    if (child == 0) {
        execvp(command[0], command);
        int error = errno;
        perror("gem5-control: exec");
        _exit(error == ENOENT ? 127 : 126);
    }
    if (child < 0) {
        perror("gem5-control: fork");
    } else {
        pid_t waited;
        do {
            waited = waitpid(child, &status, 0);
        } while (waited < 0 && errno == EINTR);
        if (waited < 0)
            perror("gem5-control: waitpid");
        else if (WIFEXITED(status))
            result = WEXITSTATUS(status);
        else if (WIFSIGNALED(status))
            result = 128 + WTERMSIG(status);
    }
    barrier();
    m5_work_end(0, 0);
    barrier();
    return result;
}

int
main(int argc, char **argv)
{
    if (argc >= 3 && !strcmp(argv[1], "run"))
        return run_command(&argv[2]);
    if (argc == 2 && (!strcmp(argv[1], "switch") ||
                      !strcmp(argv[1], "begin") ||
                      !strcmp(argv[1], "end"))) {
        barrier();
        if (!strcmp(argv[1], "end"))
            m5_work_end(0, 0);
        else
            m5_work_begin(!strcmp(argv[1], "switch") ? 0x5a535743 : 0, 0);
        barrier();
        return 0;
    }
    if (argc == 2 && !strcmp(argv[1], "checkpoint")) {
        m5_checkpoint(0, 0);
        return 0;
    }
    if (argc == 2 && !strcmp(argv[1], "readfile")) {
        /* Fault in buffer pages before gem5's functional guest-memory write. */
        char buffer[4096] = {0};
        uint64_t offset = 0, count;
        while ((count = m5_read_file(buffer, sizeof(buffer), offset)) != 0) {
            if (count > sizeof(buffer) ||
                fwrite(buffer, 1, count, stdout) != count) {
                fprintf(stderr, "gem5-control: readfile transfer failed\n");
                return 1;
            }
            offset += count;
        }
        return fflush(stdout) == 0 ? 0 : 1;
    }
    fprintf(stderr, "usage: %s checkpoint|readfile|switch|begin|end|run COMMAND [ARGS...]\n", argv[0]);
    return 2;
}
