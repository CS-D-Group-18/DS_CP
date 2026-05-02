import customtkinter as ctk

class DashboardPage(ctk.CTkFrame):
    def __init__(self, master, engine, nav_callback, **kwargs):
        super().__init__(master, **kwargs)
        self.engine = engine
        self.nav_callback = nav_callback
        
        # Configure layout
        self.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Welcome Section
        self.welcome_label = ctk.CTkLabel(
            self, text="Welcome to Task Scheduling System", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.welcome_label.grid(row=0, column=0, columnspan=4, pady=(20, 10), sticky="w", padx=20)
        
        self.subtitle_label = ctk.CTkLabel(
            self, text="Manage tasks, define dependencies, and simulate OS scheduling algorithms.", 
            text_color="gray"
        )
        self.subtitle_label.grid(row=1, column=0, columnspan=4, pady=(0, 20), sticky="w", padx=20)

        # Statistics Cards Area
        self.stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_frame.grid(row=2, column=0, columnspan=4, sticky="new", padx=20)
        self.stats_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Cards
        self.total_card = self.create_stat_card(self.stats_frame, "Total Tasks", "0", 0)
        self.pending_card = self.create_stat_card(self.stats_frame, "Pending Tasks", "0", 1)
        self.completed_card = self.create_stat_card(self.stats_frame, "Completed Tasks", "0", 2)
        self.cpu_card = self.create_stat_card(self.stats_frame, "Total Time", "0", 3)

        # Quick Actions
        self.actions_frame = ctk.CTkFrame(self)
        self.actions_frame.grid(row=3, column=0, columnspan=2, sticky="nsew", padx=(20, 10), pady=20)
        
        actions_label = ctk.CTkLabel(self.actions_frame, text="Quick Actions", font=ctk.CTkFont(size=16, weight="bold"))
        actions_label.pack(pady=10, padx=10, anchor="w")
        
        ctk.CTkButton(self.actions_frame, text="+ Add New Task", command=lambda: self.nav_callback("tasks")).pack(pady=5, padx=20, fill="x")
        ctk.CTkButton(self.actions_frame, text="Add Dependency", command=lambda: self.nav_callback("dependencies")).pack(pady=5, padx=20, fill="x")
        ctk.CTkButton(self.actions_frame, text="Run Scheduler", command=lambda: self.nav_callback("scheduler")).pack(pady=5, padx=20, fill="x")

        # Recent Logs (Preview)
        self.logs_frame = ctk.CTkFrame(self)
        self.logs_frame.grid(row=3, column=2, columnspan=2, sticky="nsew", padx=(10, 20), pady=20)
        
        logs_label = ctk.CTkLabel(self.logs_frame, text="Recent Execution Logs", font=ctk.CTkFont(size=16, weight="bold"))
        logs_label.pack(pady=10, padx=10, anchor="w")
        
        self.log_textbox = ctk.CTkTextbox(self.logs_frame, wrap="word", state="disabled")
        self.log_textbox.pack(expand=True, fill="both", padx=10, pady=(0, 10))

    def create_stat_card(self, parent, title, value, col):
        card = ctk.CTkFrame(parent)
        card.grid(row=0, column=col, padx=10, pady=10, sticky="ew")
        
        title_lbl = ctk.CTkLabel(card, text=title, text_color="gray")
        title_lbl.pack(pady=(10, 0))
        
        value_lbl = ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=28, weight="bold"))
        value_lbl.pack(pady=(5, 10))
        return value_lbl

    def update_data(self):
        """Called whenever the dashboard is shown to refresh stats."""
        total = len(self.engine.tasks)
        completed = len(self.engine.completed_tasks)
        pending = total - completed
        
        self.total_card.configure(text=str(total))
        self.completed_card.configure(text=str(completed))
        self.pending_card.configure(text=str(pending))
        
        # Total simulation time (from engine.current_time)
        self.cpu_card.configure(text=str(self.engine.current_time))
        
        # Update logs preview
        self.log_textbox.configure(state="normal")
        self.log_textbox.delete("1.0", "end")
        
        if not self.engine.execution_log:
            self.log_textbox.insert("end", "No logs available. Run the scheduler first.")
        else:
            # Show last 5 log entries
            recent_logs = self.engine.execution_log[-5:]
            for log in recent_logs:
                self.log_textbox.insert("end", f"{log}\n")
        self.log_textbox.configure(state="disabled")
