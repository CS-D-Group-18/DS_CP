import customtkinter as ctk

class SettingsPage(ctk.CTkFrame):
    def __init__(self, master, engine, nav_callback, **kwargs):
        super().__init__(master, **kwargs)
        self.engine = engine
        self.nav_callback = nav_callback
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        title_label = ctk.CTkLabel(self, text="Settings & About", font=ctk.CTkFont(size=24, weight="bold"))
        title_label.grid(row=0, column=0, pady=(20, 10), padx=20, sticky="w")
        
        # Appearance Settings
        settings_frame = ctk.CTkFrame(self)
        settings_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        
        ctk.CTkLabel(settings_frame, text="Appearance", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10, padx=10, anchor="w")
        
        theme_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        theme_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(theme_frame, text="Theme Mode:").pack(side="left", padx=(0, 20))
        self.theme_var = ctk.StringVar(value="System")
        theme_dropdown = ctk.CTkOptionMenu(theme_frame, values=["System", "Light", "Dark"], 
                                           variable=self.theme_var, command=self.change_theme)
        theme_dropdown.pack(side="left")

        # About Section
        about_frame = ctk.CTkFrame(self)
        about_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=20)
        
        ctk.CTkLabel(about_frame, text="About the Project", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10, padx=10, anchor="w")
        
        about_text = (
            "Task Scheduling System Simulator v1.0\n\n"
            "This application simulates an Operating System's task scheduling mechanisms.\n"
            "It supports multiple algorithms including Priority, Shortest Job First (SJF), "
            "and Earliest Deadline First (EDF).\n\n"
            "Features:\n"
            "- Custom Min/Max Heap implementation\n"
            "- O(1) task lookups via hash maps\n"
            "- Dependency resolution using a Directed Acyclic Graph (DAG) with Kahn's algorithm\n"
            "- Task aging to prevent starvation\n"
            "- Detailed performance metrics and visualizations"
        )
        ctk.CTkLabel(about_frame, text=about_text, justify="left").pack(pady=10, padx=20, anchor="w")
        
        # Team Members Placeholder
        ctk.CTkLabel(about_frame, text="Team Members", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(20, 5), padx=10, anchor="w")
        ctk.CTkLabel(about_frame, text="- Member 1\n- Member 2\n- Member 3", justify="left").pack(padx=20, anchor="w")

    def change_theme(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)
        
    def update_data(self):
        pass
