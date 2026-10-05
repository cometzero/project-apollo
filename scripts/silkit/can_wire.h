// SPDX-License-Identifier: MIT
#pragma once
#include <array>
#include <cstdint>
#include <cstring>
#include <string>

namespace Vmcu {
constexpr size_t WireSize = 92;
enum : uint8_t { Tx = 1, Rx = 2, Ack = 3, Control = 4 };
enum : uint8_t { Ide = 1, Rtr = 2, Fdf = 4, Brs = 8, Esi = 16 };
enum : uint32_t { Transmitted = 1, Canceled = 2, Error = 3, QueueFull = 4 };
struct Frame {
    uint8_t type = 0, flags = 0, dlc = 0, length = 0;
    uint32_t epoch = 0, token = 0, id = 0, status = 0;
    std::array<uint8_t, 64> data{};
};
inline unsigned dlc_length(unsigned dlc) {
    constexpr unsigned lengths[] = {0,1,2,3,4,5,6,7,8,12,16,20,24,32,48,64};
    return dlc < 16 ? lengths[dlc] : 255;
}
inline bool valid_can(const Frame& f) {
    if (f.flags & ~31u || f.dlc > 15 || f.length > 64) return false;
    if (f.id > ((f.flags & Ide) ? 0x1fffffffu : 0x7ffu)) return false;
    if (!(f.flags & Fdf) && (f.dlc > 8 || (f.flags & (Brs | Esi)))) return false;
    if ((f.flags & (Fdf | Rtr)) == (Fdf | Rtr)) return false;
    return f.length == ((f.flags & Rtr) ? 0 : dlc_length(f.dlc));
}
inline uint32_t crc32(const uint8_t* data, size_t size) {
    uint32_t crc = 0xffffffffu;
    for (size_t i = 0; i < size; ++i) {
        crc ^= data[i];
        for (unsigned bit = 0; bit < 8; ++bit)
            crc = (crc >> 1) ^ (0xedb88320u & (0u - (crc & 1)));
    }
    return ~crc;
}
inline void put32(uint8_t* out, uint32_t v) {
    for (unsigned i = 0; i < 4; ++i) out[i] = uint8_t(v >> (8 * i));
}
inline uint32_t get32(const uint8_t* p) {
    return uint32_t(p[0]) | uint32_t(p[1]) << 8 | uint32_t(p[2]) << 16 | uint32_t(p[3]) << 24;
}
inline std::array<uint8_t, WireSize> encode(const Frame& f) {
    std::array<uint8_t, WireSize> out{};
    std::memcpy(out.data(), "CAN1", 4);
    out[4] = f.type; out[5] = f.flags; out[6] = f.dlc; out[7] = f.length;
    put32(&out[8], f.epoch); put32(&out[12], f.token);
    put32(&out[16], f.id); put32(&out[20], f.status);
    std::memcpy(&out[24], f.data.data(), f.length);
    put32(&out[88], crc32(out.data(), 88));
    return out;
}
inline bool decode(const uint8_t* p, Frame& f) {
    if (std::memcmp(p, "CAN1", 4) || get32(p + 88) != crc32(p, 88)) return false;
    f = {};
    f.type = p[4]; f.flags = p[5]; f.dlc = p[6]; f.length = p[7];
    f.epoch = get32(p + 8); f.token = get32(p + 12);
    f.id = get32(p + 16); f.status = get32(p + 20);
    if (!f.epoch || f.length > 64) return false;
    if (f.type == Tx || f.type == Rx) {
        if (!valid_can(f) || f.status || (f.type == Tx ? !f.token : f.token != 0)) return false;
    } else if (f.type == Ack || f.type == Control) {
        if (f.flags || f.dlc || f.length || f.id) return false;
        if (f.type == Ack ? (!f.token || f.status < 1 || f.status > 4)
                          : (f.token || f.status < 1 || f.status > 2)) return false;
    } else return false;
    for (unsigned i = f.length; i < 64; ++i) if (p[24 + i]) return false;
    std::memcpy(f.data.data(), p + 24, f.length);
    return true;
}
// At most 91 incomplete bytes retained; malformed input advances one byte.
class Decoder {
    std::array<uint8_t, WireSize> bytes{};
    size_t used = 0;
public:
    uint64_t rejected = 0;
    void reset() { used = 0; }
    template<class Callback> void feed(const uint8_t* data, size_t size, Callback cb) {
        for (size_t i = 0; i < size; ++i) {
            bytes[used++] = data[i];
            if (used != WireSize) continue;
            Frame f;
            if (decode(bytes.data(), f)) { used = 0; cb(f); }
            else { ++rejected; std::memmove(bytes.data(), bytes.data() + 1, --used); }
        }
    }
};
inline std::string hex(const Frame& f) {
    const char* digits = "0123456789abcdef";
    std::string s;
    for (unsigned i = 0; i < f.length; ++i) { s += digits[f.data[i] >> 4]; s += digits[f.data[i] & 15]; }
    return s;
}
}
