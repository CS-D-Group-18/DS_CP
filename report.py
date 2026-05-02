from task import TaskStatus

class ReportGenerator:
    """
    Generates performance metrics and summaries based on the final state of the SimulationEngine.
    """

    def __init__(self, simulation_engine):
        """
        Initializes the ReportGenerator.
        
        Args:
            simulation_engine (SimulationEngine): The engine that ran the simulation.
        """
        self.engine = simulation_engine
        # all_tasks contains every task originally added to the system
        self.all_tasks = list(self.engine.tasks.values())
        # completed_tasks contains only tasks that went through execution (COMPLETED or MISSED)
        self.executed_tasks = self.engine.completed_tasks
        self.total_time = self.engine.current_time

    def calculate_waiting_time(self):
        """Calculates the average waiting time for all executed tasks."""
        if not self.executed_tasks:
            return 0.0
            
        total_wait = sum(t.waiting_time for t in self.executed_tasks)
        return total_wait / len(self.executed_tasks)

    def calculate_turnaround_time(self):
        """Calculates the average turnaround time for all executed tasks."""
        if not self.executed_tasks:
            return 0.0
            
        total_ta = sum(t.turnaround_time for t in self.executed_tasks)
        return total_ta / len(self.executed_tasks)

    def calculate_cpu_utilization(self):
        """
        Calculates CPU utilization as a percentage.
        Formula: (Total time spent executing tasks / Total simulation time) * 100
        """
        if self.total_time == 0:
            return 0.0
            
        active_time = sum(t.exec_time for t in self.executed_tasks)
        return (active_time / self.total_time) * 100.0

    def generate_summary(self):
        """
        Compiles all statistics into a dictionary summary.
        """
        completed = [t for t in self.all_tasks if t.status == TaskStatus.COMPLETED]
        missed = [t for t in self.all_tasks if t.status == TaskStatus.MISSED]
        deleted = [t for t in self.all_tasks if t.status == TaskStatus.DELETED]
        pending = [t for t in self.all_tasks if t.status == TaskStatus.PENDING]
        
        # Throughput: Tasks completed per unit of time
        throughput = len(self.executed_tasks) / self.total_time if self.total_time > 0 else 0
        
        return {
            "Total Tasks Submitted": len(self.all_tasks),
            "Tasks Executed": len(self.executed_tasks),
            "Completed Successfully": len(completed),
            "Missed Deadlines": len(missed),
            "Cancelled/Deleted": len(deleted),
            "Left Pending/Stuck": len(pending),
            "Average Waiting Time": self.calculate_waiting_time(),
            "Average Turnaround Time": self.calculate_turnaround_time(),
            "CPU Utilization (%)": self.calculate_cpu_utilization(),
            "Throughput (tasks/unit time)": throughput,
            "Total Time Taken": self.total_time
        }

    def display_report(self):
        """
        Prints a neatly formatted performance report to the console.
        """
        summary = self.generate_summary()
        
        print("\n" + "="*55)
        print("              SCHEDULING PERFORMANCE REPORT")
        print("="*55)
        
        # Print summary statistics
        for key, value in summary.items():
            if isinstance(value, float):
                print(f"{key:<30}: {value:.2f}")
            else:
                print(f"{key:<30}: {value}")
                
        print("\n--- TASK COMPLETION DETAILS ---")
        # Print table header
        print(f"{'TaskID':<8} | {'Priority':<8} | {'WaitTime':<8} | {'Turnaround':<10} | {'Status':<10}")
        print("-" * 55)
        
        # Print each task's metrics
        # Sort by task ID to make the list easier to read
        sorted_tasks = sorted(self.all_tasks, key=lambda t: str(t.task_id))
        for t in sorted_tasks:
            print(f"{t.task_id:<8} | {t.priority:<8} | {t.waiting_time:<8} | {t.turnaround_time:<10} | {t.status.value:<10}")
        
        print("="*55)

    def export_report(self, filename="report.txt"):
        """
        Exports the performance report to a text file.
        """
        summary = self.generate_summary()
        
        try:
            with open(filename, 'w') as f:
                f.write("=== SCHEDULING PERFORMANCE REPORT ===\n")
                for key, value in summary.items():
                    if isinstance(value, float):
                        f.write(f"{key:<30}: {value:.2f}\n")
                    else:
                        f.write(f"{key:<30}: {value}\n")
                        
                f.write("\n--- TASK COMPLETION DETAILS ---\n")
                f.write(f"{'TaskID':<8} | {'Priority':<8} | {'WaitTime':<8} | {'Turnaround':<10} | {'Status':<10}\n")
                f.write("-" * 55 + "\n")
                
                sorted_tasks = sorted(self.all_tasks, key=lambda t: str(t.task_id))
                for t in sorted_tasks:
                    f.write(f"{t.task_id:<8} | {t.priority:<8} | {t.waiting_time:<8} | {t.turnaround_time:<10} | {t.status.value:<10}\n")
                    
            print(f"Report successfully exported to {filename}")
        except IOError as e:
            print(f"Failed to export report: {e}")
