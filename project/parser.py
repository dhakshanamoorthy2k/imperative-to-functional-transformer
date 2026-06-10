import ast

def parse(source_code: str):
    """
    This function is the first stage of the project.

    What it does:
    - Takes Python source code as a string.
    - Uses ast.parse() to convert the source code into an Abstract Syntax Tree.

    Why it is needed:
    - The rest of the project cannot work directly on raw text code.
    - AST gives a structured representation of the program.
    - CFG and SSA stages use this AST for analysis.
    """
    try:
        tree = ast.parse(source_code)
        return tree
    except SyntaxError as e:
        print(f"[PARSER ERROR] {e}")
        return None


def print_ast(tree):
    """
    Helper function.

    What it does:
    - Prints the AST in readable format.
    - Helps to verify whether parsing was successful.
    - Useful for debugging and presentation.
    """
    print(ast.dump(tree, indent=2))