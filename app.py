import ast
import io
import contextlib

from flask import Flask, request, jsonify
from flask_cors import CORS

from project.parser import parse, print_ast
from project.cfg import build_cfg
from project.ssa import to_ssa
from project.emitter import emit

app = Flask(__name__)
CORS(app)


def capture_output(func, *args, **kwargs):
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        func(*args, **kwargs)
    return buffer.getvalue()


def get_function_info(code):
    tree = ast.parse(code)

    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            func_name = node.name
            params = ", ".join(arg.arg for arg in node.args.args)
            return func_name, params

    return "f", ""

def format_cfg_clean(cfg):
    lines = ["[CFG BLOCKS]"]

    for bid, block in cfg.blocks.items():
        lines.append(f"\nBlock {bid}:")
        lines.append(f"  Successors: {block.successors}")
        lines.append("  Statements:")

        if not block.stmts:
            lines.append("    <empty>")
        else:
            for stmt in block.stmts:
                try:
                    lines.append(f"    {ast.unparse(stmt)}")
                except Exception:
                    lines.append(f"    {stmt}")

    return "\n".join(lines)

@app.route("/transform", methods=["POST"])
def transform():
    try:
        data = request.get_json()
        code = data.get("code", "")

        func_name, params = get_function_info(code)

        tree = parse(code)
        ast_output = capture_output(print_ast, tree)

        cfg = build_cfg(tree)
        cfg_output = format_cfg_clean(cfg)

        cfg, converter = to_ssa(cfg)
        ssa_output = capture_output(converter.print_ssa)

        functional_output = emit(
            cfg,
            converter,
            func_name=func_name,
            params=params
        )

        return jsonify({
            "ast": ast_output,
            "cfg": cfg_output,
            "ssa": ssa_output,
            "functional": functional_output
        })

    except Exception as e:
        return jsonify({
            "ast": "Error while generating AST",
            "cfg": "Error while generating CFG",
            "ssa": "Error while generating SSA",
            "functional": f"Backend error:\n{str(e)}"
        }), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)