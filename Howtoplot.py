import tkinter as tk
from tkinter import filedialog, messagebox
import ttkbootstrap as ttkb  # 使用 ttkbootstrap 使 UI 更现代化
from tkinterdnd2 import TkinterDnD, DND_FILES  # 导入 TkinterDnD 库，用于实现拖放功能
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import rcParams
import matplotlib
matplotlib.use('Qt5Agg')
import pickle
import os

# Global font configuration for plots
rcParams.update({
    'font.size': 16,
    'text.usetex': False,
    'font.family': 'serif',
    'font.serif': ['Times New Roman']
})

class DataPlotter(TkinterDnD.Tk):  
    def __init__(self):
        super().__init__()
        self.title("Howtoplot")
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{screen_width}x{screen_height}")
        self.style = ttkb.Style("lumen")  # Use a modern theme

        # Set default font and style for widgets
        self.option_add("*Font", "Arial 12")
        self.style.configure("TButton", font=("Arial", 12), padding=5)
        self.style.configure("TLabel", font=("Arial", 12))
        self.style.configure("TEntry", padding=5)
        self.style.configure("TCombobox", padding=5)

        # Main frame and subframe layout
        main_frame = ttkb.Frame(self, padding="15 15 15 15")
        main_frame.pack(fill="both", expand=True)

        # Data Load section (XYXY)
        data_load_frame = ttkb.LabelFrame(main_frame, text="Data Load (XYXY)", padding="10 10 10 10")
        data_load_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.load_button = ttkb.Button(data_load_frame, text="Load Data (XYXY)", bootstyle="primary", command=self.load_data)
        self.load_button.grid(row=0, column=0, pady=5, padx=5, sticky="ew")

        self.drop_area_xyxy = ttkb.Label(data_load_frame, text="Drag & Drop File Here (XYXY)", relief="ridge", bootstyle="info", padding=10, anchor="center")
        self.drop_area_xyxy.grid(row=1, column=0, pady=5, padx=5, sticky="ew")
        self.drop_area_xyxy.drop_target_register(DND_FILES)
        self.drop_area_xyxy.dnd_bind('<<Drop>>', self.on_drop_xyxy)

        # Data Load section (XYYY)
        data_load_xyyy_frame = ttkb.LabelFrame(main_frame, text="Data Load (XYYY)", padding="10 10 10 10")
        data_load_xyyy_frame.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        self.load_button_modified = ttkb.Button(data_load_xyyy_frame, text="Load Data (XYYY)", bootstyle="primary", command=self.load_and_modify_data)
        self.load_button_modified.grid(row=0, column=0, pady=5, padx=5, sticky="ew")

        self.drop_area_xyyy = ttkb.Label(data_load_xyyy_frame, text="Drag & Drop File Here (XYYY)", relief="ridge", bootstyle="info", padding=10, anchor="center")
        self.drop_area_xyyy.grid(row=1, column=0, pady=5, padx=5, sticky="ew")
        self.drop_area_xyyy.drop_target_register(DND_FILES)
        self.drop_area_xyyy.dnd_bind('<<Drop>>', self.on_drop_xyyy)

        # Data Load section (Box Data)
        data_load_box_frame = ttkb.LabelFrame(main_frame, text="Data Load (Box Data)", padding="10 10 10 10")
        data_load_box_frame.grid(row=0, column=2, padx=10, pady=10, sticky="ew")

        self.load_button_labels = ttkb.Button(data_load_box_frame, text="Load Box Data", bootstyle="primary", command=self.load_data_boxplot)
        self.load_button_labels.grid(row=0, column=0, pady=5, padx=5, sticky="ew")

        self.drop_area_box = ttkb.Label(data_load_box_frame, text="Drag & Drop File Here (Box)", relief="ridge", bootstyle="info", padding=10, anchor="center")
        self.drop_area_box.grid(row=1, column=0, pady=5, padx=5, sticky="ew")
        self.drop_area_box.drop_target_register(DND_FILES)
        self.drop_area_box.dnd_bind('<<Drop>>', self.on_drop_box)

        # Labels for Data Sets
        self.label_frame = ttkb.LabelFrame(main_frame, text="Data Set Labels (LaTeX format)", padding="10 10 10 10")
        self.label_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

        # Settings for Style and Font Size
        settings_frame = ttkb.LabelFrame(main_frame, text="Settings", padding="10 10 10 10")
        settings_frame.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

        # BoxStyle selection
        self.Boxstyle_label = ttkb.Label(settings_frame, text="Select Box Style:")
        self.Boxstyle_label.grid(row=0, column=0, pady=5, padx=5, sticky="w")
        
        self.Boxstyle_var = tk.StringVar(value="PCE")
        self.Boxstyle_menu = ttkb.Combobox(settings_frame, textvariable=self.Boxstyle_var, values=["PCE", "Voc", "Jsc", "FF"])
        self.Boxstyle_menu.grid(row=0, column=1, pady=5, padx=5, sticky="w")

        # Style selection
        self.style_label = ttkb.Label(settings_frame, text="Select Style:")
        self.style_label.grid(row=1, column=0, pady=5, padx=5, sticky="w")
        
        self.style_var = tk.StringVar(value="PL")
        self.style_menu = ttkb.Combobox(settings_frame, textvariable=self.style_var, values=["PL", "Raman", "I-V", "TRPL", "Transmittance", "Absorbance", "XRD", "KPFM", "PYS", "EQE", "Thickness"])
        self.style_menu.grid(row=1, column=1, pady=5, padx=5, sticky="w")
        
        # Font Size selection
        self.font_size_label = ttkb.Label(settings_frame, text="Select Font Size:")
        self.font_size_label.grid(row=2, column=0, pady=5, padx=5, sticky="w")
        
        self.font_size_var = tk.StringVar(value="18")
        self.font_size_menu = ttkb.Combobox(settings_frame, textvariable=self.font_size_var, values=["14", "16", "18", "20", "22", "24"])
        self.font_size_menu.grid(row=2, column=1, pady=5, padx=5, sticky="w")

        # Axis Shift and Scale settings
        axis_settings_frame = ttkb.LabelFrame(main_frame, text="Axis Settings", padding="10 10 10 10")
        axis_settings_frame.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

        # X and Y Offset settings
        self.shift_x_label = ttkb.Label(axis_settings_frame, text="Add X-data by:")
        self.shift_x_label.grid(row=0, column=0, pady=5, padx=5, sticky="w")
        self.shift_x_var = tk.DoubleVar(value=0.0)
        self.shift_x_entry = ttkb.Entry(axis_settings_frame, textvariable=self.shift_x_var)
        self.shift_x_entry.grid(row=0, column=1, pady=5, padx=5, sticky="w")

        self.shift_y_label = ttkb.Label(axis_settings_frame, text="Add Y-data by:")
        self.shift_y_label.grid(row=1, column=0, pady=5, padx=5, sticky="w")
        self.shift_y_var = tk.DoubleVar(value=0.0)
        self.shift_y_entry = ttkb.Entry(axis_settings_frame, textvariable=self.shift_y_var)
        self.shift_y_entry.grid(row=1, column=1, pady=5, padx=5, sticky="w")

        self.times_x_label = ttkb.Label(axis_settings_frame, text="Multiply X-data by:")
        self.times_x_label.grid(row=0, column=2, pady=5, padx=5, sticky="w")
        self.times_x_var = tk.DoubleVar(value=1.0)
        self.times_x_entry = ttkb.Entry(axis_settings_frame, textvariable=self.times_x_var)
        self.times_x_entry.grid(row=0, column=3, pady=5, padx=5, sticky="w")

        self.times_y_label = ttkb.Label(axis_settings_frame, text="Multiply Y-data by:")
        self.times_y_label.grid(row=1, column=2, pady=5, padx=5, sticky="w")
        self.times_y_var = tk.DoubleVar(value=1.0)
        self.times_y_entry = ttkb.Entry(axis_settings_frame, textvariable=self.times_y_var)
        self.times_y_entry.grid(row=1, column=3, pady=5, padx=5, sticky="w")

        # Plot and Save Buttons
        action_frame = ttkb.LabelFrame(main_frame, text="Actions", padding="10 10 10 10")
        action_frame.grid(row=4, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

        # Row 1: Main Action Buttons
        self.plot_button = ttkb.Button(action_frame, text="Plot Data", bootstyle="success-outline", command=self.plot_data)
        self.plot_button.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        self.boxplot_button = ttkb.Button(action_frame, text="Plot Boxplot", bootstyle="success-outline", command=self.plot_boxplot)
        self.boxplot_button.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        self.save_button = ttkb.Button(action_frame, text="Save Plot", bootstyle="warning-outline", command=self.save_plot)
        self.save_button.grid(row=0, column=2, padx=10, pady=5, sticky="ew")

        # Row 2: Additional Save and Load Buttons
        self.save_data_button = ttkb.Button(action_frame, text="Save Raw Data", bootstyle="secondary-outline", command=self.save_plot_data)
        self.save_data_button.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        self.load_data_button = ttkb.Button(action_frame, text="Load Raw Data", bootstyle="info-outline", command=self.load_plot_data)
        self.load_data_button.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        # Spacer for Alignment
        action_frame.grid_columnconfigure(2, weight=1)  # Ensures the last button aligns well in the grid


    def show_widgets(self):
        # Show the widgets
        self.style_label.grid()
        self.style_menu.grid()
        self.font_size_label.grid()
        self.font_size_menu.grid()
        self.shift_x_label.grid()
        self.shift_x_entry.grid()
        self.shift_y_label.grid()
        self.shift_y_entry.grid()
        self.times_x_label.grid()
        self.times_x_entry.grid()
        self.times_y_label.grid()
        self.times_y_entry.grid()
        self.plot_button.grid()
        self.save_button.grid()
        self.Boxstyle_label.grid()
        self.Boxstyle_menu.grid()
        self.boxplot_button.grid()

    def configure_xy_view(self):
        # 设置 XY 图的特定显示元素
        self.show_widgets()
        self.boxplot_button.grid_remove()
        self.Boxstyle_label.grid_remove()
        self.Boxstyle_menu.grid_remove()
        # 添加其他 XY 图相关的 UI 配置

    def configure_box_view(self):
        # 设置 Box Plot 的特定显示元素
        self.show_widgets()
        self.style_label.grid_remove()
        self.style_menu.grid_remove()
        self.shift_x_label.grid_remove()
        self.shift_x_entry.grid_remove()
        self.shift_y_label.grid_remove()
        self.shift_y_entry.grid_remove()
        self.times_x_label.grid_remove()
        self.times_x_entry.grid_remove()
        self.times_y_label.grid_remove()
        self.times_y_entry.grid_remove()
        self.plot_button.grid_remove()

    def load(self, file_path):
        # 根据文件扩展名选择加载方法
        if file_path.endswith('.txt'):
            # 使用 pandas 读取 txt 文件，支持不同行列数并填充缺失值
            self.data = pd.read_csv(file_path, delim_whitespace=True, header=None)
        elif file_path.endswith(('.xls', '.xlsx')):
            # 使用 pandas 读取 Excel 文件
            self.data = pd.read_excel(file_path, header=None)
        else:
            raise ValueError("Unsupported file format")
                
    # 处理 XYXY 文件拖放
    def on_drop_xyxy(self, event):
        file_path = event.data.strip('{}')  # 处理拖放的文件路径
        if file_path.endswith((".txt", ".xls", ".xlsx")):
            try:
                self.load(file_path)
                self.create_label_entries()
                messagebox.showinfo("Load Complete", f"Data loaded from {file_path} successfully.")
                self.configure_xy_view()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load data from {file_path}: {e}")
        else:
            messagebox.showerror("Error", "Please drop a valid .txt file")

    # 处理 XYYY 文件拖放
    def on_drop_xyyy(self, event):
        file_path = event.data.strip('{}')
        if file_path.endswith((".txt", ".xls", ".xlsx")):
            try:
                self.load(file_path)
                # 获取第一列和剩余的列
                first_col = self.data.iloc[:, 0]
                data = self.data.iloc[:, 1:]

                # 动态组合数据，使第一列重复并与每一列组合
                new_data = pd.concat([first_col] * data.shape[1] + [data[col] for col in data.columns], axis=1)

                # 将 new_data 存储到 self.data
                self.data = new_data
                
                self.create_label_entries()
                messagebox.showinfo("Load and Modify Complete", f"Data loaded and modified from {file_path} successfully.")
                self.configure_xy_view()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load and modify data from {file_path}: {e}")
        else:
            messagebox.showerror("Error", "Please drop a valid .txt file")

    # 处理 Box Data 文件拖放
    def on_drop_box(self, event):
        file_path = event.data.strip('{}')
        if file_path.endswith((".txt", ".xls", ".xlsx")):
            try:
                self.load(file_path)
                if self.data.ndim == 1:
                    self.data = self.data.reshape(-1, 1)
                self.create_label_entries_boxplot()
                messagebox.showinfo("Load Complete", f"Box data loaded from {file_path} successfully.")
                self.configure_box_view()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load box data from {file_path}: {e}")
        else:
            messagebox.showerror("Error", "Please drop a valid .txt file")

    def load_data(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("Excel files", "*.xls;*.xlsx")])
        if file_path:
            try:
                self.load(file_path)
                self.create_label_entries()
                messagebox.showinfo("Load Complete", "Data loaded successfully. Please set labels for each data set.")
                self.configure_xy_view()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load data: {e}")

    def load_and_modify_data(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            try:
                self.load(file_path)
                # 获取第一列和剩余的列
                first_col = self.data.iloc[:, 0]
                data = self.data.iloc[:, 1:]

                # 动态组合数据，使第一列重复并与每一列组合
                new_data = pd.concat([first_col] * data.shape[1] + [data[col] for col in data.columns], axis=1)

                # 将 new_data 存储到 self.data
                self.data = new_data
                
                self.create_label_entries()
                messagebox.showinfo("Load and Modify Complete", "Data loaded and modified successfully. Please set labels for each data set.")
                self.configure_xy_view()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load and modify data: {e}")

    def load_data_boxplot(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            try:
                self.load(file_path)
                if self.data.ndim == 1:
                    self.data = self.data.reshape(-1, 1)
                self.create_label_entries_boxplot()
                messagebox.showinfo("Load Complete", "Data loaded successfully. Please set labels for each data set.")
                self.configure_box_view()
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
            times_x = self.times_x_var.get()
            times_y = self.times_y_var.get()
            self.fig, ax = plt.subplots()  # Create a figure and an axis
            
            # 更新字体大小
            font_size = int(self.font_size_var.get())
            rcParams.update({'font.size': font_size})

            for i in range(0, self.data.shape[1], 2):
                if self.plot_flags[i // 2].get():  # 检查是否选择绘制
                    x = self.data.iloc[:, i]*times_x + shift_x
                    y = self.data.iloc[:, i + 1]*times_y + shift_y
                    label = labels[i // 2]
                    ax.plot(x, y, label=label)   

            # Set axis labels based on selected style
            style = self.style_var.get()
            style_labels = {
                "PL": (r"$\mathrm{Wavelength\ (nm)}$", r"$\mathrm{Intensity\ (a.u.)}$"),
                "Raman": (r"$\mathrm{Raman\ Shift\ (cm^{-1})}$", r"$\mathrm{Intensity\ (a.u.)}$"),
                "I-V": (r"$\mathrm{Voltage\ (mV)}$", r"$\mathrm{Current\ density\ (mA/cm^{2})}$"),
                "TRPL": (r"$\mathrm{Time\ (ns)}$", r"$\mathrm{Intensity\ (a.u.)}$"),
                "Transmittance": (r"$\mathrm{Wavelength\ (nm)}$", r"$\mathrm{Transmittance\ (\%)}$"),
                "Absorbance": (r"$\mathrm{Wavelength\ (nm)}$", r"$\mathrm{Absorbance\ (a.u.)}$"),
                "XRD": (r"$2\theta\ \mathrm{(degrees)}$", r"$\mathrm{Intensity\ (a.u.)}$"),
                "KPFM": (r"$\mathrm{Voltage\ (V)}$", r"$\mathrm{Counts}$"),
                "PYS": (r"$\mathrm{Photon\ energy\ (eV)}$", r"$\mathrm{Yield^{1/3}}$"),
                "EQE": (r"$\mathrm{Wavelength\ (nm)}$", r"$\mathrm{EQE}$"),
                "Thickness": (r"$\mathrm{Length\ (\mu m)}$", r"$\mathrm{Height\ (\mu m)}$")
            }
    
            ax.set_xlabel(style_labels[style][0], fontsize=font_size)
            ax.set_ylabel(style_labels[style][1], fontsize=font_size)
    
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
            selected_data = [self.data.iloc[:, i].fillna(self.data.iloc[:, i].median()) for i in range(self.data.shape[1]) if self.plot_flags[i].get()]
            
            if not selected_data:
                messagebox.showerror("Error", "No data selected for plotting.")
                return
            
            filtered_data = pd.concat(selected_data, axis=1)

            # 获取对应的标签
            labels = [self.label_entries[i].get() if self.label_entries[i].get() else f"Data Set {i + 1}" for i in range(self.data.shape[1]) if self.plot_flags[i].get()]
            
            self.fig, ax = plt.subplots()
            
            # 更新字体大小
            font_size = int(self.font_size_var.get())
            rcParams.update({'font.size': font_size})
            
            ax.boxplot(filtered_data, tick_labels=labels)
            
            # 根据选择的样式设置轴标签
            style = self.Boxstyle_var.get()
            style_labels = {
                "PCE": r"$\mathrm{PCE\ (\%)}$",
                "Voc": r"$\mathrm{V_{OC}\ (mV)}$",
                "Jsc": r"$\mathrm{J_{SC}\ (mA/cm^{2})}$",
                "FF": r"$\mathrm{FF}$"
            }
    
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
            file_path = filedialog.asksaveasfilename(
    defaultextension=".png", 
    filetypes=[
        ("PNG files", "*.png"),
        ("JPEG files", "*.jpg;*.jpeg"),
        ("BMP files", "*.bmp"),
        ("TIFF files", "*.tiff;*.tif"),
        ("GIF files", "*.gif"),
        ("PDF files", "*.pdf")
    ]
)
            if file_path:
                self.fig.savefig(file_path, dpi=1200)
                messagebox.showinfo("Save Complete", "Plot has been saved")
        else:
            messagebox.showerror("Error", "Please load data and plot it first")

    # 添加保存数据方法
    def save_plot_data(self):
        if self.data is not None:
            # Collect plot data, labels, and settings for all plot types
            plot_data = {
                "data": self.data,
                "labels": [entry.get() if entry.get() else f"Data Set {i + 1}" for i, entry in enumerate(self.label_entries)],
                "shift_x": self.shift_x_var.get(),
                "shift_y": self.shift_y_var.get(),
                "times_x": self.times_x_var.get(),
                "times_y": self.times_y_var.get(),
                "font_size": self.font_size_var.get(),
                "style": self.style_var.get(),
                "Boxstyle": self.Boxstyle_var.get(),
                "plot_flags": [flag.get() for flag in self.plot_flags],
                "plot_type": "boxplot" if hasattr(self, 'boxplot_button') and self.boxplot_button.winfo_ismapped() else "line"
            }

            # Open file dialog to select save location
            file_path = filedialog.asksaveasfilename(defaultextension=".pkl", filetypes=[("Pickle files", "*.pkl")])
            if file_path:
                # Use pickle to save data
                with open(file_path, "wb") as f:
                    pickle.dump(plot_data, f)
                messagebox.showinfo("Save Successful", f"Plot data has been saved to {file_path}")

    # 添加加载数据方法
    def load_plot_data(self):
        # Open file dialog to select the file to load
        file_path = filedialog.askopenfilename(filetypes=[("Pickle files", "*.pkl")])
        if file_path and os.path.exists(file_path):
            # Use pickle to load data
            with open(file_path, "rb") as f:
                plot_data = pickle.load(f)

            # Restore plot data and settings
            self.data = plot_data["data"]
            self.shift_x_var.set(plot_data.get("shift_x", 0.0))
            self.shift_y_var.set(plot_data.get("shift_y", 0.0))
            self.times_x_var.set(plot_data.get("times_x", 1.0))
            self.times_y_var.set(plot_data.get("times_y", 1.0))
            self.font_size_var.set(plot_data.get("font_size", "18"))
            self.style_var.set(plot_data.get("style", "PL"))
            self.Boxstyle_var.set(plot_data.get("Boxstyle", "PCE"))

            # Restore labels and plot flags
            plot_type = plot_data.get("plot_type", "line")
            if plot_type == "boxplot":
                self.create_label_entries_boxplot()  # Use boxplot-specific method
                self.configure_box_view()  # Configure view for boxplot
            else:
                self.create_label_entries()  # Use line plot-specific method
                self.configure_xy_view()  # Configure view for line plot

            for i, entry in enumerate(self.label_entries):
                entry.insert(0, plot_data["labels"][i])
            for i, flag in enumerate(self.plot_flags):
                flag.set(plot_data["plot_flags"][i])

            messagebox.showinfo("Load Successful", f"Plot data has been loaded from {file_path}")

if __name__ == "__main__":
    app = DataPlotter()  # 启动应用
    app.mainloop()
