import { useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";

import SSAGraph from "./components/SSAGraph";
import Sidebar from "./components/Sidebar";
import TabsPanel from "./components/TabsPanel";
import Header from "./components/Header";
import CodeEditor from "./components/CodeEditor";
import CodeOutput from "./components/CodeOutput";
import PipelineGraph from "./components/PipelineGraph";
import StageCard from "./components/StageCard";
import CFGGraph from "./components/CFGGraph";
import ASTTree from "./components/ASTTree";
import ExportButtons from "./components/ExportButtons";

export default function App() {
  const topRef = useRef(null);
  const pipelineRef = useRef(null);
  const outputRef = useRef(null);
  const cfgRef = useRef(null);
  const ssaRef = useRef(null);
  const astRef = useRef(null);

  const [sidebarOpen, setSidebarOpen] = useState(true);

  const [code, setCode] = useState(`def f(items):
    result = []
    for x in items:
        result.append(x * 2)
    return result`);

  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState("AST");
  const [theme, setTheme] = useState("dark");

  const [output, setOutput] = useState({
    ast: "AST output will appear after transformation.",
    cfg: "CFG blocks will appear after transformation.",
    ssa: "SSA output will appear after transformation.",
    functional: "Functional code will appear here.",
  });

  function scrollToSection(section) {
    const refs = {
      top: topRef,
      pipeline: pipelineRef,
      output: outputRef,
      cfg: cfgRef,
      ssa: ssaRef,
      ast: astRef,
    };

    refs[section]?.current?.scrollIntoView({
      behavior: "smooth",
      block: "start",
    });
  }

  async function handleTransform() {
    setLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:5000/transform", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ code }),
      });

      const data = await response.json();

      setOutput({
        ast: data.ast,
        cfg: data.cfg,
        ssa: data.ssa,
        functional: data.functional,
      });
    } catch (error) {
      console.error(error);

      setOutput({
        ast: "Backend connection failed.",
        cfg: "Backend connection failed.",
        ssa: "Backend connection failed.",
        functional: "Make sure Flask backend is running.",
      });
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    function handleKeyDown(e) {
      if (e.ctrlKey && e.key === "Enter") {
        e.preventDefault();
        handleTransform();
      }

      if (e.ctrlKey && e.key === "1") {
        e.preventDefault();
        setActiveTab("AST");
        scrollToSection("ast");
      }

      if (e.ctrlKey && e.key === "2") {
        e.preventDefault();
        setActiveTab("CFG");
        scrollToSection("cfg");
      }

      if (e.ctrlKey && e.key === "3") {
        e.preventDefault();
        setActiveTab("SSA");
        scrollToSection("ssa");
      }
    }

    window.addEventListener("keydown", handleKeyDown);

    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div
      ref={topRef}
      className={`min-h-screen flex ${
        theme === "dark"
          ? "bg-slate-950 text-white"
          : "bg-slate-100 text-slate-950"
      }`}
    >
      <Sidebar
        scrollToSection={scrollToSection}
        openTab={setActiveTab}
        sidebarOpen={sidebarOpen}
      />

      <div className="flex-1 min-w-0 overflow-x-hidden">
        <Header
          sidebarOpen={sidebarOpen}
          setSidebarOpen={setSidebarOpen}
          theme={theme}
          setTheme={setTheme}
        />

        <motion.main
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5 }}
          className="p-6 space-y-6 overflow-x-hidden"
        >
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
            <StageCard
              title="Parser"
              description="Converts Python code into AST."
            />

            <StageCard
              title="CFG Builder"
              description="Creates control-flow blocks."
            />

            <StageCard
              title="SSA Converter"
              description="Renames variables uniquely."
            />

            <StageCard
              title="Emitter"
              description="Generates functional-style code."
            />
          </div>

          <div ref={outputRef} className="grid grid-cols-1 xl:grid-cols-2 gap-6 min-w-0">
            <div>
              <CodeEditor code={code} setCode={setCode} />

              <button
                onClick={handleTransform}
                disabled={loading}
                className="
                mt-4 w-full bg-gradient-to-r from-blue-600 to-cyan-500
                hover:scale-[1.02] hover:shadow-cyan-500/30
                transition-all duration-300 rounded-2xl py-3
                font-semibold shadow-xl disabled:opacity-60
                disabled:cursor-not-allowed
                "
              >
                {loading ? "Transforming..." : "Transform Code"}
              </button>
            </div>

            <CodeOutput content={output.functional} />
          </div>

          <div ref={pipelineRef}>
            <PipelineGraph />
          </div>

          <div ref={cfgRef}>
            <CFGGraph cfg={output.cfg} />
          </div>

          <div ref={ssaRef}>
            <SSAGraph ssa={output.ssa} />
          </div>

          <div ref={astRef}>
            <ASTTree ast={output.ast} />
          </div>

          <TabsPanel
            ast={output.ast}
            cfg={output.cfg}
            ssa={output.ssa}
            activeTab={activeTab}
            setActiveTab={setActiveTab}
          />

          <ExportButtons
            functional={output.functional}
            ast={output.ast}
            cfg={output.cfg}
            ssa={output.ssa}
          />
        </motion.main>
      </div>
    </div>
  );
}