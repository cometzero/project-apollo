// SPDX-License-Identifier: MIT
#include "can_wire.h"
#include <silkit/SilKit.hpp>
#include <silkit/services/can/all.hpp>
#include <silkit/services/orchestration/all.hpp>
#include <arpa/inet.h>
#include <fcntl.h>
#include <poll.h>
#include <sys/socket.h>
#include <unistd.h>
#include <atomic>
#include <cerrno>
#include <csignal>
#include <deque>
#include <fstream>
#include <iostream>
#include <map>
#include <mutex>
#include <sstream>
#include <stdexcept>
#include <thread>

namespace Can = SilKit::Services::Can;
namespace Orch = SilKit::Services::Orchestration;
using Clock = std::chrono::steady_clock;
constexpr size_t QueueLimit = 256;
volatile std::sig_atomic_t interrupted = 0;
void signal_handler(int) { interrupted = 1; }

struct Event {
    enum Kind { Receive, Acknowledge, Peer, Invalid } kind = Invalid;
    Vmcu::Frame frame;
    uintptr_t ticket = 0;
    uint32_t status = 0;
    int64_t timestamp = 0;
    bool running = false;
};
struct Ingress {
    std::mutex mutex;
    std::deque<Event> queue;
    std::atomic<bool> overflow{false}, ready{false};
    void push(Event event) {
        std::lock_guard<std::mutex> guard(mutex);
        if (queue.size() == QueueLimit) { overflow = true; return; }
        queue.push_back(std::move(event));
    }
    bool pop(Event& event) {
        std::lock_guard<std::mutex> guard(mutex);
        if (queue.empty()) return false;
        event = std::move(queue.front()); queue.pop_front(); return true;
    }
};
uint32_t silkit_flags(uint8_t flags) {
    uint32_t value = 0;
    if (flags & Vmcu::Ide) value |= uint32_t(Can::CanFrameFlag::Ide);
    if (flags & Vmcu::Rtr) value |= uint32_t(Can::CanFrameFlag::Rtr);
    if (flags & Vmcu::Fdf) value |= uint32_t(Can::CanFrameFlag::Fdf);
    if (flags & Vmcu::Brs) value |= uint32_t(Can::CanFrameFlag::Brs);
    if (flags & Vmcu::Esi) value |= uint32_t(Can::CanFrameFlag::Esi);
    return value;
}
bool copy_frame(const Can::CanFrame& src, Vmcu::Frame& dst) {
    constexpr uint32_t mask = uint32_t(Can::CanFrameFlag::Ide) | uint32_t(Can::CanFrameFlag::Rtr) |
        uint32_t(Can::CanFrameFlag::Fdf) | uint32_t(Can::CanFrameFlag::Brs) | uint32_t(Can::CanFrameFlag::Esi);
    if (src.flags & ~mask || src.dlc > 15 || src.dataField.size() > 64) return false;
    dst.id = src.canId; dst.dlc = uint8_t(src.dlc); dst.length = uint8_t(src.dataField.size());
    if (src.flags & uint32_t(Can::CanFrameFlag::Ide)) dst.flags |= Vmcu::Ide;
    if (src.flags & uint32_t(Can::CanFrameFlag::Rtr)) dst.flags |= Vmcu::Rtr;
    if (src.flags & uint32_t(Can::CanFrameFlag::Fdf)) dst.flags |= Vmcu::Fdf;
    if (src.flags & uint32_t(Can::CanFrameFlag::Brs)) dst.flags |= Vmcu::Brs;
    if (src.flags & uint32_t(Can::CanFrameFlag::Esi)) dst.flags |= Vmcu::Esi;
    if (!Vmcu::valid_can(dst)) return false;
    std::copy(src.dataField.begin(), src.dataField.end(), dst.data.begin());
    return true;
}

