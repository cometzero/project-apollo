#!/usr/bin/env python3
"""Run bounded commands on the private Apollo AutoSD demo VM and save evidence."""
import argparse
import json
import math
from pathlib import Path
import time
import threading

import paramiko


def remaining(deadline, limit=None):
    budget = deadline - time.monotonic()
    if budget <= 0:
        raise TimeoutError("Guest operation exceeded host deadline")
    return min(budget, limit) if limit is not None else budget


def bounded_request(channel, deadline, request_timeout, operation):
    """Paramiko exec/subsystem requests ignore Channel.settimeout().

    Closing the channel releases their internal event wait on expiry.
    """
    expired = threading.Event()

    def expire():
        expired.set()
        channel.close()

    timer = threading.Timer(remaining(deadline, request_timeout), expire)
    timer.daemon = True
    timer.start()
    try:
        try:
            value = operation()
        except Exception as error:
            if expired.is_set():
                raise TimeoutError("SSH channel request exceeded deadline") from error
            raise
        if expired.is_set():
            raise TimeoutError("SSH channel request exceeded deadline")
        return value
    finally:
        timer.cancel()


def open_transfer(client, deadline, request_timeout):
    """Bound both channel creation and the SFTP subsystem request."""
    channel = client.get_transport().open_session(
        timeout=remaining(deadline, request_timeout))
    try:
        channel.settimeout(remaining(deadline, request_timeout))
        bounded_request(channel, deadline, request_timeout,
                        lambda: channel.invoke_subsystem("sftp"))
        channel.settimeout(remaining(deadline, request_timeout))
        return paramiko.SFTPClient(channel)
    except Exception:
        channel.close()
        raise


def transfer_file(transfer, deadline, request_timeout, source, destination, *, download=False):
    channel = transfer.get_channel()

    def progress(transferred, total):
        channel.settimeout(remaining(deadline, request_timeout))

    progress(0, 0)
    if download:
        # Avoid a background prefetch worker outliving the deadline.
        transfer.get(source, destination, callback=progress, prefetch=False)
    else:
        transfer.put(source, destination, callback=progress)
    remaining(deadline)


def parse_downloads(items):
    downloads = []
    for item in items:
        if ":" not in item:
            raise ValueError("Download must use REMOTE:NAME")
        remote, name = item.rsplit(":", 1)
        if not remote or not name or Path(name).name != name or name in (".", "..", "console.log", "result.json"):
            raise ValueError("Download NAME must be a non-reserved filename, not a path")
        if name in [entry[1] for entry in downloads]:
            raise ValueError("Duplicate download filename")
        downloads.append((remote, name))
    return downloads


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=2224)
    parser.add_argument("--command", required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--timeout", type=float, default=300)
    parser.add_argument("--connect-timeout", type=float, default=15,
                        help="SSH connection/channel timeout for slow emulated guests")
    parser.add_argument("--upload", action="append", default=[], metavar="LOCAL:REMOTE")
    parser.add_argument("--download", action="append", default=[], metavar="REMOTE:NAME",
                        help="Fetch evidence into the new output directory after the command")
    args = parser.parse_args()
    if any(not math.isfinite(value) or value <= 0
           for value in (args.timeout, args.connect_timeout)):
        parser.error("timeouts must be finite positive seconds")
    try:
        downloads = parse_downloads(args.download)
    except ValueError as error:
        parser.error(str(error))
    args.out.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    deadline = started + args.timeout
    client = paramiko.SSHClient()
    # This endpoint is a disposable locally launched VM, never a remote host.
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    result = {"command": args.command, "port": args.port, "status": "ERROR"}
    code = 1
    try:
        print(f"[host:ssh] Connecting to private guest 127.0.0.1:{args.port}", flush=True)
        connect_timeout = remaining(deadline, args.connect_timeout)
        client.connect("127.0.0.1", port=args.port, username="root", password="password",
                       look_for_keys=False, allow_agent=False, timeout=connect_timeout,
                       banner_timeout=connect_timeout, auth_timeout=connect_timeout)
        if args.upload:
            with open_transfer(client, deadline, args.connect_timeout) as transfer:
                for item in args.upload:
                    source, destination = item.split(":", 1)
                    print(f"[host:upload] {Path(source).name} -> {destination}", flush=True)
                    transfer_file(transfer, deadline, args.connect_timeout, source, destination)
        channel = client.get_transport().open_session(timeout=remaining(deadline, args.connect_timeout))
        channel.settimeout(remaining(deadline, args.connect_timeout))
        channel.set_combine_stderr(True)
        print("[host:ssh] Starting guest command; stdout/stderr follow", flush=True)
        bounded_request(channel, deadline, args.connect_timeout,
                        lambda: channel.exec_command(args.command))
        with (args.out / "console.log").open("wb", buffering=0) as output:
            while True:
                if time.monotonic() >= deadline:
                    code, result["status"] = 124, "TIMEOUT"
                    channel.close()
                    break
                if channel.recv_ready():
                    data = channel.recv(65536)
                    output.write(data)
                    print(data.decode(errors="replace"), end="", flush=True)
                elif channel.exit_status_ready():
                    code = channel.recv_exit_status()
                    result["status"] = "PASS" if code == 0 else "FAIL"
                    break
                else:
                    time.sleep(.1)
        result["command_returncode"] = code
        print(f"[host:ssh] Guest command finished: {result['status']} rc={code}", flush=True)
        if downloads and result["status"] != "TIMEOUT":
            result["downloads"] = []
            with open_transfer(client, deadline, args.connect_timeout) as transfer:
                for remote, name in downloads:
                    print(f"[host:download] {remote} -> {name}", flush=True)
                    transfer_file(transfer, deadline, args.connect_timeout,
                                  remote, str(args.out / name), download=True)
                    result["downloads"].append({"remote": remote, "file": name})
    except TimeoutError as error:
        code, result["status"] = 124, "TIMEOUT"
        result["error"] = str(error)
        print(error, flush=True)
    except Exception as error:
        code, result["status"] = 1, "ERROR"
        result["error"] = str(error)
        print(error, flush=True)
    finally:
        client.close()
        result.update(returncode=code, elapsed_seconds=time.monotonic() - started)
        (args.out / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
