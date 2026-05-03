import customtkinter as ctk
from tkinter import filedialog, messagebox, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from report import ReportGenerator

class ReportPage(ctk.CTkScrollableFrame):
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
        
        title_label = ctk.CTkLabel(header_frame, text="Reports Overview", font=ctk.CTkFont(family="Inter", size=24, weight="bold"), text_color="#111827")
        title_label.pack(side="left")
        
        export_btn = ctk.CTkButton(header_frame, text="💾 Export Summary", fg_color="#4f46e5", hover_color="#4338ca", text_color="white", corner_radius=8, height=42, font=ctk.CTkFont(family="Inter", size=14, weight="bold"), command=self.export_report)
        export_btn.pack(side="right")
        
        # Stats summary frame
        self.stats_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=6, border_width=1, border_color="#e0e0e0")
        self.stats_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        
        ctk.CTkLabel(self.stats_frame, text="Metrics Summary", font=ctk.CTkFont(family="Inter", size=16, weight="bold"), text_color="#1e2022").pack(pady=15, padx=20, anchor="w")
        self.metrics_text = ctk.CTkLabel(self.stats_frame, text="Run the scheduler to generate metrics.", justify="left", font=ctk.CTkFont(family="Inter", size=14), text_color="#333333")
        self.metrics_text.pack(pady=5, padx=20, anchor="w")

        # Pie Chart Frame (Completion Status)
        self.pie_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=6, border_width=1, border_color="#e0e0e0")
        self.pie_frame.grid(row=1, column=1, padx=(0, 20), pady=10, sticky="nsew")
        
        # Bar Chart Frame (Task Times)
        self.bar_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=6, border_width=1, border_color="#e0e0e0")
        self.bar_frame.grid(row=2, column=0, padx=20, pady=(10, 10), sticky="nsew")

        # Line Graph Frame (CPU Utilization)
        self.line_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=6, border_width=1, border_color="#e0e0e0")
        self.line_frame.grid(row=2, column=1, padx=(0, 20), pady=(10, 10), sticky="nsew")

        # Gantt Chart Frame
        self.gantt_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=6, border_width=1, border_color="#e0e0e0")
        self.gantt_frame.grid(row=3, column=0, columnspan=2, padx=20, pady=(10, 20), sticky="nsew")

        # Treeview Frame
        self.table_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=6, border_width=1, border_color="#e0e0e0")
        self.table_frame.grid(row=4, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="nsew")
        
        ctk.CTkLabel(self.table_frame, text="Task Execution Details", font=ctk.CTkFont(family="Inter", size=16, weight="bold"), text_color="#1e2022").pack(pady=15, padx=20, anchor="w")
        
        # Configure treeview style
        style = ttk.Style()
        style.theme_use("default")
        
        # Modern Treeview Styling (Light theme)
        style.configure("Treeview", 
                        background="white", foreground="#333333", 
                        fieldbackground="white", rowheight=30, borderwidth=0, font=("Inter", 11))
        style.map('Treeview', background=[('selected', '#e9ecef')], foreground=[('selected', '#1f538d')])
        
        style.configure("Treeview.Heading", 
                        background="#f8f9fa", foreground="#6c757d", 
                        font=("Inter", 11, "bold"), borderwidth=1, padding=5)
        style.map("Treeview.Heading", background=[('active', '#e9ecef')])
        
        self.tree = ttk.Treeview(self.table_frame, columns=("ID", "Name", "Wait", "Turnaround", "Status"), show="headings", height=8)
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Wait", text="Wait Time")
        self.tree.heading("Turnaround", text="Turnaround")
        self.tree.heading("Status", text="Status")
        self.tree.pack(expand=True, fill="both", padx=10, pady=10)

    def update_data(self):
        if not self.engine.execution_log:
            self.metrics_text.configure(text="No data available. Run the scheduler first.")
            return
            
        generator = ReportGenerator(self.engine)
        metrics = generator.generate_summary()
        
        summary = (
            f"Total Tasks: {metrics['Total Tasks Submitted']}\n"
            f"Completed Tasks: {metrics['Completed Successfully']}\n"
            f"Missed Deadlines: {metrics['Missed Deadlines']}\n"
            f"Average Waiting Time: {metrics['Average Waiting Time']:.2f}\n"
            f"Average Turnaround Time: {metrics['Average Turnaround Time']:.2f}\n"
            f"Total Execution Time (CPU): {metrics['Total Time Taken']}"
        )
        self.metrics_text.configure(text=summary)
        
        self.draw_charts()

    def draw_charts(self):
        # Ahrefs styling
        bg_color = '#ffffff'
        text_color = '#6c757d'
        title_color = '#1e2022'
        
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
        colors = ['#27ae60', '#e74c3c', '#dcdcdc']
        
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
            
        fig2, ax2 = plt.subplots(figsize=(4, 3), dpi=100)
        fig2.patch.set_facecolor(bg_color)
        ax2.set_facecolor(bg_color)
        ax2.tick_params(colors=text_color)
        for spine in ax2.spines.values():
            spine.set_edgecolor('#e0e0e0')
            
        completed_tasks = self.engine.completed_tasks
        if completed_tasks:
            names = [t.task_id for t in completed_tasks]
            turnaround = [t.turnaround_time for t in completed_tasks]
            wait = [t.waiting_time for t in completed_tasks]
            
            x = range(len(names))
            width = 0.35
            
            ax2.bar([i - width/2 for i in x], turnaround, width, label='Turnaround Time', color='#004b87')
            ax2.bar([i + width/2 for i in x], wait, width, label='Waiting Time', color='#f39c12')
            
            ax2.set_ylabel('Time Units', color=text_color)
            ax2.set_title('Task Execution Times', color=title_color, pad=10, fontweight='bold')
            ax2.set_xticks(x)
            ax2.set_xticklabels(names, rotation=0, color=text_color)
            legend = ax2.legend(frameon=False)
            for text in legend.get_texts():
                text.set_color(text_color)
        else:
            ax2.text(0.5, 0.5, 'No Completed Tasks', ha='center', va='center', color=text_color)
            ax2.axis('off')
            
        fig2.tight_layout()
        canvas2 = FigureCanvasTkAgg(fig2, master=self.bar_frame)
        canvas2.draw()
        canvas2.get_tk_widget().pack(expand=True, fill="both")

        # 3. Gantt Chart
        for widget in self.gantt_frame.winfo_children():
            widget.destroy()
            
        fig3, ax3 = plt.subplots(figsize=(8, 3), dpi=100)
        fig3.patch.set_facecolor(bg_color)
        ax3.set_facecolor(bg_color)
        ax3.tick_params(colors=text_color)
        for spine in ax3.spines.values():
            spine.set_edgecolor('#e0e0e0')
            
        if completed_tasks:
            for i, t in enumerate(completed_tasks):
                start_time = t.completion_time - t.exec_time
                ax3.barh(i, t.exec_time, left=start_time, color='#27ae60', height=0.6)
                ax3.text(start_time + t.exec_time/2, i, t.task_id, ha='center', va='center', color='white', fontweight='bold')
                
            ax3.set_yticks(range(len(completed_tasks)))
            ax3.set_yticklabels([t.task_id for t in completed_tasks], color=text_color)
            ax3.set_xlabel('Time', color=text_color)
            ax3.set_title('Task Timeline (Gantt)', color=title_color, pad=10, fontweight='bold')
        else:
            ax3.text(0.5, 0.5, 'No Data', ha='center', va='center', color=text_color)
            ax3.axis('off')
            
        fig3.tight_layout()
        canvas3 = FigureCanvasTkAgg(fig3, master=self.gantt_frame)
        canvas3.draw()
        canvas3.get_tk_widget().pack(expand=True, fill="both")
        
        # 4. Line Graph for CPU Utilization over time
        for widget in self.line_frame.winfo_children():
            widget.destroy()
            
        fig4, ax4 = plt.subplots(figsize=(4, 3), dpi=100)
        fig4.patch.set_facecolor(bg_color)
        ax4.set_facecolor(bg_color)
        ax4.tick_params(colors=text_color)
        for spine in ax4.spines.values():
            spine.set_edgecolor('#e0e0e0')
            
        if completed_tasks:
            max_time = max(t.completion_time for t in completed_tasks)
            # Create a time series array
            time_series = [0] * (max_time + 1)
            for t in completed_tasks:
                start_time = t.completion_time - t.exec_time
                for i in range(start_time, t.completion_time):
                    if i <= max_time:
                        time_series[i] = 1 # CPU is active
            
            # Cumulative CPU utilization
            cum_active = 0
            utilization = []
            for i, active in enumerate(time_series):
                cum_active += active
                util = (cum_active / (i + 1)) * 100 if i > 0 else (active * 100)
                utilization.append(util)
                
            ax4.plot(range(max_time + 1), utilization, color='#004b87', linewidth=2.5)
            ax4.fill_between(range(max_time + 1), utilization, color='#004b87', alpha=0.1)
            ax4.set_xlabel('Time', color=text_color)
            ax4.set_ylabel('CPU Util (%)', color=text_color)
            ax4.set_title('CPU Utilization Trend', color=title_color, pad=10, fontweight='bold')
            ax4.set_ylim(0, 105)
        else:
            ax4.text(0.5, 0.5, 'No Data', ha='center', va='center', color=text_color)
            ax4.axis('off')
            
        fig4.tight_layout()
        canvas4 = FigureCanvasTkAgg(fig4, master=self.line_frame)
        canvas4.draw()
        canvas4.get_tk_widget().pack(expand=True, fill="both")
        
        # Populate Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        for t in self.engine.tasks.values():
            self.tree.insert("", "end", values=(t.task_id, t.name, t.waiting_time, t.turnaround_time, t.status.name))

    def export_report(self):
        if not self.engine.execution_log:
            messagebox.showwarning("Warning", "No data to export.")
            return
            
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", 
                                                 filetypes=[("CSV files", "*.csv"), ("Text files", "*.txt")],
                                                 title="Save Report")
        if file_path:
            try:
                if file_path.endswith('.csv'):
                    data = []
                    for t in self.engine.tasks.values():
                        data.append({
                            "Task ID": t.task_id,
                            "Name": t.name,
                            "Priority": t.priority,
                            "Arrival Time": t.arrival_time,
                            "Execution Time": t.exec_time,
                            "Waiting Time": t.waiting_time,
                            "Turnaround Time": t.turnaround_time,
                            "Status": t.status.name
                        })
                    df = pd.DataFrame(data)
                    df.to_csv(file_path, index=False)
                    messagebox.showinfo("Success", "Report exported to CSV successfully.")
                else:
                    with open(file_path, 'w') as f:
                        generator = ReportGenerator(self.engine)
                        metrics = generator.generate_summary()
                        f.write("TASK SCHEDULING REPORT\n")
                        f.write("="*30 + "\n\n")
                        for k, v in metrics.items():
                            f.write(f"{k.replace('_', ' ').title()}: {v}\n")
                    messagebox.showinfo("Success", "Report exported successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {e}")
