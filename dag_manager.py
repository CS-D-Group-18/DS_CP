class DAGManager:
    """
    Manages task dependencies using a Directed Acyclic Graph (DAG).
    Uses an adjacency list and in-degree mapping to resolve which tasks
    are ready to execute based on their dependencies.
    """

    def __init__(self):
        # Maps task_id to a list of task_ids that depend on it
        # Example: {A: [B, C]} means A must run before B and C.
        self.adj_list = {}
        
        # Maps task_id to the number of dependencies it is waiting on
        # Example: {B: 1, C: 1, A: 0}
        self.in_degree = {}
        
        # Keeps track of all unique tasks in the dependency graph
        self.all_tasks = set()

    def _add_task_if_missing(self, task_id):
        """
        Helper method to initialize empty graph structures for a new task.
        """
        if task_id not in self.all_tasks or task_id not in self.adj_list:
            self.adj_list[task_id] = []
            self.in_degree[task_id] = 0
            self.all_tasks.add(task_id)

    def add_dependency(self, from_id, to_id):
        """
        Adds a dependency stating that task 'from_id' must complete BEFORE task 'to_id'.
        """
        self._add_task_if_missing(from_id)
        self._add_task_if_missing(to_id)

        # Add directed edge: from_id -> to_id
        if to_id not in self.adj_list[from_id]:
            self.adj_list[from_id].append(to_id)
            self.in_degree[to_id] += 1
            
        # Check if this new dependency creates a cycle
        if self.detect_cycle():
            # Rollback the change to maintain a valid DAG
            self.remove_dependency(from_id, to_id)
            raise ValueError(f"Adding dependency {from_id} -> {to_id} creates a cycle! Dependency rejected.")

    def remove_dependency(self, from_id, to_id):
        """
        Removes a specific dependency from_id -> to_id.
        """
        if from_id in self.adj_list and to_id in self.adj_list[from_id]:
            self.adj_list[from_id].remove(to_id)
            self.in_degree[to_id] -= 1

    def reset(self):
        """Resets the engine state and the underlying DAG manager."""
        self.adj_list.clear()
        self.in_degree.clear()
        self.all_tasks.clear()

    def get_ready_tasks(self):
        """
        Returns a list of all task IDs that currently have 0 dependencies (in-degree == 0).
        These tasks are ready to be scheduled.
        """
        ready = []
        for task_id, count in self.in_degree.items():
            if count == 0:
                ready.append(task_id)
        return ready

    def resolve_completed_task(self, completed_task_id):
        """
        Called when a task finishes execution. 
        It "unlocks" dependent tasks by decrementing their in-degree.
        
        Returns:
            list: A list of task_ids that just became ready (in-degree hit 0).
        """
        newly_ready_tasks = []
        
        # If the task isn't in the DAG, no dependencies to resolve
        if completed_task_id not in self.adj_list:
            return newly_ready_tasks
            
        # For every task that was waiting on this completed task
        for dependent_id in self.adj_list[completed_task_id]:
            self.in_degree[dependent_id] -= 1
            
            # If the dependent task is no longer waiting on anything, it's ready!
            if self.in_degree[dependent_id] == 0:
                newly_ready_tasks.append(dependent_id)
                
        return newly_ready_tasks

    def detect_cycle(self):
        """
        Uses Kahn's Algorithm (BFS topological sort) to detect cycles.
        
        Returns:
            bool: True if a cycle exists, False otherwise.
        """
        # Create a temporary copy of in-degrees to mutate during the check
        temp_in_degree = self.in_degree.copy()
        
        # Find all nodes with 0 in-degree to start the queue
        queue = [node for node in self.all_tasks if temp_in_degree[node] == 0]
        
        processed_count = 0
        
        while queue:
            curr_node = queue.pop(0)
            processed_count += 1
            
            # Simulate removing curr_node from the graph
            for neighbor in self.adj_list.get(curr_node, []):
                temp_in_degree[neighbor] -= 1
                if temp_in_degree[neighbor] == 0:
                    queue.append(neighbor)
                    
        # If we successfully processed all nodes, there is no cycle.
        # If processed_count < len(all_tasks), a cycle prevented some nodes from reaching 0 in-degree.
        return processed_count != len(self.all_tasks)
