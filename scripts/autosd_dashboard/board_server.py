#!/usr/bin/env python3
"""Saturn-V dashboard; all mutation targets belong to one launcher."""
import argparse
import base64
import fcntl
from http.server import ThreadingHTTPServer
import ipaddress
import json
import math
from pathlib import Path
import signal
import socket
import sys
import threading
from urllib.parse import parse_qs, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parent))
from server import Handler as CommonHandler, access_password
from topology import topology_drawio
from yocto_board import Board, BoardError
from board_io import load

WEB = Path(__file__).resolve().parent / "web"
STATIC = {"/": ("board.html", "text/html; charset=utf-8"),
          "/board.html": ("board.html", "text/html; charset=utf-8"),
          "/board.js": ("board.js", "text/javascript; charset=utf-8"),
          "/board.css": ("board.css", "text/css; charset=utf-8"),
          "/topology.js": ("topology.js", "text/javascript; charset=utf-8")}


class Handler(CommonHandler):
    server_version = "ApolloBoardDashboard/1"

    def log_message(self, format, *args):
        # Polling must not grow an unbounded access log or expose credentials.
        if len(args) > 1 and str(args[1]).startswith(("4", "5")):
            sys.stderr.write("dashboard HTTP " + str(args[1]) + "\n")

    def do_GET(self):
        if not self.safe_request():
            return
        parsed = urlsplit(self.path)
        path, query, app = parsed.path, parse_qs(parsed.query), self.server.app
        try:
            if path in STATIC:
                name, kind = STATIC[path]
                self.send(200, (WEB / name).read_bytes(), kind)
            elif path in ("/api/board", "/api/state"):
                self.send(200, app.state())
            elif path == "/api/board/capabilities":
                self.send(200, {"capabilities": app.catalog()})
            elif path == "/api/board/stats":
                stats = app.stats()
                limit = int(query.get("limit", [120])[0])
                after = int(query.get("after", [-1])[0])
                if not 1 <= limit <= 120 or after < -1:
                    raise BoardError("invalid stats cursor/limit")
                stats["samples"] = [x for x in stats["samples"] if x.get("seq", 0) > after][-limit:]
                self.send(200, stats)
            elif path in ("/api/board/topology", "/api/topology", "/api/topology/drawio"):
                graph = app.topology()
                if path.endswith("drawio"):
                    self.send(200, topology_drawio(graph).encode(), "application/xml",
                              {"Content-Disposition": 'attachment; filename="saturn-v.drawio"'})
                else:
                    self.send(200, graph)
            elif path == "/api/board/logs":
                self.send(200, app.logs())
            elif path.startswith("/api/board/logs/"):
                identifier = path.removeprefix("/api/board/logs/")
                self.send(200, app.log(identifier, query.get("cursor", [""])[0], int(query.get("limit", [65536])[0])))
            elif path == "/api/board/scenarios":
                self.send(200, {"scenarios": app.catalog()})
            elif path.startswith("/api/board/jobs/"):
                identifier = path.removeprefix("/api/board/jobs/")
                with app.lock:
                    job = next((j for j in app.jobs if j["id"] == identifier), None)
                if not job:
                    raise KeyError(identifier)
                self.send(200, {"job": job})
            elif path == "/api/board/evidence":
                self.send(200, app.evidence()[1])
            elif path.startswith("/api/board/evidence/"):
                identifier = path.removeprefix("/api/board/evidence/")
                filename = app.evidence()[0][identifier]
                if not app.directory:
                    raise KeyError(identifier)
                target = app.directory / filename
                if target.is_symlink() or not target.is_file():
                    raise KeyError(identifier)
                if target.stat().st_size > 16 * 1024 * 1024:
                    raise BoardError("artifact exceeds 16 MiB HTTP download limit")
                self.send(200, target.read_bytes(), "application/octet-stream",
                          {"Content-Disposition": f'attachment; filename="{filename}"'})
            elif path == "/api/simulator/snapshot":
                self.send(200, app.collector.snapshot() if app.collector else {"status": "STARTING"})
            elif path == "/api/simulator/capabilities":
                self.send(200, app.collector.capabilities() if app.collector else {"features": {}})
            elif path == "/api/simulator/objects":
                if not app.collector or app.active_job:
                    raise BoardError("diagnostics unavailable during operation or startup", 409)
                self.send(200, app.collector.objects(query.get("parent", [""])[0]))
            elif path == "/api/simulator/qmp":
                if not app.diagnostics or app.active_job:
                    raise BoardError("diagnostics unavailable during operation or startup", 409)
                self.send(200, app.diagnostics.query(query.get("domain", ["ap"])[0], query.get("command", ["query-status"])[0]))
            else:
                raise KeyError(path)
        except BoardError as error:
            self.send(error.status, {"error": str(error)})
        except KeyError:
            self.send(404, {"error": "unknown resource"})
        except (ValueError, TypeError) as error:
            self.send(400, {"error": str(error)})
        except (OSError, RuntimeError) as error:
            self.send(503, {"error": str(error), "status": "UNAVAILABLE"})

    def do_POST(self):
        if not self.safe_request(mutation=True):
            return
        if self.path != "/api/jobs":
            self.send(404, {"error": "unknown action endpoint"})
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 1 <= size <= 4096 or self.headers.get("Content-Type", "").split(";")[0] != "application/json":
                raise BoardError("expected JSON body, maximum 4096 bytes")
            self.connection.settimeout(5)
            payload = json.loads(self.rfile.read(size))
            self.send(202, {"job": self.server.app.start_job(payload)})
        except BoardError as error:
            self.send(error.status, {"error": str(error)})
        except (ValueError, OSError) as error:
            self.send(400, {"error": str(error)})


