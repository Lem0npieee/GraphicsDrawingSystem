"""
3D球体图形
"""
from .base_shape3d import BaseShape3D
from typing import List, Tuple
import math


class Sphere3D(BaseShape3D):
    """3D球体类"""
    
    def __init__(self, x: float = 0, y: float = 0, z: float = 0, radius: float = 1.0):
        super().__init__(x, y, z)
        self.radius = radius  # 球体半径
        self.segments = 16  # 分段数（影响显示精度）
        
    def get_vertices(self) -> List[Tuple[float, float, float]]:
        """获取球体的顶点（使用经纬线划分）"""
        vertices = []
        
        # 添加顶点和底点
        vertices.append((0, self.radius, 0))  # 顶点
        
        # 中间的纬线
        for i in range(1, self.segments):
            phi = math.pi * i / self.segments  # 纬度角
            y = self.radius * math.cos(phi)
            radius_at_phi = self.radius * math.sin(phi)
            
            # 每条纬线上的点
            for j in range(self.segments):
                theta = 2 * math.pi * j / self.segments  # 经度角
                x = radius_at_phi * math.cos(theta)
                z = radius_at_phi * math.sin(theta)
                vertices.append((x, y, z))
        
        vertices.append((0, -self.radius, 0))  # 底点
        
        return self.apply_vertex_transform(vertices)
    
    def get_edges(self) -> List[Tuple[int, int]]:
        """获取球体的边（经线和纬线）"""
        edges = []
        
        # 从顶点到第一条纬线的经线
        for j in range(self.segments):
            edges.append((0, 1 + j))
        
        # 纬线
        for i in range(self.segments - 1):
            for j in range(self.segments):
                curr = 1 + i * self.segments + j
                next_j = 1 + i * self.segments + ((j + 1) % self.segments)
                edges.append((curr, next_j))
        
        # 经线（垂直线）
        for i in range(self.segments - 2):
            for j in range(self.segments):
                curr = 1 + i * self.segments + j
                down = 1 + (i + 1) * self.segments + j
                edges.append((curr, down))
        
        # 从最后一条纬线到底点的经线
        bottom_idx = len(self.get_vertices()) - 1
        for j in range(self.segments):
            last_ring_start = 1 + (self.segments - 2) * self.segments
            edges.append((last_ring_start + j, bottom_idx))
        
        return edges
    
    def get_faces(self) -> List[List[int]]:
        """获取球体的面（三角形面片）"""
        faces = []
        
        # 顶部三角形
        for j in range(self.segments):
            next_j = (j + 1) % self.segments
            faces.append([0, 1 + j, 1 + next_j])
        
        # 中间的四边形面（分为两个三角形）
        for i in range(self.segments - 2):
            for j in range(self.segments):
                curr = 1 + i * self.segments + j
                next_j = 1 + i * self.segments + ((j + 1) % self.segments)
                down = 1 + (i + 1) * self.segments + j
                down_next = 1 + (i + 1) * self.segments + ((j + 1) % self.segments)
                
                # 分为两个三角形
                faces.append([curr, down, next_j])
                faces.append([next_j, down, down_next])
        
        # 底部三角形
        bottom_idx = len(self.get_vertices()) - 1
        last_ring_start = 1 + (self.segments - 2) * self.segments
        for j in range(self.segments):
            next_j = (j + 1) % self.segments
            faces.append([bottom_idx, last_ring_start + next_j, last_ring_start + j])
        
        return faces
    
    def contains_point(self, x: float, y: float, z: float) -> bool:
        """检查点是否在球体内部"""
        # 计算到球心的距离
        dx = x - self.x
        dy = y - self.y
        dz = z - self.z
        
        # 考虑缩放
        dx /= self.scale_x
        dy /= self.scale_y
        dz /= self.scale_z
        
        distance_sq = dx*dx + dy*dy + dz*dz
        return distance_sq <= self.radius * self.radius
    
    def get_bounds(self) -> Tuple[float, float, float, float, float, float]:
        """获取球体的边界框"""
        r_x = self.radius * self.scale_x
        r_y = self.radius * self.scale_y
        r_z = self.radius * self.scale_z
        
        return (
            self.x - r_x, self.y - r_y, self.z - r_z,
            self.x + r_x, self.y + r_y, self.z + r_z
        )
    
    def set_radius(self, radius: float):
        """设置球体半径"""
        self.radius = max(0.1, radius)
    
    def set_segments(self, segments: int):
        """设置分段数"""
        self.segments = max(4, segments)
    
    def to_dict(self):
        """转换为字典"""
        data = super().to_dict()
        data.update({
            'radius': self.radius,
            'segments': self.segments
        })
        return data
    
    def from_dict(self, data):
        """从字典加载"""
        super().from_dict(data)
        self.radius = data.get('radius', 1.0)
        self.segments = data.get('segments', 16)