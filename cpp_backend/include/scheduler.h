#pragma once

#include <string>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <memory>
#include "task.h"
#include "dag_manager.h"
#include "heap.h"

class SimulationEngine {
public:
    std::unordered_map<std::string, std::shared_ptr<Task>> tasks;
    DAGManager dag_manager;
    std::unique_ptr<CustomHeap> heap;

    int current_time;
    int last_aging_time;
    static constexpr int AGING_INTERVAL = 5;

    std::vector<std::shared_ptr<Task>> completed_tasks;
    std::vector<std::string> execution_log;

    SimulationEngine();
    void reset();
    void add_task(std::shared_ptr<Task> task, const std::vector<std::string>& dependencies = {});
    void log(const std::string& message);
    void apply_aging(int intervals_passed);
    void execute_task(std::shared_ptr<Task> task);
    void run(const std::string& algorithm = "Priority");
};
