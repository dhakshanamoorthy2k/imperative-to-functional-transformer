"""
cfg.py

This file builds the Control Flow Graph (CFG) of the input program.

What it does:
- Takes the AST produced by parser.py.
- Divides the program into basic blocks.
- Connects the blocks using successor edges.
- Handles assignments, return statements, if/else, while loops, and for loops.

Why it is needed:
- CFG shows the execution flow of the program.
- It is required before converting the program into SSA form.
- It helps identify branches, loops, merge points, and loop back edges.
"""

import ast
from dataclasses import dataclass, field

# ─────────────────────────────────────────
#  Data structures
# ─────────────────────────────────────────
# BasicBlock represents one node in the CFG.
# Each block contains:
# - id: unique block number
# - stmts: AST statements inside the block
# - successors: list of next blocks that can execute after this block

@dataclass
class BasicBlock:
    id: int
    stmts: list = field(default_factory=list)      # AST statement nodes
    successors: list = field(default_factory=list)  # list of block ids

# CFG stores all basic blocks of the program.
# It also remembers the entry block, exit block, and block counter.
class CFG:
    def __init__(self):
        self.blocks = {}       # id -> BasicBlock
        self.entry = None
        self.exit = None
        self._counter = 0

# Creates a new basic block.
# Every new block gets a unique id.
# The block is stored inside cfg.blocks.
# This is needed whenever the program has a new control-flow region.

    def new_block(self):
        """Creates a new empty BasicBlock and stores it"""
        b = BasicBlock(id=self._counter)
        self.blocks[self._counter] = b
        self._counter += 1
        return b

    def print_cfg(self):
        """Helper: prints all blocks so you can verify"""
        print("\n[CFG BLOCKS]")
        for bid, block in self.blocks.items():
            print(f"\n  Block {bid}:")
            print(f"    Successors: {block.successors}")
            print(f"    Statements:")
            for stmt in block.stmts:
                print(f"      - {ast.dump(stmt)}")

# ─────────────────────────────────────────
#  Main builder function
# ─────────────────────────────────────────
# This function used to build the CFG.
# It receives the AST tree from parser.py.
# It creates entry and exit blocks.
# Then it processes all statements inside the function body.

def build_cfg(tree) -> CFG:
    cfg = CFG()

    # Every CFG has an entry and exit block
    entry_block = cfg.new_block()   # Block 0
    exit_block  = cfg.new_block()   # Block 1

    cfg.entry = entry_block.id
    cfg.exit  = exit_block.id

    # The project assumes the input contains one function.
    # tree.body[0] gets the first function definition.
    # func.body gives all statements inside that function.
   
    func = tree.body[0]  # first function def
    stmts = func.body    # statements inside the function

    # This is the core CFG-building function.
    # It reads statements one by one.
    # Simple statements stay in the current block.
    # Branches and loops create new blocks.
    _process_stmts(stmts, entry_block, exit_block, cfg)

    return cfg

# ─────────────────────────────────────────
#  Statement processor — the core logic
# ─────────────────────────────────────────

