#!/usr/bin/env python3
"""Run bounded commands on the private Apollo AutoSD demo VM and save evidence."""
import argparse
import json
from pathlib import Path
import time

import paramiko


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
    try:
        downloads = parse_downloads(args.download)
    except ValueError as error:
        parser.error(str(error))
    args.out.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    client = paramiko.SSHClient()
    # This endpoint is a disposable locally launched VM, never a remote host.
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    result = {"command": args.command, "port": args.port, "status": "ERROR"}
    code = 1
    try:
        client.connect("127.0.0.1", port=args.port, username="root", password="password",
                       look_for_keys=False, allow_agent=False, timeout=args.connect_timeout,
                       banner_timeout=args.connect_timeout, auth_timeout=args.connect_timeout)
        if args.upload:
            with client.open_sftp() as transfer:
                for item in args.upload:
                    source, destination = item.split(":", 1)
                    transfer.put(source, destination)
        channel = client.get_transport().open_session(timeout=args.connect_timeout)
        channel.set_combine_stderr(True)
        channel.exec_command(args.command)
        with (args.out / "console.log").open("wb", buffering=0) as output:
            while True:
                if channel.recv_ready():
                    data = channel.recv(65536)
                    output.write(data)
                    print(data.decode(errors="replace"), end="", flush=True)
                elif channel.exit_status_ready():
                    code = channel.recv_exit_status()
                    result["status"] = "PASS" if code == 0 else "FAIL"
                    break
                elif time.monotonic() - started > args.timeout:
                    code, result["status"] = 124, "TIMEOUT"
                    channel.close()
                    break
                else:
                    time.sleep(.1)
        result["command_returncode"] = code
        if downloads:
            result["downloads"] = []
            with client.open_sftp() as transfer:
                for remote, name in downloads:
                    transfer.get(remote, str(args.out / name))
                    result["downloads"].append({"remote": remote, "file": name})
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
