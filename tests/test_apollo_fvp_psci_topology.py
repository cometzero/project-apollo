"""Preprocess the real TF-A topology; this does not qualify power transitions."""

import ast
import operator
from pathlib import Path
import re
import shutil
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[1]
TFA = ROOT / "hsoc-stack/components/primary_compute/trusted-firmware-a"
PLATFORM = TFA / "plat/arm/board/automotive_rd/platform/apollo_fvp"


def integer_expression(expression):
    """Evaluate only the integer arithmetic emitted by these platform macros."""
    operations = {ast.Add: operator.add, ast.Sub: operator.sub,
                  ast.Div: operator.floordiv}

    def visit(node):
        if isinstance(node, ast.Constant) and type(node.value) is int:
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in operations:
            return operations[type(node.op)](visit(node.left), visit(node.right))
        raise AssertionError(f"Unexpected platform expression: {expression}")

    return visit(ast.parse(expression.strip(), mode="eval").body)


@pytest.mark.parametrize("cores", [1, 2, 3, 4, 5, 8, 9, 12, 13, 16])
def test_css_system_root_and_domain_capacity(cores):
    compiler = shutil.which("gcc")
    if compiler is None:
        pytest.skip("host gcc preprocessor unavailable")
    source = (PLATFORM / "apollo_fvp_topology.c").read_text()
    array = re.search(
        r"const unsigned char apollo_fvp_pd_tree_desc\[\] = \{.*?\n\};",
        source, re.S,
    )
    assert array is not None
    unit = (
        '#include <platform_def.h>\n'
        'LEVEL PLAT_MAX_PWR_LVL\n'
        'DOMAINS PLAT_NUM_PWR_DOMAINS\n' + array.group() + '\n'
    )
    # Assembly preprocessing avoids needing a target libc or cross compiler.
    result = subprocess.run(
        [compiler, "-E", "-P", "-x", "assembler-with-cpp",
         f"-DPLATFORM_CORE_COUNT={cores}",
         f"-I{TFA / 'include'}", f"-I{TFA / 'include/arch/aarch64'}",
         f"-I{PLATFORM / 'include'}", "-"],
        input=unit, text=True, capture_output=True, timeout=15, check=True,
    ).stdout
    level = integer_expression(re.search(r"LEVEL (.*)", result)[1])
    domains = integer_expression(re.search(r"DOMAINS (.*)", result)[1])
    entries = result.split("= {")[1].split("}")[0].split(",")
    tree = [integer_expression(entry) for entry in entries if entry.strip()]
    assert level == 2
    assert tree[0] == 1
    assert tree[1] == len(tree[2:]) == (cores + 3) // 4
    assert all(1 <= count <= 4 for count in tree[2:])
    assert sum(tree[2:]) == cores
    assert domains == 1 + tree[1] + cores
