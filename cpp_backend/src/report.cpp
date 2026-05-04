#include "report.h"

ReportGenerator::ReportGenerator(const SimulationEngine& engine)
    : total_time(engine.current_time)
{
    for (const auto& [id, task] : engine.tasks) {
        all_tasks.push_back(task);
    }
    executed_tasks = engine.completed_tasks;
}

double ReportGenerator::calculate_waiting_time() const {
    if (executed_tasks.empty()) return 0.0;

    double total_wait = 0.0;
    for (const auto& t : executed_tasks) {
        total_wait += t->waiting_time;
    }
    return total_wait / static_cast<double>(executed_tasks.size());
}

double ReportGenerator::calculate_turnaround_time() const {
    if (executed_tasks.empty()) return 0.0;

    double total_ta = 0.0;
    for (const auto& t : executed_tasks) {
        total_ta += t->turnaround_time;
    }
    return total_ta / static_cast<double>(executed_tasks.size());
}

double ReportGenerator::calculate_cpu_utilization() const {
    if (total_time == 0) return 0.0;

    double active_time = 0.0;
    for (const auto& t : executed_tasks) {
        active_time += t->exec_time;
    }
    return (active_time / static_cast<double>(total_time)) * 100.0;
}

ReportGenerator::Summary ReportGenerator::generate_summary() const {
    Summary s{};
    s.total_tasks = static_cast<int>(all_tasks.size());
    s.tasks_executed = static_cast<int>(executed_tasks.size());
    s.total_time = total_time;

    for (const auto& t : all_tasks) {
        switch (t->status) {
            case TaskStatus::COMPLETED: s.completed_successfully++; break;
            case TaskStatus::MISSED:    s.missed_deadlines++; break;
            case TaskStatus::DELETED:   s.cancelled_deleted++; break;
            case TaskStatus::PENDING:   s.left_pending++; break;
            default: break;
        }
    }

    s.avg_waiting_time = calculate_waiting_time();
    s.avg_turnaround_time = calculate_turnaround_time();
    s.cpu_utilization = calculate_cpu_utilization();
    s.throughput = (total_time > 0)
        ? static_cast<double>(executed_tasks.size()) / total_time
        : 0.0;

    return s;
}
