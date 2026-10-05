#!/usr/bin/env python3
"""Exercise a running owned board through the public dashboard HTTP API.

The caller chooses disruptive actions explicitly with --action. Credentials are
read locally and never included in evidence. No failed mutation is retried.
"""
import argparse
import base64
import json
from pathlib import Path
import time
import urllib.error
import urllib.request
import uuid
import xml.etree.ElementTree as ET


class Client:
    def __init__(self, url, password_file=None):
        self.url = url.rstrip("/")
        self.authorization = None
        if password_file:
            password = Path(password_file).read_text().strip()
            self.authorization = "Basic " + base64.b64encode(("autosd:" + password).encode()).decode()

    def request(self, path, payload=None, headers=None, authenticated=True):
        merged = {"Authorization": self.authorization} if authenticated and self.authorization else {}
        merged.update(headers or {})
        if payload is not None:
            merged["Content-Type"] = "application/json"
        request = urllib.request.Request(self.url + path,
            data=json.dumps(payload).encode() if payload is not None else None, headers=merged)
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                body = response.read()
                return response.status, json.loads(body) if "json" in response.headers.get("Content-Type", "") else body
        except urllib.error.HTTPError as error:
            return error.code, json.loads(error.read())

    def get(self, path):
        code, data = self.request(path)
        if code != 200:
            raise RuntimeError(f"GET {path}: {code} {data}")
        return data

    def job(self, action, arguments=None, timeout=1000):
        state = self.get("/api/board")
        body = {"action": action, "args": arguments or {}, "run_id": state["run_id"],
                "request_id": uuid.uuid4().hex, "confirm_disruptive": True}
        headers = {"X-CSRF-Token": state["csrf_token"]}
        status, data = self.request("/api/jobs", body, headers)
        if status != 202:
            raise RuntimeError(f"job {action} rejected: {status} {data}")
        job = data["job"]
        # The identical request must return the same job without another mutation.
        again, duplicate = self.request("/api/jobs", body, headers)
        if again != 202 or duplicate["job"]["id"] != job["id"]:
            raise RuntimeError("request idempotency failed")
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            job = self.get("/api/board/jobs/" + job["id"])["job"]
            if job["status"] not in ("RUNNING", "QUEUED"):
                return job
            time.sleep(.5)
        raise TimeoutError("job deadline exceeded: " + job["id"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True)
    parser.add_argument("--password-file", type=Path, help="Only for servers with login enabled")
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--action", action="append", default=[], help='ACTION or ACTION={"op":1,"arg":0}')
    parser.add_argument("--ready-timeout", type=float, default=900)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    client = Client(args.url, args.password_file)
    report = {"url": args.url, "checks": [], "jobs": [], "verdict": "FAIL"}
    def write():
        (args.out_dir / "result.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    def check(name, passed, **evidence):
        report["checks"].append(dict(name=name, passed=bool(passed), **evidence))
        write()
        if not passed:
            raise AssertionError(name)
    try:
        check("authentication-required" if args.password_file else "login-free-access",
              client.request("/api/board", authenticated=False)[0] == (401 if args.password_file else 200))
        check("untrusted-host", client.request("/api/board", headers={"Host": "untrusted.invalid"})[0] == 403)
        check("cross-origin", client.request("/api/board", headers={"Origin": "http://untrusted.invalid"})[0] == 403)
        check("csrf-required", client.request("/api/jobs", {})[0] == 403)
        deadline = time.monotonic() + args.ready_timeout
        while time.monotonic() < deadline:
            state = client.get("/api/board")
            if state["lifecycle"] in ("RUNNING", "FAILED"):
                break
            time.sleep(1)
        check("full-system-boot", state["lifecycle"] == "RUNNING", run_id=state["run_id"], domains=state["domains"])
        token = state.pop("csrf_token")
        report["initial_state"] = state
        check("stale-run-rejected", client.request("/api/jobs", {
            "action": "board.stop", "args": {}, "run_id": "previous-run",
            "request_id": uuid.uuid4().hex, "confirm_disruptive": True}, {"X-CSRF-Token": token})[0] == 409)
        graph = client.get("/api/board/topology")
        (args.out_dir / "topology.json").write_text(json.dumps(graph, ensure_ascii=False, indent=2))
        check("source-derived-topology", bool(graph.get("nodes")) and bool(graph.get("edges")),
              nodes=len(graph.get("nodes", [])), edges=len(graph.get("edges", [])), snapshot=graph.get("snapshot"))
        check("drawio-export", ET.fromstring(client.get("/api/topology/drawio")).tag in ("mxfile", "mxGraphModel"))
        for name in ["ap-primary", "ap-secure", "rse", "si-cl0", "si-cl1"] + (["tc397"] if state["vmcu"] else []):
            log = client.get("/api/board/logs/" + name)
            check("uart-" + name, bool(log["text"]) and log["run_id"] == state["run_id"])
        stats = client.get("/api/board/stats")
        if state["stats_enabled"]:
            check("host-load", stats["status"] not in ("STALE", "WARMING_UP", "DISABLED")
                  and stats["latest"]["run_id"] == state["run_id"] and stats["latest"]["threads"] > 0,
                  latest=stats["latest"])
        else:
            check("stats-disabled", stats["status"] == "DISABLED")
        for entry in args.action:
            name, separator, parameters = entry.partition("=")
            job = client.job(name, json.loads(parameters) if separator else {})
            report["jobs"].append(job)
            print(f"{name}: {job['status']}", flush=True)
            write()
            check("job-" + name, job["status"] == "PASS", job_id=job["id"])
        report["verdict"] = "PASS"
    except Exception as error:
        report["error"] = str(error)
        print(str(error), flush=True)
    finally:
        write()
    print(f"{report['verdict']}: {args.out_dir / 'result.json'}", flush=True)
    return 0 if report["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
