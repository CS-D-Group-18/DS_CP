"""
Flask REST API for the Task Scheduling System.
Bridges the Python backend logic to the React frontend.
Run with: python api.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify
from flask_cors import CORS

from scheduler import SimulationEngine
from task import Task, TaskStatus

app = Flask(__name__)
CORS(app)

# Singleton engine shared across all requests
engine = SimulationEngine()


def task_to_dict(task):
    return {
        "task_id": task.task_id,
        "name": task.name,
        "priority": task.priority,
        "exec_time": task.exec_time,
        "deadline": task.deadline,
        "arrival_time": task.arrival_time,
        "waiting_time": task.waiting_time,
        "turnaround_time": task.turnaround_time,
        "completion_time": task.completion_time,
        "status": task.status.value,
    }


# ──────────────────────────────────────────────
# Dashboard
# ──────────────────────────────────────────────
@app.route("/api/dashboard", methods=["GET"])
def dashboard():
    tasks = list(engine.tasks.values())
    total = len(tasks)
    completed = len([t for t in tasks if t.status == TaskStatus.COMPLETED])
    running = len([t for t in tasks if t.status == TaskStatus.RUNNING])
    pending = len([t for t in tasks if t.status == TaskStatus.PENDING])
    failed = len([t for t in tasks if t.status == TaskStatus.MISSED])
    deleted = len([t for t in tasks if t.status == TaskStatus.DELETED])

    avg_wait = 0
    avg_turnaround = 0
    if engine.completed_tasks:
        avg_wait = sum(t.waiting_time for t in engine.completed_tasks) / len(engine.completed_tasks)
        avg_turnaround = sum(t.turnaround_time for t in engine.completed_tasks) / len(engine.completed_tasks)

    efficiency = round((completed / total * 100), 1) if total > 0 else 0

    # Recent logs (last 10)
    recent_logs = engine.execution_log[-10:] if engine.execution_log else []

    return jsonify({
        "stats": {
            "total": total,
            "completed": completed,
            "running": running,
            "pending": pending,
            "failed": failed,
            "deleted": deleted,
            "efficiency": efficiency,
            "avg_wait": round(avg_wait, 2),
            "avg_turnaround": round(avg_turnaround, 2),
            "current_time": engine.current_time,
        },
        "recent_logs": recent_logs,
    })


# ──────────────────────────────────────────────
# Tasks
# ──────────────────────────────────────────────
@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    tasks = [task_to_dict(t) for t in engine.tasks.values()]
    return jsonify(tasks)


@app.route("/api/tasks", methods=["POST"])
def add_task():
    data = request.get_json()
    try:
        task_id = str(data["task_id"]).strip()
        name = str(data["name"]).strip()
        if not task_id or not name:
            return jsonify({"error": "Task ID and Name are required."}), 400
        if task_id in engine.tasks:
            return jsonify({"error": f"Task ID '{task_id}' already exists."}), 409

        priority = int(data.get("priority", 0))
        exec_time = int(data.get("exec_time", 1))
        deadline = int(data.get("deadline", 0))
        arrival_time = int(data.get("arrival_time", 0))

        if exec_time < 0 or arrival_time < 0:
            return jsonify({"error": "exec_time and arrival_time cannot be negative."}), 400

        new_task = Task(task_id, name, priority, exec_time, deadline, arrival_time)
        engine.add_task(new_task)
        return jsonify(task_to_dict(new_task)), 201
    except (KeyError, ValueError) as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/tasks/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    if task_id not in engine.tasks:
        return jsonify({"error": "Task not found."}), 404
    engine.tasks[task_id].status = TaskStatus.DELETED
    return jsonify({"message": f"Task {task_id} marked as deleted."})


# ──────────────────────────────────────────────
# Dependencies
# ──────────────────────────────────────────────
@app.route("/api/dependencies", methods=["GET"])
def get_dependencies():
    nodes = []
    for tid in engine.dag_manager.all_tasks:
        task = engine.tasks.get(tid)
        nodes.append({
            "id": tid,
            "name": task.name if task else tid,
            "status": task.status.value if task else "UNKNOWN",
            "in_degree": engine.dag_manager.in_degree.get(tid, 0),
        })

    edges = []
    for from_id, neighbors in engine.dag_manager.adj_list.items():
        for to_id in neighbors:
            edges.append({"from": from_id, "to": to_id})

    return jsonify({"nodes": nodes, "edges": edges})


@app.route("/api/dependencies", methods=["POST"])
def add_dependency():
    data = request.get_json()
    from_id = str(data.get("from_id", "")).strip()
    to_id = str(data.get("to_id", "")).strip()
    if not from_id or not to_id:
        return jsonify({"error": "from_id and to_id are required."}), 400
    if from_id not in engine.tasks or to_id not in engine.tasks:
        return jsonify({"error": "Both tasks must exist before adding a dependency."}), 400
    try:
        engine.dag_manager.add_dependency(from_id, to_id)
        return jsonify({"message": f"Dependency {from_id} → {to_id} added."})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


# ──────────────────────────────────────────────
# Scheduler
# ──────────────────────────────────────────────
@app.route("/api/scheduler/run", methods=["POST"])
def run_scheduler():
    data = request.get_json() or {}
    algorithm = data.get("algorithm", "Priority")
    if algorithm not in ("Priority", "SJF", "EDF"):
        return jsonify({"error": "Unknown algorithm. Use Priority, SJF, or EDF."}), 400
    if not engine.tasks:
        return jsonify({"error": "No tasks available to schedule."}), 400
    try:
        engine.run(algorithm)
        return jsonify({
            "message": f"Simulation completed with {algorithm} at time {engine.current_time}.",
            "current_time": engine.current_time,
            "log": engine.execution_log,
            "tasks": [task_to_dict(t) for t in engine.tasks.values()],
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/scheduler/reset", methods=["POST"])
def reset_scheduler():
    engine.reset()
    return jsonify({"message": "Engine reset successfully."})


# ──────────────────────────────────────────────
# Logs
# ──────────────────────────────────────────────
@app.route("/api/logs", methods=["GET"])
def get_logs():
    return jsonify(engine.execution_log)


# ──────────────────────────────────────────────
# Reports / Analytics
# ──────────────────────────────────────────────
@app.route("/api/reports", methods=["GET"])
def get_reports():
    if not engine.completed_tasks:
        return jsonify({"error": "No simulation data. Run scheduler first."}), 400

    tasks = list(engine.tasks.values())
    completed = [t for t in tasks if t.status == TaskStatus.COMPLETED]
    missed = [t for t in tasks if t.status == TaskStatus.MISSED]
    pending = [t for t in tasks if t.status == TaskStatus.PENDING]
    deleted = [t for t in tasks if t.status == TaskStatus.DELETED]

    avg_wait = sum(t.waiting_time for t in engine.completed_tasks) / len(engine.completed_tasks)
    avg_turnaround = sum(t.turnaround_time for t in engine.completed_tasks) / len(engine.completed_tasks)

    # Build Gantt data
    gantt = []
    for t in engine.completed_tasks:
        gantt.append({
            "task_id": t.task_id,
            "name": t.name,
            "start": t.completion_time - t.exec_time,
            "end": t.completion_time,
            "exec_time": t.exec_time,
            "status": t.status.value,
        })

    # CPU utilization timeline
    if engine.completed_tasks:
        max_time = max(t.completion_time for t in engine.completed_tasks)
        time_series = [0] * (max_time + 1)
        for t in engine.completed_tasks:
            start = t.completion_time - t.exec_time
            for i in range(start, t.completion_time):
                if i <= max_time:
                    time_series[i] = 1
        cum = 0
        utilization = []
        for i, active in enumerate(time_series):
            cum += active
            util = round((cum / (i + 1)) * 100, 1) if i > 0 else (active * 100)
            utilization.append({"time": i, "utilization": util})
    else:
        utilization = []

    return jsonify({
        "summary": {
            "total": len(tasks),
            "completed": len(completed),
            "missed": len(missed),
            "pending": len(pending),
            "deleted": len(deleted),
            "avg_wait": round(avg_wait, 2),
            "avg_turnaround": round(avg_turnaround, 2),
            "total_time": engine.current_time,
            "efficiency": round(len(completed) / len(tasks) * 100, 1) if tasks else 0,
        },
        "tasks": [task_to_dict(t) for t in tasks],
        "gantt": gantt,
        "utilization": utilization,
        "status_breakdown": {
            "Completed": len(completed),
            "Missed": len(missed),
            "Pending": len(pending),
            "Deleted": len(deleted),
        },
    })


# ──────────────────────────────────────────────
# Demo Data
# ──────────────────────────────────────────────
@app.route("/api/demo", methods=["POST"])
def load_demo():
    engine.reset()

    tasks_data = [
        ("INF-101", "Provision Cloud VPC", 1, 5, 20, 0),
        ("INF-102", "Configure Firewall", 2, 3, 25, 0),
        ("DB-201", "Setup PostgreSQL Cluster", 2, 6, 30, 2),
        ("STR-202", "S3 Bucket Provisioning", 3, 2, 35, 2),
        ("APP-301", "Build Backend Image", 3, 8, 40, 0),
        ("APP-302", "Compile Frontend Assets", 4, 4, 40, 0),
        ("DEP-401", "Stage Deploy", 2, 4, 50, 5),
        ("TST-402", "Run Integration Tests", 1, 10, 70, 5),
        ("PRD-501", "Production Rollout", 1, 5, 100, 10),
    ]
    for t in tasks_data:
        engine.add_task(Task(*t))

    deps = [
        ("INF-101", "DB-201"), ("INF-101", "INF-102"),
        ("DB-201", "DEP-401"), ("INF-102", "DEP-401"),
        ("APP-301", "DEP-401"), ("APP-302", "DEP-401"),
        ("DEP-401", "TST-402"),
        ("TST-402", "PRD-501"), ("STR-202", "PRD-501"),
    ]
    for f, t in deps:
        engine.dag_manager.add_dependency(f, t)

    engine.run("Priority")
    return jsonify({"message": "Demo data loaded and simulated.", "current_time": engine.current_time})


if __name__ == "__main__":
    print("Starting Task Scheduling API on http://localhost:5001")
    app.run(port=5001, debug=True, use_reloader=False)
