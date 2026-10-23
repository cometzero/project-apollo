#
# SPDX-FileCopyrightText: <text>Copyright 2025 Arm Limited
# and/or its affiliates <open-source-office@arm.com></text>
#
# SPDX-License-Identifier: MIT
#

import logging

logger = logging.getLogger(__name__)

PLATFORM_REGISTRY = {}


def register_platform(kind):
    """
    Decorator to register a factory for platform under the given kind.

    :param kind: Platform kind (e.g., ``"fvp"``, ``"fpga"``).
    :returns: Decorator that registers the factory and returns it unchanged.
    """
    kind = str(kind).lower().strip()

    def _wrap(fn):
        PLATFORM_REGISTRY[kind] = fn
        logger.debug("Registered platform type=%s via %s", kind, fn)
        return fn

    return _wrap


def get_factory(kind):
    """
    Fetch a registered platform factory by kind.

    :param kind: Platform kind (case-insensitive).
    :returns: Registered factory callable, or ``None`` if not found.
    """
    return PLATFORM_REGISTRY.get(str(kind).lower().strip())


class DriverBundle:
    """
    Container for a platform instance.

    :param driver: Platform driver instance with ``start()``, ``wait_ready()``,
        ``stop()`` (and optionally ``init()``).
    :param manager: Optional session/console manager
     (e.g., telnet, ssh, serial).
    :param login_primary: Optional callable for logging into the primary.
    :param export_env: Optional callable for exporting environment variables.

    :ivar driver: Platform driver instance.
    :ivar manager: Session/console manager object.
    :ivar login_primary: Callable for primary console login.
    :ivar export_env: Callable for exporting environment variables.
    """

    def __init__(
        self, driver, manager=None, login_primary=None, export_env=None
    ) -> None:
        self.driver = driver
        self.manager = manager
        self.login_primary = login_primary
        self.export_env = export_env
