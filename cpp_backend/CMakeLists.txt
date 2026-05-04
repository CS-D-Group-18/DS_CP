cmake_minimum_required(VERSION 3.20)
project(scheduler_server LANGUAGES CXX)

# Suppress FetchContent_Populate deprecation warnings on CMake 3.30+
if(POLICY CMP0169)
    cmake_policy(SET CMP0169 OLD)
endif()

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

include(FetchContent)

# ── nlohmann/json (CMake-native, header-only) ──────────────────────────────
FetchContent_Declare(json
    GIT_REPOSITORY https://github.com/nlohmann/json.git
    GIT_TAG        v3.11.3
    GIT_SHALLOW    TRUE
)
FetchContent_MakeAvailable(json)

# ── Standalone Asio (header-only, needed by Crow) ─────────────────────────
FetchContent_Declare(asio
    GIT_REPOSITORY https://github.com/chriskohlhoff/asio.git
    GIT_TAG        asio-1-28-0
    GIT_SHALLOW    TRUE
)
FetchContent_Populate(asio)

# ── CrowCpp (header-only — we skip its CMake to avoid Boost requirement) ──
FetchContent_Declare(crow
    GIT_REPOSITORY https://github.com/CrowCpp/Crow.git
    GIT_TAG        v1.2.0
    GIT_SHALLOW    TRUE
)
FetchContent_Populate(crow)

# ── Build target ───────────────────────────────────────────────────────────
add_executable(scheduler_server
    src/task.cpp
    src/dag_manager.cpp
    src/heap.cpp
    src/scheduler.cpp
    src/report.cpp
    src/main.cpp
)

target_include_directories(scheduler_server PRIVATE
    ${CMAKE_SOURCE_DIR}/include
    ${crow_SOURCE_DIR}/include
    ${asio_SOURCE_DIR}/asio/include
)

target_link_libraries(scheduler_server PRIVATE
    nlohmann_json::nlohmann_json
    pthread
)

target_compile_definitions(scheduler_server PRIVATE
    ASIO_STANDALONE
    CROW_DISABLE_STATIC_DIR
)

target_compile_options(scheduler_server PRIVATE -O2 -Wall -Wextra)
