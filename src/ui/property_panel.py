"""
属性面板组件
"""
import tkinter as tk
from tkinter import ttk, colorchooser


class PropertyPanel:
    """属性面板类"""
    
    def __init__(self, parent, callback):
        self.parent = parent
        self.callback = callback
        
        self.setup_ui()
        
    def setup_ui(self):
        """设置属性面板界面"""
        # 创建左侧面板框架
        panel_frame = ttk.LabelFrame(self.parent, text="属性设置", padding=10)
        panel_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        
        # 设置面板最小宽度
        panel_frame.config(width=200)
        panel_frame.pack_propagate(False)
        
        # 颜色设置
        color_frame = ttk.LabelFrame(panel_frame, text="颜色设置", padding=5)
        color_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 线条颜色
        ttk.Label(color_frame, text="线条颜色:").pack(anchor=tk.W)
        self.color_frame = tk.Frame(color_frame, height=30, bg="black")
        self.color_frame.pack(fill=tk.X, pady=2)
        self.color_frame.bind("<Button-1>", self.choose_color)
        
        self.current_color = "black"
        
        # 填充颜色
        ttk.Label(color_frame, text="填充颜色:").pack(anchor=tk.W, pady=(10, 0))
        self.fill_color_frame = tk.Frame(color_frame, height=30, bg="white")
        self.fill_color_frame.pack(fill=tk.X, pady=2)
        self.fill_color_frame.bind("<Button-1>", self.choose_fill_color)
        
        self.current_fill_color = "white"
        
        # 无填充选项
        self.no_fill_var = tk.BooleanVar(value=False)
        no_fill_cb = ttk.Checkbutton(color_frame, text="无填充", 
                                    variable=self.no_fill_var,
                                    command=self.toggle_fill)
        no_fill_cb.pack(anchor=tk.W, pady=2)
        
        # 线宽设置
        line_frame = ttk.LabelFrame(panel_frame, text="线条设置", padding=5)
        line_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(line_frame, text="线宽:").pack(anchor=tk.W)
        self.line_width_var = tk.IntVar(value=1)
        line_width_scale = ttk.Scale(line_frame, from_=1, to=10, 
                                   variable=self.line_width_var,
                                   orient=tk.HORIZONTAL,
                                   command=self.on_line_width_change)
        line_width_scale.pack(fill=tk.X, pady=2)
        
        self.line_width_label = ttk.Label(line_frame, text="1 像素")
        self.line_width_label.pack(anchor=tk.W)
        
        # 笔刷设置
        brush_frame = ttk.LabelFrame(panel_frame, text="笔刷设置", padding=5)
        brush_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(brush_frame, text="笔刷大小:").pack(anchor=tk.W)
        self.brush_size_var = tk.IntVar(value=5)
        brush_size_scale = ttk.Scale(brush_frame, from_=1, to=20, 
                                   variable=self.brush_size_var,
                                   orient=tk.HORIZONTAL,
                                   command=self.on_brush_size_change)
        brush_size_scale.pack(fill=tk.X, pady=2)
        
        self.brush_size_label = ttk.Label(brush_frame, text="5 像素")
        self.brush_size_label.pack(anchor=tk.W)
        
    def choose_color(self, event=None):
        """选择线条颜色"""
        color = colorchooser.askcolor(title="选择线条颜色", initialcolor=self.current_color)
        if color[1]:  # 如果用户选择了颜色
            self.current_color = color[1]
            self.color_frame.config(bg=self.current_color)
            if self.callback:
                self.callback("color", self.current_color)
                
    def choose_fill_color(self, event=None):
        """选择填充颜色"""
        if self.no_fill_var.get():
            return
            
        color = colorchooser.askcolor(title="选择填充颜色", 
                                    initialcolor=self.current_fill_color or "white")
        if color[1]:  # 如果用户选择了颜色
            self.current_fill_color = color[1]
            self.fill_color_frame.config(bg=self.current_fill_color)
            if self.callback:
                self.callback("fill_color", self.current_fill_color)
                
    def toggle_fill(self):
        """切换填充状态"""
        if self.no_fill_var.get():
            self.current_fill_color = None
            self.fill_color_frame.config(bg="white", relief=tk.SUNKEN)
            if self.callback:
                self.callback("fill_color", None)
        else:
            self.choose_fill_color()
            
    def on_line_width_change(self, value):
        """线宽改变回调"""
        width = int(float(value))
        self.line_width_label.config(text=f"{width} 像素")
        if self.callback:
            self.callback("line_width", width)
            
    def on_brush_size_change(self, value):
        """笔刷大小改变回调"""
        size = int(float(value))
        self.brush_size_label.config(text=f"{size} 像素")
        if self.callback:
            self.callback("brush_size", size)
            
    def get_current_color(self):
        """获取当前线条颜色"""
        return self.current_color
        
    def get_current_fill_color(self):
        """获取当前填充颜色"""
        return self.current_fill_color
        
    def get_current_line_width(self):
        """获取当前线宽"""
        return self.line_width_var.get()
        
    def update_colors_from_shape(self, shape):
        """从形状更新颜色显示"""
        if hasattr(shape, 'color') and shape.color:
            self.current_color = shape.color
            self.color_frame.config(bg=self.current_color)
        
        if hasattr(shape, 'fill_color') and shape.fill_color:
            self.current_fill_color = shape.fill_color
            self.fill_color_frame.config(bg=self.current_fill_color)
            self.no_fill_var.set(False)
        else:
            self.current_fill_color = None
            self.fill_color_frame.config(bg="white", relief=tk.SUNKEN)
            self.no_fill_var.set(True)
            
        if hasattr(shape, 'line_width') and shape.line_width:
            self.line_width_var.set(shape.line_width)
            self.line_width_label.config(text=f"{shape.line_width} 像素")