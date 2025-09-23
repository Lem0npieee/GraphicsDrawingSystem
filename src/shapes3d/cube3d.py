"""
3D立方体图形
"""
from .base_shape3d import BaseShape3D
from typing import List, Tuple


class Cube3D(BaseShape3D):
    """3D立方体类"""
    
    def __init__(self, x: float = 0, y: float = 0, z: float = 0, size: float = 1.0):
        super().__init__(x, y, z)
        self.size = size  # 立方体边长
        
    def get_vertices(self) -> List[Tuple[float, float, float]]:
        """获取立方体的8个顶点"""
        half_size = self.size / 2
        
        # 立方体的8个顶点（相对于中心）
        vertices = [
            (-half_size, -half_size, -half_size),  # 0: 左下后
            ( half_size, -half_size, -half_size),  # 1: 右下后
            ( half_size,  half_size, -half_size),  # 2: 右上后
            (-half_size,  half_size, -half_size),  # 3: 左上后
            (-half_size, -half_size,  half_size),  # 4: 左下前
            ( half_size, -half_size,  half_size),  # 5: 右下前
            ( half_size,  half_size,  half_size),  # 6: 右上前
            (-half_size,  half_size,  half_size),  # 7: 左上前
        ]
        
        return self.apply_vertex_transform(vertices)
    
    def get_edges(self) -> List[Tuple[int, int]]:
        """获取立方体的12条边"""
        return [
            # 后面的4条边
            (0, 1), (1, 2), (2, 3), (3, 0),
            # 前面的4条边
            (4, 5), (5, 6), (6, 7), (7, 4),
            # 连接前后的4条边
            (0, 4), (1, 5), (2, 6), (3, 7)
        ]
    
    def get_faces(self) -> List[List[int]]:
        """获取立方体的6个面"""
        return [
            [0, 1, 2, 3],  # 后面
            [4, 7, 6, 5],  # 前面
            [0, 4, 5, 1],  # 下面
            [2, 6, 7, 3],  # 上面
            [0, 3, 7, 4],  # 左面
            [1, 5, 6, 2]   # 右面
        ]
    
    def contains_point(self, x: float, y: float, z: float) -> bool:
        """检查点是否在立方体内部"""
        # 简化：先不考虑旋转，只检查缩放后的边界框
        half_size_x = self.size * self.scale_x / 2
        half_size_y = self.size * self.scale_y / 2
        half_size_z = self.size * self.scale_z / 2
        
        return (abs(x - self.x) <= half_size_x and 
                abs(y - self.y) <= half_size_y and 
                abs(z - self.z) <= half_size_z)
    
    def get_bounds(self) -> Tuple[float, float, float, float, float, float]:
        """获取立方体的边界框"""
        vertices = self.get_vertices()
        if not vertices:
            return (self.x, self.y, self.z, self.x, self.y, self.z)
            
        xs = [v[0] for v in vertices]
        ys = [v[1] for v in vertices]
        zs = [v[2] for v in vertices]
        
        return (min(xs), min(ys), min(zs), max(xs), max(ys), max(zs))
    
    def set_size(self, size: float):
        """设置立方体大小"""
        self.size = max(0.1, size)
    
    def to_dict(self):
        """转换为字典"""
        data = super().to_dict()
        data['size'] = self.size
        return data
    
    def from_dict(self, data):
        """从字典加载"""
        super().from_dict(data)
        self.size = data.get('size', 1.0)