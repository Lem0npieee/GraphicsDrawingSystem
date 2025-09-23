"""
3D向量图形
"""
from .base_shape3d import BaseShape3D
from typing import List, Tuple
import math


class Vector3D(BaseShape3D):
    """3D向量类 - 显示为圆柱体加圆锥的箭头"""
    
    def __init__(self, x: float = 0, y: float = 0, z: float = 0, 
                 vx: float = 1, vy: float = 0, vz: float = 0):
        super().__init__(x, y, z)
        self.vx = vx  # 向量方向x
        self.vy = vy  # 向量方向y
        self.vz = vz  # 向量方向z
        self.length = 2.0  # 向量长度
        self.shaft_radius = 0.05  # 圆柱体半径
        self.head_radius = 0.15  # 圆锥底半径
        self.head_length = 0.3  # 圆锥长度
        
    def _normalize_direction(self):
        """归一化方向向量"""
        mag = math.sqrt(self.vx*self.vx + self.vy*self.vy + self.vz*self.vz)
        if mag == 0:
            return 1, 0, 0
        return self.vx/mag, self.vy/mag, self.vz/mag
    
    def get_vertices(self) -> List[Tuple[float, float, float]]:
        """生成箭头的顶点（圆柱体 + 圆锥体）"""
        vertices = []
        
        # 归一化方向向量
        dir_x, dir_y, dir_z = self._normalize_direction()
        
        # 计算圆柱体终点和圆锥体起点
        shaft_length = self.length - self.head_length
        shaft_end_x = dir_x * shaft_length
        shaft_end_y = dir_y * shaft_length
        shaft_end_z = dir_z * shaft_length
        
        # 计算箭头尖端
        head_tip_x = dir_x * self.length
        head_tip_y = dir_y * self.length
        head_tip_z = dir_z * self.length
        
        # 计算垂直于方向的两个单位向量（用于生成圆形截面）
        if abs(dir_x) < 0.9:
            perp1_x, perp1_y, perp1_z = 0, dir_z, -dir_y
        else:
            perp1_x, perp1_y, perp1_z = -dir_z, 0, dir_x
        
        # 归一化第一个垂直向量
        perp1_mag = math.sqrt(perp1_x**2 + perp1_y**2 + perp1_z**2)
        if perp1_mag > 0:
            perp1_x, perp1_y, perp1_z = perp1_x/perp1_mag, perp1_y/perp1_mag, perp1_z/perp1_mag
        
        # 计算第二个垂直向量（叉积）
        perp2_x = dir_y * perp1_z - dir_z * perp1_y
        perp2_y = dir_z * perp1_x - dir_x * perp1_z
        perp2_z = dir_x * perp1_y - dir_y * perp1_x
        
        # 生成圆形截面的顶点
        segments = 8  # 圆形分段数
        
        # 圆柱体起点圆形
        for i in range(segments):
            angle = 2 * math.pi * i / segments
            cos_a, sin_a = math.cos(angle), math.sin(angle)
            x = self.shaft_radius * (cos_a * perp1_x + sin_a * perp2_x)
            y = self.shaft_radius * (cos_a * perp1_y + sin_a * perp2_y)
            z = self.shaft_radius * (cos_a * perp1_z + sin_a * perp2_z)
            vertices.append((x, y, z))
        
        # 圆柱体终点圆形
        for i in range(segments):
            angle = 2 * math.pi * i / segments
            cos_a, sin_a = math.cos(angle), math.sin(angle)
            x = shaft_end_x + self.shaft_radius * (cos_a * perp1_x + sin_a * perp2_x)
            y = shaft_end_y + self.shaft_radius * (cos_a * perp1_y + sin_a * perp2_y)
            z = shaft_end_z + self.shaft_radius * (cos_a * perp1_z + sin_a * perp2_z)
            vertices.append((x, y, z))
        
        # 圆锥底部圆形（更大半径）
        for i in range(segments):
            angle = 2 * math.pi * i / segments
            cos_a, sin_a = math.cos(angle), math.sin(angle)
            x = shaft_end_x + self.head_radius * (cos_a * perp1_x + sin_a * perp2_x)
            y = shaft_end_y + self.head_radius * (cos_a * perp1_y + sin_a * perp2_y)
            z = shaft_end_z + self.head_radius * (cos_a * perp1_z + sin_a * perp2_z)
            vertices.append((x, y, z))
        
        # 箭头尖端
        vertices.append((head_tip_x, head_tip_y, head_tip_z))
        
        return self.apply_vertex_transform(vertices)
    
    def get_edges(self) -> List[Tuple[int, int]]:
        """生成箭头的边"""
        edges = []
        segments = 8
        
        # 圆柱体起点圆形的边
        for i in range(segments):
            edges.append((i, (i + 1) % segments))
        
        # 圆柱体终点圆形的边
        for i in range(segments):
            start_idx = segments + i
            edges.append((start_idx, segments + (i + 1) % segments))
        
        # 圆锥底部圆形的边
        for i in range(segments):
            start_idx = 2 * segments + i
            edges.append((start_idx, 2 * segments + (i + 1) % segments))
        
        # 圆柱体侧面的边
        for i in range(segments):
            edges.append((i, segments + i))
        
        # 圆锥侧面的边
        tip_idx = 3 * segments  # 箭头尖端的索引
        for i in range(segments):
            cone_base_idx = 2 * segments + i
            edges.append((cone_base_idx, tip_idx))
        
        return edges
    
    def get_faces(self) -> List[List[int]]:
        """生成箭头的面"""
        faces = []
        segments = 8
        
        # 圆柱体底面（起点）
        bottom_face = list(range(segments))
        faces.append(bottom_face)
        
        # 圆柱体侧面
        for i in range(segments):
            next_i = (i + 1) % segments
            # 每个侧面是一个四边形，分解为两个三角形
            faces.append([i, next_i, segments + next_i])
            faces.append([i, segments + next_i, segments + i])
        
        # 圆锥底面
        cone_base = list(range(segments + segments, 2 * segments + segments))
        faces.append(cone_base)
        
        # 圆锥侧面
        tip_idx = 3 * segments
        for i in range(segments):
            next_i = (i + 1) % segments
            cone_base_i = 2 * segments + i
            cone_base_next = 2 * segments + next_i
            faces.append([cone_base_i, cone_base_next, tip_idx])
        
        return faces
    
    def contains_point(self, x: float, y: float, z: float) -> bool:
        """检查点是否在箭头几何体内"""
        # 转换到局部坐标系
        local_x = x - self.x
        local_y = y - self.y
        local_z = z - self.z
        
        # 归一化方向向量
        dir_x, dir_y, dir_z = self._normalize_direction()
        
        # 计算点在箭头方向上的投影
        proj_length = local_x * dir_x + local_y * dir_y + local_z * dir_z
        
        # 检查是否在箭头长度范围内
        if proj_length < 0 or proj_length > self.length:
            return False
        
        # 计算点到箭头轴线的距离
        proj_x = proj_length * dir_x
        proj_y = proj_length * dir_y
        proj_z = proj_length * dir_z
        
        # 到轴线的距离
        dist_to_axis = math.sqrt(
            (local_x - proj_x)**2 + 
            (local_y - proj_y)**2 + 
            (local_z - proj_z)**2
        )
        
        # 判断是在圆柱体部分还是圆锥部分
        shaft_length = self.length - self.head_length
        
        if proj_length <= shaft_length:
            # 圆柱体部分
            return dist_to_axis <= self.shaft_radius
        else:
            # 圆锥部分
            cone_progress = (proj_length - shaft_length) / self.head_length
            cone_radius = self.head_radius * (1 - cone_progress)
            return dist_to_axis <= cone_radius
    
    def get_bounds(self) -> Tuple[float, float, float, float, float, float]:
        """获取箭头的边界框"""
        dir_x, dir_y, dir_z = self._normalize_direction()
        
        # 箭头尖端位置
        tip_x = self.x + dir_x * self.length
        tip_y = self.y + dir_y * self.length
        tip_z = self.z + dir_z * self.length
        
        # 考虑圆锥底部的半径
        margin = self.head_radius
        
        min_x = min(self.x, tip_x) - margin
        max_x = max(self.x, tip_x) + margin
        min_y = min(self.y, tip_y) - margin
        max_y = max(self.y, tip_y) + margin
        min_z = min(self.z, tip_z) - margin
        max_z = max(self.z, tip_z) + margin
        
        return (min_x, min_y, min_z, max_x, max_y, max_z)
    
    def set_direction(self, vx: float, vy: float, vz: float):
        """设置向量方向"""
        self.vx = vx
        self.vy = vy
        self.vz = vz
    
    def set_length(self, length: float):
        """设置向量长度"""
        self.length = max(0.5, length)
        # 确保箭头头部不会太大
        if self.head_length > self.length * 0.5:
            self.head_length = self.length * 0.3
    
    def set_shaft_radius(self, radius: float):
        """设置圆柱体半径"""
        self.shaft_radius = max(0.01, radius)
    
    def set_head_size(self, radius: float, length: float):
        """设置箭头头部尺寸"""
        self.head_radius = max(0.05, radius)
        self.head_length = max(0.1, min(length, self.length * 0.5))
    
    def to_dict(self):
        """转换为字典"""
        data = super().to_dict()
        data.update({
            'vx': self.vx,
            'vy': self.vy,
            'vz': self.vz,
            'length': self.length,
            'shaft_radius': self.shaft_radius,
            'head_radius': self.head_radius,
            'head_length': self.head_length
        })
        return data
    
    def from_dict(self, data):
        """从字典加载"""
        super().from_dict(data)
        self.vx = data.get('vx', 1)
        self.vy = data.get('vy', 0)
        self.vz = data.get('vz', 0)
        self.length = data.get('length', 2.0)
        self.shaft_radius = data.get('shaft_radius', 0.05)
        self.head_radius = data.get('head_radius', 0.15)
        self.head_length = data.get('head_length', 0.3)