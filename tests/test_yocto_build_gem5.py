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


def test_gem5_zephyr_targets(tmp_path):
    result = run_build_dry_run(tmp_path, ["--gem5-zephyr"])
    assert result.returncode == 0, result.stderr
    assert result.stdout.split()[-4:] == [
        "gem5-native", "zephyr-si-cl1-bench", "zephyr-si-cl1-boot", "gem5-si-cl1-probes"]


def test_gem5_zephyr_conflicts(tmp_path):
    for args in (["--gem5"], ["--bsp"], ["nexios-image"],
                 ["--machine", "apollo-fvp"]):
        result = run_build_dry_run(tmp_path, ["--gem5-zephyr", *args])
        assert result.returncode == 2
        assert "--gem5-zephyr" in result.stderr
