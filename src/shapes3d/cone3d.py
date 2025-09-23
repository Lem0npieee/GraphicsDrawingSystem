"""
3D圆锥图形
"""
from .base_shape3d import BaseShape3D
from typing import List, Tuple
import math


class Cone3D(BaseShape3D):
    """3D圆锥类"""
    
    def __init__(self, x: float = 0, y: float = 0, z: float = 0, 
                 radius: float = 1.0, height: float = 1.0):
        super().__init__(x, y, z)
        self.radius = radius  # 底面半径
        self.height = height  # 高度
        self.segments = 16  # 底面圆的分段数
        
    def get_vertices(self) -> List[Tuple[float, float, float]]:
        """获取圆锥的顶点"""
        vertices = []
        
        # 底面圆心（在y=-height/2，即底部）
        vertices.append((0, -self.height/2, 0))  # 0: 底面圆心
        
        # 底面圆周上的点（在XZ平面上）
        for i in range(self.segments):
            angle = 2 * math.pi * i / self.segments
            x = self.radius * math.cos(angle)
            z = self.radius * math.sin(angle)
            y = -self.height / 2  # 底面在y=-height/2
            vertices.append((x, y, z))
        
        # 顶点（在y=height/2，即顶部）
        vertices.append((0, self.height/2, 0))  # 最后一个: 圆锥顶点
        
        return self.apply_vertex_transform(vertices)
    
    def get_edges(self) -> List[Tuple[int, int]]:
        """获取圆锥的边"""
        edges = []
        
        # 底面圆周的边
        for i in range(self.segments):
            curr = 1 + i
            next_vertex = 1 + ((i + 1) % self.segments)
            edges.append((curr, next_vertex))
        
        # 从底面圆心到圆周的边（可选，用于显示底面结构）
        for i in range(self.segments):
            edges.append((0, 1 + i))
        
        # 从圆周到顶点的边
        apex_idx = len(self.get_vertices()) - 1
        for i in range(self.segments):
            edges.append((1 + i, apex_idx))
        
        return edges
    
    def get_faces(self) -> List[List[int]]:
        """获取圆锥的面"""
        faces = []
        apex_idx = 1 + self.segments  # 顶点索引
        
        # 底面（三角形扇形）
        for i in range(self.segments):
            next_i = (i + 1) % self.segments
            faces.append([0, 1 + next_i, 1 + i])  # 顺时针
        
        # 侧面（三角形）
        for i in range(self.segments):
            next_i = (i + 1) % self.segments
            faces.append([1 + i, 1 + next_i, apex_idx])
        
        return faces
    
    def contains_point(self, x: float, y: float, z: float) -> bool:
        """检查点是否在圆锥内部"""
        # 转换到局部坐标系
        local_x = (x - self.x) / self.scale_x
        local_y = (y - self.y) / self.scale_y
        local_z = (z - self.z) / self.scale_z
        
        # 检查y范围（现在锥体沿Y轴）
        if local_y < -self.height/2 or local_y > self.height/2:
            return False
        
        # 根据y位置计算当前层的半径
        if local_y <= 0:
            # 在底部
            distance_from_axis = math.sqrt(local_x*local_x + local_z*local_z)
            return distance_from_axis <= self.radius
        else:
            # 在锥形部分，线性收缩
            t = local_y / (self.height/2)  # 0到1
            current_radius = self.radius * (1 - t)
            distance_from_axis = math.sqrt(local_x*local_x + local_z*local_z)
            return distance_from_axis <= current_radius
    
    def get_bounds(self) -> Tuple[float, float, float, float, float, float]:
        """获取圆锥的边界框"""
        vertices = self.get_vertices()
        if not vertices:
            return (self.x, self.y, self.z, self.x, self.y, self.z)
            
        xs = [v[0] for v in vertices]
        ys = [v[1] for v in vertices]
        zs = [v[2] for v in vertices]
        
        return (min(xs), min(ys), min(zs), max(xs), max(ys), max(zs))
    
    def set_radius(self, radius: float):
        """设置底面半径"""
        self.radius = max(0.1, radius)
    
    def set_height(self, height: float):
        """设置高度"""
        self.height = max(0.1, height)
    
    def set_segments(self, segments: int):
        """设置分段数"""
        self.segments = max(3, segments)
    
    def to_dict(self):
        """转换为字典"""
        data = super().to_dict()
        data.update({
            'radius': self.radius,
            'height': self.height,
            'segments': self.segments
        })
        return data
    
    def from_dict(self, data):
        """从字典加载"""
        super().from_dict(data)
        self.radius = data.get('radius', 1.0)
        self.height = data.get('height', 1.0)
        self.segments = data.get('segments', 16)