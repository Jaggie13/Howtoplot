import tkinter as tk
from tkinter import filedialog, ttk, simpledialog, messagebox
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import rcParams, rc

class DataPlotter:
    def __init__(self, root):
        self.root = root
        self.root.title("Howtoplot")
        
        self.data = None
        self.label_entries = []
        self.linestyle_menus = []
        self.plot_checkboxes = []
        self.fig = None  # To store the figure object
        
        # Set the style for the widgets
        style = ttk.Style()
        style.configure("TButton", padding=6, relief="flat", background="#ccc")
        style.configure("TLabel", padding=6, background="#f0f0f0")
        style.configure("TCombobox", padding=6)
        
        # Create a main frame
        main_frame = ttk.Frame(root, padding="10 10 10 10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # File load button
        self.load_button = ttk.Button(main_frame, text="Load txt Data (XYXY)", command=self.load_data)
        self.load_button.grid(row=0, column=0, pady=5, sticky=tk.W)

        # Add new load button
        self.load_button_modified = ttk.Button(main_frame, text="Load txt Data (XYYY)", command=self.load_and_modify_data)
        self.load_button_modified.grid(row=0, column=1, pady=5, sticky=tk.E)

        # Label entry frame
        self.label_frame = ttk.LabelFrame(main_frame, text="Data Set Labels (LaTeX format)", padding="10 10 10 10")
        self.label_frame.grid(row=1, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))

        # Chart type selection
        self.chart_type_label = ttk.Label(main_frame, text="Select Chart Type:")
        self.chart_type_var = tk.StringVar(value="line")
        self.chart_type_menu = ttk.Combobox(main_frame, textvariable=self.chart_type_var, values=["line", "scatter"])

        # Style selection
        self.style_label = ttk.Label(main_frame, text="Select Style:")
        self.style_var = tk.StringVar(value="PL")
        self.style_menu = ttk.Combobox(main_frame, textvariable=self.style_var, values=["PL", "Raman", "I-V", "TRPL", "Transmittance", "Absorbance", "XRD", "KPFM", "PYS", "Other"])
        
        # Font size selection
        self.font_size_label = ttk.Label(main_frame, text="Select Font Size:")
        self.font_size_var = tk.StringVar(value="18")
        self.font_size_menu = ttk.Combobox(main_frame, textvariable=self.font_size_var, values=["14", "16", "18", "20", "22", "24"])

        # Log scale selection
        self.log_scale_x_var = tk.BooleanVar()
        self.log_scale_y_var = tk.BooleanVar()
        self.log_scale_x_check = ttk.Checkbutton(main_frame, text="Log Scale X-axis", variable=self.log_scale_x_var)
        self.log_scale_y_check = ttk.Checkbutton(main_frame, text="Log Scale Y-axis", variable=self.log_scale_y_var)

        # Shift options
        self.shift_x_label = ttk.Label(main_frame, text="Shift X-axis by:")
        self.shift_x_var = tk.DoubleVar(value=0.0)
        self.shift_x_entry = ttk.Entry(main_frame, textvariable=self.shift_x_var)
        
        self.shift_y_label = ttk.Label(main_frame, text="Shift Y-axis by:")
        self.shift_y_var = tk.DoubleVar(value=0.0)
        self.shift_y_entry = ttk.Entry(main_frame, textvariable=self.shift_y_var)

        # Plot button
        self.plot_button = ttk.Button(main_frame, text="Plot Data", command=self.plot_data)

        # Save button
        self.save_button = ttk.Button(main_frame, text="Save Plot", command=self.save_plot)

        # Initially hide these widgets
        self.chart_type_label.grid(row=2, column=0, pady=5, sticky=tk.W)
        self.chart_type_menu.grid(row=2, column=1, pady=5, sticky=(tk.W, tk.E))
        self.style_label.grid(row=3, column=0, pady=5, sticky=tk.W)
        self.style_menu.grid(row=3, column=1, pady=5, sticky=(tk.W, tk.E))
        self.font_size_label.grid(row=4, column=0, pady=5, sticky=tk.W)
        self.font_size_menu.grid(row=4, column=1, pady=5, sticky=(tk.W, tk.E))
        self.log_scale_x_check.grid(row=5, column=0, pady=5, sticky=tk.W)
        self.log_scale_y_check.grid(row=5, column=1, pady=5, sticky=tk.E)
        self.shift_x_label.grid(row=6, column=0, pady=5, sticky=tk.W)
        self.shift_x_entry.grid(row=6, column=1, pady=5, sticky=(tk.W, tk.E))
        self.shift_y_label.grid(row=7, column=0, pady=5, sticky=tk.W)
        self.shift_y_entry.grid(row=7, column=1, pady=5, sticky=(tk.W, tk.E))
        self.plot_button.grid(row=8, column=0, pady=5, sticky=tk.W)
        self.save_button.grid(row=8, column=1, pady=5, sticky=tk.E)
        
        self.chart_type_label.grid_remove()
        self.chart_type_menu.grid_remove()
        self.style_label.grid_remove()
        self.style_menu.grid_remove()
        self.font_size_label.grid_remove()
        self.font_size_menu.grid_remove()
        self.log_scale_x_check.grid_remove()
        self.log_scale_y_check.grid_remove()
        self.shift_x_label.grid_remove()
        self.shift_x_entry.grid_remove()
        self.shift_y_label.grid_remove()
        self.shift_y_entry.grid_remove()
        self.plot_button.grid_remove()
        self.save_button.grid_remove()

    def load_data(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            try:
                self.data = np.loadtxt(file_path)
                self.create_label_entries()
                messagebox.showinfo("Load Complete", "Data loaded successfully. Please set labels for each data set.")
                self.show_widgets()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load data: {e}")

    def load_and_modify_data(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            try:
                self.data = np.loadtxt(file_path)
                first_col = self.data[:, 0]
                data = self.data[:, 1:]
                new_data = np.empty((data.shape[0], 0))
                for col in range(data.shape[1]):
                    new_data = np.column_stack((new_data, first_col, data[:, col]))
                self.data = new_data
                self.create_label_entries()
                messagebox.showinfo("Load and Modify Complete", "Data loaded and modified successfully. Please set labels for each data set.")
                self.show_widgets()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load and modify data: {e}")

    def create_label_entries(self):
        # Clear previous label entries
        for widget in self.label_frame.winfo_children():
            widget.destroy()

        self.label_entries = []
        self.linestyle_menus = []
        self.plot_checkboxes = []
        for i in range(0, self.data.shape[1], 2):
            frame = ttk.Frame(self.label_frame)
            frame.pack(pady=2, fill=tk.X)

            label = ttk.Label(frame, text=f"Label for Data Set {i//2 + 1}:")
            label.pack(side=tk.LEFT, padx=5)
            
            entry = ttk.Entry(frame)
            entry.pack(side=tk.LEFT, padx=5)
            self.label_entries.append(entry)

            linestyle_var = tk.StringVar(value="solid")
            linestyle_menu = ttk.Combobox(frame, textvariable=linestyle_var, values=["solid", "dashed", "dashdot", "dotted"])
            linestyle_menu.pack(side=tk.LEFT, padx=5)
            self.linestyle_menus.append(linestyle_var)

            plot_var = tk.BooleanVar(value=True)
            plot_check = ttk.Checkbutton(frame, variable=plot_var)
            plot_check.pack(side=tk.LEFT, padx=5)
            self.plot_checkboxes.append(plot_var)

    def show_widgets(self):
        # Show the widgets
        self.chart_type_label.grid()
        self.chart_type_menu.grid()
        self.style_label.grid()
        self.style_menu.grid()
        self.font_size_label.grid()
        self.font_size_menu.grid()
        self.log_scale_x_check.grid()
        self.log_scale_y_check.grid()
        self.shift_x_label.grid()
        self.shift_x_entry.grid()
        self.shift_y_label.grid()
        self.shift_y_entry.grid()
        self.plot_button.grid()
        self.save_button.grid()

    def plot_data(self):
        if self.data is not None:
            labels = [entry.get() if entry.get() else f"Data Set {index + 1}" for index, entry in enumerate(self.label_entries)]
            linestyles = [var.get() for var in self.linestyle_menus]
            plot_flags = [var.get() for var in self.plot_checkboxes]
            shift_x = self.shift_x_var.get()
            shift_y = self.shift_y_var.get()
            self.fig, ax = plt.subplots()  # Create a figure and an axis
            
            # Set font properties
            font_properties = {'size': int(self.font_size_var.get())}
            rcParams.update({'font.size': font_properties['size']})
            rc('text', usetex=True)  # Enable LaTeX for text rendering
            
            for i in range(0, self.data.shape[1], 2):
                if plot_flags[i // 2]:  # Check if the dataset should be plotted
                    x = self.data[:, i] + shift_x
                    y = self.data[:, i + 1] + shift_y
                    label = labels[i // 2]
                    linestyle = linestyles[i // 2]
                    if self.chart_type_var.get() == "line":
                        ax.plot(x, y, label=label, linestyle=linestyle)
                    else:
                        ax.scatter(x, y, label=label)
    
            # Set axis labels based on selected style
            style = self.style_var.get()
            style_labels = {
                "PL": (r"$\mathrm{Wavelength\ (nm)}$", r"$\mathrm{Intensity\ (a.u.)}$"),
                "Raman": (r"$\mathrm{Raman\ Shift\ (cm^{-1})}$", r"$\mathrm{Intensity\ (a.u.)}$"),
                "I-V": (r"$\mathrm{Voltage\ (mV)}$", r"$\mathrm{Current\ (mA)}$"),
                "TRPL": (r"$\mathrm{Time\ (ns)}$", r"$\mathrm{Intensity\ (a.u.)}$"),
                "Transmittance": (r"$\mathrm{Wavelength\ (nm)}$", r"$\mathrm{Transmittance\ (\%)}$"),
                "Absorbance": (r"$\mathrm{Wavelength\ (nm)}$", r"$\mathrm{Absorbance\ (a.u.)}$"),
                "XRD": (r"$2\theta\ \mathrm{(degrees)}$", r"$\mathrm{Intensity\ (a.u.)}$"),
                "KPFM": (r"$\mathrm{Voltage\ (V)}$", r"$\mathrm{Counts}$"),
                "PYS": (r"$\mathrm{Photon\ energy\ (eV)}$", r"$\mathrm{Yield^{1/3}}$")
            }
    
            if style == "Other":
                x_label = simpledialog.askstring("Input", "Enter X-axis label (in LaTeX format):")
                y_label = simpledialog.askstring("Input", "Enter Y-axis label (in LaTeX format):")
                ax.set_xlabel(x_label, fontsize=int(self.font_size_var.get()))
                ax.set_ylabel(y_label, fontsize=int(self.font_size_var.get()))
            else:
                ax.set_xlabel(style_labels[style][0], fontsize=int(self.font_size_var.get()))
                ax.set_ylabel(style_labels[style][1], fontsize=int(self.font_size_var.get()))
    
            # Apply log scale if selected
            if self.log_scale_x_var.get():
                ax.set_xscale('log')
            if self.log_scale_y_var.get():
                ax.set_yscale('log')
    
            ax.legend(frameon=False, fontsize=int(self.font_size_var.get()))
            ax.tick_params(axis='both', which='major', width=1, labelsize=int(self.font_size_var.get()))
            ax.tick_params(axis='both', which='minor', width=1, labelsize=int(self.font_size_var.get()))
            ax.minorticks_on()
            ax.spines['top'].set_linewidth(1)
            ax.spines['right'].set_linewidth(1)
            ax.spines['bottom'].set_linewidth(1)
            ax.spines['left'].set_linewidth(1)
            plt.tight_layout()
            plt.show()
        else:
            messagebox.showerror("Error", "Please load data first")

    def save_plot(self):
        if self.data is not None and self.fig is not None:
            file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("PDF files", "*.pdf")])
            if file_path:
                self.fig.savefig(file_path, dpi=1200)
                messagebox.showinfo("Save Complete", "Plot has been saved")
        else:
            messagebox.showerror("Error", "Please load data and plot it first")

if __name__ == "__main__":
    root = tk.Tk()
    app = DataPlotter(root)
    root.mainloop()
