"""
emitter.py

This file generates the final functional-style Python code.

What it does:
- Traverses the SSA-based CFG.
- Detects functional patterns.
- Converts imperative control flow into functional equivalents.
- Generates recursion, map(), filter(), and reduce() output.

Why it is needed:
- This is the final stage of the transformation pipeline.
- It produces the final transformed functional program.
"""

# ast is used to convert AST nodes back into readable Python code.
import ast

# Emitter converts the CFG + SSA representation
# into final functional-style Python code.
class Emitter:


    # Stores:
    # - cfg: Control Flow Graph
    # - converter: SSA converter object
    #
    # output_lines stores generated code line by line.
    # indent controls indentation level during code generation.
    def __init__(self, cfg, converter):
        self.cfg = cfg
        self.converter = converter
        self.output_lines = []
        self.indent = 0

    # ─────────────────────────────────────
    # Helpers
    # ─────────────────────────────────────
    # Writes one line into the output program.
    # Automatically adds indentation.
    def _write(self, line):
        self.output_lines.append("    " * self.indent + line)

    # Converts AST expressions back into readable Python code.
    # Example:
    # AST BinOp → "x + 1"
    def _expr(self, node):
        return ast.unparse(node)

    # Finds the most recent assigned variable.
    #
    # Used when generating return statements automatically.
    def _last_written_var(self):
        for line in reversed(self.output_lines):
            s = line.strip()
            if (
                "=" in s
                and not s.startswith("def")
                and not s.startswith("if")
                and not s.startswith("return")
                and not s.startswith("#")
            ):
                return s.split("=")[0].strip()
        return None
    
    # Detects whether a block is a loop header.
    #
    # Loop headers:
    # - contain loop conditions
    # - have back edges from loop body
    #
    # Needed for recursive loop generation.
    def _is_loop_header(self, block_id):
        block = self.cfg.blocks[block_id]

        # for-loop header
        for stmt in block.stmts:
            if isinstance(stmt, ast.For):
                return True
        
        # while/range loop header with direct back edge
        for succ_id in block.successors:
            succ = self.cfg.blocks[succ_id]
            if block_id in succ.successors:
                return True
        return False
    
    # Returns the loop body block connected to the loop header.
    def _get_loop_body(self, header_id):
        block = self.cfg.blocks[header_id]
        if len(block.successors) >=1:
            return block.successors[0]
        return None
    
    # Returns the block executed after loop termination.
    def _get_loop_exit(self, header_id):
        block = self.cfg.blocks[header_id]
        #for x in items header has[body, exit]
        if len(block.successors) == 2:
            return block.successors[1]
        return None
    
    # Collects loop variables used inside recursion.
    #
    # Example:
    # i, total
    #
    # Needed to generate recursive helper functions.
    def _get_loop_vars(self, body_block_id):
        block = self.cfg.blocks[body_block_id]
        loop_vars = []
        for stmt in block.stmts:
            if isinstance(stmt, ast.Assign):
                target = stmt.targets[0].id
                base   = target.rsplit('_', 1)[0]
                init   = f"{base}_1"
                loop_vars.append((base, init, target))
        return loop_vars

    # ─────────────────────────────────────
    # Find merge block
    # ─────────────────────────────────────
    # Finds the merge block after an if/else branch.
    #
    # Example:
    #
    # if condition:
    #     ...
    # else:
    #     ...
    #
    # Both branches later merge into one block.
    #
    # Needed for phi-node handling and conditional expressions.
    def _get_merge_block(self, block_id):
        block = self.cfg.blocks[block_id]
        succs = block.successors

        if len(succs) != 2:
            return None

        then_id = succs[0]
        else_id = succs[1]

        def reachable(start_id):
            seen  = set()
            stack = [start_id]
            while stack:
                bid = stack.pop()
                if bid in seen:
                    continue
                seen.add(bid)
                b = self.cfg.blocks[bid]
                for s in b.successors:
                    if s not in seen:
                        stack.append(s)
            return seen

        then_reachable = reachable(then_id)
        else_reachable = reachable(else_id)
        common         = then_reachable & else_reachable

        if not common:
            return None

        return min(common)

    # ─────────────────────────────────────
    # Recursively resolve value of a block
    # ─────────────────────────────────────
    # Recursively extracts expression values from CFG blocks.
    #
    # Used to convert if/else branches into
    # functional conditional expressions.
    def _emit_block_value(self, block_id, visited):
        if block_id in visited:
            return None
        visited.add(block_id)

        block = self.cfg.blocks[block_id]
        succs = block.successors

        if len(succs) == 2 and not self._is_loop_header(block_id):
            cond    = self._expr(block.stmts[0]) if block.stmts else "True"
            then_id = succs[0]
            else_id = succs[1]

            then_val = self._emit_block_value(then_id, visited)
            else_val = self._emit_block_value(else_id, visited)

            if then_val and else_val:
                return f"({then_val}) if {cond} else ({else_val})"
            elif then_val:
                return f"({then_val}) if {cond} else None"
            else:
                return None

        for stmt in block.stmts:
            if isinstance(stmt, ast.Assign):
                return self._expr(stmt.value)

        return None

    # ─────────────────────────────────────
    # Find result variable name
    # ─────────────────────────────────────

    # Finds the final variable produced by a branch.
    #
    # Used when generating:
    # x = a if cond else b
    def _get_result_var(self, block_id, visited=None):
        if visited is None:
            visited = set()
        if block_id in visited:
            return None
        visited.add(block_id)

        block = self.cfg.blocks[block_id]
        succs = block.successors

        if len(succs) == 2 and not self._is_loop_header(block_id):
            then_id = succs[0]
            return self._get_result_var(then_id, visited)

        for stmt in block.stmts:
            if isinstance(stmt, ast.Assign):
                return stmt.targets[0].id

        return None

    # ─────────────────────────────────────
    # Emit if/else as expression
    # ─────────────────────────────────────
    # Converts imperative if/else blocks into
    # functional conditional expressions.
    #
    # Example:
    #
    # if x > 0:
    #     y = 1
    # else:
    #     y = 2
    #
    # becomes:
    #
    # y = 1 if x > 0 else 2
    def _emit_if_else(self, cond_block_id):
        visited = set()
        value   = self._emit_block_value(cond_block_id, visited)

        block    = self.cfg.blocks[cond_block_id]
        else_id  = block.successors[1] if len(block.successors) == 2 else None
        else_var = None

        if else_id:
            else_block = self.cfg.blocks[else_id]
            for stmt in else_block.stmts:
                if isinstance(stmt, ast.Assign):
                    else_var = stmt.targets[0].id
                    break

        var = else_var or self._get_result_var(cond_block_id)

        if var and value:
            merge_id = self._get_merge_block(cond_block_id)

            # Uses phi-node variable as the merged result variable.
            #
            # Example:
            # y_3 = (1) if cond else (2)
            phi_var  = var

            if merge_id is not None:
                merge_block = self.cfg.blocks[merge_id]
                if hasattr(merge_block, 'phi_nodes') and merge_block.phi_nodes:
                    for pvar in merge_block.phi_nodes:
                        phi_var = pvar
                        break

            self._write(f"{phi_var} = {value}")

        return self._get_merge_block(cond_block_id)

    # ─────────────────────────────────────
    # Pattern detector
    # Detects map / filter / reduce / recursion
    # ─────────────────────────────────────

        """
        Looks at the loop body statements and decides
        which functional pattern best fits:
        - map    : result.append(expr)  with no condition
        - filter : result.append(x)     inside an if condition
        - reduce : acc = acc + expr      accumulator pattern
        - recursion : anything else
        """
    def _detect_loop_pattern(self, body_block_id):
        block = self.cfg.blocks[body_block_id]
        stmts = block.stmts

        # MAP: result.append(expr)
        # Detects loops that transform elements.
        #
        # Example:
        # result.append(x * 2)
        #
        # This can become:
        # map(lambda x: x * 2, items)
        for stmt in stmts:
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                func = stmt.value.func
                if isinstance(func, ast.Attribute) and func.attr == "append":
                    append_expr = stmt.value.args[0]
                    return ("map", append_expr)

        # FILTER: condition block -> append block
        # Detects loops that select elements conditionally.
        #
        # Example:
        # if x > 0:
        #     result.append(x)
        #
        # This can become:
        # filter(lambda x: x > 0, items)
        if len(block.successors) == 2 and block.stmts:
            condition = block.stmts[0]
            then_id = block.successors[0]
            then_block = self.cfg.blocks[then_id]

            for stmt in then_block.stmts:
                if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                    func = stmt.value.func
                    if isinstance(func, ast.Attribute) and func.attr == "append":
                        append_expr = stmt.value.args[0]
                        return ("filter", condition, append_expr)

        # REDUCE: total = total + x
        # Detects accumulator patterns.
        #
        # Example:
        # total = total + x
        #
        # This can become:
        # reduce(lambda acc, x: acc + x, items)
        for stmt in stmts:
            if isinstance(stmt, ast.Assign):
                target = stmt.targets[0]
                value = stmt.value

                if isinstance(target, ast.Name) and isinstance(value, ast.BinOp):
                    if isinstance(value.left, ast.Name):
                        target_name = target.id.rsplit('_', 1)[0]
                        left_base   = value.left.id.rsplit('_', 1)[0]

                        if target_name == left_base:
                            return ("reduce", target.id, value)

        return ("recursion",)
    # ─────────────────────────────────────
    # Emit map()
    # ─────────────────────────────────────
    # Generates functional map() transformation.
    #
    # Imperative:
    # for x in items:
    #     result.append(x * 2)
    #
    # Functional:
    # result = list(map(lambda x: x * 2, items))
    def _emit_map(self, iter_var, append_expr, iterable):
      
        lambda_body = self._expr(append_expr)

        iter_name   = self._expr(iter_var)
        iter_base = iter_name.rsplit("_", 1)[0]

        for i in range(1,50):
            lambda_body = lambda_body.replace(f"{iter_base}_{i}", iter_base)

        self._write(f"result = list(map(lambda {iter_name}: {lambda_body}, {iterable}))")
        self._write("return result")

    # ─────────────────────────────────────
    # Emit filter()
    # ─────────────────────────────────────
    # Generates functional filter() transformation.
    #
    # Imperative:
    # if x > 0:
    #     result.append(x)
    #
    # Functional:
    # result = list(filter(lambda x: x > 0, items))
    def _emit_filter(self, iter_var, condition, iterable):
      
        cond_str  = self._expr(condition)

        iter_name = self._expr(iter_var)
        iter_base = iter_name.rsplit("_", 1)[0]

        for i in range(1,50):
            cond_str = cond_str.replace(f"{iter_base}_{i}", iter_base)
        self._write(f"result = list(filter(lambda {iter_name}: {cond_str}, {iterable}))")
        
        self._write("return result")

    # ─────────────────────────────────────
    # Emit reduce()
    # ─────────────────────────────────────
    # Generates functional reduce() transformation.
    #
    # Imperative:
    # total = total + x
    #
    # Functional:
    # reduce(lambda acc, x: acc + x, items, 0)
    def _emit_reduce(self, iter_var, acc_var, acc_expr, init_val, iterable):
      
        lambda_body = self._expr(acc_expr)

        acc_base = acc_var.rsplit("_", 1)[0]
        iter_name = self._expr(iter_var)
        iter_base = iter_name.rsplit("_", 1)[0]

        for i in range(1, 50):
            lambda_body = lambda_body.replace(f"{acc_base}_{i}", "acc")
            lambda_body = lambda_body.replace(f"{iter_base}_{i}", iter_base)

        self._write("from functools import reduce")
        self._write(
            f"result = reduce(lambda acc, {iter_base}: {lambda_body}, {iterable}, {init_val})"
         )
        self._write("return result")

    # ─────────────────────────────────────
    # Emit loop — detects pattern first
    # then emits map / filter / reduce / recursion
    # ─────────────────────────────────────

    def _emit_loop(self, entry_stmts, header_id):
    # Main loop transformation function.
    #
    # Step 1:
    # Detect functional pattern.
    #
    # Step 2:
    # Generate: - map() - filter()- reduce() OR recursive functional loop.
        body_id = self._get_loop_body(header_id)
        exit_id = self._get_loop_exit(header_id)

        if body_id is None:
            return exit_id

        header_block = self.cfg.blocks[header_id]
        cond_node    = header_block.stmts[0] if header_block.stmts else None
        cond_str     = self._expr(cond_node) if cond_node else "True"
        body_block   = self.cfg.blocks[body_id]

        # Default iterable name
        iterable = "items"

        # Try to get iter variable name from condition
        iter_name = "x"
        if isinstance(cond_node, ast.For):
            iter_name = cond_node.target.id

            if isinstance(cond_node.iter, ast.Name):
                iterable = cond_node.iter.id
        
        # i < len(items_a)
        elif cond_node and isinstance(cond_node, ast.Compare):
            if isinstance(cond_node.left, ast.Name):
                iter_name = cond_node.left.id.rsplit('_', 1)[0]

            if len(cond_node.comparators)>0:
                comp = cond_node.comparators[0]

                #i<n
                if isinstance(comp, ast.Name):
                    iterable = f"range({comp.id})"
                
                #i<len(items_a)
                elif(
                    isinstance(comp, ast.Call)
                    and isinstance(comp.func,ast.Name)
                    and comp.func.id == "len"
                ):
                    arr_name = comp.args[0].id
                    iterable = f"range(len({arr_name}))"

        pattern = self._detect_loop_pattern(body_id)
        

        # ── map pattern ──
        if pattern[0] == 'map':
            append_expr = pattern[1]
            # emit any init stmts before the loop except result = []
            for stmt in entry_stmts:
                if isinstance(stmt, ast.Assign):
                    val = self._expr(stmt.value)
                    if val != "[]":
                        self._write(f"{stmt.targets[0].id} = {val}")
            self._emit_map(ast.Name(id=iter_name), append_expr, iterable)
            return exit_id

        # ── filter pattern ──
        elif pattern[0] == 'filter':
            condition   = pattern[1]
            append_expr = pattern[2]
            for stmt in entry_stmts:
                if isinstance(stmt, ast.Assign):
                    val = self._expr(stmt.value)
                    if val != "[]":
                        self._write(f"{stmt.targets[0].id} = {val}")
            self._emit_filter(ast.Name(id=iter_name), condition, iterable)
            return exit_id

        # ── reduce pattern ──
        elif pattern[0] == 'reduce':
            acc_var  = pattern[1]
            acc_expr = pattern[2]
            init_val = "0"
            # find the initial accumulator value from entry stmts
            for stmt in entry_stmts:
                if isinstance(stmt, ast.Assign):
                    tname = stmt.targets[0].id.rsplit('_', 1)[0]
                    if tname == acc_var.rsplit('_', 1)[0]:
                        init_val = self._expr(stmt.value)
            self._emit_reduce(
                ast.Name(id=iter_name),
                acc_var, acc_expr, init_val, iterable
            )
            return exit_id

        # ── fallback: tail recursion ──
        # If no functional pattern is detected,
        # the loop is transformed into tail recursion.
        #
        # This preserves functional programming style.
        else:
            loop_vars = self._get_loop_vars(body_id)

            iter_vars = []
            acc_vars  = []
            for (base, init, upd) in loop_vars:
                if base in cond_str:
                    iter_vars.append((base, init, upd))
                else:
                    acc_vars.append((base, init, upd))

            ordered_vars = iter_vars + acc_vars
            params       = [init for (_, init, _) in ordered_vars]
            updates      = [upd  for (_, _, upd)  in ordered_vars]
            param_str    = ", ".join(params)
            update_str   = ", ".join(updates)

            # emit init statements
            for stmt in entry_stmts:
                if isinstance(stmt, ast.Assign):
                    target = stmt.targets[0].id
                    value  = self._expr(stmt.value)
                    self._write(f"{target} = {value}")

            # emit recursive helper
            # Generates recursive helper function.
            #
            # Example:
            #
            # def _loop(i, total):
            #     ...
            self._write(f"def _loop({param_str}):")
            self.indent += 1
            self._write(f"if not ({cond_str}):")
            self.indent += 1
            ret_var = acc_vars[-1][1] if acc_vars else params[0]
            self._write(f"return {ret_var}")
            self.indent -= 1

            for stmt in body_block.stmts:
                if isinstance(stmt, ast.Assign):
                    target = stmt.targets[0].id
                    value  = self._expr(stmt.value)
                    self._write(f"{target} = {value}")

            # Recursive call replaces imperative loop iteration.
            self._write(f"return _loop({update_str})")
            self.indent -= 1
            self._write(f"result = _loop({param_str})")
            return exit_id

    # ─────────────────────────────────────
    # Emit straight line statements
    # ─────────────────────────────────────
    # Emits normal straight-line statements.
    #
    # Example:
    # x = 1
    # y = x + 2
    def _emit_stmts(self, stmts):
        for stmt in stmts:
            if isinstance(stmt, ast.Assign):
                target = stmt.targets[0].id
                value  = self._expr(stmt.value)
                self._write(f"{target} = {value}")
            elif isinstance(stmt, ast.Return):
                last_var = self._last_written_var()
                if last_var:
                    self._write(f"return {last_var}")
                else:
                    self._write(f"return {self._expr(stmt.value)}")

    # ─────────────────────────────────────
    # Find and emit return from CFG
    # ─────────────────────────────────────
    # Generates final return statement from CFG.
    def _emit_return_from_cfg(self):
        last_var = self._last_written_var()
        if last_var:
            self._write(f"return {last_var}")
            return
        for bid, blk in self.cfg.blocks.items():
            for stmt in blk.stmts:
                if isinstance(stmt, ast.Return):
                    self._write(f"return {self._expr(stmt.value)}")
                    return

    # ─────────────────────────────────────
    # Main emit — walks the CFG
    # ─────────────────────────────────────
    # Main code-generation function.
    #
    # Walks through the CFG block by block.
    # Produces final functional-style Python code.
    def emit(self, func_name="f", params=""):
        self._write(f"def {func_name}({params}):")
        self.indent += 1

        current_id = self.cfg.entry
        # Prevents infinite traversal in loops.
        visited    = set()

        while current_id is not None:
            if current_id in visited:
                break
            visited.add(current_id)

            block = self.cfg.blocks[current_id]
            succs = block.successors

            # Skip exit block
            if current_id == self.cfg.exit:
                break

            # ── Case 1: entry block leads to a loop header ──
            # Detects loops immediately after entry block.
            if succs and len(succs) == 1 and self._is_loop_header(succs[0]):
               self._emit_loop(block.stmts, succs[0])
               break

            # ── Case 2: current block IS a loop header ──
            #Directly transforms loop headers whenever encountered.
            elif self._is_loop_header(current_id):
                self._emit_loop([], current_id)
                break

            # ── Case 3: branch — simple or nested if/else ──
            # Handles functional conversion of branches.
            elif len(succs) == 2:
                next_id = self._emit_if_else(current_id)

                if next_id is not None:
                    merge_block = self.cfg.blocks[next_id]

                    if not merge_block.successors or merge_block.successors[0] == self.cfg.exit:
                        self._emit_return_from_cfg()
                        current_id = None
                        continue

                    for stmt in merge_block.stmts:
                        if isinstance(stmt, ast.Assign):
                            target = stmt.targets[0].id
                            value  = self._expr(stmt.value)
                            self._write(f"{target} = {value}")
                        elif isinstance(stmt, ast.Return):
                            last_var = self._last_written_var()
                            if last_var:
                                self._write(f"return {last_var}")
                            else:
                                self._write(f"return {self._expr(stmt.value)}")

                    after_id = merge_block.successors[0] if merge_block.successors else None

                    if after_id is not None and after_id != self.cfg.exit:
                        after_block = self.cfg.blocks[after_id]
                        for stmt in after_block.stmts:
                            if isinstance(stmt, ast.Assign):
                                target = stmt.targets[0].id
                                value  = self._expr(stmt.value)
                                self._write(f"{target} = {value}")
                            elif isinstance(stmt, ast.Return):
                                last_var = self._last_written_var()
                                if last_var:
                                    self._write(f"return {last_var}")
                                else:
                                    self._write(f"return {self._expr(stmt.value)}")
                        current_id = after_block.successors[0] if after_block.successors else None
                    else:
                        current_id = None

                else:
                    self._emit_return_from_cfg()
                    current_id = None

            # ── Case 4: straight line statements ──
            # Handles normal sequential code.
            else:
                self._emit_stmts(block.stmts)
                current_id = succs[0] if succs else None

        self.indent -= 1
        return "\n".join(self.output_lines)


# ─────────────────────────────────────────
# Entry function called from main.py
# ─────────────────────────────────────────
# Helper function used by main.py.
# Creates Emitter object and starts code generation.
def emit(cfg, converter, func_name="f", params=""):
    emitter = Emitter(cfg, converter)
    return emitter.emit(func_name=func_name, params=params)