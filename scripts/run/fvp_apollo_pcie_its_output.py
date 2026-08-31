from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import secrets
import stat
from types import TracebackType

from fvp_apollo_pcie_its_types import FvpResult, JsonObject, RunError


def _directory_flags() -> int:
    if not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "O_DIRECTORY"):
        raise RunError("output_path_secure_open_unsupported")
    return os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW


def _open_directory(name: str, parent_fd: int | None = None) -> int:
    try:
        entry = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
    except OSError as error:
        raise RunError("output_path_open_failed", name) from error
    if stat.S_ISLNK(entry.st_mode):
        raise RunError("output_path_symlink", name)
    try:
        return os.open(name, _directory_flags(), dir_fd=parent_fd)
    except OSError as error:
        raise RunError("output_path_open_failed", name) from error


def _open_or_create_directory(name: str, parent_fd: int) -> int:
    for attempt in range(2):
        try:
            os.mkdir(name, 0o700, dir_fd=parent_fd)
        except FileExistsError:
            try:
                return _open_directory(name, parent_fd)
            except RunError:
                if attempt == 0:
                    continue
                raise
        else:
            return _open_directory(name, parent_fd)
    raise RunError("output_path_collision", name)


@dataclass(slots=True)  # noqa: MUTABLE_OK
class StagedOutput:
    """Tracks whether the staged descriptor-relative file has been replaced."""

    directory: OutputDirectory
    temporary_name: str
    filename: str
    replaced: bool = False

    def discard(self) -> None:
        name = self.filename if self.replaced else self.temporary_name
        try:
            os.unlink(name, dir_fd=self.directory.fd)
        except FileNotFoundError:
            return
        except OSError as error:
            raise RunError("output_cleanup_failed", name) from error

    def commit(self) -> None:
        try:
            self.directory.ensure_visible()
            os.replace(
                self.temporary_name,
                self.filename,
                src_dir_fd=self.directory.fd,
                dst_dir_fd=self.directory.fd,
            )
            self.replaced = True
            os.fsync(self.directory.fd)
            self.directory.ensure_visible()
        except RunError:
            self.discard()
            raise
        except OSError as error:
            self.discard()
            raise RunError("output_write_failed", self.filename) from error


@dataclass(slots=True)  # noqa: MUTABLE_OK
class OutputDirectory:
    """Owns one directory FD until close releases that lifecycle resource."""

    path: Path
    fd: int
    device: int
    inode: int

    def __enter__(self) -> OutputDirectory:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()

    def close(self) -> None:
        if self.fd >= 0:
            os.close(self.fd)
            self.fd = -1

    def ensure_visible(self) -> None:
        try:
            visible = os.stat(self.path, follow_symlinks=False)
        except OSError as error:
            raise RunError("output_path_changed", str(self.path)) from error
        if (
            not stat.S_ISDIR(visible.st_mode)
            or visible.st_dev != self.device
            or visible.st_ino != self.inode
        ):
            raise RunError("output_path_changed", str(self.path))

    def stage_json(
        self, payload: JsonObject | FvpResult, filename: str = "result.json"
    ) -> StagedOutput:
        self.ensure_visible()
        temporary_name = f".{filename}.{secrets.token_hex(16)}.tmp"
        data = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
        try:
            temp_fd = os.open(
                temporary_name,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                0o600,
                dir_fd=self.fd,
            )
        except OSError as error:
            raise RunError("output_temp_create_failed", filename) from error
        try:
            written = 0
            while written < len(data):
                written += os.write(temp_fd, data[written:])
            os.fsync(temp_fd)
        except OSError as error:
            try:
                os.unlink(temporary_name, dir_fd=self.fd)
            except OSError as cleanup_error:
                raise RunError("output_cleanup_failed", temporary_name) from cleanup_error
            raise RunError("output_write_failed", filename) from error
        finally:
            os.close(temp_fd)
        return StagedOutput(self, temporary_name, filename)

    def write_json(
        self, payload: JsonObject | FvpResult, filename: str = "result.json"
    ) -> None:
        staged = self.stage_json(payload, filename)
        try:
            staged.commit()
        finally:
            if not staged.replaced:
                staged.discard()

    def create_child(self, name: str) -> OutputDirectory:
        if Path(name).name != name:
            raise RunError("output_path_child_invalid", name)
        self.ensure_visible()
        child_fd = _open_or_create_directory(name, self.fd)
        identity = os.fstat(child_fd)
        return OutputDirectory(
            self.path / name, child_fd, identity.st_dev, identity.st_ino
        )


def parse_output_dir(raw_output: Path, workspace: Path) -> OutputDirectory:
    root = workspace.resolve(strict=True)
    candidate = raw_output if raw_output.is_absolute() else root / raw_output
    if ".." in candidate.parts:
        raise RunError("output_path_traversal", str(raw_output))
    try:
        relative = candidate.relative_to(root)
    except ValueError as error:
        raise RunError("output_path_outside_workspace", str(raw_output)) from error
    current_fd = _open_directory(str(root))
    current_path = root
    try:
        for part in relative.parts:
            next_fd = _open_or_create_directory(part, current_fd)
            os.close(current_fd)
            current_fd = next_fd
            current_path = current_path / part
        identity = os.fstat(current_fd)
        return OutputDirectory(current_path, current_fd, identity.st_dev, identity.st_ino)
    except RunError:
        os.close(current_fd)
        raise
