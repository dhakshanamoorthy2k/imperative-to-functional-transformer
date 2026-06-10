# main.py is the driver file of the project.
# It connects all stages together:
# Parser → CFG → SSA → Emitter

from .parser import parse, print_ast
from .cfg import build_cfg
from tests.test_cases import test1, test2, test3, test4, test5, test6,test7,test8,test9
from .ssa import to_ssa, SSAConverter
from .emitter import emit

# Each tuple contains:
# 1. input code
# 2. function name
# 3. function parameters
# 4. test description
tests = [
    (test1, "f", "", "TEST 1 — straight line"),
    (test2, "f", "x", "TEST 2 — if/else"),
    (test3, "f", "n", "TEST 3 — while loop"),
    (test4, "f", "n", "TEST 4 — for loop"),
    (test5, "f", "x, y", "TEST 5 — nested if"),
    (test6, "f", "items", "TEST 6 — map pattern"),
    (test7, "f", "items", "TEST 7 — filter pattern"),
    (test8, "f", "items", "TEST 8 — reduce pattern"),
    (test9, "f", "items_a, items_b", "TEST 9 — zip pattern"),
]

# Run every test case through the full transformation pipeline.
for i, (code, fname, params, label) in enumerate(tests, 1):

    # Display test name
    print(f"\n{'#'*60}")
    print(f"  {label}")
    print(f"{'#'*60}")

    # ── INPUT ──
    print(f"\n{'='*50}")
    print(f" INPUT CODE")
    print(f"{'='*50}")
    print(code.strip())

    # ── STAGE 1: AST ──
    print(f"\n{'='*50}")
    print(f" STAGE 1 — AST")
    print(f"{'='*50}")
    tree = parse(code)
    print_ast(tree)

    # ── STAGE 2: CFG ──
    print(f"\n{'='*50}")
    print(f" STAGE 2 — CFG BLOCKS")
    print(f"{'='*50}")
    cfg = build_cfg(tree)
    cfg.print_cfg()

    # ── STAGE 3: SSA ──
    print(f"\n{'='*50}")
    print(f" STAGE 3 — SSA FORM")
    print(f"{'='*50}")
    cfg, converter = to_ssa(cfg)
    converter.print_ssa()

    # ── STAGE 4: FUNCTIONAL OUTPUT ──
    print(f"\n{'='*50}")
    print(f" STAGE 4 — FUNCTIONAL OUTPUT")
    print(f"{'='*50}")
    result = emit(cfg, converter, func_name=fname, params=params)
    print(result)

    print(f"\n{'#'*60}\n")
