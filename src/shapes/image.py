"""
图像类 - 支持加载和显示图片的形状
"""
from typing import Tuple, Dict, Any, Optional
from .rectangle import Rectangle
import tkinter as tk
from PIL import Image as PILImage, ImageTk
import os


class Image(Rectangle):
    """图像形状类，继承自Rectangle以获得拉伸、移动等功能"""
    
    def __init__(self, x1: float, y1: float, x2: float, y2: float, image_path: str = None):
        super().__init__(x1, y1, x2, y2)
        self.image_path = image_path
        self.pil_image = None  # PIL图像对象
        self.tk_image = None   # Tkinter图像对象
        self.canvas_image_id = None  # 画布图像ID
        self.original_width = 0
        self.original_height = 0
        
        # 如果提供了图片路径，尝试加载图片
        if image_path:
            self.load_image(image_path)
    
    def load_image(self, image_path: str) -> bool:
        """加载图片文件"""
        try:
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"图片文件不存在: {image_path}")
            
            # 使用PIL加载图片
            self.pil_image = PILImage.open(image_path)
            self.original_width, self.original_height = self.pil_image.size
            self.image_path = image_path
            
            # 初始时调整图片大小以适应矩形
            self._resize_image()
            return True
            
        except Exception as e:
            print(f"加载图片失败: {e}")
            return False
    
    def _resize_image(self):
        """根据当前矩形大小调整图片"""
        if not self.pil_image:
            return
        
        try:
            # 计算新的图片尺寸
            new_width = int(self.width)
            new_height = int(self.height)
            
            if new_width <= 0 or new_height <= 0:
                return
            
            # 调整图片大小
            resized_image = self.pil_image.resize((new_width, new_height), PILImage.Resampling.LANCZOS)
            
            # 转换为Tkinter可用的格式
            self.tk_image = ImageTk.PhotoImage(resized_image)
            
        except Exception as e:
            print(f"调整图片大小失败: {e}")
    
    def draw(self, canvas):
        """在画布上绘制图像"""
        if not self.visible:
            return
        
        # 如果有图片，绘制图片
        if self.tk_image:
            # 删除之前的图像
            if self.canvas_image_id:
                canvas.delete(self.canvas_image_id)
            
            # 绘制图片到画布中心
            center_x = (self.x1 + self.x2) / 2
            center_y = (self.y1 + self.y2) / 2
            
            self.canvas_image_id = canvas.create_image(
                center_x, center_y,
                image=self.tk_image,
                anchor=tk.CENTER
            )
        
        # 如果被选中，绘制选择框
        if self.selected:
            outline_color = "red"
            canvas.create_rectangle(self.x1, self.y1, self.x2, self.y2,
                                  outline=outline_color, width=2, fill="", tags="selection")
            
            # 绘制调整手柄
            self._draw_resize_handles(canvas)
    
    def _draw_resize_handles(self, canvas):
        """绘制调整手柄"""
        handle_size = 6
        handles = [
            (self.x1, self.y1),  # 左上
            (self.x2, self.y1),  # 右上
            (self.x1, self.y2),  # 左下
            (self.x2, self.y2),  # 右下
            ((self.x1 + self.x2) / 2, self.y1),  # 上中
            ((self.x1 + self.x2) / 2, self.y2),  # 下中
            (self.x1, (self.y1 + self.y2) / 2),  # 左中
            (self.x2, (self.y1 + self.y2) / 2),  # 右中
        ]
        
        for x, y in handles:
            canvas.create_rectangle(
                x - handle_size // 2, y - handle_size // 2,
                x + handle_size // 2, y + handle_size // 2,
                outline="red", fill="white", width=1, tags="selection"
            )
    
    def update_bounds(self, x1: float, y1: float, x2: float, y2: float):
        """更新边界并重新调整图片大小"""
        # 确保坐标正确
        self.x1 = min(x1, x2)
        self.y1 = min(y1, y2)
        self.x2 = max(x1, x2)
        self.y2 = max(y1, y2)
        
        # 更新宽高
        self.width = self.x2 - self.x1
        self.height = self.y2 - self.y1
        
        # 更新基类的位置（中心点）
        self.x = (self.x1 + self.x2) / 2
        self.y = (self.y1 + self.y2) / 2
        
        # 重新调整图片大小
        self._resize_image()
    
    def move(self, dx: float, dy: float):
        """移动图像"""
        super().move(dx, dy)
        self.x1 += dx
        self.y1 += dy
        self.x2 += dx
        self.y2 += dy
    
    def contains_point(self, x: float, y: float) -> bool:
        """检查点是否在图像内"""
        return self.x1 <= x <= self.x2 and self.y1 <= y <= self.y2
    
    def get_bounds(self) -> Tuple[float, float, float, float]:
        """获取边界框"""
        return self.x1, self.y1, self.x2, self.y2
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式（用于保存）"""
        data = super().to_dict()
        data.update({
            'type': 'image',
            'x1': self.x1,
            'y1': self.y1,
            'x2': self.x2,
            'y2': self.y2,
            'width': self.width,
            'height': self.height,
            'image_path': self.image_path,
            'original_width': self.original_width,
            'original_height': self.original_height
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Image':
        """从字典创建图像对象"""
        image = cls(data['x1'], data['y1'], data['x2'], data['y2'])
        
        # 设置基本属性
        image.color = data.get('color', 'black')
        image.fill_color = data.get('fill_color', None)
        image.line_width = data.get('line_width', 1)
        image.visible = data.get('visible', True)
        image.selected = data.get('selected', False)
        
        # 设置图像特有属性
        image.image_path = data.get('image_path')
        image.original_width = data.get('original_width', 0)
        image.original_height = data.get('original_height', 0)
        
        # 重新加载图片
        if image.image_path:
            image.load_image(image.image_path)
        
        return image
    
    def copy(self) -> 'Image':
        """创建图像的副本"""
        new_image = Image(self.x1, self.y1, self.x2, self.y2, self.image_path)
        new_image.color = self.color
        new_image.fill_color = self.fill_color
        new_image.line_width = self.line_width
        new_image.visible = self.visible
        return new_image
    
    def resize_by_handle(self, handle_type: str, dx: float, dy: float):
        """保持长宽比的调整大小"""
        if not self.pil_image:
            # 如果没有图片，使用默认的resize行为
            super().resize_by_handle(handle_type, dx, dy)
            return
        
        # 计算原始长宽比
        aspect_ratio = self.original_width / self.original_height
        
        # 保存当前边界
        old_x1, old_y1, old_x2, old_y2 = self.x1, self.y1, self.x2, self.y2
        
        # 根据拖拽方向计算新的尺寸
        if handle_type in ['nw', 'ne', 'se', 'sw']:  # 角点拖拽
            if handle_type == 'se':  # 右下角
                # 以左上角为锚点
                new_width = max(20, self.width + dx)
                new_height = new_width / aspect_ratio
                self.x2 = self.x1 + new_width
                self.y2 = self.y1 + new_height
                
            elif handle_type == 'sw':  # 左下角
                # 以右上角为锚点
                new_width = max(20, self.width - dx)
                new_height = new_width / aspect_ratio
                self.x1 = self.x2 - new_width
                self.y2 = self.y1 + new_height
                
            elif handle_type == 'ne':  # 右上角
                # 以左下角为锚点
                new_width = max(20, self.width + dx)
                new_height = new_width / aspect_ratio
                self.x2 = self.x1 + new_width
                self.y1 = self.y2 - new_height
                
            elif handle_type == 'nw':  # 左上角
                # 以右下角为锚点
                new_width = max(20, self.width - dx)
                new_height = new_width / aspect_ratio
                self.x1 = self.x2 - new_width
                self.y1 = self.y2 - new_height
                
        else:  # 边缘拖拽，也保持长宽比
            if handle_type in ['e', 'w']:  # 水平拖拽
                if handle_type == 'e':
                    new_width = max(20, self.width + dx)
                else:  # 'w'
                    new_width = max(20, self.width - dx)
                
                new_height = new_width / aspect_ratio
                center_x = (self.x1 + self.x2) / 2
                center_y = (self.y1 + self.y2) / 2
                
                self.x1 = center_x - new_width / 2
                self.x2 = center_x + new_width / 2
                self.y1 = center_y - new_height / 2
                self.y2 = center_y + new_height / 2
                
            elif handle_type in ['n', 's']:  # 垂直拖拽
                if handle_type == 's':
                    new_height = max(20, self.height + dy)
                else:  # 'n'
                    new_height = max(20, self.height - dy)
                
                new_width = new_height * aspect_ratio
                center_x = (self.x1 + self.x2) / 2
                center_y = (self.y1 + self.y2) / 2
                
                self.x1 = center_x - new_width / 2
                self.x2 = center_x + new_width / 2
                self.y1 = center_y - new_height / 2
                self.y2 = center_y + new_height / 2
        
        # 更新宽高
        self.width = self.x2 - self.x1
        self.height = self.y2 - self.y1
        
        # 更新中心点
        self.x = (self.x1 + self.x2) / 2
        self.y = (self.y1 + self.y2) / 2
        
        # 重新调整图片大小
        self._resize_image()
