import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
import ttkbootstrap as ttkb  # 使用 ttkbootstrap 使 UI 更现代化
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import rcParams, rc
import matplotlib
matplotlib.use('TkAgg')  # 确保使用 TkAgg 作为后端

# 全局配置字体属性
rcParams.update({
    'font.size': 18,
    'text.usetex': True,
    'font.family': 'serif',
    'font.serif': ['cm']
})

class DataPlotter:
    def __init__(self, root):
        self.root = root
        self.root.title("Howtoplot")
        self.style = ttkb.Style("flatly")  # 选择一个现代化主题
        self.root.geometry("800x600")
        
        self.data = None
        self.label_entries = []
        self.plot_flags = []  # 用于存储 Checkbutton 的状态
        self.fig = None  # To store the figure object
        
        # 创建主框架
        main_frame = ttkb.Frame(root, padding="10 10 10 10")
        main_frame.pack(fill="both", expand=True)

        # 加载数据按钮
        self.load_button = ttkb.Button(main_frame, text="Load txt Data (XYXY)", bootstyle="primary", command=self.load_data)
        self.load_button.grid(row=0, column=0, pady=5, padx=5, sticky=tk.W)

        self.load_button_modified = ttkb.Button(main_frame, text="Load txt Data (XYYY)", bootstyle="primary", command=self.load_and_modify_data)
        self.load_button_modified.grid(row=0, column=1, pady=5, padx=5, sticky=tk.EW)
        
        self.load_button_labels = ttkb.Button(main_frame, text="Load Box Data", bootstyle="primary", command=self.load_data_boxplot)
        self.load_button_labels.grid(row=0, column=2, pady=5, padx=5, sticky=tk.E)

        # 标签输入框架
        self.label_frame = ttkb.Labelframe(main_frame, text="Data Set Labels (LaTeX format)", padding="10 10 10 10")
        self.label_frame.grid(row=1, column=0, columnspan=3, pady=5, padx=5, sticky=(tk.W, tk.E))

        # 绘图类型选择
        self.chart_type_label = ttkb.Label(main_frame, text="Select Chart Type:")
        self.chart_type_label.grid(row=2, column=0, pady=5, padx=5, sticky=tk.W)
        
        self.chart_type_var = tk.StringVar(value="line")
        self.chart_type_menu = ttkb.Combobox(main_frame, textvariable=self.chart_type_var, values=["line", "scatter", "stacked"])
        self.chart_type_menu.grid(row=2, column=1, pady=5, padx=5, sticky=tk.W)

        # BoxStyle选择
        self.Boxstyle_label = ttkb.Label(main_frame, text="Select Box Style:")
        self.Boxstyle_label.grid(row=3, column=0, pady=5, padx=5, sticky=tk.W)
        
        self.Boxstyle_var = tk.StringVar(value="PCE")
        self.Boxstyle_menu = ttkb.Combobox(main_frame, textvariable=self.Boxstyle_var, values=["PCE", "Voc", "Jsc", "FF", "Other"])
        self.Boxstyle_menu.grid(row=3, column=1, pady=5, padx=5, sticky=tk.W)

        # 样式选择
        self.style_label = ttkb.Label(main_frame, text="Select Style:")
        self.style_label.grid(row=4, column=0, pady=5, padx=5, sticky=tk.W)
        
        self.style_var = tk.StringVar(value="PL")
        self.style_menu = ttkb.Combobox(main_frame, textvariable=self.style_var, values=["PL", "Raman", "I-V", "TRPL", "Transmittance", "Absorbance", "XRD", "KPFM", "PYS", "EQE", "Thickness", "Other"])
        self.style_menu.grid(row=4, column=1, pady=5, padx=5, sticky=tk.W)
        
        # 字体大小选择
        self.font_size_label = ttkb.Label(main_frame, text="Select Font Size:")
        self.font_size_label.grid(row=5, column=0, pady=5, padx=5, sticky=tk.W)
        
        self.font_size_var = tk.StringVar(value="18")
        self.font_size_menu = ttkb.Combobox(main_frame, textvariable=self.font_size_var, values=["14", "16", "18", "20", "22", "24"])
        self.font_size_menu.grid(row=5, column=1, pady=5, padx=5, sticky=tk.W)

        # 对数刻度选择
        self.log_scale_x_var = tk.BooleanVar()
        self.log_scale_y_var = tk.BooleanVar()
        self.log_scale_x_check = ttkb.Checkbutton(main_frame, text="Log Scale X-axis", variable=self.log_scale_x_var, bootstyle="info")
        self.log_scale_y_check = ttkb.Checkbutton(main_frame, text="Log Scale Y-axis", variable=self.log_scale_y_var, bootstyle="info")
        self.log_scale_x_check.grid(row=6, column=0, pady=5, padx=5, sticky=tk.W)
        self.log_scale_y_check.grid(row=6, column=1, pady=5, padx=5, sticky=tk.E)

        # 坐标轴偏移选项
        self.shift_x_label = ttkb.Label(main_frame, text="Shift X-axis by:")
        self.shift_x_label.grid(row=7, column=0, pady=5, padx=5, sticky=tk.W)
        
        self.shift_x_var = tk.DoubleVar(value=0.0)
        self.shift_x_entry = ttkb.Entry(main_frame, textvariable=self.shift_x_var)
        self.shift_x_entry.grid(row=7, column=1, pady=5, padx=5, sticky=(tk.W, tk.E))
        
        self.shift_y_label = ttkb.Label(main_frame, text="Shift Y-axis by:")
        self.shift_y_label.grid(row=8, column=0, pady=5, padx=5, sticky=tk.W)
        
        self.shift_y_var = tk.DoubleVar(value=0.0)
        self.shift_y_entry = ttkb.Entry(main_frame, textvariable=self.shift_y_var)
        self.shift_y_entry.grid(row=8, column=1, pady=5, padx=5, sticky=(tk.W, tk.E))

        # 绘图按钮
        self.plot_button = ttkb.Button(main_frame, text="Plot Data", bootstyle="success", command=self.plot_data)
        self.plot_button.grid(row=9, column=0, pady=5, padx=5, sticky=tk.W)
        
        # 保存图像按钮
        self.save_button = ttkb.Button(main_frame, text="Save Plot", bootstyle="warning", command=self.save_plot)
        self.save_button.grid(row=9, column=2, pady=5, padx=5, sticky=tk.W)

        # Boxplot按钮
        self.boxplot_button = ttkb.Button(main_frame, text="Plot Boxplot", bootstyle="success", command=self.plot_boxplot)
        self.boxplot_button.grid(row=9, column=1, pady=5, padx=5, sticky=tk.W)

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
        self.Boxstyle_label.grid()
        self.Boxstyle_menu.grid()
        self.boxplot_button.grid()
        
    def load_data(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            try:
                self.data = np.loadtxt(file_path)
                self.create_label_entries()
                messagebox.showinfo("Load Complete", "Data loaded successfully. Please set labels for each data set.")
                self.show_widgets()
                self.boxplot_button.grid_remove()
                self.Boxstyle_label.grid_remove()
                self.Boxstyle_menu.grid_remove()
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
                self.boxplot_button.grid_remove()
                self.Boxstyle_label.grid_remove()
                self.Boxstyle_menu.grid_remove()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load and modify data: {e}")

    def load_data_boxplot(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            try:
                self.data = np.loadtxt(file_path)
                # 确保数据是二维的
                if self.data.ndim == 1:
                    self.data = self.data.reshape(-1, 1)
                self.create_label_entries_boxplot()
                messagebox.showinfo("Load Complete", "Data loaded successfully. Please set labels for each data set.")
                self.show_widgets()
                self.chart_type_label.grid_remove()
                self.chart_type_menu.grid_remove()
                self.style_label.grid_remove()
                self.style_menu.grid_remove()
                self.log_scale_x_check.grid_remove()
                self.log_scale_y_check.grid_remove()
                self.shift_x_label.grid_remove()
                self.shift_x_entry.grid_remove()
                self.shift_y_label.grid_remove()
                self.shift_y_entry.grid_remove()
                self.plot_button.grid_remove()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load data: {e}")

    def create_label_entries(self):
        # Clear previous label entries
        for widget in self.label_frame.winfo_children():
            widget.destroy()

        self.label_entries = []
        self.plot_flags = []  # 用于存储是否绘制该数据集的标志
        for i in range(0, self.data.shape[1], 2):
            frame = ttkb.Frame(self.label_frame)
            frame.pack(pady=2, fill=tk.X)

            label = ttkb.Label(frame, text=f"Label for Data Set {i//2 + 1}:")
            label.pack(side=tk.LEFT, padx=5)

            entry = ttkb.Entry(frame)
            entry.pack(side=tk.LEFT, padx=5)
            self.label_entries.append(entry)

            # 增加一个 Checkbutton，用于选择是否绘制此数据集
            plot_flag = tk.BooleanVar(value=True)  # 默认选择绘制
            checkbutton = ttkb.Checkbutton(frame, text="Plot", variable=plot_flag)
            checkbutton.pack(side=tk.LEFT, padx=5)
            self.plot_flags.append(plot_flag)  # 存储每个 Checkbutton 的状态

    def create_label_entries_boxplot(self):
        # Clear previous label entries
        for widget in self.label_frame.winfo_children():
            widget.destroy()

        self.label_entries = []
        self.plot_flags = []  # 用于存储是否绘制该数据集的标志
        for i in range(0, self.data.shape[1], 1):
            frame = ttkb.Frame(self.label_frame)
            frame.pack(pady=2, fill=tk.X)

            label = ttkb.Label(frame, text=f"Label for Data Set {i + 1}:")
            label.pack(side=tk.LEFT, padx=5)
            
            entry = ttkb.Entry(frame)
            entry.pack(side=tk.LEFT, padx=5)
            self.label_entries.append(entry)

            # 增加一个 Checkbutton，用于选择是否绘制此数据集
            plot_flag = tk.BooleanVar(value=True)  # 默认选择绘制
            checkbutton = ttkb.Checkbutton(frame, text="Plot", variable=plot_flag)
            checkbutton.pack(side=tk.LEFT, padx=5)
            self.plot_flags.append(plot_flag)  # 存储每个 Checkbutton 的状态

    def plot_data(self):
        if self.data is not None:
            labels = [entry.get() if entry.get() else f"Data Set {index + 1}" for index, entry in enumerate(self.label_entries)]
            shift_x = self.shift_x_var.get()
            shift_y = self.shift_y_var.get()
            self.fig, ax = plt.subplots()  # Create a figure and an axis
            
            # 更新字体大小
            font_size = int(self.font_size_var.get())
            rcParams.update({'font.size': font_size})
            
            if self.chart_type_var.get() == "stacked":
                x = self.data[:, 0] + shift_x
                y_data = []
                for i in range(1, self.data.shape[1], 2):
                    if self.plot_flags[i // 2].get():  # 检查是否选择绘制
                        y_data.append(self.data[:, i] + shift_y)
                if y_data:
                    ax.stackplot(x, *y_data, labels=[labels[i // 2] for i in range(1, self.data.shape[1], 2) if self.plot_flags[i // 2].get()])
            else:
                for i in range(0, self.data.shape[1], 2):
                    if self.plot_flags[i // 2].get():  # 检查是否选择绘制
                        x = self.data[:, i] + shift_x
                        y = self.data[:, i + 1] + shift_y
                        label = labels[i // 2]
                        if self.chart_type_var.get() == "line":
                            ax.plot(x, y, label=label)   
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
                "PYS": (r"$\mathrm{Photon\ energy\ (eV)}$", r"$\mathrm{Yield^{1/3}}$"),
                "EQE": (r"$\mathrm{Wavelength\ (nm)}$", r"$\mathrm{EQE}$"),
                "Thickness": (r"$\mathrm{Length\ (\mu m)}$", r"$\mathrm{Height\ (\mu m)}$")
            }
    
            if style == "Other":
                x_label = simpledialog.askstring("Input", "Enter X-axis label (in LaTeX format):")
                y_label = simpledialog.askstring("Input", "Enter Y-axis label (in LaTeX format):")
                ax.set_xlabel(x_label, fontsize=font_size)
                ax.set_ylabel(y_label, fontsize=font_size)
            else:
                ax.set_xlabel(style_labels[style][0], fontsize=font_size)
                ax.set_ylabel(style_labels[style][1], fontsize=font_size)
    
            # Apply log scale if selected
            if self.log_scale_x_var.get():
                ax.set_xscale('log')
            if self.log_scale_y_var.get():
                ax.set_yscale('log')
    
            ax.legend(frameon=False, fontsize=font_size)
            ax.tick_params(axis='both', which='major', width=1, labelsize=font_size)
            ax.tick_params(axis='both', which='minor', width=1, labelsize=font_size)
            ax.minorticks_on()
            ax.spines['top'].set_linewidth(1)
            ax.spines['right'].set_linewidth(1)
            ax.spines['bottom'].set_linewidth(1)
            ax.spines['left'].set_linewidth(1)
            plt.tight_layout()
            plt.show()
        else:
            messagebox.showerror("Error", "Please load data first")

    def plot_boxplot(self):
        if self.data is not None:
            # 筛选出用户选择绘制的列
            selected_data = [self.data[:, i] for i in range(self.data.shape[1]) if self.plot_flags[i].get()]
            
            if not selected_data:
                messagebox.showerror("Error", "No data selected for plotting.")
                return
            
            filtered_data = np.column_stack(selected_data)
            
            # 获取对应的标签
            labels = [self.label_entries[i].get() if self.label_entries[i].get() else f"Data Set {i + 1}" for i in range(self.data.shape[1]) if self.plot_flags[i].get()]
            
            self.fig, ax = plt.subplots()
            
            # 更新字体大小
            font_size = int(self.font_size_var.get())
            rcParams.update({'font.size': font_size})
            
            ax.boxplot(filtered_data, labels=labels)
            
            # 根据选择的样式设置轴标签
            style = self.Boxstyle_var.get()
            style_labels = {
                "PCE": r"$\mathrm{PCE\ (\%)}$",
                "Voc": r"$\mathrm{V_{OC}\ (mV)}$",
                "Jsc": r"$\mathrm{J_{SC}\ (mA/cm^{2})}$",
                "FF": r"$\mathrm{FF}$"
            }
    
            if style == "Other":
                y_label = simpledialog.askstring("Input", "Enter Y-axis label (in LaTeX format):")
                if y_label:
                    ax.set_ylabel(y_label, fontsize=font_size)
                else:
                    ax.set_ylabel("", fontsize=font_size)
            else:
                ax.set_ylabel(style_labels.get(style, ""), fontsize=font_size)
            
            # 设置图形边框线宽
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
    root = ttkb.Window(themename="flatly")
    app = DataPlotter(root)
    root.mainloop()
