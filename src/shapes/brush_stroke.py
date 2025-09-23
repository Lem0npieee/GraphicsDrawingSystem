"""
笔刷轨迹图形类
"""
import random
import math
from typing import List, Tuple, Dict, Any
from .base_shape import BaseShape


class BrushStroke(BaseShape):
    """笔刷轨迹图形"""
    
    def __init__(self, points: List[Tuple[float, float]] = None, brush_type: str = "brush_ballpoint"):
        # 使用第一个点作为基准坐标，如果没有点则使用(0,0)
        first_point = points[0] if points else (0, 0)
        super().__init__(first_point[0], first_point[1])
        
        self.points = points or []  # 轨迹点列表
        self.brush_size = 5  # 笔刷大小
        self.brush_type = brush_type  # 笔刷类型
        self.spray_dots = []  # 预生成的喷雾散点，用于固定显示
        self.pencil_texture = []  # 预生成的铅笔纹理，用于固定显示
        self.highlighter_lines = []  # 预生成的荧光笔斜线，用于固定显示
        # 半透明绘制缓存（针对荧光笔的图像叠加）
        self._hl_image_tk = None
        self._hl_bbox = None  # (x0,y0,x1,y1)
        
        # 笔刷轨迹不能被选中和移动
        self.selectable = False
        
    def add_point(self, x: float, y: float):
        """添加轨迹点"""
        self.points.append((x, y))
        
        # 更新基准坐标为第一个点
        if len(self.points) == 1:
            self.x = x
            self.y = y
            
        # 如果是喷雾笔刷，为新添加的点生成固定的散点
        if self.brush_type == "brush_spray":
            self.generate_spray_dots_for_point(x, y)
        # 如果是铅笔笔刷，为新添加的线段生成固定的纹理
        elif self.brush_type == "brush_pencil" and len(self.points) > 1:
            # 获取最后两个点，为这条线段生成纹理
            x1, y1 = self.points[-2]
            x2, y2 = self.points[-1]
            self.generate_pencil_texture_for_segment(x1, y1, x2, y2)
        # 荧光笔改为与圆珠笔相同的连续笔迹样式，这里不再生成额外纹理
        elif self.brush_type == "brush_highlighter" and len(self.points) > 1:
            pass
    
    def generate_spray_dots_for_point(self, x_center: float, y_center: float):
        """为指定点生成固定的喷雾散点"""
        spray_radius = self.brush_size
        dots_per_point = 4  # 减少散点数量提高性能
        
        point_dots = []
        for _ in range(dots_per_point):
            # 在圆形区域内随机生成点
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0, spray_radius)
            
            # 计算散点坐标
            x = x_center + distance * math.cos(angle)
            y = y_center + distance * math.sin(angle)
            
            # 固定点大小
            dot_size = 1.0  # 固定大小，不再随机
            
            point_dots.append((x, y, dot_size))
        
        self.spray_dots.extend(point_dots)
    
    def generate_pencil_texture_for_segment(self, x1: float, y1: float, x2: float, y2: float):
        """为铅笔线段生成固定纹理"""
        import math
        
        # 计算线段长度和方向
        length = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        if length == 0:
            return
        
        # 主线条数据（多层叠加实现透明效果）
        for layer in range(5):  # 增加层数，每层更透明
            offset = layer * 0.2
            # 使用不同的透明度级别
            transparency_colors = ["#E8E8E8", "#D8D8D8", "#C8C8C8", "#B8B8B8", "#A8A8A8"]
            line_data = {
                'type': 'line',
                'x1': x1 + offset,
                'y1': y1 + offset,
                'x2': x2 + offset,
                'y2': y2 + offset,
                'width': max(1, self.brush_size - layer),
                'color': transparency_colors[layer],
                'stipple': 'gray25' if layer < 3 else ''  # 前几层使用stipple增加透明感
            }
            self.pencil_texture.append(line_data)
        
        # 纹理点数据（使用更透明的颜色）
        num_texture_points = max(1, int(length / 2))
        offset_range = self.brush_size / 3
        texture_colors = ["#F0F0F0", "#E0E0E0", "#D0D0D0", "#C0C0C0"]  # 更浅更透明的颜色
        
        for i in range(num_texture_points):
            t = i / max(1, num_texture_points - 1)
            x = x1 + t * (x2 - x1)
            y = y1 + t * (y2 - y1)
            
            for j, tex_color in enumerate(texture_colors):
                offset_x = random.uniform(-offset_range, offset_range)
                offset_y = random.uniform(-offset_range, offset_range)
                
                texture_x = x + offset_x
                texture_y = y + offset_y
                dot_size = random.uniform(0.1, 0.4)  # 更小的点
                
                dot_data = {
                    'type': 'dot',
                    'x': texture_x,
                    'y': texture_y,
                    'size': dot_size,
                    'color': tex_color
                }
                self.pencil_texture.append(dot_data)
    
    def generate_highlighter_lines_for_segment(self, x1: float, y1: float, x2: float, y2: float):
        """为荧光笔线段生成固定的左上到右下斜线"""
        import math
        
        # 计算线段长度和方向
        length = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        if length == 0:
            return
        
        # 计算垂直于线段的向量
        if length > 0:
            # 线段方向向量
            dx = (x2 - x1) / length
            dy = (y2 - y1) / length
            
            # 垂直向量（法线）
            nx = -dy
            ny = dx
        else:
            nx, ny = 0, 1
        
        # 沿着线段创建多条斜线
        num_lines = max(1, int(length / 3))  # 每3像素一条斜线
        line_spacing = length / max(1, num_lines)
        
        for i in range(num_lines + 1):
            # 在线段上的插值位置
            t = min(1.0, i * line_spacing / length) if length > 0 else 0
            center_x = x1 + t * (x2 - x1)
            center_y = y1 + t * (y2 - y1)
            
            # 在垂直方向上创建多条平行的斜线
            half_width = self.brush_size / 2
            num_parallel = max(3, int(self.brush_size / 2))  # 根据笔刷大小确定平行线数量
            
            for j in range(num_parallel):
                # 垂直偏移
                offset = (j - num_parallel / 2) * (half_width * 2 / num_parallel)
                base_x = center_x + nx * offset
                base_y = center_y + ny * offset
                
                # 创建左上到右下的斜线（45度角）
                line_length = self.brush_size * 0.8
                line_dx = line_length * 0.707  # cos(45°)
                line_dy = line_length * 0.707  # sin(45°)
                
                line_data = {
                    'x1': base_x - line_dx / 2,
                    'y1': base_y - line_dy / 2,
                    'x2': base_x + line_dx / 2,
                    'y2': base_y + line_dy / 2,
                    'width': max(1, int(self.brush_size / 8)),  # 细线条
                    'color': self.color
                }
                self.highlighter_lines.append(line_data)
    
    def draw(self, canvas):
        """在画布上绘制笔刷轨迹"""
        if not self.visible or len(self.points) < 2:
            return
            
        # 根据笔刷类型选择绘制方法
        if self.brush_type == "brush_ballpoint":
            self.draw_ballpoint(canvas)
        elif self.brush_type == "brush_spray":
            self.draw_spray(canvas)
        elif self.brush_type == "brush_pencil":
            self.draw_pencil(canvas)
        elif self.brush_type == "brush_highlighter":
            self.draw_highlighter(canvas)
        else:
            # 默认绘制方法
            self.draw_ballpoint(canvas)
    
    # ======= 实时绘制生命周期（与 DrawingManager 配合） =======
    def begin_live(self):
        """开始一次实时笔刷绘制，初始化临时缓存（为未来批量渲染预留）"""
        # 这里可以初始化批量缓存，如 self.temp_dots/self.temp_lines
        # 当前实现不需要特别处理，保留占位以兼容管理器
        self._live_mode = True

    def end_live_and_finalize(self):
        """结束实时绘制，清空临时缓存或将其固化到持久数组"""
        self._live_mode = False
        # 若未来有缓存，这里可将缓存合并到 spray_dots/pencil_texture 等

    def draw_ballpoint(self, canvas):
        """绘制圆珠笔效果"""
        # 绘制轨迹
        for i in range(len(self.points) - 1):
            x1, y1 = self.points[i]
            x2, y2 = self.points[i + 1]
            
            # 绘制线段
            canvas.create_line(x1, y1, x2, y2,
                             fill=self.color,
                             width=self.brush_size,
                             capstyle="round",
                             smooth=True,
                             tags="brush_stroke")
    
    def draw_spray(self, canvas):
        """绘制喷雾笔刷效果"""
        # 使用预生成的固定散点
        for x, y, dot_size in self.spray_dots:
            canvas.create_oval(x - dot_size, y - dot_size,
                             x + dot_size, y + dot_size,
                             fill=self.color,
                             outline=self.color,
                             tags="brush_stroke")
    
    def draw_pencil(self, canvas):
        """绘制铅笔效果"""
        # 使用预生成的固定纹理
        for texture_item in self.pencil_texture:
            if texture_item['type'] == 'line':
                # 绘制主线条
                canvas.create_line(texture_item['x1'], texture_item['y1'],
                                 texture_item['x2'], texture_item['y2'],
                                 fill=texture_item['color'],
                                 width=texture_item['width'],
                                 capstyle="round",
                                 smooth=True,
                                 tags="brush_stroke")
            elif texture_item['type'] == 'dot':
                # 绘制纹理点
                x, y = texture_item['x'], texture_item['y']
                size = texture_item['size']
                canvas.create_oval(x - size, y - size,
                                 x + size, y + size,
                                 fill=texture_item['color'],
                                 outline=texture_item['color'],
                                 tags="brush_stroke")
    
    def draw_highlighter(self, canvas):
        """绘制荧光笔效果 - 使用半透明图像叠加，形状同圆珠笔，真实50%透明"""
        if not self.points or len(self.points) < 2:
            return

        # 计算边界框
        xs = [p[0] for p in self.points]
        ys = [p[1] for p in self.points]
        pad = max(2, int(self.brush_size / 2 + 2))
        x0, y0 = int(min(xs)) - pad, int(min(ys)) - pad
        x1, y1 = int(max(xs)) + pad, int(max(ys)) + pad
        w, h = max(1, x1 - x0), max(1, y1 - y0)

        try:
            from PIL import Image, ImageDraw, ImageColor
            from PIL import ImageTk
        except Exception:
            # 回退到非透明方案（不推荐，但避免崩溃）
            effective_color = self._blend_with_bg(canvas, self.color, alpha=0.5)
            for i in range(len(self.points) - 1):
                xsa, ysa = self.points[i]
                xsb, ysb = self.points[i + 1]
                canvas.create_line(xsa, ysa, xsb, ysb,
                                   fill=effective_color,
                                   width=self.brush_size,
                                   capstyle="round",
                                   smooth=True,
                                   tags="brush_stroke")
            return

        # 创建透明画布
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img, "RGBA")

        # 颜色解析 + 50% 透明
        try:
            r, g, b = ImageColor.getrgb(self.color)
        except Exception:
            r, g, b = (0, 0, 0)
        rgba = (r, g, b, 128)

        # 画连续线段
        for i in range(len(self.points) - 1):
            xsa, ysa = self.points[i]
            xsb, ysb = self.points[i + 1]
            # 偏移到局部坐标
            ax, ay = xsa - x0, ysa - y0
            bx, by = xsb - x0, ysb - y0
            draw.line([(ax, ay), (bx, by)], fill=rgba, width=self.brush_size)
            # 端点加圆头（近似）
            rcap = self.brush_size / 2
            draw.ellipse([ax - rcap, ay - rcap, ax + rcap, ay + rcap], fill=rgba)
            draw.ellipse([bx - rcap, by - rcap, bx + rcap, by + rcap], fill=rgba)

        # 转成 Tk 图像并放到画布
        self._hl_image_tk = ImageTk.PhotoImage(img)
        canvas.create_image(x0, y0, image=self._hl_image_tk, anchor="nw", tags="brush_stroke")
        self._hl_bbox = (x0, y0, x1, y1)

    # ======= 颜色混合辅助函数（用于模拟50%透明） =======
    def _blend_with_bg(self, canvas, fg_color: str, alpha: float = 0.5) -> str:
        """将前景色与画布背景色做alpha混合，返回#RRGGBB
        注意：这是与画布背景颜色的混色，无法与已有笔迹逐像素混合，但足够模拟荧光笔半透明效果。
        """
        try:
            bg_color = canvas["bg"] if "bg" in canvas.keys() else canvas.cget("background")
        except Exception:
            # 兜底为白色背景
            bg_color = "white"

        fr, fg, fb = self._to_rgb_255(canvas, fg_color)
        br, bg, bb = self._to_rgb_255(canvas, bg_color)

        r = int(fr * alpha + br * (1 - alpha))
        g = int(fg * alpha + bg * (1 - alpha))
        b = int(fb * alpha + bb * (1 - alpha))
        return f"#{r:02X}{g:02X}{b:02X}"

    def _to_rgb_255(self, tk_widget, color_str: str):
        """使用 Tk 的 winfo_rgb 将任意颜色名/#RRGGBB 转成 0-255 范围的RGB元组"""
        try:
            r16, g16, b16 = tk_widget.winfo_rgb(color_str)
            return (r16 // 257, g16 // 257, b16 // 257)
        except Exception:
            # 解析失败返回黑色
            return (0, 0, 0)
    
    def get_bounds(self) -> Tuple[float, float, float, float]:
        """获取边界框"""
        if not self.points:
            return (self.x, self.y, self.x, self.y)
            
        xs = [p[0] for p in self.points]
        ys = [p[1] for p in self.points]
        
        half_brush = self.brush_size / 2
        return (
            min(xs) - half_brush,
            min(ys) - half_brush,
            max(xs) + half_brush,
            max(ys) + half_brush
        )
    
    def contains_point(self, x: float, y: float) -> bool:
        """检查点是否在轨迹内 - 笔刷轨迹不可选中，始终返回False"""
        return False
    
    def move(self, dx: float, dy: float):
        """移动轨迹 - 笔刷轨迹不可移动"""
        pass
    
    def get_resize_handles(self) -> List[Tuple[str, float, float]]:
        """获取缩放手柄 - 笔刷轨迹不可缩放"""
        return []
    
    def resize_by_handle(self, handle_name: str, new_x: float, new_y: float):
        """通过手柄缩放 - 笔刷轨迹不可缩放"""
        pass
    
    def scale(self, factor: float, center_x: float = None, center_y: float = None):
        """缩放 - 笔刷轨迹不可缩放"""
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = super().to_dict()
        data.update({
            'points': self.points,
            'brush_size': self.brush_size,
            'brush_type': self.brush_type,
            'spray_dots': self.spray_dots,
            'pencil_texture': self.pencil_texture,
            'highlighter_lines': self.highlighter_lines
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BrushStroke':
        """从字典创建实例"""
        stroke = cls(data.get('points', []), data.get('brush_type', 'brush_ballpoint'))
        stroke.color = data.get('color', 'black')
        stroke.line_width = data.get('line_width', 1)
        stroke.visible = data.get('visible', True)
        stroke.brush_size = data.get('brush_size', 5)
        stroke.spray_dots = data.get('spray_dots', [])
        stroke.pencil_texture = data.get('pencil_texture', [])
        stroke.highlighter_lines = data.get('highlighter_lines', [])
        return stroke
    
    def copy(self) -> 'BrushStroke':
        """创建副本"""
        new_stroke = BrushStroke(self.points.copy(), self.brush_type)
        new_stroke.color = self.color
        new_stroke.line_width = self.line_width
        new_stroke.visible = self.visible
        new_stroke.brush_size = self.brush_size
        new_stroke.spray_dots = self.spray_dots.copy()  # 复制散点数据
        new_stroke.pencil_texture = self.pencil_texture.copy()  # 复制铅笔纹理数据
        new_stroke.highlighter_lines = self.highlighter_lines.copy()  # 复制荧光笔斜线数据
        return new_stroke