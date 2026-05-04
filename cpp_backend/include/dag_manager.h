#pragma once

#include <string>
#include <vector>
#include <unordered_map>
#include <unordered_set>

class DAGManager {
public:
    std::unordered_map<std::string, std::vector<std::string>> adj_list;
    std::unordered_map<std::string, int> in_degree;
    std::unordered_set<std::string> all_tasks;

    void addTaskIfMissing(const std::string& task_id);
    void add_dependency(const std::string& from_id, const std::string& to_id);
    void remove_dependency(const std::string& from_id, const std::string& to_id);
    void reset();
    std::vector<std::string> get_ready_tasks() const;
    std::vector<std::string> resolve_completed_task(const std::string& completed_task_id);
    bool detect_cycle() const;
};
