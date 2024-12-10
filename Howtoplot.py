import tkinter as tk
from tkinter import filedialog, messagebox, Canvas, Scrollbar
import ttkbootstrap as ttkb  # 使用 ttkbootstrap 使 UI 更现代化
from tkinterdnd2 import TkinterDnD, DND_FILES  # 导入 TkinterDnD 库，用于实现拖放功能
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import rcParams
import matplotlib
matplotlib.use('Qt5Agg')
import pickle
import os
import ctypes
ctypes.windll.shcore.SetProcessDpiAwareness(0)  # 解决缩放
from tksheet import Sheet
import json

# Global font configuration for plots
rcParams.update({
    'font.size': 16,
    'text.usetex': True,
    'font.family': 'serif',
    'font.serif': ['Computer Modern']
})

class DataPlotter(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("Howtoplot")
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{screen_width}x{screen_height}")
        self.state('zoomed')  # 窗口启动时最大化
        self.style = ttkb.Style("flatly")  # 使用现代主题
        
        # 添加菜单栏
        self.menu_bar = tk.Menu(self)
        self.config(menu=self.menu_bar)

        # 创建 "File" 菜单
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save Plot (1200 DPI)", command=self.save_plot)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)

        # 创建 "Load" 菜单
        load_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Load", menu=load_menu)
        load_menu.add_command(label="Load Data (XYXY)", command=self.load_data)
        load_menu.add_command(label="Load Data (XYYY)", command=self.load_and_modify_data)
        load_menu.add_command(label="Load Data (Boxplot)", command=self.load_data_boxplot)
        load_menu.add_command(label="Load Data (Matrix)", command=self.load_data_matrix)
        
        # 创建 "Plot" 菜单
        plot_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Plot", menu=plot_menu)
        plot_menu.add_command(label="Plot XY Data", command=self.plot_data)
        plot_menu.add_command(label="Plot Boxplot", command=self.plot_boxplot)
        plot_menu.add_command(label="Plot Violinplot", command=self.plot_violinplot)
        plot_menu.add_command(label="Plot Heatmap (Matrix)", command=self.plot_heatmap)
        plot_menu.add_separator()
        plot_menu.add_command(label="Plot from json", command=self.json_plot)
        plot_menu.add_separator()
        plot_menu.add_command(label="Group Figure", command=self.plot_composite_figure)

        # 创建代码导出
        export_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Export", menu=export_menu)
        export_menu.add_command(label="Export Plot Code", command=self.export_plot_code)

        # 创建 "Help" 菜单
        help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Manual", command=self.manual) 
        help_menu.add_command(label="About Howtoplot", command=self.about)
        
        # 设置部件的默认字体和样式
        self.style.configure('.', font=("Arial", 12))
        self.tk.call('tk', 'scaling', 1.25)  # 高DPI适配

        # 使用 grid 布局主框架
        main_frame = ttkb.Frame(self, padding="15 15 15 15")
        main_frame.grid(row=0, column=0, sticky="nsew")

        # 配置根窗口的 grid 权重
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # 配置 main_frame 的 grid 权重
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)

        # 左侧框架用于数据加载和设置
        left_frame = ttkb.Frame(main_frame, padding="10 10 10 10")
        left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # 配置 left_frame 的 grid 权重
        left_frame.grid_rowconfigure(0, weight=1)
        left_frame.grid_rowconfigure(1, weight=1)
        left_frame.grid_rowconfigure(2, weight=1)
        left_frame.grid_rowconfigure(3, weight=1)
        left_frame.grid_rowconfigure(4, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)
        left_frame.grid_columnconfigure(1, weight=1)
        left_frame.grid_columnconfigure(2, weight=1)

        # 数据加载部分 (XYXY)
        data_load_frame = ttkb.LabelFrame(left_frame, text="Data Load (XYXY)", padding="10 10 10 10")
        data_load_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # 配置 data_load_frame 的 grid 权重
        data_load_frame.grid_rowconfigure(0, weight=1)
        data_load_frame.grid_columnconfigure(0, weight=1)

        # 删除按钮，保留拖入功能
        self.drop_area_xyxy = ttkb.Label(data_load_frame, text="Drag Here (XYXY)", relief="ridge", bootstyle="info", padding=10, anchor="center")
        self.drop_area_xyxy.grid(row=0, column=0, pady=5, padx=5, sticky="nsew")
        self.drop_area_xyxy.drop_target_register(DND_FILES)
        self.drop_area_xyxy.dnd_bind('<<Drop>>', self.on_drop_xyxy)

        # 数据加载部分 (XYYY)
        data_load_xyyy_frame = ttkb.LabelFrame(left_frame, text="Data Load (XYYY)", padding="10 10 10 10")
        data_load_xyyy_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # 配置 data_load_xyyy_frame 的 grid 权重
        data_load_xyyy_frame.grid_rowconfigure(0, weight=1)
        data_load_xyyy_frame.grid_columnconfigure(0, weight=1)

        # 删除按钮，保留拖入功能
        self.drop_area_xyyy = ttkb.Label(data_load_xyyy_frame, text="Drag Here (XYYY)", relief="ridge", bootstyle="info", padding=10, anchor="center")
        self.drop_area_xyyy.grid(row=0, column=0, pady=5, padx=5, sticky="nsew")
        self.drop_area_xyyy.drop_target_register(DND_FILES)
        self.drop_area_xyyy.dnd_bind('<<Drop>>', self.on_drop_xyyy)

        # 数据加载部分 (Box Data)
        data_load_box_frame = ttkb.LabelFrame(left_frame, text="Data Load (Box Data)", padding="10 10 10 10")
        data_load_box_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")

        # 配置 data_load_box_frame 的 grid 权重
        data_load_box_frame.grid_rowconfigure(0, weight=1)
        data_load_box_frame.grid_columnconfigure(0, weight=1)

        # 删除按钮，保留拖入功能
        self.drop_area_box = ttkb.Label(data_load_box_frame, text="Drag Here (Box)", relief="ridge", bootstyle="info", padding=10, anchor="center")
        self.drop_area_box.grid(row=0, column=0, pady=5, padx=5, sticky="nsew")
        self.drop_area_box.drop_target_register(DND_FILES)
        self.drop_area_box.dnd_bind('<<Drop>>', self.on_drop_box)

        # 初始化数据集标签部分
        self.initialize_label_frame(left_frame)

        # 样式和字体大小设置
        settings_frame = ttkb.LabelFrame(left_frame, text="Settings", padding="10 10 10 10")
        settings_frame.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

        # 配置 settings_frame 的 grid 权重
        settings_frame.grid_rowconfigure(0, weight=1)
        settings_frame.grid_rowconfigure(1, weight=1)
        settings_frame.grid_rowconfigure(2, weight=1)
        settings_frame.grid_rowconfigure(3, weight=1)
        settings_frame.grid_columnconfigure(0, weight=1)
        settings_frame.grid_columnconfigure(1, weight=1)

        # BoxStyle 选择
        self.Boxstyle_label = ttkb.Label(settings_frame, text="Select Box Style:")
        self.Boxstyle_label.grid(row=0, column=0, pady=5, padx=5, sticky="w")

        self.Boxstyle_var = tk.StringVar(value="PCE")
        self.Boxstyle_menu = ttkb.Combobox(settings_frame, textvariable=self.Boxstyle_var, values=["PCE", "Voc", "Jsc", "FF"])
        self.Boxstyle_menu.grid(row=0, column=1, pady=5, padx=5, sticky="ew")

        # 样式选择
        self.style_label = ttkb.Label(settings_frame, text="Select Style:")
        self.style_label.grid(row=1, column=0, pady=5, padx=5, sticky="w")

        self.style_var = tk.StringVar(value="PL")
        self.style_menu = ttkb.Combobox(settings_frame, textvariable=self.style_var, values=["PL", "Raman", "I-V", "TRPL", "Transmittance", "Absorbance", "XRD", "KPFM", "PYS", "XPS", "EQE", "Thickness"])
        self.style_menu.grid(row=1, column=1, pady=5, padx=5, sticky="ew")

        # 图例切换复选框
        self.legend_var = tk.BooleanVar(value=True)  # 默认显示图例
        self.legend_checkbutton = ttkb.Checkbutton(settings_frame, text="Show Legend", variable=self.legend_var)
        self.legend_checkbutton.grid(row=3, column=0, pady=5, padx=5, sticky="w")

        # 字体大小选择
        self.font_size_label = ttkb.Label(settings_frame, text="Select Font Size:")
        self.font_size_label.grid(row=2, column=0, pady=5, padx=5, sticky="w")

        self.font_size_var = tk.StringVar(value="18")
        self.font_size_menu = ttkb.Combobox(settings_frame, textvariable=self.font_size_var, values=["14", "16", "18", "20", "22", "24"])
        self.font_size_menu.grid(row=2, column=1, pady=5, padx=5, sticky="ew")

        # 轴偏移和缩放设置
        axis_settings_frame = ttkb.LabelFrame(left_frame, text="Data Settings", padding="10 10 10 10")
        axis_settings_frame.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

        # 配置 axis_settings_frame 的 grid 权重
        axis_settings_frame.grid_rowconfigure(0, weight=1)
        axis_settings_frame.grid_rowconfigure(1, weight=1)
        axis_settings_frame.grid_columnconfigure(0, weight=1)
        axis_settings_frame.grid_columnconfigure(1, weight=1)
        axis_settings_frame.grid_columnconfigure(2, weight=1)
        axis_settings_frame.grid_columnconfigure(3, weight=1)

        # X 和 Y 偏移设置
        self.shift_x_label = ttkb.Label(axis_settings_frame, text="Add X-data by:")
        self.shift_x_label.grid(row=0, column=0, pady=5, padx=5, sticky="w")
        self.shift_x_var = tk.DoubleVar(value=0.0)
        self.shift_x_entry = ttkb.Entry(axis_settings_frame, textvariable=self.shift_x_var)
        self.shift_x_entry.grid(row=0, column=1, pady=5, padx=5, sticky="ew")

        self.shift_y_label = ttkb.Label(axis_settings_frame, text="Add Y-data by:")
        self.shift_y_label.grid(row=1, column=0, pady=5, padx=5, sticky="w")
        self.shift_y_var = tk.DoubleVar(value=0.0)
        self.shift_y_entry = ttkb.Entry(axis_settings_frame, textvariable=self.shift_y_var)
        self.shift_y_entry.grid(row=1, column=1, pady=5, padx=5, sticky="ew")

        self.times_x_label = ttkb.Label(axis_settings_frame, text="Multiply X-data by:")
        self.times_x_label.grid(row=0, column=2, pady=5, padx=5, sticky="w")
        self.times_x_var = tk.DoubleVar(value=1.0)
        self.times_x_entry = ttkb.Entry(axis_settings_frame, textvariable=self.times_x_var)
        self.times_x_entry.grid(row=0, column=3, pady=5, padx=5, sticky="ew")

        self.times_y_label = ttkb.Label(axis_settings_frame, text="Multiply Y-data by:")
        self.times_y_label.grid(row=1, column=2, pady=5, padx=5, sticky="w")
        self.times_y_var = tk.DoubleVar(value=1.0)
        self.times_y_entry = ttkb.Entry(axis_settings_frame, textvariable=self.times_y_var)
        self.times_y_entry.grid(row=1, column=3, pady=5, padx=5, sticky="ew")

        # 右侧框架用于显示 tksheet
        right_frame = ttkb.Frame(main_frame, padding="10 10 10 10")
        right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # 配置 right_frame 的 grid 权重
        right_frame.grid_rowconfigure(0, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)

        # 创建可编辑表格 tksheet
        self.sheet = Sheet(right_frame)
        self.sheet.enable_bindings((
            "single_select", "row_select", "column_select",
            "column_width_resize", "double_click_column_resize",
            "arrowkeys", "right_click_popup_menu", "rc_select",
            "rc_insert_row", "rc_delete_row", "copy", "cut", "paste", "delete", "undo", "edit_cell"
        ))
        self.sheet.grid(row=0, column=0, sticky="nsew")

        # 初始化数据属性
        self.data = None

    def initialize_label_frame(self, parent_frame):
        # 固定大小和滚动条的数据集标签
        self.label_frame = ttkb.LabelFrame(parent_frame, text="Data Set Labels (LaTeX format)", padding="10 10 10 10")
        self.label_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

        # 在 label_frame 内创建一个 Canvas 以实现滚动
        self.label_canvas = Canvas(self.label_frame, height=150)  # 设置固定高度
        self.label_canvas.pack(side="left", fill="both", expand=True)

        # 向 Canvas 添加滚动条
        self.label_scrollbar = Scrollbar(self.label_frame, orient="vertical", command=self.label_canvas.yview)
        self.label_scrollbar.pack(side="right", fill="y")

        # 配置 Canvas 使用滚动条
        self.label_canvas.configure(yscrollcommand=self.label_scrollbar.set)
        self.label_canvas.bind('<Configure>', lambda e: self.label_canvas.configure(scrollregion=self.label_canvas.bbox("all")))

        # 在 Canvas 内创建一个 Frame 用于实际的标签输入部件
        self.label_container = ttkb.Frame(self.label_canvas)
        self.label_canvas.create_window((0, 0), window=self.label_container, anchor="nw")

        # 绑定鼠标滚轮在不同平台上的滚动
        self.label_canvas.bind_all("<MouseWheel>", self._on_mouse_wheel)  # Windows 和 macOS

        # 添加全选/取消全选按钮
        self.select_all_button = ttkb.Button(self.label_frame, text="Select/Deselect All", bootstyle="primary", command=self.toggle_all_checkbuttons)
        self.select_all_button.pack(pady=5)

        # 用于记录当前是否全选的标志
        self.all_selected = True

    def toggle_all_checkbuttons(self):
        """切换所有 Checkbutton 的选中状态"""
        for flag in self.plot_flags:
            flag.set(self.all_selected)
        # 切换全选标志
        self.all_selected = not self.all_selected

    def _on_mouse_wheel(self, event):
        # 根据平台滚动
        self.label_canvas.yview_scroll(-1 * (event.delta // 120), "units")

    def display_data_in_sheet(self):
        if self.data is not None:
            # 在 tksheet 中设置数据
            self.sheet.set_sheet_data(self.data.values.tolist(), reset_col_positions=True, reset_row_positions=True)
            self.sheet.headers(self.data.columns.tolist())
            self.sheet.refresh()
        else:
            messagebox.showwarning("Warning", "No data to display.")

    def update_data_from_sheet(self):
        """从 tksheet 表格中获取更新后的数据并存储到 self.data。"""
        data_from_sheet = self.sheet.get_sheet_data()
        self.data = pd.DataFrame(data_from_sheet, columns=self.data.columns)

    def show_widgets(self):
        # 显示部件
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
        self.Boxstyle_label.grid()
        self.Boxstyle_menu.grid()

    def configure_xy_view(self):
        # 设置 XY 图的特定显示元素
        self.show_widgets()
        self.Boxstyle_label.grid_remove()
        self.Boxstyle_menu.grid_remove()

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

    def load(self, file_path):
        # 保存文件路径为实例变量
        self.current_file_path = file_path  # 保存当前文件路径
        if file_path.endswith('.txt'):
            self.data = pd.read_csv(file_path, delim_whitespace=True, header=None)
        elif file_path.endswith(('.xls', '.xlsx')):
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
                # 显示数据到 tksheet
                self.display_data_in_sheet()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load data from {file_path}: {e}")
        else:
            messagebox.showerror("Error", "Please drop a valid .txt or .xls/.xlsx file")

    # 处理 XYYY 文件拖放
    def on_drop_xyyy(self, event):
        file_path = event.data.strip('{}')
        if file_path:
            try:
                self.load(file_path)
                # 获取第一列 X 和其余的 Y 列
                first_col = self.data.iloc[:, 0]
                data = self.data.iloc[:, 1:]

                # 组合 X 和每一列 Y，生成新的 DataFrame
                combined_data = pd.DataFrame()
                for col in data.columns:
                    combined_data = pd.concat([combined_data, first_col, data[col]], axis=1)

                # 存储新的 DataFrame
                self.data = combined_data

                self.create_label_entries()
                messagebox.showinfo("Load and Modify Complete", "Data loaded and modified successfully. Please set labels for each data set.")
                self.configure_xy_view()
                # 显示数据到 tksheet
                self.display_data_in_sheet()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load and modify data: {e}")

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
                # 显示数据到 tksheet
                self.display_data_in_sheet()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load box data from {file_path}: {e}")
        else:
            messagebox.showerror("Error", "Please drop a valid .txt or .xls/.xlsx file")

    def load_data(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("Excel files", "*.xls;*.xlsx")])
        if file_path:
            try:
                self.load(file_path)
                self.create_label_entries()
                messagebox.showinfo("Load Complete", "Data loaded successfully. Please set labels for each data set.")
                self.configure_xy_view()
                # 显示数据到 tksheet
                self.display_data_in_sheet()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load data: {e}")

    def load_and_modify_data(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("Excel files", "*.xls;*.xlsx")])
        if file_path:
            try:
                self.load(file_path)
                # 获取第一列 X 和其余的 Y 列
                first_col = self.data.iloc[:, 0]
                data = self.data.iloc[:, 1:]

                # 组合 X 和每一列 Y，生成新的 DataFrame
                combined_data = pd.DataFrame()
                for col in data.columns:
                    combined_data = pd.concat([combined_data, first_col, data[col]], axis=1)

                # 存储新的 DataFrame
                self.data = combined_data

                self.create_label_entries()
                messagebox.showinfo("Load and Modify Complete", "Data loaded and modified successfully. Please set labels for each data set.")
                self.configure_xy_view()
                # 显示数据到 tksheet
                self.display_data_in_sheet()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load and modify data: {e}")

    def load_data_boxplot(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("Excel files", "*.xls;*.xlsx")])
        if file_path:
            try:
                self.load(file_path)
                if self.data.ndim == 1:
                    self.data = self.data.reshape(-1, 1)
                self.create_label_entries_boxplot()
                messagebox.showinfo("Load Complete", "Data loaded successfully. Please set labels for each data set.")
                self.configure_box_view()
                # 显示数据到 tksheet
                self.display_data_in_sheet()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load data: {e}")

    def load_data_matrix(self):
        """通过文件选择对话框加载矩阵数据"""
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("Excel files", "*.xls;*.xlsx")])
        if file_path:
            try:
                self.load(file_path)
                if not self.data.ndim == 2:
                    raise ValueError("Matrix data should have two dimensions.")
                messagebox.showinfo("Load Complete", "Matrix data loaded successfully.")
                # 显示数据到 tksheet
                self.display_data_in_sheet()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load matrix data: {e}")

    def create_label_entries(self):
        # 清除先前的标签输入
        for widget in self.label_container.winfo_children():
            widget.destroy()

        self.label_entries = []
        self.plot_flags = []  # 用于存储是否绘制该数据集的标志
        for i in range(0, self.data.shape[1], 2):
            frame = ttkb.Frame(self.label_container)
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
            self.plot_flags.append(plot_flag)
        # 更新 Canvas 的滚动区域
        self.label_canvas.update_idletasks()
        self.label_canvas.config(scrollregion=self.label_canvas.bbox("all"))

    def create_label_entries_boxplot(self):
        # 清除先前的标签输入
        for widget in self.label_container.winfo_children():
            widget.destroy()

        self.label_entries = []
        self.plot_flags = []
        for i in range(0, self.data.shape[1], 1):
            frame = ttkb.Frame(self.label_container)
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
            self.plot_flags.append(plot_flag)
        # 更新 Canvas 的滚动区域
        self.label_canvas.update_idletasks()
        self.label_canvas.config(scrollregion=self.label_canvas.bbox("all"))

    def plot_data(self):
        if self.data is not None:
            # 更新数据
            self.update_data_from_sheet()
            labels = [entry.get() if entry.get() else f"Data Set {index + 1}" for index, entry in enumerate(self.label_entries)]
            shift_x = self.shift_x_var.get()
            shift_y = self.shift_y_var.get()
            times_x = self.times_x_var.get()
            times_y = self.times_y_var.get()
            self.fig, ax = plt.subplots()

            # 更新字体大小
            font_size = int(self.font_size_var.get())
            rcParams.update({'font.size': font_size})

            for i in range(0, self.data.shape[1], 2):
                if self.plot_flags[i // 2].get():
                    x = pd.to_numeric(self.data.iloc[:, i], errors='coerce').fillna(0)*times_x + shift_x
                    y = pd.to_numeric(self.data.iloc[:, i + 1], errors='coerce').fillna(0)*times_y + shift_y
                    label = labels[i // 2]
                    ax.plot(x, y, label=label)

            # 根据样式设置轴标签
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
                "XPS": (r"$\mathrm{Binding\ energy\ (eV)}$", r"$\mathrm{Intensity\ (a.u.)}$"),
                "EQE": (r"$\mathrm{Wavelength\ (nm)}$", r"$\mathrm{EQE}$"),
                "Thickness": (r"$\mathrm{Length\ (\mu m)}$", r"$\mathrm{Height\ (\mu m)}$")
            }

            ax.set_xlabel(style_labels[style][0], fontsize=font_size)
            ax.set_ylabel(style_labels[style][1], fontsize=font_size)

            # 检查是否显示图例
            if self.legend_var.get():
                ax.legend(frameon=False, fontsize=font_size)
            ax.tick_params(axis='both', which='major', width=1, labelsize=font_size)
            ax.tick_params(axis='both', which='minor', width=1, labelsize=font_size)
            ax.minorticks_on()
            plt.tight_layout()
            # 注册事件监听
            self.fig.canvas.mpl_connect('draw_event', self.on_draw)
            plt.show()

        else:
            messagebox.showerror("Error", "Please load data first")

    def plot_boxplot(self):
        if self.data is not None:
            # 更新数据
            self.update_data_from_sheet()
            selected_data = [
                pd.to_numeric(self.data.iloc[:, i], errors='coerce').fillna(self.data.iloc[:, i].median())
                for i in range(self.data.shape[1]) if self.plot_flags[i].get()
            ]
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

            ax.boxplot(filtered_data.values, labels=labels)

            # 根据选择的样式设置轴标签
            style = self.Boxstyle_var.get()
            style_labels = {
                "PCE": r"$\mathrm{PCE\ (\%)}$",
                "Voc": r"$\mathrm{V_{OC}\ (mV)}$",
                "Jsc": r"$\mathrm{J_{SC}\ (mA/cm^{2})}$",
                "FF": r"$\mathrm{FF}$"
            }

            ax.set_ylabel(style_labels.get(style, ""), fontsize=font_size)

            plt.tight_layout()
            # 注册事件监听
            self.fig.canvas.mpl_connect('draw_event', self.on_draw)            
            plt.show()
        else:
            messagebox.showerror("Error", "Please load data first")

    def plot_violinplot(self):
        if self.data is not None:
            # 更新数据
            self.update_data_from_sheet()
            selected_data = [
                pd.to_numeric(self.data.iloc[:, i], errors='coerce').fillna(self.data.iloc[:, i].median())
                for i in range(self.data.shape[1]) if self.plot_flags[i].get()
            ]
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

            # 绘制小提琴图
            parts = ax.violinplot(filtered_data.values, showmeans=False, showmedians=True)

            # 配置小提琴图的其他部分
            for key in ['cmeans', 'cmedians', 'cbars', 'cmaxes', 'cmins']:
                if key in parts:
                    parts[key].set_linewidth(1)

            # 设置 X 轴标签
            ax.set_xticks(range(1, len(labels) + 1))
            ax.set_xticklabels(labels, fontsize=font_size)

            # 根据选择的样式设置 Y 轴标签
            style = self.Boxstyle_var.get()
            style_labels = {
                "PCE": r"$\mathrm{PCE\ (\%)}$",
                "Voc": r"$\mathrm{V_{OC}\ (mV)}$",
                "Jsc": r"$\mathrm{J_{SC}\ (mA/cm^{2})}$",
                "FF": r"$\mathrm{FF}$"
            }

            ax.set_ylabel(style_labels.get(style, ""), fontsize=font_size)

            plt.tight_layout()
            # 注册事件监听
            self.fig.canvas.mpl_connect('draw_event', self.on_draw)
            plt.show()
        else:
            messagebox.showerror("Error", "Please load data first")

    def plot_heatmap(self):
        """绘制热图 (pcolormesh)"""
        if self.data is not None:
            try:
                # 更新数据
                self.update_data_from_sheet()
                data_matrix = self.data.astype(float).values  # 确保数据是浮点型
                self.fig, ax = plt.subplots()

                # 更新字体大小
                font_size = int(self.font_size_var.get())
                rcParams.update({'font.size': font_size})

                # 使用 pcolormesh 绘制
                mesh = ax.pcolormesh(data_matrix, cmap="viridis", shading='auto')
                plt.colorbar(mesh, ax=ax)

                ax.set_xlabel("Columns", fontsize=font_size)
                ax.set_ylabel("Rows", fontsize=font_size)

                plt.tight_layout()
                # 注册事件监听
                self.fig.canvas.mpl_connect('draw_event', self.on_draw)
                plt.show()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to plot heatmap: {e}")
        else:
            messagebox.showerror("Error", "Please load matrix data first")

    def plot_composite_figure(self):
        """功能：实现组图模式"""
        # 创建加载界面
        self.loading_window = tk.Toplevel(self)
        self.loading_window.title("Select Layout and Load JSON Files")
        self.loading_window.geometry("400x300")
        
        # 布局选项
        layout_options = [
            "2x2", "3x1", "1x3", "4x1", "1x4", "3x2", "2x3"
        ]
        layout_var = tk.StringVar(value="2x2")  # 默认布局选项

        # 布局选择下拉菜单
        ttkb.Label(self.loading_window, text="Select Layout:").pack(pady=10)
        layout_menu = ttkb.Combobox(
            self.loading_window,
            textvariable=layout_var,
            values=layout_options,
            state="readonly"
        )
        layout_menu.pack(pady=10)

        # JSON 文件存储
        json_files = []
        buttons_frame = ttkb.Frame(self.loading_window)
        buttons_frame.pack(fill="both", expand=True)

        def update_buttons():
            """根据选择的布局更新按钮"""
            for widget in buttons_frame.winfo_children():
                widget.destroy()  # 清除之前的按钮

            # 解析布局
            try:
                rows, cols = map(int, layout_var.get().split("x"))
            except ValueError:
                messagebox.showerror("Error", "Invalid layout format. Please use 'NxM'.")
                return

            nonlocal json_files
            json_files = [None] * (rows * cols)  # 初始化 JSON 文件存储
            buttons = []

            def load_json_for_position(idx):
                """为特定位置加载 JSON 文件"""
                file_path = filedialog.askopenfilename(
                    title=f"Select JSON for Subplot {idx + 1}",
                    filetypes=[("JSON Files", "*.json")]
                )
                if file_path:
                    json_files[idx] = file_path
                    buttons[idx].config(text=f"Loaded: {os.path.basename(file_path)}")

            for r in range(rows):
                for c in range(cols):
                    idx = r * cols + c
                    button = ttkb.Button(
                        buttons_frame,
                        text=f"Position {idx + 1}",
                        command=lambda idx=idx: load_json_for_position(idx),
                        bootstyle="primary"
                    )
                    button.grid(row=r, column=c, padx=10, pady=10, sticky="nsew")
                    buttons.append(button)

        # 初次更新按钮
        update_buttons()

        # 监听下拉菜单变化，实时更新按钮
        layout_menu.bind("<<ComboboxSelected>>", lambda e: update_buttons())

        # 完成按钮
        def finish_and_plot():
            """完成加载后绘制组图"""
            self.loading_window.destroy()  # 关闭加载窗口

            # 创建组图
            rows, cols = map(int, layout_var.get().split("x"))
            fig, axes = plt.subplots(rows, cols, figsize=(cols * 5, rows * 4))
            axes = axes.flatten() if rows * cols > 1 else [axes]  # 统一处理单图和多图情况

            for idx, ax in enumerate(axes):
                if json_files[idx]:  # 如果用户加载了文件
                    try:
                        # 加载 JSON 文件参数
                        params = self.load_params(json_files[idx])
                        if params:
                            self.apply_params(ax, params)  # 应用参数到子图
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to load plot for Subplot {idx + 1}: {e}")
                else:
                    ax.set_visible(False)  # 如果未加载文件，隐藏子图

            # 调整布局并显示
            plt.tight_layout()
            self.fig = fig  # 保存组图到实例变量
            plt.show()

        ttkb.Button(
            self.loading_window,
            text="Finish and Plot",
            command=finish_and_plot,
            bootstyle="success"
        ).pack(pady=20)



    def save_plot(self):
        if self.data is not None and hasattr(self, 'fig') and self.fig is not None:
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

    def extract_interactive_params(self, ax):
        """
        提取交互后绘图的所有参数，包括坐标轴、线条、图例等。
        """
        # 初始化参数字典
        params = {
            "plot_type": self.detect_plot_type(ax),  # 自动检测绘图类型
            "xlim": list(ax.get_xlim()),
            "ylim": list(ax.get_ylim()),
            "xlabel": ax.get_xlabel(),
            "ylabel": ax.get_ylabel(),
            "title": ax.get_title(),
            "grid": {
                "x": ax.xaxis._major_tick_kw.get('gridOn', False),
                "y": ax.yaxis._major_tick_kw.get('gridOn', False),
            },
            "tick_params": {
                "xticks": ax.get_xticks().tolist(),
                "yticks": ax.get_yticks().tolist(),
                "xticklabels": [label.get_text() for label in ax.get_xticklabels()],
                "yticklabels": [label.get_text() for label in ax.get_yticklabels()],
            },
            "font_size": plt.rcParams['font.size'],
        }

        # 根据类型提取特定内容
        if params["plot_type"] == "lineplot":
            params["lines"] = [
                {
                    "xdata": line.get_xdata().tolist(),
                    "ydata": line.get_ydata().tolist(),
                    "color": line.get_color(),
                    "linestyle": line.get_linestyle(),
                    "linewidth": line.get_linewidth(),
                    "marker": line.get_marker(),
                    "label": line.get_label(),
                }
                for line in ax.get_lines()
            ]
        elif params["plot_type"] == "boxplot":
            params["box_data"] = self.extract_boxplot_data(ax)  # 自定义提取 boxplot 数据

        # 提取 legend 信息
        legend = ax.get_legend()
        if legend is not None:
            params["legend"] = {
                "visible": True,
                "location": legend._loc,
                "fontsize": legend.get_texts()[0].get_fontsize() if legend.get_texts() else None,
                "frameon": legend.get_frame_on(),
                "labels": [text.get_text() for text in legend.get_texts()],
            }
        else:
            params["legend"] = {"visible": False}

        return params


    def extract_boxplot_data(self, ax):
        """
        提取 boxplot 的绘图数据和标签。
        """
        box_data = []
        labels = []
        for child in ax.get_children():
            if isinstance(child, matplotlib.text.Text):  # 检查是否是标签
                labels.append(child.get_text())
        for line in ax.get_lines():
            if line.get_linestyle() == '--':  # 检测中位数线条
                box_data.append(line.get_ydata().tolist())
        return {"data": box_data, "labels": labels}

    def detect_plot_type(self, ax):
        """
        根据绘图的特性检测绘图类型。
        """
        # 如果图中有线条，认为是线图
        if ax.get_lines():
            return "lineplot"
        # 如果图中有箱线图的艺术元素，认为是箱线图
        for child in ax.get_children():
            if isinstance(child, matplotlib.patches.PathPatch):
                return "boxplot"
        # 未知类型
        return "unknown"

    def on_draw(self, event):
        """
        处理交互完成后的绘图事件，提取并保存所有参数。
        """
        try:
            ax = event.canvas.figure.axes[0]  # 获取当前绘图的坐标轴
            params = self.extract_interactive_params(ax)  # 提取参数
            if hasattr(self, 'current_file_path'):
                self.save_params(params, self.current_file_path)  # 使用加载的数据文件路径保存参数
            else:
                self.save_params(params, None)  # 如果没有路径，使用默认文件名保存
        except Exception as e:
            print(f"Error capturing parameters: {e}")


    def save_params(self, params, data_file_path=None):
        """Save captured parameters to a JSON file, with the file name matching the data file name."""
        if data_file_path:
            # Get the base name and directory of the data file
            base_name = os.path.splitext(os.path.basename(data_file_path))[0]
            dir_name = os.path.dirname(data_file_path)
            # Construct the full path for the JSON file in the same directory
            filename = os.path.join(dir_name, f"{base_name}.json")
        else:
            filename = "plot_params.json"  # Default filename if data_file_path is not provided

        try:
            with open(filename, "w") as f:
                json.dump(params, f, indent=4)
            print(f"Parameters saved to {filename}")
        except Exception as e:
            print(f"Error saving parameters: {e}")

    def load_params(self, filename=None):
        """加载保存的绘图参数，支持文件选择"""
        if filename is None:
            # 打开文件选择对话框
            filename = filedialog.askopenfilename(
                title="Select Plot Parameters File",
                filetypes=[("JSON Files", "*.json")]
            )
        if not filename:
            # 用户取消了文件选择
            messagebox.showwarning("Warning", "No file selected. Parameters not loaded.")
            return None

        try:
            with open(filename, "r") as f:
                params = json.load(f)
            return params
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load parameters: {e}")
            return None

    def apply_params(self, ax, params):
        """
        将保存的参数应用到图形
        """
        # 清空轴内容
        ax.clear()

        # 根据绘图类型恢复内容
        if params["plot_type"] == "lineplot":
            for line_params in params["lines"]:
                ax.plot(
                    line_params["xdata"],
                    line_params["ydata"],
                    color=line_params["color"],
                    linestyle=line_params["linestyle"],
                    linewidth=line_params["linewidth"],
                    marker=line_params["marker"],
                    label=line_params["label"]
                )
        elif params["plot_type"] == "boxplot":
            if "box_data" in params:
                data = params["box_data"]["data"]
                tick_labels = params["box_data"]["labels"]  # 使用新的参数名称
                ax.boxplot(data, tick_labels=tick_labels)  # 修改为 tick_labels

        # 恢复 legend 信息
        if params.get("legend", {}).get("visible", False):
            legend_params = params["legend"]
            ax.legend(
                loc=legend_params.get("location", "best"),
                fontsize=legend_params.get("fontsize", params.get("font_size", 12)),
                frameon=legend_params.get("frameon", True)
            )

        # 恢复坐标轴标签和标题
        ax.set_xlabel(params["xlabel"])
        ax.set_ylabel(params["ylabel"])
        ax.set_title(params["title"])

        # 设置网格
        ax.grid(params["grid"]["x"], axis="x")
        ax.grid(params["grid"]["y"], axis="y")

        # 设置刻度
        ax.set_xticks(params["tick_params"]["xticks"])
        ax.set_yticks(params["tick_params"]["yticks"])
        ax.set_xticklabels(params["tick_params"]["xticklabels"])
        ax.set_yticklabels(params["tick_params"]["yticklabels"])
        ax.minorticks_on()
        # 应用坐标轴范围
        if "xlim" in params:
            ax.set_xlim(params["xlim"])
        if "ylim" in params:
            ax.set_ylim(params["ylim"])


    def plot_line(self, ax, params):
        """根据参数绘制线图"""
        for line_params in params.get("lines", []):
            ax.plot(
                line_params["xdata"],
                line_params["ydata"],
                color=line_params["color"],
                linestyle=line_params["linestyle"],
                linewidth=line_params["linewidth"],
                marker=line_params["marker"],
                label=line_params["label"]
            )

        # 添加图例（如果存在）
        if params.get("legend", {}).get("visible", False):
            ax.legend(
                loc=params["legend"].get("location", 'best'),
                fontsize=params["legend"].get("fontsize", params.get('font_size', 12)),
                frameon=params["legend"].get("frameon", True)
            )

    def plot_box(self, ax, params):
        """根据参数绘制箱线图"""
        box_data = params["box_data"]["data"]
        labels = params["box_data"]["labels"]
        ax.boxplot(box_data, labels=labels)

    def json_plot(self):
        """选择并加载 JSON 文件以恢复保存的绘图"""
        file_path = filedialog.askopenfilename(
            title="Select JSON File",
            filetypes=[("JSON Files", "*.json")]
        )
        if file_path:
            try:
                # 加载 JSON 文件中的参数
                params = self.load_params(file_path)
                self.fig, ax = plt.subplots()

                # 应用参数到绘图
                self.apply_params(ax, params)

                plt.tight_layout()
                self.current_file_path = file_path  # 保存当前文件路径
                self.fig.canvas.mpl_connect('draw_event', self.on_draw)
                plt.show()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to restore plot from {file_path}: {e}")
        else:
            messagebox.showinfo("Info", "No file selected.")


    def export_plot_code(self):
        """Generate and export complete Python plotting code that imports data from a JSON file."""
        try:
            # Select JSON file
            json_file_path = filedialog.askopenfilename(
                title="Select JSON File",
                filetypes=[("JSON Files", "*.json")]
            )
            if not json_file_path:
                messagebox.showinfo("Cancelled", "No file selected.")
                return

            # Load parameters from JSON file
            with open(json_file_path, "r", encoding="utf-8") as f:
                params = json.load(f)

            # Ensure parameters are valid
            if not params.get("lines") or len(params["lines"]) == 0:
                raise ValueError("No valid plotting parameters in the JSON file.")

            # Get the base name and directory of the JSON file
            json_file_name = os.path.basename(json_file_path)
            json_dir = os.path.dirname(json_file_path)
            code_file_name = os.path.splitext(json_file_name)[0] + ".py"

            # Generate code that imports data from the JSON file
            code_lines = [
                "import json",
                "import matplotlib.pyplot as plt",
                "",
                f"# Load data from JSON file '{json_file_name}'",
                f"with open('{json_file_name}', 'r', encoding='utf-8') as f:",
                "    params = json.load(f)",
                "",
                "# Set global font size",
                f"plt.rcParams['font.size'] = {params.get('font_size', 12)}",
                "",
                "# Create the plot",
                "fig, ax = plt.subplots()",
                "",
                "# Plot each line",
                "for line_params in params['lines']:",
                "    xdata = line_params['xdata']",
                "    ydata = line_params['ydata']",
                "    label = line_params.get('label', '')",
                "    ax.plot(",
                "        xdata,",
                "        ydata,",
                "        color=line_params.get('color', 'blue'),",
                "        linestyle=line_params.get('linestyle', '-'),",
                "        linewidth=line_params.get('linewidth', 1.5),",
                "        marker=line_params.get('marker', ''),",
                "        label=label",
                "    )",
                "",
                "# Set axis labels and title",
                f"ax.set_xlabel({repr(params['xlabel'])}, fontsize={params.get('font_size', 12)})",
                f"ax.set_ylabel({repr(params['ylabel'])}, fontsize={params.get('font_size', 12)})",
                f"ax.set_title({repr(params['title'])}, fontsize={params.get('font_size', 12)})",
                "",
                "# Set axis limits if they exist",
                "if 'xlim' in params:",
                "    ax.set_xlim(params['xlim'])",
                "if 'ylim' in params:",
                "    ax.set_ylim(params['ylim'])",
                "",
                "# Add grid if specified",
                "if params.get('grid', {}).get('x', False):",
                "    ax.grid(True, axis='x')",
                "if params.get('grid', {}).get('y', False):",
                "    ax.grid(True, axis='y')",
                "",
                "# Set ticks and tick labels if specified",
                "if 'tick_params' in params:",
                "    tick_params = params['tick_params']",
                "    ax.set_xticks(tick_params.get('xticks', []))",
                "    ax.set_yticks(tick_params.get('yticks', []))",
                "    ax.set_xticklabels(tick_params.get('xticklabels', []), fontsize=params.get('font_size', 12))",
                "    ax.set_yticklabels(tick_params.get('yticklabels', []), fontsize=params.get('font_size', 12))",
                "",
                "# Set tick parameters",
                f"ax.tick_params(axis='both', which='major', labelsize={params.get('font_size', 12)})",
                "",
                "# Add legend if specified",
                "if params.get('legend', {}).get('visible', False):",
                "    legend_params = params['legend']",
                "    ax.legend(",
                "        loc=legend_params.get('location', 'best'),",
                "        fontsize=legend_params.get('fontsize', params.get('font_size', 12)),",
                "        frameon=legend_params.get('frameon', True)",
                "    )",
                "",
                "plt.tight_layout()",
                "plt.show()",
            ]

            # Save generated code to file with the same name as JSON file
            save_path = filedialog.asksaveasfilename(
                title="Save Python Code",
                defaultextension=".py",
                initialfile=code_file_name,
                initialdir=json_dir,
                filetypes=[("Python Files", "*.py")]
            )
            if save_path:
                # Copy the JSON file to the same directory as the code file if necessary
                json_destination = os.path.join(os.path.dirname(save_path), json_file_name)
                if not os.path.exists(json_destination):
                    shutil.copy(json_file_path, json_destination)

                with open(save_path, "w", encoding="utf-8") as f:
                    f.write("\n".join(code_lines))
                messagebox.showinfo("Export Completed", f"Code successfully exported to {save_path}")
            else:
                messagebox.showinfo("Export Cancelled", "No file selected.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate plotting code from JSON: {e}")


    def manual(self):
        """Display the user manual"""
        manual_message = (
            "User Manual - Howtoplot\n\n"
            "Overview:\n"
            "Howtoplot is a versatile data plotting tool designed to handle various data formats and generate customizable plots, including line plots, boxplots, violin plots, and heatmaps. It supports drag-and-drop functionality for easy data loading and provides a modern, user-friendly interface.\n\n"
            "Features:\n"
            "1. **Data Loading**:\n"
            "   - **Load Data (XYXY)**: Load data with alternating X and Y columns (e.g., X1, Y1, X2, Y2, ...).\n"
            "   - **Load Data (XYYY)**: Load data with one X column followed by multiple Y columns (e.g., X, Y1, Y2, Y3, ...).\n"
            "   - **Load Data (Boxplot)**: Load data suitable for boxplots.\n"
            "   - **Load Data (Matrix)**: Load matrix data for heatmaps.\n\n"
            "2. **Plotting Functions**:\n"
            "   - **Plot XY Data**: Create line plots using the loaded XY data.\n"
            "   - **Plot Boxplot**: Generate boxplots from the loaded data.\n"
            "   - **Plot Violinplot**: Generate violin plots from the loaded data.\n"
            "   - **Plot Heatmap (Matrix)**: Generate heatmaps based on matrix data.\n"
            "   - **Plot from JSON**: Load plot parameters from a JSON file to recreate a plot.\n\n"
            "3. **Export Functions**:\n"
            "   - **Export Plot Code**: Generate standalone Python plotting code.\n\n"
            "4. **Settings Options**:\n"
            "   - Adjust plot style, font size, data shifts, and scaling factors.\n"
            "   - Toggle the display of legends.\n\n"
            "5. **Data Manipulation**:\n"
            "   - Use a spreadsheet-like interface to view and edit data.\n"
            "   - Set labels for each dataset and select which datasets to plot.\n\n"
            "6. **Drag-and-Drop Functionality**:\n"
            "   - Drag and drop files into designated areas to quickly load data.\n\n"
            "7. **Help**:\n"
            "   - **Manual**: Display this user manual.\n"
            "   - **About Howtoplot**: View information about the application and the author.\n\n"
            "Instructions:\n"
            "- **Loading Data**: Use the 'Load' menu or drag and drop files into the appropriate areas to load your data.\n"
            "- **Editing Data**: After loading, the data will be displayed in a table where you can edit it as needed.\n"
            "- **Setting Labels**: Provide labels for each dataset in the 'Data Set Labels' section. You can also select or deselect datasets for plotting.\n"
            "- **Adjusting Settings**: Use the 'Settings' and 'Data Settings' sections to customize your plot.\n"
            "- **Plotting**: Use the 'Plot' menu to generate the desired plot type.\n"
            "- **Exporting Code**: After plotting, you can export the plotting code using the 'Export' menu.\n"
            "- **Saving Plots**: Use the 'File' menu to save your plot as an image.\n\n"
            "For detailed examples and further assistance, please refer to the documentation or contact support."
        )
        messagebox.showinfo("Manual", manual_message)

    def about(self):
        """显示关于 Howtoplot 的信息"""
        about_message = (
            "Howtoplot\n"
            "Version: 1.0.0\n"
            "Author: Jiaqi Liu\n"
            "Contact: liujiaqi@uec.ac.jp\n\n"
            "Howtoplot is a versatile data plotting tool designed to handle "
            "various data formats and generate customizable plots, including "
            "line plots, boxplots, violin plots, and heatmaps. It supports drag-and-drop "
            "functionality for easy data loading and provides a modern, user-friendly interface.\n\n"
            "For help or more information, please contact the author."
        )
        messagebox.showinfo("About Howtoplot", about_message)

if __name__ == "__main__":
    app = DataPlotter()  # 启动应用
    app.mainloop()
