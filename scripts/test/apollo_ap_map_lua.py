from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Final


DOFILE_RE: Final = re.compile(r'\bdofile\s*\(([^)]*)\)')
LUA_PATH_RE: Final = re.compile(r'''["']([^"']+\.lua)["']''')


@dataclass(frozen=True, slots=True)
class LuaModuleError(Exception):
    reason: str
    path: Path

    def __str__(self) -> str:
        return f"{self.reason}:{self.path}"


def strip_comments(text: str) -> str:
    return re.sub(r"--.*", "", text)


def includes(path: Path, text: str, root: Path | None = None) -> tuple[Path, ...]:
    clean = strip_comments(text)
    matches = tuple(DOFILE_RE.finditer(clean))
    if len(re.findall(r"\bdofile\s*\(", clean)) != len(matches):
        raise LuaModuleError("malformed_dofile", path)
    directories = {"dir": path.parent, "apollo_dir": root or path.parent,
                   "ctx.apollo_dir": root or path.parent}
    for alias, parent, suffix in re.findall(
        r'''\blocal\s+(\w+)\s*=\s*([\w.]+)\s*\.\.\s*["']([^"']*)["']''', clean
    ):
        if parent in directories:
            directories[alias] = directories[parent] / suffix
    paths = []
    for match in matches:
        argument = match.group(1)
        literals = LUA_PATH_RE.findall(argument)
        if len(literals) != 1:
            raise LuaModuleError("nonliteral_dofile", path)
        # ctx.apollo_dir is rooted at the entrypoint, including from deeply
        # nested factory modules. It is not relative to the including file.
        prefix = re.match(r"\s*([\w.]+)\s*\.\.", argument)
        if prefix and prefix.group(1) not in directories:
            raise LuaModuleError("unknown_dofile_directory", path)
        base = directories[prefix.group(1)] if prefix else path.parent
        paths.append(base / literals[0])
    return tuple(paths)


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
        for included in includes(resolved, text, base):
            visit(included)
        visiting.remove(resolved)
        loaded[relative.as_posix()] = text

    visit(entry)
    return loaded
