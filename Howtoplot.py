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

# 全局配置字体属性
rcParams.update({
    'font.size': 18,
    'text.usetex': False,
    'font.family': 'serif',
    'font.serif': ['Times New Roman']
})

class DataPlotter(TkinterDnD.Tk):  # 继承 TkinterDnD 以支持拖放
    def __init__(self):
        super().__init__()
        self.title("Howtoplot")
        self.style = ttkb.Style("flatly")  # 选择一个现代化主题
        self.style.configure("TButton", font=("Arial", 13))  # 设置 TButton 的全局字体
        self.style.configure("TLabel", font=("Arial", 13))   # 设置 TLabel 的全局字体

        self.geometry("800x550")

        # 设置界面全局字体大小
        self.option_add("*Font", "Arial 13")
        
        self.data = None
        self.label_entries = []
        self.plot_flags = []  # 用于存储 Checkbutton 的状态
        self.fig = None  # To store the figure object
        
        # 创建主框架
        main_frame = ttkb.Frame(self, padding="10 10 10 10")
        main_frame.pack(fill="both", expand=True)

        # 加载数据按钮 (XYXY)
        self.load_button = ttkb.Button(main_frame, text="Load Data (XYXY)", bootstyle="primary", command=self.load_data)
        self.load_button.grid(row=0, column=0, pady=5, padx=5, sticky=tk.EW)

        # 拖放区域 (XYXY)
        self.drop_area_xyxy = ttkb.Label(main_frame, text="Drag file here (XYXY)", relief="ridge", bootstyle="info", padding=5, anchor="center")
        self.drop_area_xyxy.grid(row=1, column=0, pady=5, padx=5, ipady=10, sticky=tk.EW)
        self.drop_area_xyxy.drop_target_register(DND_FILES)  # 注册为拖放目标
        self.drop_area_xyxy.dnd_bind('<<Drop>>', self.on_drop_xyxy)  # 绑定拖放事件

        # 加载数据按钮 (XYYY)
        self.load_button_modified = ttkb.Button(main_frame, text="Load Data (XYYY)", bootstyle="primary", command=self.load_and_modify_data)
        self.load_button_modified.grid(row=0, column=1, pady=5, padx=5, sticky=tk.EW)

        # 拖放区域 (XYYY)
        self.drop_area_xyyy = ttkb.Label(main_frame, text="Drag file here (XYYY)", relief="ridge", bootstyle="info", padding=5, anchor="center")
        self.drop_area_xyyy.grid(row=1, column=1, pady=5, padx=5, ipady=10, sticky=tk.EW)
        self.drop_area_xyyy.drop_target_register(DND_FILES)
        self.drop_area_xyyy.dnd_bind('<<Drop>>', self.on_drop_xyyy)

        # 加载数据按钮 (Box Data)
        self.load_button_labels = ttkb.Button(main_frame, text="Load Box Data", bootstyle="primary", command=self.load_data_boxplot)
        self.load_button_labels.grid(row=0, column=2, pady=5, padx=5, sticky=tk.EW)

        # 拖放区域 (Box Data)
        self.drop_area_box = ttkb.Label(main_frame, text="Drag file here (Box)", relief="ridge", bootstyle="info", padding=5, anchor="center")
        self.drop_area_box.grid(row=1, column=2, pady=5, padx=5, ipady=10, sticky=tk.EW)
        self.drop_area_box.drop_target_register(DND_FILES)
        self.drop_area_box.dnd_bind('<<Drop>>', self.on_drop_box)

        # 标签输入框架
        self.label_frame = ttkb.Labelframe(main_frame, text="Data Set Labels (LaTeX format)", padding="10 10 10 10")
        self.label_frame.grid(row=2, column=0, columnspan=3, pady=5, padx=5, sticky=(tk.W, tk.E))

        # BoxStyle选择
        self.Boxstyle_label = ttkb.Label(main_frame, text="Select Box Style:")
        self.Boxstyle_label.grid(row=4, column=0, pady=5, padx=5, sticky=tk.W)
        
        self.Boxstyle_var = tk.StringVar(value="PCE")
        self.Boxstyle_menu = ttkb.Combobox(main_frame, textvariable=self.Boxstyle_var, values=["PCE", "Voc", "Jsc", "FF"])
        self.Boxstyle_menu.grid(row=4, column=1, pady=5, padx=5, sticky=tk.W)

        # 样式选择
        self.style_label = ttkb.Label(main_frame, text="Select Style:")
        self.style_label.grid(row=5, column=0, pady=5, padx=5, sticky=tk.W)
        
        self.style_var = tk.StringVar(value="PL")
        self.style_menu = ttkb.Combobox(main_frame, textvariable=self.style_var, values=["PL", "Raman", "I-V", "TRPL", "Transmittance", "Absorbance", "XRD", "KPFM", "PYS", "EQE", "Thickness"])
        self.style_menu.grid(row=5, column=1, pady=5, padx=5, sticky=tk.W)
        
        # 字体大小选择
        self.font_size_label = ttkb.Label(main_frame, text="Select Font Size:")
        self.font_size_label.grid(row=6, column=0, pady=5, padx=5, sticky=tk.W)
        
        self.font_size_var = tk.StringVar(value="18")
        self.font_size_menu = ttkb.Combobox(main_frame, textvariable=self.font_size_var, values=["14", "16", "18", "20", "22", "24"])
        self.font_size_menu.grid(row=6, column=1, pady=5, padx=5, sticky=tk.W)

        # 坐标轴偏移选项
        self.shift_x_label = ttkb.Label(main_frame, text="Add X-data by:")
        self.shift_x_label.grid(row=4, column=2, pady=5, padx=5, sticky=tk.W)
        
        self.shift_x_var = tk.DoubleVar(value=0.0)
        self.shift_x_entry = ttkb.Entry(main_frame, textvariable=self.shift_x_var)
        self.shift_x_entry.grid(row=4, column=3, pady=5, padx=5, sticky=(tk.W, tk.E))
        
        self.shift_y_label = ttkb.Label(main_frame, text="Add Y-data by:")
        self.shift_y_label.grid(row=5, column=2, pady=5, padx=5, sticky=tk.W)
        
        self.shift_y_var = tk.DoubleVar(value=0.0)
        self.shift_y_entry = ttkb.Entry(main_frame, textvariable=self.shift_y_var)
        self.shift_y_entry.grid(row=5, column=3, pady=5, padx=5, sticky=(tk.W, tk.E))

        # 坐标轴倍数选项
        self.times_x_label = ttkb.Label(main_frame, text="Multiply X-data by:")
        self.times_x_label.grid(row=6, column=2, pady=5, padx=5, sticky=tk.W)
        
        self.times_x_var = tk.DoubleVar(value=1.0)  # 默认倍数设置为 1.0 表示无缩放
        self.times_x_entry = ttkb.Entry(main_frame, textvariable=self.times_x_var)
        self.times_x_entry.grid(row=6, column=3, pady=5, padx=5, sticky=(tk.W, tk.E))
        
        self.times_y_label = ttkb.Label(main_frame, text="Multiply Y-data by:")
        self.times_y_label.grid(row=7, column=2, pady=5, padx=5, sticky=tk.W)
        
        self.times_y_var = tk.DoubleVar(value=1.0)  # 默认倍数设置为 1.0 表示无缩放
        self.times_y_entry = ttkb.Entry(main_frame, textvariable=self.times_y_var)
        self.times_y_entry.grid(row=7, column=3, pady=5, padx=5, sticky=(tk.W, tk.E))


        # 绘图按钮
        self.plot_button = ttkb.Button(main_frame, text="Plot Data", bootstyle="success", command=self.plot_data)
        self.plot_button.grid(row=10, column=0, pady=5, padx=5, sticky=tk.W)
        
        # 保存图像按钮
        self.save_button = ttkb.Button(main_frame, text="Save Plot", bootstyle="warning", command=self.save_plot)
        self.save_button.grid(row=10, column=2, pady=5, padx=5, sticky=tk.W)

        # Boxplot按钮
        self.boxplot_button = ttkb.Button(main_frame, text="Plot Boxplot", bootstyle="success", command=self.plot_boxplot)
        self.boxplot_button.grid(row=10, column=1, pady=5, padx=5, sticky=tk.W)

        # 保存绘图数据按钮
        self.save_data_button = ttkb.Button(main_frame, text="Save Raw Data", bootstyle="warning", command=self.save_plot_data)
        self.save_data_button.grid(row=11, column=2, pady=5, padx=5, sticky=tk.W)

        # 加载绘图数据按钮
        self.load_data_button = ttkb.Button(main_frame, text="Load Raw Data", bootstyle="info", command=self.load_plot_data)
        self.load_data_button.grid(row=11, column=0, pady=5, padx=5, sticky=tk.W)


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
        self.boxplot_button.grid_remove()
        self.Boxstyle_label.grid_remove()
        self.Boxstyle_menu.grid_remove()
        # 添加其他 XY 图相关的 UI 配置

    def configure_box_view(self):
        # 设置 Box Plot 的特定显示元素
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
                self.show_widgets()
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
                self.show_widgets()
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
                self.show_widgets()
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
                self.show_widgets()
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
                self.show_widgets()
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
                self.show_widgets()
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
            # 收集绘图数据、标签和设置
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
                "plot_flags": [flag.get() for flag in self.plot_flags]
            }
            
            # 打开文件对话框选择保存位置
            file_path = filedialog.asksaveasfilename(defaultextension=".pkl", filetypes=[("Pickle files", "*.pkl")])
            if file_path:
                # 使用pickle保存数据
                with open(file_path, "wb") as f:
                    pickle.dump(plot_data, f)
                messagebox.showinfo("保存成功", f"绘图数据已保存到 {file_path}")

    # 添加加载数据方法
    def load_plot_data(self):
        # 打开文件对话框选择要加载的文件
        file_path = filedialog.askopenfilename(filetypes=[("Pickle files", "*.pkl")])
        if file_path and os.path.exists(file_path):
            # 使用pickle加载数据
            with open(file_path, "rb") as f:
                plot_data = pickle.load(f)

            # 恢复绘图数据和设置
            self.data = plot_data["data"]
            self.shift_x_var.set(plot_data["shift_x"])
            self.shift_y_var.set(plot_data["shift_y"])
            self.times_x_var.set(plot_data["times_x"])
            self.times_y_var.set(plot_data["times_y"])
            self.font_size_var.set(plot_data["font_size"])
            self.style_var.set(plot_data["style"])
            self.Boxstyle_var.set(plot_data["Boxstyle"])

            # 重建标签和复选框
            self.create_label_entries()  # 或根据需要调用 create_label_entries_boxplot()
            for i, entry in enumerate(self.label_entries):
                entry.insert(0, plot_data["labels"][i])
            for i, flag in enumerate(self.plot_flags):
                flag.set(plot_data["plot_flags"][i])

            messagebox.showinfo("加载成功", f"绘图数据已从 {file_path} 加载")


if __name__ == "__main__":
    app = DataPlotter()  # 启动应用
    app.mainloop()
