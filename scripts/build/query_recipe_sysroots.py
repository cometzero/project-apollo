#!/usr/bin/env python3

from __future__ import annotations

import argparse
from contextlib import redirect_stdout
import importlib
import sys
from typing import Protocol, Self, cast


class RecipeData(Protocol):
    def getVar(self, name: str) -> object: ...


class TinfoilSession(Protocol):
    def __enter__(self) -> Self: ...

    def __exit__(
        self,
        exc_type: object,
        exc_value: object,
        traceback: object,
    ) -> None: ...

    def prepare(self, *, quiet: int) -> None: ...

    def parse_recipe(self, recipe: str) -> RecipeData: ...


class TinfoilFactory(Protocol):
    def __call__(self) -> TinfoilSession: ...


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("recipes", nargs="+")
    return parser.parse_args()


def checked_field(value: object, variable: str, recipe: str) -> str:
    if not isinstance(value, str) or not value:
        raise RuntimeError(f"{variable} is empty for {recipe}")
    if "\t" in value or "\n" in value:
        raise RuntimeError(f"{variable} is not a single TSV field for {recipe}")
    return value


def main() -> int:
    args = parse_args()
    module = importlib.import_module("bb.tinfoil")
    factory = cast(TinfoilFactory, getattr(module, "Tinfoil"))
    rows: list[tuple[str, str, str]] = []

    with redirect_stdout(sys.stderr):
        with factory() as tinfoil:
            tinfoil.prepare(quiet=2)
            for recipe in args.recipes:
                data = tinfoil.parse_recipe(recipe)
                workdir = checked_field(
                    data.getVar("WORKDIR"),
                    "WORKDIR",
                    recipe,
                )
                target_prefix = checked_field(
                    data.getVar("TARGET_PREFIX"),
                    "TARGET_PREFIX",
                    recipe,
                )
                rows.append((recipe, workdir, target_prefix))
    for row in rows:
        print("\t".join(row))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