def _process_stmts(stmts, current_block, exit_block, cfg):
    """
    Walks through statements one by one.
    Puts them in the current block.
    When it hits a branch or loop, creates new blocks.
    """
    for stmt in stmts:

        # Assignment statements do not change control flow.
        if isinstance(stmt, ast.Assign):
            # Simple assignment: x = 1
            # Just add it to the current block
            current_block.stmts.append(stmt)

        # Converts augmented assignment into normal assignment.
        # Example:x += 1
        # becomes:x = x + 1
        #This is needed because SSA conversion works better with normal assignments.
        elif isinstance(stmt, ast.AugAssign):
            new_stmt = ast.Assign(
                targets=[stmt.target],
                value=ast.BinOp(
                    left=stmt.target,
                    op=stmt.op,
                    right=stmt.value
                ),
                lineno=stmt.lineno,
                col_offset=stmt.col_offset
            )
            current_block.stmts.append(new_stmt)

        # Return statement ends the function execution.
        # The return is added to the current block.
        # Then the current block is connected to the exit block.
        elif isinstance(stmt, ast.Return):
            # return y
            # Add to current block, connect to exit
            current_block.stmts.append(stmt)
            if exit_block.id not in current_block.successors:
                current_block.successors.append(exit_block.id)

        # For an if/else statement, the CFG needs separate paths.
        # It creates:
        # - then_block: statements when condition is true
        # - else_block: statements when condition is false
        # - merge_block: where both branches join again
        elif isinstance(stmt, ast.If):
            # if x > 0: ... else: ...
            # Create 3 new blocks: then, else, merge
            then_block  = cfg.new_block()
            else_block  = cfg.new_block()
            merge_block = cfg.new_block()

            # The condition is stored in the current block.
            # From this condition block, execution can go to either:
            # - then block - else block
            current_block.stmts.append(stmt.test)
            current_block.successors = [then_block.id, else_block.id]

            # Process then branch
            _process_stmts(stmt.body, then_block, merge_block, cfg)

            # Process else branch
            if stmt.orelse:
                _process_stmts(stmt.orelse, else_block, merge_block, cfg)

            # Connect then/else to merge if not already connected
            if not then_block.successors:
                then_block.successors = [merge_block.id]
            if not else_block.successors:
                else_block.successors = [merge_block.id]

            # Continue processing after the if/else from merge block
            current_block = merge_block
            
        # For a while loop, the CFG creates:
        # - header_block: checks the loop condition
        # - body_block: contains loop body statements
        # - after_block: continues after the loop ends
        elif isinstance(stmt, ast.While):
            # while i < n: ...
            # Creates 3 blocks: header (condition), body, after
            header_block = cfg.new_block()
            body_block   = cfg.new_block()
            after_block  = cfg.new_block()

            # Connect current to header
            current_block.successors = [header_block.id]

            header_block.stmts.append(stmt.test)

            # If condition is true, control goes to loop body.
            # If condition is false, control goes to after_loop block.
            header_block.successors = [body_block.id, after_block.id]

            # Process loop body — exits back to header (back-edge)
            _process_stmts(stmt.body, body_block, header_block, cfg)
            if not body_block.successors:

                # This creates the loop back edge.
                # After executing the body, control returns to the header condition.
                body_block.successors = [header_block.id]

            # Continue after the loop
            current_block = after_block

        elif isinstance(stmt, ast.For):

            # Handles for-loops using range().
            # Example:
            # for i in range(n):
            #The code converts it internally into:
            # i = 0
            # while i < n:
            #     ...
            # i = i + 1
            #
            # This makes it easier for CFG and SSA processing.

            if (
                isinstance(stmt.iter, ast.Call)
                and isinstance(stmt.iter.func, ast.Name)
                and stmt.iter.func.id == "range"
            ):
                init_stmt = ast.Assign(
                    targets=[ast.Name(id=stmt.target.id, ctx=ast.Store())],
                    value=ast.Constant(value=0),
                    lineno=stmt.lineno,
                    col_offset=stmt.col_offset
                )
                ast.fix_missing_locations(init_stmt)
                current_block.stmts.append(init_stmt)

                header_block = cfg.new_block()
                body_block = cfg.new_block()
                after_block = cfg.new_block()

                current_block.successors = [header_block.id]

                range_arg = stmt.iter.args[0]

                condition = ast.Compare(
                    left=ast.Name(id=stmt.target.id, ctx=ast.Load()),
                    ops=[ast.Lt()],
                    comparators=[range_arg]
                )
                ast.fix_missing_locations(condition)

                header_block.stmts.append(condition)
                header_block.successors = [body_block.id, after_block.id]

                _process_stmts(stmt.body, body_block, header_block, cfg)

                increment = ast.Assign(
                    targets=[ast.Name(id=stmt.target.id, ctx=ast.Store())],
                    value=ast.BinOp(
                        left=ast.Name(id=stmt.target.id, ctx=ast.Load()),
                        op=ast.Add(),
                        right=ast.Constant(value=1)
                    ),
                    lineno=stmt.lineno,
                    col_offset=stmt.col_offset
                )
                ast.fix_missing_locations(increment)

                body_block.stmts.append(increment)

                if not body_block.successors:
                    body_block.successors = [header_block.id]

                current_block = after_block

            # Handles collection-based for loops.
            # Example:
            # for x in items:
            #
            # This is important for detecting functional patterns like:
            # - map()- filter()- reduce()
            elif isinstance(stmt.iter, ast.Name):

                header_block = cfg.new_block()
                body_block = cfg.new_block()
                after_block = cfg.new_block()

                current_block.successors = [header_block.id]

                header_block.stmts.append(stmt)
                header_block.successors = [body_block.id, after_block.id]

                _process_stmts(stmt.body, body_block, header_block, cfg)

                if not body_block.successors:
                    body_block.successors = [header_block.id]

                current_block = after_block

            else:
                print(f"[CFG WARNING] Unsupported for-loop iterator: {ast.dump(stmt.iter)}")

        # Expression statements are added directly to the block.
        # Example: result.append(x)
        # This is important for detecting map/filter patterns later.
        elif isinstance(stmt, ast.Expr):
            current_block.stmts.append(stmt)

        else:
            print(f"[CFG WARNING] Unhandled statement type: {type(stmt).__name__}")
            
    # If a block has no successor, connect it to the exit block.
    # This prevents disconnected blocks in the CFG.    
    if not current_block.successors and current_block.id != exit_block.id:
        current_block.successors.append(exit_block.id)