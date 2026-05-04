/**
 * main.cpp — Crow REST API server for the Task Scheduling System.
 * Drop-in replacement for the Python Flask api.py.
 * All endpoints, JSON field names, and HTTP methods are identical.
 */

#include <iostream>
#include <mutex>
#include <memory>
#include <algorithm>
#include <cmath>

#include "crow.h"
#include "crow/middlewares/cors.h"
#include <nlohmann/json.hpp>

#include "task.h"
#include "dag_manager.h"
#include "heap.h"
#include "scheduler.h"
#include "report.h"

using json = nlohmann::json;

// ---------------------------------------------------------------------------
// Global state (mirrors the Python global `engine = SimulationEngine()`)
// ---------------------------------------------------------------------------
static SimulationEngine engine;
static std::mutex engine_mutex;

// ---------------------------------------------------------------------------
// Helper: serialise a Task to JSON (mirrors Python task_to_dict)
// ---------------------------------------------------------------------------
static json task_to_json(const std::shared_ptr<Task>& t) {
    return {
        {"task_id",         t->task_id},
        {"name",            t->name},
        {"priority",        t->priority},
        {"exec_time",       t->exec_time},
        {"deadline",        t->deadline},
        {"arrival_time",    t->arrival_time},
        {"waiting_time",    t->waiting_time},
        {"turnaround_time", t->turnaround_time},
        {"completion_time", t->completion_time},
        {"status",          taskStatusToString(t->status)}
    };
}

