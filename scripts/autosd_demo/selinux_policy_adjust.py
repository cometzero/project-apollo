#!/usr/bin/env python3
"""Create an explicit, narrow local policy derivative; preserve selcraft output."""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / "build/autosd/demo-selinux-followup"
source = WORK / "policy"
target = WORK / "policy-v1.0.1"
target.mkdir(exist_ok=False)
for name in ("Makefile", "build.sh", "custom-policy-selinux.conf", "custom-policy-selinux.if"):
    shutil.copy2(source / name, target / name)
makefile = (target / "Makefile").read_text()
assert "VERSION=1.0.0" in makefile
(target / "Makefile").write_text(makefile.replace("VERSION=1.0.0", "VERSION=1.0.1", 1))
spec = (source / "custom-policy-selinux.spec").read_text()
assert "Version:\t1.0.0" in spec
(target / "custom-policy-selinux.spec").write_text(spec.replace("Version:\t1.0.0", "Version:\t1.0.1", 1))
contexts = (source / "custom-policy-selinux.fc").read_text()
assert contexts.count("/dev/shm(/.*)?") == 1
(target / "custom-policy-selinux.fc").write_text(contexts.replace("/dev/shm(/.*)?", "/dev/shm/qm(/.*)?"))
policy = (source / "custom-policy-selinux.te").read_text()
assert "policy_module(custom-policy-selinux, 1.0.0)" in policy
policy = policy.replace("policy_module(custom-policy-selinux, 1.0.0)", "policy_module(custom-policy-selinux, 1.0.1)", 1)
policy += """
# Local Apollo validation derivative, not unmodified selcraft output.
# Let the two intentionally unauthorized QM applications reach the IPC resource.
# Their original failures were /dev/null and QM-rootfs traversal denials.
# This does NOT grant any shared_uds_uds_t or named_shm_shm_t permissions.
"""
for domain in ("qm_qm_server_t", "qm_qm_client_other_t"):
    policy += f"allow {domain} qm_file_t:dir search;\n"
    policy += f"allow {domain} qm_file_t:chr_file read;\n"
    policy += f"allow qm_t {domain}:dir search;\n"
(target / "custom-policy-selinux.te").write_text(policy)
print(target)
