from __future__ import annotations

from pathlib import Path

from apollo_validation.profiles import (
    CpuCountMismatch,
    load_test_profile,
    required_cpu_count_mismatch,
)
from apollo_validation.provenance import ProvenanceRequest, _runtime_path


WORKSPACE = Path(__file__).resolve().parents[2]


def test_mbpp_four_cpu_context_is_explicitly_not_applicable() -> None:
    profile = load_test_profile(WORKSPACE, "mbpp", "fvp", "product")

    mismatch = required_cpu_count_mismatch(profile, 4)

    assert mismatch == CpuCountMismatch(required=16, actual=4)
    assert mismatch is not None
    assert mismatch.reason == "not_applicable_cpu_count"


def test_mbpp_sixteen_cpu_context_satisfies_requirement() -> None:
    profile = load_test_profile(WORKSPACE, "mbpp", "fvp", "product")

    assert required_cpu_count_mismatch(profile, 16) is None


def test_mbpp_provenance_uses_the_isolated_tmpdir(tmp_path: Path) -> None:
    build_dir = tmp_path / "build/validation/apollo-fvp-16"
    conf = build_dir / "conf"
    conf.mkdir(parents=True)
    (conf / "local.conf").write_text(
        'TMPDIR = "${TOPDIR}/tmp_mbpp16"\n', encoding="utf-8"
    )
    request = ProvenanceRequest(
        root=tmp_path,
        build_dir=Path("build/validation/apollo-fvp-16"),
        backend="fvp",
        machine="apollo-fvp",
        image="nexios-image",
        image_profile="product",
        profile_id="mbpp",
        selectors=("test_73_power_mbpp",),
        cpu_count=16,
    )

    path = _runtime_path(request, "wic")

    assert path == (
        build_dir
        / "tmp_mbpp16/deploy/images/apollo-fvp/nexios-image-apollo-fvp.wic"
    )
