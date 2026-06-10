export default function Header({
  sidebarOpen,
  setSidebarOpen,
  theme,
  setTheme,
}) {
  return (
    <div
      className="
      border-b border-slate-800
      bg-slate-950/80
      backdrop-blur-xl
      px-6 py-4
      flex items-center justify-between
      sticky top-0 z-50
      "
    >
      <div className="flex items-center gap-4">
        <button
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="
          bg-slate-900
          border border-slate-700
          hover:border-blue-500/50
          text-slate-300
          hover:text-white
          rounded-xl
          px-3 py-2
          transition
          "
        >
          {sidebarOpen ? "☰" : "→"}
        </button>

        <div className="bg-blue-600 p-2 rounded-xl text-white text-xl">
          {"</>"}
        </div>

        <div>
          <h1 className="text-white text-xl font-bold">
            Imperative to Functional Transformer
          </h1>
          <p className="text-slate-400 text-sm">
            Parser → AST → CFG → SSA → Functional Output
          </p>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <button
          onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
          className="
          bg-slate-900
          border border-slate-700
          hover:border-cyan-500/50
          text-slate-300
          hover:text-white
          rounded-xl
          px-3 py-2
          transition
          "
        >
          {theme === "dark" ? "☀️ Light" : "🌙 Dark"}
        </button>

        <span className="text-xs px-3 py-1 rounded-full bg-green-500/10 text-green-400 border border-green-500/30">
          Compiler Pipeline
        </span>
      </div>
    </div>
  );
}