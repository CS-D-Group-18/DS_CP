import customtkinter as ctk
from tkinter import messagebox

class SchedulerPage(ctk.CTkFrame):
    def __init__(self, master, engine, nav_callback, **kwargs):
        super().__init__(master, **kwargs)
        self.engine = engine
        self.nav_callback = nav_callback
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # Top section
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        
        title_label = ctk.CTkLabel(top_frame, text="Scheduler Simulation", font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(side="left")
        
        # Controls
        controls_frame = ctk.CTkFrame(self)
        controls_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        
        ctk.CTkLabel(controls_frame, text="Select Algorithm:").pack(side="left", padx=(20, 10), pady=20)
        self.algo_var = ctk.StringVar(value="Priority")
        self.algo_dropdown = ctk.CTkOptionMenu(controls_frame, variable=self.algo_var, 
                                               values=["Priority", "SJF", "EDF"])
        self.algo_dropdown.pack(side="left", padx=10)
        
        self.run_btn = ctk.CTkButton(controls_frame, text="Run Simulation", command=self.run_simulation, fg_color="#2E7D32", hover_color="#1B5E20")
        self.run_btn.pack(side="left", padx=20)
        
        self.status_lbl = ctk.CTkLabel(controls_frame, text="Status: Ready", text_color="gray")
        self.status_lbl.pack(side="right", padx=20)
        
        # Main content area
        content_frame = ctk.CTkFrame(self)
        content_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 20))
        content_frame.grid_columnconfigure((0, 1), weight=1)
        content_frame.grid_rowconfigure(1, weight=1)
        
        # Log Output
        ctk.CTkLabel(content_frame, text="Execution Log", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, pady=(10, 0), sticky="w")
        self.log_textbox = ctk.CTkTextbox(content_frame, wrap="word", state="disabled")
        self.log_textbox.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        # Final State
        ctk.CTkLabel(content_frame, text="Final Task State", font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, padx=10, pady=(10, 0), sticky="w")
        self.state_textbox = ctk.CTkTextbox(content_frame, wrap="word", state="disabled")
        self.state_textbox.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

    def run_simulation(self):
        if not self.engine.tasks:
            messagebox.showwarning("Warning", "No tasks available to schedule.")
            return
            
        algo = self.algo_var.get()
        self.status_lbl.configure(text=f"Status: Running {algo}...")
        self.run_btn.configure(state="disabled")
        
        try:
            # We run it synchronously as it's typically fast enough.
            # Real-time visualization would require a separate thread or step-by-step logic.
            self.engine.run(algo)
            
            self.status_lbl.configure(text=f"Status: Completed (Time: {self.engine.current_time})", text_color="green")
            self.refresh_displays()
            messagebox.showinfo("Success", "Simulation completed successfully.")
            
        except Exception as e:
            self.status_lbl.configure(text="Status: Failed", text_color="red")
            messagebox.showerror("Simulation Error", str(e))
        finally:
            self.run_btn.configure(state="normal")
            
    def refresh_displays(self):
        self.log_textbox.configure(state="normal")
        self.log_textbox.delete("1.0", "end")
        for log in self.engine.execution_log:
            self.log_textbox.insert("end", log + "\n")
        self.log_textbox.configure(state="disabled")
        
        self.state_textbox.configure(state="normal")
        self.state_textbox.delete("1.0", "end")
        for task in self.engine.tasks.values():
            self.state_textbox.insert("end", f"[{task.task_id}] {task.name}: {task.status.name} "
                                             f"(Turnaround: {task.turnaround_time}, Wait: {task.waiting_time})\n")
        self.state_textbox.configure(state="disabled")

    def update_data(self):
        # Clear logs if simulation was reset elsewhere, but typically we just keep it
        pass
