/* SPDX-License-Identifier: MIT */
/* Functional duplex pause/resume test; no physical I2S timing qualification. */
#include <alsa/asoundlib.h>
#include <signal.h>
#include <stdint.h>
#include <time.h>
#include <unistd.h>

#define PERIOD 1024
#define FRAMES 16384

static void check(int rc, const char *operation)
{
    if (rc < 0) {
        fprintf(stderr, "FAIL %s: %s (no recovery)\n", operation, snd_strerror(rc));
        exit(1);
    }
}

static void expired(int sig)
{
    static const char message[] = "FAIL pause test timeout\n";
    ssize_t ignored = write(STDERR_FILENO, message, sizeof(message) - 1);
    (void)ignored;
    (void)sig;
    _exit(124);
}

static snd_pcm_t *open_pcm(const char *name, snd_pcm_stream_t stream,
                           snd_pcm_uframes_t buffer, int require_pause)
{
    snd_pcm_t *pcm;
    snd_pcm_hw_params_t *hw;
    snd_pcm_sw_params_t *sw;
    snd_pcm_uframes_t boundary;

    check(snd_pcm_open(&pcm, name, stream, SND_PCM_NONBLOCK), "open");
    snd_pcm_hw_params_alloca(&hw);
    check(snd_pcm_hw_params_any(pcm, hw), "hw any");
    check(snd_pcm_hw_params_set_access(pcm, hw, SND_PCM_ACCESS_RW_INTERLEAVED), "access");
    check(snd_pcm_hw_params_set_format(pcm, hw, SND_PCM_FORMAT_S16_LE), "format");
    check(snd_pcm_hw_params_set_channels(pcm, hw, 2), "channels");
    check(snd_pcm_hw_params_set_rate(pcm, hw, 48000, 0), "rate");
    check(snd_pcm_hw_params_set_period_size(pcm, hw, PERIOD, 0), "period");
    check(snd_pcm_hw_params_set_buffer_size(pcm, hw, buffer), "buffer");
    check(snd_pcm_hw_params(pcm, hw), "hw params");
    printf("CAPABILITY pcm=%s pause=%d period=%d buffer=%lu\n", name,
           snd_pcm_hw_params_can_pause(hw), PERIOD, (unsigned long)buffer);
    if (require_pause && !snd_pcm_hw_params_can_pause(hw)) {
        fprintf(stderr, "FAIL pause unsupported: %s\n", name);
        exit(1);
    }
    snd_pcm_sw_params_alloca(&sw);
    check(snd_pcm_sw_params_current(pcm, sw), "sw current");
    check(snd_pcm_sw_params_get_boundary(sw, &boundary), "boundary");
    check(snd_pcm_sw_params_set_start_threshold(pcm, sw, boundary), "manual start");
    check(snd_pcm_sw_params_set_avail_min(pcm, sw, PERIOD), "avail min");
    check(snd_pcm_sw_params(pcm, sw), "sw params");
    check(snd_pcm_prepare(pcm), "prepare");
    return pcm;
}

static void pause_stream(snd_pcm_t *pcm, int enable, const char *name)
{
    check(snd_pcm_pause(pcm, enable), name);
    snd_pcm_state_t expected = enable ? SND_PCM_STATE_PAUSED : SND_PCM_STATE_RUNNING;
    if (snd_pcm_state(pcm) != expected) {
        fprintf(stderr, "FAIL %s state=%s\n", name,
                snd_pcm_state_name(snd_pcm_state(pcm)));
        exit(1);
    }
    printf("CONTROL %s state=%s\n", name, snd_pcm_state_name(expected));
}

