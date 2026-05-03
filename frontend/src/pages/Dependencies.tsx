import { useState, useEffect, useCallback } from "react";
import { motion } from "framer-motion";
import { Network, Plus, X } from "lucide-react";
import { getDependencies, addDependency } from "../lib/api";
import type { DependencyNode, DependencyEdge } from "../lib/api";

export default function Dependencies() {
  const [nodes, setNodes] = useState<DependencyNode[]>([]);
  const [edges, setEdges] = useState<DependencyEdge[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showModal, setShowModal] = useState(false);

  const fetchDeps = useCallback(async () => {
    try { const res = await getDependencies(); setNodes(res.data.nodes); setEdges(res.data.edges); setError(null); }
    catch { setError("Cannot connect to backend."); } finally { setLoading(false); }
  }, []);

  useEffect(() => { fetchDeps(); }, [fetchDeps]);

  const STATUS_COLORS: Record<string, string> = {
    PENDING: "#f59e0b", RUNNING: "#6366f1", COMPLETED: "#10b981", MISSED: "#ef4444", DELETED: "#71717a",
  };

  return (
    <div style={{ minHeight: "100vh", background: "#09090b" }}>
      <section className="pt-28 pb-12 px-6" style={{ background: "linear-gradient(160deg, #09090b, #18181b)" }}>
        <div className="max-w-7xl mx-auto">
          <p className="text-xs font-black tracking-widest mb-3" style={{ color: "#6366f1" }}>DEPENDENCY GRAPH</p>
          <div className="flex justify-between items-end flex-wrap gap-6">
            <h1 className="text-5xl md:text-7xl font-black leading-none" style={{ color: "#fafafa" }}>
              TASK<br /><span style={{ color: "#6366f1" }}>FLOW.</span>
            </h1>
            <button onClick={() => setShowModal(true)}
              className="flex items-center gap-2 px-6 py-3 rounded-full text-sm font-black tracking-widest"
              style={{ background: "#6366f1", color: "#fafafa" }}>
              <Plus size={16} /> ADD DEPENDENCY
            </button>
          </div>
          <p className="mt-4 text-lg" style={{ color: "#71717a" }}>{edges.length} edges across {nodes.length} tasks</p>
        </div>
      </section>

      <section className="px-6 py-12">
        <div className="max-w-7xl mx-auto space-y-8">
          {error && <div className="p-4 rounded-xl text-sm" style={{ background: "#1a0a0a", color: "#f87171", border: "1px solid #3b0f0f" }}>⚠️ {error}</div>}

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="p-6 rounded-2xl" style={{ background: "#18181b", border: "1px solid #27272a" }}>
              <p className="text-xs font-black tracking-widest mb-6" style={{ color: "#6366f1" }}>TASK NODES</p>
              {loading ? <p className="text-sm" style={{ color: "#71717a" }}>Loading...</p> :
                nodes.length === 0 ? <p className="text-sm" style={{ color: "#71717a" }}>No tasks. Add tasks from the Tasks page first.</p> :
                <div className="space-y-2">
                  {nodes.map((node) => (
                    <div key={node.id} className="flex items-center justify-between p-4 rounded-xl" style={{ background: "#09090b" }}>
                      <div className="flex items-center gap-3">
                        <div className="w-2.5 h-2.5 rounded-full" style={{ background: STATUS_COLORS[node.status] || "#71717a" }} />
                        <span className="font-mono text-sm font-black" style={{ color: "#6366f1" }}>{node.id}</span>
                        <span className="text-xs" style={{ color: "#71717a" }}>{node.name}</span>
                      </div>
                      <span className="text-xs font-black px-2 py-0.5 rounded-full"
                        style={{ background: (STATUS_COLORS[node.status] || "#71717a") + "22", color: STATUS_COLORS[node.status] || "#71717a" }}>
                        {node.status}
                      </span>
                    </div>
                  ))}
                </div>
              }
            </div>

            <div className="p-6 rounded-2xl" style={{ background: "#18181b", border: "1px solid #27272a" }}>
              <p className="text-xs font-black tracking-widest mb-6" style={{ color: "#6366f1" }}>DEPENDENCY EDGES</p>
              {edges.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-16">
                  <Network size={48} style={{ color: "#27272a" }} className="mb-4" />
                  <p className="text-sm" style={{ color: "#71717a" }}>No dependencies defined yet.</p>
                </div>
              ) : (
                <div className="space-y-2">
                  {edges.map((edge, i) => (
                    <div key={i} className="flex items-center gap-3 p-4 rounded-xl" style={{ background: "#09090b" }}>
                      <span className="font-mono text-sm font-black px-3 py-1 rounded-lg" style={{ background: "#18181b", color: "#6366f1" }}>{edge.from}</span>
                      <span style={{ color: "#27272a" }}>→</span>
                      <span className="font-mono text-sm font-black px-3 py-1 rounded-lg" style={{ background: "#18181b", color: "#3b82f6" }}>{edge.to}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {edges.length > 0 && (
            <div className="p-6 rounded-2xl" style={{ background: "#18181b", border: "1px solid #27272a" }}>
              <p className="text-xs font-black tracking-widest mb-6" style={{ color: "#6366f1" }}>EXECUTION FLOW VISUALIZATION</p>
              <div className="flex flex-wrap gap-6">
                {nodes.filter(n => n.in_degree === 0).map(root => (
                  <FlowNode key={root.id} node={root} edges={edges} allNodes={nodes} STATUS_COLORS={STATUS_COLORS} depth={0} />
                ))}
              </div>
            </div>
          )}
        </div>
      </section>

      {showModal && <AddDepModal nodes={nodes} onClose={() => setShowModal(false)} onAdded={fetchDeps} />}
    </div>
  );
}

function FlowNode({ node, edges, allNodes, STATUS_COLORS, depth }: any) {
  const children = edges.filter((e: DependencyEdge) => e.from === node.id)
    .map((e: DependencyEdge) => allNodes.find((n: DependencyNode) => n.id === e.to)).filter(Boolean);
  return (
    <div className="flex flex-col items-start gap-2">
      <div className="px-4 py-2 rounded-xl text-xs font-mono font-black"
        style={{ background: (STATUS_COLORS[node.status] || "#71717a"), color: "#fafafa", opacity: Math.max(0.5, 1 - depth * 0.15) }}>
        {node.id}
      </div>
      {children.length > 0 && (
        <div className="flex gap-3 pl-4 ml-2 border-l-2 border-dashed" style={{ borderColor: "#27272a" }}>
          {children.map((child: DependencyNode) => (
            <FlowNode key={child.id} node={child} edges={edges} allNodes={allNodes} STATUS_COLORS={STATUS_COLORS} depth={depth + 1} />
          ))}
        </div>
      )}
    </div>
  );
}

function AddDepModal({ nodes, onClose, onAdded }: { nodes: DependencyNode[]; onClose: () => void; onAdded: () => void }) {
  const [fromId, setFromId] = useState("");
  const [toId, setToId] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!fromId || !toId) { setError("Both tasks are required."); return; }
    if (fromId === toId) { setError("Cannot depend on itself."); return; }
    setSubmitting(true); setError(null);
    try { await addDependency(fromId, toId); onAdded(); onClose(); }
    catch (err: any) { setError(err.response?.data?.error || "Failed."); } finally { setSubmitting(false); }
  };

  return (
    <motion.div className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ background: "rgba(9,9,11,0.92)", backdropFilter: "blur(8px)" }}
      initial={{ opacity: 0 }} animate={{ opacity: 1 }} onClick={onClose}>
      <motion.div className="w-full max-w-sm p-8 rounded-2xl" style={{ background: "#18181b", border: "1px solid #27272a" }}
        initial={{ scale: 0.9 }} animate={{ scale: 1 }} onClick={(e) => e.stopPropagation()}>
        <div className="flex justify-between items-center mb-6">
          <div>
            <p className="text-xs font-black tracking-widest mb-1" style={{ color: "#6366f1" }}>NEW DEPENDENCY</p>
            <h2 className="text-xl font-black" style={{ color: "#fafafa" }}>ADD EDGE</h2>
          </div>
          <button onClick={onClose} style={{ color: "#71717a" }}><X size={18} /></button>
        </div>
        {error && <div className="mb-4 p-3 rounded-lg text-sm" style={{ background: "#1a0a0a", color: "#f87171" }}>{error}</div>}
        <form onSubmit={handleSubmit} className="space-y-4">
          {[{ label: "MUST RUN FIRST (FROM)", val: fromId, set: setFromId }, { label: "MUST RUN AFTER (TO)", val: toId, set: setToId }].map(({ label, val, set }) => (
            <div key={label}>
              <label className="block text-xs font-black tracking-widest mb-2" style={{ color: "#71717a" }}>{label}</label>
              <select value={val} onChange={(e) => set(e.target.value)}
                className="w-full px-4 py-3 rounded-xl text-sm focus:outline-none"
                style={{ background: "#09090b", border: "1px solid #27272a", color: "#fafafa" }}>
                <option value="">-- Select Task --</option>
                {nodes.map((n: DependencyNode) => <option key={n.id} value={n.id}>{n.id} — {n.name}</option>)}
              </select>
            </div>
          ))}
          <button type="submit" disabled={submitting}
            className="w-full py-4 rounded-full text-sm font-black tracking-widest disabled:opacity-60"
            style={{ background: "#6366f1", color: "#fafafa" }}>
            {submitting ? "ADDING..." : "ADD DEPENDENCY"}
          </button>
        </form>
      </motion.div>
    </motion.div>
  );
}