class Connection {
    int fd = -1;
    sockaddr_in address{};
    bool connecting = false;
    Clock::time_point retry{};
    std::deque<std::array<uint8_t, Vmcu::WireSize>> outgoing;
    size_t sent = 0;
public:
    Vmcu::Decoder decoder;
    uint64_t generation = 0;
    bool connected = false;
    explicit Connection(const std::string& endpoint) {
        auto split = endpoint.find(':');
        if (split == std::string::npos || endpoint.substr(0, split) != "127.0.0.1")
            throw std::runtime_error("QEMU endpoint must be 127.0.0.1:PORT");
        const std::string port = endpoint.substr(split + 1);
        size_t end = 0; auto number = std::stoul(port, &end);
        if (end != port.size() || !number || number > 65535) throw std::runtime_error("Invalid QEMU port");
        address.sin_family = AF_INET; address.sin_port = htons(uint16_t(number));
        inet_pton(AF_INET, "127.0.0.1", &address.sin_addr);
    }
    ~Connection() { close_peer(); }
    void close_peer() {
        if (fd >= 0) close(fd);
        fd = -1; connecting = connected = false; decoder.reset(); outgoing.clear(); sent = 0;
        retry = Clock::now() + std::chrono::milliseconds(100);
    }
    void send(const Vmcu::Frame& frame) {
        if (!connected) return;
        if (outgoing.size() == QueueLimit) throw std::runtime_error("QEMU output queue overflow");
        outgoing.push_back(Vmcu::encode(frame));
    }
    template<class Handler> void poll(Handler handler) {
        if (fd < 0 && Clock::now() >= retry) {
            fd = socket(AF_INET, SOCK_STREAM | SOCK_NONBLOCK | SOCK_CLOEXEC, 0);
            if (fd < 0) throw std::runtime_error("socket failed");
            int result = connect(fd, reinterpret_cast<sockaddr*>(&address), sizeof(address));
            if (result < 0 && errno != EINPROGRESS) { close_peer(); return; }
            connecting = true;
        }
        if (fd < 0) return;
        if (connecting) {
            pollfd p{fd, POLLOUT, 0};
            if (::poll(&p, 1, 0) <= 0) return;
            int error = 0; socklen_t length = sizeof(error);
            if (getsockopt(fd, SOL_SOCKET, SO_ERROR, &error, &length) || error) { close_peer(); return; }
            connecting = false; connected = true; ++generation;
        }
        for (unsigned batch = 0; batch < 8; ++batch) {
            std::array<uint8_t, 4096> bytes;
            auto count = recv(fd, bytes.data(), bytes.size(), 0);
            if (count > 0) decoder.feed(bytes.data(), size_t(count), handler);
            else if (count == 0 || (errno != EAGAIN && errno != EWOULDBLOCK && errno != EINTR)) {
                close_peer(); return;
            } else break;
        }
        for (unsigned batch = 0; batch < 8 && !outgoing.empty(); ++batch) {
            auto& frame = outgoing.front();
            auto count = ::send(fd, frame.data() + sent, frame.size() - sent, MSG_NOSIGNAL);
            if (count > 0) {
                sent += size_t(count);
                if (sent == frame.size()) { sent = 0; outgoing.pop_front(); }
            } else if (count < 0 && errno != EAGAIN && errno != EWOULDBLOCK && errno != EINTR) {
                close_peer(); return;
            } else break;
        }
    }
};

