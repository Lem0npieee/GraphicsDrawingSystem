"""
3D图形基类 - 所有3D图形的父类
"""
import json
import math
from abc import ABC, abstractmethod
from typing import Tuple, Dict, Any, List, Optional


class BaseShape3D(ABC):
    """所有3D图形的基础类"""
    
    def __init__(self, x: float = 0, y: float = 0, z: float = 0):
        # 位置
        self.x = x
        self.y = y 
        self.z = z
        
        # 旋转（弧度）
        self.rotation_x = 0.0
        self.rotation_y = 0.0
        self.rotation_z = 0.0
        
        # 缩放
        self.scale_x = 1.0
        self.scale_y = 1.0
        self.scale_z = 1.0
        
        # 显示属性
        self.color = "black"  # 线条颜色
        self.fill_color = None  # 填充颜色
        self.line_width = 1  # 线宽
        self.selected = False  # 是否被选中
        self.visible = True  # 是否可见
        
        # 交互属性
        self.selectable = True  # 是否可选择
        self.movable = True  # 是否可移动
        self.rotatable = True  # 是否可旋转
        self.scalable = True  # 是否可缩放
        
    @abstractmethod
    def get_vertices(self) -> List[Tuple[float, float, float]]:
        """获取3D顶点列表（应用变换后）"""
        pass
    
    @abstractmethod
    def get_edges(self) -> List[Tuple[int, int]]:
        """获取边列表（顶点索引对）"""
        pass
    
    @abstractmethod
    def get_faces(self) -> List[List[int]]:
        """获取面列表（顶点索引列表）"""
        pass
    
    @abstractmethod
    def contains_point(self, x: float, y: float, z: float) -> bool:
        """检查点(x,y,z)是否在图形内部"""
        pass
    
    @abstractmethod
    def get_bounds(self) -> Tuple[float, float, float, float, float, float]:
        """获取图形的3D边界框 (x1, y1, z1, x2, y2, z2)"""
        pass
    
    def move(self, dx: float, dy: float, dz: float):
        """移动图形"""
        if self.movable:
            self.x += dx
            self.y += dy
            self.z += dz
    
    def translate(self, dx: float, dy: float, dz: float):
        """平移图形（move的别名）"""
        self.move(dx, dy, dz)
    
    def rotate(self, rx: float, ry: float, rz: float):
        """旋转图形（弧度）"""
        if self.rotatable:
            self.rotation_x += rx
            self.rotation_y += ry
            self.rotation_z += rz
    
    def scale(self, sx: float, sy: float = None, sz: float = None):
        """缩放图形"""
        if self.scalable:
            if sy is None:
                sy = sx
            if sz is None:
                sz = sx
            self.scale_x *= sx
            self.scale_y *= sy
            self.scale_z *= sz
    
    def set_position(self, x: float, y: float, z: float):
        """设置位置"""
        self.x = x
        self.y = y
        self.z = z
    
    def set_rotation(self, rx: float, ry: float, rz: float):
        """设置旋转（弧度）"""
        self.rotation_x = rx
        self.rotation_y = ry
        self.rotation_z = rz
    
    def set_scale(self, sx: float, sy: float = None, sz: float = None):
        """设置缩放"""
        if sy is None:
            sy = sx
        if sz is None:
            sz = sx
        self.scale_x = sx
        self.scale_y = sy
        self.scale_z = sz
    
    def set_color(self, color: str):
        """设置线条颜色"""
        self.color = color
    
    def set_fill_color(self, color: str):
        """设置填充颜色"""
        self.fill_color = color
    
    def set_line_width(self, width: int):
        """设置线宽"""
        self.line_width = width
    
    def apply_transform_matrix(self, matrix):
        """应用变换矩阵（直接操作图形的变换属性）"""
        # 这是一个简化的实现，实际应该通过矩阵分解获取变换参数
        # 对于缩放矩阵，我们可以直接从对角线元素获取缩放因子
        if isinstance(matrix, list) and len(matrix) == 4 and len(matrix[0]) == 4:
            # 检查是否是缩放矩阵（对角线矩阵）
            if (matrix[0][1] == 0 and matrix[0][2] == 0 and 
                matrix[1][0] == 0 and matrix[1][2] == 0 and 
                matrix[2][0] == 0 and matrix[2][1] == 0):
                # 这是一个缩放矩阵
                self.scale_x *= matrix[0][0]
                self.scale_y *= matrix[1][1] 
                self.scale_z *= matrix[2][2]
            else:
                # 这是一个旋转矩阵，我们需要提取旋转角度
                # 简化处理：直接累加小的旋转增量
                self._apply_rotation_matrix(matrix)
    
    def _apply_rotation_matrix(self, matrix):
        """应用旋转矩阵（简化实现）"""
        # 从旋转矩阵提取欧拉角（简化实现）
        # 这是一个近似的实现，仅适用于小角度旋转
        if abs(matrix[2][0]) < 0.99999:
            rotation_y = math.atan2(matrix[2][0], matrix[2][2])
            rotation_x = math.atan2(-matrix[2][1], math.sqrt(matrix[2][0]**2 + matrix[2][2]**2))
            rotation_z = math.atan2(matrix[1][0], matrix[0][0])
        else:
            rotation_z = 0
            if matrix[2][0] < 0:
                rotation_y = math.pi / 2
                rotation_x = rotation_z + math.atan2(matrix[0][1], matrix[0][2])
            else:
                rotation_y = -math.pi / 2
                rotation_x = -rotation_z + math.atan2(-matrix[0][1], -matrix[0][2])
        
        # 累加旋转
        self.rotation_x += rotation_x
        self.rotation_y += rotation_y
        self.rotation_z += rotation_z
    
    # 为了向后兼容，添加别名方法
    def apply_transform(self, matrix):
        """应用变换矩阵（别名方法）"""
        self.apply_transform_matrix(matrix)
    
    def set_fill_color(self, fill_color: str):
        """设置填充颜色"""
        self.fill_color = fill_color
    
    def set_line_width(self, width: int):
        """设置线宽"""
        self.line_width = width
    
    def get_center(self) -> Tuple[float, float, float]:
        """获取图形中心点"""
        return (self.x, self.y, self.z)
    
    def apply_vertex_transform(self, vertices: List[Tuple[float, float, float]]) -> List[Tuple[float, float, float]]:
        """对顶点应用变换（缩放、旋转、平移）"""
        transformed = []
        
        for vx, vy, vz in vertices:
            # 1. 缩放
            vx *= self.scale_x
            vy *= self.scale_y
            vz *= self.scale_z
            
            # 2. 旋转（按照 X -> Y -> Z 顺序）
            # X轴旋转
            if self.rotation_x != 0:
                cos_x = math.cos(self.rotation_x)
                sin_x = math.sin(self.rotation_x)
                new_y = vy * cos_x - vz * sin_x
                new_z = vy * sin_x + vz * cos_x
                vy, vz = new_y, new_z
            
            # Y轴旋转
            if self.rotation_y != 0:
                cos_y = math.cos(self.rotation_y)
                sin_y = math.sin(self.rotation_y)
                new_x = vx * cos_y + vz * sin_y
                new_z = -vx * sin_y + vz * cos_y
                vx, vz = new_x, new_z
            
            # Z轴旋转
            if self.rotation_z != 0:
                cos_z = math.cos(self.rotation_z)
                sin_z = math.sin(self.rotation_z)
                new_x = vx * cos_z - vy * sin_z
                new_y = vx * sin_z + vy * cos_z
                vx, vy = new_x, new_y
            
            # 3. 平移
            vx += self.x
            vy += self.y
            vz += self.z
            
            transformed.append((vx, vy, vz))
        
        return transformed
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典（用于保存）"""
        return {
            'type': self.__class__.__name__,
            'x': self.x,
            'y': self.y,
            'z': self.z,
            'rotation_x': self.rotation_x,
            'rotation_y': self.rotation_y,
            'rotation_z': self.rotation_z,
            'scale_x': self.scale_x,
            'scale_y': self.scale_y,
            'scale_z': self.scale_z,
            'color': self.color,
            'fill_color': self.fill_color,
            'line_width': self.line_width,
            'visible': self.visible
        }
    
    def from_dict(self, data: Dict[str, Any]):
        """从字典加载（用于读取）"""
        self.x = data.get('x', 0)
        self.y = data.get('y', 0)
        self.z = data.get('z', 0)
        self.rotation_x = data.get('rotation_x', 0)
        self.rotation_y = data.get('rotation_y', 0)
        self.rotation_z = data.get('rotation_z', 0)
        self.scale_x = data.get('scale_x', 1.0)
        self.scale_y = data.get('scale_y', 1.0)
        self.scale_z = data.get('scale_z', 1.0)
        self.color = data.get('color', 'black')
        self.fill_color = data.get('fill_color', None)
        self.line_width = data.get('line_width', 1)
        self.visible = data.get('visible', True)