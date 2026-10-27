/* SPDX-License-Identifier: BSD-3-Clause */
#include <stdbool.h>
#include <stdint.h>

#define HIPC_TX 0x39000000UL
#define HIPC_RX 0x39040000UL
#define PFDI_TX 0x39200000UL
#define PFDI_RX 0x39240000UL
#define SHMEM 0x48000000UL
#define GICD 0x30200000UL
#define GUARD 0x5a17c0deU

volatile uint64_t recovery_pc, el2_return_pc;
static unsigned failures;

static uint32_t rd(uint64_t address)
{
    return *(volatile uint32_t *)address;
}

static void wr(uint64_t address, uint32_t value)
{
    *(volatile uint32_t *)address = value;
    __asm__ volatile("dsb sy" ::: "memory");
}

static void putstr(const char *s)
{
    while (*s)
        wr(0x2a410000, *s++);
}

static void check(bool ok, const char *name)
{
    failures += !ok;
    putstr(ok ? "PASS " : "FAIL ");
    putstr(name);
    putstr("\n");
}

__attribute__((noreturn)) static void finish(unsigned code)
{
    if (code) {
        __asm__ volatile("mov x0, #0; mov x1, #1; .inst 0xff220110"
                         ::: "x0", "x1", "memory");
    } else {
        __asm__ volatile("mov x0, #0; .inst 0xff210110"
                         ::: "x0", "memory");
    }
    for (;;)
        __asm__ volatile("wfi");
}

uint64_t exception_handler(void)
{
    putstr("FAIL unexpected exception\n");
    finish(1);
}

static uint64_t dbc(uint64_t frame, unsigned channel)
{
    return frame + 0x1000 + channel * 32;
}

static uint32_t pending(unsigned irq)
{
    return rd(GICD + 0x200 + (irq / 32) * 4) & (1U << (irq % 32));
}

static uint32_t header(unsigned protocol, unsigned msg, unsigned slot)
{
    return (slot << 18) | (protocol << 10) | msg;
}

static void request(unsigned slot, uint32_t hdr, uint32_t len)
{
    uint64_t addr = SHMEM + slot * 40;
    wr(addr + 4, 0);
    wr(addr + 0x10, 0); /* SCMI poll mode. */
    wr(addr + 0x14, len);
    wr(addr + 0x18, hdr);
    wr(dbc(PFDI_TX, slot + 2) + 0xc, 1);
}

static void check_response(unsigned slot, uint32_t hdr, uint32_t len,
                           int32_t status)
{
    uint64_t addr = SHMEM + slot * 40;
    check(rd(addr + 4) == 1 && rd(addr + 0x10) == 0 &&
          rd(addr + 0x14) == len && rd(addr + 0x18) == hdr &&
          rd(addr + 0x1c) == (uint32_t)status,
          "SCMI response header status length");
    check(rd(addr) == GUARD && rd(addr + 0x24) == GUARD &&
          rd(SHMEM + 160) == GUARD, "SCMI slot guard words intact");
}

