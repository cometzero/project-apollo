"""Check audio CLI DT selection without launching a platform."""

import importlib.util
import json
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/test/verify_qbox_linux_audio.py"


@pytest.mark.parametrize("selected", [None, "apollo-qvp-saturn-v-4cpus.dtb", "apollo-qvp-saturn-v.dtb"])
@pytest.mark.parametrize("explicit", [False, True])
def test_audio_cli_uses_bsp_selected_dtb(tmp_path, monkeypatch, selected, explicit):
    monkeypatch.syspath_prepend(str(SCRIPT.parent))
    spec = importlib.util.spec_from_file_location("verify_audio_dtb", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, "ROOT", tmp_path)
    deploy = tmp_path / "build/tmp_baremetal/deploy/images/apollo-qvp"
    deploy.mkdir(parents=True)
    if selected:
        (deploy / "nexios-bsp-initramfs-apollo-qvp.qboxconf").write_text(
            json.dumps({"images": {"dtb": selected}}))
    command = [str(SCRIPT), "--out-dir", str(tmp_path / "evidence")]
    override = tmp_path / "profile.dtb"
    if explicit:
        command += ["--dtb", str(override)]
    monkeypatch.setattr(sys, "argv", command)
    args = module.parse_args()
    assert args.dtb == (override if explicit else deploy / (selected or "apollo-qvp-saturn-v.dtb"))
    assert not args.out_dir.exists()
