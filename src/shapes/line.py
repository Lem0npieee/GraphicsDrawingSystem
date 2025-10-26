"""
直线图形类
"""
from typing import Tuple, Dict, Any, List
from .base_shape import BaseShape


class Line(BaseShape):
    """直线图形"""
    
    def __init__(self, x1: float, y1: float, x2: float, y2: float):
        # 使用线段的中点作为基准点
        super().__init__((x1 + x2) / 2, (y1 + y2) / 2)
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
    
    def bresenham_line(self, x0: int, y0: int, x1: int, y1: int) -> List[Tuple[int, int]]:
        """
        Bresenham直线算法
        返回直线上所有像素点的坐标列表
        """
        points = []
        
        # 计算增量
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        
        # 确定步进方向
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        
        # 初始化误差项
        err = dx - dy
        
        # 当前点
        x, y = x0, y0
        
        while True:
            # 添加当前点
            points.append((x, y))
            
            # 检查是否到达终点
            if x == x1 and y == y1:
                break
            
            # 计算新的误差项
            e2 = 2 * err
            
            # X方向步进判断
            if e2 > -dy:
                err -= dy
                x += sx
            
            # Y方向步进判断  
            if e2 < dx:
                err += dx
                y += sy
        
        return points
    
    def draw_outline_only(self, canvas, outline_color=None):
        """只绘制直线，不填充 - 用于临时预览"""
        if not self.visible:
            return
            
        if outline_color is None:
            outline_color = "red" if self.selected else self.color
        
        # 使用Bresenham算法计算直线上的所有像素点
        x0, y0 = int(round(self.x1)), int(round(self.y1))
        x1, y1 = int(round(self.x2)), int(round(self.y2))
        
        line_points = self.bresenham_line(x0, y0, x1, y1)
        
        # 根据线宽绘制像素点
        pixel_size = max(1, self.line_width)
        half_size = pixel_size // 2
        
        for px, py in line_points:
            # 绘制正方形像素点来模拟像素
            canvas.create_rectangle(
                px - half_size, py - half_size,
                px + half_size, py + half_size,
                fill=outline_color,
                outline=outline_color,
                tags="temp"  # 使用temp标签便于清除
            )
    
    def draw(self, canvas):
        """在画布上绘制直线 - 使用Bresenham算法"""
        if not self.visible:
            return
            
        outline_color = "red" if self.selected else self.color
        
        # 使用Bresenham算法计算直线上的所有像素点
        x0, y0 = int(round(self.x1)), int(round(self.y1))
        x1, y1 = int(round(self.x2)), int(round(self.y2))
        
        line_points = self.bresenham_line(x0, y0, x1, y1)
        
        # 根据线宽绘制像素点
        pixel_size = max(1, self.line_width)
        half_size = pixel_size // 2
        
        for px, py in line_points:
            # 绘制正方形像素点来模拟像素
            canvas.create_rectangle(
                px - half_size, py - half_size,
                px + half_size, py + half_size,
                fill=outline_color,
                outline=outline_color,
                tags="shape"
            )
        
        # 如果被选中，在端点绘制小圆点
        if self.selected:
            r = 3
            canvas.create_oval(self.x1-r, self.y1-r, self.x1+r, self.y1+r,
                             fill="red", outline="red", tags="shape")
            canvas.create_oval(self.x2-r, self.y2-r, self.x2+r, self.y2+r,
                             fill="red", outline="red", tags="shape")
        
        # 绘制调整大小的控制点
        self.draw_resize_handles(canvas)
    
    def contains_point(self, x: float, y: float) -> bool:
        """检查点是否在直线附近"""
        # 计算点到直线的距离
        A = self.y2 - self.y1
        B = self.x1 - self.x2
        C = self.x2 * self.y1 - self.x1 * self.y2
        
        # 避免除零错误
        denominator = (A * A + B * B) ** 0.5
        if denominator == 0:
            return False
            
        distance = abs(A * x + B * y + C) / denominator
        
        # 检查点是否在线段范围内
        min_x, max_x = min(self.x1, self.x2), max(self.x1, self.x2)
        min_y, max_y = min(self.y1, self.y2), max(self.y1, self.y2)
        
        return (distance <= 5 and  # 距离阈值
                min_x - 5 <= x <= max_x + 5 and
                min_y - 5 <= y <= max_y + 5)
    
    def get_bounds(self) -> Tuple[float, float, float, float]:
        """获取直线的边界框"""
        return (min(self.x1, self.x2), min(self.y1, self.y2),
                max(self.x1, self.x2), max(self.y1, self.y2))
    
    def move(self, dx: float, dy: float):
        """移动直线"""
        self.x += dx
        self.y += dy
        self.x1 += dx
        self.y1 += dy
        self.x2 += dx
        self.y2 += dy
    
    def scale(self, factor: float, center_x: float = None, center_y: float = None):
        """缩放直线"""
        if center_x is None:
            center_x = self.x
        if center_y is None:
            center_y = self.y
            
        # 缩放两个端点
        self.x1 = center_x + (self.x1 - center_x) * factor
        self.y1 = center_y + (self.y1 - center_y) * factor
        self.x2 = center_x + (self.x2 - center_x) * factor
        self.y2 = center_y + (self.y2 - center_y) * factor
        
        # 更新中心点
        self.x = (self.x1 + self.x2) / 2
        self.y = (self.y1 + self.y2) / 2
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = super().to_dict()
        data.update({
            'x1': self.x1,
            'y1': self.y1,
            'x2': self.x2,
            'y2': self.y2
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """从字典创建直线对象"""
        line = cls(data['x1'], data['y1'], data['x2'], data['y2'])
        line.color = data.get('color', 'black')
        line.fill_color = data.get('fill_color')
        line.line_width = data.get('line_width', 1)
        line.visible = data.get('visible', True)
        return line
    
    def get_resize_handles(self) -> List[Tuple[float, float, str]]:
        """获取直线的调整大小控制点"""
        if not self.selected:
            return []
        
        # 直线只有两个端点控制点
        handles = [
            (self.x1, self.y1, 'start'),  # 起点
            (self.x2, self.y2, 'end'),    # 终点
        ]
        return handles
    
    def resize_by_handle(self, handle_type: str, dx: float, dy: float):
        """通过控制点调整直线大小"""
        if handle_type == 'start':
            self.x1 += dx
            self.y1 += dy
        elif handle_type == 'end':
            self.x2 += dx
            self.y2 += dy
        
        # 更新中心点
        self.x = (self.x1 + self.x2) / 2
        self.y = (self.y1 + self.y2) / 2