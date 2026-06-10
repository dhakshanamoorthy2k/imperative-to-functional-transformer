import Editor from "@monaco-editor/react";

export default function CodeEditor({ code, setCode }) {
  return (
    <div
      className="
      bg-slate-900/70
      backdrop-blur-xl
      border border-slate-800
      rounded-2xl
      overflow-hidden
      shadow-2xl
      min-w-0
    "
    >
      <div className="px-4 py-3 border-b border-slate-800 flex justify-between">
        <h2 className="text-white font-semibold">
          Input Python Code
        </h2>

        <span className="text-slate-500 text-sm">
          imperative.py
        </span>
      </div>

      <Editor
        height="420px"
        language="python"
        theme="vs-dark"
        value={code}
        onChange={(value) => setCode(value)}
        options={{
          minimap: { enabled: false },
          fontSize: 14,
          smoothScrolling: true,
          padding: {
            top: 16,
          },
          scrollBeyondLastLine: false,
          fontFamily: "Fira Code, monospace",
        }}
      />
    </div>
  );
}