from nexios_bsp_workflow_support import run_build_dry_run


def test_gem5_selects_only_initramfs(tmp_path):
    result = run_build_dry_run(tmp_path, ["--gem5"])
    assert result.returncode == 0, result.stderr
    assert result.stdout.split()[-1] == "nexios-gem5-initramfs"


def test_gem5_rejects_conflicting_profiles(tmp_path):
    for args in (["--bsp"], ["nexios-image"], ["--machine", "apollo-fvp"]):
        result = run_build_dry_run(tmp_path, ["--gem5", *args])
        assert result.returncode == 2
        assert "--gem5" in result.stderr
