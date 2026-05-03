import axios from "axios";

// Directly target Flask API - CORS is enabled on the backend
// Using direct URL avoids Vite proxy 502 issues
const API_BASE = "http://127.0.0.1:5001/api";

const api = axios.create({
  baseURL: API_BASE,
  headers: { "Content-Type": "application/json" },
});

export default api;

// Types
export interface TaskData {
  task_id: string;
  name: string;
  priority: number;
  exec_time: number;
  deadline: number;
  arrival_time: number;
  waiting_time: number;
  turnaround_time: number;
  completion_time: number;
  status: string;
}

export interface DashboardStats {
  total: number;
  completed: number;
  running: number;
  pending: number;
  failed: number;
  deleted: number;
  efficiency: number;
  avg_wait: number;
  avg_turnaround: number;
  current_time: number;
}

export interface DependencyNode {
  id: string;
  name: string;
  status: string;
  in_degree: number;
}

export interface DependencyEdge {
  from: string;
  to: string;
}

// API Calls
export const getDashboard = () => api.get<{ stats: DashboardStats; recent_logs: string[] }>("/dashboard");
export const getTasks = () => api.get<TaskData[]>("/tasks");
export const addTask = (data: Omit<TaskData, "waiting_time" | "turnaround_time" | "completion_time" | "status">) =>
  api.post<TaskData>("/tasks", data);
export const deleteTask = (id: string) => api.delete(`/tasks/${id}`);
export const getDependencies = () => api.get<{ nodes: DependencyNode[]; edges: DependencyEdge[] }>("/dependencies");
export const addDependency = (from_id: string, to_id: string) =>
  api.post("/dependencies", { from_id, to_id });
export const runScheduler = (algorithm: string) => api.post("/scheduler/run", { algorithm });
export const resetScheduler = () => api.post("/scheduler/reset");
export const getLogs = () => api.get<string[]>("/logs");
export const getReports = () => api.get("/reports");
export const loadDemo = () => api.post("/demo");
