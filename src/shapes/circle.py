"""
圆形图形类
"""
import math
from typing import Tuple, Dict, Any, List
from .base_shape import BaseShape


class Circle(BaseShape):
    """圆形图形（支持椭圆变形）"""
    
    def __init__(self, center_x: float, center_y: float, radius: float):
        super().__init__(center_x, center_y)
        self.radius = max(radius, 1)  # 确保半径至少为1
        # 椭圆支持：半长轴和半短轴，初始时都等于半径（圆形）
        self.radius_x = max(radius, 1)  # 水平半径（半长轴）
        self.radius_y = max(radius, 1)  # 垂直半径（半短轴）
    
    def draw(self, canvas):
        """在画布上绘制圆形/椭圆"""
        if not self.visible:
            return
            
        # 使用椭圆半径绘制
        x1 = self.x - self.radius_x
        y1 = self.y - self.radius_y
        x2 = self.x + self.radius_x
        y2 = self.y + self.radius_y
        
        outline_color = "red" if self.selected else self.color
        fill_color = self.fill_color
        
        canvas.create_oval(x1, y1, x2, y2,
                          outline=outline_color,
                          fill=fill_color,
                          width=self.line_width,
                          tags="shape")
        
        # 如果被选中，在圆心和边界上绘制标记点
        if self.selected:
            r = 3
            # 圆心
            canvas.create_oval(self.x-r, self.y-r, self.x+r, self.y+r,
                             fill="red", outline="red", tags="shape")
            # 四个方向的边界点（椭圆边界）
            points = [
                (self.x + self.radius_x, self.y),  # 右
                (self.x - self.radius_x, self.y),  # 左
                (self.x, self.y + self.radius_y),  # 下
                (self.x, self.y - self.radius_y)   # 上
            ]
            for px, py in points:
                canvas.create_oval(px-r, py-r, px+r, py+r,
                                 fill="red", outline="red", tags="shape")
        
        # 绘制调整大小的控制点
        self.draw_resize_handles(canvas)
    
    def contains_point(self, x: float, y: float) -> bool:
        """检查点是否在椭圆内部"""
        # 椭圆内部判断公式：(x-cx)²/rx² + (y-cy)²/ry² <= 1
        # 防止除零错误
        if self.radius_x <= 0 or self.radius_y <= 0:
            return False
            
        dx = x - self.x
        dy = y - self.y
        return (dx * dx) / (self.radius_x * self.radius_x) + (dy * dy) / (self.radius_y * self.radius_y) <= 1
    
    def get_bounds(self) -> Tuple[float, float, float, float]:
        """获取椭圆的边界框"""
        return (self.x - self.radius_x, self.y - self.radius_y,
                self.x + self.radius_x, self.y + self.radius_y)
    
    def move(self, dx: float, dy: float):
        """移动圆形"""
        self.x += dx
        self.y += dy
    
    def scale(self, factor: float, center_x: float = None, center_y: float = None):
        """缩放椭圆"""
        if center_x is None:
            center_x = self.x
        if center_y is None:
            center_y = self.y
            
        # 缩放位置
        self.x = center_x + (self.x - center_x) * factor
        self.y = center_y + (self.y - center_y) * factor
        
        # 缩放半径
        self.radius *= factor
        self.radius_x *= factor
        self.radius_y *= factor
        # 确保最小半径
        self.radius = max(self.radius, 1)
        self.radius_x = max(self.radius_x, 1)
        self.radius_y = max(self.radius_y, 1)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = super().to_dict()
        data['radius'] = self.radius
        data['radius_x'] = self.radius_x
        data['radius_y'] = self.radius_y
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """从字典创建圆形/椭圆对象"""
        circle = cls(data['x'], data['y'], data['radius'])
        circle.color = data.get('color', 'black')
        circle.fill_color = data.get('fill_color')
        circle.line_width = data.get('line_width', 1)
        # 恢复椭圆半径（如果存在）
        circle.radius_x = data.get('radius_x', data['radius'])
        circle.radius_y = data.get('radius_y', data['radius'])
        circle.visible = data.get('visible', True)
        return circle
    
    def get_resize_handles(self) -> List[Tuple[float, float, str]]:
        """获取椭圆的调整大小控制点"""
        if not self.selected:
            return []
        
        # 8个控制点：椭圆周上的8个方向
        # 计算椭圆上的点位置
        diagonal_factor = 0.707  # sqrt(2)/2
        handles = [
            (self.x, self.y - self.radius_y, 'n'),  # 上
            (self.x + self.radius_x * diagonal_factor, self.y - self.radius_y * diagonal_factor, 'ne'),  # 右上
            (self.x + self.radius_x, self.y, 'e'),  # 右
            (self.x + self.radius_x * diagonal_factor, self.y + self.radius_y * diagonal_factor, 'se'),  # 右下
            (self.x, self.y + self.radius_y, 's'),  # 下
            (self.x - self.radius_x * diagonal_factor, self.y + self.radius_y * diagonal_factor, 'sw'),  # 左下
            (self.x - self.radius_x, self.y, 'w'),  # 左
            (self.x - self.radius_x * diagonal_factor, self.y - self.radius_y * diagonal_factor, 'nw'),  # 左上
        ]
        return handles
    
    def resize_by_handle(self, handle_type: str, dx: float, dy: float):
        """通过控制点调整椭圆大小 - 支持单向拉伸"""
        # 四边控制点：单向拉伸变成椭圆
        if handle_type == 'n':  # 上边：调整垂直半径
            self.radius_y -= dy  # 向上拖动减小半径，向下拖动增大半径
        elif handle_type == 's':  # 下边：调整垂直半径
            self.radius_y += dy  # 向下拖动增大半径，向上拖动减小半径
        elif handle_type == 'e':  # 右边：调整水平半径
            self.radius_x += dx  # 向右拖动增大半径，向左拖动减小半径
        elif handle_type == 'w':  # 左边：调整水平半径
            self.radius_x -= dx  # 向左拖动减小半径，向右拖动增大半径
        else:
            # 角控制点：等比例缩放保持椭圆比例
            abs_dx = abs(dx)
            abs_dy = abs(dy)
            
            # 计算缩放因子
            if abs_dx > abs_dy:
                primary_delta = dx
                direction_sign = 1 if handle_type in ['ne', 'se'] else -1
            else:
                primary_delta = dy
                direction_sign = 1 if handle_type in ['se', 'sw'] else -1
            
            # 计算半径变化
            radius_change = primary_delta * direction_sign * 0.5
            
            # 等比例调整两个半径
            self.radius_x += radius_change
            self.radius_y += radius_change
        
        # 限制最小半径
        self.radius_x = max(self.radius_x, 5)
        self.radius_y = max(self.radius_y, 5)
        
        # 更新radius属性（取较大值作为主半径）
        self.radius = max(self.radius_x, self.radius_y)