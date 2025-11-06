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
    
    def midpoint_ellipse(self, cx: int, cy: int, rx: int, ry: int) -> List[Tuple[int, int]]:
        """
        中点椭圆算法
        返回椭圆上所有像素点的坐标列表
        cx, cy: 椭圆中心坐标
        rx: 水平半径（半长轴）
        ry: 垂直半径（半短轴）
        """
        points = []
        
        # 第一个区域 (|斜率| < 1)
        x = 0
        y = ry
        rx2 = rx * rx
        ry2 = ry * ry
        tworx2 = 2 * rx2
        twory2 = 2 * ry2
        
        # 初始决策参数 p1
        p1 = ry2 - (rx2 * ry) + (0.25 * rx2)
        dx = twory2 * x
        dy = tworx2 * y
        
        # 第一个区域的点
        while dx < dy:
            # 添加当前点到四个象限
            points.extend([
                (cx + x, cy + y),  # 第一象限
                (cx - x, cy + y),  # 第二象限
                (cx + x, cy - y),  # 第四象限
                (cx - x, cy - y)   # 第三象限
            ])
            
            if p1 < 0:
                # 选择东点 (x+1, y)
                x += 1
                dx += twory2
                p1 += dx + ry2
            else:
                # 选择东南点 (x+1, y-1)
                x += 1
                y -= 1
                dx += twory2
                dy -= tworx2
                p1 += dx - dy + ry2
        
        # 第二个区域 (|斜率| >= 1)
        # 重新计算决策参数 p2
        p2 = (ry2 * (x + 0.5) * (x + 0.5)) + (rx2 * (y - 1) * (y - 1)) - (rx2 * ry2)
        
        while y >= 0:
            # 添加当前点到四个象限
            points.extend([
                (cx + x, cy + y),  # 第一象限
                (cx - x, cy + y),  # 第二象限
                (cx + x, cy - y),  # 第四象限
                (cx - x, cy - y)   # 第三象限
            ])
            
            if p2 > 0:
                # 选择南点 (x, y-1)
                y -= 1
                dy -= tworx2
                p2 += rx2 - dy
            else:
                # 选择东南点 (x+1, y-1)
                y -= 1
                x += 1
                dx += twory2
                dy -= tworx2
                p2 += dx - dy + rx2
        
        return points
    
    def scanline_fill_ellipse(self, cx: int, cy: int, rx: int, ry: int) -> List[Tuple[int, int]]:
        """
        扫描线填充算法 - 椭圆（按作业要求逐像素生成）
        返回值为像素点列表 (x, y)
        """
        fill_points: List[Tuple[int, int]] = []

        if rx <= 0 or ry <= 0:
            return fill_points

        # 获取椭圆边界框
        min_y = cy - ry
        max_y = cy + ry

        # 对每条扫描线进行处理
        for scan_y in range(min_y, max_y + 1):
            # 计算椭圆在当前扫描线上的交点
            intersections = []

            # 椭圆方程: (x-cx)²/rx² + (y-cy)²/ry² = 1
            # 解出x: x = cx ± rx * sqrt(1 - (y-cy)²/ry²)
            dy = scan_y - cy
            if abs(dy) <= ry:
                # 计算判别式
                discriminant = 1 - (dy * dy) / (ry * ry)
                if discriminant >= 0:
                    x_offset = rx * math.sqrt(discriminant)

                    # 两个交点
                    x1 = cx - x_offset
                    x2 = cx + x_offset

                    intersections.extend([x1, x2])

            # 对交点进行排序
            intersections.sort()

            # 填充交点对之间的像素，逐像素生成
            i = 0
            while i < len(intersections) - 1:
                x_start = int(math.ceil(intersections[i]))
                x_end = int(math.floor(intersections[i + 1]))
                
                # 填充水平线段
                for x in range(x_start, x_end + 1):
                    fill_points.append((x, scan_y))
                    
                i += 2  # 处理下一对交点

        return fill_points

    def _optimize_fill_rendering(self, fill_points: List[Tuple[int, int]]) -> List[Tuple[int, int, int, int]]:
        """
        悄咪咪的优化函数：将像素点合并为矩形块以减少canvas调用
        输入：[(x, y)] 像素点列表
        输出：[(x1, y1, x2, y2)] 矩形块列表
        """
        if not fill_points:
            return []
        
        # 按行分组像素点
        rows = {}
        for x, y in fill_points:
            if y not in rows:
                rows[y] = []
            rows[y].append(x)
        
        # 对每行的x坐标排序
        for y in rows:
            rows[y].sort()
        
        rectangles = []
        
        # 将连续的像素点合并为水平线段
        for y in sorted(rows.keys()):
            x_coords = rows[y]
            if not x_coords:
                continue
                
            # 找连续的x坐标段
            start_x = x_coords[0]
            end_x = x_coords[0]
            
            for i in range(1, len(x_coords)):
                if x_coords[i] == end_x + 1:
                    # 连续
                    end_x = x_coords[i]
                else:
                    # 不连续，保存前一段
                    rectangles.append((start_x, y, end_x, y))
                    start_x = x_coords[i]
                    end_x = x_coords[i]
            
            # 保存最后一段
            rectangles.append((start_x, y, end_x, y))
        
        return rectangles

    def draw_outline_only(self, canvas, outline_color=None):
        """只绘制椭圆边框，不填充 - 用于临时预览"""
        if not self.visible:
            return
            
        if outline_color is None:
            outline_color = "red" if self.selected else self.color
        
        # 转换为整数坐标
        cx, cy = int(round(self.x)), int(round(self.y))
        rx, ry = int(round(self.radius_x)), int(round(self.radius_y))
        
        # 确保半径为正数
        rx = max(1, rx)
        ry = max(1, ry)
        
        # 只绘制椭圆边框
        ellipse_points = self.midpoint_ellipse(cx, cy, rx, ry)
        
        # 根据线宽绘制边框
        line_width = max(1, self.line_width)
        half_width = line_width // 2
        
        for px, py in ellipse_points:
            # 为了实现线宽效果，在每个点周围绘制小矩形
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
        """在画布上绘制圆形/椭圆 - 使用中点椭圆算法"""
        if not self.visible:
            return
            
        outline_color = "red" if self.selected else self.color
        fill_color = self.fill_color
        
        # 转换为整数坐标
        cx, cy = int(round(self.x)), int(round(self.y))
        rx, ry = int(round(self.radius_x)), int(round(self.radius_y))
        
        # 确保半径为正数
        rx = max(1, rx)
        ry = max(1, ry)
        
        # 如果需要填充，先绘制填充区域（悄咪咪优化：用大块矩形替换像素点）
        if fill_color and fill_color.lower() != "white":
            # 按作业要求生成每个像素点
            fill_points = self.scanline_fill_ellipse(cx, cy, rx, ry)
            # 悄咪咪地将像素点合并为矩形块绘制
            rectangles = self._optimize_fill_rendering(fill_points)
            for x1, y1, x2, y2 in rectangles:
                canvas.create_rectangle(
                    x1, y1, x2 + 1, y2 + 1,
                    fill=fill_color,
                    outline=fill_color,
                    tags="shape"
                )
        
        # 绘制椭圆边框
        ellipse_points = self.midpoint_ellipse(cx, cy, rx, ry)
        
        # 根据线宽绘制边框
        line_width = max(1, self.line_width)
        half_width = line_width // 2
        
        for px, py in ellipse_points:
            # 为了实现线宽效果，在每个点周围绘制小矩形
            for dx in range(-half_width, half_width + 1):
                for dy in range(-half_width, half_width + 1):
                    canvas.create_rectangle(
                        px + dx, py + dy, 
                        px + dx + 1, py + dy + 1,
                        fill=outline_color,
                        outline=outline_color,
                        tags="shape"
                    )
        
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