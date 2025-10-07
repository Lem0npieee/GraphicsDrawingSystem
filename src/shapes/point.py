"""
点图形类
"""
from typing import Tuple, Dict, Any
from .base_shape import BaseShape


class Point(BaseShape):
    """点图形"""
    
    def __init__(self, x: float, y: float, size: float = 3):
        super().__init__(x, y)
        self.size = size  # 点的大小（半径）
    
    def draw(self, canvas):
        """在画布上绘制点"""
        if not self.visible:
            return
            
        # 绘制一个小圆形表示点
        x1 = self.x - self.size
        y1 = self.y - self.size
        x2 = self.x + self.size
        y2 = self.y + self.size
        
        # 点只有一个颜色，不区分轮廓和填充
        point_color = "red" if self.selected else self.color
        
        canvas.create_oval(x1, y1, x2, y2, 
                          outline=point_color, 
                          fill=point_color,
                          width=1,  # 点的轮廓线宽固定为1
                          tags="shape")
    
    def contains_point(self, x: float, y: float) -> bool:
        """检查点(x,y)是否在这个点的范围内"""
        distance = ((x - self.x) ** 2 + (y - self.y) ** 2) ** 0.5
        return distance <= self.size + 2  # 增加一点点击容错范围
    
    def get_bounds(self) -> Tuple[float, float, float, float]:
        """获取点的边界框"""
        return (self.x - self.size, self.y - self.size, 
                self.x + self.size, self.y + self.size)
    
    def move(self, dx: float, dy: float):
        """移动点"""
        self.x += dx
        self.y += dy
    
    def scale(self, factor: float, center_x: float = None, center_y: float = None):
        """缩放点（改变大小）"""
        if center_x is None:
            center_x = self.x
        if center_y is None:
            center_y = self.y
            
        # 缩放位置
        self.x = center_x + (self.x - center_x) * factor
        self.y = center_y + (self.y - center_y) * factor
        
        # 缩放大小
        self.size *= factor
        if self.size < 1:
            self.size = 1
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = super().to_dict()
        data['size'] = self.size
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """从字典创建点对象"""
        point = cls(data['x'], data['y'], data.get('size', 3))
        point.color = data.get('color', 'black')
        # 点不使用填充颜色，只有一个颜色
        point.fill_color = None
        point.line_width = data.get('line_width', 1)
        point.visible = data.get('visible', True)
        return point