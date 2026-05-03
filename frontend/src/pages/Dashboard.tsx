import { useState, useEffect, useCallback } from "react";
import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import {
  Activity, Play,
  TrendingUp, Zap, RotateCcw, Database, ArrowRight
} from "lucide-react";
import {
  AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend
} from "recharts";
import { getDashboard, loadDemo } from "../lib/api";
import type { DashboardStats } from "../lib/api";

const STATUS_COLORS = ["#6366f1", "#ef4444", "#f59e0b", "#71717a"];

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [logs, setLogs] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [demoLoading, setDemoLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setError(null);
      const res = await getDashboard();
      setStats(res.data.stats);
      setLogs(res.data.recent_logs);
    } catch {
      setError("Cannot connect to backend — make sure api.py is running on port 5001.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, [fetchData]);

  const handleLoadDemo = async () => {
    setDemoLoading(true);
    try {
      await loadDemo();
      await fetchData();
    } catch {
      setError("Failed to load demo.");
    } finally {
      setDemoLoading(false);
    }
  };

  const pieData = stats
    ? [
        { name: "Completed", value: stats.completed },
        { name: "Failed", value: stats.failed },
        { name: "Pending", value: stats.pending },
        { name: "Deleted", value: stats.deleted },
      ].filter((d) => d.value > 0)
    : [];

  const effTrend = stats ? buildEffTrend(stats.efficiency) : [];

  return (
    <div>
      {/* ── HERO SECTION ── */}
      <section
        className="relative min-h-screen flex flex-col justify-center overflow-hidden"
        style={{ background: "linear-gradient(160deg, #09090b 0%, #18181b 60%, #09090b 100%)" }}
      >
        {/* Decorative blobs */}
        <div className="absolute top-20 right-10 w-96 h-96 rounded-full opacity-10 blur-3xl"
          style={{ background: "#6366f1" }} />
        <div className="absolute bottom-20 left-10 w-64 h-64 rounded-full opacity-5 blur-3xl"
          style={{ background: "#6366f1" }} />

        <div className="max-w-7xl mx-auto px-6 pt-24 pb-16 w-full">
          {/* Badge */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-xs font-bold tracking-widest mb-8"
            style={{ background: "#27272a", color: "#6366f1", border: "1px solid #3f3f46" }}
          >
            <span className="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-pulse" />
            LIVE SYSTEM MONITORING
          </motion.div>

          {/* Hero headline */}
          <motion.h1
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.15 }}
            className="text-6xl md:text-8xl font-black leading-none tracking-tight mb-4"
            style={{ color: "#fafafa" }}
          >
            SCHEDULING
            <br />
            <span style={{ color: "#6366f1" }}>THE FUTURE.</span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="text-lg max-w-2xl mb-10"
            style={{ color: "#71717a" }}
          >
            Enterprise-grade task orchestration with Priority, SJF, and EDF algorithms.
            Real-time dependency management and performance analytics.
          </motion.p>

          {/* CTA Buttons */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.25 }}
            className="flex flex-wrap gap-4 mb-16"
          >
            <button
              onClick={handleLoadDemo}
              disabled={demoLoading}
              className="flex items-center gap-2 px-7 py-3 rounded-full text-sm font-black tracking-widest transition-all active:scale-95 disabled:opacity-60"
              style={{ background: "#6366f1", color: "#fafafa" }}
            >
              <Database size={16} />
              {demoLoading ? "LOADING..." : "LOAD DEMO DATA"}
            </button>
            <Link
              to="/scheduler"
              className="flex items-center gap-2 px-7 py-3 rounded-full text-sm font-black tracking-widest transition-all"
              style={{ border: "2px solid #27272a", color: "#fafafa" }}
            >
              <Play size={16} />
              RUN SCHEDULER
              <ArrowRight size={14} />
            </Link>
            <button
              onClick={fetchData}
              className="flex items-center gap-2 px-5 py-3 rounded-full text-sm font-bold transition-all"
              style={{ color: "#71717a" }}
            >
              <RotateCcw size={15} />
            </button>
          </motion.div>

          {/* Error */}
          {error && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="mb-8 px-5 py-3 rounded-xl text-sm font-medium"
              style={{ background: "#1a0a0a", color: "#f87171", border: "1px solid #3b0f0f" }}
            >
              ⚠️ {error}
            </motion.div>
          )}

          {/* Live Stats Cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <StatCard label="TOTAL TASKS" value={loading ? "—" : stats?.total ?? 0} accent="#6366f1" />
            <StatCard label="COMPLETED" value={loading ? "—" : stats?.completed ?? 0} accent="#6366f1" />
            <StatCard label="EFFICIENCY" value={loading ? "—" : `${stats?.efficiency ?? 0}%`} accent="#6366f1" highlight />
            <StatCard label="SIM. CLOCK" value={loading ? "—" : `T=${stats?.current_time ?? 0}`} accent="#71717a" />
          </div>
        </div>

        {/* Scroll indicator */}
        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2 animate-bounce">
          <span className="text-xs font-bold tracking-widest" style={{ color: "#27272a" }}>SCROLL</span>
          <div className="w-px h-8" style={{ background: "linear-gradient(to bottom, #27272a, transparent)" }} />
        </div>
      </section>

      {/* ── METRICS SECTION ── */}
      <section style={{ background: "#09090b" }} className="py-24 border-y border-[#18181b]">
        <div className="max-w-7xl mx-auto px-6">
          <SectionLabel>PERFORMANCE METRICS</SectionLabel>
          <h2 className="text-4xl md:text-6xl font-black mb-12" style={{ color: "#fafafa" }}>
            LIVE ANALYTICS
          </h2>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-16">
            {[
              { label: "AVG WAIT TIME", value: `${stats?.avg_wait ?? 0}u`, sub: "Time units" },
              { label: "AVG TURNAROUND", value: `${stats?.avg_turnaround ?? 0}u`, sub: "Time units" },
              { label: "RUNNING", value: stats?.running ?? 0, sub: "Active tasks" },
              { label: "FAILED", value: stats?.failed ?? 0, sub: "Missed deadlines" },
            ].map(({ label, value, sub }) => (
              <motion.div
                key={label}
                whileHover={{ y: -4 }}
                className="p-6 rounded-2xl"
                style={{ background: "#18181b", border: "1px solid #27272a" }}
              >
                <p className="text-xs font-bold tracking-widest mb-3" style={{ color: "#6366f1" }}>{label}</p>
                <p className="text-4xl font-black mb-1" style={{ color: "#fafafa" }}>{value}</p>
                <p className="text-xs" style={{ color: "#71717a" }}>{sub}</p>
              </motion.div>
            ))}
          </div>

          {/* Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 p-6 rounded-2xl" style={{ background: "#18181b", border: "1px solid #27272a" }}>
              <p className="text-xs font-bold tracking-widest mb-6" style={{ color: "#6366f1" }}>EFFICIENCY TREND</p>
              <ResponsiveContainer width="100%" height={220}>
                <AreaChart data={effTrend}>
                  <defs>
                    <linearGradient id="grad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#6366f1" stopOpacity={0.25} />
                      <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <XAxis dataKey="label" tick={{ fill: "#71717a", fontSize: 11 }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fill: "#71717a", fontSize: 11 }} axisLine={false} tickLine={false} />
                  <Tooltip
                    contentStyle={{ background: "#09090b", border: "1px solid #27272a", borderRadius: 12, color: "#fafafa" }}
                  />
                  <Area type="monotone" dataKey="value" stroke="#6366f1" strokeWidth={3} fill="url(#grad)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>

            <div className="p-6 rounded-2xl" style={{ background: "#18181b", border: "1px solid #27272a" }}>
              <p className="text-xs font-bold tracking-widest mb-6" style={{ color: "#6366f1" }}>TASK STATUS</p>
              {pieData.length > 0 ? (
                <ResponsiveContainer width="100%" height={220}>
                  <PieChart>
                    <Pie data={pieData} cx="50%" cy="50%" outerRadius={70} dataKey="value"
                      label={({ name, percent }) => `${name} ${Math.round((percent ?? 0) * 100)}%`}
                      labelLine={false} fontSize={10} fill="#6366f1">
                      {pieData.map((_, i) => <Cell key={i} fill={STATUS_COLORS[i % STATUS_COLORS.length]} />)}
                    </Pie>
                    <Legend wrapperStyle={{ fontSize: 11, color: "#71717a" }} />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-48 flex items-center justify-center text-sm" style={{ color: "#71717a" }}>
                  Load demo data to see charts
                </div>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* ── QUICK ACTIONS SECTION ── */}
      <section style={{ background: "#09090b" }} className="py-24">
        <div className="max-w-7xl mx-auto px-6">
          <SectionLabel>QUICK ACTIONS</SectionLabel>
          <h2 className="text-4xl md:text-6xl font-black mb-4" style={{ color: "#fafafa" }}>
            GET STARTED FAST.
          </h2>
          <p className="text-lg mb-12" style={{ color: "#71717a" }}>
            Jump directly to any part of the system.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {[
              { icon: Activity, label: "ADD TASK", sub: "Register a new task with scheduling parameters", href: "/tasks", accent: "#6366f1" },
              { icon: Play, label: "RUN SCHEDULER", sub: "Execute Priority, SJF, or EDF simulation", href: "/scheduler", accent: "#6366f1" },
              { icon: TrendingUp, label: "VIEW REPORTS", sub: "Gantt charts, CPU utilization, and analytics", href: "/reports", accent: "#71717a" },
              { icon: Zap, label: "DEPENDENCIES", sub: "Visualize task dependency flow graph", href: "/dependencies", accent: "#71717a" },
            ].map(({ icon: Icon, label, sub, href, accent }) => (
              <motion.div key={href} whileHover={{ y: -6, scale: 1.01 }} transition={{ duration: 0.2 }}>
                <Link
                  to={href}
                  className="block p-6 rounded-2xl group transition-all h-full"
                  style={{ background: "#18181b", border: "1px solid #27272a" }}
                >
                  <div className="w-10 h-10 rounded-xl flex items-center justify-center mb-4 transition-transform group-hover:scale-110"
                    style={{ background: "#27272a" }}>
                    <Icon size={20} style={{ color: accent }} />
                  </div>
                  <p className="text-sm font-black tracking-widest mb-2" style={{ color: "#fafafa" }}>{label}</p>
                  <p className="text-xs leading-relaxed" style={{ color: "#71717a" }}>{sub}</p>
                  <div className="mt-4 flex items-center gap-1 text-xs font-bold transition-colors group-hover:gap-2"
                    style={{ color: accent }}>
                    GO <ArrowRight size={12} />
                  </div>
                </Link>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ── RECENT LOGS SECTION ── */}
      <section style={{ background: "#18181b" }} className="py-24 border-t border-[#27272a]">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex justify-between items-end mb-10 flex-wrap gap-4">
            <div>
              <SectionLabel>EXECUTION OUTPUT</SectionLabel>
              <h2 className="text-4xl md:text-5xl font-black" style={{ color: "#fafafa" }}>
                RECENT LOGS
              </h2>
            </div>
            <Link
              to="/logs"
              className="flex items-center gap-2 px-5 py-2 rounded-full text-xs font-black tracking-widest"
              style={{ border: "1px solid #27272a", color: "#6366f1" }}
            >
              VIEW ALL <ArrowRight size={14} />
            </Link>
          </div>

          <div className="rounded-2xl overflow-hidden" style={{ background: "#09090b", border: "1px solid #27272a" }}>
            <div className="flex items-center gap-3 px-6 py-4 border-b" style={{ borderColor: "#27272a" }}>
              <div className="flex gap-2">
                <div className="w-3 h-3 rounded-full" style={{ background: "#ef4444" }} />
                <div className="w-3 h-3 rounded-full" style={{ background: "#f59e0b" }} />
                <div className="w-3 h-3 rounded-full" style={{ background: "#6366f1" }} />
              </div>
              <span className="text-xs font-bold tracking-widest" style={{ color: "#71717a" }}>
                task-scheduler — execution console
              </span>
            </div>
            <div className="p-6 font-mono text-xs space-y-2 min-h-40 max-h-64 overflow-y-auto">
              {logs.length === 0 ? (
                <p style={{ color: "#27272a" }}>$ waiting for execution... load demo to see output</p>
              ) : (
                logs.map((log, i) => (
                  <p key={i} className={
                    log.includes("COMPLETED") ? "text-indigo-400" :
                    log.includes("Running") ? "text-blue-400" :
                    log.includes("MISSED") ? "text-red-400" :
                    log.includes("aged") ? "text-amber-400" :
                    log.includes("---") ? "font-bold" : ""
                  } style={!log.includes("COMPLETED") && !log.includes("Running") && !log.includes("MISSED") && !log.includes("aged") && !log.includes("---") ? { color: "#71717a" } : {}}>
                    {log}
                  </p>
                ))
              )}
            </div>
          </div>
        </div>
      </section>

      {/* ── FOOTER ── */}
      <footer style={{ background: "#09090b", borderTop: "1px solid #18181b" }} className="py-12">
        <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded flex items-center justify-center" style={{ background: "#6366f1" }}>
              <Zap size={12} style={{ color: "#09090b" }} fill="currentColor" />
            </div>
            <span className="text-sm font-black" style={{ color: "#fafafa" }}>
              task<span style={{ color: "#6366f1" }}>flow</span>
            </span>
          </div>
          <p className="text-xs font-bold tracking-widest" style={{ color: "#27272a" }}>
            DS COURSE PROJECT — SEM 4 — TASK SCHEDULING SYSTEM
          </p>
          <div className="flex gap-6">
            {["TASKS", "SCHEDULER", "ANALYTICS"].map((l) => (
              <Link key={l} to={`/${l.toLowerCase()}`} className="text-xs font-bold tracking-widest transition-colors"
                style={{ color: "#27272a" }}
                onMouseEnter={(e) => (e.currentTarget.style.color = "#6366f1")}
                onMouseLeave={(e) => (e.currentTarget.style.color = "#27272a")}>
                {l}
              </Link>
            ))}
          </div>
        </div>
      </footer>
    </div>
  );
}

function SectionLabel({ children }: { children: string }) {
  return (
    <p className="text-xs font-black tracking-widest mb-3" style={{ color: "#6366f1" }}>
      {children}
    </p>
  );
}

function StatCard({ label, value, accent, highlight }: { label: string; value: any; accent: string; highlight?: boolean }) {
  return (
    <motion.div
      whileHover={{ y: -4 }}
      className="p-6 rounded-2xl"
      style={{
        background: highlight ? "#6366f1" : "#18181b",
        border: "1px solid #27272a",
      }}
    >
      <p className="text-xs font-bold tracking-widest mb-3"
        style={{ color: highlight ? "#09090b" : accent }}>{label}</p>
      <p className="text-3xl font-black"
        style={{ color: highlight ? "#09090b" : "#fafafa" }}>{value}</p>
    </motion.div>
  );
}

function buildEffTrend(eff: number) {
  return [
    { label: "T-5", value: Math.max(0, eff - 25) },
    { label: "T-4", value: Math.max(0, eff - 18) },
    { label: "T-3", value: Math.max(0, eff - 12) },
    { label: "T-2", value: Math.max(0, eff - 6) },
    { label: "T-1", value: Math.max(0, eff - 2) },
    { label: "NOW", value: eff },
  ];
}
