import sys
from cli import SchedulerCLI

def main():
    """
    Entry point for the Task Scheduling System.
    This function initializes the application and starts the Command Line Interface (CLI).
    """
    print("Initializing Task Scheduling System modules...")
    
    try:
        # Create an instance of the SchedulerCLI class.
        # This initializes the simulation engine and required modules under the hood.
        app = SchedulerCLI()
        
        # Start the main loop of the CLI, allowing user interaction
        app.run()
        
    except KeyboardInterrupt:
        # Graceful exit when the user presses Ctrl+C
        print("\n[Notice] Keyboard interrupt received.")
        print("Simulation aborted by user. Shutting down gracefully. Goodbye!")
        sys.exit(0)
        
    except Exception as e:
        # Catch-all for any unexpected errors during runtime
        print(f"\n[Error] An unexpected error occurred: {e}")
        print("The program will now terminate.")
        sys.exit(1)

if __name__ == "__main__":
    # This block ensures that main() is called only when this script is executed directly
    # (e.g., 'python main.py'), and not if it's imported as a module in another file.
    main()
