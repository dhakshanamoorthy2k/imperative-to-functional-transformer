
import { motion, AnimatePresence } from "framer-motion";

export default function TabsPanel({ ast, cfg, ssa, activeTab, setActiveTab }) {
  

  const tabs = {
    AST: ast,
    CFG: cfg,
    SSA: ssa,
  };

  return (
    <div className="bg-slate-900/70 backdrop-blur-xl border border-slate-800 rounded-2xl overflow-hidden shadow-2xl">
      <div className="flex border-b border-slate-800 bg-slate-950/40">
        {Object.keys(tabs).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`relative px-6 py-3 text-sm font-semibold transition ${
              activeTab === tab
                ? "text-white"
                : "text-slate-400 hover:text-white"
            }`}
          >
            {activeTab === tab && (
              <motion.div
                layoutId="activeTab"
                className="absolute inset-0 bg-blue-600 rounded-none"
                transition={{ type: "spring", stiffness: 300, damping: 30 }}
              />
            )}

            <span className="relative z-10">{tab}</span>
          </button>
        ))}
      </div>

      <AnimatePresence mode="wait">
        <motion.pre
          key={activeTab}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -8 }}
          transition={{ duration: 0.2 }}
          className="p-5 h-[320px] overflow-auto bg-slate-950 text-slate-300 text-sm font-mono"
        >
          {tabs[activeTab]}
        </motion.pre>
      </AnimatePresence>
    </div>
  );
}