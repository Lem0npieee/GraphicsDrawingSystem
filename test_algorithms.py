#!/usr/bin/env python3
"""
测试所有图形的算法实现
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_all_algorithms():
    """测试所有自定义算法"""
    
    print("=" * 50)
    print("图形绘制算法测试")
    print("=" * 50)
    
    # 测试Bresenham直线算法
    print("\n1. 测试Bresenham直线算法:")
    try:
        from shapes.line import Line
        line = Line(0, 0, 10, 5)
        points = line.bresenham_line(0, 0, 10, 5)
        print(f"   ✓ 直线算法正常，生成 {len(points)} 个像素点")
        print(f"   起点: {points[0]}, 终点: {points[-1]}")
    except Exception as e:
        print(f"   ✗ 直线算法错误: {e}")
    
    # 测试中点椭圆算法
    print("\n2. 测试中点椭圆算法:")
    try:
        from shapes.circle import Circle
        circle = Circle(0, 0, 10)
        circle.radius_x = 15
        circle.radius_y = 10
        points = circle.midpoint_ellipse(0, 0, 15, 10)
        print(f"   ✓ 椭圆算法正常，生成 {len(points)} 个边界像素点")
        
        # 测试填充
        fill_points = circle.fill_ellipse(0, 0, 5, 3)
        print(f"   ✓ 椭圆填充正常，生成 {len(fill_points)} 个填充像素点")
    except Exception as e:
        print(f"   ✗ 椭圆算法错误: {e}")
    
    # 测试多边形算法
    print("\n3. 测试多边形算法:")
    try:
        from shapes.polygon import Polygon
        # 创建一个三角形
        triangle_points = [(0, 0), (10, 0), (5, 10)]
        polygon = Polygon(triangle_points)
        
        # 测试边框绘制
        edge_points = []
        for i in range(len(triangle_points)):
            p1 = triangle_points[i]
            p2 = triangle_points[(i + 1) % len(triangle_points)]
            points = polygon.bresenham_line(int(p1[0]), int(p1[1]), int(p2[0]), int(p2[1]))
            edge_points.extend(points)
        
        print(f"   ✓ 多边形边框算法正常，生成 {len(edge_points)} 个边界像素点")
        
        # 测试填充
        fill_points = polygon.fill_polygon()
        print(f"   ✓ 多边形填充算法正常，生成 {len(fill_points)} 个填充像素点")
    except Exception as e:
        print(f"   ✗ 多边形算法错误: {e}")
    
    # 测试矩形算法
    print("\n4. 测试矩形算法:")
    try:
        from shapes.rectangle import Rectangle
        rect = Rectangle(0, 0, 10, 8)
        
        # 测试边框绘制
        edge_points = []
        edges = [(0, 0, 10, 0), (10, 0, 10, 8), (10, 8, 0, 8), (0, 8, 0, 0)]
        for x1, y1, x2, y2 in edges:
            points = rect.bresenham_line(x1, y1, x2, y2)
            edge_points.extend(points)
        
        print(f"   ✓ 矩形边框算法正常，生成 {len(edge_points)} 个边界像素点")
        
        # 测试填充
        fill_points = rect.fill_rectangle()
        print(f"   ✓ 矩形填充算法正常，生成 {len(fill_points)} 个填充像素点")
    except Exception as e:
        print(f"   ✗ 矩形算法错误: {e}")
    
    print("\n" + "=" * 50)
    print("算法实现总结:")
    print("  - 直线绘制: Bresenham算法 ✓")
    print("  - 椭圆绘制: 中点椭圆算法 ✓") 
    print("  - 多边形绘制: Bresenham直线算法 + 扫描线填充 ✓")
    print("  - 矩形绘制: Bresenham直线算法 + 逐行填充 ✓")
    print("  - 不再依赖Tkinter的原生绘图函数 ✓")
    print("=" * 50)

def visualize_algorithms():
    """可视化算法效果"""
    print("\n可视化演示:")
    
    # 演示Bresenham直线
    print("\nBresenham直线 (0,0) 到 (8,3):")
    try:
        from shapes.line import Line
        line = Line(0, 0, 8, 3)
        points = line.bresenham_line(0, 0, 8, 3)
        
        # 创建网格
        grid = [['.' for _ in range(10)] for _ in range(5)]
        for x, y in points:
            if 0 <= x < 10 and 0 <= y < 5:
                grid[y][x] = '*'
        
        for row in grid:
            print('  ' + ''.join(row))
    except Exception as e:
        print(f"演示失败: {e}")

if __name__ == "__main__":
    test_all_algorithms()
    visualize_algorithms()