# Task Scheduling System — C++17 Backend

A high-performance C++17 rewrite of the Python/Flask task scheduling backend.
Drop-in replacement: the Vite/React frontend requires **zero changes**.

## Architecture

```
include/          ← Header files
  task.h          ← TaskStatus enum + Task class
  dag_manager.h   ← DAG dependency manager (Kahn's cycle detection)
  heap.h          ← Custom min/max heap with O(1) hashmap lookup
  scheduler.h     ← SimulationEngine (Priority, SJF, EDF algorithms)
  report.h        ← ReportGenerator (performance metrics)

src/              ← Implementation files
  task.cpp
  dag_manager.cpp
  heap.cpp
  scheduler.cpp
  report.cpp
  main.cpp        ← Crow REST API server (all 12 endpoints)

CMakeLists.txt    ← Build system (auto-fetches Crow, Asio, nlohmann/json)
```

## Prerequisites

- **CMake** ≥ 3.20
- **GCC** ≥ 9 or **Clang** ≥ 10 (C++17 support)
- **Git** (for FetchContent downloads)
- Internet connection (first build downloads dependencies)

## Build Instructions

```bash
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
cmake --build .
```

## Run

```bash
./scheduler_server
```

The server starts on **http://localhost:5001**, exposing these endpoints:

| Method   | Endpoint              | Description                    |
|----------|-----------------------|--------------------------------|
| `GET`    | `/api/dashboard`      | Aggregated stats + recent logs |
| `GET`    | `/api/tasks`          | List all tasks                 |
| `POST`   | `/api/tasks`          | Create a new task              |
| `DELETE` | `/api/tasks/<id>`     | Soft-delete a task             |
| `GET`    | `/api/dependencies`   | Dependency graph (nodes+edges) |
| `POST`   | `/api/dependencies`   | Add a dependency edge          |
| `POST`   | `/api/scheduler/run`  | Run simulation (algo param)    |
| `POST`   | `/api/scheduler/reset`| Reset engine state             |
| `GET`    | `/api/logs`           | Full execution log             |
| `GET`    | `/api/reports`        | Gantt, utilization, summary    |
| `POST`   | `/api/demo`           | Load & run demo dataset        |

## Connecting to the Frontend

Point the Vite frontend to `http://localhost:5001` (same port as the old Flask server). No frontend changes required.

## Scheduling Algorithms

- **Priority** — Min-heap on `priority` field (with starvation-preventing aging)
- **SJF** — Min-heap on `exec_time` (Shortest Job First)
- **EDF** — Min-heap on `deadline` (Earliest Deadline First)
