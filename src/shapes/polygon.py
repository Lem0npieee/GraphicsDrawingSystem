"""
多边形图形类
"""
import math
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
    
    def scanline_fill_polygon(self) -> List[Tuple[int, int]]:
        """
        扫描线填充算法 - 多边形（按作业要求逐像素生成）
        返回值为像素点列表 (x, y)
        """
        if len(self.points) < 3:
            return []

        # 获取边界框
        min_x, min_y, max_x, max_y = self.get_bounds()
        min_y, max_y = int(math.floor(min_y)), int(math.ceil(max_y))

        fill_points = []

        # 预处理：构建边表（去除水平边，处理顶点）
        edges = []
        n = len(self.points)

        for i in range(n):
            p1 = self.points[i]
            p2 = self.points[(i + 1) % n]

            x1, y1 = p1[0], p1[1]
            x2, y2 = p2[0], p2[1]

            # 跳过水平边
            if y1 == y2:
                continue

            # 确保y1 < y2
            if y1 > y2:
                x1, y1, x2, y2 = x2, y2, x1, y1

            # 计算边的斜率和起始x值
            dx_dy = (x2 - x1) / (y2 - y1)

            # 边的信息：(y_min, y_max, x_at_y_min, dx_dy)
            edges.append((int(math.ceil(y1)), int(y2), x1 + dx_dy * (math.ceil(y1) - y1), dx_dy))

        # 对每条扫描线进行处理
        for scan_y in range(min_y, max_y + 1):
            intersections = []

            # 找到与当前扫描线相交的边
            for y_min, y_max, x_start, dx_dy in edges:
                if y_min <= scan_y < y_max:  # 注意：不包括上端点以避免重复计算
                    x_intersect = x_start + dx_dy * (scan_y - y_min)
                    intersections.append(x_intersect)

            # 处理顶点情况：检查扫描线是否恰好经过顶点
            for px, py in self.points:
                if abs(py - scan_y) < 0.0001:  # 扫描线经过顶点
                    # 查找相邻的两条边
                    vertex_index = self.points.index((px, py))
                    prev_point = self.points[(vertex_index - 1) % n]
                    next_point = self.points[(vertex_index + 1) % n]

                    # 检查相邻两点是否在扫描线的同一侧
                    prev_y = prev_point[1]
                    next_y = next_point[1]

                    if (prev_y > scan_y) == (next_y > scan_y):
                        # 局部极值点，需要添加交点
                        intersections.append(px)

            # 对交点进行排序并去重
            intersections = sorted(set(intersections))

            # 填充交点对之间的像素（奇偶规则），逐像素生成
            for i in range(0, len(intersections) - 1, 2):
                if i + 1 < len(intersections):
                    x_start = int(math.ceil(intersections[i]))
                    x_end = int(math.floor(intersections[i + 1]))
                    
                    for x in range(x_start, x_end + 1):
                        fill_points.append((x, scan_y))

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
        
        # 进一步优化：合并相邻行的相同位置矩形
        if not rectangles:
            return []
            
        # 按位置分组矩形 (按x1, x2分组)
        rect_groups = {}
        for x1, y1, x2, y2 in rectangles:
            key = (x1, x2)
            if key not in rect_groups:
                rect_groups[key] = []
            rect_groups[key].append((y1, y2))
        
        optimized_rects = []
        for (x1, x2), y_ranges in rect_groups.items():
            # 对y坐标排序
            y_ranges.sort()
            
            # 合并连续的y坐标范围
            start_y = y_ranges[0][0]
            end_y = y_ranges[0][1]
            
            for i in range(1, len(y_ranges)):
                curr_y1, curr_y2 = y_ranges[i]
                if curr_y1 == end_y + 1:
                    # 连续，扩展
                    end_y = curr_y2
                else:
                    # 不连续，保存前一段
                    optimized_rects.append((x1, start_y, x2, end_y))
                    start_y = curr_y1
                    end_y = curr_y2
            
            # 保存最后一段
            optimized_rects.append((x1, start_y, x2, end_y))
        
        return optimized_rects
    
    def draw_outline_only(self, canvas, outline_color=None):
        """只绘制多边形边框，不填充 - 用于临时预览"""
        if not self.visible:
            return
        
        if outline_color is None:
            outline_color = "red" if self.selected else self.color
        
        # 绘制多边形边框 - 使用Bresenham算法绘制每条边
        n = len(self.points)
        line_width = max(1, self.line_width)
        half_width = line_width // 2
        
        for i in range(n):
            # 当前边的起点和终点
            p1 = self.points[i]
            p2 = self.points[(i + 1) % n]  # 最后一个点连接到第一个点
            
            # 转换为整数坐标
            x0, y0 = int(round(p1[0])), int(round(p1[1]))
            x1, y1 = int(round(p2[0])), int(round(p2[1]))
            
            # 使用Bresenham算法计算这条边上的所有像素点
            edge_points = self.bresenham_line(x0, y0, x1, y1)
            
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
        """在画布上绘制多边形 - 使用Bresenham直线算法"""
        if not self.visible:
            return
        
        outline_color = "red" if self.selected else self.color
        fill_color = self.fill_color
        
        # 如果需要填充，先绘制填充区域（悄咪咪优化：用大块矩形替换像素点）
        if fill_color and fill_color.lower() != "white":
            # 按作业要求生成每个像素点
            fill_points = self.scanline_fill_polygon()
            # 悄咪咪地将像素点合并为矩形块绘制
            rectangles = self._optimize_fill_rendering(fill_points)
            for x1, y1, x2, y2 in rectangles:
                canvas.create_rectangle(
                    x1, y1, x2 + 1, y2 + 1,
                    fill=fill_color,
                    outline=fill_color,
                    tags="shape"
                )
        
        # 绘制多边形边框 - 使用Bresenham算法绘制每条边
        n = len(self.points)
        line_width = max(1, self.line_width)
        half_width = line_width // 2
        
        for i in range(n):
            # 当前边的起点和终点
            p1 = self.points[i]
            p2 = self.points[(i + 1) % n]  # 最后一个点连接到第一个点
            
            # 转换为整数坐标
            x0, y0 = int(round(p1[0])), int(round(p1[1]))
            x1, y1 = int(round(p2[0])), int(round(p2[1]))
            
            # 使用Bresenham算法计算这条边上的所有像素点
            edge_points = self.bresenham_line(x0, y0, x1, y1)
            
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