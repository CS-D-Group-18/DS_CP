import customtkinter as ctk

class Sidebar(ctk.CTkFrame):
    def __init__(self, master, nav_callback, **kwargs):
        super().__init__(master, fg_color="#111827", **kwargs) # Modern dark theme
        self.nav_callback = nav_callback
        
        # Project Title
        self.title_label = ctk.CTkLabel(
            self, 
            text="⚙️ Task System", 
            font=ctk.CTkFont(family="Inter", size=22, weight="bold"),
            text_color="#f9fafb"
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=(30, 20), sticky="w")
        
        # Navigation Buttons
        self.buttons = []
        
        self.dashboard_btn = self.create_nav_button("📊 Dashboard", "dashboard", row=1)
        self.task_btn = self.create_nav_button("📝 Manage Tasks", "tasks", row=2)
        self.dep_btn = self.create_nav_button("🔗 Dependencies", "dependencies", row=3)
        self.scheduler_btn = self.create_nav_button("▶️ Run Scheduler", "scheduler", row=4)
        self.logs_btn = self.create_nav_button("📜 Execution Logs", "logs", row=5)
        self.report_btn = self.create_nav_button("📈 Reports", "reports", row=6)
        self.settings_btn = self.create_nav_button("⚙️ Settings", "settings", row=7)

        # Bottom stretch to push things up
        self.grid_rowconfigure(8, weight=1)
        
        # App Version / Info at the bottom
        self.info_label = ctk.CTkLabel(
            self, 
            text="Version 1.0\nOS Simulator", 
            font=ctk.CTkFont(size=10, weight="normal"),
            text_color="#a0c4e0"
        )
        self.info_label.grid(row=9, column=0, padx=20, pady=20)

    def create_nav_button(self, text, page_name, row):
        btn = ctk.CTkButton(
            self, 
            text=text, 
            corner_radius=8, 
            height=40,
            border_spacing=10, 
            text_color="#9ca3af", # gray-400
            hover_color="#1f2937", # gray-800
            fg_color="transparent",
            anchor="w",
            font=ctk.CTkFont(family="Inter", size=14, weight="normal"),
            command=lambda: self.on_nav_click(page_name)
        )
        btn.grid(row=row, column=0, sticky="ew", padx=15, pady=4)
        self.buttons.append((btn, page_name))
        return btn

    def on_nav_click(self, page_name):
        # Update button colors to indicate active
        for btn, name in self.buttons:
            if name == page_name:
                # Active state: lighter text, visible background, bold font
                btn.configure(
                    fg_color="#374151", # gray-700
                    text_color="#ffffff",
                    font=ctk.CTkFont(family="Inter", size=14, weight="bold")
                )
            else:
                # Inactive state
                btn.configure(
                    fg_color="transparent", 
                    text_color="#9ca3af",
                    font=ctk.CTkFont(family="Inter", size=14, weight="normal")
                )
                
        # Call the app's callback to switch frame
        self.nav_callback(page_name)
