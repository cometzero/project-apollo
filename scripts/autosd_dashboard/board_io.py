"""Bounded files and console transport for a launcher-owned board run."""
import base64
import json
import os
import re
import stat
import time

ANSI = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
LOGS = {
    "ap-primary": ("AP · Linux", "qbox-primary-console.log"),
    "ap-secure": ("AP · Secure", "qbox-secure-console.log"),
    "rse": ("RSE", "qbox-rse.log"),
    "si-cl0": ("SI CL0 · SCP", "qbox-safety-island-cl0.log"),
    "si-cl1": ("SI CL1 · Zephyr", "qbox-safety-island-cl1.log"),
    "tc397": ("TC397 · Zephyr", "tc397-uart.log"),
    "platform": ("QBox host", "qbox-platform.log"),
    "launcher": ("Board runner", "board-runner.log"),
    "vehicle-can": ("Vehicle CAN", "vehicle-can.jsonl"),
    "tc397-can": ("TC397 CAN", "tc397-can.jsonl"),
    "silkit-bridge": ("SIL Kit bridge", "silkit-bridge.log"),
    "silkit-restbus": ("SIL Kit restbus", "silkit-restbus.log"),
}


def load(path):
    try:
        if path.stat().st_size > 8 * 1024 * 1024:
            return {}
        value = json.loads(path.read_text())
        return value if isinstance(value, dict) else {}
    except (OSError, ValueError):
        return {}


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
    temporary.replace(path)


def tail(path, limit=1024 * 1024):
    try:
        with path.open("rb") as stream:
            stream.seek(max(0, os.fstat(stream.fileno()).st_size - limit))
            return stream.read(limit).decode("utf-8", "replace")
    except OSError:
        return ""


def clean(text):
    return ANSI.sub("", text).replace("\r", "")


def position(path):
    try:
        return path.stat().st_size
    except OSError:
        return 0


def since(path, offset, limit=4 * 1024 * 1024):
    with path.open("rb") as stream:
        size = os.fstat(stream.fileno()).st_size
        if size < offset or size - offset > limit:
            raise RuntimeError("evidence log rotated or exceeded bounded observation window")
        stream.seek(offset)
        return clean(stream.read(limit).decode("utf-8", "replace"))


def records(path, offset=0):
    text = since(path, offset) if offset else tail(path)
    result = []
    for line in text.splitlines():
        try:
            item = json.loads(line)
            if isinstance(item, dict):
                result.append(item)
        except ValueError:
            continue
    return result


def fifo_write(path, text):
    fd = os.open(path, os.O_WRONLY | os.O_NONBLOCK | os.O_NOFOLLOW)
    try:
        info = os.fstat(fd)
        if not stat.S_ISFIFO(info.st_mode) or info.st_uid != os.getuid():
            raise ValueError("console is not an owned FIFO")
        payload = text.encode()
        if len(payload) > 2048 or os.write(fd, payload) != len(payload):
            raise RuntimeError("console write incomplete")
    finally:
        os.close(fd)


def wait_match(path, pattern, offset=0, timeout=15, stopped=lambda: False):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if stopped():
            raise InterruptedError("board operation stopped")
        try:
            match = re.search(pattern, since(path, offset))
            if match:
                return match.group(0)
        except FileNotFoundError:
            pass
        time.sleep(.05)
    raise TimeoutError(f"No matching response in {path.name}: {pattern}")


def fields(line):
    return dict(re.findall(r"([A-Za-z_][A-Za-z_0-9]*)=([^\s]+)", line))


def log_page(directory, run_id, identifier, cursor="", limit=65536):
    if identifier not in LOGS:
        raise KeyError(identifier)
    if not isinstance(limit, int) or not 1 <= limit <= 65536:
        raise ValueError("log limit must be 1..65536")
    path = directory / LOGS[identifier][1]
    if path.is_symlink():
        raise ValueError("symlink log rejected")
    gap, offset, previous = False, 0, None
    if cursor:
        try:
            if len(cursor) > 1024:
                raise ValueError()
            previous = json.loads(base64.urlsafe_b64decode(cursor + "=" * (-len(cursor) % 4)))
            if (not isinstance(previous, list) or len(previous) != 5 or
                    previous[:2] != [run_id, identifier] or type(previous[4]) is not int or previous[4] < 0):
                raise ValueError()
            offset = previous[4]
        except (ValueError, TypeError):
            raise ValueError("invalid or stale log cursor") from None
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    except FileNotFoundError:
        return {"run_id": run_id, "text": "", "next_cursor": "", "gap": False, "status": "WAITING"}
    with os.fdopen(fd, "rb") as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode):
            raise ValueError("log is not a regular file")
        identity = [info.st_dev, info.st_ino]
        if previous and (previous[2:4] != identity or offset > info.st_size):
            offset, gap = 0, True
        if not previous and info.st_size > limit:
            offset, gap = info.st_size - limit, True
        stream.seek(offset)
        chunk = stream.read(limit)
        # Defer a split UTF-8 sequence, but consume invalid bytes with replacement.
        usable = len(chunk)
        try:
            chunk.decode("utf-8")
        except UnicodeDecodeError as error:
            if error.reason == "unexpected end of data" and error.end == len(chunk):
                usable = error.start
        token = base64.urlsafe_b64encode(json.dumps(
            [run_id, identifier, *identity, offset + usable]).encode()).decode().rstrip("=")
        return {"run_id": run_id, "text": clean(chunk[:usable].decode("utf-8", "replace")),
                "next_cursor": token, "gap": gap, "status": "ONLINE"}