struct Options {
    std::string role = "bridge", registry = "silkit://127.0.0.1:8500", endpoint;
    std::string name, network = "VehicleCAN", peer, config, events;
    uint64_t duration = 0, period = 0;
    bool input = false, allow_actuation = false, echo_fixture = false;
};
Options options(int argc, char** argv) {
    Options o;
    for (int i = 1; i < argc; ++i) {
        std::string key = argv[i];
        if (key == "--stdin") { o.input = true; continue; }
        if (key == "--allow-actuation") { o.allow_actuation = true; continue; }
        if (key == "--echo-fixture") { o.echo_fixture = true; continue; }
        if (key == "--help") {
            std::cout << "vmcu-silkit --role bridge|restbus --registry-uri URI [--qemu-endpoint 127.0.0.1:PORT] "
                "[--name NAME] [--network VehicleCAN] [--require-peer NAME] [--config YAML] "
                "[--events JSONL] [--duration-ms N] [--period-ms N] [--stdin] [--echo-fixture] [--allow-actuation]\n"
                "stdin: send ID FLAGS DLC HEX | command OP ARG | status | quit\n";
            std::exit(0);
        }
        if (++i == argc) throw std::runtime_error("Missing option argument");
        std::string value = argv[i];
        if (key == "--role") o.role = value;
        else if (key == "--registry-uri") o.registry = value;
        else if (key == "--qemu-endpoint") o.endpoint = value;
        else if (key == "--name") o.name = value;
        else if (key == "--network") o.network = value;
        else if (key == "--require-peer") o.peer = value;
        else if (key == "--config") o.config = value;
        else if (key == "--events") o.events = value;
        else if (key == "--duration-ms" || key == "--period-ms") {
            size_t end; auto number = std::stoull(value, &end);
            if (end != value.size() || value.empty() || value[0] == '-') throw std::runtime_error("Invalid duration");
            (key == "--duration-ms" ? o.duration : o.period) = number;
        } else throw std::runtime_error("Unknown option: " + key);
    }
    if (o.role != "bridge" && o.role != "restbus") throw std::runtime_error("Invalid role");
    if (o.name.empty()) o.name = o.role == "bridge" ? "TC397CanBridge" : "VehicleRestbus";
    if (o.role == "bridge" && o.endpoint.empty()) throw std::runtime_error("Bridge requires --qemu-endpoint");
    return o;
}

