"""
贝塞尔曲线图形类
实现三次贝塞尔曲线，支持4个控制点调整曲率
"""
import math
from typing import Tuple, Dict, Any, List
from .base_shape import BaseShape


class BezierCurve(BaseShape):
    """三次贝塞尔曲线图形"""
    
    def __init__(self, p0: Tuple[float, float], p1: Tuple[float, float], 
                 p2: Tuple[float, float], p3: Tuple[float, float]):
        """
        初始化贝塞尔曲线
        p0: 起点
        p1: 第一个控制点
        p2: 第二个控制点
        p3: 终点
        """
        # 计算中心点
        center_x = (p0[0] + p1[0] + p2[0] + p3[0]) / 4
        center_y = (p0[1] + p1[1] + p2[1] + p3[1]) / 4
        super().__init__(center_x, center_y)
        
        self.p0 = p0  # 起点
        self.p1 = p1  # 第一个控制点
        self.p2 = p2  # 第二个控制点
        self.p3 = p3  # 终点
        
        self.curve_resolution = 50  # 曲线分段数，影响绘制精度
        
    def bezier_point(self, t: float) -> Tuple[float, float]:
        """
        计算贝塞尔曲线上参数为t的点
        t: 参数，范围[0, 1]
        返回: (x, y) 坐标
        """
        # 三次贝塞尔曲线公式：
        # B(t) = (1-t)³P₀ + 3(1-t)²tP₁ + 3(1-t)t²P₂ + t³P₃
        
        u = 1 - t
        tt = t * t
        uu = u * u
        uuu = uu * u
        ttt = tt * t
        
        x = (uuu * self.p0[0] + 
             3 * uu * t * self.p1[0] + 
             3 * u * tt * self.p2[0] + 
             ttt * self.p3[0])
        
        y = (uuu * self.p0[1] + 
             3 * uu * t * self.p1[1] + 
             3 * u * tt * self.p2[1] + 
             ttt * self.p3[1])
        
        return (x, y)
    
    def get_curve_points(self) -> List[Tuple[float, float]]:
        """获取曲线上的所有点"""
        points = []
        for i in range(self.curve_resolution + 1):
            t = i / self.curve_resolution
            points.append(self.bezier_point(t))
        return points
    
    def draw(self, canvas):
        """在画布上绘制贝塞尔曲线"""
        if not self.visible:
            return
            
        outline_color = "red" if self.selected else self.color
        
        # 获取曲线上的所有点
        curve_points = self.get_curve_points()
        
        # 绘制曲线（连接所有点）
        for i in range(len(curve_points) - 1):
            x1, y1 = curve_points[i]
            x2, y2 = curve_points[i + 1]
            canvas.create_line(x1, y1, x2, y2,
                              fill=outline_color,
                              width=self.line_width,
                              tags="shape")
        
        # 如果被选中，绘制控制点和控制线
        if self.selected:
            self.draw_control_structure(canvas)
        
        # 绘制调整大小的控制点
        self.draw_resize_handles(canvas)
    
    def draw_control_structure(self, canvas):
        """绘制控制点和控制线"""
        # 绘制控制线（虚线）
        canvas.create_line(self.p0[0], self.p0[1], self.p1[0], self.p1[1],
                          fill="gray", dash=(5, 5), width=1, tags="shape")
        canvas.create_line(self.p2[0], self.p2[1], self.p3[0], self.p3[1],
                          fill="gray", dash=(5, 5), width=1, tags="shape")
        
        # 绘制端点（较大的圆）
        r1 = 5
        canvas.create_oval(self.p0[0]-r1, self.p0[1]-r1, self.p0[0]+r1, self.p0[1]+r1,
                          fill="blue", outline="darkblue", width=2, tags="shape")
        canvas.create_oval(self.p3[0]-r1, self.p3[1]-r1, self.p3[0]+r1, self.p3[1]+r1,
                          fill="blue", outline="darkblue", width=2, tags="shape")
        
        # 绘制控制点（较小的圆）
        r2 = 4
        canvas.create_oval(self.p1[0]-r2, self.p1[1]-r2, self.p1[0]+r2, self.p1[1]+r2,
                          fill="green", outline="darkgreen", width=2, tags="shape")
        canvas.create_oval(self.p2[0]-r2, self.p2[1]-r2, self.p2[0]+r2, self.p2[1]+r2,
                          fill="green", outline="darkgreen", width=2, tags="shape")
    
    def contains_point(self, x: float, y: float) -> bool:
        """检查点是否在曲线附近"""
        curve_points = self.get_curve_points()
        
        # 检查是否靠近曲线上的任意一点
        for px, py in curve_points:
            distance = math.sqrt((x - px) ** 2 + (y - py) ** 2)
            if distance <= 5:  # 5像素的容错范围
                return True
        
        return False
    
    def get_bounds(self) -> Tuple[float, float, float, float]:
        """获取曲线的边界框"""
        curve_points = self.get_curve_points()
        
        if not curve_points:
            return (0, 0, 0, 0)
        
        x_coords = [p[0] for p in curve_points]
        y_coords = [p[1] for p in curve_points]
        
        return (min(x_coords), min(y_coords), max(x_coords), max(y_coords))
    
    def move(self, dx: float, dy: float):
        """移动曲线"""
        self.x += dx
        self.y += dy
        
        # 移动所有控制点
        self.p0 = (self.p0[0] + dx, self.p0[1] + dy)
        self.p1 = (self.p1[0] + dx, self.p1[1] + dy)
        self.p2 = (self.p2[0] + dx, self.p2[1] + dy)
        self.p3 = (self.p3[0] + dx, self.p3[1] + dy)
    
    def scale(self, factor: float, center_x: float = None, center_y: float = None):
        """缩放曲线"""
        if center_x is None:
            center_x = self.x
        if center_y is None:
            center_y = self.y
        
        # 缩放所有控制点
        def scale_point(px, py):
            new_x = center_x + (px - center_x) * factor
            new_y = center_y + (py - center_y) * factor
            return (new_x, new_y)
        
        self.p0 = scale_point(self.p0[0], self.p0[1])
        self.p1 = scale_point(self.p1[0], self.p1[1])
        self.p2 = scale_point(self.p2[0], self.p2[1])
        self.p3 = scale_point(self.p3[0], self.p3[1])
        
        # 更新中心点
        self.x = (self.p0[0] + self.p1[0] + self.p2[0] + self.p3[0]) / 4
        self.y = (self.p0[1] + self.p1[1] + self.p2[1] + self.p3[1]) / 4
    
    def get_resize_handles(self) -> List[Tuple[float, float, str]]:
        """获取贝塞尔曲线的调整控制点"""
        if not self.selected:
            return []
        
        # 4个控制点：2个端点 + 2个控制点
        handles = [
            (self.p0[0], self.p0[1], 'p0'),  # 起点
            (self.p1[0], self.p1[1], 'p1'),  # 第一个控制点
            (self.p2[0], self.p2[1], 'p2'),  # 第二个控制点
            (self.p3[0], self.p3[1], 'p3'),  # 终点
        ]
        return handles
    
    def resize_by_handle(self, handle_type: str, dx: float, dy: float):
        """通过控制点调整曲线形状"""
        if handle_type == 'p0':
            self.p0 = (self.p0[0] + dx, self.p0[1] + dy)
        elif handle_type == 'p1':
            self.p1 = (self.p1[0] + dx, self.p1[1] + dy)
        elif handle_type == 'p2':
            self.p2 = (self.p2[0] + dx, self.p2[1] + dy)
        elif handle_type == 'p3':
            self.p3 = (self.p3[0] + dx, self.p3[1] + dy)
        
        # 更新中心点
        self.x = (self.p0[0] + self.p1[0] + self.p2[0] + self.p3[0]) / 4
        self.y = (self.p0[1] + self.p1[1] + self.p2[1] + self.p3[1]) / 4
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = super().to_dict()
        data.update({
            'p0': self.p0,
            'p1': self.p1,
            'p2': self.p2,
            'p3': self.p3,
            'curve_resolution': self.curve_resolution
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """从字典创建贝塞尔曲线对象"""
        curve = cls(
            tuple(data['p0']), 
            tuple(data['p1']), 
            tuple(data['p2']), 
            tuple(data['p3'])
        )
        curve.color = data.get('color', 'black')
        curve.fill_color = data.get('fill_color')
        curve.line_width = data.get('line_width', 1)
        curve.visible = data.get('visible', True)
        curve.curve_resolution = data.get('curve_resolution', 50)
        return curve