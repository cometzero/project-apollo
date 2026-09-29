"""Exercise the private RT package workflow without touching host packages."""
from pathlib import Path
import subprocess

SCRIPT = Path(__file__).resolve().parents[1] / "autosd/customization/rt/prepare-guest.sh"


def invoke(dnf_status=0, machine="aarch64"):
    # All mutating/system-inspection commands are shell functions. Do not run
    # this script against the host's package manager or Podman daemon.
    prelude = r'''
id() { echo 0; }
uname() { echo MACHINE; }
getenforce() { echo Enforcing; }
podman() {
    if [[ $1 == inspect ]]; then echo /usr/lib/qm/rootfs; else return 0; fi
}
timeout() { shift; "$@"; }
dnf() { echo "DNF $*"; return DNF_STATUS; }
systemctl() { echo "SYSTEMCTL $*"; }
rpm() { echo "RPM $*"; }
sleep() { :; }
source "$1" install
'''.replace("DNF_STATUS", str(dnf_status)).replace("MACHINE", machine)
    return subprocess.run(["bash", "-c", prelude, "test", str(SCRIPT)],
                          text=True, capture_output=True, timeout=5)


def test_install_stops_qm_for_packages_then_restores_container():
    result = invoke()
    assert result.returncode == 0, result.stderr
    out = result.stdout
    assert out.index("SYSTEMCTL stop qm") < out.index("DNF --installroot")
    assert out.index("DNF --installroot") < out.index("SYSTEMCTL start qm")
    assert "AUTOSD_RT_PACKAGES_INSTALLED" in out


def test_package_failure_is_not_readiness_pass():
    result = invoke(dnf_status=3)
    assert result.returncode == 3
    assert "AUTOSD_RT_PACKAGES_INSTALLED" not in result.stdout
    assert "SYSTEMCTL" not in result.stdout


def test_non_arm_guest_rejected_before_packages():
    result = invoke(machine="x86_64")
    assert result.returncode != 0
    assert "DNF" not in result.stdout
