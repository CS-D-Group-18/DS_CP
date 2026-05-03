import { useState, useEffect, useCallback } from "react";
import { motion } from "framer-motion";
import { Download } from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend, AreaChart, Area } from "recharts";
import { getReports } from "../lib/api";

const COLORS = ["#6366f1", "#ef4444", "#f59e0b", "#71717a"];

export default function Reports() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchReports = useCallback(async () => {
    try { const res = await getReports(); setData(res.data); setError(null); }
    catch (err: any) { setError(err.response?.data?.error || "No simulation data. Run scheduler first."); } finally { setLoading(false); }
  }, []);

  useEffect(() => { fetchReports(); }, [fetchReports]);

  const exportCSV = () => {
    if (!data) return;
    const headers = "Task ID,Name,Priority,Arrival,Exec,Wait,Turnaround,Status\n";
    const rows = data.tasks.map((t: any) => `${t.task_id},${t.name},${t.priority},${t.arrival_time},${t.exec_time},${t.waiting_time},${t.turnaround_time},${t.status}`).join("\n");
    const blob = new Blob([headers + rows], { type: "text/csv" });
    const a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = `report_${Date.now()}.csv`; a.click();
  };

  const pieData = data ? Object.entries(data.status_breakdown).filter(([, v]) => (v as number) > 0).map(([k, v]) => ({ name: k, value: v })) : [];
  const barData = data?.tasks.filter((t: any) => t.turnaround_time > 0).map((t: any) => ({ id: t.task_id, turnaround: t.turnaround_time, waiting: t.waiting_time })) || [];

  const tooltipStyle = { background: "#09090b", border: "1px solid #27272a", borderRadius: 12, color: "#fafafa" };
  const axisProps = { tick: { fill: "#71717a", fontSize: 11 }, axisLine: false, tickLine: false };

  return (
    <div style={{ minHeight: "100vh", background: "#09090b" }}>
      <section className="pt-28 pb-12 px-6" style={{ background: "linear-gradient(160deg, #09090b, #18181b)" }}>
        <div className="max-w-7xl mx-auto">
          <p className="text-xs font-black tracking-widest mb-3" style={{ color: "#6366f1" }}>ANALYTICS & REPORTS</p>
          <div className="flex justify-between items-end flex-wrap gap-6">
            <h1 className="text-5xl md:text-7xl font-black leading-none" style={{ color: "#fafafa" }}>
              PERFORMANCE<br /><span style={{ color: "#6366f1" }}>INSIGHTS.</span>
            </h1>
            <div className="flex gap-3">
              <button onClick={fetchReports} className="px-5 py-3 rounded-full text-xs font-black tracking-widest" style={{ border: "1px solid #27272a", color: "#71717a" }}>REFRESH</button>
              <button onClick={exportCSV} disabled={!data} className="flex items-center gap-2 px-6 py-3 rounded-full text-sm font-black tracking-widest disabled:opacity-50" style={{ background: "#6366f1", color: "#fafafa" }}>
                <Download size={16} /> EXPORT CSV
              </button>
            </div>
          </div>
        </div>
      </section>

      <section className="px-6 py-12">
        <div className="max-w-7xl mx-auto space-y-8">
          {error && <div className="p-5 rounded-2xl text-sm" style={{ background: "#18181b", color: "#6366f1", border: "1px solid #27272a" }}>ℹ️ {error} — Run the Scheduler and return here.</div>}
          {loading && <p className="text-sm" style={{ color: "#71717a" }}>Loading report data...</p>}

          {data && (
            <>
              {/* Summary KPIs */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {[
                  { label: "EFFICIENCY", value: `${data.summary.efficiency}%`, accent: "#6366f1", highlight: true },
                  { label: "COMPLETED", value: data.summary.completed, accent: "#10b981" },
                  { label: "MISSED", value: data.summary.missed, accent: "#ef4444" },
                  { label: "TOTAL TIME", value: `T=${data.summary.total_time}`, accent: "#71717a" },
                  { label: "AVG WAIT", value: `${data.summary.avg_wait}u`, accent: "#f59e0b" },
                  { label: "AVG TURNAROUND", value: `${data.summary.avg_turnaround}u`, accent: "#3b82f6" },
                  { label: "TOTAL TASKS", value: data.summary.total, accent: "#71717a" },
                  { label: "PENDING", value: data.summary.pending, accent: "#f59e0b" },
                ].map(({ label, value, accent, highlight }) => (
                  <motion.div key={label} whileHover={{ y: -4 }} className="p-6 rounded-2xl"
                    style={{ background: highlight ? "#6366f1" : "#18181b", border: `1px solid ${highlight ? "#6366f1" : "#27272a"}` }}>
                    <p className="text-xs font-black tracking-widest mb-3" style={{ color: highlight ? "#09090b" : accent }}>{label}</p>
                    <p className="text-3xl font-black" style={{ color: highlight ? "#09090b" : "#fafafa" }}>{value}</p>
                  </motion.div>
                ))}
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="p-6 rounded-2xl" style={{ background: "#18181b", border: "1px solid #27272a" }}>
                  <p className="text-xs font-black tracking-widest mb-6" style={{ color: "#6366f1" }}>TURNAROUND vs WAIT TIME</p>
                  {barData.length > 0 ? (
                    <ResponsiveContainer width="100%" height={220}>
                      <BarChart data={barData}>
                        <XAxis dataKey="id" {...axisProps} />
                        <YAxis {...axisProps} />
                        <Tooltip contentStyle={tooltipStyle} />
                        <Legend wrapperStyle={{ fontSize: 11, color: "#71717a" }} />
                        <Bar dataKey="turnaround" fill="#6366f1" radius={[4, 4, 0, 0]} name="Turnaround" />
                        <Bar dataKey="waiting" fill="#3b82f6" radius={[4, 4, 0, 0]} name="Wait Time" />
                      </BarChart>
                    </ResponsiveContainer>
                  ) : <div className="h-48 flex items-center justify-center text-sm" style={{ color: "#71717a" }}>No data</div>}
                </div>

                <div className="p-6 rounded-2xl" style={{ background: "#18181b", border: "1px solid #27272a" }}>
                  <p className="text-xs font-black tracking-widest mb-6" style={{ color: "#6366f1" }}>STATUS DISTRIBUTION</p>
                  <ResponsiveContainer width="100%" height={220}>
                    <PieChart>
                      <Pie data={pieData} cx="50%" cy="50%" outerRadius={75} dataKey="value"
                        label={({ name, percent }) => `${name} ${Math.round((percent ?? 0) * 100)}%`} labelLine={false} fontSize={10}>
                        {pieData.map((_: any, i: number) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                      </Pie>
                      <Legend wrapperStyle={{ fontSize: 11, color: "#71717a" }} />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {data.utilization.length > 0 && (
                <div className="p-6 rounded-2xl" style={{ background: "#18181b", border: "1px solid #27272a" }}>
                  <p className="text-xs font-black tracking-widest mb-6" style={{ color: "#6366f1" }}>CPU UTILIZATION OVER TIME</p>
                  <ResponsiveContainer width="100%" height={180}>
                    <AreaChart data={data.utilization}>
                      <defs>
                        <linearGradient id="cpuGrad" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#6366f1" stopOpacity={0.2} />
                          <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                        </linearGradient>
                      </defs>
                      <XAxis dataKey="time" {...axisProps} />
                      <YAxis {...axisProps} domain={[0, 100]} unit="%" />
                      <Tooltip contentStyle={tooltipStyle} formatter={(v: any) => [`${v}%`, "CPU Util"]} />
                      <Area type="monotone" dataKey="utilization" stroke="#6366f1" strokeWidth={2.5} fill="url(#cpuGrad)" />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              )}

              {data.gantt.length > 0 && (
                <div className="p-6 rounded-2xl overflow-x-auto" style={{ background: "#18181b", border: "1px solid #27272a" }}>
                  <p className="text-xs font-black tracking-widest mb-6" style={{ color: "#6366f1" }}>GANTT CHART — TASK TIMELINE</p>
                  <div className="space-y-2 min-w-96">
                    {data.gantt.map((g: any) => {
                      const total = data.summary.total_time || 1;
                      return (
                        <div key={g.task_id} className="flex items-center gap-4">
                          <span className="w-20 text-xs font-mono font-black shrink-0" style={{ color: "#6366f1" }}>{g.task_id}</span>
                          <div className="flex-1 h-8 relative rounded" style={{ background: "#09090b" }}>
                            <div className="absolute top-0 h-8 rounded flex items-center px-2"
                              style={{ left: `${(g.start / total) * 100}%`, width: `${Math.max((g.exec_time / total) * 100, 2)}%`, background: g.status === "COMPLETED" ? "#10b981" : "#ef4444" }}>
                              <span className="text-xs font-black truncate" style={{ color: "#fafafa" }}>{g.task_id}</span>
                            </div>
                          </div>
                          <span className="text-xs shrink-0 font-mono" style={{ color: "#71717a" }}>T{g.start}–T{g.end}</span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              <div className="rounded-2xl overflow-hidden" style={{ border: "1px solid #27272a" }}>
                <div className="p-6" style={{ background: "#18181b" }}>
                  <p className="text-xs font-black tracking-widest" style={{ color: "#6366f1" }}>TASK EXECUTION TABLE</p>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-left">
                    <thead>
                      <tr style={{ background: "#09090b" }}>
                        {["ID", "Name", "Priority", "Arrival", "Exec", "Wait", "Turnaround", "Status"].map(h => (
                          <th key={h} className="py-4 px-5 text-xs font-black tracking-widest" style={{ color: "#27272a" }}>{h}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {data.tasks.map((t: any, i: number) => (
                        <tr key={t.task_id} style={{ background: i % 2 === 0 ? "#111114" : "#18181b", borderBottom: "1px solid #27272a" }}>
                          <td className="py-3 px-5 text-xs font-mono font-black" style={{ color: "#6366f1" }}>{t.task_id}</td>
                          <td className="py-3 px-5 text-xs" style={{ color: "#fafafa" }}>{t.name}</td>
                          <td className="py-3 px-5 text-xs" style={{ color: "#71717a" }}>{t.priority}</td>
                          <td className="py-3 px-5 text-xs font-mono" style={{ color: "#71717a" }}>T{t.arrival_time}</td>
                          <td className="py-3 px-5 text-xs" style={{ color: "#71717a" }}>{t.exec_time}u</td>
                          <td className="py-3 px-5 text-xs" style={{ color: "#71717a" }}>{t.waiting_time}u</td>
                          <td className="py-3 px-5 text-xs" style={{ color: "#71717a" }}>{t.turnaround_time}u</td>
                          <td className="py-3 px-5">
                            <span className="px-2 py-1 rounded-full text-xs font-black"
                              style={{ background: t.status === "COMPLETED" ? "#052e16" : t.status === "MISSED" ? "#450a0a" : "#2d1f00", color: t.status === "COMPLETED" ? "#10b981" : t.status === "MISSED" ? "#f87171" : "#f59e0b" }}>
                              {t.status}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </>
          )}
        </div>
      </section>
    </div>
  );
}
