#
# SPDX-FileCopyrightText: <text>Copyright 2025 Arm Limited and/or its
# affiliates <open-source-office@arm.com></text>
#
# SPDX-License-Identifier: MIT

import logging

logger = logging.getLogger(__name__)


class AutoTestPlatformBase:
    """
    Base helpers and common attributes for automated platform tests.

    :ivar mgr: Telnet/session manager used to resolve console ports.
    :ivar platform: Platform name (lowercased) from config.
    :ivar cli_platform: Platform name provided via CLI (lowercased).
    :ivar target: Target kind from config.
    :ivar config_data: Raw platform configuration dictionary.
    :ivar rse_port: Port handle for the RSE console.
    :ivar scp_port: Port handle for the SCP console.
    :ivar default_console: Port handle for the default/primary console.
    :ivar secure_world_ap_console: Port handle for the Secure World AP console.
    :ivar si_cluster0: Port handle for Safety Island cluster 0.
    :ivar si_cluster1: Port handle for Safety Island cluster 1.
    :ivar si_cluster2: Port handle for Safety Island cluster 2.
    """

    def __init__(self, telnet_mgr, platform_config: dict, cli_platform: str):
        """
        Initialize base platform using telnet manager and configuration.

        :param telnet_mgr: Manager object exposing ports/sessions.
        :param platform_config: Platform configuration dictionary.
        :param cli_platform: Platform name provided via CLI(optional override).
        :returns: None.
        """

        self.mgr = telnet_mgr
        self.platform = platform_config.get("name", "").lower()
        self.cli_platform = (cli_platform or "").lower()
        self.target = str(platform_config.get("target", "fvp")).lower()
        logger.info(
            "Tests are running on Platform: %s and Target: %s",
            self.platform,
            self.target,
        )
        self.config_data = platform_config
        self.rse_port = self.mgr.get_port(self.config_data["port_map"]["rse"])
        self.scp_port = self.mgr.get_port(self.config_data["port_map"]["scp"])
        self.default_console = self.mgr.get_port(
            self.config_data["port_map"]["default_console"]
        )
        self.secure_world_ap_console = self.mgr.get_port(
            self.config_data["port_map"]["secure_world_ap_console"]
        )
