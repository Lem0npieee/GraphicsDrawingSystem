# 图形模块初始化文件
from .base_shape import BaseShape
from .point import Point
from .line import Line
from .rectangle import Rectangle
from .circle import Circle
from .polygon import Polygon
from .bezier_curve import BezierCurve
from .brush_stroke import BrushStroke
from .image import Image

__all__ = ['BaseShape', 'Point', 'Line', 'Rectangle', 'Circle', 'Polygon', 'BezierCurve', 'BrushStroke', 'Image']