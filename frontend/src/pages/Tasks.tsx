import { useState, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Plus, Trash2, Search, X } from "lucide-react";
import { getTasks, addTask, deleteTask } from "../lib/api";
import type { TaskData } from "../lib/api";

const STATUS_COLORS: Record<string, { bg: string; text: string }> = {
  PENDING: { bg: "#2d1f00", text: "#fbbf24" },
  RUNNING: { bg: "#001a3d", text: "#60a5fa" },
  COMPLETED: { bg: "#052e16", text: "#10b981" },
  MISSED: { bg: "#450a0a", text: "#f87171" },
  DELETED: { bg: "#18181b", text: "#71717a" },
};

const SORT_OPTIONS = ["Arrival Time", "Priority", "Deadline"];

export default function Tasks() {
  const [tasks, setTasks] = useState<TaskData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [search, setSearch] = useState("");
  const [sortBy, setSortBy] = useState("Arrival Time");

  const fetchTasks = useCallback(async () => {
    try {
      const res = await getTasks();
      setTasks(res.data);
      setError(null);
    } catch {
      setError("Cannot connect to backend. Make sure api.py is running.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchTasks(); }, [fetchTasks]);

  const handleDelete = async (id: string) => {
    if (!confirm(`Delete task ${id}?`)) return;
    try { await deleteTask(id); fetchTasks(); } catch { alert("Failed."); }
  };

  const filtered = tasks
    .filter((t) =>
      t.task_id.toLowerCase().includes(search.toLowerCase()) ||
      t.name.toLowerCase().includes(search.toLowerCase())
    )
    .sort((a, b) => {
      if (sortBy === "Priority") return a.priority - b.priority;
      if (sortBy === "Deadline") return (a.deadline || 999999) - (b.deadline || 999999);
      return a.arrival_time - b.arrival_time;
    });

  return (
    <div style={{ minHeight: "100vh", background: "#09090b" }}>
      {/* Page Hero */}
      <section className="pt-28 pb-12 px-6" style={{ background: "linear-gradient(160deg, #09090b, #18181b)" }}>
        <div className="max-w-7xl mx-auto">
          <p className="text-xs font-black tracking-widest mb-3" style={{ color: "#6366f1" }}>TASK MANAGEMENT</p>
          <div className="flex justify-between items-end flex-wrap gap-6">
            <h1 className="text-5xl md:text-7xl font-black leading-none" style={{ color: "#fafafa" }}>
              YOUR TASKS.
            </h1>
            <button
              onClick={() => setShowModal(true)}
              className="flex items-center gap-2 px-6 py-3 rounded-full text-sm font-black tracking-widest transition-all active:scale-95"
              style={{ background: "#6366f1", color: "#fafafa" }}
            >
              <Plus size={16} /> ADD TASK
            </button>
          </div>
          <p className="mt-4 text-lg" style={{ color: "#71717a" }}>
            {tasks.length} tasks registered in the scheduler
          </p>
        </div>
      </section>

      {/* Content */}
      <section className="px-6 py-12">
        <div className="max-w-7xl mx-auto space-y-6">
          {error && (
            <div className="p-4 rounded-xl text-sm font-medium" style={{ background: "#1a0a0a", color: "#f87171", border: "1px solid #3b0f0f" }}>
              ⚠️ {error}
            </div>
          )}

          {/* Toolbar */}
          <div className="flex gap-3 flex-wrap">
            <div className="relative flex-1 min-w-48">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2" size={16} style={{ color: "#71717a" }} />
              <input
                type="text"
                placeholder="Search tasks..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full pl-11 pr-4 py-3 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/30"
                style={{ background: "#18181b", border: "1px solid #27272a", color: "#fafafa" }}
              />
            </div>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="px-4 py-3 rounded-xl text-sm focus:outline-none"
              style={{ background: "#18181b", border: "1px solid #27272a", color: "#fafafa" }}
            >
              {SORT_OPTIONS.map((o) => <option key={o}>{o}</option>)}
            </select>
          </div>

          {/* Table */}
          <div className="rounded-2xl overflow-hidden" style={{ border: "1px solid #27272a" }}>
            <table className="w-full text-left">
              <thead>
                <tr style={{ background: "#09090b" }}>
                  {["ID", "Name", "Priority", "Exec Time", "Deadline", "Arrival", "Status", ""].map((h) => (
                    <th key={h} className="py-4 px-5 text-xs font-black tracking-widest" style={{ color: "#6366f1" }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {loading && (
                  <tr><td colSpan={8} className="py-16 text-center text-sm" style={{ color: "#71717a", background: "#18181b" }}>Loading tasks...</td></tr>
                )}
                {!loading && filtered.length === 0 && (
                  <tr><td colSpan={8} className="py-16 text-center" style={{ background: "#18181b" }}>
                    <p className="text-4xl font-black mb-3" style={{ color: "#27272a" }}>NO TASKS</p>
                    <p className="text-sm" style={{ color: "#71717a" }}>Add a task or load demo data from the Dashboard</p>
                  </td></tr>
                )}
                {filtered.map((task, i) => {
                  const s = STATUS_COLORS[task.status] || STATUS_COLORS.DELETED;
                  return (
                    <motion.tr
                      key={task.task_id}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: i * 0.03 }}
                      style={{ background: i % 2 === 0 ? "#111114" : "#18181b", borderBottom: "1px solid #27272a" }}
                    >
                      <td className="py-4 px-5 text-sm font-mono font-bold" style={{ color: "#6366f1" }}>{task.task_id}</td>
                      <td className="py-4 px-5 text-sm font-semibold" style={{ color: "#fafafa" }}>{task.name}</td>
                      <td className="py-4 px-5 text-sm" style={{ color: "#71717a" }}>{task.priority}</td>
                      <td className="py-4 px-5 text-sm" style={{ color: "#71717a" }}>{task.exec_time}u</td>
                      <td className="py-4 px-5 text-sm" style={{ color: "#71717a" }}>{task.deadline || "—"}</td>
                      <td className="py-4 px-5 text-sm font-mono" style={{ color: "#71717a" }}>T{task.arrival_time}</td>
                      <td className="py-4 px-5">
                        <span className="px-3 py-1 rounded-full text-xs font-black tracking-wider"
                          style={{ background: s.bg, color: s.text }}>
                          {task.status}
                        </span>
                      </td>
                      <td className="py-4 px-5">
                        <button onClick={() => handleDelete(task.task_id)}
                          className="p-2 rounded-lg transition-colors"
                          style={{ color: "#71717a" }}
                          onMouseEnter={(e) => (e.currentTarget.style.color = "#f87171")}
                          onMouseLeave={(e) => (e.currentTarget.style.color = "#71717a")}>
                          <Trash2 size={15} />
                        </button>
                      </td>
                    </motion.tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <AnimatePresence>
        {showModal && <AddTaskModal onClose={() => setShowModal(false)} onAdded={fetchTasks} />}
      </AnimatePresence>
    </div>
  );
}

function AddTaskModal({ onClose, onAdded }: { onClose: () => void; onAdded: () => void }) {
  const [form, setForm] = useState({ task_id: "", name: "", priority: "0", exec_time: "5", deadline: "0", arrival_time: "0" });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true); setError(null);
    try {
      await addTask({ task_id: form.task_id.trim(), name: form.name.trim(), priority: parseInt(form.priority), exec_time: parseInt(form.exec_time), deadline: parseInt(form.deadline), arrival_time: parseInt(form.arrival_time) });
      onAdded(); onClose();
    } catch (err: any) {
      setError(err.response?.data?.error || "Failed to add task.");
    } finally { setSubmitting(false); }
  };

  const fields = [
    { key: "task_id", label: "TASK ID", placeholder: "e.g. INF-101" },
    { key: "name", label: "TASK NAME", placeholder: "e.g. Provision Cloud VPC" },
    { key: "priority", label: "PRIORITY (lower = higher)", placeholder: "0" },
    { key: "exec_time", label: "EXECUTION TIME (units)", placeholder: "5" },
    { key: "deadline", label: "DEADLINE (0 = none)", placeholder: "0" },
    { key: "arrival_time", label: "ARRIVAL TIME", placeholder: "0" },
  ];

  return (
    <motion.div className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ background: "rgba(9,9,11,0.9)", backdropFilter: "blur(8px)" }}
      initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
      onClick={onClose}>
      <motion.div className="w-full max-w-md p-8 rounded-2xl"
        style={{ background: "#18181b", border: "1px solid #27272a" }}
        initial={{ scale: 0.9 }} animate={{ scale: 1 }} exit={{ scale: 0.9 }}
        onClick={(e) => e.stopPropagation()}>
        <div className="flex justify-between items-center mb-8">
          <div>
            <p className="text-xs font-black tracking-widest mb-1" style={{ color: "#6366f1" }}>NEW TASK</p>
            <h2 className="text-2xl font-black" style={{ color: "#fafafa" }}>ADD TASK</h2>
          </div>
          <button onClick={onClose} className="p-2 rounded-lg" style={{ color: "#71717a" }}><X size={18} /></button>
        </div>
        {error && <div className="mb-4 p-3 rounded-lg text-sm" style={{ background: "#1a0a0a", color: "#f87171" }}>{error}</div>}
        <form onSubmit={handleSubmit} className="space-y-4">
          {fields.map(({ key, label, placeholder }) => (
            <div key={key}>
              <label className="block text-xs font-black tracking-widest mb-2" style={{ color: "#71717a" }}>{label}</label>
              <input type="text" placeholder={placeholder} value={(form as any)[key]}
                onChange={(e) => setForm({ ...form, [key]: e.target.value })}
                className="w-full px-4 py-3 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/30"
                style={{ background: "#09090b", border: "1px solid #27272a", color: "#fafafa" }} />
            </div>
          ))}
          <button type="submit" disabled={submitting}
            className="w-full py-4 rounded-full text-sm font-black tracking-widest mt-4 disabled:opacity-60 flex items-center justify-center gap-2"
            style={{ background: "#6366f1", color: "#fafafa" }}>
            {submitting ? "ADDING..." : <><Plus size={16} /> ADD TASK</>}
          </button>
        </form>
      </motion.div>
    </motion.div>
  );
}
