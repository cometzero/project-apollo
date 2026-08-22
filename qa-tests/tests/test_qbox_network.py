from __future__ import annotations

import json
from pathlib import Path
import socket

from apollo_validation.qbox_runner import platform_network_server


def _request(port: int, path: str) -> bytes:
    with socket.create_connection(("127.0.0.1", port), timeout=1.0) as stream:
        stream.sendall(
            f"GET {path} HTTP/1.0\r\nHost: 10.0.2.100\r\n\r\n".encode()
        )
        response = bytearray()
        while chunk := stream.recv(4096):
            response.extend(chunk)
    return bytes(response)


def test_platform_network_server_serves_exact_body_and_cleans_up(
    tmp_path: Path,
) -> None:
    log_path = tmp_path / "network.jsonl"

    with platform_network_server(log_path) as forward:
        assert forward.guest_endpoint == (
            "http://10.0.2.100:18080/apollo-qbox-net"
        )
        response = _request(forward.host_port, "/apollo-qbox-net")
        assert response.endswith(b"APOLLO_QBOX_NET_OK")
        host_port = forward.host_port

    with socket.socket() as probe:
        assert probe.connect_ex(("127.0.0.1", host_port)) != 0
    records = [json.loads(line) for line in log_path.read_text().splitlines()]
    assert [record["event"] for record in records] == [
        "server-started",
        "request-served",
        "server-stopped",
    ]


def test_platform_network_server_rejects_wrong_path(tmp_path: Path) -> None:
    with platform_network_server(tmp_path / "network.jsonl") as forward:
        response = _request(forward.host_port, "/wrong")

    assert b" 404 " in response
    assert not response.endswith(b"APOLLO_QBOX_NET_OK")
