import customtkinter as ctk

class Sidebar(ctk.CTkFrame):
    def __init__(self, master, nav_callback, **kwargs):
        super().__init__(master, **kwargs)
        self.nav_callback = nav_callback
        
        # Project Title
        self.title_label = ctk.CTkLabel(
            self, 
            text="Task Scheduler", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Navigation Buttons
        self.buttons = []
        
        self.dashboard_btn = self.create_nav_button("Dashboard", "dashboard", row=1)
        self.task_btn = self.create_nav_button("Manage Tasks", "tasks", row=2)
        self.dep_btn = self.create_nav_button("Dependencies", "dependencies", row=3)
        self.scheduler_btn = self.create_nav_button("Run Scheduler", "scheduler", row=4)
        self.logs_btn = self.create_nav_button("Execution Logs", "logs", row=5)
        self.report_btn = self.create_nav_button("Reports", "reports", row=6)
        self.settings_btn = self.create_nav_button("Settings", "settings", row=7)

        # Bottom stretch to push things up
        self.grid_rowconfigure(8, weight=1)
        
        # App Version / Info at the bottom
        self.info_label = ctk.CTkLabel(
            self, 
            text="Version 1.0\nOS Simulator", 
            font=ctk.CTkFont(size=10, weight="normal"),
            text_color="gray"
        )
        self.info_label.grid(row=9, column=0, padx=20, pady=20)

    def create_nav_button(self, text, page_name, row):
        btn = ctk.CTkButton(
            self, 
            text=text, 
            corner_radius=0, 
            height=40,
            border_spacing=10, 
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"),
            fg_color="transparent",
            anchor="w",
            command=lambda: self.on_nav_click(page_name)
        )
        btn.grid(row=row, column=0, sticky="ew")
        self.buttons.append((btn, page_name))
        return btn

    def on_nav_click(self, page_name):
        # Update button colors to indicate active
        for btn, name in self.buttons:
            if name == page_name:
                btn.configure(fg_color=("gray75", "gray25"))
            else:
                btn.configure(fg_color="transparent")
                
        # Call the app's callback to switch frame
        self.nav_callback(page_name)
