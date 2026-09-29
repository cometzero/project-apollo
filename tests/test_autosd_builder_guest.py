"""Reject mutable or foreign builder references before touching guest disks."""
from pathlib import Path
import subprocess

import pytest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/autosd_demo/builder_guest.sh"


@pytest.mark.parametrize("image", ["latest", "quay.io/centos-sig-automotive/automotive-image-builder:latest",
                                 "example.com/image@sha256:" + "a" * 64,
                                 "quay.io/centos-sig-automotive/automotive-image-builder@sha256:bad"])
def test_reject_unpinned_builder_before_guest_operations(image):
    result = subprocess.run(["bash", str(SCRIPT), image], capture_output=True, text=True)
    assert result.returncode == 2
    assert "Expected a digest-pinned official AIB image" in result.stderr


def test_shell_syntax():
    subprocess.run(["bash", "-n", str(SCRIPT)], check=True)
