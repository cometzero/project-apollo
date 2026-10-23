from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/test/build_gic720ae_linux_probe_profile.py"


def load_builder():
    spec = importlib.util.spec_from_file_location(SCRIPT.stem, SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def arguments(output: Path) -> argparse.Namespace:
    return argparse.Namespace(
        output_root=output,
        tmpdir=output / "tmp",
        deploy_dir=output / "bitbake-deploy",
        deploy_dir_image=output / "bitbake-deploy/images/apollo-qvp",
        sstate_dir=output / "sstate-cache",
    )


@pytest.mark.parametrize(
    ("field", "path"),
    (
        ("tmpdir", ROOT / "build/tmp_baremetal"),
        ("deploy_dir", ROOT / "build/tmp_baremetal/deploy"),
    ),
)
def test_builder_rejects_active_default_paths(
    tmp_path: Path, field: str, path: Path,
) -> None:
    builder = load_builder()
    args = arguments(tmp_path / "profile")
    setattr(args, field, path)
    with pytest.raises(builder.BuildError) as error:
        builder.validate_isolated_paths(args, ROOT)
    assert error.value.reason == "active_default_path_forbidden"


def test_builder_accepts_only_exact_meta_hsoc_bsp_provider() -> None:
    builder = load_builder()
    expected = (
        ROOT / "hsoc-stack/yocto/meta-hsoc-bsp/recipes-test/"
        "gic720ae-selftest/gic720ae-selftest.bb"
    ).resolve()
    assert builder.verify_provider_path(str(expected), ROOT) == expected
    with pytest.raises(builder.BuildError) as error:
        builder.verify_provider_path(
            str(ROOT / "layers/poky/meta/gic720ae-selftest.bb"), ROOT,
        )
    assert error.value.reason == "unexpected_recipe_provider"


def test_force_clean_removes_only_isolated_deploy_children(
    tmp_path: Path,
) -> None:
    builder = load_builder()
    deploy = tmp_path / "bitbake-deploy"
    deploy.mkdir()
    (deploy / "stale").mkdir()
    (deploy / "stale/file").write_text("stale", encoding="utf-8")
    sibling = tmp_path / "default-deploy-manifest.json"
    sibling.write_text("preserve", encoding="utf-8")

    builder.clear_generated_deploy(deploy)

    assert list(deploy.iterdir()) == []
    assert sibling.read_text(encoding="utf-8") == "preserve"


@pytest.mark.parametrize("name", ["apollo-qvp-saturn-v-4cpus.dtb", "apollo-qvp-saturn-v.dtb"])
def test_probe_uses_kernel_selected_cpu_population(tmp_path, monkeypatch, name):
    builder = load_builder()
    args = arguments(tmp_path / "profile")
    args.package = "gic720ae-selftest"
    args.image = "nexios-bsp-initramfs"
    include = tmp_path / "override.conf"
    builder.write_override(args, include, ROOT)
    assert "KERNEL_DEVICETREE" not in include.read_text()

    def selected(recipe, variable, *unused):
        assert (recipe, variable) == ("linux-yocto-rt", "KERNEL_DEVICETREE")
        return f"hsoc/{name}"

    monkeypatch.setattr(builder, "bitbake_value", selected)
    assert builder.kernel_dtb_path(args, include, ROOT, {}, tmp_path) == args.deploy_dir_image / name


@pytest.mark.parametrize("value", ["", "hsoc/first.dtb hsoc/second.dtb"])
def test_probe_refuses_ambiguous_kernel_dt_selection(tmp_path, monkeypatch, value):
    builder = load_builder()
    monkeypatch.setattr(builder, "bitbake_value", lambda *args: value)
    with pytest.raises(builder.BuildError) as error:
        builder.kernel_dtb_path(arguments(tmp_path), tmp_path / "override.conf", ROOT, {}, tmp_path)
    assert error.value.reason == "ambiguous_kernel_dtb"
