from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
import json
import os
from typing import Protocol

from .profiles import FvpTapNetwork


SELECTED_SUITES_ENV = "APOLLO_VALIDATION_TEST_SUITES"
SELECTED_KIND_ENV = "APOLLO_VALIDATION_OEQA_KIND"
SELECTED_TARGET_ENV = "APOLLO_VALIDATION_TEST_TARGET"
SELECTED_FVP_CONFIG_ENV = "APOLLO_VALIDATION_FVP_CONFIG"
SELECTED_FVP_TAP_NETWORK_ENV = "APOLLO_VALIDATION_FVP_TAP_NETWORK"
BITBAKE_PASSTHROUGH_ENV = "BB_ENV_PASSTHROUGH_ADDITIONS"


class SelectedTest(Protocol):
    @property
    def oeqa_kind(self) -> str | None: ...

    @property
    def ordered_tests(self) -> tuple[str, ...]: ...

    @property
    def test_target(self) -> str | None: ...

    @property
    def fvp_config(self) -> tuple[tuple[str, str], ...]: ...

    @property
    def fvp_tap_network(self) -> FvpTapNetwork | None: ...


@contextmanager
def selected_test_environment(selection: SelectedTest | None) -> Iterator[None]:
    keys = (
        SELECTED_SUITES_ENV,
        SELECTED_KIND_ENV,
        SELECTED_TARGET_ENV,
        SELECTED_FVP_CONFIG_ENV,
        SELECTED_FVP_TAP_NETWORK_ENV,
        BITBAKE_PASSTHROUGH_ENV,
    )
    previous = {key: os.environ.get(key) for key in keys}
    try:
        if selection is not None and selection.oeqa_kind is not None:
            os.environ[SELECTED_SUITES_ENV] = json.dumps(selection.ordered_tests)
            os.environ[SELECTED_KIND_ENV] = selection.oeqa_kind
        if selection is not None and selection.test_target is not None:
            os.environ[SELECTED_TARGET_ENV] = selection.test_target
        if selection is not None and selection.fvp_config:
            os.environ[SELECTED_FVP_CONFIG_ENV] = json.dumps(
                dict(selection.fvp_config), sort_keys=True
            )
            passthrough = set((previous[BITBAKE_PASSTHROUGH_ENV] or "").split())
            passthrough.add(SELECTED_FVP_CONFIG_ENV)
            os.environ[BITBAKE_PASSTHROUGH_ENV] = " ".join(sorted(passthrough))
        else:
            os.environ.pop(SELECTED_FVP_CONFIG_ENV, None)
        if selection is not None and selection.fvp_tap_network is not None:
            os.environ[SELECTED_FVP_TAP_NETWORK_ENV] = json.dumps(
                selection.fvp_tap_network.as_json(), sort_keys=True
            )
            passthrough = set((os.environ.get(BITBAKE_PASSTHROUGH_ENV) or "").split())
            passthrough.add(SELECTED_FVP_TAP_NETWORK_ENV)
            os.environ[BITBAKE_PASSTHROUGH_ENV] = " ".join(sorted(passthrough))
        else:
            os.environ.pop(SELECTED_FVP_TAP_NETWORK_ENV, None)
        yield
    finally:
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
