# SPDX-FileCopyrightText: <text>Copyright 2026 Arm Limited
# and/or its affiliates <open-source-office@arm.com></text>
#
# SPDX-License-Identifier: MIT
"""
Abstract base for networking/session managers used by targets.

This is intentionally minimal so that existing FVP (TelnetSessionManager)
and new FPGA (SSHSessionManager) can adopt it with very small changes.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional
from types import SimpleNamespace


class BaseNetworkManager(ABC):
    """
    Base interface for target networking/session managers.

    """

    # ----------------
    # Target lifecycle
    # ----------------

    @abstractmethod
    def connect(self) -> None:
        """
        Establish underlying connections/sessions.

        """
        raise NotImplementedError

    @abstractmethod
    def disconnect(self) -> None:
        """
        Tear down all underlying sessions, connections and file handles.

        """
        raise NotImplementedError

    # ---- optional hooks ----

    def set_log_dir(self, path: str) -> None:
        """
        Optional hook to change the base directory used for logs.

        """
        return

    def execute_simple_command(
        self,
        command: str,
        options: Optional[SimpleNamespace] = None,
        **kwargs,
    ) -> int:
        """
        Optional generic "run one shell command" hook.

        Subclasses may override this to run a command and return its exit
        code. Provide structured settings via ``options``; ``**kwargs`` is
        available for backward-compatible extras.

        :param command: Shell command to execute.
        :param options: Optional settings namespace.
        :param kwargs: Legacy/extra keyword arguments accepted for backward
            compatibility.
        :returns: Command exit code.
        :raises NotImplementedError: If not implemented by subclass.
        """
        # allow legacy args via kwargs for compatibility.
        raise NotImplementedError(
            f"{self.__class__.__name__} does not implement "
            "execute_simple_command()"
        )