int run(const Options& o) {
    auto ingress = std::make_shared<Ingress>();
    auto configuration = o.config.empty()
        ? SilKit::Config::ParticipantConfigurationFromString("{\"Logging\":{\"Sinks\":[{\"Type\":\"Stdout\",\"Level\":\"Warn\"}]}}")
        : SilKit::Config::ParticipantConfigurationFromFile(o.config);
    auto participant = SilKit::CreateParticipant(configuration, o.name, o.registry);
    auto* lifecycle = participant->CreateLifecycleService({Orch::OperationMode::Autonomous});
    auto* controller = participant->CreateCanController(o.role == "bridge" ? "VMCU_CAN0" : "Vehicle_CAN0", o.network);
    auto* monitor = participant->CreateSystemMonitor();
    const auto receive_id = controller->AddFrameHandler([ingress](Can::ICanController*, const Can::CanFrameEvent& ev) {
        Event event; event.kind = copy_frame(ev.frame, event.frame) ? Event::Receive : Event::Invalid;
        event.timestamp = ev.timestamp.count(); ingress->push(event);
    }, static_cast<SilKit::Services::DirectionMask>(SilKit::Services::TransmitDirection::RX));
    const auto ack_id = controller->AddFrameTransmitHandler([ingress](Can::ICanController*, const Can::CanFrameTransmitEvent& ev) {
        Event event; event.kind = Event::Acknowledge;
        event.frame.id = ev.canId;
        // userContext is a never-dereferenced monotonic opaque handle, not an
        // address of a queued frame or an object with a callback lifetime.
        event.ticket = reinterpret_cast<uintptr_t>(ev.userContext);
        event.timestamp = ev.timestamp.count();
        event.status = ev.status == Can::CanTransmitStatus::Transmitted ? Vmcu::Transmitted :
            ev.status == Can::CanTransmitStatus::Canceled ? Vmcu::Canceled : Vmcu::QueueFull;
        ingress->push(event);
    });
    const auto peer_id = monitor->AddParticipantStatusHandler([ingress, &o](const Orch::ParticipantStatus& status) {
        if (status.participantName != o.peer) return;
        Event event; event.kind = Event::Peer; event.running = status.state == Orch::ParticipantState::Running;
        ingress->push(event);
    });
    monitor->SetParticipantDisconnectedHandler([ingress, &o](const Orch::ParticipantConnectionInformation& info) {
        if (info.participantName == o.peer) { Event event; event.kind = Event::Peer; ingress->push(event); }
    });
    lifecycle->SetCommunicationReadyHandler([controller, ingress] {
        controller->SetBaudRate(500000, 2000000, 0); controller->Start(); ingress->ready = true;
    });
    auto final_state = lifecycle->StartLifecycle();
    std::unique_ptr<Connection> connection;
    if (o.role == "bridge") connection.reset(new Connection(o.endpoint));
    std::ofstream file;
    if (!o.events.empty()) { file.open(o.events); if (!file) throw std::runtime_error("Cannot open event log"); }
    auto log = [&](const std::string& type, const Vmcu::Frame& f = {}, int64_t timestamp = 0) {
        std::ostringstream line;
        line << "{\"event\":\"" << type << "\",\"id\":" << f.id << ",\"flags\":" << unsigned(f.flags)
             << ",\"dlc\":" << unsigned(f.dlc) << ",\"length\":" << unsigned(f.length)
             << ",\"data\":\"" << Vmcu::hex(f) << "\",\"epoch\":" << f.epoch << ",\"token\":" << f.token
             << ",\"status\":" << f.status << ",\"silkit_ns\":" << timestamp << "}";
        std::cout << line.str() << std::endl;
        if (file) file << line.str() << std::endl;
    };
    struct Pending { Vmcu::Frame frame; uint64_t generation; Clock::time_point deadline; };
    std::map<uintptr_t, Pending> pending;
    uintptr_t next_ticket = 1;
    uint32_t epoch = 0, cycle = 0;
    uint32_t vehicle_epoch = 0, vehicle_cookie = 0, command_sequence = 0;
    std::string input_line;
    bool input_eof = false, quit = false;
    struct StdinFlags {
        int saved = -1;
        explicit StdinFlags(bool enable) {
            if (enable) { saved = fcntl(STDIN_FILENO, F_GETFL); if (saved >= 0) fcntl(STDIN_FILENO, F_SETFL, saved | O_NONBLOCK); }
        }
        ~StdinFlags() { if (saved >= 0) fcntl(STDIN_FILENO, F_SETFL, saved); }
    } stdin_flags(o.input);
    bool active = false, peer_running = o.peer.empty(), announced = false;
    uint64_t generation = 0, rejected = 0;
    auto start = Clock::now(), next_period = start;
    auto acknowledge = [&](const Vmcu::Frame& frame, uint32_t status) {
        Vmcu::Frame ack; ack.type = Vmcu::Ack; ack.epoch = frame.epoch;
        ack.token = frame.token; ack.status = status; connection->send(ack);
    };
    auto send_can = [&](const Vmcu::Frame& frame, uintptr_t ticket) {
        Can::CanFrame can{}; can.canId = frame.id; can.flags = silkit_flags(frame.flags); can.dlc = frame.dlc;
        can.dataField = SilKit::Util::Span<const uint8_t>(frame.data.data(), frame.length);
        controller->SendFrame(can, reinterpret_cast<void*>(ticket));
        log("silkit_tx", frame);
    };
    while (!interrupted && !quit && (!o.duration || Clock::now() - start < std::chrono::milliseconds(o.duration))) {
        if (ingress->overflow) throw std::runtime_error("SIL Kit callback queue overflow");
        if (final_state.wait_for(std::chrono::milliseconds(0)) == std::future_status::ready)
            throw std::runtime_error("SIL Kit lifecycle terminated unexpectedly");
        if (ingress->ready && !announced) { log("participant_ready"); announced = true; }
        Event event;
        while (ingress->pop(event)) {
            if (event.kind == Event::Peer) {
                peer_running = event.running;
                if (!peer_running) vehicle_epoch = vehicle_cookie = command_sequence = 0;
                log(peer_running ? "peer_running" : "peer_unavailable");
            }
            else if (event.kind == Event::Invalid) log("invalid_silkit_rx");
            else if (event.kind == Event::Acknowledge) {
                auto item = pending.find(event.ticket);
                if (item == pending.end()) {
                    if (!event.ticket) { event.frame.status = event.status; log("restbus_ack", event.frame, event.timestamp); }
                    else log("late_ack_discarded");
                    continue;
                }
                auto frame = item->second.frame; frame.status = event.status;
                log("silkit_ack", frame, event.timestamp);
                if (connection && connection->connected && item->second.generation == connection->generation && frame.epoch == epoch && active)
                    acknowledge(frame, event.status);
                else log("stale_ack_discarded", frame);
                pending.erase(item);
            } else if (event.kind == Event::Receive) {
                log("silkit_rx", event.frame, event.timestamp);
                if (!connection && event.frame.id == 0x510 &&
                    (event.frame.flags & (Vmcu::Fdf | Vmcu::Ide | Vmcu::Rtr)) == Vmcu::Fdf &&
                    event.frame.length == 32 && event.frame.data[0] == 1) {
                    const auto e = Vmcu::get32(&event.frame.data[4]);
                    const auto cookie = Vmcu::get32(&event.frame.data[8]);
                    if (vehicle_epoch != e || vehicle_cookie != cookie) command_sequence = 0;
                    vehicle_epoch = e; vehicle_cookie = cookie;
                    command_sequence = std::max(command_sequence, Vmcu::get32(&event.frame.data[24]));
                }
                if (connection) {
                    if (active && connection->connected && peer_running) {
                        event.frame.type = Vmcu::Rx; event.frame.epoch = epoch;
                        connection->send(event.frame);
                    } else log("rx_discarded_inactive", event.frame);
                } else if (o.echo_fixture && ingress->ready && peer_running &&
                           (event.frame.id == 0x123 || event.frame.id == 0x1abcde)) {
                    event.frame.id = event.frame.id == 0x123 ? 0x321 : 0x1abcdf;
                    send_can(event.frame, 0);
                }
            }
        }
        if (connection) {
            connection->poll([&](const Vmcu::Frame& frame) {
                if (frame.type == Vmcu::Control) {
                    epoch = frame.epoch; active = frame.status == 1; generation = connection->generation;
                    log(active ? "controller_started" : "controller_stopped", frame); return;
                }
                if (frame.type != Vmcu::Tx) { log("unexpected_wire_type", frame); return; }
                if (!active || frame.epoch != epoch || generation != connection->generation) { log("stale_tx_discarded", frame); return; }
                if (!ingress->ready || !peer_running) { acknowledge(frame, Vmcu::Error); log("tx_peer_unavailable", frame); return; }
                if (pending.size() == QueueLimit) { acknowledge(frame, Vmcu::QueueFull); log("tx_queue_full", frame); return; }
                for (const auto& p : pending) if (p.second.generation == generation && p.second.frame.epoch == epoch && p.second.frame.token == frame.token) {
                    log("duplicate_tx_discarded", frame); return;
                }
                if (!next_ticket) throw std::runtime_error("CAN callback handle exhausted");
                const uintptr_t ticket = next_ticket++;
                pending.emplace(ticket, Pending{frame, generation, Clock::now() + std::chrono::seconds(2)});
                send_can(frame, ticket);
            });
            if (!connection->connected) { active = false; epoch = 0; }
            if (rejected != connection->decoder.rejected) {
                rejected = connection->decoder.rejected;
                Vmcu::Frame diagnostics; diagnostics.status = uint32_t(std::min<uint64_t>(rejected, UINT32_MAX));
                log("wire_rejected", diagnostics);
            }
        } else if (ingress->ready && peer_running && o.period && Clock::now() >= next_period) {
            Vmcu::Frame frame; frame.id = 0x700; frame.dlc = frame.length = 8;
            Vmcu::put32(frame.data.data(), ++cycle); send_can(frame, 0);
            next_period = Clock::now() + std::chrono::milliseconds(o.period);
        }
        if (o.input && !input_eof) {
            std::array<char, 512> bytes;
            auto count = read(STDIN_FILENO, bytes.data(), bytes.size());
            if (!count) input_eof = true;
            if (count > 0) for (ssize_t i = 0; i < count; ++i) {
                if (bytes[i] == '\r') continue;
                if (bytes[i] != '\n') {
                    if (input_line.size() == 2048) throw std::runtime_error("stdin command too long");
                    input_line += bytes[i]; continue;
                }
                try {
                    std::istringstream command(input_line); std::string verb; command >> verb;
                    auto number = [](const std::string& text) -> uint32_t {
                        size_t end; auto v = std::stoull(text, &end, 0);
                        if (text.empty() || text[0] == '-' || end != text.size() || v > UINT32_MAX) throw std::runtime_error("Invalid integer");
                        return uint32_t(v);
                    };
                    if (verb == "quit") quit = true;
                    else if (verb == "status") {
                        Vmcu::Frame f; f.epoch = vehicle_epoch; f.token = vehicle_cookie; f.status = peer_running;
                        log("restbus_status", f);
                    } else if (verb == "send" || verb == "command") {
                        if (connection) throw std::runtime_error("stdin CAN injection is a Restbus operation");
                        if (!ingress->ready || !peer_running) throw std::runtime_error("CAN participant not ready");
                        Vmcu::Frame f;
                        std::string a, b, c, d, extra;
                        if (verb == "send") {
                            if (!(command >> a >> b >> c >> d) || (command >> extra)) throw std::runtime_error("send ID FLAGS DLC HEX");
                            f.id = number(a); const auto flags = number(b), dlc = number(c);
                            if (flags > 31 || dlc > 15) throw std::runtime_error("Invalid flags or DLC");
                            f.flags = uint8_t(flags); f.dlc = uint8_t(dlc);
                            if (d == "-") d.clear();
                            if (d.size() > 128 || d.size() % 2) throw std::runtime_error("Invalid payload length");
                            f.length = uint8_t(d.size() / 2);
                            for (unsigned j = 0; j < f.length; ++j) f.data[j] = uint8_t(number("0x" + d.substr(2 * j, 2)));
                            if (f.id == 0x600) throw std::runtime_error("Use session-checked command for vehicle actuation");
                        } else {
                            if (!(command >> a >> b) || (command >> extra)) throw std::runtime_error("command OP ARG");
                            auto op = number(a), arg = number(b);
                            if (op < 1 || op > 7 || (op >= 5 && !o.allow_actuation)) throw std::runtime_error("Operation not allowed (5..7 require --allow-actuation)");
                            if (!vehicle_epoch || !vehicle_cookie) throw std::runtime_error("No current vMCU telemetry session");
                            if (++command_sequence == 0) throw std::runtime_error("Command sequence exhausted");
                            f.id = 0x600; f.flags = Vmcu::Fdf; f.dlc = 12; f.length = 24;
                            f.data[0] = 1; f.data[1] = uint8_t(op);
                            Vmcu::put32(&f.data[4], vehicle_epoch); Vmcu::put32(&f.data[8], vehicle_cookie);
                            Vmcu::put32(&f.data[12], command_sequence); Vmcu::put32(&f.data[16], arg);
                        }
                        if (!Vmcu::valid_can(f)) throw std::runtime_error("Invalid CAN frame");
                        send_can(f, 0);
                    } else throw std::runtime_error("Unknown stdin command");
                } catch (const std::exception& error) {
                    log("command_rejected"); std::cerr << "command: " << error.what() << '\n';
                }
                input_line.clear();
            }
        }
        for (auto it = pending.begin(); it != pending.end();) {
            if (Clock::now() < it->second.deadline) { ++it; continue; }
            auto& p = it->second;
            if (connection && connection->connected && p.generation == connection->generation && p.frame.epoch == epoch && active)
                acknowledge(p.frame, Vmcu::Error);
            log("ack_timeout", p.frame); it = pending.erase(it);
            // The monotonically increasing handle is never reused: a later SDK
            // callback cannot alias a fresh request after reset or reconnect.
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(2));
    }
    if (connection) connection->close_peer();
    controller->RemoveFrameHandler(receive_id); controller->RemoveFrameTransmitHandler(ack_id);
    monitor->RemoveParticipantStatusHandler(peer_id); monitor->SetParticipantDisconnectedHandler({});
    controller->Stop(); lifecycle->Stop("Apollo vMCU runner stopped");
    if (final_state.wait_for(std::chrono::seconds(3)) != std::future_status::ready)
        throw std::runtime_error("SIL Kit lifecycle shutdown timed out");
    final_state.get(); participant.reset(); log("stopped"); return 0;
}
int main(int argc, char** argv) {
    std::signal(SIGINT, signal_handler); std::signal(SIGTERM, signal_handler);
    try { return run(options(argc, argv)); }
    catch (const std::exception& error) { std::cerr << "vmcu-silkit: " << error.what() << '\n'; return 1; }
}
