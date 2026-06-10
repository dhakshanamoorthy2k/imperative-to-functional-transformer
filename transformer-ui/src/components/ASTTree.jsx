import { motion } from "framer-motion";

function parseAST(astText) {
  if (!astText) return [];

  return astText
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean)
    .filter((line) =>
      line.includes("Module") ||
      line.includes("FunctionDef") ||
      line.includes("Assign") ||
      line.includes("For") ||
      line.includes("While") ||
      line.includes("If") ||
      line.includes("Return") ||
      line.includes("Name") ||
      line.includes("BinOp") ||
      line.includes("Call") ||
      line.includes("Constant")
    );
}

function ASTNode({ label, index }) {
  const colors = [
    "border-blue-500/40 text-blue-300",
    "border-cyan-500/40 text-cyan-300",
    "border-green-500/40 text-green-300",
    "border-purple-500/40 text-purple-300",
    "border-amber-500/40 text-amber-300",
  ];

  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      className={`
        inline-block
        bg-slate-950
        border
        ${colors[index % colors.length]}
        px-3 py-2
        rounded-xl
        text-sm
        font-mono
        mb-3
      `}
    >
      {label}
    </motion.div>
  );
}

export default function ASTTree({ ast }) {
  const astNodes = parseAST(ast);

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45 }}
      className="bg-slate-900/70 backdrop-blur-xl border border-slate-800 rounded-2xl shadow-2xl overflow-hidden max-w-full"
    >
      <div className="px-5 py-4 border-b border-slate-800 flex justify-between">
        <h2 className="text-white font-semibold">AST Tree Visualization</h2>
        <span className="text-xs text-cyan-400">dynamic backend AST</span>
      </div>

      <div className="p-5 bg-slate-950 h-[420px] overflow-auto">
        {astNodes.length > 0 ? (
          <div className="space-y-2">
            {astNodes.map((node, index) => (
              <div
                key={index}
                className="border-l border-slate-700 pl-4"
                style={{ marginLeft: `${Math.min(index, 8) * 16}px` }}
              >
                <ASTNode label={node} index={index} />
              </div>
            ))}
          </div>
        ) : (
          <div className="text-slate-400">
            Click Transform Code to generate AST visualization.
          </div>
        )}
      </div>
    </motion.div>
  );
}