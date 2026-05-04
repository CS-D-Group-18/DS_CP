#include "task.h"

std::string taskStatusToString(TaskStatus status) {
    switch (status) {
        case TaskStatus::PENDING:   return "PENDING";
        case TaskStatus::RUNNING:   return "RUNNING";
        case TaskStatus::COMPLETED: return "COMPLETED";
        case TaskStatus::MISSED:    return "MISSED";
        case TaskStatus::DELETED:   return "DELETED";
    }
    return "UNKNOWN";
}

TaskStatus taskStatusFromString(const std::string& s) {
    if (s == "PENDING")   return TaskStatus::PENDING;
    if (s == "RUNNING")   return TaskStatus::RUNNING;
    if (s == "COMPLETED") return TaskStatus::COMPLETED;
    if (s == "MISSED")    return TaskStatus::MISSED;
    if (s == "DELETED")   return TaskStatus::DELETED;
    throw std::invalid_argument("Unknown TaskStatus: " + s);
}

Task::Task(const std::string& task_id,
           const std::string& name,
           int priority,
           int exec_time,
           int deadline,
           int arrival_time)
    : task_id(task_id)
    , name(name)
    , priority(priority)
    , exec_time(exec_time)
    , deadline(deadline)
    , arrival_time(arrival_time)
    , waiting_time(0)
    , turnaround_time(0)
    , completion_time(0)
    , status(TaskStatus::PENDING)
{}
