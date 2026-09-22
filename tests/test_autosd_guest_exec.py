from pathlib import Path
import sys

import pytest

pytest.importorskip("paramiko")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.autosd_demo.guest_exec import parse_downloads


def test_download_names_are_scoped_to_new_output_directory():
    assert parse_downloads(["/var/tmp/evidence.tar.gz:evidence.tar.gz"]) == [
        ("/var/tmp/evidence.tar.gz", "evidence.tar.gz")
    ]


@pytest.mark.parametrize("item", [
    "missing-separator", "/remote:../escape", "/remote:/absolute", "/remote:.",
    "/remote:..", "/remote:console.log", "/remote:result.json", "/remote:", ":name",
])
def test_download_rejects_paths_and_reserved_outputs(item):
    with pytest.raises(ValueError):
        parse_downloads([item])


def test_download_rejects_duplicate_names():
    with pytest.raises(ValueError, match="Duplicate"):
        parse_downloads(["/first:same.tar", "/second:same.tar"])
