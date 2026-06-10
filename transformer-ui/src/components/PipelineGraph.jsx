import { motion } from "framer-motion";

export default function PipelineGraph() {
  const stages = ["Parser", "AST", "CFG", "SSA", "Emitter"];

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45 }}
      className="bg-slate-900/70 backdrop-blur-xl border border-slate-800 rounded-2xl shadow-2xl overflow-hidden"
    >
      <div className="px-5 py-4 border-b border-slate-800 flex justify-between">
        <h2 className="text-white font-semibold">Transformation Pipeline</h2>
        <span className="text-xs text-cyan-400">live compiler stages</span>
      </div>

      <div className="p-6 flex items-center justify-between overflow-x-auto">
        {stages.map((stage, index) => (
          <div key={stage} className="flex items-center">
            <motion.div
              whileHover={{ scale: 1.05 }}
              className="bg-blue-600/20 border border-blue-500/40 text-blue-300 px-5 py-3 rounded-xl font-semibold shadow-lg"
            >
              {stage}
            </motion.div>

            {index < stages.length - 1 && (
              <div className="mx-4 text-slate-500 text-2xl">→</div>
            )}
          </div>
        ))}
      </div>
    </motion.div>
  );
}