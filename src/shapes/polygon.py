"""
多边形图形类
"""
from typing import List, Tuple, Dict, Any
from .base_shape import BaseShape


class Polygon(BaseShape):
    """多边形图形"""
    
    def __init__(self, points: List[Tuple[float, float]]):
        if len(points) < 3:
            raise ValueError("多边形至少需要3个点")
        
        self.points = points[:]  # 复制点列表
        
        # 计算中心点
        center_x = sum(p[0] for p in points) / len(points)
        center_y = sum(p[1] for p in points) / len(points)
        super().__init__(center_x, center_y)
    
    def draw(self, canvas):
        """在画布上绘制多边形"""
        if not self.visible:
            return
            
        # 将点列表转换为平坦列表
        flat_points = []
        for x, y in self.points:
            flat_points.extend([x, y])
        
        outline_color = "red" if self.selected else self.color
        fill_color = self.fill_color
        
        canvas.create_polygon(flat_points,
                             outline=outline_color,
                             fill=fill_color,
                             width=self.line_width,
                             tags="shape")
        
        # 如果被选中，在每个顶点绘制小圆点
        if self.selected:
            r = 3
            for x, y in self.points:
                canvas.create_oval(x-r, y-r, x+r, y+r,
                                 fill="red", outline="red", tags="shape")
        
        # 绘制调整大小的控制点
        self.draw_resize_handles(canvas)
    
    def contains_point(self, x: float, y: float) -> bool:
        """使用射线法检查点是否在多边形内部"""
        n = len(self.points)
        inside = False
        
        j = n - 1
        for i in range(n):
            xi, yi = self.points[i]
            xj, yj = self.points[j]
            
            if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
                inside = not inside
            j = i
        
        return inside
    
    def get_bounds(self) -> Tuple[float, float, float, float]:
        """获取多边形的边界框"""
        if not self.points:
            return (0, 0, 0, 0)
        
        x_coords = [p[0] for p in self.points]
        y_coords = [p[1] for p in self.points]
        
        return (min(x_coords), min(y_coords), max(x_coords), max(y_coords))
    
    def move(self, dx: float, dy: float):
        """移动多边形"""
        self.x += dx
        self.y += dy
        self.points = [(x + dx, y + dy) for x, y in self.points]
    
    def scale(self, factor: float, center_x: float = None, center_y: float = None):
        """缩放多边形"""
        if center_x is None:
            center_x = self.x
        if center_y is None:
            center_y = self.y
            
        # 缩放每个顶点
        new_points = []
        for x, y in self.points:
            new_x = center_x + (x - center_x) * factor
            new_y = center_y + (y - center_y) * factor
            new_points.append((new_x, new_y))
        
        self.points = new_points
        
        # 更新中心点
        self.x = sum(p[0] for p in self.points) / len(self.points)
        self.y = sum(p[1] for p in self.points) / len(self.points)
    
    def add_point(self, x: float, y: float):
        """添加一个新的顶点"""
        self.points.append((x, y))
        # 重新计算中心点
        self.x = sum(p[0] for p in self.points) / len(self.points)
        self.y = sum(p[1] for p in self.points) / len(self.points)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = super().to_dict()
        data['points'] = self.points
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """从字典创建多边形对象"""
        polygon = cls(data['points'])
        polygon.color = data.get('color', 'black')
        polygon.fill_color = data.get('fill_color')
        polygon.line_width = data.get('line_width', 1)
        polygon.visible = data.get('visible', True)
        return polygon
    
    def get_resize_handles(self) -> List[Tuple[float, float, str]]:
        """获取多边形的调整大小控制点"""
        if not self.selected:
            return []
        
        # 多边形的每个顶点都是控制点
        handles = []
        for i, (x, y) in enumerate(self.points):
            handles.append((x, y, f'vertex_{i}'))
        return handles
    
    def resize_by_handle(self, handle_type: str, dx: float, dy: float):
        """通过控制点调整多边形大小"""
        if handle_type.startswith('vertex_'):
            # 获取顶点索引
            vertex_index = int(handle_type.split('_')[1])
            if 0 <= vertex_index < len(self.points):
                # 移动指定的顶点
                x, y = self.points[vertex_index]
                self.points[vertex_index] = (x + dx, y + dy)
                
                # 重新计算中心点
                self.x = sum(p[0] for p in self.points) / len(self.points)
                self.y = sum(p[1] for p in self.points) / len(self.points)