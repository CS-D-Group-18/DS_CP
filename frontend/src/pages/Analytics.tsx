import { useState, useEffect, useCallback } from "react";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  LineChart, Line, PieChart, Pie, Cell, Legend
} from "recharts";
import { getReports } from "../lib/api";

const COLORS = ["#6366f1", "#ef4444", "#f59e0b", "#71717a"];

export default function Analytics() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      const res = await getReports();
      setData(res.data);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.error || "No data yet. Run the scheduler first.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  const pieData = data
    ? Object.entries(data.status_breakdown).filter(([, v]) => (v as number) > 0).map(([k, v]) => ({ name: k, value: v }))
    : [];

  const topPerformers = data?.tasks.filter((t: any) => t.status === "COMPLETED").sort((a: any, b: any) => a.turnaround_time - b.turnaround_time).slice(0, 5) || [];

  const tooltipStyle = { background: "#09090b", border: "1px solid #27272a", borderRadius: 12, color: "#fafafa" };
  const axisProps = { tick: { fill: "#71717a", fontSize: 11 }, axisLine: false, tickLine: false };

  return (
    <div style={{ minHeight: "100vh", background: "#09090b" }}>
      <section className="pt-28 pb-12 px-6" style={{ background: "linear-gradient(160deg, #09090b, #18181b)" }}>
        <div className="max-w-7xl mx-auto">
          <p className="text-xs font-black tracking-widest mb-3" style={{ color: "#6366f1" }}>DEEP ANALYTICS</p>
          <div className="flex justify-between items-end flex-wrap gap-6">
            <h1 className="text-5xl md:text-7xl font-black leading-none" style={{ color: "#fafafa" }}>
              SYSTEM<br /><span style={{ color: "#6366f1" }}>INSIGHTS.</span>
            </h1>
            <button onClick={fetchData} className="px-5 py-3 rounded-full text-xs font-black tracking-widest" style={{ border: "1px solid #27272a", color: "#71717a" }}>REFRESH</button>
          </div>
          <p className="mt-4 text-lg" style={{ color: "#71717a" }}>Performance profiling and bottleneck detection</p>
        </div>
      </section>

      <section className="px-6 py-12">
        <div className="max-w-7xl mx-auto space-y-8">
          {error && (
            <div className="p-5 rounded-2xl text-sm" style={{ background: "#18181b", color: "#6366f1", border: "1px solid #27272a" }}>ℹ️ {error}</div>
          )}
          {loading && <p className="text-sm" style={{ color: "#71717a" }}>Loading analytics...</p>}

          {data && (
            <>
              {/* KPI Row */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {[
                  { label: "SUCCESS RATE", value: `${data.summary.efficiency}%`, color: "#10b981" },
                  { label: "AVG WAIT", value: `${data.summary.avg_wait}u`, color: "#f59e0b" },
                  { label: "AVG TURNAROUND", value: `${data.summary.avg_turnaround}u`, color: "#3b82f6" },
                  { label: "MISSED", value: data.summary.missed, color: "#ef4444" },
                ].map(({ label, value, color }) => (
                  <div key={label} className="bg-[#18181b] p-6 rounded-2xl border border-[#27272a]">
                    <p className="text-xs font-black tracking-widest mb-3" style={{ color }}>{label}</p>
                    <p className="text-4xl font-black" style={{ color: "#fafafa" }}>{value}</p>
                  </div>
                ))}
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Status Breakdown Pie */}
                <div className="bg-[#18181b] p-6 rounded-2xl border border-[#27272a]">
                  <p className="text-xs font-black tracking-widest mb-6" style={{ color: "#6366f1" }}>OUTCOME DISTRIBUTION</p>
                  <ResponsiveContainer width="100%" height={250}>
                    <PieChart>
                      <Pie data={pieData} cx="50%" cy="50%" outerRadius={80} dataKey="value" label={({ name, percent }) => `${name} ${Math.round((percent ?? 0) * 100)}%`} fontSize={11}>
                        {pieData.map((_: any, i: number) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                      </Pie>
                      <Legend wrapperStyle={{ fontSize: 11, color: "#71717a" }} />
                    </PieChart>
                  </ResponsiveContainer>
                </div>

                {/* Best performers */}
                <div className="bg-[#18181b] p-6 rounded-2xl border border-[#27272a]">
                  <p className="text-xs font-black tracking-widest mb-6" style={{ color: "#6366f1" }}>FASTEST TASKS</p>
                  <ResponsiveContainer width="100%" height={250}>
                    <BarChart data={topPerformers.map((t: any) => ({ id: t.task_id, turnaround: t.turnaround_time }))}>
                      <XAxis dataKey="id" {...axisProps} />
                      <YAxis {...axisProps} />
                      <Tooltip contentStyle={tooltipStyle} />
                      <Bar dataKey="turnaround" fill="#6366f1" radius={[4, 4, 0, 0]} name="Turnaround Time" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* CPU Utilization Line */}
              {data.utilization.length > 0 && (
                <div className="bg-[#18181b] p-6 rounded-2xl border border-[#27272a]">
                  <p className="text-xs font-black tracking-widest mb-6" style={{ color: "#6366f1" }}>CPU LOAD PROFILE</p>
                  <ResponsiveContainer width="100%" height={250}>
                    <LineChart data={data.utilization}>
                      <XAxis dataKey="time" {...axisProps} />
                      <YAxis domain={[0, 100]} unit="%" {...axisProps} />
                      <Tooltip formatter={(v: any) => [`${v}%`, "CPU Util"]} contentStyle={tooltipStyle} />
                      <Line type="monotone" dataKey="utilization" stroke="#6366f1" strokeWidth={3} dot={false} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              )}
            </>
          )}
        </div>
      </section>
    </div>
  );
}
