import tkinter as tk
from tkinter import filedialog, ttk, simpledialog, messagebox
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import rcParams

class DataPlotter:
    def __init__(self, root):
        self.root = root
        self.root.title("Howtoplot")
        
        self.data = None
        self.label_entries = []
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
        self.load_button = ttk.Button(main_frame, text="Load txt Data", command=self.load_data)
        self.load_button.grid(row=0, column=0, pady=5, sticky=tk.W)

        # Label entry frame
        self.label_frame = ttk.LabelFrame(main_frame, text="Data Set Labels", padding="10 10 10 10")
        self.label_frame.grid(row=1, column=0, pady=5, sticky=(tk.W, tk.E))

        # Chart type selection
        self.chart_type_label = ttk.Label(main_frame, text="Select Chart Type:")
        self.chart_type_label.grid(row=2, column=0, pady=5, sticky=tk.W)
        self.chart_type_var = tk.StringVar(value="line")
        self.chart_type_menu = ttk.Combobox(main_frame, textvariable=self.chart_type_var, values=["line", "scatter"])
        self.chart_type_menu.grid(row=2, column=1, pady=5, sticky=(tk.W, tk.E))
        
        # Style selection
        self.style_label = ttk.Label(main_frame, text="Select Style:")
        self.style_label.grid(row=3, column=0, pady=5, sticky=tk.W)
        self.style_var = tk.StringVar(value="PL")
        self.style_menu = ttk.Combobox(main_frame, textvariable=self.style_var, values=["PL", "Raman", "I-V", "TRPL", "Transmittance", "Absorbance", "XRD", "Other"])
        self.style_menu.grid(row=3, column=1, pady=5, sticky=(tk.W, tk.E))
        
        # Font size selection
        self.font_size_label = ttk.Label(main_frame, text="Select Font Size:")
        self.font_size_label.grid(row=4, column=0, pady=5, sticky=tk.W)
        self.font_size_var = tk.StringVar(value="13")
        self.font_size_menu = ttk.Combobox(main_frame, textvariable=self.font_size_var, values=["8", "10", "12", "14", "16", "18", "20"])
        self.font_size_menu.grid(row=4, column=1, pady=5, sticky=(tk.W, tk.E))

        # Plot button
        self.plot_button = ttk.Button(main_frame, text="Plot Data", command=self.plot_data)
        self.plot_button.grid(row=5, column=0, pady=5, sticky=tk.W)

        # Save button
        self.save_button = ttk.Button(main_frame, text="Save Plot", command=self.save_plot)
        self.save_button.grid(row=5, column=1, pady=5, sticky=tk.E)

    def load_data(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            try:
                self.data = np.loadtxt(file_path)
                self.create_label_entries()
                messagebox.showinfo("Load Complete", "Data loaded successfully. Please set labels for each data set.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load data: {e}")

    def create_label_entries(self):
        # Clear previous label entries
        for widget in self.label_frame.winfo_children():
            widget.destroy()

        self.label_entries = []
        for i in range(0, self.data.shape[1], 2):
            label = ttk.Label(self.label_frame, text=f"Label for Data Set {i//2+1}:")
            label.pack(pady=2)
            entry = ttk.Entry(self.label_frame)
            entry.pack(pady=2)
            self.label_entries.append(entry)

    def plot_data(self):
        if self.data is not None:
            labels = [entry.get() if entry.get() else f"Data Set {i//2+1}" for i, entry in enumerate(self.label_entries)]
            self.fig, ax = plt.subplots()  # Create a figure and an axis
            
            # Set font properties
            font_properties = {'family': 'Times New Roman', 'size': int(self.font_size_var.get())}
            rcParams.update({'font.family': font_properties['family'], 'font.size': font_properties['size']})
            
            for i in range(0, self.data.shape[1], 2):
                x = self.data[:, i]
                y = self.data[:, i+1]
                label = labels[i//2]
                if self.chart_type_var.get() == "line":
                    ax.plot(x, y, label=label)
                else:
                    ax.scatter(x, y, label=label)

            # Set axis labels based on selected style
            style = self.style_var.get()
            style_labels = {
                "PL": (r"$\mathrm{Wavelength\ (nm)}$", r"$\mathrm{Intensity\ (a.u.)}$"),
                "Raman": (r"$\mathrm{Raman\ Shift\ (cm^{-1})}$", r"$\mathrm{Intensity\ (a.u.)}$"),
                "I-V": (r"$\mathrm{Voltage\ (V)}$", r"$\mathrm{Current\ (A)}$"),
                "TRPL": (r"$\mathrm{Time\ (ns)}$", r"$\mathrm{Intensity\ (a.u.)}$"),
                "Transmittance": (r"$\mathrm{Wavelength\ (nm)}$", r"$\mathrm{Transmittance\ (\%)}$"),
                "Absorbance": (r"$\mathrm{Wavelength\ (nm)}$", r"$\mathrm{Absorbance\ (a.u.)}$"),
                "XRD": (r"$2\theta\ \mathrm{(degrees)}$", r"$\mathrm{Intensity\ (a.u.)}$")
            }

            if style == "Other":
                x_label = simpledialog.askstring("Input", "Enter X-axis label (in LaTeX format):")
                y_label = simpledialog.askstring("Input", "Enter Y-axis label (in LaTeX format):")
                ax.set_xlabel(x_label, fontsize=int(self.font_size_var.get()), fontfamily='Times New Roman')
                ax.set_ylabel(y_label, fontsize=int(self.font_size_var.get()), fontfamily='Times New Roman')
            else:
                ax.set_xlabel(style_labels[style][0], fontsize=int(self.font_size_var.get()), fontfamily='Times New Roman')
                ax.set_ylabel(style_labels[style][1], fontsize=int(self.font_size_var.get()), fontfamily='Times New Roman')

            ax.legend(frameon=False, fontsize=int(self.font_size_var.get()), prop={'family': 'Times New Roman'})
            ax.tick_params(axis='both', which='major', labelsize=int(self.font_size_var.get()))
            ax.tick_params(axis='both', which='minor', labelsize=int(self.font_size_var.get()))
            ax.minorticks_on()
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