int main(int argc, char **argv)
{
    static uint16_t tx[FRAMES][2], rx[PERIOD][2];
    snd_pcm_uframes_t buffer = 2048;
    unsigned int written, received = 0;
    uint32_t seed = 0x193a78;
    int paused = 0, draining = 0, drained = 0;
    int both, drop_paused;
    char *end;

    if (argc < 4 || argc > 5 ||
        (strcmp(argv[3], "tx") && strcmp(argv[3], "both") &&
         strcmp(argv[3], "drop"))) {
        fprintf(stderr, "Usage: %s playback-pcm capture-pcm tx|both|drop [buffer-frames]\n", argv[0]);
        return 2;
    }
    if (argc == 5) {
        buffer = strtoul(argv[4], &end, 10);
        if (*end || buffer < 2 * PERIOD || buffer > FRAMES / 2 || buffer % PERIOD) {
            fprintf(stderr, "buffer must be 2048..8192 and a multiple of 1024\n");
            return 2;
        }
    }
    drop_paused = !strcmp(argv[3], "drop");
    both = !strcmp(argv[3], "both") || drop_paused;
    setvbuf(stdout, NULL, _IOLBF, 0);
    signal(SIGALRM, expired);
    alarm(120);
    for (unsigned int i = 0; i < FRAMES; i++) {
        for (unsigned int c = 0; c < 2; c++) {
            seed = seed * 1664525u + 1013904223u;
            tx[i][c] = (uint16_t)(seed >> 16) | 1u;
        }
    }
    snd_pcm_t *capture = open_pcm(argv[2], SND_PCM_STREAM_CAPTURE, buffer, both);
    snd_pcm_t *play = open_pcm(argv[1], SND_PCM_STREAM_PLAYBACK, buffer, 1);
    snd_pcm_sframes_t n = snd_pcm_writei(play, tx, buffer);
    check((int)n, "preload");
    if ((snd_pcm_uframes_t)n != buffer) {
        fprintf(stderr, "FAIL short preload\n");
        return 1;
    }
    written = buffer;
    check(snd_pcm_start(capture), "start capture");
    check(snd_pcm_start(play), "start playback");
    while (received < FRAMES || !drained) {
        int progress = 0;
        if (received < FRAMES) {
            unsigned int count = FRAMES - received;
            if (count > PERIOD) count = PERIOD;
            n = snd_pcm_readi(capture, rx, count);
            if (n > 0) {
                for (snd_pcm_sframes_t i = 0; i < n; i++, received++) {
                    if (memcmp(rx[i], tx[received], sizeof(rx[i]))) {
                        fprintf(stderr, "FAIL frame=%u expected=%04x/%04x actual=%04x/%04x\n",
                                received, tx[received][0], tx[received][1], rx[i][0], rx[i][1]);
                        return 1;
                    }
                }
                progress = 1;
            } else if (n != -EAGAIN) check((int)n, "capture read");
        }
        if (written < FRAMES) {
            n = snd_pcm_writei(play, tx + written, FRAMES - written);
            if (n > 0) { written += n; progress = 1; }
            else if (n != -EAGAIN) check((int)n, "playback write");
        }
        if (!paused && received >= 2 * PERIOD && written < FRAMES) {
            pause_stream(play, 1, "pause TX");
            if (both) pause_stream(capture, 1, "pause RX");
            /* TX is stopped; no deliberate producer overrun during the hold.
             * In tx-only mode RX may consume the bounded in-flight FIFO tail.
             */
            struct timespec hold = { .tv_nsec = 100000000 };
            if (nanosleep(&hold, NULL)) { perror("pause hold"); return 1; }
            if (drop_paused) {
                check(snd_pcm_drop(play), "drop paused TX");
                check(snd_pcm_drop(capture), "drop paused RX");
                if (snd_pcm_state(play) != SND_PCM_STATE_SETUP ||
                    snd_pcm_state(capture) != SND_PCM_STATE_SETUP) {
                    fprintf(stderr, "FAIL paused drop did not reach SETUP\n");
                    return 1;
                }
                check(snd_pcm_close(play), "close dropped TX");
                check(snd_pcm_close(capture), "close dropped RX");
                alarm(0);
                /* Intentional cancellation: not a full-file data PASS. */
                printf("I2S_PAUSED_STOP_PASS playback=%s capture=%s compared_prefix=%u\n",
                       argv[1], argv[2], received);
                return 0;
            }
            if (both) pause_stream(capture, 0, "resume RX");
            pause_stream(play, 0, "resume TX");
            paused = 1;
        }
        if (written == FRAMES && !drained) {
            int rc = snd_pcm_drain(play);
            if (!draining) { printf("DRAIN submitted=%u received=%u\n", written, received); draining = 1; }
            if (!rc) drained = 1;
            else if (rc != -EAGAIN) check(rc, "drain playback");
            else if (snd_pcm_state(play) == SND_PCM_STATE_SETUP)
                drained = 1;
        }
        if (!progress) usleep(100);
    }
    check(snd_pcm_drop(capture), "drop capture");
    check(snd_pcm_close(capture), "close capture");
    check(snd_pcm_close(play), "close playback");
    alarm(0);
    if (!paused) { fprintf(stderr, "FAIL pause was not exercised\n"); return 1; }
    printf("I2S_PAUSE_PASS playback=%s capture=%s mode=%s frames=%d bytes=%d format=S16_LE rate=48000 period=%d buffer=%lu\n",
           argv[1], argv[2], argv[3], FRAMES, FRAMES * 4, PERIOD, (unsigned long)buffer);
    return 0;
}
