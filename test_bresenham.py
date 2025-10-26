#!/usr/bin/env python3
"""
测试Bresenham算法实现
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from shapes.line import Line

def test_bresenham():
    """测试Bresenham算法"""
    print("测试Bresenham直线算法...")
    
    # 创建一条测试直线
    line = Line(0, 0, 10, 5)
    
    # 测试算法
    points = line.bresenham_line(0, 0, 10, 5)
    
    print(f"从(0,0)到(10,5)的直线像素点:")
    for i, (x, y) in enumerate(points):
        print(f"点{i+1}: ({x}, {y})")
    
    print(f"\n总共生成了 {len(points)} 个像素点")
    
    # 测试垂直线
    print("\n测试垂直线...")
    vertical_points = line.bresenham_line(5, 0, 5, 8)
    print(f"垂直线点数: {len(vertical_points)}")
    
    # 测试水平线
    print("\n测试水平线...")
    horizontal_points = line.bresenham_line(0, 3, 8, 3)
    print(f"水平线点数: {len(horizontal_points)}")
    
    # 测试对角线
    print("\n测试对角线...")
    diagonal_points = line.bresenham_line(0, 0, 5, 5)
    print(f"对角线点数: {len(diagonal_points)}")
    for x, y in diagonal_points:
        print(f"({x}, {y})")

if __name__ == "__main__":
    test_bresenham()