// ---------------------------------------------------------------------------
// Entry point
// ---------------------------------------------------------------------------
int main() {
    crow::App<crow::CORSHandler> app;

    // ── CORS (mirrors Flask-CORS behaviour) ──
    auto& cors = app.get_middleware<crow::CORSHandler>();
    cors.global()
        .headers("Content-Type", "Accept", "Authorization")
        .methods("GET"_method, "POST"_method, "PUT"_method,
                 "DELETE"_method, "OPTIONS"_method)
        .origin("*");

    // ════════════════════════════════════════════
    //  GET /api/dashboard
    // ════════════════════════════════════════════
    CROW_ROUTE(app, "/api/dashboard").methods("GET"_method)
    ([&]() {
        std::lock_guard<std::mutex> lock(engine_mutex);

        auto& tasks = engine.tasks;
        int total = static_cast<int>(tasks.size());
        int completed = 0, running = 0, pending = 0, failed = 0, deleted = 0;

        for (const auto& [id, t] : tasks) {
            switch (t->status) {
                case TaskStatus::COMPLETED: completed++; break;
                case TaskStatus::RUNNING:   running++;   break;
                case TaskStatus::PENDING:   pending++;   break;
                case TaskStatus::MISSED:    failed++;    break;
                case TaskStatus::DELETED:   deleted++;   break;
            }
        }

        double avg_wait = 0.0, avg_turnaround = 0.0;
        if (!engine.completed_tasks.empty()) {
            double sw = 0, st = 0;
            for (const auto& ct : engine.completed_tasks) {
                sw += ct->waiting_time;
                st += ct->turnaround_time;
            }
            avg_wait = sw / engine.completed_tasks.size();
            avg_turnaround = st / engine.completed_tasks.size();
        }

        double efficiency = (total > 0)
            ? std::round(static_cast<double>(completed) / total * 1000.0) / 10.0
            : 0.0;

        // Recent logs (last 10)
        json recent_logs = json::array();
        auto& elog = engine.execution_log;
        int start = std::max(0, static_cast<int>(elog.size()) - 10);
        for (int i = start; i < static_cast<int>(elog.size()); ++i) {
            recent_logs.push_back(elog[i]);
        }

        json result = {
            {"stats", {
                {"total",          total},
                {"completed",      completed},
                {"running",        running},
                {"pending",        pending},
                {"failed",         failed},
                {"deleted",        deleted},
                {"efficiency",     efficiency},
                {"avg_wait",       std::round(avg_wait * 100.0) / 100.0},
                {"avg_turnaround", std::round(avg_turnaround * 100.0) / 100.0},
                {"current_time",   engine.current_time}
            }},
            {"recent_logs", recent_logs}
        };

        auto resp = crow::response(200, result.dump());
        resp.set_header("Content-Type", "application/json");
        return resp;
    });

    // ════════════════════════════════════════════
    //  GET /api/tasks
    // ════════════════════════════════════════════
    CROW_ROUTE(app, "/api/tasks").methods("GET"_method)
    ([&]() {
        std::lock_guard<std::mutex> lock(engine_mutex);

        json arr = json::array();
        for (const auto& [id, t] : engine.tasks) {
            arr.push_back(task_to_json(t));
        }

        auto resp = crow::response(200, arr.dump());
        resp.set_header("Content-Type", "application/json");
        return resp;
    });

    // ════════════════════════════════════════════
    //  POST /api/tasks
    // ════════════════════════════════════════════
    CROW_ROUTE(app, "/api/tasks").methods("POST"_method)
    ([&](const crow::request& req) {
        std::lock_guard<std::mutex> lock(engine_mutex);

        json data;
        try { data = json::parse(req.body); }
        catch (...) {
            return crow::response(400, json({{"error", "Invalid JSON."}}).dump());
        }

        try {
            std::string task_id = data.at("task_id").get<std::string>();
            std::string name    = data.at("name").get<std::string>();

            // Trim whitespace
            auto trim = [](std::string s) {
                s.erase(0, s.find_first_not_of(" \t\n\r"));
                s.erase(s.find_last_not_of(" \t\n\r") + 1);
                return s;
            };
            task_id = trim(task_id);
            name    = trim(name);

            if (task_id.empty() || name.empty()) {
                auto r = crow::response(400,
                    json({{"error", "Task ID and Name are required."}}).dump());
                r.set_header("Content-Type", "application/json");
                return r;
            }
            if (engine.tasks.count(task_id)) {
                auto r = crow::response(409,
                    json({{"error", "Task ID '" + task_id + "' already exists."}}).dump());
                r.set_header("Content-Type", "application/json");
                return r;
            }

            int priority     = data.value("priority", 0);
            int exec_time    = data.value("exec_time", 1);
            int deadline     = data.value("deadline", 0);
            int arrival_time = data.value("arrival_time", 0);

            if (exec_time < 0 || arrival_time < 0) {
                auto r = crow::response(400,
                    json({{"error", "exec_time and arrival_time cannot be negative."}}).dump());
                r.set_header("Content-Type", "application/json");
                return r;
            }

            auto new_task = std::make_shared<Task>(task_id, name, priority,
                                                   exec_time, deadline, arrival_time);
            engine.add_task(new_task);

            auto r = crow::response(201, task_to_json(new_task).dump());
            r.set_header("Content-Type", "application/json");
            return r;
        } catch (const std::exception& e) {
            auto r = crow::response(400, json({{"error", std::string(e.what())}}).dump());
            r.set_header("Content-Type", "application/json");
            return r;
        }
    });

    // ════════════════════════════════════════════
    //  DELETE /api/tasks/<task_id>
    // ════════════════════════════════════════════
    CROW_ROUTE(app, "/api/tasks/<string>").methods("DELETE"_method)
    ([&](const std::string& task_id) {
        std::lock_guard<std::mutex> lock(engine_mutex);

        auto it = engine.tasks.find(task_id);
        if (it == engine.tasks.end()) {
            auto r = crow::response(404,
                json({{"error", "Task not found."}}).dump());
            r.set_header("Content-Type", "application/json");
            return r;
        }

        it->second->status = TaskStatus::DELETED;
        auto r = crow::response(200,
            json({{"message", "Task " + task_id + " marked as deleted."}}).dump());
        r.set_header("Content-Type", "application/json");
        return r;
    });

    // ════════════════════════════════════════════
    //  GET /api/dependencies
    // ════════════════════════════════════════════
    CROW_ROUTE(app, "/api/dependencies").methods("GET"_method)
    ([&]() {
        std::lock_guard<std::mutex> lock(engine_mutex);

        json nodes = json::array();
        for (const auto& tid : engine.dag_manager.all_tasks) {
            auto task_it = engine.tasks.find(tid);
            std::string name   = task_it != engine.tasks.end() ? task_it->second->name : tid;
            std::string status = task_it != engine.tasks.end()
                ? taskStatusToString(task_it->second->status) : "UNKNOWN";
            int in_deg = 0;
            auto deg_it = engine.dag_manager.in_degree.find(tid);
            if (deg_it != engine.dag_manager.in_degree.end()) in_deg = deg_it->second;

            nodes.push_back({
                {"id",        tid},
                {"name",      name},
                {"status",    status},
                {"in_degree", in_deg}
            });
        }

        json edges = json::array();
        for (const auto& [from_id, neighbors] : engine.dag_manager.adj_list) {
            for (const auto& to_id : neighbors) {
                edges.push_back({{"from", from_id}, {"to", to_id}});
            }
        }

        json result = {{"nodes", nodes}, {"edges", edges}};
        auto resp = crow::response(200, result.dump());
        resp.set_header("Content-Type", "application/json");
        return resp;
    });

    // ════════════════════════════════════════════
    //  POST /api/dependencies
    // ════════════════════════════════════════════
    CROW_ROUTE(app, "/api/dependencies").methods("POST"_method)
    ([&](const crow::request& req) {
        std::lock_guard<std::mutex> lock(engine_mutex);

        json data;
        try { data = json::parse(req.body); }
        catch (...) {
            return crow::response(400, json({{"error", "Invalid JSON."}}).dump());
        }

        std::string from_id = data.value("from_id", "");
        std::string to_id   = data.value("to_id", "");

        // Trim
        auto trim = [](std::string s) {
            s.erase(0, s.find_first_not_of(" \t\n\r"));
            s.erase(s.find_last_not_of(" \t\n\r") + 1);
            return s;
        };
        from_id = trim(from_id);
        to_id   = trim(to_id);

        if (from_id.empty() || to_id.empty()) {
            auto r = crow::response(400,
                json({{"error", "from_id and to_id are required."}}).dump());
            r.set_header("Content-Type", "application/json");
            return r;
        }
        if (!engine.tasks.count(from_id) || !engine.tasks.count(to_id)) {
            auto r = crow::response(400,
                json({{"error", "Both tasks must exist before adding a dependency."}}).dump());
            r.set_header("Content-Type", "application/json");
            return r;
        }

        try {
            engine.dag_manager.add_dependency(from_id, to_id);
            std::string arrow = from_id + " \xe2\x86\x92 " + to_id; // UTF-8 →
            auto r = crow::response(200,
                json({{"message", "Dependency " + arrow + " added."}}).dump());
            r.set_header("Content-Type", "application/json");
            return r;
        } catch (const std::exception& e) {
            auto r = crow::response(400, json({{"error", std::string(e.what())}}).dump());
            r.set_header("Content-Type", "application/json");
            return r;
        }
    });

    // ════════════════════════════════════════════
    //  POST /api/scheduler/run
    // ════════════════════════════════════════════
    CROW_ROUTE(app, "/api/scheduler/run").methods("POST"_method)
    ([&](const crow::request& req) {
        std::lock_guard<std::mutex> lock(engine_mutex);

        json data;
        try { data = json::parse(req.body.empty() ? "{}" : req.body); }
        catch (...) { data = json::object(); }

        std::string algorithm = data.value("algorithm", "Priority");

        if (algorithm != "Priority" && algorithm != "SJF" && algorithm != "EDF") {
            auto r = crow::response(400,
                json({{"error", "Unknown algorithm. Use Priority, SJF, or EDF."}}).dump());
            r.set_header("Content-Type", "application/json");
            return r;
        }
        if (engine.tasks.empty()) {
            auto r = crow::response(400,
                json({{"error", "No tasks available to schedule."}}).dump());
            r.set_header("Content-Type", "application/json");
            return r;
        }

        try {
            engine.run(algorithm);

            json tasks_arr = json::array();
            for (const auto& [id, t] : engine.tasks) {
                tasks_arr.push_back(task_to_json(t));
            }

            json result = {
                {"message",      "Simulation completed with " + algorithm +
                                 " at time " + std::to_string(engine.current_time) + "."},
                {"current_time", engine.current_time},
                {"log",          engine.execution_log},
                {"tasks",        tasks_arr}
            };

            auto r = crow::response(200, result.dump());
            r.set_header("Content-Type", "application/json");
            return r;
        } catch (const std::exception& e) {
            auto r = crow::response(500, json({{"error", std::string(e.what())}}).dump());
            r.set_header("Content-Type", "application/json");
            return r;
        }
    });

    // ════════════════════════════════════════════
    //  POST /api/scheduler/reset
    // ════════════════════════════════════════════
    CROW_ROUTE(app, "/api/scheduler/reset").methods("POST"_method)
    ([&]() {
        std::lock_guard<std::mutex> lock(engine_mutex);
        engine.reset();
        auto r = crow::response(200,
            json({{"message", "Engine reset successfully."}}).dump());
        r.set_header("Content-Type", "application/json");
        return r;
    });

    // ════════════════════════════════════════════
    //  GET /api/logs
    // ════════════════════════════════════════════
    CROW_ROUTE(app, "/api/logs").methods("GET"_method)
    ([&]() {
        std::lock_guard<std::mutex> lock(engine_mutex);
        json arr = json(engine.execution_log);
        auto r = crow::response(200, arr.dump());
        r.set_header("Content-Type", "application/json");
        return r;
    });

    // ════════════════════════════════════════════
    //  GET /api/reports
    // ════════════════════════════════════════════
    CROW_ROUTE(app, "/api/reports").methods("GET"_method)
    ([&]() {
        std::lock_guard<std::mutex> lock(engine_mutex);

        if (engine.completed_tasks.empty()) {
            auto r = crow::response(400,
                json({{"error", "No simulation data. Run scheduler first."}}).dump());
            r.set_header("Content-Type", "application/json");
            return r;
        }

        int total = static_cast<int>(engine.tasks.size());
        int n_completed = 0, n_missed = 0, n_pending = 0, n_deleted = 0;
        for (const auto& [id, t] : engine.tasks) {
            switch (t->status) {
                case TaskStatus::COMPLETED: n_completed++; break;
                case TaskStatus::MISSED:    n_missed++;    break;
                case TaskStatus::PENDING:   n_pending++;   break;
                case TaskStatus::DELETED:   n_deleted++;   break;
                default: break;
            }
        }

        double avg_wait = 0.0, avg_turnaround = 0.0;
        {
            double sw = 0, st = 0;
            for (const auto& ct : engine.completed_tasks) {
                sw += ct->waiting_time;
                st += ct->turnaround_time;
            }
            avg_wait = sw / engine.completed_tasks.size();
            avg_turnaround = st / engine.completed_tasks.size();
        }

        // Gantt data
        json gantt = json::array();
        for (const auto& t : engine.completed_tasks) {
            gantt.push_back({
                {"task_id",   t->task_id},
                {"name",      t->name},
                {"start",     t->completion_time - t->exec_time},
                {"end",       t->completion_time},
                {"exec_time", t->exec_time},
                {"status",    taskStatusToString(t->status)}
            });
        }

        // CPU utilization timeline
        json utilization = json::array();
        if (!engine.completed_tasks.empty()) {
            int max_time = 0;
            for (const auto& t : engine.completed_tasks) {
                max_time = std::max(max_time, t->completion_time);
            }
            std::vector<int> time_series(max_time + 1, 0);
            for (const auto& t : engine.completed_tasks) {
                int start = t->completion_time - t->exec_time;
                for (int i = start; i < t->completion_time && i <= max_time; ++i) {
                    time_series[i] = 1;
                }
            }
            int cum = 0;
            for (int i = 0; i <= max_time; ++i) {
                cum += time_series[i];
                double util = (i > 0)
                    ? std::round(static_cast<double>(cum) / (i + 1) * 1000.0) / 10.0
                    : static_cast<double>(time_series[i]) * 100.0;
                utilization.push_back({{"time", i}, {"utilization", util}});
            }
        }

        json tasks_arr = json::array();
        for (const auto& [id, t] : engine.tasks) {
            tasks_arr.push_back(task_to_json(t));
        }

        double efficiency = (total > 0)
            ? std::round(static_cast<double>(n_completed) / total * 1000.0) / 10.0
            : 0.0;

        json result = {
            {"summary", {
                {"total",          total},
                {"completed",      n_completed},
                {"missed",         n_missed},
                {"pending",        n_pending},
                {"deleted",        n_deleted},
                {"avg_wait",       std::round(avg_wait * 100.0) / 100.0},
                {"avg_turnaround", std::round(avg_turnaround * 100.0) / 100.0},
                {"total_time",     engine.current_time},
                {"efficiency",     efficiency}
            }},
            {"tasks",            tasks_arr},
            {"gantt",            gantt},
            {"utilization",      utilization},
            {"status_breakdown", {
                {"Completed", n_completed},
                {"Missed",    n_missed},
                {"Pending",   n_pending},
                {"Deleted",   n_deleted}
            }}
        };

        auto r = crow::response(200, result.dump());
        r.set_header("Content-Type", "application/json");
        return r;
    });

    // ════════════════════════════════════════════
    //  POST /api/demo
    // ════════════════════════════════════════════
    CROW_ROUTE(app, "/api/demo").methods("POST"_method)
    ([&]() {
        std::lock_guard<std::mutex> lock(engine_mutex);
        engine.reset();

        // Same demo dataset as the Python version
        struct TD { std::string id, name; int pri, exec, dl, arr; };
        std::vector<TD> tasks_data = {
            {"INF-101", "Provision Cloud VPC",    1, 5,  20,  0},
            {"INF-102", "Configure Firewall",     2, 3,  25,  0},
            {"DB-201",  "Setup PostgreSQL Cluster",2, 6,  30,  2},
            {"STR-202", "S3 Bucket Provisioning",  3, 2,  35,  2},
            {"APP-301", "Build Backend Image",     3, 8,  40,  0},
            {"APP-302", "Compile Frontend Assets", 4, 4,  40,  0},
            {"DEP-401", "Stage Deploy",            2, 4,  50,  5},
            {"TST-402", "Run Integration Tests",   1, 10, 70,  5},
            {"PRD-501", "Production Rollout",      1, 5, 100, 10},
        };
        for (const auto& td : tasks_data) {
            engine.add_task(std::make_shared<Task>(
                td.id, td.name, td.pri, td.exec, td.dl, td.arr));
        }

        struct Dep { std::string from, to; };
        std::vector<Dep> deps = {
            {"INF-101", "DB-201"},  {"INF-101", "INF-102"},
            {"DB-201",  "DEP-401"}, {"INF-102", "DEP-401"},
            {"APP-301", "DEP-401"}, {"APP-302", "DEP-401"},
            {"DEP-401", "TST-402"},
            {"TST-402", "PRD-501"}, {"STR-202", "PRD-501"},
        };
        for (const auto& d : deps) {
            engine.dag_manager.add_dependency(d.from, d.to);
        }

        engine.run("Priority");

        json result = {
            {"message",      "Demo data loaded and simulated."},
            {"current_time", engine.current_time}
        };
        auto r = crow::response(200, result.dump());
        r.set_header("Content-Type", "application/json");
        return r;
    });

    // ── Start ──
    std::cout << "Starting Task Scheduling API on http://localhost:5001" << std::endl;
    app.port(5001).multithreaded().run();
    return 0;
}
