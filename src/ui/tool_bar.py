"""
工具栏组件
"""
import tkinter as tk        # 笔刷工具列表
from tkinter import ttk


class ToolBar:
    """工具栏类"""
    
    def __init__(self, parent, callback, mode="2d"):
        self.parent = parent
        self.callback = callback
        self.current_tool = "select"
        self.mode = mode  # "2d" or "3d"
        
        self.setup_ui()
        
    def setup_ui(self):
        """设置工具栏界面"""
        # 清除现有内容
        for widget in self.parent.winfo_children():
            widget.destroy()
            
        # 工具栏标题
        mode_text = "3D工具栏:" if self.mode == "3d" else "工具栏:"
        title_label = ttk.Label(self.parent, text=mode_text, font=("Arial", 10, "bold"))
        title_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # 工具按钮容器
        tool_frame = ttk.Frame(self.parent)
        tool_frame.pack(side=tk.LEFT)
        
        if self.mode == "3d":
            self.setup_3d_tools(tool_frame)
        else:
            self.setup_2d_tools(tool_frame)
    
    def setup_2d_tools(self, tool_frame):
        """设置2D工具"""
        # 基础工具按钮列表
        self.basic_tools = [
            ("select", "选择", "🖱️"),
            ("point", "点", "●"),
            ("line", "直线", "—"),
            ("rectangle", "矩形", "⬜"),
            ("circle", "圆形", "○"),
            ("polygon", "多边形", "⬟"),
            ("bezier", "曲线", "〰️"),
            ("image", "插入图片", "🖼️")
        ]
        
        # 笔刷工具列表
        self.brush_tools = [
            ("brush_ballpoint", "圆珠笔", "🖊️"),
            ("brush_spray", "喷雾笔刷", "🖌️"),
            ("brush_pencil", "铅笔", "✏️"),
            ("brush_highlighter", "荧光笔", "🖍️")
        ]
        
        self.tool_buttons = {}
        self.tool_var = tk.StringVar(value="select")
        
        # 创建基础工具按钮
        for tool_id, tool_name, tool_icon in self.basic_tools:
            btn = ttk.Radiobutton(
                tool_frame,
                text=f"{tool_icon} {tool_name}",
                value=tool_id,
                variable=self.tool_var,
                command=lambda t=tool_id: self.select_tool(t)
            )
            btn.pack(side=tk.LEFT, padx=2)
            self.tool_buttons[tool_id] = btn
        
        # 创建笔刷工具组
        self.create_brush_tool_group(tool_frame)
        
        self.create_action_buttons()
    
    def setup_3d_tools(self, tool_frame):
        """设置3D工具"""
        # 基础工具（选择工具）
        select_btn = ttk.Radiobutton(
            tool_frame,
            text="🖱️ 选择",
            value="select",
            variable=tk.StringVar(value="select"),
            command=lambda: self.select_tool("select")
        )
        select_btn.pack(side=tk.LEFT, padx=2)
        
        # 分隔符
        separator1 = ttk.Separator(tool_frame, orient=tk.VERTICAL)
        separator1.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # 3D形状创建按钮组
        shapes_frame = ttk.LabelFrame(tool_frame, text="创建3D形状", padding=3)
        shapes_frame.pack(side=tk.LEFT, padx=5)
        
        # 3D形状按钮列表（改为普通按钮）
        self.shape_tools = [
            ("point3d", "3D点", "⚫"),
            ("vector3d", "向量", "➡️"),
            ("cube3d", "立方体", "🟧"),
            ("sphere3d", "球体", "🔵"),
            ("pyramid3d", "四棱锥", "🔺"),
            ("cone3d", "圆锥", "🔸")
        ]
        
        # 创建形状按钮（普通按钮，点击即创建）
        for shape_id, shape_name, shape_icon in self.shape_tools:
            btn = ttk.Button(
                shapes_frame,
                text=f"{shape_icon} {shape_name}",
                command=lambda s=shape_id: self.create_shape(s)
            )
            btn.pack(side=tk.LEFT, padx=1)
        
        # 添加变换模式选择器
        self.create_transform_mode_selector()
        
        self.create_action_buttons()
    
    def create_shape(self, shape_type):
        """创建3D形状"""
        if self.callback:
            self.callback("create_shape", shape_type)
    
    def create_transform_mode_selector(self):
        """创建变换模式选择器"""
        # 分隔符
        separator = ttk.Separator(self.parent, orient=tk.VERTICAL)
        separator.pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # 变换模式框架
        transform_frame = ttk.LabelFrame(self.parent, text="变换模式", padding=5)
        transform_frame.pack(side=tk.LEFT, padx=5)
        
        # 变换模式变量
        self.transform_mode_var = tk.StringVar(value="move")
        
        # 变换模式按钮
        transform_modes = [
            ("move", "移动", "↔️"),
            ("scale", "缩放", "⚡"),
            ("rotate", "旋转", "🔄")
        ]
        
        for mode_id, mode_name, mode_icon in transform_modes:
            btn = ttk.Radiobutton(
                transform_frame,
                text=f"{mode_icon} {mode_name}",
                value=mode_id,
                variable=self.transform_mode_var,
                command=lambda m=mode_id: self.set_transform_mode(m)
            )
            btn.pack(side=tk.LEFT, padx=2)
    
    def set_transform_mode(self, mode):
        """设置变换模式"""
        self.transform_mode_var.set(mode)
        # 通过回调通知主窗口更新Canvas3D的变换模式
        self.callback("set_transform_mode", mode)
    
    def create_action_buttons(self):
        """创建操作按钮"""
        # 分隔符
        separator = ttk.Separator(self.parent, orient=tk.VERTICAL)
        separator.pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # 操作按钮
        action_frame = ttk.Frame(self.parent)
        action_frame.pack(side=tk.LEFT)
        
        actions = [
            ("clear", "清空画布", self.clear_canvas),
            ("delete", "删除选中", self.delete_selected)
        ]
        
        for action_id, action_name, action_callback in actions:
            btn = ttk.Button(
                action_frame,
                text=action_name,
                command=action_callback
            )
            btn.pack(side=tk.LEFT, padx=2)
    
    def create_brush_tool_group(self, parent):
        """创建笔刷工具组"""
        # 笔刷工具容器
        brush_frame = ttk.Frame(parent)
        brush_frame.pack(side=tk.LEFT, padx=2)
        
        # 当前选中的笔刷类型
        self.current_brush_type = "brush_ballpoint"
        
        # 主笔刷按钮
        self.main_brush_button = ttk.Radiobutton(
            brush_frame,
            text="🖊️ 圆珠笔",
            value="brush",
            variable=self.tool_var,
            command=lambda: self.select_tool("brush")
        )
        self.main_brush_button.pack(side=tk.LEFT)
        self.tool_buttons["brush"] = self.main_brush_button
        
        # 展开按钮
        self.expand_button = ttk.Button(
            brush_frame,
            text="▼",
            width=3,
            command=self.toggle_brush_menu
        )
        self.expand_button.pack(side=tk.LEFT, padx=(2, 0))
        
        # 笔刷选项菜单（初始隐藏）
        self.brush_menu_visible = False
        self.brush_menu = None
        
    def toggle_brush_menu(self):
        """切换笔刷菜单显示/隐藏"""
        if self.brush_menu_visible:
            self.hide_brush_menu()
        else:
            self.show_brush_menu()
    
    def show_brush_menu(self):
        """显示笔刷菜单"""
        if self.brush_menu:
            return
            
        # 创建弹出菜单
        self.brush_menu = tk.Toplevel()
        self.brush_menu.title("笔刷选项")
        self.brush_menu.geometry("160x130")  # 调整高度
        self.brush_menu.resizable(False, False)
        
        # 设置菜单位置（在展开按钮下方）
        button_x = self.expand_button.winfo_rootx()
        button_y = self.expand_button.winfo_rooty() + self.expand_button.winfo_height()
        self.brush_menu.geometry(f"+{button_x}+{button_y}")
        
        # 创建笔刷选项
        for brush_id, brush_name, brush_icon in self.brush_tools:
            btn = ttk.Button(
                self.brush_menu,
                text=f"{brush_icon} {brush_name}",
                command=lambda bid=brush_id, bname=brush_name, bicon=brush_icon: self.select_brush_type(bid, bname, bicon)
            )
            btn.pack(fill=tk.X, padx=5, pady=2)
        
        # 绑定失去焦点时关闭菜单
        self.brush_menu.bind("<FocusOut>", lambda e: self.hide_brush_menu())
        self.brush_menu.focus_set()
        
        self.brush_menu_visible = True
        self.expand_button.config(text="▲")
    
    def hide_brush_menu(self):
        """隐藏笔刷菜单"""
        if self.brush_menu:
            self.brush_menu.destroy()
            self.brush_menu = None
        self.brush_menu_visible = False
        self.expand_button.config(text="▼")
    
    def select_brush_type(self, brush_id, brush_name, brush_icon):
        """选择笔刷类型"""
        self.current_brush_type = brush_id
        self.main_brush_button.config(text=f"{brush_icon} {brush_name}")
        self.hide_brush_menu()
        
        # 通知选择了笔刷工具
        self.tool_var.set("brush")
        if self.callback:
            self.callback(brush_id)  # 传递具体的笔刷类型
            
    def select_tool(self, tool_id):
        """选择工具"""
        self.current_tool = tool_id
        if self.callback:
            # 如果是笔刷工具，传递具体的笔刷类型
            if tool_id == "brush":
                self.callback(self.current_brush_type)
            else:
                self.callback(tool_id)
                
    def get_current_tool(self):
        """获取当前选择的工具"""
        if self.current_tool == "brush":
            return self.current_brush_type
        return self.current_tool
        
    def get_current_brush_type(self):
        """获取当前笔刷类型"""
        return self.current_brush_type
        
    def clear_canvas(self):
        """清空画布"""
        if self.callback:
            self.callback("clear")
            
    def delete_selected(self):
        """删除选中的图形"""
        if self.callback:
            self.callback("delete")
    
    def switch_mode(self, mode):
        """切换模式"""
        if mode != self.mode:
            self.mode = mode
            self.current_tool = "select"
            self.setup_ui()