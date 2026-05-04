#pragma once

#include <vector>
#include <unordered_map>
#include <functional>
#include <memory>
#include "task.h"

class CustomHeap {
public:
    using KeyExtractor = std::function<int(const Task&)>;

    CustomHeap(KeyExtractor key_extractor, bool is_min_heap = true);

    void insert(std::shared_ptr<Task> task);
    std::shared_ptr<Task> extract();
    std::shared_ptr<Task> peek();
    int size() const;
    bool is_empty() const;
    void heapifyUp(int index);
    void heapifyDown(int index);
    void updateKey(const std::string& task_id);
    void remove(const std::string& task_id);

    std::vector<std::shared_ptr<Task>>& getHeap();

private:
    bool compare(const std::shared_ptr<Task>& t1, const std::shared_ptr<Task>& t2) const;
    void swapNodes(int i, int j);

    std::vector<std::shared_ptr<Task>> heap_;
    std::unordered_map<std::string, int> task_map_;
    KeyExtractor key_extractor_;
    bool is_min_heap_;
};
