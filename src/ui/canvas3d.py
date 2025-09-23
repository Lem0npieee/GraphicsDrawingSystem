import tkinter as tk
import math
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shapes3d import BaseShape3D, Point3D, Vector3D


class Canvas3D:
    """简易3D画布：显示网格地板，右键拖动旋转，滚轮缩放（目标点固定）。"""

    def __init__(self, parent, width=800, height=600, bg="#1e1e1e"):
        self.parent = parent
        self.canvas = tk.Canvas(parent, bg=bg, width=width, height=height, highlightthickness=0)

        # 相机参数（球坐标）
        self.target = (0.0, 0.0, 0.0)
        self.distance = 20.0
        self.yaw = 45.0  # 水平角度（度）
        self.pitch = 30.0  # 俯仰角（度）

        # 网格参数
        self.grid_size = 10  # 基础网格大小
        self.grid_step = 1
        self.grid_color_major = "#3a3a3a"
        self.grid_color_minor = "#2a2a2a"
        self.axis_x_color = "#bb5555"
        self.axis_y_color = "#55bb55"  # Y轴绿色
        self.axis_z_color = "#5599bb"

        # 3D图形管理
        self.shapes_3d = []  # 3D图形列表
        self.selected_shape = None  # 当前选中的图形
        self.show_gizmos = True  # 是否显示操作控件

        # 变换模式
        self.transform_mode = "move"  # "move", "scale", "rotate"
        
        # 回调函数
        self.selection_callback = None  # 选择改变时的回调
        
        # 状态
        self._last_rx = None
        self._last_ry = None
        self.has_content = False  # 网格不算内容

        # 交互状态
        self.dragging = False
        self.drag_start_pos = None
        self.drag_gizmo_axis = None  # 当前拖动的轴（'x', 'y', 'z'）
        self.rotation_start = {}  # 旋转模式的起始状态
        self.hover_gizmo_axis = None  # 当前悬停的轴
        
        # 绑定事件
        self.canvas.bind("<Configure>", lambda e: self.redraw())
        self.canvas.bind("<Button-3>", self._on_right_press)
        self.canvas.bind("<B3-Motion>", self._on_right_drag)
        self.canvas.bind("<MouseWheel>", self._on_mouse_wheel)
        self.canvas.bind("<Button-1>", self._on_left_click)
        self.canvas.bind("<B1-Motion>", self._on_left_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_left_release)
        self.canvas.bind("<Motion>", self._on_mouse_move)

    def pack(self, **kwargs):
        self.canvas.pack(**kwargs)

    def pack_forget(self):
        self.canvas.pack_forget()

    def clear_objects(self):
        self.shapes_3d.clear()
        self.selected_shape = None
        self.has_content = False
        self.redraw()

    def set_transform_mode(self, mode):
        """设置变换模式：move, scale, rotate"""
        if mode in ["move", "scale", "rotate"]:
            # 检查当前选中图形的变换限制
            if self.selected_shape:
                allowed_modes = self._get_allowed_transform_modes(self.selected_shape)
                if mode not in allowed_modes:
                    # 如果当前模式不被允许，默认切换到移动模式
                    mode = "move"
            
            self.transform_mode = mode
            self.redraw()  # 重绘以更新gizmo显示
    
    def _get_allowed_transform_modes(self, shape):
        """获取指定图形允许的变换模式"""
        if isinstance(shape, Point3D):
            # 点只能移动
            return ["move"]
        elif isinstance(shape, Vector3D):
            # 向量可以移动和缩放（但缩放有特殊处理）
            return ["move", "scale"]
        else:
            # 其他图形支持所有模式
            return ["move", "scale", "rotate"]
    
    def get_transform_mode(self):
        """获取当前变换模式"""
        return self.transform_mode

    # 事件处理
    def _on_right_press(self, event):
        self._last_rx, self._last_ry = event.x, event.y

    def _on_right_drag(self, event):
        if self._last_rx is None:
            self._last_rx, self._last_ry = event.x, event.y
            return
        dx = event.x - self._last_rx
        dy = event.y - self._last_ry
        self._last_rx, self._last_ry = event.x, event.y

        self.yaw = (self.yaw - dx * 0.4) % 360  # 改为减法，右拖=逆时针
        self.pitch = max(-89.0, min(89.0, self.pitch + dy * 0.3))  # 改为加法，上拖=向上看
        self.redraw()

    def _on_mouse_wheel(self, event):
        # Windows: event.delta 为±120的倍数
        zoom_factor = 1.0 - (event.delta / 1200.0)
        self.distance = max(2.0, min(200.0, self.distance * zoom_factor))
        self.redraw()
    
    def _on_left_click(self, event):
        """左键点击处理：选择3D图形或开始拖动操作"""
        self.drag_start_pos = (event.x, event.y)
        self.dragging = False
        self.drag_gizmo_axis = None
        
        # 检查是否点击了gizmo控件
        if self.selected_shape and self.show_gizmos:
            gizmo_axis = self._check_gizmo_click(event.x, event.y)
            if gizmo_axis:
                self.drag_gizmo_axis = gizmo_axis
                self.dragging = True
                return
        
        # 检查是否点击了3D图形
        clicked_shape = self._pick_shape(event.x, event.y)
        if clicked_shape:
            self.select_shape(clicked_shape)
            self.dragging = True
        else:
            self.select_shape(None)
    
    def _on_left_drag(self, event):
        """左键拖动处理"""
        if not self.dragging or not self.drag_start_pos:
            return
            
        dx = event.x - self.drag_start_pos[0]
        dy = event.y - self.drag_start_pos[1]
        
        if self.drag_gizmo_axis and self.selected_shape:
            # 拖动gizmo轴进行单轴移动
            self._drag_gizmo(dx, dy)
        elif self.selected_shape:
            # 拖动图形进行自由移动
            self._drag_shape(dx, dy)
        
        self.drag_start_pos = (event.x, event.y)
    
    def _on_left_release(self, event):
        """左键释放处理"""
        self.dragging = False
        self.drag_start_pos = None
        self.drag_gizmo_axis = None
    
    def _on_mouse_move(self, event):
        """鼠标移动处理：更新悬停状态以高亮可选择的陀螺仪环"""
        if self.dragging:
            return  # 正在拖动时不处理悬停
        
        old_hover = self.hover_gizmo_axis
        self.hover_gizmo_axis = self._check_gizmo_click(event.x, event.y)
        
        # 如果悬停状态发生变化，重新绘制以显示高亮效果
        if old_hover != self.hover_gizmo_axis:
            self.redraw()

    # 渲染
    def redraw(self):
        c = self.canvas
        w = c.winfo_width()
        h = c.winfo_height()
        if w <= 1 or h <= 1:
            return
        c.delete("all")

        # 计算相机位置
        rad_yaw = math.radians(self.yaw)
        rad_pitch = math.radians(self.pitch)
        cx = self.target[0] + self.distance * math.cos(rad_pitch) * math.cos(rad_yaw)
        cy = self.target[1] + self.distance * math.sin(rad_pitch)
        cz = self.target[2] + self.distance * math.cos(rad_pitch) * math.sin(rad_yaw)

        # 预计算投影比例
        fov = math.radians(60.0)
        f = 1.0 / math.tan(fov / 2.0)
        scale = (h / 2.0) * f

        def world_to_screen(px, py, pz):
            # 视图坐标
            # 生成相机坐标系
            tx, ty, tz = self.target
            # 前向（摄像机 -> 目标）
            zx, zy, zz = (tx - cx, ty - cy, tz - cz)
            zlen = math.sqrt(zx*zx + zy*zy + zz*zz) or 1.0
            zx, zy, zz = zx / zlen, zy / zlen, zz / zlen
            # 右向
            upx, upy, upz = 0.0, 1.0, 0.0
            xx = upy * zz - upz * zy
            xy = upz * zx - upx * zz
            xz = upx * zy - upy * zx
            xlen = math.sqrt(xx*xx + xy*xy + xz*xz) or 1.0
            xx, xy, xz = xx / xlen, xy / xlen, xz / xlen
            # 上向
            yx = zy * xz - zz * xy
            yy = zz * xx - zx * xz
            yz = zx * xy - zy * xx

            # 点到相机坐标
            dx, dy, dz = px - cx, py - cy, pz - cz
            rx = dx * xx + dy * xy + dz * xz
            ry = dx * yx + dy * yy + dz * yz
            rz = dx * zx + dy * zy + dz * zz
            if rz <= 0.1:
                return None
            sx = w/2.0 + (rx * scale) / rz
            sy = h/2.0 - (ry * scale) / rz
            return (sx, sy)

        # 动态计算网格渲染范围（基于视距和视角）
        # 距离越远，需要渲染的网格范围越大，营造无限延伸的效果
        dynamic_range = max(30, int(self.distance * 2.0))
        
        # 绘制网格线 - 使用更宽松的渲染条件
        grid_lines = []
        for i in range(-dynamic_range, dynamic_range + 1, self.grid_step):
            color = self.grid_color_major if i % 5 == 0 else self.grid_color_minor
            
            # 线平行X轴（沿Z变化）
            p1 = world_to_screen(-dynamic_range, 0, i)
            p2 = world_to_screen(dynamic_range, 0, i)
            # 只要有一个点能投影就绘制线段
            if p1 or p2:
                if not p1:
                    p1 = world_to_screen(-dynamic_range*0.5, 0, i)
                if not p2:
                    p2 = world_to_screen(dynamic_range*0.5, 0, i)
                if p1 and p2:
                    grid_lines.append((*p1, *p2, color))
                
            # 线平行Z轴（沿X变化）
            p3 = world_to_screen(i, 0, -dynamic_range)
            p4 = world_to_screen(i, 0, dynamic_range)
            # 只要有一个点能投影就绘制线段
            if p3 or p4:
                if not p3:
                    p3 = world_to_screen(i, 0, -dynamic_range*0.5)
                if not p4:
                    p4 = world_to_screen(i, 0, dynamic_range*0.5)
                if p3 and p4:
                    grid_lines.append((*p3, *p4, color))
        
        # 绘制网格线
        for x1, y1, x2, y2, color in grid_lines:
            c.create_line(x1, y1, x2, y2, fill=color)

        # 坐标轴（使用固定长度，确保在任何放大级别下都能正常显示）
        x0 = world_to_screen(0, 0, 0)
        # 使用适中的轴长度，既能看清方向又不会超出投影范围
        axis_length = min(10, self.distance)  # 轴长度与视距相关，但有上限
        
        # X轴（红色）- 只向正方向延伸
        x_pos = world_to_screen(axis_length, 0, 0)
        if x0 and x_pos:
            c.create_line(*x0, *x_pos, fill=self.axis_x_color, width=3)
        elif x0:  # 如果终点投影失败，使用更短的轴
            for length in [axis_length*0.5, axis_length*0.25, 1.0]:
                x_fallback = world_to_screen(length, 0, 0)
                if x_fallback:
                    c.create_line(*x0, *x_fallback, fill=self.axis_x_color, width=3)
                    break
            
        # Y轴（绿色）- 只向正方向延伸
        y_pos = world_to_screen(0, axis_length, 0)
        if x0 and y_pos:
            c.create_line(*x0, *y_pos, fill=self.axis_y_color, width=3)
        elif x0:  # 如果终点投影失败，使用更短的轴
            for length in [axis_length*0.5, axis_length*0.25, 1.0]:
                y_fallback = world_to_screen(0, length, 0)
                if y_fallback:
                    c.create_line(*x0, *y_fallback, fill=self.axis_y_color, width=3)
                    break
            
        # Z轴（蓝色）- 只向正方向延伸
        z_pos = world_to_screen(0, 0, axis_length)
        if x0 and z_pos:
            c.create_line(*x0, *z_pos, fill=self.axis_z_color, width=3)
        elif x0:  # 如果终点投影失败，使用更短的轴
            for length in [axis_length*0.5, axis_length*0.25, 1.0]:
                z_fallback = world_to_screen(0, 0, length)
                if z_fallback:
                    c.create_line(*x0, *z_fallback, fill=self.axis_z_color, width=3)
                    break
        
        # 绘制坐标轴标签（如果原点可见）
        if x0:
            # X轴标签（红色）
            x_label_pos = world_to_screen(axis_length * 0.8, 0.3, 0)
            if x_label_pos:
                c.create_text(x_label_pos[0], x_label_pos[1], text="X", fill=self.axis_x_color, 
                             font=("Arial", 12, "bold"))
            
            # Y轴标签（绿色）
            y_label_pos = world_to_screen(0.3, axis_length * 0.8, 0)
            if y_label_pos:
                c.create_text(y_label_pos[0], y_label_pos[1], text="Y", fill=self.axis_y_color, 
                             font=("Arial", 12, "bold"))
            
            # Z轴标签（蓝色）
            z_label_pos = world_to_screen(0, 0.3, axis_length * 0.8)
            if z_label_pos:
                c.create_text(z_label_pos[0], z_label_pos[1], text="Z", fill=self.axis_z_color, 
                             font=("Arial", 12, "bold"))
        
        # 绘制3D图形
        self.draw_3d_shapes(world_to_screen)
        
        # 绘制选中图形的操作控件
        if self.selected_shape and self.show_gizmos:
            self.draw_gizmos(world_to_screen)
    
    def draw_3d_shapes(self, world_to_screen):
        """绘制3D图形（实体模式）"""
        # 收集所有面信息用于深度排序
        all_faces = []
        
        for shape in self.shapes_3d:
            if not shape.visible:
                continue
            
            # 获取图形的顶点和面
            vertices = shape.get_vertices()
            faces = shape.get_faces() if hasattr(shape, 'get_faces') else []
            
            # 将3D顶点投影到屏幕坐标
            screen_vertices = []
            world_vertices = []
            for vertex in vertices:
                screen_pos = world_to_screen(vertex[0], vertex[1], vertex[2])
                screen_vertices.append(screen_pos)
                world_vertices.append(vertex)
            
            # 收集所有面及其深度信息
            for face in faces:
                if len(face) >= 3:  # 至少需要3个顶点组成面
                    # 计算面的平均Z深度（在世界坐标系中）
                    total_z = 0
                    valid_vertices = 0
                    face_screen_coords = []
                    face_world_coords = []
                    
                    for vertex_idx in face:
                        if vertex_idx < len(world_vertices) and vertex_idx < len(screen_vertices):
                            world_vertex = world_vertices[vertex_idx]
                            screen_vertex = screen_vertices[vertex_idx]
                            if screen_vertex:
                                total_z += world_vertex[2]  # 使用世界坐标的Z值
                                valid_vertices += 1
                                face_screen_coords.append(screen_vertex)
                                face_world_coords.append(world_vertex)
                    
                    if valid_vertices >= 3:  # 面有足够的有效顶点
                        # 使用外积进行背面剔除
                        if self._is_face_front_facing(face_world_coords):
                            avg_z = total_z / valid_vertices
                            face_info = {
                                'shape': shape,
                                'face_coords': face_screen_coords,
                                'depth': avg_z,
                                'face_indices': face
                            }
                            all_faces.append(face_info)
        
        # 按深度排序（远的先画）
        all_faces.sort(key=lambda x: x['depth'], reverse=True)
        
        # 绘制所有面
        for face_info in all_faces:
            self._draw_face(face_info)
    
    def _is_face_front_facing(self, face_world_coords):
        """使用外积判断面是否朝向观察者（背面剔除）"""
        if len(face_world_coords) < 3:
            return True  # 不足3个点，默认渲染
        
        try:
            # 获取面的前三个顶点
            v1 = face_world_coords[0]
            v2 = face_world_coords[1] 
            v3 = face_world_coords[2]
            
            # 计算两个边向量
            edge1 = (v2[0] - v1[0], v2[1] - v1[1], v2[2] - v1[2])
            edge2 = (v3[0] - v1[0], v3[1] - v1[1], v3[2] - v1[2])
            
            # 计算法向量（外积）
            normal = (
                edge1[1] * edge2[2] - edge1[2] * edge2[1],  # nx
                edge1[2] * edge2[0] - edge1[0] * edge2[2],  # ny  
                edge1[0] * edge2[1] - edge1[1] * edge2[0]   # nz
            )
            
            # 计算相机位置
            camera_pos = self._get_camera_position()
            
            # 计算从面中心到相机的向量
            face_center = (
                (v1[0] + v2[0] + v3[0]) / 3,
                (v1[1] + v2[1] + v3[1]) / 3,
                (v1[2] + v2[2] + v3[2]) / 3
            )
            
            view_vector = (
                camera_pos[0] - face_center[0],
                camera_pos[1] - face_center[1], 
                camera_pos[2] - face_center[2]
            )
            
            # 计算法向量与视线向量的点积
            dot_product = (normal[0] * view_vector[0] + 
                          normal[1] * view_vector[1] + 
                          normal[2] * view_vector[2])
            
            # 如果点积为负，说明面朝向观察者（修复反向问题）
            return dot_product < 0
            
        except (IndexError, ZeroDivisionError):
            return True  # 出错时默认渲染
    
    def _get_camera_position(self):
        """获取相机在世界坐标系中的位置"""
        # 将球坐标转换为笛卡尔坐标
        yaw_rad = math.radians(self.yaw)
        pitch_rad = math.radians(self.pitch)
        
        x = self.target[0] + self.distance * math.cos(pitch_rad) * math.cos(yaw_rad)
        y = self.target[1] + self.distance * math.sin(pitch_rad)
        z = self.target[2] + self.distance * math.cos(pitch_rad) * math.sin(yaw_rad)
        
        return (x, y, z)
    
    def _draw_face(self, face_info):
        """绘制单个面"""
        shape = face_info['shape']
        face_coords = face_info['face_coords']
        
        if len(face_coords) < 3:
            return
        
        # 计算面的法向量来确定明暗（简单光照）
        brightness = self._calculate_face_brightness(face_info['face_indices'], shape)
        
        # 根据选中状态和形状属性确定颜色
        if shape.selected:
            # 选中时为黄色
            fill_color = "#ffff00"
            outline_color = "#ff8800"  # 橙色边框表示选中
        else:
            # 使用形状的填充颜色，如果没有则使用线条颜色
            if hasattr(shape, 'fill_color') and shape.fill_color:
                fill_color = shape.fill_color
            else:
                fill_color = shape.color
            # 线条颜色
            outline_color = shape.color if hasattr(shape, 'color') else "#333333"
        
        # 应用明暗效果到填充色
        face_color = self._apply_brightness(fill_color, brightness)
        
        # 创建多边形坐标列表
        coords = []
        for coord in face_coords:
            coords.extend([coord[0], coord[1]])
        
        # 绘制填充的多边形
        if len(coords) >= 6:  # 至少3个点，每个点2个坐标
            # 获取线宽
            line_width = shape.line_width if hasattr(shape, 'line_width') else 1
            
            self.canvas.create_polygon(
                coords,
                fill=face_color,
                outline=outline_color,  # 使用形状的颜色作为边框
                width=line_width
            )
    
    def _calculate_face_brightness(self, face_indices, shape):
        """计算面的亮度（简单的光照模拟）"""
        if len(face_indices) < 3:
            return 0.7
        
        try:
            vertices = shape.get_vertices()
            # 获取面的前三个顶点
            v1 = vertices[face_indices[0]]
            v2 = vertices[face_indices[1]]
            v3 = vertices[face_indices[2]]
            
            # 计算法向量
            edge1 = (v2[0] - v1[0], v2[1] - v1[1], v2[2] - v1[2])
            edge2 = (v3[0] - v1[0], v3[1] - v1[1], v3[2] - v1[2])
            
            # 叉积得到法向量（调整顺序以匹配背面剔除逻辑）
            normal = (
                edge1[1] * edge2[2] - edge1[2] * edge2[1],
                edge1[2] * edge2[0] - edge1[0] * edge2[2],
                edge1[0] * edge2[1] - edge1[1] * edge2[0]
            )
            
            # 归一化法向量
            length = (normal[0]**2 + normal[1]**2 + normal[2]**2)**0.5
            if length > 0:
                normal = (normal[0]/length, normal[1]/length, normal[2]/length)
            
            # 简单的定向光源（从右上方照射）
            light_direction = (0.5, 0.7, 0.5)
            
            # 计算光照强度（点积）- 反转以匹配新的面朝向
            dot_product = normal[0]*light_direction[0] + normal[1]*light_direction[1] + normal[2]*light_direction[2]
            
            # 将亮度限制在0.3到1.0之间（反转亮度映射）
            brightness = max(0.3, min(1.0, (-dot_product + 1) / 2))
            return brightness
            
        except (IndexError, ZeroDivisionError):
            return 0.7  # 默认亮度
    
    def _apply_brightness(self, color_hex, brightness):
        """将亮度应用到颜色上"""
        try:
            # 移除#号
            if color_hex.startswith('#'):
                color_hex = color_hex[1:]
            
            # 转换为RGB
            r = int(color_hex[0:2], 16)
            g = int(color_hex[2:4], 16)
            b = int(color_hex[4:6], 16)
            
            # 应用亮度
            r = int(r * brightness)
            g = int(g * brightness)
            b = int(b * brightness)
            
            # 确保值在0-255范围内
            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))
            
            # 转换回十六进制
            return f"#{r:02x}{g:02x}{b:02x}"
            
        except (ValueError, IndexError):
            return color_hex  # 如果转换失败，返回原色
    
    def draw_gizmos(self, world_to_screen):
        """绘制选中图形的操作控件（根据当前变换模式显示不同的gizmo）"""
        if not self.selected_shape:
            return
        
        center = self.selected_shape.get_center()
        center_screen = world_to_screen(center[0], center[1], center[2])
        
        if not center_screen:
            return
        
        cx, cy = center_screen
        
        if self.transform_mode == "move":
            self._draw_move_gizmo(world_to_screen, center, cx, cy)
        elif self.transform_mode == "scale":
            self._draw_scale_gizmo(world_to_screen, center, cx, cy)
        elif self.transform_mode == "rotate":
            self._draw_rotate_gizmo(world_to_screen, center, cx, cy)
    
    def _draw_move_gizmo(self, world_to_screen, center, cx, cy):
        """绘制移动模式的三轴移动箭头"""
        # X轴（红色）
        x_end = world_to_screen(center[0] + 2, center[1], center[2])
        if x_end:
            self.canvas.create_line(cx, cy, x_end[0], x_end[1], 
                                  fill="#ff0000", width=3, tags="gizmo_x")
            # 箭头头部
            self.canvas.create_polygon(x_end[0], x_end[1],
                                     x_end[0]-8, x_end[1]-4,
                                     x_end[0]-8, x_end[1]+4,
                                     fill="#ff0000", tags="gizmo_x")
        
        # Y轴（绿色）
        y_end = world_to_screen(center[0], center[1] + 2, center[2])
        if y_end:
            self.canvas.create_line(cx, cy, y_end[0], y_end[1],
                                  fill="#00ff00", width=3, tags="gizmo_y")
            # 箭头头部
            self.canvas.create_polygon(y_end[0], y_end[1],
                                     y_end[0]-4, y_end[1]-8,
                                     y_end[0]+4, y_end[1]-8,
                                     fill="#00ff00", tags="gizmo_y")
        
        # Z轴（蓝色）
        z_end = world_to_screen(center[0], center[1], center[2] + 2)
        if z_end:
            self.canvas.create_line(cx, cy, z_end[0], z_end[1],
                                  fill="#0000ff", width=3, tags="gizmo_z")
            # 箭头头部
            self.canvas.create_polygon(z_end[0], z_end[1],
                                     z_end[0]-4, z_end[1]-8,
                                     z_end[0]+4, z_end[1]+8,
                                     fill="#0000ff", tags="gizmo_z")
    
    def _draw_scale_gizmo(self, world_to_screen, center, cx, cy):
        """绘制缩放模式的控制器"""
        if isinstance(self.selected_shape, Vector3D):
            # 向量的特殊缩放控制：只沿向量方向
            self._draw_vector_scale_gizmo(world_to_screen, center, cx, cy)
        else:
            # 其他图形的标准三轴缩放控制
            self._draw_standard_scale_gizmo(world_to_screen, center, cx, cy)
    
    def _draw_vector_scale_gizmo(self, world_to_screen, center, cx, cy):
        """绘制向量的单轴缩放控制器"""
        vector = self.selected_shape
        # 获取向量的归一化方向
        dir_x, dir_y, dir_z = vector._normalize_direction()
        
        # 计算向量方向上的控制点
        scale_length = vector.length * 0.8  # 缩放控制器长度
        
        # 向量正方向的控制点
        pos_x = center[0] + dir_x * scale_length
        pos_y = center[1] + dir_y * scale_length
        pos_z = center[2] + dir_z * scale_length
        pos_screen = world_to_screen(pos_x, pos_y, pos_z)
        
        # 向量负方向的控制点（从起点）
        neg_x = center[0] - dir_x * 0.3
        neg_y = center[1] - dir_y * 0.3
        neg_z = center[2] - dir_z * 0.3
        neg_screen = world_to_screen(neg_x, neg_y, neg_z)
        
        if pos_screen and neg_screen:
            # 绘制向量方向的缩放线
            self.canvas.create_line(neg_screen[0], neg_screen[1], pos_screen[0], pos_screen[1],
                                  fill="#ffaa00", width=4, tags="gizmo_vector")
            
            # 正方向控制点（拉长）
            self.canvas.create_oval(pos_screen[0]-8, pos_screen[1]-8,
                                  pos_screen[0]+8, pos_screen[1]+8,
                                  fill="#ff6600", outline="#ff0000", width=2, tags="gizmo_vector")
            
            # 负方向控制点（缩短）
            self.canvas.create_oval(neg_screen[0]-6, neg_screen[1]-6,
                                  neg_screen[0]+6, neg_screen[1]+6,
                                  fill="#6600ff", outline="#0000ff", width=2, tags="gizmo_vector")
    
    def _draw_standard_scale_gizmo(self, world_to_screen, center, cx, cy):
        """绘制标准的三轴缩放控制器"""
        # 计算图形的大小来调整箭头长度
        shape_size = self._get_shape_size()
        arrow_length = max(1.5, min(3.0, shape_size * 0.5))  # 根据形状大小调整
        
        # X轴缩放控制（红色双向箭头）
        x_pos = world_to_screen(center[0] + arrow_length, center[1], center[2])
        x_neg = world_to_screen(center[0] - arrow_length, center[1], center[2])
        if x_pos and x_neg:
            self.canvas.create_line(x_neg[0], x_neg[1], x_pos[0], x_pos[1],
                                  fill="#ff0000", width=3, tags="gizmo_x")
            # 双向箭头头部
            self.canvas.create_polygon(x_pos[0], x_pos[1],
                                     x_pos[0]-8, x_pos[1]-4,
                                     x_pos[0]-8, x_pos[1]+4,
                                     fill="#ff0000", tags="gizmo_x")
            self.canvas.create_polygon(x_neg[0], x_neg[1],
                                     x_neg[0]+8, x_neg[1]-4,
                                     x_neg[0]+8, x_neg[1]+4,
                                     fill="#ff0000", tags="gizmo_x")
        
        # Y轴缩放控制（绿色双向箭头）
        y_pos = world_to_screen(center[0], center[1] + arrow_length, center[2])
        y_neg = world_to_screen(center[0], center[1] - arrow_length, center[2])
        if y_pos and y_neg:
            self.canvas.create_line(y_neg[0], y_neg[1], y_pos[0], y_pos[1],
                                  fill="#00ff00", width=3, tags="gizmo_y")
            # 双向箭头头部
            self.canvas.create_polygon(y_pos[0], y_pos[1],
                                     y_pos[0]-4, y_pos[1]-8,
                                     y_pos[0]+4, y_pos[1]-8,
                                     fill="#00ff00", tags="gizmo_y")
            self.canvas.create_polygon(y_neg[0], y_neg[1],
                                     y_neg[0]-4, y_neg[1]+8,
                                     y_neg[0]+4, y_neg[1]+8,
                                     fill="#00ff00", tags="gizmo_y")
        
        # Z轴缩放控制（蓝色双向箭头）
        z_pos = world_to_screen(center[0], center[1], center[2] + arrow_length)
        z_neg = world_to_screen(center[0], center[1], center[2] - arrow_length)
        if z_pos and z_neg:
            self.canvas.create_line(z_neg[0], z_neg[1], z_pos[0], z_pos[1],
                                  fill="#0000ff", width=3, tags="gizmo_z")
            # 双向箭头头部
            self.canvas.create_polygon(z_pos[0], z_pos[1],
                                     z_pos[0]-4, z_pos[1]-8,
                                     z_pos[0]+4, z_pos[1]+8,
                                     fill="#0000ff", tags="gizmo_z")
            self.canvas.create_polygon(z_neg[0], z_neg[1],
                                     z_neg[0]-4, z_neg[1]+8,
                                     z_neg[0]+4, z_neg[1]-8,
                                     fill="#0000ff", tags="gizmo_z")
        z_pos = world_to_screen(center[0], center[1], center[2] + arrow_length)
        z_neg = world_to_screen(center[0], center[1], center[2] - arrow_length)
        if z_pos and z_neg:
            self.canvas.create_line(z_neg[0], z_neg[1], z_pos[0], z_pos[1],
                                  fill="#0000ff", width=3, tags="gizmo_z")
            # 双向箭头头部
            self.canvas.create_polygon(z_pos[0], z_pos[1],
                                     z_pos[0]-4, z_pos[1]-8,
                                     z_pos[0]+4, z_pos[1]+8,
                                     fill="#0000ff", tags="gizmo_z")
            self.canvas.create_polygon(z_neg[0], z_neg[1],
                                     z_neg[0]-4, z_neg[1]+8,
                                     z_neg[0]+4, z_neg[1]-8,
                                     fill="#0000ff", tags="gizmo_z")
    
    def _draw_rotate_gizmo(self, world_to_screen, center, cx, cy):
        """绘制旋转模式的三个旋转环（真正的3D环形，固定在世界坐标系）"""
        # 使用固定大小的旋转环半径
        base_radius = 2.5  # 固定3D空间中的半径
        
        # 绘制旋转环，使用更粗的线条
        ring_width = 6  # 基础线条宽度
        
        # 生成3D圆环的顶点（每个环32个点）
        import math
        num_points = 32
        
        # X轴旋转环（红色）- 在YZ平面的圆环（垂直于世界X轴）
        x_width = ring_width + (3 if self.hover_gizmo_axis == "x" else 0)
        x_color = "#ff6666" if self.hover_gizmo_axis == "x" else "#ff0000"
        x_points = []
        for i in range(num_points):
            angle = 2 * math.pi * i / num_points
            # 在YZ平面生成圆环点（固定在世界坐标系）
            y = center[1] + base_radius * math.cos(angle)
            z = center[2] + base_radius * math.sin(angle)
            point_3d = (center[0], y, z)
            point_2d = world_to_screen(point_3d[0], point_3d[1], point_3d[2])
            if point_2d:
                x_points.append(point_2d)
        
        # 绘制X轴环
        if len(x_points) > 1:
            # 创建多个线段形成圆环
            for i in range(len(x_points)):
                next_i = (i + 1) % len(x_points)
                self.canvas.create_line(
                    x_points[i][0], x_points[i][1],
                    x_points[next_i][0], x_points[next_i][1],
                    fill=x_color, width=x_width, tags="gizmo_x"
                )
            # 添加不可见的可点击区域
            for point in x_points:
                self.canvas.create_oval(
                    point[0]-15, point[1]-15, point[0]+15, point[1]+15,
                    fill="", outline="", width=0, tags="gizmo_x"
                )
            # 添加X轴标签
            label_pos = world_to_screen(center[0], center[1], center[2] + base_radius * 1.2)
            if label_pos:
                self.canvas.create_text(label_pos[0], label_pos[1], text="X", 
                                      fill=x_color, font=("Arial", 10, "bold"), tags="gizmo_x")
        
        # Y轴旋转环（绿色）- 在XZ平面的圆环（垂直于世界Y轴）
        y_width = ring_width + (3 if self.hover_gizmo_axis == "y" else 0)
        y_color = "#66ff66" if self.hover_gizmo_axis == "y" else "#00ff00"
        y_points = []
        for i in range(num_points):
            angle = 2 * math.pi * i / num_points
            # 在XZ平面生成圆环点（固定在世界坐标系）
            x = center[0] + base_radius * math.cos(angle)
            z = center[2] + base_radius * math.sin(angle)
            point_3d = (x, center[1], z)
            point_2d = world_to_screen(point_3d[0], point_3d[1], point_3d[2])
            if point_2d:
                y_points.append(point_2d)
        
        # 绘制Y轴环
        if len(y_points) > 1:
            for i in range(len(y_points)):
                next_i = (i + 1) % len(y_points)
                self.canvas.create_line(
                    y_points[i][0], y_points[i][1],
                    y_points[next_i][0], y_points[next_i][1],
                    fill=y_color, width=y_width, tags="gizmo_y"
                )
            # 添加不可见的可点击区域
            for point in y_points:
                self.canvas.create_oval(
                    point[0]-15, point[1]-15, point[0]+15, point[1]+15,
                    fill="", outline="", width=0, tags="gizmo_y"
                )
            # 添加Y轴标签
            label_pos = world_to_screen(center[0] + base_radius * 1.2, center[1], center[2])
            if label_pos:
                self.canvas.create_text(label_pos[0], label_pos[1], text="Y", 
                                      fill=y_color, font=("Arial", 10, "bold"), tags="gizmo_y")
        
        # Z轴旋转环（蓝色）- 在XY平面的圆环（垂直于世界Z轴）
        z_width = ring_width + (3 if self.hover_gizmo_axis == "z" else 0)
        z_color = "#6666ff" if self.hover_gizmo_axis == "z" else "#0000ff"
        z_points = []
        for i in range(num_points):
            angle = 2 * math.pi * i / num_points
            # 在XY平面生成圆环点（固定在世界坐标系）
            x = center[0] + base_radius * math.cos(angle)
            y = center[1] + base_radius * math.sin(angle)
            point_3d = (x, y, center[2])
            point_2d = world_to_screen(point_3d[0], point_3d[1], point_3d[2])
            if point_2d:
                z_points.append(point_2d)
        
        # 绘制Z轴环
        if len(z_points) > 1:
            for i in range(len(z_points)):
                next_i = (i + 1) % len(z_points)
                self.canvas.create_line(
                    z_points[i][0], z_points[i][1],
                    z_points[next_i][0], z_points[next_i][1],
                    fill=z_color, width=z_width, tags="gizmo_z"
                )
            # 添加不可见的可点击区域
            for point in z_points:
                self.canvas.create_oval(
                    point[0]-15, point[1]-15, point[0]+15, point[1]+15,
                    fill="", outline="", width=0, tags="gizmo_z"
                )
            # 添加Z轴标签
            label_pos = world_to_screen(center[0], center[1] + base_radius * 1.2, center[2])
            if label_pos:
                self.canvas.create_text(label_pos[0], label_pos[1], text="Z", 
                                      fill=z_color, font=("Arial", 10, "bold"), tags="gizmo_z")
    
    def _get_shape_size(self):
        """获取当前选中形状的大小（用于调整gizmo尺寸）"""
        if not self.selected_shape:
            return 2.0
        
        vertices = self.selected_shape.get_vertices()
        if not vertices:
            return 2.0
        
        # 计算边界框大小
        min_x = min(v[0] for v in vertices)
        max_x = max(v[0] for v in vertices)
        min_y = min(v[1] for v in vertices)
        max_y = max(v[1] for v in vertices)
        min_z = min(v[2] for v in vertices)
        max_z = max(v[2] for v in vertices)
        
        # 返回边界框的平均尺寸
        return (max_x - min_x + max_y - min_y + max_z - min_z) / 3.0
    
    # 3D图形管理方法
    def add_shape(self, shape: BaseShape3D):
        """添加3D图形"""
        self.shapes_3d.append(shape)
        self.has_content = True
        self.redraw()
    
    def remove_shape(self, shape: BaseShape3D):
        """移除3D图形"""
        if shape in self.shapes_3d:
            self.shapes_3d.remove(shape)
            if shape == self.selected_shape:
                self.selected_shape = None
            self.has_content = len(self.shapes_3d) > 0
            self.redraw()
    
    def select_shape(self, shape: BaseShape3D):
        """选择3D图形"""
        self._select_shape_internal(shape)
        
        # 调用选择回调
        if self.selection_callback:
            self.selection_callback(shape)
    
    def _select_shape_internal(self, shape: BaseShape3D):
        """内部选择方法，不触发回调"""
        # 取消之前的选择
        if self.selected_shape:
            self.selected_shape.selected = False
        
        # 选择新图形
        self.selected_shape = shape
        if shape:
            shape.selected = True
            
            # 检查当前变换模式是否适用于新选中的图形
            allowed_modes = self._get_allowed_transform_modes(shape)
            if self.transform_mode not in allowed_modes:
                # 自动切换到允许的第一个模式
                self.transform_mode = allowed_modes[0]
                
        self.redraw()
    
    def set_selection_callback(self, callback):
        """设置选择改变时的回调函数"""
        self.selection_callback = callback
    
    def get_selected_shape(self):
        """获取当前选中的图形"""
        return self.selected_shape
    
    def _pick_shape(self, screen_x, screen_y):
        """根据屏幕坐标选择3D图形"""
        # 计算投影函数
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w <= 1 or h <= 1:
            return None
            
        # 计算相机位置
        rad_yaw = math.radians(self.yaw)
        rad_pitch = math.radians(self.pitch)
        cx = self.target[0] + self.distance * math.cos(rad_pitch) * math.cos(rad_yaw)
        cy = self.target[1] + self.distance * math.sin(rad_pitch)
        cz = self.target[2] + self.distance * math.cos(rad_pitch) * math.sin(rad_yaw)
        
        fov = math.radians(60.0)
        f = 1.0 / math.tan(fov / 2.0)
        scale = (h / 2.0) * f
        
        def world_to_screen(px, py, pz):
            # 简化的投影计算
            tx, ty, tz = self.target
            zx, zy, zz = (tx - cx, ty - cy, tz - cz)
            zlen = math.sqrt(zx*zx + zy*zy + zz*zz) or 1.0
            zx, zy, zz = zx / zlen, zy / zlen, zz / zlen
            
            upx, upy, upz = 0.0, 1.0, 0.0
            xx = upy * zz - upz * zy
            xy = upz * zx - upx * zz
            xz = upx * zy - upy * zx
            xlen = math.sqrt(xx*xx + xy*xy + xz*xz) or 1.0
            xx, xy, xz = xx / xlen, xy / xlen, xz / xlen
            
            yx = zy * xz - zz * xy
            yy = zz * xx - zx * xz
            yz = zx * xy - zy * xx
            
            dx, dy, dz = px - cx, py - cy, pz - cz
            rx = dx * xx + dy * xy + dz * xz
            ry = dx * yx + dy * yy + dz * yz
            rz = dx * zx + dy * zy + dz * zz
            if rz <= 0.1:
                return None
            sx = w/2.0 + (rx * scale) / rz
            sy = h/2.0 - (ry * scale) / rz
            return (sx, sy)
        
        # 检查每个图形的中心点是否在点击范围内
        pick_radius = 20  # 选择半径
        closest_shape = None
        closest_dist = float('inf')
        
        for shape in self.shapes_3d:
            if not shape.visible:
                continue
                
            center = shape.get_center()
            screen_pos = world_to_screen(center[0], center[1], center[2])
            
            if screen_pos:
                dist = math.sqrt((screen_pos[0] - screen_x)**2 + (screen_pos[1] - screen_y)**2)
                if dist < pick_radius and dist < closest_dist:
                    closest_dist = dist
                    closest_shape = shape
        
        return closest_shape
    
    def _check_gizmo_click(self, screen_x, screen_y):
        """检查是否点击了gizmo控件"""
        if not self.selected_shape:
            return None
            
        # 根据变换模式调整检测敏感度
        if self.transform_mode == "rotate":
            # 旋转模式下使用更大的检测范围，因为现在是3D环形
            detect_range = 20
        else:
            # 移动和缩放模式使用标准检测范围
            detect_range = 8
            
        # 检查canvas上的标签
        items = self.canvas.find_overlapping(screen_x - detect_range, screen_y - detect_range, 
                                           screen_x + detect_range, screen_y + detect_range)
        
        # 优先级：优先检测更精确的轴
        axes_found = []
        for item in items:
            tags = self.canvas.gettags(item)
            if "gizmo_vector" in tags:
                return "vector"  # 向量的特殊缩放控制
            elif "gizmo_x" in tags:
                axes_found.append("x")
            elif "gizmo_y" in tags:
                axes_found.append("y")
            elif "gizmo_z" in tags:
                axes_found.append("z")
        
        # 如果找到多个轴，返回第一个（通常是最上层的）
        if axes_found:
            return axes_found[0]
        
        return None
    
    def _drag_gizmo(self, dx, dy):
        """拖动gizmo轴进行变换操作（根据当前模式执行不同操作）"""
        if not self.selected_shape or not self.drag_gizmo_axis:
            return
        
        if self.transform_mode == "move":
            self._drag_gizmo_move(dx, dy)
        elif self.transform_mode == "scale":
            self._drag_gizmo_scale(dx, dy)
        elif self.transform_mode == "rotate":
            self._drag_gizmo_rotate(dx, dy)
    
    def _drag_gizmo_move(self, dx, dy):
        """移动模式：单轴移动"""
        move_factor = 0.05  # 调整移动敏感度，使操作更精确
        
        if self.drag_gizmo_axis == "x":
            # X轴（红色）：左右拖动，右拖动 = 正X方向移动
            offset = (-dx * move_factor, 0, 0)  # 反转X轴方向
        elif self.drag_gizmo_axis == "y":
            # Y轴（绿色）：上下拖动，上拖动 = 正Y方向移动
            offset = (0, -dy * move_factor, 0)  # 使用-dy，因为屏幕坐标向下为正，世界坐标向上为正
        elif self.drag_gizmo_axis == "z":
            # Z轴（蓝色）：上下拖动，上拖动 = 正Z方向移动
            offset = (0, 0, dy * move_factor)  # 反转Z轴方向
        else:
            return
            
        self.selected_shape.translate(offset[0], offset[1], offset[2])
        self.redraw()
    
    def _drag_gizmo_scale(self, dx, dy):
        """缩放模式：根据图形类型进行不同的缩放操作"""
        if isinstance(self.selected_shape, Vector3D) and self.drag_gizmo_axis == "vector":
            # 向量的特殊缩放：只调整长度，不改变起点位置
            self._drag_vector_scale(dx, dy)
        else:
            # 标准的轴向缩放
            self._drag_standard_scale(dx, dy)
    
    def _drag_vector_scale(self, dx, dy):
        """向量的长度缩放（保持起点不变）"""
        vector = self.selected_shape
        
        # 计算缩放因子（向右或向上拖动增加长度）
        scale_delta = (dx - dy) * 0.02  # 使用dx-dy，向右向上为正
        new_length = vector.length + scale_delta
        new_length = max(0.2, min(10.0, new_length))  # 限制长度范围
        
        # 直接设置新长度
        vector.set_length(new_length)
        self.redraw()
    
    def _drag_standard_scale(self, dx, dy):
        """标准的轴向缩放"""
        scale_delta = 0.005  # 调整敏感度
        
        # 根据拖动的轴进行单轴缩放，修正方向
        if self.drag_gizmo_axis == "x":
            # X轴（红色）：左右拖动，右拖动放大
            scale_factor = 1.0 + (-dx * scale_delta)  # 反转X轴方向
            scale_vector = (scale_factor, 1.0, 1.0)
        elif self.drag_gizmo_axis == "y":
            # Y轴（绿色）：上下拖动，上拖动放大
            scale_factor = 1.0 + (-dy * scale_delta)  # 使用-dy
            scale_vector = (1.0, scale_factor, 1.0)
        elif self.drag_gizmo_axis == "z":
            # Z轴（蓝色）：上下拖动，上拖动放大
            scale_factor = 1.0 + (dy * scale_delta)  # 反转Z轴方向
            scale_vector = (1.0, 1.0, scale_factor)
        else:
            return
        
        scale_factor = max(0.1, min(3.0, scale_factor))  # 限制缩放范围
        
        # 获取中心点进行缩放
        center = self.selected_shape.get_center()
        self._scale_shape_around_center(scale_vector, center)
        self.redraw()
    
    def _drag_gizmo_rotate(self, dx, dy):
        """旋转模式：单轴旋转"""
        rotation_speed = 1.0  # 降低旋转敏感度，使操作更精确
        
        if self.drag_gizmo_axis == "x":
            # 绕X轴旋转：上下拖动，向上为负角度（右手定则）
            angle = -dy * rotation_speed
            self._rotate_shape_around_axis("x", angle)
        elif self.drag_gizmo_axis == "y":
            # 绕Y轴旋转：左右拖动，向右为正角度
            angle = dx * rotation_speed
            self._rotate_shape_around_axis("y", angle)
        elif self.drag_gizmo_axis == "z":
            # 绕Z轴旋转：左右拖动，向右为正角度
            angle = dx * rotation_speed
            self._rotate_shape_around_axis("z", angle)
        
        self.redraw()
    
    def _drag_shape(self, dx, dy):
        """拖动图形进行操作（根据当前模式执行不同操作）"""
        if not self.selected_shape:
            return
        
        if self.transform_mode == "move":
            self._drag_shape_move(dx, dy)
        elif self.transform_mode == "scale":
            self._drag_shape_scale(dx, dy)
        elif self.transform_mode == "rotate":
            self._drag_shape_rotate(dx, dy)
    
    def _drag_shape_move(self, dx, dy):
        """移动模式：自由移动"""
        move_factor = 0.03  # 调整移动敏感度
        
        # 计算相机的右向量和上向量
        rad_yaw = math.radians(self.yaw)
        rad_pitch = math.radians(self.pitch)
        
        # 右向量（X方向）
        right_x = -math.sin(rad_yaw)
        right_z = math.cos(rad_yaw)
        
        # 上向量投影到水平面
        up_x = -math.cos(rad_yaw) * math.sin(rad_pitch)
        up_y = math.cos(rad_pitch)
        up_z = -math.sin(rad_yaw) * math.sin(rad_pitch)
        
        # 计算移动偏移（调整Y轴方向）
        offset_x = (dx * right_x - dy * up_x) * move_factor  # 注意dy变为负
        offset_y = -dy * up_y * move_factor  # Y轴向上为正
        offset_z = (dx * right_z - dy * up_z) * move_factor  # 注意dy变为负
        
        self.selected_shape.translate(offset_x, offset_y, offset_z)
        self.redraw()
    
    def _drag_shape_scale(self, dx, dy):
        """缩放模式：均匀缩放"""
        # 向右向上拖动增大，向左向下拖动减小
        scale_delta = (dx - dy) * 0.005  # 使用dx-dy，调整敏感度
        scale_factor = 1.0 + scale_delta
        scale_factor = max(0.1, min(3.0, scale_factor))
        
        center = self.selected_shape.get_center()
        self._scale_shape_around_center((scale_factor, scale_factor, scale_factor), center)
        self.redraw()
    
    def _drag_shape_rotate(self, dx, dy):
        """旋转模式：基于视角的旋转"""
        rotation_speed = 0.5  # 降低旋转敏感度
        
        # 基于鼠标移动进行多轴旋转
        if abs(dx) > abs(dy):
            # 主要是水平移动，绕Y轴旋转
            self._rotate_shape_around_axis("y", dx * rotation_speed)
        else:
            # 主要是垂直移动，绕X轴旋转
            self._rotate_shape_around_axis("x", -dy * rotation_speed)  # 注意负号
        
        self.redraw()
    
    def _scale_shape_around_center(self, scale_vector, center):
        """围绕中心点缩放图形"""
        # 将图形移动到原点
        self.selected_shape.translate(-center[0], -center[1], -center[2])
        
        # 应用缩放变换（使用纯Python实现）
        scale_matrix = [
            [scale_vector[0], 0, 0, 0],
            [0, scale_vector[1], 0, 0],
            [0, 0, scale_vector[2], 0],
            [0, 0, 0, 1]
        ]
        self.selected_shape.apply_transform(scale_matrix)
        
        # 移回原位置
        self.selected_shape.translate(center[0], center[1], center[2])
    
    def _rotate_shape_around_axis(self, axis, angle_degrees):
        """围绕指定轴旋转图形"""
        center = self.selected_shape.get_center()
        angle_rad = math.radians(angle_degrees)
        
        # 将图形移动到原点
        self.selected_shape.translate(-center[0], -center[1], -center[2])
        
        # 创建旋转矩阵（使用纯Python实现）
        if axis == "x":
            rotation_matrix = [
                [1, 0, 0, 0],
                [0, math.cos(angle_rad), -math.sin(angle_rad), 0],
                [0, math.sin(angle_rad), math.cos(angle_rad), 0],
                [0, 0, 0, 1]
            ]
        elif axis == "y":
            rotation_matrix = [
                [math.cos(angle_rad), 0, math.sin(angle_rad), 0],
                [0, 1, 0, 0],
                [-math.sin(angle_rad), 0, math.cos(angle_rad), 0],
                [0, 0, 0, 1]
            ]
        elif axis == "z":
            rotation_matrix = [
                [math.cos(angle_rad), -math.sin(angle_rad), 0, 0],
                [math.sin(angle_rad), math.cos(angle_rad), 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, 1]
            ]
        else:
            return
        
        # 应用旋转变换
        self.selected_shape.apply_transform(rotation_matrix)
        
        # 移回原位置
        self.selected_shape.translate(center[0], center[1], center[2])
