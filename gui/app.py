import customtkinter as ctk
from gui.components.sidebar import Sidebar
from scheduler import SimulationEngine

from gui.dashboard import DashboardPage
from gui.task_page import TaskPage
from gui.dependency_page import DependencyPage
from gui.scheduler_page import SchedulerPage
from gui.logs_page import LogsPage
from gui.report_page import ReportPage
from gui.settings_page import SettingsPage
# ...

ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window configuration
        self.title("Task Scheduling System")
        self.geometry("1100x700")
        
        # Backend initialization
        self.engine = SimulationEngine()
        self.has_run = False # Tracks if simulation has run
        
        # Configure grid layout (1x2)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Create sidebar frame
        self.sidebar_frame = Sidebar(self, nav_callback=self.show_page, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        
        # Create main content frame area
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Dictionary to hold the pages
        self.pages = {}
        
        self.init_pages()
        
        # Show default page
        self.sidebar_frame.on_nav_click("dashboard")

    def init_pages(self):
        """Initialize all pages and hide them."""
        # Dashboard
        self.pages["dashboard"] = DashboardPage(self.main_frame, self.engine, self.show_page)
        
        # Tasks
        self.pages["tasks"] = TaskPage(self.main_frame, self.engine, self.show_page)
        
        # Dependencies
        self.pages["dependencies"] = DependencyPage(self.main_frame, self.engine, self.show_page)
        
        # Scheduler
        self.pages["scheduler"] = SchedulerPage(self.main_frame, self.engine, self.show_page)
        
        # Logs
        self.pages["logs"] = LogsPage(self.main_frame, self.engine, self.show_page)
        
        # Reports
        self.pages["reports"] = ReportPage(self.main_frame, self.engine, self.show_page)
        
        # Settings
        self.pages["settings"] = SettingsPage(self.main_frame, self.engine, self.show_page)
        self.placeholder_page = ctk.CTkLabel(self.main_frame, text="Page content will load here", font=("Arial", 20))
        self.placeholder_page.grid(row=0, column=0, sticky="nsew")

    def show_page(self, page_name):
        """Switches the active page in the main frame."""
        # Hide all pages
        for page in self.pages.values():
            page.grid_forget()
            
        # Hide placeholder if it exists
        if hasattr(self, "placeholder_page"):
            self.placeholder_page.grid_forget()
            
        # Show the requested page
        if page_name in self.pages:
            self.pages[page_name].grid(row=0, column=0, sticky="nsew")
            
            # If the page has an update method (to refresh data), call it
            if hasattr(self.pages[page_name], "update_data"):
                self.pages[page_name].update_data()
        else:
            # Fallback for unimplemented pages
            self.placeholder_page.configure(text=f"{page_name.capitalize()} Page (Under Construction)")
            self.placeholder_page.grid(row=0, column=0, sticky="nsew")

if __name__ == "__main__":
    app = App()
    app.mainloop()
