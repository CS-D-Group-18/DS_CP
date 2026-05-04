#pragma once

#include <string>
#include <stdexcept>

enum class TaskStatus {
    PENDING,
    RUNNING,
    COMPLETED,
    MISSED,
    DELETED
};

std::string taskStatusToString(TaskStatus status);
TaskStatus taskStatusFromString(const std::string& s);

class Task {
public:
    std::string task_id;
    std::string name;
    int priority;
    int exec_time;
    int deadline;
    int arrival_time;
    int waiting_time;
    int turnaround_time;
    int completion_time;
    TaskStatus status;

    Task(const std::string& task_id,
         const std::string& name,
         int priority,
         int exec_time,
         int deadline,
         int arrival_time);
};
