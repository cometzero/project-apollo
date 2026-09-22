#!/usr/bin/env python3
"""Verify the recorded base/good/bad automatic-rollback run, without guest writes."""
import argparse
import hashlib
import json
from pathlib import Path
import re


def require(condition, message):
    if not condition:
        raise ValueError(message)


def bootc_records(text):
    decoder = json.JSONDecoder()
    return [decoder.raw_decode(text[match.start():])[0]
            for match in re.finditer(r'\{"apiVersion":"org.containers.bootc/v1"', text)]


def verify_uart(text):
    text = re.sub(r"\x1b\[[0-?]*[ -/]*[@-~]", "", text).replace("\r", "")
    loads = list(re.finditer(r"Loading UKI from partition ukiboot_([ab])", text))
    require([item[1] for item in loads] == ["a", "b"] + ["a"] * 7 + ["b"],
            "Unexpected boot sequence; need base A, good B, seven bad A, recovered B")
    tries = [int(value) for value in re.findall(r"Test booting slot A, tries_remaining: (\d+)", text)]
    require(tries == [7] + list(range(7, 0, -1)), "Bad slot retries were not exhausted in order")
    for index in range(2, 9):
        segment = text[loads[index].start():loads[index + 1].start()]
        require(re.search(r"Failed to start .*System boot check - failure\.", segment),
                "A bad boot did not report the intended health failure")
        require("systemd-shutdown[1]: Rebooting." in segment,
                "A bad boot lacks an automatic shutdown/reboot record")
    return {"loaded_slots": [item[1] for item in loads], "bad_tries": tries[1:],
            "failed_health_boots": 7}


def verify(root):
    def record(name):
        return json.loads((root / name).read_text())

    logs = {}
    for name in ("base-state", "good-state", "rollback-state", "stage-good", "stage-bad",
                 "reboot-good", "reboot-bad", "rollback-history"):
        result = record(name + "/result.json")
        require(result["status"] == "PASS" and result["returncode"] == 0, name + " failed")
        logs[name] = (root / name / "console.log").read_text()
    images = {name: record(name + "-archive/inspect.json") for name in ("base", "good", "bad")}
    digest = {name: image["image_digest"] for name, image in images.items()}
    for phase, image in (("base", "base"), ("good", "good"), ("rollback", "good")):
        state = bootc_records(logs[phase + "-state"])[0]
        require(state["status"]["booted"]["image"]["imageDigest"] == digest[image],
                phase + " booted the wrong image")
        require(f"APOLLO_OTA_{phase}_STATE_PASS" in logs[phase + "-state"], phase + " gate missing")
    for name in ("good", "bad"):
        states = bootc_records(logs["stage-" + name])
        require(len(states) == 2 and states[-1]["status"]["staged"]["image"]["imageDigest"] == digest[name],
                name + " staging digest mismatch")
    final = bootc_records(logs["rollback-state"])[0]
    require(final["spec"]["bootOrder"] == "rollback" and final["status"]["rollbackQueued"],
            "Final bootc state does not report rollback")
    require(final["status"]["rollback"]["image"]["imageDigest"] == digest["bad"], "Bad deployment missing")
    history = logs["rollback-history"]
    for index in range(-7, 0):
        segment = history.split(f"FAILED_BOOT_INDEX={index}\n", 1)[1].split("FAILED_BOOT_INDEX=", 1)[0]
        require("status=1/FAILURE" in segment, "Missing failed-health journal for a boot")
    boot_ids = re.findall(r"^\s*-?\d+ ([0-9a-f]{32}) ", history, re.M)
    require(len(boot_ids) == len(set(boot_ids)) == 10, "Expected ten distinct recorded boots")
    before = record("good-slot-b/inspect.json")
    after = record("rollback-slot-b/inspect.json")
    require(before["sha256"] == after["sha256"], "Good slot changed during rollback")
    bad = record("bad-slot-a-after-rollback/inspect.json")
    modules = "usr/lib/modules/6.18.5-rt3-yocto-preempt-rt/"
    require(bad["sections"][".initrd"]["sha256"] == images["bad"]["files"][modules + "initramfs.img"]["sha256"],
            "Exhausted slot does not contain the bad image initramfs")
    require(bad["kernel_sha256"] == after["kernel_sha256"] == before["kernel_sha256"], "Kernel changed")
    esp = []
    for name in ("base-state", "good-state", "rollback-state"):
        esp.append(re.search(r"([0-9a-f]{64})  /boot/efi/EFI/BOOT/BOOTAA64.EFI", logs[name])[1])
    require(len(set(esp)) == 1, "ESP baseline loader changed")
    uart_path = root / "target-native-session/linux-uart.log"
    uart = uart_path.read_bytes()
    result = verify_uart(uart.decode(errors="replace"))
    result.update(status="PASS", scope="QEMU native EFI bootc good update and automatic health-failure rollback",
                  image_digests=digest, boot_ids=boot_ids, good_slot_sha256=after["sha256"],
                  bad_slot_sha256=bad["sha256"], esp_loader_sha256=esp[0],
                  uart_sha256=hashlib.sha256(uart).hexdigest())
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("evidence", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    result = verify(args.evidence)
    with args.output.open("x") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
