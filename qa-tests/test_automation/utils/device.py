#
# SPDX-FileCopyrightText: <text>Copyright 2025 Arm Limited and/or its
# affiliates <open-source-office@arm.com></text>
#
# SPDX-License-Identifier: MIT

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Optional

# ---------------------------
# Abstract device API
# ---------------------------


class Device(ABC):
    """
    Abstract device manager API required for both local and
    hardware farm device connections.

    :returns: None.
    """

    @abstractmethod
    def init(self) -> None:
        """
        Prepare resources but do not power on/run yet.

        :returns: None.
        """

    @abstractmethod
    def start(self) -> None:
        """
        Power on the DUT.

        :returns: None.
        """

    @abstractmethod
    def stop(self) -> None:
        """
        Power off the DUT and clean up the resources.

        :returns: None.
        """

    @abstractmethod
    def reset(self) -> None:
        """
        Power cycle DUT. Power on and off as per the current state.

        :returns: None.
        """

    @abstractmethod
    def wait_ready(self, timeout_s: Optional[int] = None) -> None:
        """
        Block until the DUT is ready (e.g., exported telnet ports detected).

        :returns: None.
        """

    @abstractmethod
    def is_running(self) -> bool:
        """
        True if the model is alive.

        :returns: ``True`` if the device is running, else ``False``.
        """

    @abstractmethod
    def get_ports(self) -> Dict[str, int]:
        """
        Return discovered terminal name -> telnet port mappings.

        :returns: Dictionary mapping terminal names to telnet port numbers.
        """

    @abstractmethod
    def log_path(self) -> Path:
        """
        Return path to the primary boot log.

        :returns: Path object pointing to the boot log file.
        """
