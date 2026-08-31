from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Final


DOFILE_RE: Final = re.compile(r'dofile\s*\([^)]*"([^"]+\.lua)"[^)]*\)')


@dataclass(frozen=True, slots=True)
class LuaModuleError(Exception):
    reason: str
    path: Path

    def __str__(self) -> str:
        return f"{self.reason}:{self.path}"


def strip_comments(text: str) -> str:
    return re.sub(r"--.*", "", text)


def includes(path: Path, text: str) -> tuple[Path, ...]:
    clean = strip_comments(text)
    matches = tuple(DOFILE_RE.finditer(clean))
    if clean.count("dofile(") != len(matches):
        raise LuaModuleError("malformed_dofile", path)
    return tuple(path.parent / match.group(1) for match in matches)


def load_module_graph(entry: Path) -> dict[str, str]:
    base = entry.parent.resolve()
    loaded: dict[str, str] = {}
    visiting: set[Path] = set()

    def visit(path: Path) -> None:
        resolved = path.resolve()
        try:
            relative = resolved.relative_to(base)
        except ValueError as error:
            raise LuaModuleError("module_outside_root", resolved) from error
        if resolved in visiting:
            raise LuaModuleError("module_cycle", resolved)
        if relative.as_posix() in loaded:
            return
        try:
            text = resolved.read_text(encoding="utf-8")
        except OSError as error:
            raise LuaModuleError("missing_module", resolved) from error
        visiting.add(resolved)
        for included in includes(resolved, text):
            visit(included)
        visiting.remove(resolved)
        loaded[relative.as_posix()] = text

    visit(entry)
    return loaded
