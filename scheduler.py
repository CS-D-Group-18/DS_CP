from task import TaskStatus, Task
from heap import CustomHeap
from dag_manager import DAGManager

class SimulationEngine:
    """
    The core scheduler that simulates an Operating System's task management.
    Handles scheduling algorithms, task execution, time progression, and task aging.
    """

    def __init__(self):
        self.tasks = {}                  # Maps task_id -> Task object
        self.dag_manager = DAGManager()  # Manages dependencies
        self.heap = None                 # Will be initialized in run()
        
        self.current_time = 0
        self.last_aging_time = 0
        self.AGING_INTERVAL = 5          # Time units before priority is boosted
        
        self.completed_tasks = []
        self.execution_log = []          # Stores chronological events

    def add_task(self, task, dependencies=None):
        """
        Registers a task in the system and sets up its dependencies.
        
        Args:
            task (Task): The task object to add.
            dependencies (list): List of task_ids that must complete before this task.
        """
        self.tasks[task.task_id] = task
        
        # Add to DAG manager
        self.dag_manager._add_task_if_missing(task.task_id)
        
        if dependencies:
            for dep_id in dependencies:
                # Add dependency: dep_id must run before task.task_id
                self.dag_manager.add_dependency(dep_id, task.task_id)

    def load_tasks(self, task_list):
        """
        Helper to load multiple tasks at once.
        task_list should be a list of tuples: (Task, [dependencies])
        """
        for task, deps in task_list:
            self.add_task(task, deps)

    def log(self, message):
        """Records an event in the execution log."""
        self.execution_log.append(message)
        # Uncomment the line below if you want real-time console output during simulation:
        # print(message)

    def apply_aging(self, intervals_passed):
        """
        Prevents starvation by boosting the priority of all tasks currently waiting in the heap.
        
        Args:
            intervals_passed (int): How many aging intervals have elapsed since last check.
        """
        if self.heap.is_empty():
            return
            
        for task in self.heap.heap:
            if task.status == TaskStatus.PENDING:
                old_priority = task.priority
                # Decrease priority value (which means HIGHER priority in our min-heap)
                # Ensure priority doesn't drop below 0
                task.priority = max(0, task.priority - intervals_passed)
                
                if old_priority != task.priority:
                    self.log(f"Time {self.current_time}: Task {task.task_id} aged. Priority boosted from {old_priority} to {task.priority}")
                    # Re-heapify this specific task to restore heap property
                    self.heap.updateKey(task.task_id)

    def execute_task(self, task):
        """
        Simulates the execution of a single task.
        Updates metrics, advances the clock, and resolves dependencies.
        """
        # Calculate how long it was sitting in the ready queue
        task.waiting_time = self.current_time - task.arrival_time
        
        task.status = TaskStatus.RUNNING
        self.log(f"Time {self.current_time}: Running Task {task.task_id} ('{task.name}', priority: {task.priority}, execTime: {task.exec_time})")
        
        # Simulate time passing as the task executes
        self.current_time += task.exec_time
        
        # Update metrics
        task.completion_time = self.current_time
        task.turnaround_time = task.completion_time - task.arrival_time
        
        # Check deadline (if EDF mode or just generally tracked)
        if task.deadline and self.current_time > task.deadline:
            task.status = TaskStatus.MISSED
            self.log(f"Time {self.current_time}: Task {task.task_id} COMPLETED but MISSED deadline! (Deadline: {task.deadline})")
        else:
            task.status = TaskStatus.COMPLETED
            self.log(f"Time {self.current_time}: Task {task.task_id} COMPLETED successfully.")
            
        self.completed_tasks.append(task)
        
        # Unlock dependent tasks
        newly_unlocked = self.dag_manager.resolve_completed_task(task.task_id)
        if newly_unlocked:
            self.log(f"Time {self.current_time}: Task {task.task_id} completion unlocked tasks: {newly_unlocked}")

    def run(self, algorithm="Priority"):
        """
        The main simulation loop.
        
        Args:
            algorithm (str): 'Priority', 'SJF', or 'EDF'
        """
        self.log(f"--- Starting Simulation ({algorithm} Scheduling) ---")
        
        # 1. Initialize the correct heap behavior based on the chosen algorithm
        if algorithm == "Priority":
            self.heap = CustomHeap(key_extractor=lambda t: t.priority, is_min_heap=True)
        elif algorithm == "SJF":
            self.heap = CustomHeap(key_extractor=lambda t: t.exec_time, is_min_heap=True)
        elif algorithm == "EDF":
            self.heap = CustomHeap(key_extractor=lambda t: t.deadline, is_min_heap=True)
        else:
            raise ValueError("Unknown scheduling algorithm.")

        # Track which tasks haven't been added to the heap yet
        unstarted_task_ids = set(self.tasks.keys())
        
        # Reset time for fresh run
        self.current_time = 0
        self.last_aging_time = 0
        
        while unstarted_task_ids or not self.heap.is_empty():
            
            # 1. Check for new arrivals that are also unlocked (in-degree == 0)
            ready_to_load = []
            for t_id in list(unstarted_task_ids):
                task = self.tasks[t_id]
                # If task has arrived AND has no pending dependencies
                if task.arrival_time <= self.current_time and self.dag_manager.in_degree.get(t_id, 0) == 0:
                    # Skip deleted tasks
                    if task.status == TaskStatus.DELETED:
                        unstarted_task_ids.remove(t_id)
                        continue
                        
                    ready_to_load.append(task)
                    unstarted_task_ids.remove(t_id)
            
            # Load them into the heap
            for task in ready_to_load:
                self.heap.insert(task)
                self.log(f"Time {self.current_time}: Task {task.task_id} arrived and added to ready queue.")

            # 2. If heap is empty but we still have unstarted tasks, time must advance
            if self.heap.is_empty() and unstarted_task_ids:
                # Fast-forward time to the next closest arrival
                next_arrival = min([self.tasks[tid].arrival_time for tid in unstarted_task_ids])
                # We also need to check if there are tasks that arrived but are locked by dependencies.
                # If ALL unstarted tasks have arrived but are locked, we have a deadlock!
                if next_arrival <= self.current_time:
                    raise RuntimeError("Deadlock detected! Tasks are waiting on dependencies that will never resolve.")
                
                self.current_time = next_arrival
                continue
                
            # 3. Apply Task Aging (only relevant for Priority scheduling usually, but we'll run it)
            if algorithm == "Priority":
                intervals_passed = (self.current_time - self.last_aging_time) // self.AGING_INTERVAL
                if intervals_passed > 0:
                    self.apply_aging(intervals_passed)
                    self.last_aging_time += intervals_passed * self.AGING_INTERVAL

            # 4. Extract and execute the next task
            current_task = self.heap.extract()
            if current_task:
                self.execute_task(current_task)

        self.log(f"--- Simulation Complete at Time {self.current_time} ---")

    def display_execution(self):
        """
        Prints the chronological execution log.
        """
        print("\n=== EXECUTION LOG ===")
        for entry in self.execution_log:
            print(entry)