int main(void)
{
    const uint64_t frames[] = {HIPC_TX, HIPC_RX, PFDI_TX, PFDI_RX};
    for (unsigned i = 0; i < 4; ++i) {
        uint64_t frame = frames[i];
        check(rd(frame) == (i & 1) && rd(frame + 0x10) == 1 &&
              rd(frame + 0x20) == 31 && rd(frame + 0xfcc) == 0x20 &&
              (rd(frame + 0xfc8) & 0xfff) == 0x43b,
              "MHUv3 frame discovery");
        wr(frame + 0x100, 1);
        check(rd(frame + 0x100) == 1, "MHU operational request");
    }
    // ArmRelease has no Security extension: distributor uses single state.
    // Keep CPU DAIF masked; inspect the GIC's level-pending bit directly.
    wr(GICD, 0x40);
    wr(SHMEM + 160, GUARD);
    for (unsigned slot = 0; slot < 4; ++slot) {
        uint64_t addr = SHMEM + slot * 40;
        check(rd(addr + 4) == 1, "initial SCMI FREE status");
        wr(addr, GUARD);
        wr(addr + 0x24, GUARD);
    }
    for (unsigned slot = 0; slot < 4; ++slot) {
        unsigned channel = slot + 2;
        uint64_t tx = dbc(PFDI_TX, channel);
        uint64_t rx = dbc(PFDI_RX, channel);
        uint32_t hdr = header(0x90, 0, slot);
        request(slot, hdr, 4);
        check_response(slot, hdr, 12, 0);
        check(rd(SHMEM + slot * 40 + 0x20) == 0x20000,
              "PFDI protocol version 2.0");
        check(rd(tx) == 0 && rd(tx + 0x10) == 1,
              "TX doorbell consumed and ACK latched");
        check(rd(PFDI_TX + 0x400) == 0 && !pending(82),
              "disabled TX completion does not raise IRQ");
        wr(tx + 0x1c, 1);
        wr(tx + 0x18, 1);
        check(rd(PFDI_TX + 0x400) == (1U << channel) && pending(82),
              "TX completion enable raises combined GIC IRQ");
        wr(tx + 0x14, 1);
        check(rd(tx + 0x10) == 0 && rd(PFDI_TX + 0x400) == 0 && !pending(82),
              "TX ACK W1C deasserts GIC IRQ");
        wr(tx + 0x18, 0);
        wr(tx + 0x1c, 0);

        check(rd(rx) == 1 && rd(rx + 4) == 0,
              "RX response pending while masked");
        wr(rx + 0x1c, 1);
        wr(rx + 0x18, 1);
        check(rd(rx + 4) == 1 &&
              rd(PFDI_RX + 0x400) == (1U << channel) && pending(82),
              "RX unmask raises combined GIC IRQ");
        wr(rx + 0x14, 1);
        check(rd(rx) == 1 && !pending(82),
              "RX mask deasserts IRQ without discarding pending data");
        wr(rx + 0x18, 1);
        wr(rx + 8, 1);
        check(rd(rx) == 0 && rd(PFDI_RX + 0x400) == 0 && !pending(82),
              "RX W1C clears doorbell and GIC IRQ");
        wr(rx + 0x14, ~0U);
        wr(rx + 0x1c, 0);

        for (unsigned message = 3; message <= 4; ++message) {
            hdr = header(0x90, message, slot);
            request(slot, hdr, 8);
            check_response(slot, hdr, 8, 0);
        }
        wr(tx + 0x14, 1);
        wr(rx + 8, ~0U);
    }

    const uint32_t bad_headers[] = {
        header(0x90, 0x55, 0), header(0x91, 0, 0)
    };
    for (unsigned i = 0; i < 2; ++i) {
        request(0, bad_headers[i], 4);
        check_response(0, bad_headers[i], 8, -1);
    }
    const uint32_t bad_lengths[] = {0, 3, 17, 0xffffffff};
    uint32_t hdr = header(0x90, 0, 0);
    for (unsigned i = 0; i < 4; ++i) {
        request(0, hdr, bad_lengths[i]);
        check_response(0, hdr, 8, -10);
    }
    request(0, hdr, 8); /* Version has no request payload. */
    check_response(0, hdr, 8, -10);
    for (unsigned msg = 3; msg <= 4; ++msg) {
        uint32_t status_hdr = header(0x90, msg, 0);
        request(0, status_hdr, 4); /* Status requires one payload word. */
        check_response(0, status_hdr, 8, -10);
    }
    hdr |= 1U << 8;
    request(0, hdr, 4);
    check_response(0, hdr, 8, -10);
    // No SCMI slot is mapped to channel 0; it must not alias CPU0's slot.
    wr(dbc(PFDI_TX, 0) + 0xc, 1);
    check(rd(dbc(PFDI_TX, 0)) == 1 && rd(dbc(PFDI_TX, 0) + 0x10) == 0,
          "unsupported PFDI channel remains pending");
    check_response(0, hdr, 8, -10);

    wr(dbc(HIPC_TX, 0) + 0x1c, 1);
    wr(dbc(HIPC_TX, 0) + 0x18, 1);
    wr(dbc(HIPC_TX, 0) + 0xc, 1);
    check(rd(dbc(HIPC_TX, 0)) == 1 && rd(dbc(HIPC_TX, 0) + 0x10) == 0 &&
          rd(dbc(HIPC_RX, 0)) == 0 && !pending(72) && !pending(73),
          "HIPC AP offline has no synthetic handshake or completion");
    putstr(failures ? "MHU_NATIVE_FAIL\n" : "MHU_NATIVE_PASS\n");
    finish(failures);
}
