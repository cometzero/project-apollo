from __future__ import annotations

from pathlib import Path

from pytest import MonkeyPatch

from apollo_validation import runner


def test_profile_preflight_does_not_normalize_before_oeqa(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
) -> None:
    # Given: a profile run whose empty interim summary would be BLOCKED.
    monkeypatch.setattr(runner, "_run_subprocess", lambda *_args, **_kwargs: 0)
    monkeypatch.setattr(runner, "_write_summary", lambda _path: 2)

    # When: the functional runner asks only for prerequisite preflight.
    result = runner.run_basic(
        tmp_path,
        Path("build"),
        "apollo-fvp",
        "nexios-bsp-initramfs",
        300,
        tmp_path / "run",
        False,
        True,
    )

    # Then: OEQA may continue and own profile assertion normalization.
    assert result == 0
