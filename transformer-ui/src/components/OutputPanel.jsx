export default function OutputPanel({ title, content, color = "text-slate-300" }) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
      <div className="px-4 py-3 border-b border-slate-800">
        <h2 className="text-white font-semibold">{title}</h2>
      </div>

      <pre className={`p-4 text-sm overflow-auto h-[260px] bg-slate-950 ${color}`}>
        {content}
      </pre>
    </div>
  );
}