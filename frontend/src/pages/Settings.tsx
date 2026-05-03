import { useState } from "react";
import { motion } from "framer-motion";
import { resetScheduler } from "../lib/api";

export default function Settings() {
  const [apiUrl] = useState("http://localhost:5001/api");
  const [resetting, setResetting] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);

  const handleReset = async () => {
    if (!confirm("Reset the scheduler engine? This clears all tasks and logs.")) return;
    setResetting(true);
    try {
      await resetScheduler();
      setMsg("✅ Scheduler engine reset successfully.");
    } catch {
      setMsg("❌ Failed to reset. Is api.py running?");
    } finally {
      setResetting(false);
      setTimeout(() => setMsg(null), 4000);
    }
  };

  return (
    <div style={{ minHeight: "100vh", background: "#09090b" }}>
      <section className="pt-28 pb-12 px-6" style={{ background: "linear-gradient(160deg, #09090b, #18181b)" }}>
        <div className="max-w-7xl mx-auto">
          <p className="text-xs font-black tracking-widest mb-3" style={{ color: "#6366f1" }}>SYSTEM CONFIG</p>
          <h1 className="text-5xl md:text-7xl font-black leading-none" style={{ color: "#fafafa" }}>
            PREFERENCES<br /><span style={{ color: "#6366f1" }}>& SETUP.</span>
          </h1>
          <p className="mt-4 text-lg" style={{ color: "#71717a" }}>Configure environment and manage system state</p>
        </div>
      </section>

      <section className="px-6 py-12">
        <div className="max-w-3xl mx-auto space-y-8">
          {msg && (
            <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="p-4 rounded-xl text-sm font-bold" style={{ background: msg.startsWith("✅") ? "#052e16" : "#2d0a0a", color: msg.startsWith("✅") ? "#10b981" : "#f87171", border: "1px solid #27272a" }}>
              {msg}
            </motion.div>
          )}

          <div className="bg-[#18181b] rounded-2xl border border-[#27272a] overflow-hidden">
            <div className="p-8 border-b border-[#27272a]">
              <h3 className="font-black text-sm tracking-widest" style={{ color: "#6366f1" }}>API CONFIGURATION</h3>
              <p className="text-xs mt-2" style={{ color: "#71717a" }}>The frontend connects to the Python Flask API at this address.</p>
            </div>
            <div className="p-8 space-y-6">
              <div>
                <label className="block text-xs font-black tracking-widest mb-3" style={{ color: "#71717a" }}>BACKEND API URL</label>
                <div className="flex gap-4">
                  <input
                    type="text"
                    value={apiUrl}
                    readOnly
                    className="flex-1 px-4 py-3 rounded-xl text-sm font-mono"
                    style={{ background: "#09090b", border: "1px solid #27272a", color: "#71717a" }}
                  />
                  <span className="px-4 py-3 rounded-xl text-xs font-black tracking-widest flex items-center" style={{ background: "#1e1b4b", color: "#6366f1" }}>CONNECTED</span>
                </div>
              </div>
              <div>
                <label className="block text-xs font-black tracking-widest mb-3" style={{ color: "#71717a" }}>ACTIVE ENDPOINTS</label>
                <div className="space-y-2 font-mono text-xs">
                  {[
                    "GET  /api/dashboard",
                    "GET  /api/tasks",
                    "POST /api/tasks",
                    "DELETE /api/tasks/:id",
                    "GET  /api/dependencies",
                    "POST /api/dependencies",
                    "POST /api/scheduler/run",
                    "POST /api/scheduler/reset",
                  ].map((e) => (
                    <p key={e} className="px-4 py-2 rounded-lg" style={{ background: "#09090b", color: "#71717a", border: "1px solid #27272a" }}>{e}</p>
                  ))}
                </div>
              </div>
            </div>
          </div>

          <div className="bg-[#18181b] rounded-2xl border border-[#27272a] overflow-hidden">
            <div className="p-8 border-b border-[#27272a]">
              <h3 className="font-black text-sm tracking-widest" style={{ color: "#ef4444" }}>DANGER ZONE</h3>
              <p className="text-xs mt-2" style={{ color: "#71717a" }}>Irreversible actions that modify system core state.</p>
            </div>
            <div className="p-8">
              <div className="flex justify-between items-center p-6 rounded-2xl border-2" style={{ borderColor: "#2d0a0a", background: "#1a0a0a" }}>
                <div>
                  <p className="font-black text-sm" style={{ color: "#f87171" }}>RESET ENGINE</p>
                  <p className="text-xs mt-1" style={{ color: "#ef4444" }}>Clears all tasks, dependencies, and history.</p>
                </div>
                <button
                  onClick={handleReset}
                  disabled={resetting}
                  className="px-6 py-3 rounded-full text-xs font-black tracking-widest text-white disabled:opacity-60 transition-all active:scale-95"
                  style={{ background: "#ef4444" }}
                >
                  {resetting ? "RESETTING..." : "RESET NOW"}
                </button>
              </div>
            </div>
          </div>

          <div className="bg-[#18181b] rounded-2xl border border-[#27272a] p-8">
            <h3 className="font-black text-sm tracking-widest mb-4" style={{ color: "#6366f1" }}>SYSTEM ABOUT</h3>
            <div className="space-y-3 text-xs font-mono leading-relaxed" style={{ color: "#71717a" }}>
              <p>TASK SCHEDULING SYSTEM V2.0</p>
              <p>DESIGN: PROFESSIONAL INDIGO DARK THEME</p>
              <p>STACK: REACT 19 + FLASK + CUSTOM DAG ENGINE</p>
              <p>© 2026 DS SEM 4 COURSE PROJECT</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
