from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
PSA_HELPER = (
    ROOT
    / "hsoc-stack/yocto/meta-hsoc-auto-solutions/lib/oeqa/utils"
    / "apollo_psa_validation.py"
)
CRYPTO_HELPER = (
    ROOT
    / "hsoc-stack/yocto/meta-hsoc-auto-solutions/lib/oeqa/utils"
    / "apollo_crypto_validation.py"
)


def _module(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _summary(total: int = 10, passed: int = 10) -> str:
    return "\n".join(
        (
            "************ Crypto Suite Report **********",
            f"TOTAL TESTS     : {total}",
            f"TOTAL PASSED    : {passed}",
            "TOTAL SIM ERROR : 0",
            "TOTAL FAILED    : 0",
            f"TOTAL SKIPPED   : {total - passed}",
        )
    )


def test_parse_psa_summary_accepts_complete_numeric_report() -> None:
    # Given: a complete real-suite shaped PSA report.
    # When: summary validation parses it.
    summary = _module(PSA_HELPER).parse_psa_summary(_summary())

    # Then: all numeric totals are retained.
    assert summary == {"tests": 10, "passed": 10, "sim_error": 0, "failed": 0, "skipped": 0}


def test_parse_psa_summary_accepts_console_crlf_report() -> None:
    # Given: the CRLF-formatted report emitted by the real serial console.
    # When: summary validation parses it.
    summary = _module(PSA_HELPER).parse_psa_summary(_summary().replace("\n", "\r\n"))

    # Then: numeric totals remain valid across console line endings.
    assert summary["tests"] == 10


@pytest.mark.parametrize(
    "output",
    ("TOTAL", _summary(total=0, passed=0), _summary().replace("TOTAL FAILED    : 0", "TOTAL FAILED    : 1")),
)
def test_parse_psa_summary_rejects_incomplete_or_failing_report(output: str) -> None:
    # Given: bare, zero-test, or failed PSA output.
    # When/Then: it cannot claim complete conformance success.
    with pytest.raises(ValueError):
        _module(PSA_HELPER).parse_psa_summary(output)


def test_parse_psa_summary_rejects_duplicate_total() -> None:
    # Given: otherwise-valid output with an ambiguous duplicate total.
    # When/Then: the duplicate is rejected instead of silently selecting one.
    with pytest.raises(ValueError):
        _module(PSA_HELPER).parse_psa_summary(_summary() + "\nTOTAL TESTS     : 10")


@pytest.mark.parametrize(
    "extra",
    (
        "TOTAL TESTS : nope",
        "TOTAL ERRORS : 1",
        "TOTAL FOO : 99",
        "total tests : 10",
        "TOTAL PASSED : 10 trailing",
    ),
)
def test_parse_psa_summary_rejects_every_malformed_or_unknown_total_record(
    extra: str,
) -> None:
    # Given: a valid report followed by an unrecognized TOTAL record.
    # When/Then: the whole summary is rejected rather than ignoring the record.
    with pytest.raises(ValueError):
        _module(PSA_HELPER).parse_psa_summary(_summary() + f"\n{extra}")


def _samples(real: tuple[float, ...], user: tuple[float, ...]):
    return tuple(
        {"real": real[index], "user": user[index], "sys": 0.01}
        for index in range(len(real))
    )


def test_crypto_samples_accept_stable_meaningful_improvement() -> None:
    # Given: the observed FVP-shaped enabled and disabled timing samples.
    # When: FVP performance validation evaluates their medians.
    result = _module(CRYPTO_HELPER).validate_crypto_samples(
        _samples((0.117, 0.117, 0.117), (0.022, 0.024, 0.019)),
        _samples((0.360, 0.360, 0.360), (0.239, 0.282, 0.215)),
    )

    # Then: both timing dimensions have a meaningful stable improvement.
    assert result["real"] == (0.117, 0.360)
    assert result["user"] == (0.022, 0.239)


def test_crypto_samples_accept_quantized_fvp_user_cpu_time() -> None:
    # Given: valid FVP user CPU samples quantized at the 10ms scale.
    # When: real and user stability are evaluated with their own bounds.
    result = _module(CRYPTO_HELPER).validate_crypto_samples(
        _samples((0.117, 0.117, 0.117), (0.011, 0.011, 0.021)),
        _samples((0.360, 0.360, 0.360), (0.191, 0.282, 0.239)),
    )

    # Then: the meaningful FVP acceleration is accepted.
    assert result["user"] == (0.011, 0.239)


def test_crypto_samples_accept_user_spread_at_two_point_five() -> None:
    # Given: user samples on the named 2.5x boundary.
    # When/Then: they pass the inclusive user CPU spread contract.
    _module(CRYPTO_HELPER).validate_crypto_samples(
        _samples((0.1, 0.1, 0.1), (0.01, 0.01, 0.025)),
        _samples((0.2, 0.2, 0.2), (0.1, 0.1, 0.25)),
    )


def test_crypto_samples_reject_user_spread_above_two_point_five() -> None:
    # Given: user samples beyond the named 2.5x boundary.
    # When/Then: the timing evidence fails closed.
    with pytest.raises(ValueError):
        _module(CRYPTO_HELPER).validate_crypto_samples(
            _samples((0.1, 0.1, 0.1), (0.01, 0.01, 0.026)),
            _samples((0.2, 0.2, 0.2), (0.1, 0.1, 0.26)),
        )


@pytest.mark.parametrize(
    "enabled,disabled",
    (
        (_samples((0.1, 100.0, 0.1), (0.1, 100.0, 0.1)), _samples((0.101, 0.102, 100.0), (0.101, 0.102, 100.0))),
        (_samples((0.1, 0.1, 0.1), (0.101, 0.101, 0.101)), _samples((0.1, 0.1, 0.1), (0.101, 0.101, 0.101))),
        (_samples((0.2, 0.2, 0.2), (0.2, 0.2, 0.2)), _samples((0.1, 0.1, 0.1), (0.1, 0.1, 0.1))),
    ),
)
def test_crypto_samples_reject_noisy_near_equal_or_inverted_results(
    enabled: tuple[dict[str, float], ...],
    disabled: tuple[dict[str, float], ...],
) -> None:
    # Given: noisy, near-equal, or inverted performance measurements.
    # When/Then: FVP-only timing validation fails closed.
    with pytest.raises(ValueError):
        _module(CRYPTO_HELPER).validate_crypto_samples(enabled, disabled)


def test_crypto_samples_reject_nonfinite_or_insufficient_data() -> None:
    # Given: invalid timing values or fewer than three samples.
    # When/Then: neither can establish crypto performance.
    with pytest.raises(ValueError):
        _module(CRYPTO_HELPER).validate_crypto_samples(
            _samples((0.1, 0.1), (0.1, 0.1)),
            _samples((0.2, 0.2), (0.2, 0.2)),
        )
    with pytest.raises(ValueError):
        _module(CRYPTO_HELPER).validate_crypto_samples(
            _samples((float("nan"), 0.1, 0.1), (0.1, 0.1, 0.1)),
            _samples((0.2, 0.2, 0.2), (0.2, 0.2, 0.2)),
        )
