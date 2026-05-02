import customtkinter as ctk
from tkinter import filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from report import ReportGenerator

class ReportPage(ctk.CTkFrame):
    def __init__(self, master, engine, nav_callback, **kwargs):
        super().__init__(master, **kwargs)
        self.engine = engine
        self.nav_callback = nav_callback
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=20, pady=20)
        
        title_label = ctk.CTkLabel(header_frame, text="Reports & Analytics", font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(side="left")
        
        export_btn = ctk.CTkButton(header_frame, text="Export Summary", command=self.export_report)
        export_btn.pack(side="right")
        
        # Stats summary frame
        self.stats_frame = ctk.CTkFrame(self)
        self.stats_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        
        ctk.CTkLabel(self.stats_frame, text="Metrics Summary", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        self.metrics_text = ctk.CTkLabel(self.stats_frame, text="Run the scheduler to generate metrics.", justify="left")
        self.metrics_text.pack(pady=10, padx=20, anchor="w")

        # Pie Chart Frame (Completion Status)
        self.pie_frame = ctk.CTkFrame(self)
        self.pie_frame.grid(row=1, column=1, padx=(0, 20), pady=10, sticky="nsew")
        
        # Bar Chart Frame (Task Times)
        self.bar_frame = ctk.CTkFrame(self)
        self.bar_frame.grid(row=2, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="nsew")

    def update_data(self):
        if not self.engine.execution_log:
            self.metrics_text.configure(text="No data available. Run the scheduler first.")
            return
            
        generator = ReportGenerator(self.engine)
        metrics = generator.calculate_metrics()
        
        summary = (
            f"Total Tasks: {metrics['total_tasks']}\n"
            f"Completed Tasks: {metrics['completed_tasks']}\n"
            f"Missed Deadlines: {metrics['missed_deadlines']}\n"
            f"Average Waiting Time: {metrics['avg_waiting_time']:.2f}\n"
            f"Average Turnaround Time: {metrics['avg_turnaround_time']:.2f}\n"
            f"Total Execution Time (CPU): {metrics['total_execution_time']}"
        )
        self.metrics_text.configure(text=summary)
        
        self.draw_charts()

    def draw_charts(self):
        # Apply dark/light mode bg
        mode = ctk.get_appearance_mode()
        bg_color = '#2b2b2b' if mode == 'Dark' else '#f0f0f0'
        text_color = 'white' if mode == 'Dark' else 'black'
        
        # 1. Pie Chart for Status
        for widget in self.pie_frame.winfo_children():
            widget.destroy()
            
        completed = len([t for t in self.engine.tasks.values() if t.status.name == "COMPLETED"])
        missed = len([t for t in self.engine.tasks.values() if t.status.name == "MISSED"])
        others = len(self.engine.tasks) - completed - missed
        
        fig1, ax1 = plt.subplots(figsize=(3, 3), dpi=100)
        fig1.patch.set_facecolor(bg_color)
        
        labels = ['Completed', 'Missed', 'Pending/Other']
        sizes = [completed, missed, others]
        colors = ['#2ca02c', '#d62728', '#7f7f7f']
        
        # Filter out 0s
        labels = [l for l, s in zip(labels, sizes) if s > 0]
        colors = [c for c, s in zip(colors, sizes) if s > 0]
        sizes = [s for s in sizes if s > 0]
        
        if sizes:
            ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90, textprops={'color': text_color})
            ax1.axis('equal')
        else:
            ax1.set_facecolor(bg_color)
            ax1.text(0.5, 0.5, 'No Data', ha='center', va='center', color=text_color)
            ax1.axis('off')
            
        canvas1 = FigureCanvasTkAgg(fig1, master=self.pie_frame)
        canvas1.draw()
        canvas1.get_tk_widget().pack(expand=True, fill="both")

        # 2. Bar Chart for Turnaround vs Wait Time
        for widget in self.bar_frame.winfo_children():
            widget.destroy()
            
        fig2, ax2 = plt.subplots(figsize=(8, 3), dpi=100)
        fig2.patch.set_facecolor(bg_color)
        ax2.set_facecolor(bg_color)
        ax2.tick_params(colors=text_color)
        for spine in ax2.spines.values():
            spine.set_edgecolor(text_color)
            
        completed_tasks = self.engine.completed_tasks
        if completed_tasks:
            names = [t.task_id for t in completed_tasks]
            turnaround = [t.turnaround_time for t in completed_tasks]
            wait = [t.waiting_time for t in completed_tasks]
            
            x = range(len(names))
            width = 0.35
            
            ax2.bar([i - width/2 for i in x], turnaround, width, label='Turnaround Time', color='#1f77b4')
            ax2.bar([i + width/2 for i in x], wait, width, label='Waiting Time', color='#ff7f0e')
            
            ax2.set_ylabel('Time Units', color=text_color)
            ax2.set_title('Task Execution Times', color=text_color)
            ax2.set_xticks(x)
            ax2.set_xticklabels(names, rotation=45, color=text_color)
            legend = ax2.legend()
            for text in legend.get_texts():
                text.set_color("black")
        else:
            ax2.text(0.5, 0.5, 'No Completed Tasks', ha='center', va='center', color=text_color)
            ax2.axis('off')
            
        fig2.tight_layout()
        canvas2 = FigureCanvasTkAgg(fig2, master=self.bar_frame)
        canvas2.draw()
        canvas2.get_tk_widget().pack(expand=True, fill="both")

    def export_report(self):
        if not self.engine.execution_log:
            messagebox.showwarning("Warning", "No data to export.")
            return
            
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", 
                                                 filetypes=[("Text files", "*.txt")],
                                                 title="Save Report")
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    generator = ReportGenerator(self.engine)
                    metrics = generator.calculate_metrics()
                    f.write("TASK SCHEDULING REPORT\n")
                    f.write("="*30 + "\n\n")
                    for k, v in metrics.items():
                        f.write(f"{k.replace('_', ' ').title()}: {v}\n")
                messagebox.showinfo("Success", "Report exported successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {e}")
