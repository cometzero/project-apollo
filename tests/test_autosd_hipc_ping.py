import importlib.util
from pathlib import Path
import socket
import struct
import subprocess
import unittest
import os
import tempfile

spec = importlib.util.spec_from_file_location("probe", Path(__file__).resolve().parents[1] / "scripts/autosd_demo/hipc_ping.py")
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)


class ProbeTests(unittest.TestCase):
    def packet(self, identifier=123, sequence=2, payload=b"odd"):
        icmp = struct.pack("!BBHHH", 0, 0, 0, identifier, sequence) + payload
        icmp = icmp[:2] + struct.pack("!H", probe.checksum(icmp)) + icmp[4:]
        ip = struct.pack("!BBHHHBBH4s4s", 0x45, 0, 20 + len(icmp), 1, 0, 64, 1, 0,
                         socket.inet_aton("192.168.1.1"), socket.inet_aton("192.168.1.2"))
        ip = ip[:10] + struct.pack("!H", probe.checksum(ip)) + ip[12:]
        return ip + icmp

    def valid(self, packet):
        return probe.valid_reply(packet, "192.168.1.1", "192.168.1.2", 123, 2, b"odd")

    def test_known_checksum(self):
        self.assertEqual(probe.checksum(bytes.fromhex("0001f203f4f5f6f7")), 0x220d)
        self.assertEqual(probe.checksum(b"a"), 0x9eff)

    def test_request_checksum(self):
        message = probe.echo_request(123, 2, b"odd")
        self.assertEqual(message[0], 8)
        self.assertEqual(probe.checksum(message), 0)

    def test_valid_reply(self):
        self.assertTrue(self.valid(self.packet()))

    def test_identity_and_payload(self):
        for kwargs in ({"identifier": 124}, {"sequence": 3}, {"payload": b"bad"}):
            self.assertFalse(self.valid(self.packet(**kwargs)))

    def test_corruption_and_truncation(self):
        packet = self.packet()
        for position in (0, 6, 10, 12, 20, len(packet) - 1):
            damaged = bytearray(packet)
            damaged[position] ^= 1
            self.assertFalse(self.valid(bytes(damaged)))
        for length in range(len(packet)):
            self.assertFalse(self.valid(packet[:length]))

    def test_source_destination_are_checked(self):
        for offset in (12, 16):
            packet = bytearray(self.packet())
            packet[offset:offset + 4] = socket.inet_aton("192.168.1.9")
            packet[10:12] = b"\0\0"
            packet[10:12] = struct.pack("!H", probe.checksum(bytes(packet[:20])))
            self.assertFalse(self.valid(bytes(packet)))

    def test_temporary_connection_cleanup_contract(self):
        script = Path(__file__).resolve().parents[1] / "scripts/autosd_demo/check_hipc_link.sh"
        subprocess.run(["sh", "-n", str(script)], check=True)
        source = script.read_text()
        self.assertIn("set -eu", source)
        self.assertIn("connection add save no", source)
        self.assertIn("connection.autoconnect no", source)
        self.assertIn('trial_created=1', source)
        self.assertNotIn('connection show uuid', source)
        self.assertIn('connection delete uuid "$trial_uuid"', source)
        self.assertIn("trap cleanup EXIT", source)
        self.assertIn("test ! -e /sys/class/net/ethsi1.200", source)
        self.assertNotIn("connection delete id", source)

    def test_cleanup_success_and_failures_with_mock_nmcli(self):
        script = Path(__file__).resolve().parents[1] / "scripts/autosd_demo/check_hipc_link.sh"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "ifindex").write_text("4")
            (root / "probe.py").write_text("")
            source = script.read_text().replace("/sys/class/net/ethsi1/ifindex", str(root / "ifindex"))
            source = source.replace("/sys/class/net/ethsi1.200", str(root / "absent"))
            mocks = r'''
id() { echo 0; }
python3() {
    if [ "$1" = -c ]; then echo test-owned-uuid; else return "$PROBE_RC"; fi
}
nmcli() {
    printf '%s\n' "$*" >> "$CALLS"
    case "$*" in
        *"connection add"*) return "$ADD_RC";;
        *"connection delete"*) return "$DELETE_RC";;
        *"connection show"*) return 10;;
    esac
    return 0
}
'''
            for add, probe_rc, delete, expected in ((0, 0, 0, 0), (0, 1, 0, 1),
                                                     (0, 0, 10, 1), (10, 0, 0, 1)):
                calls = root / f"calls-{add}-{probe_rc}-{delete}"
                env = dict(os.environ, ADD_RC=str(add), PROBE_RC=str(probe_rc),
                           DELETE_RC=str(delete), CALLS=str(calls))
                result = subprocess.run(["sh", "-c", mocks + source, "trial", str(root / "probe.py")],
                                        env=env, text=True, capture_output=True, timeout=5)
                self.assertEqual(result.returncode, expected, result.stderr)
                recorded = calls.read_text()
                self.assertEqual("connection delete uuid test-owned-uuid" in recorded, add == 0)
                self.assertNotIn("connection show", recorded)
                if delete:
                    self.assertIn("HIPC_TRIAL_CLEANUP_FAILED", result.stderr)
                if add:
                    self.assertIn("HIPC_TRIAL_CREATE_UNCONFIRMED", result.stderr)


if __name__ == "__main__":
    unittest.main()
