from task import Task
from scheduler import SimulationEngine
from report import ReportGenerator

class SchedulerCLI:
    """
    Provides a Command Line Interface (CLI) for users to interact with the Task Scheduling System.
    """

    def __init__(self):
        # Create a fresh simulation engine instance
        self.engine = SimulationEngine()
        # Track whether a simulation has been run (so we know if reports can be generated)
        self.has_run = False

    def display_menu(self):
        """Prints the main menu options."""
        print("\n" + "="*40)
        print("    TASK SCHEDULING SYSTEM MENU")
        print("="*40)
        print("1. Add Task")
        print("2. Add Dependency (A must run before B)")
        print("3. View All Tasks")
        print("4. Run Scheduler")
        print("5. Display Execution Log")
        print("6. Generate Performance Report")
        print("7. Load Hardcoded Sample Dataset")
        print("8. Exit")
        print("="*40)

    def get_int_input(self, prompt, allow_negative=False):
        """Helper to continuously ask for input until a valid integer is provided."""
        while True:
            try:
                val = int(input(prompt))
                if not allow_negative and val < 0:
                    print("Please enter a positive number or zero.")
                    continue
                return val
            except ValueError:
                print("Invalid input. Please enter a valid integer.")

    def add_task_menu(self):
        """Handles adding a single task via user input."""
        print("\n--- Add New Task ---")
        task_id = input("Enter Task ID (e.g., T1, 100): ").strip()
        
        # Check if ID already exists
        if task_id in self.engine.tasks:
            print("Error: A task with this ID already exists.")
            return

        name = input("Enter Task Name: ").strip()
        
        # Get integer metrics safely
        priority = self.get_int_input("Enter Priority (lower number = higher priority): ")
        exec_time = self.get_int_input("Enter Execution Time: ")
        deadline = self.get_int_input("Enter Deadline (0 if none): ")
        arrival_time = self.get_int_input("Enter Arrival Time: ")
        
        # Create and add the task
        new_task = Task(task_id, name, priority, exec_time, deadline, arrival_time)
        self.engine.add_task(new_task)
        print(f"Task '{name}' (ID: {task_id}) added successfully!")

    def add_dependency_menu(self):
        """Handles adding a dependency between two existing tasks."""
        print("\n--- Add Dependency ---")
        if not self.engine.tasks:
            print("No tasks available. Please add tasks first.")
            return
            
        print("Available Task IDs:", ", ".join(self.engine.tasks.keys()))
        from_id = input("Enter the ID of the task that MUST RUN FIRST: ").strip()
        to_id = input("Enter the ID of the task that MUST WAIT: ").strip()
        
        if from_id not in self.engine.tasks or to_id not in self.engine.tasks:
            print("Error: One or both Task IDs do not exist.")
            return
            
        try:
            self.engine.dag_manager.add_dependency(from_id, to_id)
            print(f"Dependency added: {from_id} must run before {to_id}.")
        except ValueError as e:
            # This catches the cycle detection error raised by DAGManager
            print(f"Error: {e}")

    def view_tasks_menu(self):
        """Displays all currently loaded tasks."""
        print("\n--- Current Tasks ---")
        if not self.engine.tasks:
            print("No tasks in the system.")
            return
            
        for t_id, task in self.engine.tasks.items():
            print(task)
            
        print("\n--- Current Dependencies ---")
        if not self.engine.dag_manager.adj_list:
            print("No dependencies defined.")
        else:
            for from_id, to_ids in self.engine.dag_manager.adj_list.items():
                if to_ids:
                    print(f"{from_id} must run before: {', '.join(to_ids)}")

    def run_scheduler_menu(self):
        """Lets the user pick an algorithm and runs the simulation."""
        if not self.engine.tasks:
            print("No tasks to schedule. Please add tasks first.")
            return
            
        print("\n--- Select Scheduling Algorithm ---")
        print("1. Priority Scheduling")
        print("2. Shortest Job First (SJF)")
        print("3. Earliest Deadline First (EDF)")
        
        choice = input("Enter choice (1-3): ").strip()
        
        algo_map = {"1": "Priority", "2": "SJF", "3": "EDF"}
        if choice not in algo_map:
            print("Invalid choice. Returning to main menu.")
            return
            
        algorithm = algo_map[choice]
        print(f"\nStarting simulation using {algorithm} algorithm...")
        
        try:
            self.engine.run(algorithm)
            self.has_run = True
            print("Simulation completed successfully! Use options 5 and 6 to view results.")
        except Exception as e:
            print(f"Simulation failed: {e}")

    def display_log_menu(self):
        """Shows the chronological event log from the simulation."""
        if not self.has_run:
            print("You must run the scheduler first (Option 4).")
            return
        self.engine.display_execution()

    def generate_report_menu(self):
        """Generates and displays the final performance metrics."""
        if not self.has_run:
            print("You must run the scheduler first (Option 4).")
            return
            
        report = ReportGenerator(self.engine)
        report.display_report()

    def load_hardcoded_data(self):
        """Loads a pre-defined complex dataset for easy testing."""
        print("\nLoading sample dataset...")
        
        # Clear existing
        self.engine = SimulationEngine()
        self.has_run = False
        
        # task_id, name, priority, exec_time, deadline, arrival_time
        tasks = [
            Task("T1", "OS Boot", 1, 10, 15, 0),
            Task("T2", "Init GUI", 3, 5, 25, 2),
            Task("T3", "Load Network", 2, 8, 20, 5),
            Task("T4", "Check Updates", 4, 3, 30, 6),
            Task("T5", "Sync Files", 5, 12, 50, 10)
        ]
        
        for t in tasks:
            self.engine.add_task(t)
            
        # Add dependencies: T1 -> T2, T1 -> T3, T3 -> T4
        self.engine.dag_manager.add_dependency("T1", "T2")
        self.engine.dag_manager.add_dependency("T1", "T3")
        self.engine.dag_manager.add_dependency("T3", "T4")
        
        print("Loaded 5 tasks and 3 dependencies successfully.")

    def run(self):
        """Main loop that keeps the CLI running."""
        print("Welcome to the Task Scheduling System!")
        
        while True:
            self.display_menu()
            choice = input("Enter your choice (1-8): ").strip()
            
            if choice == '1':
                self.add_task_menu()
            elif choice == '2':
                self.add_dependency_menu()
            elif choice == '3':
                self.view_tasks_menu()
            elif choice == '4':
                self.run_scheduler_menu()
            elif choice == '5':
                self.display_log_menu()
            elif choice == '6':
                self.generate_report_menu()
            elif choice == '7':
                self.load_hardcoded_data()
            elif choice == '8':
                print("Exiting system. Goodbye!")
                break
            else:
                print("Invalid choice. Please enter a number between 1 and 8.")

if __name__ == "__main__":
    # If the file is run directly, start the CLI
    cli = SchedulerCLI()
    cli.run()
