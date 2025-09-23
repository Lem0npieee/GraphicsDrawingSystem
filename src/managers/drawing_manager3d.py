"""
3D绘图管理器 - 负责3D图形的创建、管理和渲染
"""
import json
import os
import sys
from typing import List, Optional, Tuple

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shapes3d import BaseShape3D, Point3D, Vector3D, Cube3D, Sphere3D, Pyramid3D, Cone3D


class DrawingManager3D:
    """3D绘图管理器类"""
    
    def __init__(self):
        self.shapes: List[BaseShape3D] = []  # 所有3D图形列表
        self.selected_shapes: List[BaseShape3D] = []  # 选中的图形列表
        self.canvas3d = None  # 3D画布引用
        
        # 当前绘制状态
        self.current_tool = "select"
        self.current_color = "black"  # 与属性面板默认值一致
        self.current_fill_color = "white"  # 默认白色填充
        self.current_line_width = 1  # 与属性面板默认值一致
        
        # 绘制状态变量
        self.is_drawing = False
        self.temp_shape = None
        
        # 撤销/重做
        self.history = []  # 历史记录
        self.history_index = -1  # 当前历史位置
        self.max_history = 50  # 最大历史记录数
        
    def set_canvas3d(self, canvas3d):
        """设置3D画布引用"""
        self.canvas3d = canvas3d
    
    def create_shape(self, tool_name: str, x: float = 0, y: float = 0, z: float = 0, **kwargs) -> Optional[BaseShape3D]:
        """根据工具名称创建3D图形"""
        shape = None
        
        if tool_name == "point3d":
            shape = Point3D(x, y, z)
        elif tool_name == "vector3d":
            vx = kwargs.get("vx", 1)
            vy = kwargs.get("vy", 0)
            vz = kwargs.get("vz", 0)
            shape = Vector3D(x, y, z, vx, vy, vz)
        elif tool_name == "cube3d":
            size = kwargs.get("size", 2.0)
            shape = Cube3D(x, y, z, size)
        elif tool_name == "sphere3d":
            radius = kwargs.get("radius", 1.0)
            shape = Sphere3D(x, y, z, radius)
        elif tool_name == "pyramid3d":
            base_size = kwargs.get("base_size", 2.0)
            height = kwargs.get("height", 2.0)
            shape = Pyramid3D(x, y, z, base_size, height)
        elif tool_name == "cone3d":
            radius = kwargs.get("radius", 1.0)
            height = kwargs.get("height", 2.0)
            shape = Cone3D(x, y, z, radius, height)
        
        if shape:
            # 设置当前属性
            shape.set_color(self.current_color)
            shape.set_fill_color(self.current_fill_color)
            shape.set_line_width(self.current_line_width)
            
        return shape
    
    def add_shape(self, shape: BaseShape3D):
        """添加图形到画布"""
        if shape:
            self.shapes.append(shape)
            if self.canvas3d:
                self.canvas3d.add_shape(shape)
            self.save_state()  # 保存状态用于撤销
    
    def remove_shape(self, shape: BaseShape3D):
        """移除图形"""
        if shape in self.shapes:
            self.shapes.remove(shape)
            if shape in self.selected_shapes:
                self.selected_shapes.remove(shape)
            if self.canvas3d:
                self.canvas3d.remove_shape(shape)
            self.save_state()
    
    def select_shape(self, shape: BaseShape3D):
        """选择图形"""
        self.clear_selection()
        if shape:
            self.selected_shapes.append(shape)
            shape.selected = True
            if self.canvas3d:
                self.canvas3d._select_shape_internal(shape)
    
    def clear_selection(self):
        """清除选择"""
        for shape in self.selected_shapes:
            shape.selected = False
        self.selected_shapes.clear()
        if self.canvas3d:
            self.canvas3d._select_shape_internal(None)
    
    def delete_selected(self):
        """删除选中的图形"""
        for shape in self.selected_shapes[:]:  # 复制列表避免迭代时修改
            self.remove_shape(shape)
        self.clear_selection()
    
    def clear(self):
        """清空所有图形"""
        self.shapes.clear()
        self.selected_shapes.clear()
        if self.canvas3d:
            self.canvas3d.clear_objects()
        self.save_state()
    
    # 鼠标事件处理
    def on_mouse_press(self, screen_x: float, screen_y: float, tool_name: str):
        """鼠标按下事件"""
        if tool_name == "select":
            # TODO: 实现3D选择逻辑
            pass
        else:
            # 创建新图形
            # 将屏幕坐标转换为3D坐标（简化：默认放在原点）
            world_pos = self.screen_to_world(screen_x, screen_y)
            shape = self.create_shape(tool_name, world_pos[0], world_pos[1], world_pos[2])
            if shape:
                self.add_shape(shape)
    
    def screen_to_world(self, screen_x: float, screen_y: float) -> Tuple[float, float, float]:
        """将屏幕坐标转换为世界坐标（简化版本）"""
        # 简化：将新图形放在原点附近的随机位置
        import random
        return (
            random.uniform(-2, 2),
            random.uniform(-2, 2), 
            random.uniform(-2, 2)
        )
    
    # 属性设置
    def set_current_color(self, color: str):
        """设置当前颜色"""
        self.current_color = color
        # 应用到选中的图形
        for shape in self.selected_shapes:
            shape.set_color(color)
        if self.canvas3d:
            self.canvas3d.redraw()
    
    def set_current_fill_color(self, fill_color: str):
        """设置当前填充颜色"""
        self.current_fill_color = fill_color
        for shape in self.selected_shapes:
            shape.set_fill_color(fill_color)
        if self.canvas3d:
            self.canvas3d.redraw()
    
    def set_current_line_width(self, line_width: int):
        """设置当前线宽"""
        self.current_line_width = line_width
        for shape in self.selected_shapes:
            shape.set_line_width(line_width)
        if self.canvas3d:
            self.canvas3d.redraw()
    
    # 变换操作
    def move_selected(self, dx: float, dy: float, dz: float):
        """移动选中的图形"""
        for shape in self.selected_shapes:
            shape.move(dx, dy, dz)
        if self.canvas3d:
            self.canvas3d.redraw()
    
    def rotate_selected(self, rx: float, ry: float, rz: float):
        """旋转选中的图形"""
        for shape in self.selected_shapes:
            shape.rotate(rx, ry, rz)
        if self.canvas3d:
            self.canvas3d.redraw()
    
    def scale_selected(self, sx: float, sy: float = None, sz: float = None):
        """缩放选中的图形"""
        for shape in self.selected_shapes:
            shape.scale(sx, sy, sz)
        if self.canvas3d:
            self.canvas3d.redraw()
    
    # 撤销/重做
    def save_state(self):
        """保存当前状态"""
        # 序列化当前状态
        state = {
            'shapes': [shape.to_dict() for shape in self.shapes]
        }
        
        # 如果不是在历史中间，清除后续历史
        if self.history_index < len(self.history) - 1:
            self.history = self.history[:self.history_index + 1]
        
        # 添加新状态
        self.history.append(state)
        self.history_index += 1
        
        # 限制历史记录数量
        if len(self.history) > self.max_history:
            self.history.pop(0)
            self.history_index -= 1
    
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
        
        for shape_data in state['shapes']:
            shape = self.create_shape_from_dict(shape_data)
            if shape:
                self.shapes.append(shape)
        
        if self.canvas3d:
            self.canvas3d.clear_objects()
            for shape in self.shapes:
                self.canvas3d.add_shape(shape)
    
    def create_shape_from_dict(self, data: dict) -> Optional[BaseShape3D]:
        """从字典创建图形"""
        shape_type = data.get('type')
        shape = None
        
        if shape_type == 'Point3D':
            shape = Point3D()
        elif shape_type == 'Vector3D':
            shape = Vector3D()
        elif shape_type == 'Cube3D':
            shape = Cube3D()
        elif shape_type == 'Sphere3D':
            shape = Sphere3D()
        elif shape_type == 'Pyramid3D':
            shape = Pyramid3D()
        elif shape_type == 'Cone3D':
            shape = Cone3D()
        
        if shape:
            shape.from_dict(data)
        
        return shape
    
    # 文件操作
    def save_to_file(self, filename: str):
        """保存到文件"""
        data = {
            'version': '1.0',
            'mode': '3D',
            'shapes': [shape.to_dict() for shape in self.shapes]
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def load_from_file(self, filename: str):
        """从文件加载"""
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if data.get('mode') != '3D':
            raise ValueError("文件不是3D场景文件")
        
        self.clear()
        
        for shape_data in data.get('shapes', []):
            shape = self.create_shape_from_dict(shape_data)
            if shape:
                self.add_shape(shape)