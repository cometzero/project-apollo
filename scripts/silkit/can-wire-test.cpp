// SPDX-License-Identifier: MIT
#include "can_wire.h"
#include <cstdlib>
#include <iostream>
#define CHECK(condition) do { if (!(condition)) { std::cerr << "FAIL line " << __LINE__ << '\n'; return 1; } } while (false)
int main() {
    using namespace Vmcu;
    CHECK(crc32(reinterpret_cast<const uint8_t*>("123456789"), 9) == 0xcbf43926u);
    Frame f; f.type = Tx; f.epoch = 1; f.token = 7; f.id = 0x123;
    for (unsigned dlc = 0; dlc < 16; ++dlc) {
        f.flags = Fdf | Brs; f.dlc = dlc; f.length = dlc_length(dlc);
        for (unsigned i = 0; i < f.length; ++i) f.data[i] = uint8_t(i);
        auto bytes = encode(f); Frame parsed;
        CHECK(decode(bytes.data(), parsed)); CHECK(parsed.length == f.length);
        CHECK(parsed.token == 7);
        for (unsigned i = 0; i < f.length; ++i) CHECK(parsed.data[i] == f.data[i]);
        for (unsigned i = f.length; i < 64; ++i) CHECK(parsed.data[i] == 0);
    }
    f.flags = 0; f.dlc = 9; f.length = 12; CHECK(!valid_can(f));
    f.flags = Fdf | Rtr; f.length = 0; CHECK(!valid_can(f));
    f.flags = Brs; f.dlc = 0; CHECK(!valid_can(f));
    f.flags = Esi; CHECK(!valid_can(f));
    f.flags = 0; f.id = 0x800; CHECK(!valid_can(f));
    f.flags = Ide; f.id = 0x1fffffff; CHECK(valid_can(f));
    f.id++; CHECK(!valid_can(f));
    f = {}; f.type = Tx; f.epoch = 3; f.token = 1; f.id = 0x123;
    f.flags = Rtr; f.dlc = 8; CHECK(valid_can(f));
    auto bytes = encode(f); Frame parsed; CHECK(decode(bytes.data(), parsed));
    Decoder decoder; unsigned delivered = 0;
    auto collect = [&](const Frame&) { ++delivered; };
    decoder.feed(bytes.data(), 9, collect); CHECK(delivered == 0);
    decoder.feed(bytes.data() + 9, bytes.size() - 9, collect); CHECK(delivered == 1);
    bytes[45] ^= 1; decoder.feed(bytes.data(), bytes.size(), collect); CHECK(delivered == 1);
    bytes = encode(f); decoder.feed(bytes.data(), bytes.size(), collect); CHECK(delivered == 2);
    CHECK(decoder.rejected > 0);
    f = {}; f.type = Ack; f.epoch = 4; f.token = 7; f.status = Transmitted;
    bytes = encode(f); CHECK(decode(bytes.data(), parsed));
    bytes[24] = 1; put32(&bytes[88], crc32(bytes.data(), 88)); CHECK(!decode(bytes.data(), parsed));
    std::cout << "PASS CAN1 CRC, FD DLC0..15, classic/RTR bounds, flags, IDs, fragmentation, resync, padding\n";
}
