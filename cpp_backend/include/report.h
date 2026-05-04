#pragma once

#include <string>
#include <vector>
#include <memory>
#include "task.h"
#include "scheduler.h"

class ReportGenerator {
public:
    explicit ReportGenerator(const SimulationEngine& engine);

    double calculate_waiting_time() const;
    double calculate_turnaround_time() const;
    double calculate_cpu_utilization() const;

    // Returns a JSON-compatible summary map as key-value pairs
    struct Summary {
        int total_tasks;
        int tasks_executed;
        int completed_successfully;
        int missed_deadlines;
        int cancelled_deleted;
        int left_pending;
        double avg_waiting_time;
        double avg_turnaround_time;
        double cpu_utilization;
        double throughput;
        int total_time;
    };

    Summary generate_summary() const;

private:
    std::vector<std::shared_ptr<Task>> all_tasks;
    std::vector<std::shared_ptr<Task>> executed_tasks;
    int total_time;
};
