"""
ssa.py

This file converts the CFG into Static Single Assignment (SSA) form.

What it does:
- Renames variables so every variable is assigned only once.
- Inserts phi nodes at merge points.
- Rewrites variable uses to correct SSA versions.

Why it is needed:
- SSA simplifies program analysis.
- Makes data flow easier to track.
- Helps functional code generation because immutable variables are easier to represent.
"""
# ast is used to inspect and modify Python AST nodes.
# CFG is imported because SSA conversion works on the Control Flow Graph.
import ast
from .cfg import CFG

# SSAConverter transforms the CFG into SSA form.
# SSA means:
# every variable gets assigned exactly once.
#
# Example:
# x = 1
# x = x + 1
#
# becomes:
# x_1 = 1
# x_2 = x_1 + 1
class SSAConverter:
    # Stores the CFG.
    # var_counter keeps track of how many versions each variable has.
    #Example:x -> x_1, x_2, x_3

    def __init__(self, cfg: CFG):
        self.cfg = cfg
        self.var_counter = {}

    # Main SSA conversion pipeline.
    # Step 1:Rename variables into unique versions.
    # Step 2:Insert phi nodes at merge points.
    # Step 3:Rewrite variable usages to use phi versions correctly.
    def convert(self):
        self._rename_all_blocks()
        self._insert_all_phi_nodes()
        self._rewrite_uses_from_phi_nodes()
        return self.cfg

    # -----------------------------
    # Helpers
    # -----------------------------

    # Removes SSA version numbers from variables.
    # Example: x_3 -> x
    # Needed when creating new versions or comparing variables.
    def _base_name(self, name):
        if "_" in name and name.rsplit("_", 1)[1].isdigit():
            return name.rsplit("_", 1)[0]
        return name
    
    # Creates a new SSA version for a variable.
    # Example: x -> x_1 x -> x_2
    # Ensures every assignment is unique.
    def _new_version(self, base):
        base = self._base_name(base)
        self.var_counter[base] = self.var_counter.get(base, 0) + 1
        return f"{base}_{self.var_counter[base]}"
    
    # Finds all predecessor blocks.
    #
    # Predecessor:
    # a block that can execute before the current block.
    #
    # Needed for phi-node insertion.
    def _get_predecessors(self, block_id):
        preds = []
        for bid, block in self.cfg.blocks.items():
            if block_id in block.successors:
                preds.append(bid)
        return preds
    
    # Finds the latest variable definitions inside a block.
    #
    # Example:
    # x_1 = 1
    # x_2 = x_1 + 1
    #
    # Last definition of x is x_2.
    #
    # Needed for data-flow analysis.
    def _block_last_defs(self, block_id):
        block = self.cfg.blocks[block_id]
        defs = {}

        if hasattr(block, "phi_nodes"):
            for phi_var in block.phi_nodes:
                defs[self._base_name(phi_var)] = phi_var

        for stmt in block.stmts:
            if isinstance(stmt, ast.Assign):
                target = stmt.targets[0]
                if isinstance(target, ast.Name):
                    defs[self._base_name(target.id)] = target.id

        return defs

    # Finds variable definitions that can reach a block.
    #
    # Example:
    # if condition:
    #     x_1 = 1
    # else:
    #     x_2 = 2
    #
    # Both x_1 and x_2 reach the merge block.
    #
    # Needed to determine where phi nodes are required.
    def _find_reaching_defs(self, block_id):
        defs = {}
        visited = set()
        stack = [block_id]

        while stack:
            bid = stack.pop()
            if bid in visited:
                continue
            visited.add(bid)

            local_defs = self._block_last_defs(bid)
            for base, version in local_defs.items():
                if base not in defs:
                    defs[base] = version

            for pred in self._get_predecessors(bid):
                stack.append(pred)

        return defs

    # -----------------------------
    # First pass: normal SSA rename
    # -----------------------------
    # Starts SSA renaming from the entry block.
    # Traverses all CFG blocks recursively.
    def _rename_all_blocks(self):
        current = {}
        visited = set()
        self._rename_block(self.cfg.entry, current, visited)

    # Renames variables inside expressions.
    #
    # Example:
    # y = x + 1
    #
    # becomes:
    # y_1 = x_2 + 1
    #
    # Uses the current active variable versions.
    def _rename_expr(self, node, current):

        # Replaces variable name with latest SSA version.
        if isinstance(node, ast.Name):
            base = self._base_name(node.id)
            if base in current:
                node.id = current[base]

        elif isinstance(node, ast.BinOp):
            self._rename_expr(node.left, current)
            self._rename_expr(node.right, current)

        elif isinstance(node, ast.Compare):
            self._rename_expr(node.left, current)
            for c in node.comparators:
                self._rename_expr(c, current)

        elif isinstance(node, ast.Call):
            for arg in node.args:
                self._rename_expr(arg, current)

        elif isinstance(node, ast.Subscript):
            self._rename_expr(node.value, current)
            self._rename_expr(node.slice, current)

        elif isinstance(node, ast.Expr):
            self._rename_expr(node.value, current)

        elif isinstance(node, ast.For):
            self._rename_expr(node.iter, current)
            for s in node.body:
                self._rename_stmt(s, current)

        return node
    
    # Renames variables inside statements.
    #
    # Handles:
    # - assignments
    # - returns
    # - comparisons
    # - expressions
    # - for loops
    def _rename_stmt(self, stmt, current):
        if isinstance(stmt, ast.Assign):
            self._rename_expr(stmt.value, current)

            target = stmt.targets[0]
            if isinstance(target, ast.Name):
                base = self._base_name(target.id)

                # Creates a completely new SSA version after assignment.
                #
                # Example:
                # x = ...
                #
                # becomes:
                # x_3 = ...
                new_name = self._new_version(base)
                target.id = new_name
                current[base] = new_name

        elif isinstance(stmt, ast.Return):
            self._rename_expr(stmt.value, current)

        elif isinstance(stmt, ast.Compare):
            self._rename_expr(stmt, current)

        elif isinstance(stmt, ast.Expr):
            self._rename_expr(stmt, current)

        elif isinstance(stmt, ast.For):
            self._rename_expr(stmt, current)

        return stmt

    # Recursively renames all variables in CFG blocks.
    #
    # Each branch gets its own copy of current variable versions.
    # This prevents incorrect overwriting between branches.
    def _rename_block(self, block_id, current, visited):
        if block_id in visited:
            return

        visited.add(block_id)
        block = self.cfg.blocks[block_id]

        local_current = current.copy()
        new_stmts = []

        for stmt in block.stmts:
            new_stmts.append(self._rename_stmt(stmt, local_current))

        block.stmts = new_stmts

        for succ in block.successors:
            self._rename_block(succ, local_current.copy(), visited)

    # -----------------------------
    # Second pass: phi insertion
    # -----------------------------

    # Tries to insert phi nodes into every block.
    #
    # Phi nodes are needed when multiple control-flow paths merge.
    def _insert_all_phi_nodes(self):
        for block_id in self.cfg.blocks:
            self._insert_phi_nodes(block_id)

    # Inserts phi nodes into one block if needed.
    #
    # Example:
    #
    # if cond:
    #     x_1 = 1
    # else:
    #     x_2 = 2
    #
    # merge:
    #     x_3 = phi(x_1, x_2)
    #
    #Phi chooses the correct value depending on execution path.
    def _insert_phi_nodes(self, block_id):
        preds = self._get_predecessors(block_id)

        # Phi nodes are only needed when a block has multiple predecessors.
        if len(preds) < 2:
            return

        incoming = {}

        for pred in preds:
            reaching = self._find_reaching_defs(pred)

            for base, version in reaching.items():
                incoming.setdefault(base, set()).add(version)

        phi_nodes = {}

        for base, versions in incoming.items():
            versions = sorted(list(versions))

            if len(versions) >= 2:
                # Creates a new merged SSA version.
                #Example: x_3 = phi(x_1, x_2)
                phi_var = self._new_version(base)
                phi_nodes[phi_var] = versions

        if phi_nodes:
            block = self.cfg.blocks[block_id]
            block.phi_nodes = phi_nodes

    # -----------------------------
    # Third pass: rewrite uses to phi versions
    # -----------------------------
    # After phi nodes are inserted,
    # variable usages must be updated to use phi versions.
    #
    # Otherwise later stages may use outdated variable versions.

    def _rewrite_uses_from_phi_nodes(self):
        for bid, block in self.cfg.blocks.items():
            if hasattr(block, "phi_nodes") and block.phi_nodes:
                phi_map = {}

                for phi_var in block.phi_nodes:
                    base = self._base_name(phi_var)
                    phi_map[base] = phi_var

                self._rewrite_block_uses(block, phi_map)

                for succ_id in block.successors:
                    succ_block = self.cfg.blocks[succ_id]
                    self._rewrite_block_uses(succ_block, phi_map)

        # Fix return blocks using previous merge phi
        for bid, block in self.cfg.blocks.items():
            preds = self._get_predecessors(bid)

            for pred in preds:
                pred_block = self.cfg.blocks[pred]

                if hasattr(pred_block, "phi_nodes"):
                    phi_map = {}

                    for phi_var in pred_block.phi_nodes:
                        base = self._base_name(phi_var)
                        phi_map[base] = phi_var

                    self._rewrite_block_uses(block, phi_map)

    # Replaces variable usages with phi versions.
    #
    # Example:return x_2
    # becomes: return x_3
    #
    # where x_3 is the phi variable.

    def _rewrite_expr_with_phi(self, node, phi_map):
        if isinstance(node, ast.Name):
            base = self._base_name(node.id)
            if base in phi_map:
                node.id = phi_map[base]

        elif isinstance(node, ast.BinOp):
            self._rewrite_expr_with_phi(node.left, phi_map)
            self._rewrite_expr_with_phi(node.right, phi_map)

        elif isinstance(node, ast.Compare):
            self._rewrite_expr_with_phi(node.left, phi_map)
            for c in node.comparators:
                self._rewrite_expr_with_phi(c, phi_map)

        elif isinstance(node, ast.Call):
            for arg in node.args:
                self._rewrite_expr_with_phi(arg, phi_map)

        elif isinstance(node, ast.Subscript):
            self._rewrite_expr_with_phi(node.value, phi_map)
            self._rewrite_expr_with_phi(node.slice, phi_map)

        elif isinstance(node, ast.Expr):
            self._rewrite_expr_with_phi(node.value, phi_map)

        elif isinstance(node, ast.For):
            self._rewrite_expr_with_phi(node.iter, phi_map)
            for s in node.body:
                self._rewrite_stmt_with_phi(s, phi_map)

    def _rewrite_stmt_with_phi(self, stmt, phi_map):
        if isinstance(stmt, ast.Assign):
            self._rewrite_expr_with_phi(stmt.value, phi_map)

        elif isinstance(stmt, ast.Return):
            self._rewrite_expr_with_phi(stmt.value, phi_map)

        elif isinstance(stmt, ast.Compare):
            self._rewrite_expr_with_phi(stmt, phi_map)

        elif isinstance(stmt, ast.Expr):
            self._rewrite_expr_with_phi(stmt, phi_map)

        elif isinstance(stmt, ast.For):
            self._rewrite_expr_with_phi(stmt, phi_map)

    # Applies phi-variable rewriting to all statements in a block.
    def _rewrite_block_uses(self, block, phi_map):
        for stmt in block.stmts:
            self._rewrite_stmt_with_phi(stmt, phi_map)

    # -----------------------------
    # Print SSA
    # -----------------------------
    # Prints the final SSA representation.
    #
    # Useful for:
    # - debugging
    # - testing
    # - presentation demonstration

    def print_ssa(self):
        print("\n[SSA BLOCKS]")

        for bid, block in self.cfg.blocks.items():
            print(f"\n  Block {bid}:")
            print(f"    Successors: {block.successors}")

            if hasattr(block, "phi_nodes") and block.phi_nodes:
                print("    Phi Nodes:")
                for new_var, versions in block.phi_nodes.items():
                    # Displays phi-node relationships.
                    #
                    # Example:x_3 = phi(x_1, x_2)
                    print(f"      {new_var} = phi({', '.join(versions)})")

            print("    Statements:")
            for stmt in block.stmts:
                print(f"      - {ast.unparse(stmt)}")


def to_ssa(cfg: CFG):
    converter = SSAConverter(cfg)
    converter.convert()
    return cfg, converter