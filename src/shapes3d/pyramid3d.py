"""
3D四棱锥图形
"""
from .base_shape3d import BaseShape3D
from typing import List, Tuple


class Pyramid3D(BaseShape3D):
    """3D四棱锥类"""
    
    def __init__(self, x: float = 0, y: float = 0, z: float = 0, 
                 base_size: float = 1.0, height: float = 1.0):
        super().__init__(x, y, z)
        self.base_size = base_size  # 底面边长
        self.height = height  # 高度
        
    def get_vertices(self) -> List[Tuple[float, float, float]]:
        """获取四棱锥的5个顶点"""
        half_base = self.base_size / 2
        
        # 四棱锥的5个顶点（相对于中心，沿Y轴向上）
        vertices = [
            # 底面的4个顶点（在y=-height/2平面上，即XZ平面）
            (-half_base, -self.height/2, -half_base),  # 0: 左下
            ( half_base, -self.height/2, -half_base),  # 1: 右下
            ( half_base, -self.height/2,  half_base),  # 2: 右上
            (-half_base, -self.height/2,  half_base),  # 3: 左上
            # 顶点（在y=height/2，即顶部）
            (0, self.height/2, 0),  # 4: 顶点
        ]
        
        return self.apply_vertex_transform(vertices)
    
    def get_edges(self) -> List[Tuple[int, int]]:
        """获取四棱锥的8条边"""
        return [
            # 底面的4条边
            (0, 1), (1, 2), (2, 3), (3, 0),
            # 从底面各顶点到顶点的4条边
            (0, 4), (1, 4), (2, 4), (3, 4)
        ]
    
    def get_faces(self) -> List[List[int]]:
        """获取四棱锥的5个面"""
        return [
            [0, 3, 2, 1],  # 底面（逆时针）
            [0, 1, 4],     # 侧面1
            [1, 2, 4],     # 侧面2
            [2, 3, 4],     # 侧面3
            [3, 0, 4]      # 侧面4
        ]
    
    def contains_point(self, x: float, y: float, z: float) -> bool:
        """检查点是否在四棱锥内部"""
        # 简化：检查是否在边界框内，然后检查高度约束
        # 转换到局部坐标系
        local_x = (x - self.x) / self.scale_x
        local_y = (y - self.y) / self.scale_y
        local_z = (z - self.z) / self.scale_z
        
        # 检查y范围（现在锥体沿Y轴）
        if local_y < -self.height/2 or local_y > self.height/2:
            return False
        
        # 检查是否在四棱锥内部
        # 根据y位置计算当前层的边长
        if local_y <= 0:
            # 在底部
            half_base = self.base_size / 2
            return (abs(local_x) <= half_base and abs(local_z) <= half_base)
        else:
            # 在锥形部分，线性收缩
            t = local_y / (self.height/2)  # 0到1
            current_half_base = self.base_size / 2 * (1 - t)
            return (abs(local_x) <= current_half_base and abs(local_z) <= current_half_base)
    
    def get_bounds(self) -> Tuple[float, float, float, float, float, float]:
        """获取四棱锥的边界框"""
        vertices = self.get_vertices()
        if not vertices:
            return (self.x, self.y, self.z, self.x, self.y, self.z)
            
        xs = [v[0] for v in vertices]
        ys = [v[1] for v in vertices]
        zs = [v[2] for v in vertices]
        
        return (min(xs), min(ys), min(zs), max(xs), max(ys), max(zs))
    
    def set_base_size(self, base_size: float):
        """设置底面大小"""
        self.base_size = max(0.1, base_size)
    
    def set_height(self, height: float):
        """设置高度"""
        self.height = max(0.1, height)
    
    def to_dict(self):
        """转换为字典"""
        data = super().to_dict()
        data.update({
            'base_size': self.base_size,
            'height': self.height
        })
        return data
    
    def from_dict(self, data):
        """从字典加载"""
        super().from_dict(data)
        self.base_size = data.get('base_size', 1.0)
        self.height = data.get('height', 1.0)