"""
矩形图形类
"""
from typing import Tuple, Dict, Any, List
from .base_shape import BaseShape


class Rectangle(BaseShape):
    """矩形图形"""
    
    def __init__(self, x1: float, y1: float, x2: float, y2: float):
        # 使用矩形的中心作为基准点
        super().__init__((x1 + x2) / 2, (y1 + y2) / 2)
        # 确保x1,y1是左上角，x2,y2是右下角
        self.x1 = min(x1, x2)
        self.y1 = min(y1, y2)
        self.x2 = max(x1, x2)
        self.y2 = max(y1, y2)
        self.width = self.x2 - self.x1
        self.height = self.y2 - self.y1
    
    def draw(self, canvas):
        """在画布上绘制矩形"""
        if not self.visible:
            return
            
        outline_color = "red" if self.selected else self.color
        fill_color = self.fill_color
        
        canvas.create_rectangle(self.x1, self.y1, self.x2, self.y2,
                               outline=outline_color,
                               fill=fill_color,
                               width=self.line_width,
                               tags="shape")
        
        # 如果被选中，在四个角绘制小方块
        if self.selected:
            r = 3
            corners = [(self.x1, self.y1), (self.x2, self.y1), 
                      (self.x1, self.y2), (self.x2, self.y2)]
            for cx, cy in corners:
                canvas.create_rectangle(cx-r, cy-r, cx+r, cy+r,
                                       fill="red", outline="red", tags="shape")
        
        # 绘制调整大小的控制点
        self.draw_resize_handles(canvas)
    
    def contains_point(self, x: float, y: float) -> bool:
        """检查点是否在矩形内部或边界上"""
        return (self.x1 <= x <= self.x2 and self.y1 <= y <= self.y2)
    
    def get_bounds(self) -> Tuple[float, float, float, float]:
        """获取矩形的边界框"""
        return (self.x1, self.y1, self.x2, self.y2)
    
    def move(self, dx: float, dy: float):
        """移动矩形"""
        self.x += dx
        self.y += dy
        self.x1 += dx
        self.y1 += dy
        self.x2 += dx
        self.y2 += dy
    
    def scale(self, factor: float, center_x: float = None, center_y: float = None):
        """缩放矩形"""
        if center_x is None:
            center_x = self.x
        if center_y is None:
            center_y = self.y
            
        # 缩放四个角的坐标
        self.x1 = center_x + (self.x1 - center_x) * factor
        self.y1 = center_y + (self.y1 - center_y) * factor
        self.x2 = center_x + (self.x2 - center_x) * factor
        self.y2 = center_y + (self.y2 - center_y) * factor
        
        # 更新中心点和尺寸
        self.x = (self.x1 + self.x2) / 2
        self.y = (self.y1 + self.y2) / 2
        self.width = abs(self.x2 - self.x1)
        self.height = abs(self.y2 - self.y1)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = super().to_dict()
        data.update({
            'x1': self.x1,
            'y1': self.y1,
            'x2': self.x2,
            'y2': self.y2,
            'width': self.width,
            'height': self.height
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """从字典创建矩形对象"""
        rect = cls(data['x1'], data['y1'], data['x2'], data['y2'])
        rect.color = data.get('color', 'black')
        rect.fill_color = data.get('fill_color')
        rect.line_width = data.get('line_width', 1)
        rect.visible = data.get('visible', True)
        return rect
    
    def get_resize_handles(self) -> List[Tuple[float, float, str]]:
        """获取矩形的调整大小控制点"""
        if not self.selected:
            return []
        
        # 8个控制点：4个角 + 4个边的中点
        handles = [
            (self.x1, self.y1, 'nw'),  # 左上角
            ((self.x1 + self.x2) / 2, self.y1, 'n'),  # 上边中点
            (self.x2, self.y1, 'ne'),  # 右上角
            (self.x2, (self.y1 + self.y2) / 2, 'e'),  # 右边中点
            (self.x2, self.y2, 'se'),  # 右下角
            ((self.x1 + self.x2) / 2, self.y2, 's'),  # 下边中点
            (self.x1, self.y2, 'sw'),  # 左下角
            (self.x1, (self.y1 + self.y2) / 2, 'w'),  # 左边中点
        ]
        return handles
    
    def resize_by_handle(self, handle_type: str, dx: float, dy: float):
        """通过控制点调整矩形大小"""
        # 对于角控制点，以对角为锚点，直接跟随鼠标拖动
        if handle_type in ['nw', 'ne', 'se', 'sw']:
            self._resize_corner_with_anchor(handle_type, dx, dy)
        else:
            # 边控制点保持原有逻辑
            if handle_type == 'n':  # 上边
                self.y1 += dy
            elif handle_type == 'e':  # 右边
                self.x2 += dx
            elif handle_type == 's':  # 下边
                self.y2 += dy
            elif handle_type == 'w':  # 左边
                self.x1 += dx
        
        # 确保x1 <= x2, y1 <= y2
        if self.x1 > self.x2:
            self.x1, self.x2 = self.x2, self.x1
        if self.y1 > self.y2:
            self.y1, self.y2 = self.y2, self.y1
        
        # 更新中心点和尺寸
        self.x = (self.x1 + self.x2) / 2
        self.y = (self.y1 + self.y2) / 2
        self.width = self.x2 - self.x1
        self.height = self.y2 - self.y1
    
    def _resize_corner_with_anchor(self, handle_type: str, dx: float, dy: float):
        """以对角为锚点调整角控制点 - 直接跟随鼠标"""
        # 直接调整对应的角点坐标，保持对角不变
        if handle_type == 'nw':  # 左上角
            self.x1 += dx
            self.y1 += dy
        elif handle_type == 'ne':  # 右上角
            self.x2 += dx
            self.y1 += dy
        elif handle_type == 'se':  # 右下角
            self.x2 += dx
            self.y2 += dy
        elif handle_type == 'sw':  # 左下角
            self.x1 += dx
            self.y2 += dy