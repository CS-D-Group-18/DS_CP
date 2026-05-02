from enum import Enum

class TaskStatus(Enum):
    """
    Enum representing the various states a task can be in during its lifecycle.
    """
    PENDING = "PENDING"     # Task is waiting to be executed
    RUNNING = "RUNNING"     # Task is currently being executed
    COMPLETED = "COMPLETED" # Task has finished execution
    MISSED = "MISSED"       # Task failed to complete before its deadline
    DELETED = "DELETED"     # Task was cancelled (lazy deletion)


class Task:
    """
    Represents a single job or process to be scheduled by the system.
    """
    
    def __init__(self, task_id, name, priority, exec_time, deadline, arrival_time):
        """
        Initializes a new Task with the provided parameters.
        
        Args:
            task_id (int/str): A unique identifier for the task.
            name (str): A human-readable name or description of the task.
            priority (int): The priority level (lower number = higher priority).
            exec_time (int): Time units required to fully execute the task.
            deadline (int): The absolute time unit by which the task must complete.
            arrival_time (int): The time unit at which the task enters the system.
        """
        self.task_id = task_id
        self.name = name
        
        # Scheduling parameters
        self.priority = priority
        self.exec_time = exec_time
        self.deadline = deadline
        self.arrival_time = arrival_time
        
        # Metrics calculated during simulation
        self.waiting_time = 0
        self.turnaround_time = 0
        self.completion_time = 0
        
        # State tracking
        self.status = TaskStatus.PENDING

    def __str__(self):
        """
        Returns a formatted string representation of the Task for easy debugging and logging.
        """
        return (f"Task(id={self.task_id}, name='{self.name}', "
                f"priority={self.priority}, exec_time={self.exec_time}, "
                f"deadline={self.deadline}, arrival={self.arrival_time}, "
                f"status={self.status.value})")

    def __repr__(self):
        """
        Returns an unambiguous string representation of the object.
        """
        return self.__str__()
