import { useState, useEffect, useCallback, useRef } from "react";
import { Search, Download } from "lucide-react";
import { getLogs } from "../lib/api";

const getLevel = (log: string) => {
  if (log.includes("COMPLETED successfully")) return "SUCCESS";
  if (log.includes("MISSED")) return "ERROR";
  if (log.includes("Running") || log.includes("---")) return "INFO";
  if (log.includes("aged") || log.includes("arrived")) return "WARN";
  return "LOG";
};
const LEVEL_COLORS: Record<string, string> = {
  SUCCESS: "#10b981", ERROR: "#ef4444", INFO: "#6366f1", WARN: "#f59e0b", LOG: "#71717a",
};

export default function Logs() {
  const [logs, setLogs] = useState<string[]>([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState("ALL");
  const bottomRef = useRef<HTMLDivElement>(null);

  const fetchLogs = useCallback(async () => {
    try { const res = await getLogs(); setLogs(res.data); setError(null); }
    catch { setError("Cannot connect to backend."); } finally { setLoading(false); }
  }, []);

  useEffect(() => { fetchLogs(); const i = setInterval(fetchLogs, 3000); return () => clearInterval(i); }, [fetchLogs]);
  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: "smooth" }); }, [logs]);

  const filtered = logs.filter((log) => {
    const level = getLevel(log);
    return (search === "" || log.toLowerCase().includes(search.toLowerCase())) &&
      (filter === "ALL" || level === filter);
  });

  const handleExport = () => {
    const blob = new Blob([logs.join("\n")], { type: "text/plain" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob); a.download = `logs_${Date.now()}.txt`; a.click();
  };

  return (
    <div style={{ minHeight: "100vh", background: "#09090b" }}>
      <section className="pt-28 pb-12 px-6" style={{ background: "linear-gradient(160deg, #09090b, #18181b)" }}>
        <div className="max-w-7xl mx-auto">
          <p className="text-xs font-black tracking-widest mb-3" style={{ color: "#6366f1" }}>SYSTEM OUTPUT</p>
          <div className="flex justify-between items-end flex-wrap gap-6">
            <h1 className="text-5xl md:text-7xl font-black leading-none" style={{ color: "#fafafa" }}>
              EXECUTION<br /><span style={{ color: "#6366f1" }}>LOGS.</span>
            </h1>
            <button onClick={handleExport}
              className="flex items-center gap-2 px-6 py-3 rounded-full text-sm font-black tracking-widest"
              style={{ border: "1px solid #27272a", color: "#6366f1" }}>
              <Download size={16} /> EXPORT
            </button>
          </div>
          <p className="mt-4 text-lg" style={{ color: "#71717a" }}>{logs.length} entries — auto-refreshes every 3s</p>
        </div>
      </section>

      <section className="px-6 py-12">
        <div className="max-w-7xl mx-auto space-y-6">
          {error && <div className="p-4 rounded-xl text-sm" style={{ background: "#1a0a0a", color: "#f87171", border: "1px solid #3b0f0f" }}>⚠️ {error}</div>}

          <div className="flex gap-3 flex-wrap">
            <div className="relative flex-1 min-w-48">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2" size={16} style={{ color: "#71717a" }} />
              <input type="text" placeholder="Filter logs..." value={search} onChange={(e) => setSearch(e.target.value)}
                className="w-full pl-11 pr-4 py-3 rounded-xl text-sm focus:outline-none"
                style={{ background: "#18181b", border: "1px solid #27272a", color: "#fafafa" }} />
            </div>
            {["ALL", "INFO", "SUCCESS", "WARN", "ERROR"].map((lvl) => (
              <button key={lvl} onClick={() => setFilter(lvl)}
                className="px-4 py-3 rounded-xl text-xs font-black tracking-widest transition-all"
                style={{ background: filter === lvl ? "#6366f1" : "#18181b", color: filter === lvl ? "#fafafa" : "#71717a", border: "1px solid #27272a" }}>
                {lvl}
              </button>
            ))}
          </div>

          <div className="rounded-2xl overflow-hidden" style={{ border: "1px solid #27272a" }}>
            <div className="flex items-center gap-3 px-6 py-4 border-b" style={{ background: "#09090b", borderColor: "#27272a" }}>
              <div className="flex gap-2">
                {["#ef4444", "#f59e0b", "#6366f1"].map(c => <div key={c} className="w-3 h-3 rounded-full" style={{ background: c }} />)}
              </div>
              <span className="text-xs font-bold tracking-widest" style={{ color: "#71717a" }}>task-scheduler — console</span>
              <span className="ml-auto text-xs" style={{ color: "#27272a" }}>{filtered.length} entries</span>
            </div>
            <div className="p-6 font-mono text-xs space-y-1 min-h-96 max-h-screen overflow-y-auto" style={{ background: "#09090b" }}>
              {loading ? <p style={{ color: "#27272a" }}>Connecting...</p> :
                filtered.length === 0 ? <p style={{ color: "#27272a" }}>$ No logs match filter. Run scheduler first.</p> :
                filtered.map((log, i) => {
                  const level = getLevel(log);
                  return (
                    <div key={i} className="flex gap-4 group px-2 py-0.5 rounded hover:bg-white/5">
                      <span style={{ color: "#27272a" }} className="shrink-0 w-10 select-none">{String(i + 1).padStart(3, "0")}</span>
                      <span className="shrink-0 w-16 font-black" style={{ color: LEVEL_COLORS[level] }}>[{level}]</span>
                      <span style={{ color: LEVEL_COLORS[level] }}>{log}</span>
                    </div>
                  );
                })}
              <div ref={bottomRef} />
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
