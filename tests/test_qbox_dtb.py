from __future__ import annotations

import json
from pathlib import Path
import subprocess

import pytest

from scripts.run.qbox_dtb import deployment_dtb, read_dtb_config, resolve_cpu_count


def test_missing_or_unpopulated_manifest_keeps_legacy_selection(tmp_path):
    expected = tmp_path / "apollo-qvp-saturn-v.dtb"
    assert deployment_dtb(tmp_path, "nexios-image") == expected
    (tmp_path / "nexios-image-apollo-qvp.qboxconf").write_text("{}")
    assert deployment_dtb(tmp_path, "nexios-image") == expected
    assert resolve_cpu_count(None, None, expected) == 4
    assert resolve_cpu_count(2, None, expected) == 2


@pytest.mark.parametrize("key", ["ap_dtb", "dtb"])
def test_manifest_selects_its_named_dtb_without_guessing_from_existing_files(tmp_path, key):
    conf = tmp_path / "nexios-image-apollo-qvp.qboxconf"
    conf.write_text(json.dumps({"images": {key: "selected-4cpus.dtb"},
                                "env": {"QBOX_APOLLO_NUM_CPUS": "4"}}))
    (tmp_path / "apollo-qvp-saturn-v.dtb").write_bytes(b"stale")
    assert read_dtb_config(conf) == (tmp_path / "selected-4cpus.dtb", 4)
    assert deployment_dtb(tmp_path, "nexios-image") == tmp_path / "selected-4cpus.dtb"


@pytest.mark.parametrize("value", ["../outside.dtb", "/outside.dtb", 4])
def test_manifest_rejects_invalid_dtb_paths(tmp_path, value):
    conf = tmp_path / "invalid.qboxconf"
    conf.write_text(json.dumps({"images": {"dtb": value}}))
    with pytest.raises(ValueError, match="safe relative path"):
        read_dtb_config(conf)


def test_cpu_override_requires_matching_explicit_dtb(tmp_path):
    dtb = tmp_path / "cpu16.dtb"
    source = '/dts-v1/; / { cpus { ' + " ".join(
        f'cpu@{cpu:x} {{ device_type = "cpu"; }};' for cpu in range(16)
    ) + ' }; };'
    subprocess.run(["dtc", "-I", "dts", "-O", "dtb", "-o", str(dtb)],
                   input=source, text=True, capture_output=True, check=True)
    with pytest.raises(ValueError, match="image manifest selects 4"):
        resolve_cpu_count(16, 4, dtb)
    assert resolve_cpu_count(16, 4, dtb, explicit_dtb=True) == 16
    with pytest.raises(ValueError, match="describes 16 CPUs; requested 4"):
        resolve_cpu_count(None, 4, dtb)


def test_manifest_default_cpu_population_is_used(tmp_path):
    dtb = tmp_path / "cpu4.dtb"
    source = '/dts-v1/; / { cpus { ' + " ".join(
        f'cpu@{cpu:x} {{ device_type = "cpu"; }};' for cpu in range(4)
    ) + ' }; };'
    subprocess.run(["dtc", "-I", "dts", "-O", "dtb", "-o", str(dtb)],
                   input=source, text=True, capture_output=True, check=True)
    assert resolve_cpu_count(None, 4, dtb) == 4
