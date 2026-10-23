# SPDX-License-Identifier: MIT
"""QBox factory using the upstream DriverBundle registration contract."""
from test_automation.targets.registry import DriverBundle, register_platform
from .controller import LocalQBox
from .networking import QBoxNetworkManager


def _login_primary(manager, platform_dict):
    manager.login_primary()


@register_platform("qbox")
def make_qbox_bundle(platform_dict, cfg=None):
    manager = QBoxNetworkManager(platform_dict, config=cfg)
    return DriverBundle(driver=LocalQBox(platform_dict, manager), manager=manager,
                        login_primary=_login_primary)
