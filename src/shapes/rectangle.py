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
    
    def scanline_fill_rectangle(self) -> List[Tuple[int, int]]:
        """
        扫描线填充算法 - 矩形
        使用扫描线算法填充矩形内部所有像素点
        """
        fill_points = []
        
        x1, y1 = int(round(self.x1)), int(round(self.y1))
        x2, y2 = int(round(self.x2)), int(round(self.y2))
        
        # 确保坐标顺序正确
        min_x, max_x = min(x1, x2), max(x1, x2)
        min_y, max_y = min(y1, y2), max(y1, y2)
        
        # 对每条扫描线进行处理
        for scan_y in range(min_y, max_y + 1):
            # 矩形的交点很简单：左边界和右边界
            intersections = [min_x, max_x]
            
            # 填充交点对之间的像素
            x_start, x_end = intersections[0], intersections[1]
            for x in range(x_start, x_end + 1):
                fill_points.append((x, scan_y))
        
        return fill_points
    
    def draw_outline_only(self, canvas, outline_color=None):
        """只绘制矩形边框，不填充 - 用于临时预览"""
        if not self.visible:
            return
            
        if outline_color is None:
            outline_color = "red" if self.selected else self.color
        
        # 绘制矩形边框 - 使用Bresenham算法绘制四条边
        x1, y1 = int(round(self.x1)), int(round(self.y1))
        x2, y2 = int(round(self.x2)), int(round(self.y2))
        
        # 定义矩形的四条边
        edges = [
            (x1, y1, x2, y1),  # 上边
            (x2, y1, x2, y2),  # 右边
            (x2, y2, x1, y2),  # 下边
            (x1, y2, x1, y1)   # 左边
        ]
        
        line_width = max(1, self.line_width)
        half_width = line_width // 2
        
        for edge_x1, edge_y1, edge_x2, edge_y2 in edges:
            # 使用Bresenham算法计算这条边上的所有像素点
            edge_points = self.bresenham_line(edge_x1, edge_y1, edge_x2, edge_y2)
            
            # 绘制像素点，考虑线宽
            for px, py in edge_points:
                for dx in range(-half_width, half_width + 1):
                    for dy in range(-half_width, half_width + 1):
                        canvas.create_rectangle(
                            px + dx, py + dy,
                            px + dx + 1, py + dy + 1,
                            fill=outline_color,
                            outline=outline_color,
                            tags="temp"  # 使用temp标签便于清除
                        )
    
    def draw(self, canvas):
        """在画布上绘制矩形 - 使用Bresenham直线算法"""
        if not self.visible:
            return
            
        outline_color = "red" if self.selected else self.color
        fill_color = self.fill_color
        
        # 如果需要填充，先绘制填充区域
        if fill_color and fill_color.lower() != "white":
            fill_points = self.scanline_fill_rectangle()
            for px, py in fill_points:
                canvas.create_rectangle(
                    px, py, px + 1, py + 1,
                    fill=fill_color,
                    outline=fill_color,
                    tags="shape"
                )
        
        # 绘制矩形边框 - 使用Bresenham算法绘制四条边
        x1, y1 = int(round(self.x1)), int(round(self.y1))
        x2, y2 = int(round(self.x2)), int(round(self.y2))
        
        # 定义矩形的四条边
        edges = [
            (x1, y1, x2, y1),  # 上边
            (x2, y1, x2, y2),  # 右边
            (x2, y2, x1, y2),  # 下边
            (x1, y2, x1, y1)   # 左边
        ]
        
        line_width = max(1, self.line_width)
        half_width = line_width // 2
        
        for edge_x1, edge_y1, edge_x2, edge_y2 in edges:
            # 使用Bresenham算法计算这条边上的所有像素点
            edge_points = self.bresenham_line(edge_x1, edge_y1, edge_x2, edge_y2)
            
            # 绘制像素点，考虑线宽
            for px, py in edge_points:
                for dx in range(-half_width, half_width + 1):
                    for dy in range(-half_width, half_width + 1):
                        canvas.create_rectangle(
                            px + dx, py + dy,
                            px + dx + 1, py + dy + 1,
                            fill=outline_color,
                            outline=outline_color,
                            tags="shape"
                        )
        
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