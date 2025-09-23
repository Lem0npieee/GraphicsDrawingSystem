"""
3D点图形
"""
from .base_shape3d import BaseShape3D
from typing import List, Tuple
import math


class Point3D(BaseShape3D):
    """3D点类 - 显示为实心小球"""
    
    def __init__(self, x: float = 0, y: float = 0, z: float = 0):
        super().__init__(x, y, z)
        self.radius = 0.15  # 点球的半径
        
    def get_vertices(self) -> List[Tuple[float, float, float]]:
        """生成球体的顶点（简化版）"""
        vertices = []
        
        # 使用较少的分段数以避免过于复杂
        lat_segments = 8  # 纬度分段
        lon_segments = 12  # 经度分段
        
        # 生成球体顶点
        for i in range(lat_segments + 1):
            lat = math.pi * (-0.5 + i / lat_segments)
            y = self.radius * math.sin(lat)
            
            for j in range(lon_segments):
                lon = 2 * math.pi * j / lon_segments
                x = self.radius * math.cos(lat) * math.cos(lon)
                z = self.radius * math.cos(lat) * math.sin(lon)
                vertices.append((x, y, z))
        
        return self.apply_vertex_transform(vertices)
    
    def get_edges(self) -> List[Tuple[int, int]]:
        """生成球体的边（简化版线框）"""
        edges = []
        lat_segments = 8
        lon_segments = 12
        
        # 生成纬线
        for i in range(lat_segments + 1):
            for j in range(lon_segments):
                current = i * lon_segments + j
                next_j = i * lon_segments + (j + 1) % lon_segments
                if current < len(self.get_vertices()) and next_j < len(self.get_vertices()):
                    edges.append((current, next_j))
        
        # 生成经线
        for i in range(lat_segments):
            for j in range(lon_segments):
                current = i * lon_segments + j
                next_i = (i + 1) * lon_segments + j
                if current < len(self.get_vertices()) and next_i < len(self.get_vertices()):
                    edges.append((current, next_i))
        
        return edges
    
    def get_faces(self) -> List[List[int]]:
        """球体的面（简化版）"""
        faces = []
        lat_segments = 8
        lon_segments = 12
        
        # 生成四边形面（简化为三角形）
        for i in range(lat_segments):
            for j in range(lon_segments):
                # 当前四边形的四个顶点
                tl = i * lon_segments + j  # 左上
                tr = i * lon_segments + (j + 1) % lon_segments  # 右上
                bl = (i + 1) * lon_segments + j  # 左下
                br = (i + 1) * lon_segments + (j + 1) % lon_segments  # 右下
                
                # 分解为两个三角形
                if all(v < lat_segments * lon_segments + lon_segments for v in [tl, tr, bl]):
                    faces.append([tl, tr, bl])
                if all(v < lat_segments * lon_segments + lon_segments for v in [tr, br, bl]):
                    faces.append([tr, br, bl])
        
        return faces
    
    def contains_point(self, x: float, y: float, z: float) -> bool:
        """检查点是否在球体内"""
        dx = x - self.x
        dy = y - self.y
        dz = z - self.z
        return (dx*dx + dy*dy + dz*dz) <= (self.radius * 1.2)**2
    
    def get_bounds(self) -> Tuple[float, float, float, float, float, float]:
        """获取球体的边界框"""
        r = self.radius * 1.1  # 稍微放大边界
        return (
            self.x - r, self.y - r, self.z - r,
            self.x + r, self.y + r, self.z + r
        )
    
    def set_radius(self, radius: float):
        """设置球体半径"""
        self.radius = max(0.05, radius)
    
    def to_dict(self):
        """转换为字典"""
        data = super().to_dict()
        data['radius'] = self.radius
        return data
        return data
    
    def from_dict(self, data):
        """从字典加载"""
        super().from_dict(data)
        self.size = data.get('size', 3)