import sys
# from cli import SchedulerCLI  # Keep for reference or fallback
from gui.app import App

def main():
    """
    Entry point for the Task Scheduling System GUI.
    """
    print("Initializing Task Scheduling System GUI...")
    
    try:
        # Create and run the CustomTkinter application
        app = App()
        app.mainloop()
        
    except KeyboardInterrupt:
        # Graceful exit when the user presses Ctrl+C
        print("\n[Notice] Keyboard interrupt received.")
        sys.exit(0)
        
    except Exception as e:
        # Catch-all for any unexpected errors during runtime
        print(f"\n[Error] An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
