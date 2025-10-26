"""
2D图形绘制系统 - 主程序入口
"""
import os
import sys
import tkinter as tk
from tkinter import messagebox

# 添加项目路径 - 修复exe文件的路径问题
def get_resource_path(relative_path):
    """获取资源文件的绝对路径，兼容开发环境和打包后的exe"""
    try:
        # PyInstaller创建临时文件夹并将路径存储在_MEIPASS中
        base_path = sys._MEIPASS
    except AttributeError:
        # 如果不是打包环境，使用当前文件所在目录
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

# 添加src目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = get_resource_path('src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# 如果src目录不存在，尝试当前目录
if not os.path.exists(src_path):
    sys.path.insert(0, current_dir)

try:
    from ui.main_window import MainWindow
except ImportError as e:
    print(f"导入错误: {e}")
    print(f"当前工作目录: {os.getcwd()}")
    print(f"Python路径: {sys.path}")
    print("请确保所有必要的模块都已正确安装")
    
    # 尝试直接从当前目录导入
    try:
        sys.path.insert(0, os.path.join(current_dir, 'src'))
        from ui.main_window import MainWindow
        print("成功从备用路径导入模块")
    except ImportError as e2:
        print(f"备用导入也失败: {e2}")
        input("按回车键退出...")
        sys.exit(1)


def main():
    """主函数"""
    try:
        # 创建并运行主窗口
        app = MainWindow()
        app.run()
    except Exception as e:
        messagebox.showerror("错误", f"程序启动失败:\\n{str(e)}")
        print(f"错误详情: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()