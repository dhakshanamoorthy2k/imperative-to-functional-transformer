import { motion } from "framer-motion";

function parseSSA(ssaText) {
  if (!ssaText) return [];

  return ssaText
    .split("\n")
    .map((line) => line.trim())
    .filter((line) => line.length > 0)
    .filter((line) => !line.startsWith("["))
    .map((line, index) => ({
      id: index,
      title: line.includes("=") ? line.split("=")[0].trim() : `step_${index + 1}`,
      value: line.includes("=") ? line.split("=").slice(1).join("=").trim() : line,
    }));
}

function SSANode({ title, value, index }) {
  const colors = [
    "border-blue-500/40",
    "border-cyan-500/40",
    "border-green-500/40",
    "border-purple-500/40",
    "border-amber-500/40",
  ];

  return (
    <motion.div
      whileHover={{ scale: 1.03 }}
      className={`
        border ${colors[index % colors.length]}
        bg-slate-950
        rounded-2xl
        px-5 py-4
        shadow-xl
        min-w-[240px]
      `}
    >
      <div className="text-slate-400 text-xs mb-2">SSA Assignment</div>
      <div className="text-white font-mono text-sm">{title}</div>
      <div className="text-cyan-400 font-mono text-sm mt-2">{value}</div>
    </motion.div>
  );
}

export default function SSAGraph({ ssa }) {
  const nodes = parseSSA(ssa);

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45 }}
      className="bg-slate-900/70 backdrop-blur-xl border border-slate-800 rounded-2xl shadow-2xl overflow-hidden max-w-full"
    >
      <div className="px-5 py-4 border-b border-slate-800 flex justify-between">
        <h2 className="text-white font-semibold">SSA Visualization</h2>
        <span className="text-xs text-cyan-400">dynamic SSA form</span>
      </div>

      <div className="p-6 bg-slate-950 overflow-x-auto max-w-full">
        {nodes.length > 0 ? (
          <div className="flex items-center gap-5 w-max">
            {nodes.map((node, index) => (
              <div key={node.id} className="flex items-center gap-5">
                <SSANode
                  title={node.title}
                  value={node.value}
                  index={index}
                />

                {index < nodes.length - 1 && (
                  <div className="text-slate-500 text-2xl">→</div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="text-slate-400">
            Click Transform Code to generate SSA visualization.
          </div>
        )}
      </div>
    </motion.div>
  );
}