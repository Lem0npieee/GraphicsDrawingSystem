"""
绘图管理器 - 负责图形的创建、管理和渲染
"""
import json
import os
import sys
from typing import List, Optional, Tuple
from PIL import Image, ImageDraw

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shapes import BaseShape, Point, Line, Rectangle, Circle, Polygon, BezierCurve, BrushStroke
from shapes.image import Image as ImageShape


class DrawingManager:
    """绘图管理器类"""
    
    def __init__(self):
        self.shapes: List[BaseShape] = []  # 所有图形列表
        self.selected_shapes: List[BaseShape] = []  # 选中的图形列表
        self.canvas = None  # 画布引用
        
        # 当前绘制状态
        self.current_tool = "select"
        self.current_color = "black"
        self.current_fill_color = "white"
        self.current_line_width = 1
        self.current_brush_size = 5
        self.current_brush_type = "brush_ballpoint"  # 当前笔刷类型
        
        # 绘制状态变量
        self.is_drawing = False
        self.start_x = 0
        self.start_y = 0
        self.temp_shape = None
        self.polygon_points = []  # 多边形临时点列表
        self.bezier_points = []   # 贝塞尔曲线临时点列表
        self.bezier_step = 0      # 贝塞尔曲线绘制步骤
        self.current_brush_stroke = None  # 当前笔刷轨迹
        
        # 喷雾笔刷连续绘制
        self.spray_timer = None  # 喷雾定时器
        self.last_spray_x = 0  # 最后喷雾位置
        self.last_spray_y = 0
        
        # 撤销/重做
        self.history = []  # 历史记录
        self.history_index = -1  # 当前历史位置
        self.max_history = 50  # 最大历史记录数
        
        # 拖拽相关
        self.dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        
        # 调整大小相关
        self.resizing = False
        self.resize_handle = ""
        self.resize_shape = None
        
        # 复制粘贴
        self.clipboard = []
        
    def set_canvas(self, canvas):
        """设置画布"""
        self.canvas = canvas
        
    def set_current_tool(self, tool):
        """设置当前工具"""
        self.current_tool = tool
        if tool != "polygon":
            self.polygon_points = []  # 切换工具时清空多边形点
        if tool != "bezier":
            self.bezier_points = []   # 切换工具时清空贝塞尔曲线点
            self.bezier_step = 0
            
    def set_current_color(self, color):
        """设置当前颜色"""
        self.current_color = color
        # 应用到选中的图形
        for shape in self.selected_shapes:
            shape.set_color(color)
        self.redraw()
        
    def set_current_fill_color(self, color):
        """设置当前填充颜色"""
        self.current_fill_color = color
        # 应用到选中的图形
        for shape in self.selected_shapes:
            shape.set_fill_color(color)
        self.redraw()
        
    def set_current_line_width(self, width):
        """设置当前线宽"""
        self.current_line_width = width
        # 应用到选中的图形
        for shape in self.selected_shapes:
            shape.set_line_width(width)
        self.redraw()
        
    def set_current_brush_size(self, size):
        """设置当前笔刷大小"""
        self.current_brush_size = size
        
    def on_mouse_press(self, x, y, tool):
        """鼠标按下事件"""
        self.start_x = x
        self.start_y = y
        self.current_tool = tool
        
        if tool == "select":
            self.handle_select_press(x, y)
        elif tool == "point":
            self.create_point(x, y)
        elif tool == "line":
            self.start_line(x, y)
        elif tool == "rectangle":
            self.start_rectangle(x, y)
        elif tool == "circle":
            self.start_circle(x, y)
        elif tool == "polygon":
            self.handle_polygon_click(x, y)
        elif tool == "bezier":
            self.handle_bezier_click(x, y)
        elif tool == "image":
            self.import_image(x, y)
        elif tool.startswith("brush_"):
            self.current_brush_type = tool
            self.start_brush_stroke(x, y)
        elif tool == "brush":  # 兼容旧版本
            self.start_brush_stroke(x, y)
            
    def on_mouse_drag(self, x, y):
        """鼠标拖拽事件"""
        if self.current_tool == "select":
            if self.resizing:
                self.handle_resize(x, y)
            elif self.dragging:
                self.handle_drag(x, y)
        elif self.current_tool.startswith("brush_") and self.current_brush_stroke:
            self.continue_brush_stroke(x, y)
        elif self.current_tool == "brush" and self.current_brush_stroke:  # 兼容旧版本
            self.continue_brush_stroke(x, y)
        elif self.is_drawing and self.current_tool not in ["polygon", "bezier"] and not self.current_tool.startswith("brush_"):
            self.update_temp_shape(x, y)
            
    def on_mouse_release(self, x, y):
        """鼠标释放事件"""
        if self.current_tool == "select":
            if self.resizing:
                self.resizing = False
                self.resize_handle = ""
                self.resize_shape = None
                self.save_state()  # 保存状态以支持撤销
            self.dragging = False
        elif self.current_tool.startswith("brush_") and self.current_brush_stroke:
            self.finish_brush_stroke()
        elif self.current_tool == "brush" and self.current_brush_stroke:  # 兼容旧版本
            self.finish_brush_stroke()
        elif self.is_drawing and self.current_tool not in ["polygon", "bezier"] and not self.current_tool.startswith("brush_"):
            self.finish_shape(x, y)
            
    def handle_select_press(self, x, y):
        """处理选择工具的鼠标按下"""
        # 首先检查是否点击了调整大小的控制点
        for shape in self.selected_shapes:
            handle_type = shape.get_handle_at_point(x, y)
            if handle_type:
                self.resizing = True
                self.resize_handle = handle_type
                self.resize_shape = shape
                self.drag_start_x = x
                self.drag_start_y = y
                return
        
        # 查找点击的图形
        clicked_shape = self.find_shape_at_point(x, y)
        
        if clicked_shape:
            if clicked_shape not in self.selected_shapes:
                self.clear_selection()
                self.select_shape(clicked_shape)
            # 开始拖拽
            self.dragging = True
            self.drag_start_x = x
            self.drag_start_y = y
        else:
            self.clear_selection()
            
    def handle_drag(self, x, y):
        """处理拖拽"""
        if self.selected_shapes:
            dx = x - self.drag_start_x
            dy = y - self.drag_start_y
            
            for shape in self.selected_shapes:
                shape.move(dx, dy)
                
            self.drag_start_x = x
            self.drag_start_y = y
            self.redraw()
            
    def handle_resize(self, x, y):
        """处理调整大小"""
        if self.resize_shape and self.resize_handle:
            dx = x - self.drag_start_x
            dy = y - self.drag_start_y
            
            self.resize_shape.resize_by_handle(self.resize_handle, dx, dy)
            
            self.drag_start_x = x
            self.drag_start_y = y
            self.redraw()
            
    def create_point(self, x, y):
        """创建点"""
        point = Point(x, y)
        point.set_color(self.current_color)
        point.set_fill_color(self.current_fill_color)
        point.set_line_width(self.current_line_width)
        self.add_shape(point)
        
    def start_line(self, x, y):
        """开始绘制直线"""
        self.is_drawing = True
        self.temp_shape = Line(x, y, x, y)
        self.temp_shape.set_color(self.current_color)
        self.temp_shape.set_line_width(self.current_line_width)
        
    def start_rectangle(self, x, y):
        """开始绘制矩形"""
        self.is_drawing = True
        self.temp_shape = Rectangle(x, y, x, y)
        self.temp_shape.set_color(self.current_color)
        self.temp_shape.set_fill_color(self.current_fill_color)
        self.temp_shape.set_line_width(self.current_line_width)
        
    def start_circle(self, x, y):
        """开始绘制圆形"""
        self.is_drawing = True
        self.temp_shape = Circle(x, y, 0)
        self.temp_shape.set_color(self.current_color)
        self.temp_shape.set_fill_color(self.current_fill_color)
        self.temp_shape.set_line_width(self.current_line_width)
        
    def handle_polygon_click(self, x, y):
        """处理多边形点击"""
        self.polygon_points.append((x, y))
        
        if len(self.polygon_points) >= 3:
            # 检查是否双击或点击第一个点来完成多边形
            if len(self.polygon_points) > 3:
                first_point = self.polygon_points[0]
                if abs(x - first_point[0]) < 10 and abs(y - first_point[1]) < 10:
                    # 完成多边形
                    self.finish_polygon()
                    return
                    
        # 绘制临时点
        self.redraw()
        if self.canvas:
            for px, py in self.polygon_points:
                self.canvas.create_oval(px-3, py-3, px+3, py+3, 
                                      fill="red", outline="red", tags="temp")
                                      
    def finish_polygon(self):
        """完成多边形绘制"""
        if len(self.polygon_points) >= 3:
            polygon = Polygon(self.polygon_points)
            polygon.set_color(self.current_color)
            polygon.set_fill_color(self.current_fill_color)
            polygon.set_line_width(self.current_line_width)
            self.add_shape(polygon)
            
        self.polygon_points = []
        self.redraw()
        
    def handle_bezier_click(self, x, y):
        """处理贝塞尔曲线点击"""
        self.bezier_points.append((x, y))
        
        if len(self.bezier_points) == 1:
            # 第一个点：起点
            self.bezier_step = 1
        elif len(self.bezier_points) == 2:
            # 第二个点：终点（临时）
            self.bezier_step = 2
        elif len(self.bezier_points) == 3:
            # 第三个点：第一个控制点
            self.bezier_step = 3
        elif len(self.bezier_points) == 4:
            # 第四个点：第二个控制点，完成曲线
            self.finish_bezier()
            return
            
        # 绘制临时点和指导信息
        self.redraw()
        self.draw_bezier_guide()
        
    def finish_bezier(self):
        """完成贝塞尔曲线绘制"""
        if len(self.bezier_points) == 4:
            p0, p3, p1, p2 = self.bezier_points  # 重新排列点的顺序
            bezier = BezierCurve(p0, p1, p2, p3)
            bezier.set_color(self.current_color)
            bezier.set_line_width(self.current_line_width)
            self.add_shape(bezier)
            
        self.bezier_points = []
        self.bezier_step = 0
        self.redraw()
        
    def draw_bezier_guide(self):
        """绘制贝塞尔曲线绘制指导"""
        if not self.canvas:
            return
            
        # 绘制已点击的点
        for i, (x, y) in enumerate(self.bezier_points):
            r = 4
            if i == 0:
                # 起点 - 蓝色
                color = "blue"
                label = "起点"
            elif i == 1:
                # 终点 - 蓝色
                color = "blue" 
                label = "终点"
            elif i == 2:
                # 第一个控制点 - 绿色
                color = "green"
                label = "控制点1"
            else:
                # 第二个控制点 - 绿色
                color = "green"
                label = "控制点2"
                
            self.canvas.create_oval(x-r, y-r, x+r, y+r,
                                  fill=color, outline="black", tags="temp")
            self.canvas.create_text(x, y-15, text=label, fill=color, tags="temp")
            
        # 如果有2个或更多点，绘制连接线指导
        if len(self.bezier_points) >= 2:
            p0 = self.bezier_points[0]
            p3 = self.bezier_points[1]
            self.canvas.create_line(p0[0], p0[1], p3[0], p3[1],
                                  fill="gray", dash=(3, 3), tags="temp")
                                  
        # 绘制提示信息
        if self.bezier_step == 0:
            hint = "点击设置起点"
        elif self.bezier_step == 1:
            hint = "点击设置终点"
        elif self.bezier_step == 2:
            hint = "点击设置第一个控制点"
        elif self.bezier_step == 3:
            hint = "点击设置第二个控制点完成曲线"
        else:
            hint = ""
            
        if hint and self.canvas:
            self.canvas.create_text(10, 10, anchor="nw", text=hint, 
                                  fill="red", font=("Arial", 10), tags="temp")
        
    def update_temp_shape(self, x, y):
        """更新临时图形"""
        if not self.temp_shape:
            return
            
        if isinstance(self.temp_shape, Line):
            self.temp_shape.x2 = x
            self.temp_shape.y2 = y
            self.temp_shape.x = (self.temp_shape.x1 + x) / 2
            self.temp_shape.y = (self.temp_shape.y1 + y) / 2
        elif isinstance(self.temp_shape, Rectangle):
            self.temp_shape.x1 = min(self.start_x, x)
            self.temp_shape.y1 = min(self.start_y, y)
            self.temp_shape.x2 = max(self.start_x, x)
            self.temp_shape.y2 = max(self.start_y, y)
            self.temp_shape.x = (self.temp_shape.x1 + self.temp_shape.x2) / 2
            self.temp_shape.y = (self.temp_shape.y1 + self.temp_shape.y2) / 2
            self.temp_shape.width = self.temp_shape.x2 - self.temp_shape.x1
            self.temp_shape.height = self.temp_shape.y2 - self.temp_shape.y1
        elif isinstance(self.temp_shape, Circle):
            # 椭圆创建：鼠标拉到哪是哪
            # 计算椭圆的半长轴和半短轴
            radius_x = abs(x - self.start_x)
            radius_y = abs(y - self.start_y)
            
            # 设置椭圆半径
            self.temp_shape.radius_x = max(radius_x, 1)  # 最小半径为1
            self.temp_shape.radius_y = max(radius_y, 1)  # 最小半径为1
            
            # 设置主半径为较大值
            self.temp_shape.radius = max(self.temp_shape.radius_x, self.temp_shape.radius_y)
            
        self.redraw_with_temp()
        
    def finish_shape(self, x, y):
        """完成图形绘制"""
        if self.temp_shape:
            self.add_shape(self.temp_shape)
            self.temp_shape = None
        self.is_drawing = False
        
    def start_brush_stroke(self, x, y):
        """开始笔刷轨迹"""
        self.current_brush_stroke = BrushStroke(brush_type=self.current_brush_type)
        self.current_brush_stroke.color = self.current_color
        self.current_brush_stroke.brush_size = self.current_brush_size
        self.current_brush_stroke.add_point(x, y)
        self.is_drawing = True
        
        # 为喷雾笔刷启动连续绘制定时器
        if self.current_brush_type == "brush_spray":
            self.last_spray_x = x
            self.last_spray_y = y
            self.start_spray_timer()
        
    def continue_brush_stroke(self, x, y):
        """继续笔刷轨迹"""
        if self.current_brush_stroke:
            self.current_brush_stroke.add_point(x, y)
            # 为喷雾笔刷更新位置
            if self.current_brush_type == "brush_spray":
                self.last_spray_x = x
                self.last_spray_y = y
            self.redraw()
            
    def finish_brush_stroke(self):
        """完成笔刷轨迹"""
        # 停止喷雾定时器
        self.stop_spray_timer()
        
        if self.current_brush_stroke and len(self.current_brush_stroke.points) > 1:
            self.add_shape(self.current_brush_stroke)
        self.current_brush_stroke = None
        self.is_drawing = False
        
    def start_spray_timer(self):
        """启动喷雾定时器"""
        if self.canvas and self.current_brush_type == "brush_spray":
            # 每50ms添加一次散点，实现连续喷雾效果
            self.spray_timer = self.canvas.after(20, self.spray_timer_callback)
    
    def stop_spray_timer(self):
        """停止喷雾定时器"""
        if self.canvas and self.spray_timer:
            self.canvas.after_cancel(self.spray_timer)
            self.spray_timer = None
    
    def spray_timer_callback(self):
        """喷雾定时器回调"""
        if (self.current_brush_stroke and 
            self.current_brush_type == "brush_spray" and 
            self.is_drawing):
            
            # 在当前位置添加散点
            self.current_brush_stroke.add_point(self.last_spray_x, self.last_spray_y)
            
            # 增量绘制新添加的散点，避免重绘整个画布
            if self.canvas and self.current_brush_stroke.spray_dots:
                # 只绘制最新添加的散点
                last_dots = self.current_brush_stroke.spray_dots[-4:]  # 最后4个散点
                for x, y, dot_size in last_dots:
                    self.canvas.create_oval(x - dot_size, y - dot_size,
                                          x + dot_size, y + dot_size,
                                          fill=self.current_brush_stroke.color,
                                          outline=self.current_brush_stroke.color,
                                          tags="brush_stroke")
            
            # 继续定时器
            self.start_spray_timer()
        
    def add_shape(self, shape):
        """添加图形"""
        self.shapes.append(shape)
        self.save_state()
        self.redraw()
        
    def find_shape_at_point(self, x, y) -> Optional[BaseShape]:
        """查找指定点处的图形"""
        # 从后往前查找（最后绘制的在最上层）
        for shape in reversed(self.shapes):
            if shape.contains_point(x, y):
                return shape
        return None
        
    def select_shape(self, shape):
        """选中图形"""
        shape.set_selected(True)
        self.selected_shapes.append(shape)
        self.redraw()
        
    def clear_selection(self):
        """清除选择"""
        for shape in self.selected_shapes:
            shape.set_selected(False)
        self.selected_shapes.clear()
        self.redraw()
        
    def select_all(self):
        """全选"""
        self.clear_selection()
        for shape in self.shapes:
            self.select_shape(shape)
            
    def delete_selected(self):
        """删除选中的图形"""
        for shape in self.selected_shapes:
            if shape in self.shapes:
                self.shapes.remove(shape)
        self.selected_shapes.clear()
        self.save_state()
        self.redraw()
        
    def copy(self):
        """复制选中的图形"""
        self.clipboard = [shape.to_dict() for shape in self.selected_shapes]
        
    def paste(self):
        """粘贴图形"""
        if not self.clipboard:
            return
            
        self.clear_selection()
        for shape_data in self.clipboard:
            # 创建图形副本并稍微偏移位置
            shape_data = shape_data.copy()
            shape_data['x'] += 20
            shape_data['y'] += 20
            
            # 根据类型创建图形
            shape = self.create_shape_from_dict(shape_data)
            if shape:
                self.shapes.append(shape)
                self.select_shape(shape)
                
        self.save_state()
        self.redraw()
        
    def create_shape_from_dict(self, data):
        """从字典数据创建图形"""
        shape_type = data.get('type')
        
        if shape_type == 'Point':
            return Point.from_dict(data)
        elif shape_type == 'Line':
            return Line.from_dict(data)
        elif shape_type == 'Rectangle':
            return Rectangle.from_dict(data)
        elif shape_type == 'Circle':
            return Circle.from_dict(data)
        elif shape_type == 'Polygon':
            return Polygon.from_dict(data)
        elif shape_type == 'BezierCurve':
            return BezierCurve.from_dict(data)
        
        return None
        
    def clear(self):
        """清空所有图形"""
        self.shapes.clear()
        self.selected_shapes.clear()
        self.polygon_points.clear()
        self.bezier_points.clear()
        self.bezier_step = 0
        self.temp_shape = None
        self.is_drawing = False
        self.save_state()
        self.redraw()
        
    def redraw(self):
        """重新绘制所有图形"""
        if not self.canvas:
            return
            
        # 清除所有图形和辅助元素
        self.canvas.delete("shape")
        self.canvas.delete("temp")
        self.canvas.delete("resize_handle")
        self.canvas.delete("brush_stroke")
        self.canvas.delete("selection")  # 清除选择框和调整手柄
        
        # 绘制所有图形
        for shape in self.shapes:
            shape.draw(self.canvas)
            
        # 绘制当前正在绘制的笔刷轨迹
        if self.current_brush_stroke and len(self.current_brush_stroke.points) > 1:
            self.current_brush_stroke.draw(self.canvas)
            
    def redraw_with_temp(self):
        """重新绘制包括临时图形"""
        self.redraw()
        if self.temp_shape and self.canvas:
            self.temp_shape.draw(self.canvas)
            
    def save_state(self):
        """保存当前状态到历史记录"""
        # 移除当前位置之后的历史
        self.history = self.history[:self.history_index + 1]
        
        # 保存当前状态
        state = [shape.to_dict() for shape in self.shapes]
        self.history.append(state)
        
        # 限制历史记录数量
        if len(self.history) > self.max_history:
            self.history.pop(0)
        else:
            self.history_index += 1
            
    def undo(self):
        """撤销"""
        if self.history_index > 0:
            self.history_index -= 1
            self.restore_state(self.history[self.history_index])
            
    def redo(self):
        """重做"""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.restore_state(self.history[self.history_index])
            
    def restore_state(self, state):
        """恢复状态"""
        self.shapes.clear()
        self.selected_shapes.clear()
        
        for shape_data in state:
            shape = self.create_shape_from_dict(shape_data)
            if shape:
                self.shapes.append(shape)
                
        self.redraw()
        
    def save_to_file(self, filename):
        """保存到文件"""
        data = {
            'version': '1.0',
            'shapes': [shape.to_dict() for shape in self.shapes]
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
    def load_from_file(self, filename):
        """从文件加载"""
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        self.clear()
        
        for shape_data in data.get('shapes', []):
            shape = self.create_shape_from_dict(shape_data)
            if shape:
                self.shapes.append(shape)
                
        self.save_state()
        self.redraw()
        
    def export_image(self, filename):
        """导出为图片"""
        if not self.shapes:
            # 如果没有图形，创建一个空白图像
            image = Image.new('RGB', (800, 600), 'white')
            image.save(filename)
            return
            
        # 计算边界
        bounds = self.get_all_bounds()
        if not bounds:
            return
            
        x1, y1, x2, y2 = bounds
        width = int(x2 - x1) + 40  # 添加边距
        height = int(y2 - y1) + 40
        
        # 创建PIL图像
        image = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(image)
        
        # 偏移量，用于居中图形
        offset_x = 20 - x1
        offset_y = 20 - y1
        
        # 绘制所有图形
        for shape in self.shapes:
            self.draw_shape_to_image(draw, shape, offset_x, offset_y)
        
        image.save(filename)
        
    def draw_shape_to_image(self, draw, shape, offset_x, offset_y):
        """将图形绘制到PIL图像上"""
        from shapes import Point, Line, Rectangle, Circle, Polygon, BezierCurve
        
        # 转换颜色格式
        fill_color = shape.fill_color if hasattr(shape, 'fill_color') and shape.fill_color else None
        outline_color = shape.color if hasattr(shape, 'color') else 'black'
        line_width = shape.line_width if hasattr(shape, 'line_width') else 1
        
        if isinstance(shape, Point):
            x = shape.x + offset_x
            y = shape.y + offset_y
            r = max(line_width, 2)
            draw.ellipse([x-r, y-r, x+r, y+r], fill=outline_color)
            
        elif isinstance(shape, Line):
            x1 = shape.x1 + offset_x
            y1 = shape.y1 + offset_y
            x2 = shape.x2 + offset_x
            y2 = shape.y2 + offset_y
            draw.line([x1, y1, x2, y2], fill=outline_color, width=line_width)
            
        elif isinstance(shape, Rectangle):
            x1 = shape.x + offset_x
            y1 = shape.y + offset_y
            x2 = shape.x + shape.width + offset_x
            y2 = shape.y + shape.height + offset_y
            draw.rectangle([x1, y1, x2, y2], fill=fill_color, outline=outline_color, width=line_width)
            
        elif isinstance(shape, Circle):
            x1 = shape.x - shape.radius + offset_x
            y1 = shape.y - shape.radius + offset_y
            x2 = shape.x + shape.radius + offset_x
            y2 = shape.y + shape.radius + offset_y
            draw.ellipse([x1, y1, x2, y2], fill=fill_color, outline=outline_color, width=line_width)
            
        elif isinstance(shape, Polygon):
            points = [(p[0] + offset_x, p[1] + offset_y) for p in shape.points]
            if len(points) >= 3:
                draw.polygon(points, fill=fill_color, outline=outline_color)
                
        elif isinstance(shape, BezierCurve):
            # 绘制贝塞尔曲线
            points = []
            for t in range(101):  # 100段
                t_normalized = t / 100.0
                x, y = shape.bezier_point(t_normalized)
                points.append((x + offset_x, y + offset_y))
            
            # 绘制曲线
            for i in range(len(points) - 1):
                draw.line([points[i], points[i + 1]], fill=outline_color, width=line_width)
                
        elif isinstance(shape, BrushStroke):
            # 绘制笔刷轨迹
            if len(shape.points) >= 2:
                for i in range(len(shape.points) - 1):
                    x1 = shape.points[i][0] + offset_x
                    y1 = shape.points[i][1] + offset_y
                    x2 = shape.points[i + 1][0] + offset_x
                    y2 = shape.points[i + 1][1] + offset_y
                    draw.line([x1, y1, x2, y2], fill=outline_color, width=shape.brush_size)
        
    def get_all_bounds(self):
        """获取所有图形的边界"""
        if not self.shapes:
            return None
            
        bounds = []
        for shape in self.shapes:
            bounds.append(shape.get_bounds())
            
        x1 = min(b[0] for b in bounds)
        y1 = min(b[1] for b in bounds)
        x2 = max(b[2] for b in bounds)
        y2 = max(b[3] for b in bounds)
        
        return (x1, y1, x2, y2)
    
    def import_image(self, x: float, y: float):
        """导入图片"""
        from tkinter import filedialog
        
        # 打开文件选择对话框
        file_path = filedialog.askopenfilename(
            title="选择图片文件",
            filetypes=[
                ("图片文件", "*.jpg *.jpeg *.png *.gif *.bmp *.tiff"),
                ("JPEG文件", "*.jpg *.jpeg"),
                ("PNG文件", "*.png"),
                ("GIF文件", "*.gif"),
                ("BMP文件", "*.bmp"),
                ("TIFF文件", "*.tiff"),
                ("所有文件", "*.*")
            ]
        )
        
        if file_path:
            # 先创建临时图像对象获取原始尺寸
            temp_image = ImageShape(0, 0, 100, 100, file_path)
            
            if temp_image.pil_image:  # 确保图片加载成功
                # 获取原始图片尺寸
                original_width = temp_image.original_width
                original_height = temp_image.original_height
                
                # 计算合适的显示尺寸，保持长宽比
                max_size = 300  # 最大边长
                if original_width > original_height:
                    # 宽图
                    display_width = min(max_size, original_width)
                    display_height = int(display_width * original_height / original_width)
                else:
                    # 高图
                    display_height = min(max_size, original_height)
                    display_width = int(display_height * original_width / original_height)
                
                # 以点击位置为中心创建图像
                x1 = x - display_width // 2
                y1 = y - display_height // 2
                x2 = x + display_width // 2
                y2 = y + display_height // 2
                
                # 创建正确尺寸的图像对象
                image_shape = ImageShape(x1, y1, x2, y2, file_path)
            
            if image_shape.pil_image:  # 确保图片加载成功
                # 应用当前的填充和边框设置
                image_shape.color = self.current_color
                image_shape.fill_color = self.current_fill_color
                image_shape.line_width = self.current_line_width
                
                # 添加到形状列表
                self.add_shape(image_shape)
                
                # 自动选择新创建的图像
                self.clear_selection()
                image_shape.selected = True
                self.selected_shapes = [image_shape]
                
                # 重绘画布
                self.redraw()
                
                print(f"图片导入成功: {file_path}")
            else:
                print(f"图片加载失败: {file_path}")