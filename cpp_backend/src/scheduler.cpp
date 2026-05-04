#include "scheduler.h"
#include <algorithm>
#include <sstream>
#include <stdexcept>
#include <climits>

SimulationEngine::SimulationEngine()
    : current_time(0)
    , last_aging_time(0)
{}

void SimulationEngine::reset() {
    tasks.clear();
    dag_manager.reset();
    completed_tasks.clear();
    execution_log.clear();
    current_time = 0;
    last_aging_time = 0;
    heap.reset();
}

void SimulationEngine::add_task(std::shared_ptr<Task> task,
                                const std::vector<std::string>& dependencies) {
    tasks[task->task_id] = task;
    dag_manager.addTaskIfMissing(task->task_id);

    for (const auto& dep_id : dependencies) {
        dag_manager.add_dependency(dep_id, task->task_id);
    }
}

void SimulationEngine::log(const std::string& message) {
    execution_log.push_back(message);
}

void SimulationEngine::apply_aging(int intervals_passed) {
    if (!heap || heap->is_empty()) return;

    for (auto& task : heap->getHeap()) {
        if (task->status == TaskStatus::PENDING) {
            int old_priority = task->priority;
            task->priority = std::max(0, task->priority - intervals_passed);

            if (old_priority != task->priority) {
                std::ostringstream oss;
                oss << "Time " << current_time << ": Task " << task->task_id
                    << " aged. Priority boosted from " << old_priority
                    << " to " << task->priority;
                log(oss.str());
                heap->updateKey(task->task_id);
            }
        }
    }
}

void SimulationEngine::execute_task(std::shared_ptr<Task> task) {
    task->waiting_time = current_time - task->arrival_time;

    task->status = TaskStatus::RUNNING;
    {
        std::ostringstream oss;
        oss << "Time " << current_time << ": Running Task " << task->task_id
            << " ('" << task->name << "', priority: " << task->priority
            << ", execTime: " << task->exec_time << ")";
        log(oss.str());
    }

    current_time += task->exec_time;

    task->completion_time = current_time;
    task->turnaround_time = task->completion_time - task->arrival_time;

    if (task->deadline > 0 && current_time > task->deadline) {
        task->status = TaskStatus::MISSED;
        std::ostringstream oss;
        oss << "Time " << current_time << ": Task " << task->task_id
            << " COMPLETED but MISSED deadline! (Deadline: " << task->deadline << ")";
        log(oss.str());
    } else {
        task->status = TaskStatus::COMPLETED;
        std::ostringstream oss;
        oss << "Time " << current_time << ": Task " << task->task_id
            << " COMPLETED successfully.";
        log(oss.str());
    }

    completed_tasks.push_back(task);

    auto newly_unlocked = dag_manager.resolve_completed_task(task->task_id);
    if (!newly_unlocked.empty()) {
        std::ostringstream oss;
        oss << "Time " << current_time << ": Task " << task->task_id
            << " completion unlocked tasks: [";
        for (size_t i = 0; i < newly_unlocked.size(); ++i) {
            if (i > 0) oss << ", ";
            oss << "'" << newly_unlocked[i] << "'";
        }
        oss << "]";
        log(oss.str());
    }
}

void SimulationEngine::run(const std::string& algorithm) {
    log("--- Starting Simulation (" + algorithm + " Scheduling) ---");

    // Initialize the correct heap behavior
    if (algorithm == "Priority") {
        heap = std::make_unique<CustomHeap>(
            [](const Task& t) { return t.priority; }, true);
    } else if (algorithm == "SJF") {
        heap = std::make_unique<CustomHeap>(
            [](const Task& t) { return t.exec_time; }, true);
    } else if (algorithm == "EDF") {
        heap = std::make_unique<CustomHeap>(
            [](const Task& t) { return t.deadline; }, true);
    } else {
        throw std::invalid_argument("Unknown scheduling algorithm.");
    }

    std::unordered_set<std::string> unstarted_task_ids;
    for (const auto& [tid, _] : tasks) {
        unstarted_task_ids.insert(tid);
    }

    // Reset metrics for a fresh run
    completed_tasks.clear();
    execution_log.clear();
    current_time = 0;
    last_aging_time = 0;

    // Restore in-degrees from adjacency list
    dag_manager.in_degree.clear();
    for (const auto& [tid, _] : tasks) {
        dag_manager.in_degree[tid] = 0;
    }
    for (const auto& [u, neighbors] : dag_manager.adj_list) {
        for (const auto& v : neighbors) {
            if (dag_manager.in_degree.count(v)) {
                dag_manager.in_degree[v]++;
            }
        }
    }

    // Re-log the start message after clearing logs
    log("--- Starting Simulation (" + algorithm + " Scheduling) ---");

    while (!unstarted_task_ids.empty() || !heap->is_empty()) {
        // 1. Check for new arrivals that are also unlocked (in-degree == 0)
        std::vector<std::shared_ptr<Task>> ready_to_load;
        for (auto it = unstarted_task_ids.begin(); it != unstarted_task_ids.end(); ) {
            const auto& t_id = *it;
            auto& task = tasks[t_id];

            if (task->arrival_time <= current_time &&
                dag_manager.in_degree.count(t_id) &&
                dag_manager.in_degree[t_id] == 0) {

                if (task->status == TaskStatus::DELETED) {
                    it = unstarted_task_ids.erase(it);
                    continue;
                }

                ready_to_load.push_back(task);
                it = unstarted_task_ids.erase(it);
            } else {
                ++it;
            }
        }

        for (auto& task : ready_to_load) {
            heap->insert(task);
            std::ostringstream oss;
            oss << "Time " << current_time << ": Task " << task->task_id
                << " arrived and added to ready queue.";
            log(oss.str());
        }

        // 2. If heap is empty but we still have unstarted tasks, advance time
        if (heap->is_empty() && !unstarted_task_ids.empty()) {
            int next_arrival = INT_MAX;
            for (const auto& tid : unstarted_task_ids) {
                next_arrival = std::min(next_arrival, tasks[tid]->arrival_time);
            }

            if (next_arrival <= current_time) {
                throw std::runtime_error(
                    "Deadlock detected! Tasks are waiting on dependencies that will never resolve.");
            }

            current_time = next_arrival;
            continue;
        }

        // 3. Apply Task Aging (Priority scheduling only)
        if (algorithm == "Priority") {
            int intervals_passed = (current_time - last_aging_time) / AGING_INTERVAL;
            if (intervals_passed > 0) {
                apply_aging(intervals_passed);
                last_aging_time += intervals_passed * AGING_INTERVAL;
            }
        }

        // 4. Extract and execute the next task
        auto current_task = heap->extract();
        if (current_task) {
            execute_task(current_task);
        }
    }

    log("--- Simulation Complete at Time " + std::to_string(current_time) + " ---");
}
