#include "heap.h"

CustomHeap::CustomHeap(KeyExtractor key_extractor, bool is_min_heap)
    : key_extractor_(std::move(key_extractor))
    , is_min_heap_(is_min_heap)
{}

bool CustomHeap::compare(const std::shared_ptr<Task>& t1,
                         const std::shared_ptr<Task>& t2) const {
    int v1 = key_extractor_(*t1);
    int v2 = key_extractor_(*t2);
    return is_min_heap_ ? (v1 < v2) : (v1 > v2);
}

void CustomHeap::swapNodes(int i, int j) {
    std::swap(heap_[i], heap_[j]);
    task_map_[heap_[i]->task_id] = i;
    task_map_[heap_[j]->task_id] = j;
}

int CustomHeap::size() const {
    return static_cast<int>(heap_.size());
}

bool CustomHeap::is_empty() const {
    return heap_.empty();
}

void CustomHeap::insert(std::shared_ptr<Task> task) {
    heap_.push_back(task);
    int index = size() - 1;
    task_map_[task->task_id] = index;
    heapifyUp(index);
}

std::shared_ptr<Task> CustomHeap::extract() {
    while (!is_empty()) {
        auto root_task = heap_.front();
        auto last_task = heap_.back();
        heap_.pop_back();

        task_map_.erase(root_task->task_id);

        if (!is_empty()) {
            heap_[0] = last_task;
            task_map_[last_task->task_id] = 0;
            heapifyDown(0);
        }

        // Lazy deletion: skip DELETED tasks
        if (root_task->status != TaskStatus::DELETED) {
            return root_task;
        }
    }
    return nullptr;
}

std::shared_ptr<Task> CustomHeap::peek() {
    while (!is_empty() && heap_[0]->status == TaskStatus::DELETED) {
        extract();
    }
    if (is_empty()) return nullptr;
    return heap_[0];
}

void CustomHeap::heapifyUp(int index) {
    while (index > 0) {
        int parent = (index - 1) / 2;
        if (compare(heap_[index], heap_[parent])) {
            swapNodes(index, parent);
            index = parent;
        } else {
            break;
        }
    }
}

void CustomHeap::heapifyDown(int index) {
    int n = size();
    while (true) {
        int left = 2 * index + 1;
        int right = 2 * index + 2;
        int extreme = index;

        if (left < n && compare(heap_[left], heap_[extreme])) {
            extreme = left;
        }
        if (right < n && compare(heap_[right], heap_[extreme])) {
            extreme = right;
        }

        if (extreme == index) break;

        swapNodes(index, extreme);
        index = extreme;
    }
}

void CustomHeap::updateKey(const std::string& task_id) {
    auto it = task_map_.find(task_id);
    if (it == task_map_.end()) return;

    int index = it->second;
    int parent = (index - 1) / 2;
    if (index > 0 && compare(heap_[index], heap_[parent])) {
        heapifyUp(index);
    } else {
        heapifyDown(index);
    }
}

void CustomHeap::remove(const std::string& task_id) {
    auto it = task_map_.find(task_id);
    if (it != task_map_.end()) {
        int index = it->second;
        heap_[index]->status = TaskStatus::DELETED;
        task_map_.erase(it);
    }
}

std::vector<std::shared_ptr<Task>>& CustomHeap::getHeap() {
    return heap_;
}
