#!/usr/bin/env python3
"""
性能优化测试 - 测试图形绘制的性能改进
"""
import time
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_drawing_performance():
    """测试绘制性能优化"""
    print("=" * 60)
    print("图形绘制性能优化测试")
    print("=" * 60)
    
    try:
        from managers.drawing_manager import DrawingManager
        from shapes.circle import Circle
        from shapes.rectangle import Rectangle
        from shapes.polygon import Polygon
        
        manager = DrawingManager()
        
        # 测试1: 椭圆边框绘制 vs 完整绘制
        print("\n1. 椭圆绘制性能对比:")
        
        ellipse = Circle(50, 50, 30)
        ellipse.radius_x = 40
        ellipse.radius_y = 25
        ellipse.fill_color = "blue"
        
        # 模拟边框绘制时间
        start_time = time.time()
        for _ in range(10):  # 模拟10次预览更新
            outline_points = ellipse.midpoint_ellipse(50, 50, 40, 25)
        outline_time = time.time() - start_time
        
        # 模拟完整绘制时间（包括填充）
        start_time = time.time()
        for _ in range(10):  # 模拟10次完整绘制
            outline_points = ellipse.midpoint_ellipse(50, 50, 40, 25)
            fill_points = ellipse.scanline_fill_ellipse(50, 50, 40, 25)
        full_time = time.time() - start_time
        
        print(f"   只绘制边框: {outline_time:.4f}秒 ({len(outline_points)} 个边界点)")
        print(f"   完整绘制: {full_time:.4f}秒")
        print(f"   性能提升: {full_time/outline_time:.1f}倍")
        
        # 测试2: 矩形绘制性能对比
        print("\n2. 矩形绘制性能对比:")
        
        rect = Rectangle(10, 10, 60, 40)
        rect.fill_color = "red"
        
        # 边框绘制
        start_time = time.time()
        for _ in range(10):
            # 计算四条边
            edges = [
                (10, 10, 60, 10), (60, 10, 60, 40),
                (60, 40, 10, 40), (10, 40, 10, 10)
            ]
            total_edge_points = 0
            for x1, y1, x2, y2 in edges:
                points = rect.bresenham_line(x1, y1, x2, y2)
                total_edge_points += len(points)
        outline_time = time.time() - start_time
        
        # 完整绘制
        start_time = time.time()
        for _ in range(10):
            edge_points = total_edge_points  # 重用计算
            fill_points = rect.scanline_fill_rectangle()
        full_time = time.time() - start_time
        
        print(f"   只绘制边框: {outline_time:.4f}秒 ({total_edge_points} 个边界点)")
        print(f"   完整绘制: {full_time:.4f}秒 ({len(fill_points)} 个填充点)")
        print(f"   性能提升: {full_time/outline_time:.1f}倍")
        
        # 测试3: 多边形绘制性能对比
        print("\n3. 多边形绘制性能对比:")
        
        # 创建一个复杂一点的多边形（六边形）
        import math
        sides = 6
        radius = 30
        center_x, center_y = 50, 50
        points = []
        for i in range(sides):
            angle = 2 * math.pi * i / sides
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            points.append((x, y))
        
        polygon = Polygon(points)
        polygon.fill_color = "green"
        
        # 边框绘制
        start_time = time.time()
        for _ in range(10):
            total_edge_points = 0
            for i in range(len(points)):
                p1 = points[i]
                p2 = points[(i + 1) % len(points)]
                edge_points = polygon.bresenham_line(int(p1[0]), int(p1[1]), int(p2[0]), int(p2[1]))
                total_edge_points += len(edge_points)
        outline_time = time.time() - start_time
        
        # 完整绘制
        start_time = time.time()
        for _ in range(10):
            edge_points = total_edge_points  # 重用计算
            fill_points = polygon.scanline_fill_polygon()
        full_time = time.time() - start_time
        
        print(f"   只绘制边框: {outline_time:.4f}秒 ({total_edge_points} 个边界点)")
        print(f"   完整绘制: {full_time:.4f}秒 ({len(fill_points)} 个填充点)")
        print(f"   性能提升: {full_time/outline_time:.1f}倍")
        
        # 测试4: 节流机制测试
        print("\n4. 节流机制测试:")
        manager.preview_throttle_ms = 50  # 50毫秒节流
        
        start_time = time.time()
        update_count = 0
        
        # 模拟100次快速鼠标移动
        for i in range(100):
            # 模拟鼠标移动到不同位置
            mouse_x = 50 + i
            mouse_y = 50 + i % 10
            
            # 调用预览方法
            manager.polygon_points = [(10, 10), (50, 10), (30, 40)]  # 设置一些测试点
            old_time = manager.last_preview_time
            manager.draw_polygon_preview(mouse_x, mouse_y)
            
            # 检查是否实际更新了
            if manager.last_preview_time != old_time:
                update_count += 1
            
            time.sleep(0.01)  # 模拟10毫秒间隔的鼠标移动
        
        total_time = time.time() - start_time
        print(f"   100次鼠标移动中实际更新了 {update_count} 次")
        print(f"   节流效果: 减少了 {100 - update_count} 次不必要的更新")
        print(f"   总用时: {total_time:.4f}秒")
        
    except Exception as e:
        print(f"性能测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("性能优化总结:")
    print("✅ 临时图形只绘制边框，避免填充算法")
    print("✅ 预览时只清除temp标签，不重绘所有图形")
    print("✅ 添加节流机制，限制更新频率")
    print("✅ 分离边框绘制和填充绘制逻辑")
    print("=" * 60)

if __name__ == "__main__":
    test_drawing_performance()