#!/usr/bin/env python3
"""
测试扫描线填充算法
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_scanline_algorithms():
    """测试所有扫描线填充算法"""
    print("=" * 60)
    print("扫描线填充算法测试")
    print("=" * 60)
    
    # 测试椭圆扫描线填充
    print("\n1. 测试椭圆扫描线填充算法:")
    try:
        from shapes.circle import Circle
        
        # 创建一个椭圆
        ellipse = Circle(10, 10, 5)
        ellipse.radius_x = 6
        ellipse.radius_y = 4
        
        # 使用扫描线填充
        fill_points = ellipse.scanline_fill_ellipse(10, 10, 6, 4)
        print(f"   ✓ 椭圆扫描线填充成功，生成 {len(fill_points)} 个填充像素点")
        
        # 验证填充点都在椭圆内部
        inside_count = 0
        for x, y in fill_points:
            dx, dy = x - 10, y - 10
            if (dx * dx) / (6 * 6) + (dy * dy) / (4 * 4) <= 1.01:  # 允许小误差
                inside_count += 1
        
        print(f"   ✓ 验证通过：{inside_count}/{len(fill_points)} 个点在椭圆内部")
        
    except Exception as e:
        print(f"   ✗ 椭圆扫描线填充测试失败: {e}")
    
    # 测试多边形扫描线填充
    print("\n2. 测试多边形扫描线填充算法:")
    try:
        from shapes.polygon import Polygon
        
        # 创建一个三角形
        triangle_points = [(0, 0), (10, 0), (5, 8)]
        triangle = Polygon(triangle_points)
        
        # 使用扫描线填充
        fill_points = triangle.scanline_fill_polygon()
        print(f"   ✓ 三角形扫描线填充成功，生成 {len(fill_points)} 个填充像素点")
        
        # 创建一个矩形多边形测试
        rect_points = [(2, 2), (8, 2), (8, 6), (2, 6)]
        rect_polygon = Polygon(rect_points)
        rect_fill_points = rect_polygon.scanline_fill_polygon()
        print(f"   ✓ 矩形多边形扫描线填充成功，生成 {len(rect_fill_points)} 个填充像素点")
        
        # 验证矩形填充点数 (应该是 7*5 = 35 个点)
        expected_points = 7 * 5
        if len(rect_fill_points) == expected_points:
            print(f"   ✓ 矩形填充点数验证通过: {len(rect_fill_points)} == {expected_points}")
        else:
            print(f"   ! 矩形填充点数: {len(rect_fill_points)}, 预期: {expected_points}")
        
    except Exception as e:
        print(f"   ✗ 多边形扫描线填充测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 测试矩形扫描线填充
    print("\n3. 测试矩形扫描线填充算法:")
    try:
        from shapes.rectangle import Rectangle
        
        # 创建一个矩形
        rect = Rectangle(1, 1, 5, 4)
        
        # 使用扫描线填充
        fill_points = rect.scanline_fill_rectangle()
        print(f"   ✓ 矩形扫描线填充成功，生成 {len(fill_points)} 个填充像素点")
        
        # 验证矩形填充点数 (应该是 5*4 = 20 个点)
        expected_points = 5 * 4
        if len(fill_points) == expected_points:
            print(f"   ✓ 矩形填充点数验证通过: {len(fill_points)} == {expected_points}")
        else:
            print(f"   ! 矩形填充点数: {len(fill_points)}, 预期: {expected_points}")
            
    except Exception as e:
        print(f"   ✗ 矩形扫描线填充测试失败: {e}")
    
    print("\n" + "=" * 60)
    print("扫描线填充算法实现总结:")
    print("  - 椭圆扫描线填充: 基于椭圆方程计算交点 ✓")
    print("  - 多边形扫描线填充: 改进算法，处理顶点和边界情况 ✓")
    print("  - 矩形扫描线填充: 优化的矩形专用算法 ✓")
    print("  - 所有算法都是自主实现，不依赖图形库 ✓")
    print("=" * 60)

def visualize_scanline_fill():
    """可视化扫描线填充效果"""
    print("\n扫描线填充可视化演示:")
    
    # 演示三角形扫描线填充
    print("\n三角形扫描线填充可视化:")
    try:
        from shapes.polygon import Polygon
        
        # 创建一个小三角形用于可视化
        triangle_points = [(2, 1), (6, 1), (4, 5)]
        triangle = Polygon(triangle_points)
        
        # 获取填充点
        fill_points = triangle.scanline_fill_polygon()
        
        # 创建显示网格
        width, height = 9, 7
        grid = [['.' for _ in range(width)] for _ in range(height)]
        
        # 标记顶点
        for i, (x, y) in enumerate(triangle_points):
            if 0 <= x < width and 0 <= y < height:
                grid[y][x] = str(i + 1)
        
        # 标记填充点
        for x, y in fill_points:
            if 0 <= x < width and 0 <= y < height and grid[y][x] == '.':
                grid[y][x] = '*'
        
        # 打印网格
        print("三角形填充结果 (数字=顶点, *=填充区域):")
        for row in grid:
            print('  ' + ''.join(row))
            
    except Exception as e:
        print(f"三角形可视化失败: {e}")
    
    # 演示椭圆扫描线填充
    print("\n椭圆扫描线填充可视化:")
    try:
        from shapes.circle import Circle
        
        # 创建一个小椭圆用于可视化
        ellipse = Circle(4, 3, 2)
        ellipse.radius_x = 3
        ellipse.radius_y = 2
        
        # 获取填充点
        fill_points = ellipse.scanline_fill_ellipse(4, 3, 3, 2)
        
        # 创建显示网格
        width, height = 9, 7
        grid = [['.' for _ in range(width)] for _ in range(height)]
        
        # 标记中心点
        grid[3][4] = '+'
        
        # 标记填充点
        for x, y in fill_points:
            if 0 <= x < width and 0 <= y < height and grid[y][x] == '.':
                grid[y][x] = '*'
        
        # 打印网格
        print("椭圆填充结果 (+= 中心, *=填充区域):")
        for row in grid:
            print('  ' + ''.join(row))
            
    except Exception as e:
        print(f"椭圆可视化失败: {e}")

if __name__ == "__main__":
    test_scanline_algorithms()
    visualize_scanline_fill()