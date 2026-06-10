import unittest
import ast
from unittest import result
from parser import parse
from cfg import build_cfg
from ssa import to_ssa
from emitter import emit

# ─────────────────────────────
# UNIT TESTS — test each stage
# ─────────────────────────────

class TestParser(unittest.TestCase):
    """Unit test for Stage 1 — Parser"""

    def test_parse_returns_ast(self):
        code = "def f():\n    x = 1\n    return x"
        tree = parse(code)
        self.assertIsNotNone(tree)
        self.assertIsInstance(tree, ast.Module)

    def test_parse_detects_function(self):
        code = "def f():\n    x = 1\n    return x"
        tree = parse(code)
        self.assertIsInstance(tree.body[0], ast.FunctionDef)


class TestCFG(unittest.TestCase):
    """Unit test for Stage 2 — CFG Builder"""

    def test_straight_line_has_2_blocks(self):
        code = "def f():\n    x = 1\n    return x"
        tree = parse(code)
        cfg  = build_cfg(tree)
        self.assertEqual(len(cfg.blocks), 2)

    def test_if_else_has_5_blocks(self):
        code = "def f(x):\n    if x > 0:\n        y = 1\n    else:\n        y = 0\n    return y"
        tree = parse(code)
        cfg  = build_cfg(tree)
        self.assertEqual(len(cfg.blocks), 5)

    def test_while_loop_has_back_edge(self):
        code = "def f(n):\n    i = 0\n    while i < n:\n        i = i + 1\n    return i"
        tree = parse(code)
        cfg  = build_cfg(tree)
        # check back edge exists — body block points to header
        back_edge_found = False
        for bid, block in cfg.blocks.items():
            for succ in block.successors:
                if succ < bid:
                    back_edge_found = True
        self.assertTrue(back_edge_found)


class TestSSA(unittest.TestCase):
    """Unit test for Stage 3 — SSA Converter"""

    def test_variables_versioned(self):
        code = "def f():\n    x = 1\n    y = x + 2\n    return y"
        tree           = parse(code)
        cfg            = build_cfg(tree)
        cfg, converter = to_ssa(cfg)
        # check x_1 appears in output
        block0_stmts = [ast.unparse(s) for s in cfg.blocks[0].stmts]
        self.assertTrue(any("x_1" in s for s in block0_stmts))

    def test_each_variable_assigned_once(self):
        code = "def f():\n    x = 1\n    y = x + 2\n    return y"
        tree           = parse(code)
        cfg            = build_cfg(tree)
        cfg, converter = to_ssa(cfg)
        # collect all assignment targets
        targets = []
        for block in cfg.blocks.values():
            for stmt in block.stmts:
                if isinstance(stmt, ast.Assign):
                    targets.append(stmt.targets[0].id)
        # no duplicates — each variable assigned once
        self.assertEqual(len(targets), len(set(targets)))


class TestEmitter(unittest.TestCase):
    """Unit test for Stage 4 — Emitter"""

    def test_output_is_string(self):
        code           = "def f():\n    x = 1\n    return x"
        tree           = parse(code)
        cfg            = build_cfg(tree)
        cfg, converter = to_ssa(cfg)
        result         = emit(cfg, converter, func_name="f", params="")
        self.assertIsInstance(result, str)

    def test_output_starts_with_def(self):
        code           = "def f():\n    x = 1\n    return x"
        tree           = parse(code)
        cfg            = build_cfg(tree)
        cfg, converter = to_ssa(cfg)
        result         = emit(cfg, converter, func_name="f", params="")
        self.assertTrue(result.strip().startswith("def f"))


# ─────────────────────────────────────
# INTEGRATION TEST — two stages together
# ─────────────────────────────────────

class TestIntegration(unittest.TestCase):
    """Integration test — Parser + CFG together"""

    def test_parser_to_cfg(self):
        code = "def f(x):\n    if x > 0:\n        y = 1\n    else:\n        y = 0\n    return y"
        tree = parse(code)
        cfg  = build_cfg(tree)
        # entry block should have 2 successors (then + else)
        entry = cfg.blocks[cfg.entry]
        self.assertEqual(len(entry.successors), 2)

    def test_cfg_to_ssa(self):
        code           = "def f():\n    x = 1\n    y = x + 2\n    return y"
        tree           = parse(code)
        cfg            = build_cfg(tree)
        cfg, converter = to_ssa(cfg)
        # var_stack keys are base names, values are version lists
    # check x exists and has version x_1
        block0_stmts = [ast.unparse(s) for s in cfg.blocks[0].stmts]
        self.assertTrue(any("x_1" in s for s in block0_stmts))
        self.assertTrue(any("y_1" in s for s in block0_stmts))


# ─────────────────────────────────────
# END TO END TESTS — full pipeline
# ─────────────────────────────────────

class TestEndToEnd(unittest.TestCase):
    """End-to-end test — full pipeline"""

    def _run(self, code, func_name, params):
        tree           = parse(code)
        cfg            = build_cfg(tree)
        cfg, converter = to_ssa(cfg)
        return emit(cfg, converter, func_name=func_name, params=params)

    def test_straight_line_output(self):
        code   = "def f():\n    x = 1\n    y = x + 2\n    return y"
        result = self._run(code, "f", "")
        self.assertIn("x_1 = 1", result)
        self.assertIn("y_1 = x_1 + 2", result)

    def test_while_loop_becomes_reduce(self):
        code = """
def f(n):
    total = 0
    i = 0
    while i < n:
        total = total + i
        i = i + 1
    return total
"""
        result = self._run(code, "f", "n")
        self.assertIn("reduce(", result)
        self.assertIn("lambda acc, i", result)
        self.assertIn("range(n)", result)
        self.assertIn("return result", result)

    def test_if_else_becomes_expression(self):
        code = """
def f(x):
    if x > 0:
        y = x + 1
    else:
        y = 0
    return y
"""
        result = self._run(code, "f", "x")
        self.assertIn("if x > 0", result)


# ─────────────────────────────────────
# Run all tests
# ─────────────────────────────────────

if __name__ == "__main__":
    unittest.main(verbosity=2)