from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
from threading import Thread
from typing import Final


RESPONSE_BODY: Final = b"APOLLO_QBOX_NET_OK"
REQUEST_PATH: Final = "/apollo-qbox-net"
GUEST_ENDPOINT: Final = "http://10.0.2.100:18080/apollo-qbox-net"


@dataclass(frozen=True, slots=True)
class NetworkForward:
    host_port: int
    guest_endpoint: str = GUEST_ENDPOINT


def _append_event(log_path: Path, event: str, status: int) -> None:
    record = {
        "event": event,
        "owner_pid": os.getpid(),
        "status": status,
    }
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(record, sort_keys=True) + "\n")


def _handler(log_path: Path) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            status = 200 if self.path == REQUEST_PATH else 404
            body = RESPONSE_BODY if status == 200 else b""
            self.send_response(status)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            _append_event(log_path, "request-served", status)

        def log_message(
            self,
            _format: str,
            *_args: str | int,
        ) -> None:
            return

    return Handler


@contextmanager
def platform_network_server(log_path: Path) -> Iterator[NetworkForward]:
    server = ThreadingHTTPServer(("127.0.0.1", 0), _handler(log_path))
    thread = Thread(target=server.serve_forever, name="qbox-platform-http")
    thread.start()
    _append_event(log_path, "server-started", 0)
    try:
        yield NetworkForward(server.server_port)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5.0)
        _append_event(log_path, "server-stopped", 0 if not thread.is_alive() else 1)
