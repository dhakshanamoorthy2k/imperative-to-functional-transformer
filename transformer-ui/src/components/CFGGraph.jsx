import { ReactFlow, Background } from "@xyflow/react";

function parseCFG(cfgText) {
  const blocks = [];
  const edges = [];

  const blockRegex = /Block\s+(\d+):([\s\S]*?)(?=\n\s*Block\s+\d+:|$)/g;
  let match;

  while ((match = blockRegex.exec(cfgText)) !== null) {
    const id = match[1];
    const content = match[2];

    const successorsMatch = content.match(/Successors:\s*\[([^\]]*)\]/);
    const successors = successorsMatch
      ? successorsMatch[1].split(",").map((s) => s.trim()).filter(Boolean)
      : [];

    const label = `Block ${id}\n${content
      .replace(/Successors:.*/g, "")
      .replace(/Statements:/g, "")
      .trim()}`;

    blocks.push({
      id,
      position: {
        x: Number(id) * 240,
        y: Number(id) % 2 === 0 ? 80 : 220,
      },
      data: { label },
      style: {
        background: "#020617",
        color: "white",
        border: "1px solid #06b6d4",
        borderRadius: "14px",
        padding: "12px",
        whiteSpace: "pre-line",
        minWidth: "180px",
      },
    });

    successors.forEach((target) => {
      edges.push({
        id: `e${id}-${target}`,
        source: id,
        target,
        animated: true,
        label: Number(target) <= Number(id) ? "loop back" : "",
      });
    });
  }

  return { nodes: blocks, edges };
}

export default function CFGGraph({ cfg }) {
  const { nodes, edges } = parseCFG(cfg || "");

  return (
    <div className="bg-slate-900/70 backdrop-blur-xl border border-slate-800 rounded-2xl shadow-2xl overflow-hidden max-w-full">
      <div className="px-5 py-4 border-b border-slate-800 flex justify-between">
        <h2 className="text-white font-semibold">CFG Visualization</h2>
        <span className="text-xs text-cyan-400">dynamic backend CFG</span>
      </div>

      <div className="h-[420px] bg-slate-950">
        {nodes.length > 0 ? (
          <ReactFlow nodes={nodes} edges={edges} fitView>
            <Background />
          </ReactFlow>
        ) : (
          <div className="p-6 text-slate-400">
            Click Transform Code to generate CFG visualization.
          </div>
        )}
      </div>
    </div>
  );
}