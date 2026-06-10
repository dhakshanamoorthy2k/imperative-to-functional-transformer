export default function ExportButtons({ functional, ast, cfg, ssa }) {
  function downloadFile(filename, content) {
    const blob = new Blob([content], { type: "text/plain" });
    const url = URL.createObjectURL(blob);

    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    link.click();

    URL.revokeObjectURL(url);
  }

  return (
    <div className="bg-slate-900/70 backdrop-blur-xl border border-slate-800 rounded-2xl shadow-2xl p-5">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-white font-semibold">Export Results</h2>
          <p className="text-slate-400 text-sm">
            Download generated compiler outputs
          </p>
        </div>
      </div>

      <div className="grid grid-cols-4 gap-4">
        <button
          onClick={() => downloadFile("functional_output.py", functional)}
          className="bg-blue-600 hover:bg-blue-700 transition rounded-xl py-3 font-semibold"
        >
          Export Functional Code
        </button>

        <button
          onClick={() => downloadFile("ast_output.txt", ast)}
          className="bg-slate-800 hover:bg-slate-700 transition rounded-xl py-3 font-semibold"
        >
          Export AST
        </button>

        <button
          onClick={() => downloadFile("cfg_output.txt", cfg)}
          className="bg-slate-800 hover:bg-slate-700 transition rounded-xl py-3 font-semibold"
        >
          Export CFG
        </button>

        <button
          onClick={() => downloadFile("ssa_output.txt", ssa)}
          className="bg-slate-800 hover:bg-slate-700 transition rounded-xl py-3 font-semibold"
        >
          Export SSA
        </button>
      </div>
    </div>
  );
}