def default_addresses():
    addresses = ["127.0.0.1"]
    try:
        # UDP connect selects a local route; it sends no packet.
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("192.0.2.1", 9))
            candidate = sock.getsockname()[0]
            if candidate not in addresses:
                addresses.append(candidate)
    except OSError:
        pass
    return addresses


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--launch-spec", type=Path, required=True)
    parser.add_argument("--listen", action="append")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--password-file", type=Path, help="Enable login (default: no login required)")
    parser.add_argument("--boot-timeout", type=float, default=900)
    args = parser.parse_args(argv)
    if not 1024 <= args.port <= 65535 or not math.isfinite(args.boot_timeout) or args.boot_timeout <= 0:
        parser.error("use an unprivileged port and a finite positive boot timeout")
    addresses = list(dict.fromkeys(str(ipaddress.IPv4Address(value)) for value in (args.listen or default_addresses())))
    if "0.0.0.0" in addresses:
        parser.error("use exact local IPv4 addresses")
    spec = load(args.launch_spec)
    base = Path(spec["out_dir"]).resolve()
    base.mkdir(parents=True, exist_ok=True, mode=0o700)
    password_path = args.password_file
    password = access_password(password_path) if password_path else None
    servers, started_servers, app = [], [], None
    stop = threading.Event()
    with (base / "dashboard.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            hosts = {f"{address}:{args.port}" for address in addresses}
            if "127.0.0.1" in addresses:
                hosts.add(f"localhost:{args.port}")
            # Bind every listener before a VM is started.
            for address in addresses:
                server = ThreadingHTTPServer((address, args.port), Handler)
                server.daemon_threads = True
                server.allowed_hosts = hosts
                server.authorization = ("Basic " + base64.b64encode(("autosd:" + password).encode()).decode()) if password else None
                servers.append(server)
            app = Board(args.launch_spec, args.boot_timeout)
            for server in servers:
                server.app = app
                threading.Thread(target=server.serve_forever, daemon=True).start()
                started_servers.append(server)
                print(f"Apollo dashboard: http://{server.server_address[0]}:{args.port}", flush=True)
            print(f"Login user: autosd; password file: {password_path}" if password_path else "Access: no login required", flush=True)
            if len(addresses) == 1 and addresses[0] == "127.0.0.1":
                print("External access: no LAN listener configured", flush=True)
            for sig in (signal.SIGTERM, signal.SIGINT):
                signal.signal(sig, lambda *_: stop.set())
            app.start_job({"action": "board.start", "args": {}, "run_id": None, "request_id": "launcher-auto-boot"})
            stop.wait()
        finally:
            try:
                if app:
                    app.close()
            finally:
                for server in servers:
                    if server in started_servers:
                        server.shutdown()
                    server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
