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
        self.state('zoomed')  # 窗口启动时最大化
        self.style = ttkb.Style("lumen")  # 使用现代主题

        # 设置部件的默认字体和样式
        self.option_add("*Font", "Arial 12")
        self.style.configure("TButton", font=("Arial", 12), padding=5)
        self.style.configure("TLabel", font=("Arial", 12))
        self.style.configure("TEntry", padding=5)
        self.style.configure("TCombobox", padding=5)

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
        data_load_frame.grid_rowconfigure(1, weight=1)
        data_load_frame.grid_columnconfigure(0, weight=1)

        self.load_button = ttkb.Button(data_load_frame, text="Load Data (XYXY)", bootstyle="primary", command=self.load_data)
        self.load_button.grid(row=0, column=0, pady=5, padx=5, sticky="nsew")

        self.drop_area_xyxy = ttkb.Label(data_load_frame, text="Drag & Drop File Here (XYXY)", relief="ridge", bootstyle="info", padding=10, anchor="center")
        self.drop_area_xyxy.grid(row=1, column=0, pady=5, padx=5, sticky="nsew")
        self.drop_area_xyxy.drop_target_register(DND_FILES)
        self.drop_area_xyxy.dnd_bind('<<Drop>>', self.on_drop_xyxy)

        # 数据加载部分 (XYYY)
        data_load_xyyy_frame = ttkb.LabelFrame(left_frame, text="Data Load (XYYY)", padding="10 10 10 10")
        data_load_xyyy_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # 配置 data_load_xyyy_frame 的 grid 权重
        data_load_xyyy_frame.grid_rowconfigure(0, weight=1)
        data_load_xyyy_frame.grid_rowconfigure(1, weight=1)
        data_load_xyyy_frame.grid_columnconfigure(0, weight=1)

        self.load_button_modified = ttkb.Button(data_load_xyyy_frame, text="Load Data (XYYY)", bootstyle="primary", command=self.load_and_modify_data)
        self.load_button_modified.grid(row=0, column=0, pady=5, padx=5, sticky="nsew")

        self.drop_area_xyyy = ttkb.Label(data_load_xyyy_frame, text="Drag & Drop File Here (XYYY)", relief="ridge", bootstyle="info", padding=10, anchor="center")
        self.drop_area_xyyy.grid(row=1, column=0, pady=5, padx=5, sticky="nsew")
        self.drop_area_xyyy.drop_target_register(DND_FILES)
        self.drop_area_xyyy.dnd_bind('<<Drop>>', self.on_drop_xyyy)

        # 数据加载部分 (Box Data)
        data_load_box_frame = ttkb.LabelFrame(left_frame, text="Data Load (Box Data)", padding="10 10 10 10")
        data_load_box_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")

        # 配置 data_load_box_frame 的 grid 权重
        data_load_box_frame.grid_rowconfigure(0, weight=1)
        data_load_box_frame.grid_rowconfigure(1, weight=1)
        data_load_box_frame.grid_columnconfigure(0, weight=1)

        self.load_button_labels = ttkb.Button(data_load_box_frame, text="Load Box Data", bootstyle="primary", command=self.load_data_boxplot)
        self.load_button_labels.grid(row=0, column=0, pady=5, padx=5, sticky="nsew")

        self.drop_area_box = ttkb.Label(data_load_box_frame, text="Drag & Drop File Here (Box)", relief="ridge", bootstyle="info", padding=10, anchor="center")
        self.drop_area_box.grid(row=1, column=0, pady=5, padx=5, sticky="nsew")
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
        axis_settings_frame = ttkb.LabelFrame(left_frame, text="Axis Settings", padding="10 10 10 10")
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

        # 绘图和保存按钮
        action_frame = ttkb.LabelFrame(left_frame, text="Actions", padding="10 10 10 10")
        action_frame.grid(row=4, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

        # 配置 action_frame 的 grid 权重
        action_frame.grid_rowconfigure(0, weight=1)
        action_frame.grid_rowconfigure(1, weight=1)
        action_frame.grid_columnconfigure(0, weight=1)
        action_frame.grid_columnconfigure(1, weight=1)
        action_frame.grid_columnconfigure(2, weight=1)

        # 行 1：主要操作按钮
        self.plot_button = ttkb.Button(action_frame, text="Plot Data", bootstyle="success-outline", command=self.plot_data)
        self.plot_button.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")

        self.boxplot_button = ttkb.Button(action_frame, text="Plot Boxplot", bootstyle="success-outline", command=self.plot_boxplot)
        self.boxplot_button.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")

        self.save_button = ttkb.Button(action_frame, text="Save Plot", bootstyle="warning-outline", command=self.save_plot)
        self.save_button.grid(row=0, column=2, padx=10, pady=5, sticky="nsew")

        # 行 2：附加的保存和加载按钮
        self.save_data_button = ttkb.Button(action_frame, text="Save Raw Data", bootstyle="secondary-outline", command=self.save_plot_data)
        self.save_data_button.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

        self.load_data_button = ttkb.Button(action_frame, text="Load Raw Data", bootstyle="info-outline", command=self.load_plot_data)
        self.load_data_button.grid(row=1, column=1, padx=10, pady=5, sticky="nsew")

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

    # 保存数据方法
    def save_plot_data(self):
        if self.data is not None:
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

            file_path = filedialog.asksaveasfilename(defaultextension=".pkl", filetypes=[("Pickle files", "*.pkl")])
            if file_path:
                with open(file_path, "wb") as f:
                    pickle.dump(plot_data, f)
                messagebox.showinfo("Save Successful", f"Plot data has been saved to {file_path}")

    # 加载数据方法
    def load_plot_data(self):
        file_path = filedialog.askopenfilename(filetypes=[("Pickle files", "*.pkl")])
        if file_path and os.path.exists(file_path):
            with open(file_path, "rb") as f:
                plot_data = pickle.load(f)

            self.data = plot_data["data"]
            self.shift_x_var.set(plot_data.get("shift_x", 0.0))
            self.shift_y_var.set(plot_data.get("shift_y", 0.0))
            self.times_x_var.set(plot_data.get("times_x", 1.0))
            self.times_y_var.set(plot_data.get("times_y", 1.0))
            self.font_size_var.set(plot_data.get("font_size", "18"))
            self.style_var.set(plot_data.get("style", "PL"))
            self.Boxstyle_var.set(plot_data.get("Boxstyle", "PCE"))

            plot_type = plot_data.get("plot_type", "line")
            if plot_type == "boxplot":
                self.create_label_entries_boxplot()
                self.configure_box_view()
            else:
                self.create_label_entries()
                self.configure_xy_view()

            for i, entry in enumerate(self.label_entries):
                entry.insert(0, plot_data["labels"][i])
            for i, flag in enumerate(self.plot_flags):
                flag.set(plot_data["plot_flags"][i])

            # 显示数据到 tksheet
            self.display_data_in_sheet()
            messagebox.showinfo("Load Successful", f"Plot data has been loaded from {file_path}")

if __name__ == "__main__":
    app = DataPlotter()  # 启动应用
    app.mainloop()
