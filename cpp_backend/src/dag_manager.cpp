#include "dag_manager.h"
#include <queue>
#include <algorithm>
#include <stdexcept>

void DAGManager::addTaskIfMissing(const std::string& task_id) {
    if (all_tasks.find(task_id) == all_tasks.end() ||
        adj_list.find(task_id) == adj_list.end()) {
        adj_list[task_id] = {};
        in_degree[task_id] = 0;
        all_tasks.insert(task_id);
    }
}

void DAGManager::add_dependency(const std::string& from_id, const std::string& to_id) {
    addTaskIfMissing(from_id);
    addTaskIfMissing(to_id);

    auto& neighbors = adj_list[from_id];
    if (std::find(neighbors.begin(), neighbors.end(), to_id) == neighbors.end()) {
        neighbors.push_back(to_id);
        in_degree[to_id]++;
    }

    if (detect_cycle()) {
        remove_dependency(from_id, to_id);
        throw std::runtime_error(
            "Adding dependency " + from_id + " -> " + to_id +
            " creates a cycle! Dependency rejected.");
    }
}

void DAGManager::remove_dependency(const std::string& from_id, const std::string& to_id) {
    auto it_adj = adj_list.find(from_id);
    if (it_adj != adj_list.end()) {
        auto& neighbors = it_adj->second;
        auto it = std::find(neighbors.begin(), neighbors.end(), to_id);
        if (it != neighbors.end()) {
            neighbors.erase(it);
            in_degree[to_id]--;
        }
    }
}

void DAGManager::reset() {
    adj_list.clear();
    in_degree.clear();
    all_tasks.clear();
}

std::vector<std::string> DAGManager::get_ready_tasks() const {
    std::vector<std::string> ready;
    for (const auto& [task_id, count] : in_degree) {
        if (count == 0) {
            ready.push_back(task_id);
        }
    }
    return ready;
}

std::vector<std::string> DAGManager::resolve_completed_task(const std::string& completed_task_id) {
    std::vector<std::string> newly_ready;

    auto it = adj_list.find(completed_task_id);
    if (it == adj_list.end()) {
        return newly_ready;
    }

    for (const auto& dependent_id : it->second) {
        in_degree[dependent_id]--;
        if (in_degree[dependent_id] == 0) {
            newly_ready.push_back(dependent_id);
        }
    }

    return newly_ready;
}

bool DAGManager::detect_cycle() const {
    std::unordered_map<std::string, int> temp_in_degree = in_degree;

    std::queue<std::string> q;
    for (const auto& node : all_tasks) {
        if (temp_in_degree[node] == 0) {
            q.push(node);
        }
    }

    int processed_count = 0;
    while (!q.empty()) {
        std::string curr = q.front();
        q.pop();
        processed_count++;

        auto it = adj_list.find(curr);
        if (it != adj_list.end()) {
            for (const auto& neighbor : it->second) {
                temp_in_degree[neighbor]--;
                if (temp_in_degree[neighbor] == 0) {
                    q.push(neighbor);
                }
            }
        }
    }

    return processed_count != static_cast<int>(all_tasks.size());
}
