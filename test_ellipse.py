#!/usr/bin/env python3
"""
测试中点椭圆算法实现
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from shapes.circle import Circle

def test_midpoint_ellipse():
    """测试中点椭圆算法"""
    print("测试中点椭圆算法...")
    
    # 创建一个测试椭圆
    ellipse = Circle(50, 50, 20)
    ellipse.radius_x = 30  # 水平半径
    ellipse.radius_y = 20  # 垂直半径
    
    # 测试圆形 (rx = ry)
    print("测试圆形 (半径=10):")
    circle_points = ellipse.midpoint_ellipse(0, 0, 10, 10)
    print(f"圆形边界点数: {len(circle_points)}")
    
    # 显示前10个点
    print("前10个点:")
    for i, (x, y) in enumerate(circle_points[:10]):
        print(f"  点{i+1}: ({x}, {y})")
    
    # 测试椭圆 (rx != ry)
    print(f"\n测试椭圆 (rx=20, ry=15):")
    ellipse_points = ellipse.midpoint_ellipse(0, 0, 20, 15)
    print(f"椭圆边界点数: {len(ellipse_points)}")
    
    # 测试极端情况
    print(f"\n测试线段椭圆 (rx=1, ry=10):")
    line_ellipse_points = ellipse.midpoint_ellipse(0, 0, 1, 10)
    print(f"线段椭圆点数: {len(line_ellipse_points)}")
    
    # 测试填充
    print(f"\n测试小椭圆填充 (rx=3, ry=2):")
    fill_points = ellipse.fill_ellipse(0, 0, 3, 2)
    print(f"填充点数: {len(fill_points)}")
    
    # 打印填充点分布
    print("填充点坐标:")
    for x in range(-3, 4):
        line = ""
        for y in range(-2, 3):
            if (x, y) in fill_points:
                line += "●"
            else:
                line += "○"
        print(f"x={x:2d}: {line}")

def visualize_ellipse_in_console():
    """在控制台可视化椭圆"""
    print("\n控制台椭圆可视化:")
    ellipse = Circle(0, 0, 5)
    
    # 测试小椭圆
    rx, ry = 8, 5
    points = ellipse.midpoint_ellipse(0, 0, rx, ry)
    
    # 创建显示网格
    width, height = 2 * rx + 5, 2 * ry + 5
    grid = [['.' for _ in range(width)] for _ in range(height)]
    
    # 标记椭圆点
    for x, y in points:
        grid_x = x + rx + 2
        grid_y = y + ry + 2
        if 0 <= grid_x < width and 0 <= grid_y < height:
            grid[grid_y][grid_x] = '*'
    
    # 标记中心点
    center_x, center_y = rx + 2, ry + 2
    grid[center_y][center_x] = '+'
    
    # 打印网格
    print(f"椭圆 (rx={rx}, ry={ry}):")
    for row in grid:
        print(''.join(row))

if __name__ == "__main__":
    test_midpoint_ellipse()
    visualize_ellipse_in_console()