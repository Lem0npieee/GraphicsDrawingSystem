"""
主窗口界面
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, colorchooser
import os
import sys

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from managers.drawing_manager import DrawingManager
from managers.drawing_manager3d import DrawingManager3D
from .tool_bar import ToolBar
from .property_panel import PropertyPanel
from .canvas3d import Canvas3D


class MainWindow:
    """主窗口类"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("2D图形绘制系统")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # 创建绘图管理器
        self.drawing_manager = DrawingManager()
        self.drawing_manager3d = DrawingManager3D()
        
        # 初始化界面组件
        self.setup_ui()
        
        # 绑定事件
        self.bind_events()
        
        # 当前选择的工具
        self.current_tool = "select"
        
    def setup_ui(self):
        """设置用户界面"""
        # 创建菜单栏
        self.create_menu_bar()
        
        # 创建主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建工具栏框架
        tool_frame = ttk.Frame(main_frame)
        tool_frame.pack(fill=tk.X, pady=(0, 5))
        
        # 创建工具栏
        self.tool_bar = ToolBar(tool_frame, self.on_tool_selected, mode="2d")
        
        # 创建中间内容框架
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建左侧属性面板
        self.property_panel = PropertyPanel(content_frame, self.on_property_changed)
        
        # 创建右侧绘图区域
        canvas_frame = ttk.Frame(content_frame)
        canvas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        self.canvas_frame = canvas_frame
        
        # 创建画布滚动条
        canvas_scrollbar_v = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL)
        canvas_scrollbar_h = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL)
        
        # 创建画布
        self.canvas = tk.Canvas(canvas_frame, 
                            bg="white", 
                            scrollregion=(0, 0, 2000, 2000),
                            yscrollcommand=canvas_scrollbar_v.set,
                            xscrollcommand=canvas_scrollbar_h.set)
        
        # 配置滚动条
        canvas_scrollbar_v.config(command=self.canvas.yview)
        canvas_scrollbar_h.config(command=self.canvas.xview)
        
        # 布局滚动条和画布
        canvas_scrollbar_v.pack(side=tk.RIGHT, fill=tk.Y)
        canvas_scrollbar_h.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 将画布传递给绘图管理器
        self.drawing_manager.set_canvas(self.canvas)
        
        # 创建独立的模式切换按钮框架
        mode_frame = ttk.Frame(main_frame)
        mode_frame.pack(fill=tk.X, pady=(2, 0))
        
        # 模式切换按钮（放在独立框架中，确保始终可见）
        self.mode_var = tk.StringVar(value="2D")
        switch_btn = ttk.Button(mode_frame, text="切换到3D", command=self.toggle_mode, 
                               style="Accent.TButton")  # 使用强调样式
        switch_btn.pack(side=tk.RIGHT, padx=5)
        self.switch_btn = switch_btn
        
        # 添加模式指示标签
        mode_label = ttk.Label(mode_frame, text="当前模式: 2D", font=("Arial", 10, "bold"))
        mode_label.pack(side=tk.RIGHT, padx=(0, 10))
        self.mode_label = mode_label

        # 创建状态栏
        self.create_status_bar()

        # 当前模式
        self.mode = "2D"
        self.canvas3d = None
        
        # 同步初始颜色设置
        self.sync_initial_colors()
        
    def sync_initial_colors(self):
        """同步属性面板的初始颜色到3D绘图管理器"""
        # 获取属性面板的当前颜色
        current_color = self.property_panel.get_current_color()
        current_fill_color = self.property_panel.get_current_fill_color()
        current_line_width = self.property_panel.get_current_line_width()
        
        # 同步到3D绘图管理器
        self.drawing_manager3d.set_current_color(current_color)
        self.drawing_manager3d.set_current_fill_color(current_fill_color)
        self.drawing_manager3d.set_current_line_width(current_line_width)
        
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="新建", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="打开", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="保存", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="导出为图片", command=self.export_image)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)
        
        # 编辑菜单
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="编辑", menu=edit_menu)
        edit_menu.add_command(label="撤销", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="重做", command=self.redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="复制", command=self.copy, accelerator="Ctrl+C")
        edit_menu.add_command(label="粘贴", command=self.paste, accelerator="Ctrl+V")
        edit_menu.add_command(label="删除", command=self.delete, accelerator="Delete")
        edit_menu.add_separator()
        edit_menu.add_command(label="全选", command=self.select_all, accelerator="Ctrl+A")
        edit_menu.add_command(label="清除选中", command=self.clear_selection)
        edit_menu.add_command(label="清空画布", command=self.clear_all)
        
        # 视图菜单
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="视图", menu=view_menu)
        view_menu.add_command(label="放大", command=self.zoom_in, accelerator="Ctrl++")
        view_menu.add_command(label="缩小", command=self.zoom_out, accelerator="Ctrl+-")
        view_menu.add_command(label="适应窗口", command=self.fit_to_window)
        view_menu.add_command(label="实际大小", command=self.actual_size)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="使用说明", command=self.show_help)
        help_menu.add_command(label="关于", command=self.show_about)
        
    def create_status_bar(self):
        """创建状态栏"""
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = ttk.Label(self.status_bar, text="就绪")
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        self.coord_label = ttk.Label(self.status_bar, text="坐标: (0, 0)")
        self.coord_label.pack(side=tk.RIGHT, padx=5)
        
    def bind_events(self):
        """绑定事件"""
        # 键盘快捷键
        self.root.bind('<Control-n>', lambda e: self.new_file())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<Control-z>', lambda e: self.undo())
        self.root.bind('<Control-y>', lambda e: self.redo())
        self.root.bind('<Control-c>', lambda e: self.copy())
        self.root.bind('<Control-v>', lambda e: self.paste())
        self.root.bind('<Control-a>', lambda e: self.select_all())
        self.root.bind('<Delete>', lambda e: self.delete())
        
        # 画布事件（2D模式）
        self.bind_canvas_2d_events()

    def bind_canvas_2d_events(self):
        # 解绑所有旧事件，然后绑定2D事件
        for seq in ['<Button-1>', '<B1-Motion>', '<ButtonRelease-1>', '<Motion>', '<Button-3>', '<MouseWheel>']:
            self.canvas.unbind(seq)
        self.canvas.bind('<Button-1>', self.on_canvas_click)
        self.canvas.bind('<B1-Motion>', self.on_canvas_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_canvas_release)
        self.canvas.bind('<Motion>', self.on_canvas_motion)
        self.canvas.bind('<Button-3>', self.on_canvas_right_click)
        
    def on_tool_selected(self, action, data=None):
        """工具选择和动作回调"""
        if action == "set_transform_mode":
            # 设置3D变换模式
            if self.mode == '3D' and hasattr(self, 'canvas3d'):
                self.canvas3d.set_transform_mode(data)
                self.update_status(f"切换到{data}模式")
        elif action == "create_shape":
            # 创建3D形状
            if self.mode == '3D' and hasattr(self, 'drawing_manager3d'):
                self.create_3d_shape_at_origin(data)
        elif action == "clear":
            # 清空画布
            self.clear_all()
        elif action == "delete":
            # 删除选中的图形
            self.delete()
        else:
            # 兼容旧的工具选择调用（当action实际是tool_name时）
            tool_name = action
            self.current_tool = tool_name
            # 根据当前模式更新状态信息
            if self.mode == '3D':
                self.update_status(f"选择3D工具: {tool_name}")
                # 处理3D工具点击创建图形（保留兼容性）
                if tool_name in ["point3d", "vector3d", "cube3d", "sphere3d", "pyramid3d", "cone3d"]:
                    self.create_3d_shape_at_origin(tool_name)
            else:
                self.update_status(f"选择工具: {tool_name}")
    
    def create_3d_shape_at_origin(self, shape_type):
        """在原点创建标准大小的3D形状"""
        if not hasattr(self, 'drawing_manager3d'):
            return
        
        # 定义标准形状参数
        standard_shapes = {
            "point3d": {"x": 0, "y": 0, "z": 0},
            "vector3d": {"x": 0, "y": 0, "z": 0, "vx": 2, "vy": 1, "vz": 1},
            "cube3d": {"x": 0, "y": 0, "z": 0, "size": 2},
            "sphere3d": {"x": 0, "y": 0, "z": 0, "radius": 1.5},
            "pyramid3d": {"x": 0, "y": 0, "z": 0, "base_size": 2, "height": 3},
            "cone3d": {"x": 0, "y": 0, "z": 0, "radius": 1.5, "height": 3}
        }
        
        if shape_type in standard_shapes:
            # 创建形状
            shape = self.drawing_manager3d.create_shape(shape_type, **standard_shapes[shape_type])
            if shape:
                # 添加到绘图管理器（这会自动添加到画布）
                self.drawing_manager3d.add_shape(shape)
                # 选中新创建的形状
                self.canvas3d.select_shape(shape)
                self.update_status(f"在原点创建了{shape_type}")
            else:
                self.update_status(f"创建{shape_type}失败")
        
    def on_property_changed(self, property_name, value):
        """属性改变回调"""
        if property_name == "color":
            self.drawing_manager.set_current_color(value)
            # 同步到3D绘图管理器
            if hasattr(self, 'drawing_manager3d'):
                self.drawing_manager3d.set_current_color(value)
            # 应用到3D画布选中的形状
            if self.canvas3d and self.canvas3d.selected_shape:
                self.canvas3d.selected_shape.set_color(value)
                self.canvas3d.redraw()
        elif property_name == "fill_color":
            self.drawing_manager.set_current_fill_color(value)
            # 同步到3D绘图管理器
            if hasattr(self, 'drawing_manager3d'):
                self.drawing_manager3d.set_current_fill_color(value)
            # 应用到3D画布选中的形状
            if self.canvas3d and self.canvas3d.selected_shape:
                self.canvas3d.selected_shape.set_fill_color(value)
                self.canvas3d.redraw()
        elif property_name == "line_width":
            self.drawing_manager.set_current_line_width(value)
            # 同步到3D绘图管理器
            if hasattr(self, 'drawing_manager3d'):
                self.drawing_manager3d.set_current_line_width(value)
            # 应用到3D画布选中的形状
            if self.canvas3d and self.canvas3d.selected_shape:
                self.canvas3d.selected_shape.set_line_width(value)
                self.canvas3d.redraw()
        elif property_name == "brush_size":
            self.drawing_manager.set_current_brush_size(value)
    
    def on_3d_shape_selected(self, shape):
        """3D形状选择改变回调"""
        if shape:
            # 更新3D绘图管理器的选择状态
            self.drawing_manager3d.select_shape(shape)
            # 更新属性面板显示选中形状的颜色
            self.property_panel.update_colors_from_shape(shape)
        else:
            # 清除3D绘图管理器的选择
            self.drawing_manager3d.clear_selection()
        # 这里可以添加更多的选择处理逻辑
            
    def on_canvas_click(self, event):
        """画布点击事件"""
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        self.drawing_manager.on_mouse_press(x, y, self.current_tool)
        
    def on_canvas_drag(self, event):
        """画布拖拽事件"""
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        self.drawing_manager.on_mouse_drag(x, y)
        
    def on_canvas_release(self, event):
        """画布释放事件"""
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        self.drawing_manager.on_mouse_release(x, y)
        
    def on_canvas_motion(self, event):
        """鼠标移动事件"""
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        self.coord_label.config(text=f"坐标: ({int(x)}, {int(y)})")
        
        # 多边形绘制时的实时预览
        if self.current_tool == "polygon" and len(self.drawing_manager.polygon_points) > 0:
            self.drawing_manager.draw_polygon_preview(x, y)
        
        # 更新鼠标光标
        self.update_cursor(x, y)
        
    def on_canvas_right_click(self, event):
        """右键点击事件"""
        # 可以添加右键菜单
        pass
        
    def update_status(self, message):
        """更新状态栏"""
        self.status_label.config(text=message)

    # 模式切换
    def has_2d_content(self) -> bool:
        return bool(self.drawing_manager.shapes)

    def has_3d_content(self) -> bool:
        return self.canvas3d.has_content if self.canvas3d else False

    def confirm_switch(self) -> bool:
        if (self.mode == '2D' and self.has_2d_content()) or (self.mode == '3D' and self.has_3d_content()):
            return messagebox.askyesno("确认切换", "检测到当前画布有未保存内容，切换将清空当前画布，是否继续？")
        return True

    def toggle_mode(self):
        if not self.confirm_switch():
            return

        if self.mode == '2D':
            # 切到3D：隐藏2D画布，加载3D画布
            self.drawing_manager.clear()  # 清空2D内容
            self.canvas.pack_forget()
            if self.canvas3d is None:
                self.canvas3d = Canvas3D(self.canvas_frame)
                self.drawing_manager3d.set_canvas3d(self.canvas3d)  # 连接管理器和画布
                self.canvas3d.set_selection_callback(self.on_3d_shape_selected)  # 连接选择回调
            self.canvas3d.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            self.switch_btn.config(text="切换到2D")
            self.mode_label.config(text="当前模式: 3D", foreground="blue")
            self.mode = '3D'
            self.tool_bar.switch_mode("3d")  # 切换工具栏到3D模式
            self.update_status("切换到3D视图：右键拖动旋转，滚轮缩放")
        else:
            # 切回2D：隐藏3D，显示2D
            if self.canvas3d:
                self.canvas3d.pack_forget()
                self.drawing_manager3d.clear()  # 清空3D内容
            self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            self.switch_btn.config(text="切换到3D")
            self.mode_label.config(text="当前模式: 2D", foreground="green")
            self.mode = '2D'
            self.tool_bar.switch_mode("2d")  # 切换工具栏到2D模式
            self.update_status("切换到2D视图")
            self.bind_canvas_2d_events()
        
    # 菜单回调函数
    def new_file(self):
        """新建文件"""
        self.drawing_manager.clear()
        self.update_status("新建文件")
        
    def open_file(self):
        """打开文件"""
        filename = filedialog.askopenfilename(
            title="打开文件",
            filetypes=[("项目文件", "*.json"), ("所有文件", "*.*")]
        )
        if filename:
            try:
                # 首先尝试检测文件类型
                import json
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                file_mode = data.get('mode', '2D')
                
                # 如果文件模式与当前模式不匹配，询问是否切换
                if file_mode != self.mode:
                    result = messagebox.askyesno("模式切换", 
                        f"文件是{file_mode}格式，当前是{self.mode}模式。是否切换到{file_mode}模式？")
                    if result:
                        # 切换模式
                        if file_mode == '3D' and self.mode == '2D':
                            self.toggle_mode()
                        elif file_mode == '2D' and self.mode == '3D':
                            self.toggle_mode()
                
                # 加载文件
                if self.mode == '3D':
                    self.drawing_manager3d.load_from_file(filename)
                else:
                    self.drawing_manager.load_from_file(filename)
                    
                self.update_status(f"打开文件: {filename}")
            except Exception as e:
                messagebox.showerror("错误", f"无法打开文件: {str(e)}")
                
    def save_file(self):
        """保存文件"""
        filename = filedialog.asksaveasfilename(
            title="保存文件",
            defaultextension=".json",
            filetypes=[("项目文件", "*.json"), ("所有文件", "*.*")]
        )
        if filename:
            try:
                if self.mode == '3D':
                    self.drawing_manager3d.save_to_file(filename)
                else:
                    self.drawing_manager.save_to_file(filename)
                self.update_status(f"保存文件: {filename}")
            except Exception as e:
                messagebox.showerror("错误", f"无法保存文件: {str(e)}")
                
    def export_image(self):
        """导出为图片"""
        filename = filedialog.asksaveasfilename(
            title="导出图片",
            defaultextension=".png",
            filetypes=[("PNG文件", "*.png"), ("JPEG文件", "*.jpg"), ("所有文件", "*.*")]
        )
        if filename:
            try:
                if self.mode == '3D':
                    self.export_3d_image(filename)
                else:
                    self.export_2d_image(filename)
                self.update_status(f"导出图片: {filename}")
            except Exception as e:
                messagebox.showerror("错误", f"无法导出图片: {str(e)}")
    
    def export_2d_image(self, filename: str):
        """导出2D场景为图片（使用屏幕截图）"""
        if not self.canvas:
            raise Exception("2D画布未初始化")
        
        try:
            from PIL import ImageGrab
            
            canvas = self.canvas
            
            # 确保画布已更新到最新状态
            canvas.update_idletasks()
            canvas.update()
            
            # 获取画布在屏幕上的绝对位置
            x = canvas.winfo_rootx()
            y = canvas.winfo_rooty()
            width = canvas.winfo_width()
            height = canvas.winfo_height()
            
            # 截取屏幕区域
            bbox = (x, y, x + width, y + height)
            img = ImageGrab.grab(bbox)
            
            # 保存图片
            if filename.lower().endswith('.jpg') or filename.lower().endswith('.jpeg'):
                img.save(filename, 'JPEG', quality=95)
            else:
                img.save(filename, 'PNG')
                
        except ImportError:
            raise Exception("需要安装PIL库来导出图片")
        except Exception as e:
            raise Exception(f"导出图片失败: {e}")
    
    def export_3d_image(self, filename: str):
        """导出3D场景为图片（使用屏幕截图）"""
        if not self.canvas3d:
            raise Exception("3D画布未初始化")
        
        try:
            from PIL import ImageGrab
            
            canvas = self.canvas3d.canvas
            
            # 确保画布已更新到最新状态
            canvas.update_idletasks()
            canvas.update()
            
            # 获取画布在屏幕上的绝对位置
            x = canvas.winfo_rootx()
            y = canvas.winfo_rooty()
            width = canvas.winfo_width()
            height = canvas.winfo_height()
            
            # 截取屏幕区域
            bbox = (x, y, x + width, y + height)
            img = ImageGrab.grab(bbox)
            
            # 保存图片
            if filename.lower().endswith('.jpg') or filename.lower().endswith('.jpeg'):
                img.save(filename, 'JPEG', quality=95)
            else:
                img.save(filename, 'PNG')
                
        except ImportError:
            raise Exception("需要安装PIL库来导出图片")
        except Exception as e:
            raise Exception(f"导出图片失败: {e}")
                
    def undo(self):
        """撤销"""
        if self.mode == '3D':
            self.drawing_manager3d.undo()
        else:
            self.drawing_manager.undo()
        self.update_status("撤销")
        
    def redo(self):
        """重做"""
        if self.mode == '3D':
            self.drawing_manager3d.redo()
        else:
            self.drawing_manager.redo()
        self.update_status("重做")
        
    def copy(self):
        """复制"""
        self.drawing_manager.copy()
        self.update_status("复制")
        
    def paste(self):
        """粘贴"""
        self.drawing_manager.paste()
        self.update_status("粘贴")
        
    def delete(self):
        """删除"""
        if self.mode == '3D':
            self.drawing_manager3d.delete_selected()
        else:
            self.drawing_manager.delete_selected()
        self.update_status("删除")
        
    def select_all(self):
        """全选"""
        self.drawing_manager.select_all()
        self.update_status("全选")
        
    def clear_all(self):
        """清空所有图形"""
        result = messagebox.askyesno("确认", "确定要清空所有图形吗？此操作不可撤销。")
        if result:
            if self.mode == '3D':
                self.drawing_manager3d.clear()
            else:
                self.drawing_manager.clear()
            self.update_status("已清空所有图形")
        
    def clear_selection(self):
        """清除选中"""
        self.drawing_manager.clear_selection()
        self.update_status("已清除选中")
        
    def zoom_in(self):
        """放大"""
        self.update_status("放大")
        
    def zoom_out(self):
        """缩小"""
        self.update_status("缩小")
        
    def fit_to_window(self):
        """适应窗口"""
        self.update_status("适应窗口")
        
    def actual_size(self):
        """实际大小"""
        self.update_status("实际大小")
        
    def show_help(self):
        """显示帮助"""
        help_text = """
2D图形绘制系统 使用说明

工具栏:
- 选择: 选择和移动图形
- 点: 绘制点
- 直线: 绘制直线
- 矩形: 绘制矩形
- 圆形: 绘制圆形
- 多边形: 绘制多边形

属性面板:
- 可以设置图形的颜色、填充色、线宽等属性

快捷键:
- Ctrl+N: 新建
- Ctrl+O: 打开
- Ctrl+S: 保存
- Ctrl+Z: 撤销
- Ctrl+Y: 重做
- Ctrl+C: 复制
- Ctrl+V: 粘贴
- Ctrl+A: 全选
- Delete: 删除
        """
        messagebox.showinfo("使用说明", help_text)
        
    def show_about(self):
        """显示关于"""
        messagebox.showinfo("关于", "2D图形绘制系统\\n版本 1.0\\n\\n一个简单易用的图形绘制工具")
        
    def update_cursor(self, x, y):
        """根据鼠标位置更新光标样式"""
        if self.current_tool != "select":
            self.canvas.config(cursor="crosshair")
            return
        
        # 检查是否在调整大小的控制点上
        for shape in self.drawing_manager.selected_shapes:
            handle_type = shape.get_handle_at_point(x, y)
            if handle_type:
                # 根据控制点类型设置不同的光标
                cursor_map = {
                    'nw': 'size_nw_se',
                    'n': 'size_ns',
                    'ne': 'size_ne_sw',
                    'e': 'size_we',
                    'se': 'size_nw_se',
                    's': 'size_ns',
                    'sw': 'size_ne_sw',
                    'w': 'size_we',
                    'start': 'dotbox',
                    'end': 'dotbox',
                    'center': 'fleur',
                    'p0': 'dotbox',  # 贝塞尔曲线起点
                    'p1': 'dotbox',  # 贝塞尔曲线控制点1
                    'p2': 'dotbox',  # 贝塞尔曲线控制点2
                    'p3': 'dotbox'   # 贝塞尔曲线终点
                }
                # 多边形顶点
                if handle_type.startswith('vertex_'):
                    cursor = 'dotbox'
                else:
                    cursor = cursor_map.get(handle_type, 'size')
                
                self.canvas.config(cursor=cursor)
                return
        
        # 检查是否在图形上
        shape = self.drawing_manager.find_shape_at_point(x, y)
        if shape:
            self.canvas.config(cursor="hand2")
        else:
            self.canvas.config(cursor="arrow")
        
    def run(self):
        """运行主窗口"""
        self.root.mainloop()