from task import TaskStatus

class CustomHeap:
    """
    A custom Heap implementation from scratch.
    Supports both Min-Heap and Max-Heap behavior dynamically using a comparator.
    Maintains a HashMap (dictionary) for O(1) lookup of task indices.
    """

    def __init__(self, key_extractor, is_min_heap=True):
        """
        Initializes the custom heap.
        
        Args:
            key_extractor (callable): A function that takes a Task and returns the value to compare.
                                      e.g., lambda task: task.priority
            is_min_heap (bool): If True, functions as a Min-Heap. If False, Max-Heap.
        """
        self.heap = []          # Dynamic array to store the tasks
        self.task_map = {}      # HashMap: taskId -> index in self.heap
        self.key_extractor = key_extractor
        self.is_min_heap = is_min_heap

    def _compare(self, task1, task2):
        """
        Internal comparison function based on heap type and key_extractor.
        Returns True if task1 should be placed HIGHER (closer to root) than task2.
        """
        val1 = self.key_extractor(task1)
        val2 = self.key_extractor(task2)
        
        if self.is_min_heap:
            return val1 < val2
        else:
            return val1 > val2

    def _swap(self, i, j):
        """
        Swaps two elements in the heap array and updates their indices in the hashmap.
        """
        # Swap elements in the array
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]
        
        # Update the HashMap to reflect the new indices
        task_i_id = self.heap[i].task_id
        task_j_id = self.heap[j].task_id
        
        self.task_map[task_i_id] = i
        self.task_map[task_j_id] = j

    def size(self):
        """Returns the current number of tasks in the heap."""
        return len(self.heap)

    def is_empty(self):
        """Returns True if the heap is empty."""
        return self.size() == 0

    def insert(self, task):
        """
        Inserts a new task into the heap.
        """
        # Add to the end of the array
        self.heap.append(task)
        index = self.size() - 1
        
        # Store in hashmap
        self.task_map[task.task_id] = index
        
        # Restore heap property
        self.heapifyUp(index)

    def extract(self):
        """
        Removes and returns the root of the heap (min or max depending on setup).
        Handles lazy deletion: if the extracted task is marked DELETED, it skips it.
        """
        while not self.is_empty():
            # Get the root
            root_task = self.heap[0]
            
            # Replace root with the last element
            last_task = self.heap.pop()
            
            # Remove root from hashmap
            if root_task.task_id in self.task_map:
                del self.task_map[root_task.task_id]
                
            if not self.is_empty():
                self.heap[0] = last_task
                self.task_map[last_task.task_id] = 0
                # Restore heap property
                self.heapifyDown(0)
            
            # Lazy Deletion Check: if the extracted task was cancelled, 
            # we don't return it to the caller, just extract the next one.
            if root_task.status != TaskStatus.DELETED:
                return root_task
                
        return None # Heap is empty

    def peek(self):
        """
        Returns the root task without removing it. Skips over deleted tasks.
        """
        # Clean up any deleted tasks at the root lazily
        while not self.is_empty() and self.heap[0].status == TaskStatus.DELETED:
            self.extract()
            
        if self.is_empty():
            return None
        return self.heap[0]

    def heapifyUp(self, index):
        """
        Bubbles up the element at 'index' until the heap property is restored.
        """
        parent_index = (index - 1) // 2
        
        # While not at root and current node is "smaller/larger" than parent
        while index > 0 and self._compare(self.heap[index], self.heap[parent_index]):
            self._swap(index, parent_index)
            index = parent_index
            parent_index = (index - 1) // 2

    def heapifyDown(self, index):
        """
        Bubbles down the element at 'index' until the heap property is restored.
        """
        size = self.size()
        
        while True:
            left_child = 2 * index + 1
            right_child = 2 * index + 2
            
            # Assume current index is the most extreme (smallest for min-heap, largest for max-heap)
            extreme_index = index
            
            # Check left child
            if left_child < size and self._compare(self.heap[left_child], self.heap[extreme_index]):
                extreme_index = left_child
                
            # Check right child
            if right_child < size and self._compare(self.heap[right_child], self.heap[extreme_index]):
                extreme_index = right_child
                
            # If the current node is still the extreme, heap property is satisfied
            if extreme_index == index:
                break
                
            # Otherwise, swap with the extreme child and continue
            self._swap(index, extreme_index)
            index = extreme_index

    def updateKey(self, task_id):
        """
        Called when a task's priority/execution time/deadline is modified externally.
        Uses the HashMap for O(1) lookup to find the task's index, then restores heap property.
        """
        if task_id not in self.task_map:
            return # Task might have been extracted or doesn't exist
            
        index = self.task_map[task_id]
        
        # We don't know if the key increased or decreased, so we try both.
        # Only one will actually do work.
        parent_index = (index - 1) // 2
        if index > 0 and self._compare(self.heap[index], self.heap[parent_index]):
            self.heapifyUp(index)
        else:
            self.heapifyDown(index)

    def remove(self, task_id):
        """
        Lazy deletion: Instead of an expensive O(N) removal, we just find the task
        using our O(1) hashmap and mark its status as DELETED. 
        It will be naturally discarded during extract() or peek().
        """
        if task_id in self.task_map:
            index = self.task_map[task_id]
            self.heap[index].status = TaskStatus.DELETED
            # Note: We do NOT remove it from self.heap array yet.
            # We can optionally remove it from task_map so it can't be updated anymore.
            del self.task_map[task_id]
