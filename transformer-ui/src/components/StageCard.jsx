import { motion } from "framer-motion";

export default function StageCard({ title, description }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}

      className="
      bg-slate-900/70
      backdrop-blur-xl
      border border-slate-800
      rounded-2xl
      p-5
      hover:border-blue-500/40
      hover:shadow-blue-500/10
      hover:shadow-2xl
      transition-all duration-300
      hover:-translate-y-1
    "
    >
      <h3 className="text-white font-semibold text-lg">
        {title}
      </h3>

      <p className="text-slate-400 text-sm mt-2 leading-relaxed">
        {description}
      </p>
    </motion.div>
  );
}