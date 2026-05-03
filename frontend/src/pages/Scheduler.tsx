import { useState, useEffect, useCallback } from "react";
import { motion } from "framer-motion";
import { Play, RotateCcw, CheckCircle, ChevronRight } from "lucide-react";
import { runScheduler, resetScheduler, getTasks } from "../lib/api";
import type { TaskData } from "../lib/api";

const ALGORITHMS = ["Priority", "SJF", "EDF"] as const;
const ALGO_DESC: Record<string, string> = {
  Priority: "Priority order with anti-starvation aging.",
  SJF: "Shortest Job First — smallest exec time next.",
  EDF: "Earliest Deadline First.",
};
const STATUS_COLORS: Record<string, string> = {
  PENDING: "#f59e0b", RUNNING: "#6366f1", COMPLETED: "#10b981",
  MISSED: "#ef4444", DELETED: "#71717a",
};

export default function Scheduler() {
  const [algo, setAlgo] = useState("Priority");
  const [running, setRunning] = useState(false);
  const [resetting, setResetting] = useState(false);
  const [result, setResult] = useState<{ log: string[]; tasks: TaskData[]; current_time: number } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [taskCount, setTaskCount] = useState<number | null>(null);

  const fetchTasks = useCallback(async () => {
    try { const res = await getTasks(); setTaskCount(res.data.length); } catch {}
  }, []);

  useEffect(() => { fetchTasks(); }, [fetchTasks]);

  const handleRun = async () => {
    setRunning(true); setError(null); setResult(null);
    try {
      const res = await runScheduler(algo);
      setResult({ log: res.data.log, tasks: res.data.tasks, current_time: res.data.current_time });
      fetchTasks();
    } catch (err: any) {
      setError(err.response?.data?.error || "Simulation failed.");
    } finally { setRunning(false); }
  };

  const handleReset = async () => {
    if (!confirm("Reset all tasks and logs?")) return;
    setResetting(true);
    try { await resetScheduler(); setResult(null); setError(null); fetchTasks(); }
    catch { setError("Reset failed."); } finally { setResetting(false); }
  };

  return (
    <div style={{ minHeight: "100vh", background: "#09090b" }}>
      <section className="pt-28 pb-12 px-6" style={{ background: "linear-gradient(160deg, #09090b, #18181b)" }}>
        <div className="max-w-7xl mx-auto">
          <p className="text-xs font-black tracking-widest mb-3" style={{ color: "#6366f1" }}>SCHEDULER CONTROL</p>
          <div className="flex justify-between items-end flex-wrap gap-6">
            <h1 className="text-5xl md:text-7xl font-black leading-none" style={{ color: "#fafafa" }}>
              RUN THE<br /><span style={{ color: "#6366f1" }}>ENGINE.</span>
            </h1>
            <button onClick={handleReset} disabled={resetting}
              className="flex items-center gap-2 px-5 py-3 rounded-full text-xs font-black tracking-widest disabled:opacity-60"
              style={{ border: "1px solid #27272a", color: "#71717a" }}>
              <RotateCcw size={14} /> {resetting ? "RESETTING..." : "RESET"}
            </button>
          </div>
          <p className="mt-4 text-lg" style={{ color: "#71717a" }}>
            {taskCount !== null ? `${taskCount} tasks loaded` : "Loading..."}
          </p>
        </div>
      </section>

      <section className="px-6 py-12">
        <div className="max-w-7xl mx-auto space-y-8">
          {error && <div className="p-4 rounded-xl text-sm" style={{ background: "#1a0a0a", color: "#f87171", border: "1px solid #3b0f0f" }}>⚠️ {error}</div>}

          <div>
            <p className="text-xs font-black tracking-widest mb-4" style={{ color: "#6366f1" }}>SELECT ALGORITHM</p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {ALGORITHMS.map((a) => (
                <motion.button key={a} onClick={() => setAlgo(a)} whileHover={{ y: -4 }}
                  className="p-6 rounded-2xl text-left"
                  style={{ background: algo === a ? "#6366f1" : "#18181b", border: `2px solid ${algo === a ? "#6366f1" : "#27272a"}` }}>
                  <p className="text-lg font-black mb-2" style={{ color: algo === a ? "#fafafa" : "#fafafa" }}>{a}</p>
                  <p className="text-xs" style={{ color: algo === a ? "#e0e7ff" : "#71717a" }}>{ALGO_DESC[a]}</p>
                  {algo === a && <ChevronRight size={18} className="mt-3" style={{ color: "#fafafa" }} />}
                </motion.button>
              ))}
            </div>
          </div>

          <motion.button onClick={handleRun} disabled={running} whileHover={{ scale: 1.01 }} whileTap={{ scale: 0.98 }}
            className="w-full py-5 rounded-2xl text-lg font-black tracking-widest flex items-center justify-center gap-3 disabled:opacity-60"
            style={{ background: running ? "#27272a" : "#6366f1", color: "#fafafa", border: running ? "1px solid #3f3f46" : "none" }}>
            <Play size={22} />
            {running ? "RUNNING SIMULATION..." : `RUN ${algo.toUpperCase()} SCHEDULER`}
          </motion.button>

          {result && (
            <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
              <div className="p-5 rounded-2xl flex items-center gap-3"
                style={{ background: "#052e16", border: "1px solid #14532d" }}>
                <CheckCircle size={20} style={{ color: "#10b981" }} />
                <div>
                  <p className="text-sm font-black" style={{ color: "#10b981" }}>SIMULATION COMPLETE — T={result.current_time}</p>
                  <p className="text-xs" style={{ color: "#71717a" }}>
                    {result.tasks.filter(t => t.status === "COMPLETED").length} completed, {result.tasks.filter(t => t.status === "MISSED").length} missed
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="p-6 rounded-2xl" style={{ background: "#18181b", border: "1px solid #27272a" }}>
                  <p className="text-xs font-black tracking-widest mb-4" style={{ color: "#6366f1" }}>FINAL TASK STATE</p>
                  <div className="space-y-2 max-h-96 overflow-y-auto pr-2">
                    {result.tasks.map((t) => (
                      <div key={t.task_id} className="flex items-center justify-between p-3 rounded-xl" style={{ background: "#09090b" }}>
                        <div>
                          <span className="font-mono text-xs font-black" style={{ color: "#6366f1" }}>{t.task_id}</span>
                          <span className="text-xs ml-2" style={{ color: "#71717a" }}>{t.name}</span>
                        </div>
                        <span className="text-xs font-black px-2 py-0.5 rounded-full"
                          style={{ background: (STATUS_COLORS[t.status] || "#71717a") + "22", color: STATUS_COLORS[t.status] || "#71717a" }}>
                          {t.status}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="rounded-2xl overflow-hidden" style={{ background: "#09090b", border: "1px solid #27272a" }}>
                  <div className="flex items-center gap-3 px-4 py-3 border-b" style={{ borderColor: "#27272a" }}>
                    <div className="flex gap-2">
                      {["#ef4444", "#f59e0b", "#6366f1"].map(c => <div key={c} className="w-3 h-3 rounded-full" style={{ background: c }} />)}
                    </div>
                    <span className="text-xs font-bold" style={{ color: "#71717a" }}>execution log</span>
                  </div>
                  <div className="p-4 font-mono text-xs space-y-1 max-h-96 overflow-y-auto">
                    {result.log.map((line, i) => (
                      <p key={i} style={{
                        color: line.includes("COMPLETED") ? "#10b981" : line.includes("Running") ? "#6366f1" :
                          line.includes("MISSED") ? "#ef4444" : line.includes("aged") ? "#f59e0b" :
                          line.includes("---") ? "#fafafa" : "#71717a"
                      }}>{line}</p>
                    ))}
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </div>
      </section>
    </div>
  );
}
