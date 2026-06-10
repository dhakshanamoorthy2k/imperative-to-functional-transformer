export default function Sidebar({ scrollToSection, openTab, sidebarOpen }) {
  const menuItems = [
    { label: "Dashboard", icon: "▣", action: () => scrollToSection("top") },
    { label: "Parser", icon: "↳", action: () => scrollToSection("pipeline") },
    { label: "AST", icon: "🌳", action: () => scrollToSection("ast") },
    { label: "CFG", icon: "⛓", action: () => scrollToSection("cfg") },
    {
      label: "SSA",
      icon: "Φ",
      action: () => {
        scrollToSection("ssa");
        openTab("SSA");
      },
    },
    { label: "Emitter", icon: "λ", action: () => scrollToSection("output") },
  ];

  return (
    <aside
      className={`
        min-h-screen
        bg-slate-950
        border-r
        border-slate-800
        px-4
        py-5
        hidden
        lg:block
        transition-all
        duration-300
        ${sidebarOpen ? "w-64" : "w-20"}
      `}
    >
      <div className="mb-8">
        <div className="text-blue-400 text-2xl font-bold">
          {sidebarOpen ? "λ Transformer" : "λ"}
        </div>

        {sidebarOpen && (
          <p className="text-slate-500 text-sm mt-1">
            Compiler visualization tool
          </p>
        )}
      </div>

      <nav className="space-y-2">
        {menuItems.map((item) => (
          <button
            key={item.label}
            onClick={item.action}
            className="
              w-full
              flex
              items-center
              gap-3
              px-4
              py-3
              rounded-xl
              text-sm
              cursor-pointer
              transition
              text-slate-400
              hover:bg-slate-900
              hover:text-white
            "
          >
            <span>{item.icon}</span>

            {sidebarOpen && <span>{item.label}</span>}
          </button>
        ))}
      </nav>

      {sidebarOpen && (
        <div className="mt-10 bg-slate-900 border border-slate-800 rounded-2xl p-4">
          <p className="text-slate-400 text-sm">Current Pipeline</p>
          <p className="text-white font-semibold mt-1">
            AST → CFG → SSA → Functional
          </p>
        </div>
      )}
    </aside>
  );
}