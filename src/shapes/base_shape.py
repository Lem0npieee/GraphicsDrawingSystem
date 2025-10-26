"""
基础图形类 - 所有图形的父类
"""
import json
from abc import ABC, abstractmethod
from typing import Tuple, Dict, Any, List


class BaseShape(ABC):
    """所有图形的基础类"""
    
    def __init__(self, x: float = 0, y: float = 0):
        self.x = x  # 图形的x坐标
        self.y = y  # 图形的y坐标
        self.color = "black"  # 图形颜色
        self.fill_color = None  # 填充颜色
        self.line_width = 1  # 线宽
        self.selected = False  # 是否被选中
        self.visible = True  # 是否可见
        self.resize_handle_size = 6  # 调整大小控制点的大小
        
    @abstractmethod
    def draw(self, canvas):
        """绘制图形到画布上"""
        pass
    
    @abstractmethod
    def contains_point(self, x: float, y: float) -> bool:
        """检查点(x,y)是否在图形内部"""
        pass
    
    @abstractmethod
    def get_bounds(self) -> Tuple[float, float, float, float]:
        """获取图形的边界框 (x1, y1, x2, y2)"""
        pass
    
    @abstractmethod
    def move(self, dx: float, dy: float):
        """移动图形"""
        pass
    
    @abstractmethod
    def scale(self, factor: float, center_x: float = None, center_y: float = None):
        """缩放图形"""
        pass
    
    def set_color(self, color: str):
        """设置图形颜色"""
        self.color = color
    
    def set_fill_color(self, color: str):
        """设置填充颜色"""
        self.fill_color = color
    
    def set_line_width(self, width: int):
        """设置线宽"""
        self.line_width = width
    
    def set_selected(self, selected: bool):
        """设置选中状态"""
        self.selected = selected
    
    def set_visible(self, visible: bool):
        """设置可见性"""
        self.visible = visible
    
    def to_dict(self) -> Dict[str, Any]:
        """将图形转换为字典格式，用于保存"""
        return {
            'type': self.__class__.__name__,
            'x': self.x,
            'y': self.y,
            'color': self.color,
            'fill_color': self.fill_color,
            'line_width': self.line_width,
            'visible': self.visible
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """从字典创建图形对象"""
        # 这个方法在子类中具体实现
        raise NotImplementedError("子类必须实现 from_dict 方法")
    
    def get_resize_handles(self) -> List[Tuple[float, float, str]]:
        """获取调整大小的控制点列表
        返回: [(x, y, handle_type), ...]
        handle_type: 'nw', 'n', 'ne', 'e', 'se', 's', 'sw', 'w', 'center'
        """
        if not self.selected:
            return []
        return []  # 默认实现，子类可以重写
    
    def get_handle_at_point(self, x: float, y: float) -> str:
        """获取指定点处的控制点类型"""
        handles = self.get_resize_handles()
        handle_size = self.resize_handle_size
        
        for hx, hy, handle_type in handles:
            if (abs(x - hx) <= handle_size and abs(y - hy) <= handle_size):
                return handle_type
        return ""
    
    def resize_by_handle(self, handle_type: str, dx: float, dy: float):
        """通过控制点调整大小
        handle_type: 控制点类型
        dx, dy: 移动量
        """
        # 默认实现，子类应该重写
        pass
    
    def draw_resize_handles(self, canvas):
        """绘制调整大小的控制点"""
        if not self.selected:
            return
            
        handles = self.get_resize_handles()
        handle_size = self.resize_handle_size
        
        for hx, hy, handle_type in handles:
            x1 = hx - handle_size // 2
            y1 = hy - handle_size // 2
            x2 = hx + handle_size // 2
            y2 = hy + handle_size // 2
            
            # 根据控制点类型设置不同的颜色
            if handle_type == 'center':
                color = "blue"
            else:
                color = "red"
            
            canvas.create_rectangle(x1, y1, x2, y2,
                                   fill=color, outline="black",
                                   width=1, tags="resize_handle")