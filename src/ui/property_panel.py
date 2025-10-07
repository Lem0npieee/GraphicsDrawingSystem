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
        # 更新线条颜色
        if hasattr(shape, 'color') and shape.color:
            self.current_color = shape.color
            self.color_frame.config(bg=self.current_color)
        
        # 根据图形类型显示/隐藏填充颜色控件
        from ..shapes.point import Point
        if isinstance(shape, Point):
            # 点类型：隐藏填充颜色相关控件
            self.hide_fill_controls()
        else:
            # 其他图形：显示填充颜色控件
            self.show_fill_controls()
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
    
    def hide_fill_controls(self):
        """隐藏填充颜色相关控件"""
        # 隐藏填充颜色标签、颜色框和无填充复选框
        for widget in self.color_frame.master.winfo_children():
            if hasattr(widget, 'cget'):
                try:
                    if widget.cget('text') == '填充颜色:':
                        widget.pack_forget()
                        # 找到并隐藏对应的颜色框和复选框
                        widget_list = list(self.color_frame.master.winfo_children())
                        widget_index = widget_list.index(widget)
                        if widget_index + 1 < len(widget_list):
                            widget_list[widget_index + 1].pack_forget()  # 颜色框
                        if widget_index + 2 < len(widget_list):
                            widget_list[widget_index + 2].pack_forget()  # 复选框
                        break
                except:
                    pass
    
    def show_fill_controls(self):
        """显示填充颜色相关控件"""
        # 重建填充颜色控件（简单的方法是重新pack）
        widgets_in_color_frame = self.color_frame.master.winfo_children()
        fill_label_exists = False
        
        for widget in widgets_in_color_frame:
            if hasattr(widget, 'cget'):
                try:
                    if widget.cget('text') == '填充颜色:':
                        fill_label_exists = True
                        widget.pack(anchor=tk.W, pady=(10, 0))
                        break
                except:
                    pass
        
        # 如果标签不存在，说明控件被销毁了，需要重新创建
        if not fill_label_exists:
            self._recreate_fill_controls()
        else:
            # 重新显示颜色框和复选框
            self.fill_color_frame.pack(fill=tk.X, pady=2)
            # 查找复选框并显示
            for widget in widgets_in_color_frame:
                if hasattr(widget, 'cget') and hasattr(widget, 'config'):
                    try:
                        if 'text' in widget.keys() and widget.cget('text') == '无填充':
                            widget.pack(anchor=tk.W, pady=2)
                            break
                    except:
                        pass
    
    def _recreate_fill_controls(self):
        """重新创建填充颜色控件"""
        color_frame = self.color_frame.master
        
        # 填充颜色标签
        fill_label = ttk.Label(color_frame, text="填充颜色:")
        fill_label.pack(anchor=tk.W, pady=(10, 0))
        
        # 填充颜色框
        if not hasattr(self, 'fill_color_frame') or not self.fill_color_frame.winfo_exists():
            self.fill_color_frame = tk.Frame(color_frame, height=30, bg="white")
            self.fill_color_frame.bind("<Button-1>", self.choose_fill_color)
        self.fill_color_frame.pack(fill=tk.X, pady=2)
        
        # 无填充复选框
        if not hasattr(self, 'no_fill_var'):
            self.no_fill_var = tk.BooleanVar(value=False)
        no_fill_cb = ttk.Checkbutton(color_frame, text="无填充", 
                                    variable=self.no_fill_var,
                                    command=self.toggle_fill)
        no_fill_cb.pack(anchor=tk.W, pady=2)